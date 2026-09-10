"""Hosted compilation workflow from scanned upload through approved release."""

from __future__ import annotations

import hashlib
import uuid
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Protocol

from pydantic import BaseModel, ConfigDict

from shaper.application.agent_tools import EvidenceContext, ReadOnlyToolRegistry
from shaper.application.ingestion import ingest_content
from shaper.application.jobs import JobConflictError, JobStore
from shaper.application.ports import (
    DocumentParser,
    ModelGateway,
    UploadStore,
    Validator,
)
from shaper.application.review import ReviewRecord, ReviewService
from shaper.application.shaping import CheckpointStore, ShapingBudget, ShapingLoop
from shaper.domain import (
    AnswerUnit,
    CollectionRole,
    CompileJob,
    JobState,
    Principal,
    ReviewDecision,
    SourceSpan,
)
from shaper.domain.models import OutputKind, ReviewOutcome, SourceKind


class CompilationRecord(BaseModel):
    """Durable candidate state associated with one compile job."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    job_id: str
    tenant_id: str
    collection_id: str
    permission_hash: str
    run_id: str
    unit: AnswerUnit
    release_id: str | None = None


class CandidateStore(Protocol):
    """Durable compilation-candidate boundary."""

    def get(self, job_id: str) -> tuple[CompilationRecord, int] | None:
        """Return a candidate and its storage revision."""

    def save(
        self,
        record: CompilationRecord,
        *,
        expected_revision: int,
    ) -> tuple[CompilationRecord, int]:
        """Persist a candidate using optimistic concurrency."""


class CompilationPublisher(Protocol):
    """Publish one approved candidate as a complete release."""

    def publish(self, record: CompilationRecord, approved: ReviewRecord) -> str:
        """Publish and return the immutable release identifier."""


class _DocumentEvidence(EvidenceContext):
    def __init__(self, spans: Sequence[SourceSpan]) -> None:
        self._spans = tuple(spans)

    def spans(self, source_id: str) -> Sequence[SourceSpan]:
        return tuple(span for span in self._spans if span.source_id == source_id)

    def taxonomy(self, collection_id: str, name: str) -> Sequence[str]:
        del collection_id, name
        return ()

    def conflicts(self, collection_id: str, text: str, limit: int) -> Sequence[str]:
        del collection_id, text, limit
        return ()


class CompilationService:
    """Execute and approve hosted compilation jobs."""

    def __init__(
        self,
        *,
        jobs: JobStore,
        uploads: UploadStore,
        parser: DocumentParser,
        model: ModelGateway,
        validator: Validator,
        checkpoints: CheckpointStore,
        candidates: CandidateStore,
        reviews: ReviewService,
        publisher: CompilationPublisher,
    ) -> None:
        self._jobs = jobs
        self._uploads = uploads
        self._parser = parser
        self._model = model
        self._validator = validator
        self._checkpoints = checkpoints
        self._candidates = candidates
        self._reviews = reviews
        self._publisher = publisher

    def compile(self, job: CompileJob) -> JobState:
        """Shape one scanned upload and persist it for independent review."""
        if job.source.kind is not SourceKind.UPLOAD:
            raise NotImplementedError("Hosted SharePoint compilation is not configured")
        if job.output.kind is not OutputKind.FILESYSTEM:
            raise NotImplementedError("Hosted SharePoint publication is not configured")
        principal = Principal(
            principal_id=job.submitted_by,
            tenant_id=job.tenant_id,
            collection_roles={
                job.collection_id: frozenset({CollectionRole.COMPILE}),
            },
        )
        asset = self._uploads.describe(job.source.locator, principal)
        permission_hash = hashlib.sha256(
            f"{job.tenant_id}:{job.collection_id}:{asset.asset_id}".encode()
        ).hexdigest()
        with self._uploads.open_asset(job.source.locator, principal) as stream:
            ingested = ingest_content(
                source_id=asset.asset_id,
                tenant_id=job.tenant_id,
                collection_id=job.collection_id,
                title=asset.filename,
                media_type=asset.media_type,
                stream=stream,
                permission_hash=permission_hash,
                parser=self._parser,
            )
        tools = ReadOnlyToolRegistry(
            _DocumentEvidence(ingested.spans),
            source_id=ingested.document.source_id,
            collection_id=job.collection_id,
        )
        outcome = ShapingLoop(
            model=self._model,
            tools=tools,
            validator=self._validator,
            checkpoints=self._checkpoints,
            budget=ShapingBudget(maximum_tokens=job.requested_token_budget),
        ).run(
            run_id=job.job_id,
            document=ingested.document,
            spans=ingested.spans,
            principal=principal,
            cancelled=lambda: self._is_cancelling(job.job_id),
        )
        if outcome.unit is None:
            raise RuntimeError(f"Answer shaping abstained: {outcome.reason}")
        findings = self._validator.validate(outcome.unit, ingested.spans)
        review = self._reviews.submit(outcome.unit, findings)
        self._candidates.save(
            CompilationRecord(
                job_id=job.job_id,
                tenant_id=job.tenant_id,
                collection_id=job.collection_id,
                permission_hash=permission_hash,
                run_id=job.job_id,
                unit=review.unit,
            ),
            expected_revision=0,
        )
        return JobState.AWAITING_REVIEW

    def review_status(self, job_id: str, *, principal: Principal) -> ReviewRecord:
        """Return the candidate review state for an authorized reviewer."""
        stored = self._required_candidate(job_id)
        principal.require(stored[0].collection_id, CollectionRole.REVIEW)
        return self._reviews.get(stored[0].unit.unit_id)

    def approve(
        self,
        job_id: str,
        *,
        principal: Principal,
        reason: str,
        expected_revision: int,
    ) -> tuple[ReviewRecord, str]:
        """Approve, publish, and complete one reviewed compile job."""
        candidate, candidate_revision = self._required_candidate(job_id)
        principal.require(candidate.collection_id, CollectionRole.REVIEW)
        approved = self._reviews.decide(
            ReviewDecision(
                decision_id=uuid.uuid4().hex,
                unit_id=candidate.unit.unit_id,
                unit_version=candidate.unit.unit_version,
                outcome=ReviewOutcome.APPROVE,
                actor=principal,
                reason=reason,
                expected_revision=expected_revision,
                decided_at=datetime.now(UTC),
            ),
            expected_revision=expected_revision,
        )
        release_id = self._publisher.publish(candidate, approved)
        self._complete_job(job_id)
        self._candidates.save(
            candidate.model_copy(update={"unit": approved.unit, "release_id": release_id}),
            expected_revision=candidate_revision,
        )
        return approved, release_id

    def _required_candidate(self, job_id: str) -> tuple[CompilationRecord, int]:
        stored = self._candidates.get(job_id)
        if stored is None:
            raise KeyError(f"Compile job has no review candidate: {job_id}")
        return stored

    def _is_cancelling(self, job_id: str) -> bool:
        current = self._jobs.get(job_id)
        return current is not None and current.state is JobState.CANCELLING

    def _complete_job(self, job_id: str) -> CompileJob:
        job = self._jobs.get(job_id)
        if job is None:
            raise KeyError(f"Compile job does not exist: {job_id}")
        if job.state is not JobState.AWAITING_REVIEW:
            raise JobConflictError(
                f"Only a job awaiting review can be completed, not {job.state.value!r}"
            )
        return self._jobs.save(
            CompileJob.model_validate({**job.model_dump(), "state": JobState.COMPLETED}),
            expected_revision=job.revision,
        )
