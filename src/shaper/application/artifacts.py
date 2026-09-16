"""Approved transformation, safe HTML rendering, and artifact publication."""

from __future__ import annotations

import hashlib
import html
import re
import time
import uuid
from collections.abc import Callable, Sequence
from datetime import datetime, timedelta

from shaper.application.agent_tools import EvidenceContext, ReadOnlyToolRegistry
from shaper.application.estates import EstateRepository, EstateService, VersionedRecord
from shaper.application.model import ModelProviderError
from shaper.application.ports import ModelGateway, Validator
from shaper.application.review import ReviewRecord, ReviewService
from shaper.application.shaping import (
    CheckpointStore,
    ShapingBudget,
    ShapingBudgetExceeded,
    ShapingCancelled,
    ShapingLoop,
)
from shaper.application.token_estimation import ESTIMATOR_VERSION
from shaper.application.transformation_actions import derive_approved_source_exclusions
from shaper.application.validation import findings_for_review
from shaper.domain import (
    AnswerUnit,
    ArtifactStatus,
    CollectionRole,
    KnowledgeArtifact,
    KnowledgeEstate,
    PermissionSnapshot,
    Principal,
    ReviewDecision,
    SourceDocument,
    SourceSpan,
    TokenUsage,
    TransformationProposal,
    ValidationFinding,
    WorkflowKind,
    WorkflowRun,
    WorkflowStatus,
)
from shaper.domain.models import ReviewOutcome, canonical_hash
from shaper.prompts import SHAPING_PROMPT

TransformationProgress = Callable[[dict[str, object]], None]


class HtmlArtifactRenderer:
    """Render byte-stable semantic HTML with escaped untrusted values."""

    def render(
        self,
        *,
        title: str,
        unit: AnswerUnit,
        proposal: TransformationProposal,
    ) -> bytes:
        """Render one answer unit and its derivation metadata."""
        questions = "".join(
            f"<li>{html.escape(question)}</li>" for question in unit.canonical_questions
        )
        claims = "".join(f"<li>{html.escape(claim.text)}</li>" for claim in unit.claims)
        guidance = self._semantic_content(unit.answer)
        markup = (
            "<!doctype html>\n"
            '<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            f"<title>{html.escape(title)}</title>\n"
            '<meta name="generator" content="Shaper">\n'
            f'<meta name="shaper-source-version" content="{unit.source_version}">\n'
            f'<meta name="shaper-unit-id" content="{unit.unit_id}">\n'
            "</head>\n<body>\n"
            "<article>\n"
            f"<header><h1>{html.escape(title)}</h1></header>\n"
            '<section aria-labelledby="reshaped-content">'
            '<h2 id="reshaped-content">Reshaped document</h2>'
            f"{guidance}</section>\n"
            '<section aria-labelledby="questions"><h2 id="questions">Questions answered</h2>'
            f"<ul>{questions}</ul></section>\n"
            '<section aria-labelledby="claims"><h2 id="claims">Grounded claims</h2>'
            f"<ul>{claims}</ul></section>\n"
            "<footer>"
            f"<p>Recommendation: {proposal.recommendation_version}</p>"
            f"<p>Source version: {proposal.source_version}</p>"
            "</footer>\n"
            "</article>\n</body>\n</html>\n"
        )
        return markup.encode("utf-8")

    @staticmethod
    def _semantic_content(value: str) -> str:
        """Render simple model-authored Markdown as escaped semantic HTML."""
        parts: list[str] = []
        list_type: str | None = None

        def close_list() -> None:
            nonlocal list_type
            if list_type is not None:
                parts.append(f"</{list_type}>")
                list_type = None

        for raw_line in value.splitlines():
            line = raw_line.strip()
            if not line:
                close_list()
                continue
            heading = re.match(r"^(#{1,5})\s+(.+)$", line)
            if heading:
                close_list()
                level = len(heading.group(1)) + 1
                parts.append(f"<h{level}>{html.escape(heading.group(2))}</h{level}>")
                continue
            bullet = re.match(r"^[-*]\s+(.+)$", line)
            numbered = re.match(r"^\d+[.)]\s+(.+)$", line)
            if bullet or numbered:
                required_type = "ul" if bullet else "ol"
                if list_type != required_type:
                    close_list()
                    list_type = required_type
                    parts.append(f"<{list_type}>")
                match = bullet or numbered
                assert match is not None
                parts.append(f"<li>{html.escape(match.group(1))}</li>")
                continue
            close_list()
            parts.append(f"<p>{html.escape(line)}</p>")
        close_list()
        return "".join(parts)


class _RepositoryCheckpoints(CheckpointStore):
    def __init__(self, repository: EstateRepository) -> None:
        self._repository = repository

    def save(self, run_id: str, state: str, payload: str) -> None:
        self._repository.save_shaping_checkpoint(run_id, state, payload)


class _Evidence(EvidenceContext):
    def __init__(self, span: SourceSpan) -> None:
        self._span = span

    def spans(self, source_id: str) -> Sequence[SourceSpan]:
        return (self._span,) if self._span.source_id == source_id else ()

    def taxonomy(self, collection_id: str, name: str) -> Sequence[str]:
        del collection_id, name
        return ()

    def conflicts(self, collection_id: str, text: str, limit: int) -> Sequence[str]:
        del collection_id, text, limit
        return ()


class EstateTransformationService:
    """Execute only current approvals and retain estimate, usage, and artifact records."""

    def __init__(
        self,
        repository: EstateRepository,
        *,
        model: ModelGateway,
        validator: Validator,
        reviews: ReviewService,
        renderer: HtmlArtifactRenderer,
        clock: Callable[[], datetime],
        monotonic: Callable[[], float] = time.monotonic,
        id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._repository = repository
        self._model = model
        self._validator = validator
        self._reviews = reviews
        self._renderer = renderer
        self._clock = clock
        self._monotonic = monotonic
        self._id_factory = id_factory or (lambda: uuid.uuid4().hex)

    def start(
        self,
        recommendation_ids: Sequence[str],
        *,
        principal: Principal,
        enforce_preservation_checks: bool = True,
        progress: TransformationProgress | None = None,
        cancelled: Callable[[], bool] = lambda: False,
    ) -> VersionedRecord[WorkflowRun]:
        """Transform approved proposals and place generated outputs in review."""
        if not recommendation_ids or len(recommendation_ids) > 100:
            raise ValueError("Transformation requires between 1 and 100 recommendations")
        if len(recommendation_ids) != len(set(recommendation_ids)):
            raise ValueError("Transformation recommendations must be unique")
        proposals = tuple(self._required_proposal(item) for item in recommendation_ids)
        estate_ids = {proposal.estate_id for proposal in proposals}
        if len(estate_ids) != 1:
            raise ValueError("One transformation run cannot span knowledge estates")
        estate = self._repository.get_estate(next(iter(estate_ids)))
        if estate is None:
            raise KeyError("Knowledge estate does not exist")
        EstateService._authorize(estate.value, principal, CollectionRole.COMPILE)
        EstateService.require_active(estate.value)
        now = self._clock()
        queued = self._repository.save_run(
            WorkflowRun(
                run_id=f"transform-{self._id_factory()}",
                estate_id=estate.value.estate_id,
                kind=WorkflowKind.TRANSFORM,
                status=WorkflowStatus.QUEUED,
                requested_document_ids=tuple(item.document_id for item in proposals),
                created_at=now,
                updated_at=now,
            )
        )
        running = self._running(queued)
        self._report_progress(
            progress,
            {
                "type": "run_started",
                "run_id": running.value.run_id,
                "document_count": len(proposals),
            },
        )
        completed: list[str] = []
        failed: list[str] = []
        failure_messages: list[str] = []
        cancelled_run = False
        for index, proposal in enumerate(proposals):
            if cancelled():
                failed.extend(item.document_id for item in proposals[index:])
                failure_messages.append("Transformation was cancelled by the requesting client")
                cancelled_run = True
                break
            self._report_progress(
                progress,
                {
                    "type": "document_started",
                    "document_id": proposal.document_id,
                    "artifact_name": proposal.expected_artifact,
                },
            )
            try:
                self._transform(
                    running.value.run_id,
                    proposal,
                    principal,
                    enforce_preservation_checks=enforce_preservation_checks,
                    progress=progress,
                    cancelled=cancelled,
                )
                completed.append(proposal.document_id)
            except ShapingCancelled as error:
                detail = self._failure_detail(error)
                failed.extend(item.document_id for item in proposals[index:])
                failure_messages.append(f"{proposal.document_id}: {detail}")
                self._report_progress(
                    progress,
                    {
                        "type": "document_failed",
                        "document_id": proposal.document_id,
                        "detail": detail,
                    },
                )
                cancelled_run = True
                break
            except (
                KeyError,
                ModelProviderError,
                PermissionError,
                ValueError,
                ShapingBudgetExceeded,
            ) as error:
                detail = self._failure_detail(error)
                failed.append(proposal.document_id)
                failure_messages.append(f"{proposal.document_id}: {detail}")
                self._report_progress(
                    progress,
                    {
                        "type": "document_failed",
                        "document_id": proposal.document_id,
                        "detail": detail,
                    },
                )
        values = running.value.model_dump()
        values.update(
            {
                "status": (
                    WorkflowStatus.CANCELLED
                    if cancelled_run
                    else WorkflowStatus.FAILED
                    if not completed
                    else WorkflowStatus.PARTIAL
                    if failed
                    else WorkflowStatus.COMPLETED
                ),
                "completed_document_ids": tuple(completed),
                "failed_document_ids": tuple(failed),
                "lease_owner": None,
                "lease_expires_at": None,
                "updated_at": self._clock(),
                "error": "; ".join(failure_messages)[:2000] if failed else None,
            }
        )
        final = self._repository.save_run(
            WorkflowRun.model_validate(values),
            expected_revision=running.revision,
        )
        self._report_progress(
            progress,
            {
                "type": "run_completed",
                "run_id": final.value.run_id,
                "status": final.value.status.value,
                "completed_document_ids": list(final.value.completed_document_ids),
                "failed_document_ids": list(final.value.failed_document_ids),
                "error": final.value.error,
            },
        )
        return final

    def approve(
        self,
        artifact_id: str,
        *,
        principal: Principal,
        reason: str,
        expected_review_revision: int,
        expected_artifact_revision: int,
        acknowledged_finding_ids: Sequence[str] = (),
    ) -> tuple[ReviewRecord, VersionedRecord[KnowledgeArtifact]]:
        """Apply separate output review and publish an approved artifact."""
        artifact = self._repository.get_artifact(artifact_id)
        if artifact is None:
            raise KeyError(f"Knowledge artifact does not exist: {artifact_id}")
        estate = self._repository.get_estate(artifact.value.estate_id)
        if estate is None:
            raise KeyError(f"Knowledge estate does not exist: {artifact.value.estate_id}")
        EstateService._authorize(estate.value, principal, CollectionRole.REVIEW)
        review = self._reviews.get(artifact.value.unit_id)
        required_acknowledgments = {
            finding.rule_id for finding in artifact.value.validation_findings
        }
        if required_acknowledgments != set(acknowledged_finding_ids):
            raise PermissionError("Artifact approval must acknowledge every validation finding")
        approved = self._reviews.decide(
            ReviewDecision(
                decision_id=f"review-{self._id_factory()}",
                unit_id=review.unit.unit_id,
                unit_version=review.unit.unit_version,
                outcome=ReviewOutcome.APPROVE,
                actor=principal,
                reason=reason,
                expected_revision=expected_review_revision,
                decided_at=self._clock(),
            ),
            expected_revision=expected_review_revision,
        )
        values = artifact.value.model_dump()
        values.update(
            {
                "status": ArtifactStatus.APPROVED,
                "approval_id": approved.decisions[-1].decision_id,
            }
        )
        published = self._repository.save_artifact(
            KnowledgeArtifact.model_validate(values),
            expected_revision=expected_artifact_revision,
        )
        return approved, published

    def content(self, artifact_id: str, *, principal: Principal) -> bytes:
        """Return hash-verified bytes for an approved artifact."""
        artifact = self._repository.get_artifact(artifact_id)
        if artifact is None:
            raise KeyError(f"Knowledge artifact does not exist: {artifact_id}")
        estate = self._repository.get_estate(artifact.value.estate_id)
        if estate is None:
            raise KeyError(f"Knowledge estate does not exist: {artifact.value.estate_id}")
        EstateService._authorize(estate.value, principal, CollectionRole.QUERY)
        if artifact.value.status is not ArtifactStatus.APPROVED:
            raise PermissionError("Artifact is not approved for publication")
        return self._verified_content(artifact_id, artifact.value.content_hash)

    def preview(self, artifact_id: str, *, principal: Principal) -> bytes:
        """Return hash-verified artifact bytes to an authorized reviewer."""
        artifact = self._repository.get_artifact(artifact_id)
        if artifact is None:
            raise KeyError(f"Knowledge artifact does not exist: {artifact_id}")
        estate = self._repository.get_estate(artifact.value.estate_id)
        if estate is None:
            raise KeyError(f"Knowledge estate does not exist: {artifact.value.estate_id}")
        EstateService._authorize(estate.value, principal, CollectionRole.REVIEW)
        return self._verified_content(artifact_id, artifact.value.content_hash)

    def _verified_content(self, artifact_id: str, expected_hash: str) -> bytes:
        content = self._repository.load_artifact_content(artifact_id)
        if hashlib.sha256(content).hexdigest() != expected_hash:
            raise ValueError("Artifact content hash does not match its manifest")
        return content

    def _transform(
        self,
        run_id: str,
        proposal: TransformationProposal,
        principal: Principal,
        *,
        enforce_preservation_checks: bool = True,
        progress: TransformationProgress | None = None,
        cancelled: Callable[[], bool] = lambda: False,
    ) -> None:
        decision = self._repository.latest_decision(proposal.document_id)
        if decision is None or not decision.permits(proposal):
            raise PermissionError("Transformation requires a current exact approval")
        reports = tuple(
            report
            for report in self._repository.list_reports(proposal.discovery_run_id)
            if report.document_id == proposal.document_id
        )
        if not reports:
            raise ValueError("Approved transformation proposal is missing its discovery report")
        report = next(
            (candidate for candidate in reports if candidate.report_id == proposal.report_id),
            None,
        )
        if report is None:
            raise ValueError("Approved transformation proposal does not match its discovery report")
        if report.source_version != proposal.source_version:
            raise ValueError(
                "Approved transformation proposal does not match its discovery report version"
            )
        if proposal.token_estimate.estimator_version != ESTIMATOR_VERSION:
            raise ValueError(
                f"Token estimate v{proposal.token_estimate.estimator_version} is outdated; "
                "request recommendations again and approve the new estimate"
            )
        if proposal.token_estimate.prompt_hash != canonical_hash(SHAPING_PROMPT):
            raise ValueError(
                "The shaping instructions changed after this estimate was approved; "
                "request recommendations again and approve the new estimate"
            )
        document = self._repository.get_document(proposal.document_id)
        if (
            document is None
            or document.value.deleted
            or document.value.source_version != proposal.source_version
        ):
            raise PermissionError("Approved source version is no longer current")
        text = self._repository.load_document_content(
            proposal.document_id,
            proposal.source_version,
        )
        source = SourceDocument(
            source_id=document.value.document_id,
            source_version=document.value.source_version,
            content_hash=document.value.content_hash,
            tenant_id=principal.tenant_id,
            collection_id=self._required_estate(proposal).collection_id,
            title=document.value.title,
            media_type=document.value.media_type,
            observed_at=document.value.modified_at,
            permission=PermissionSnapshot(
                permission_hash=canonical_hash(
                    {
                        "estate_id": proposal.estate_id,
                        "source_id": document.value.source_id,
                    }
                ),
                captured_at=document.value.discovered_at,
            ),
        )
        span = SourceSpan(
            span_id=f"{document.value.document_id}:0",
            source_id=source.source_id,
            source_version=source.source_version,
            ordinal=0,
            text=text,
            text_hash=hashlib.sha256(text.encode()).hexdigest(),
        )
        approved_source_exclusions = derive_approved_source_exclusions(
            report,
            source_version=source.source_version,
            source_text=text,
            approved_actions=proposal.proposed_changes,
        )
        self._report_progress(
            progress,
            {
                "type": "check_updated",
                "document_id": proposal.document_id,
                "check": "reshape",
                "status": "running",
                "detail": "Creating a complete reshaped document.",
            },
        )
        started = self._monotonic()

        def report_validation_failure(
            attempt: int,
            maximum: int,
            findings: Sequence[ValidationFinding],
        ) -> None:
            finding = findings[0]
            retrying = attempt < maximum
            self._report_progress(
                progress,
                {
                    "type": "check_updated",
                    "document_id": proposal.document_id,
                    "check": "reshape",
                    "status": "running" if retrying else "failed",
                    "detail": (
                        f"Attempt {attempt} failed {finding.rule_id}: {finding.message}. "
                        + (
                            "Applying one targeted repair."
                            if retrying
                            else "No artifact was created."
                        )
                    ),
                },
            )

        try:
            outcome = ShapingLoop(
                model=self._model,
                tools=ReadOnlyToolRegistry(
                    _Evidence(span),
                    source_id=source.source_id,
                    collection_id=source.collection_id,
                ),
                validator=self._validator,
                checkpoints=_RepositoryCheckpoints(self._repository),
                budget=ShapingBudget(
                    maximum_tokens=proposal.token_estimate.enforced_maximum,
                ),
                monotonic=self._monotonic,
                on_model_attempt=lambda attempt, maximum: self._report_progress(
                    progress,
                    {
                        "type": "check_updated",
                        "document_id": proposal.document_id,
                        "check": "reshape",
                        "status": "running",
                        "detail": (
                            f"Generating reshaped content (model attempt {attempt} of {maximum})."
                        ),
                    },
                ),
                on_validation_failure=report_validation_failure,
                maximum_output_tokens=proposal.token_estimate.output_max,
            ).run(
                run_id=f"{run_id}:{document.value.document_id}",
                document=source,
                spans=(span,),
                principal=principal,
                transformation_requirements=proposal.proposed_changes,
                assessment_findings=report.findings,
                approved_source_exclusions=approved_source_exclusions,
                enforce_preservation_checks=enforce_preservation_checks,
                cancelled=cancelled,
            )
        except ShapingBudgetExceeded as error:
            self._append_usage(
                run_id,
                proposal,
                input_tokens=error.input_tokens,
                output_tokens=error.output_tokens,
                model_calls=error.model_calls,
                duration_ms=max(0, round((self._monotonic() - started) * 1000)),
            )
            raise
        duration_ms = max(0, round((self._monotonic() - started) * 1000))
        self._append_usage(
            run_id,
            proposal,
            input_tokens=outcome.input_tokens,
            output_tokens=outcome.output_tokens,
            model_calls=outcome.model_calls,
            duration_ms=duration_ms,
        )
        if outcome.unit is None:
            raise ValueError(f"Transformation abstained: {outcome.reason}")
        self._report_progress(
            progress,
            {
                "type": "check_updated",
                "document_id": proposal.document_id,
                "check": "reshape",
                "status": "passed",
                "detail": "Complete reshaped content was generated.",
            },
        )
        raw_findings = (
            self._validator.validate(
                outcome.unit,
                (span,),
                approved_source_exclusions=approved_source_exclusions,
            )
            if approved_source_exclusions
            else self._validator.validate(outcome.unit, (span,))
        )
        findings = findings_for_review(
            raw_findings,
            enforce_preservation_checks=False,
        )
        warnings = sum(1 for finding in findings if finding.severity.value == "warning")
        self._report_progress(
            progress,
            {
                "type": "check_updated",
                "document_id": proposal.document_id,
                "check": "source_preservation",
                "status": "review" if warnings else "passed",
                "detail": (
                    "Source coverage, material facts, numbers, and operative clauses "
                    "were preserved."
                    if warnings == 0
                    else f"{warnings} preservation finding(s) require human review."
                ),
            },
        )
        self._report_progress(
            progress,
            {
                "type": "check_updated",
                "document_id": proposal.document_id,
                "check": "grounding",
                "status": "passed",
                "detail": "Claims remain grounded in the version-pinned source.",
            },
        )
        review = self._reviews.submit(outcome.unit, findings)
        self._report_progress(
            progress,
            {
                "type": "check_updated",
                "document_id": proposal.document_id,
                "check": "quality",
                "status": "review" if warnings else "passed",
                "detail": (
                    f"Checks completed with {warnings} finding(s) for review."
                    if warnings
                    else "No preservation findings remain."
                ),
            },
        )
        content = self._renderer.render(
            title=document.value.title,
            unit=review.unit,
            proposal=proposal,
        )
        content_hash = hashlib.sha256(content).hexdigest()
        artifact = KnowledgeArtifact(
            artifact_id=canonical_hash(
                {
                    "proposal": proposal.recommendation_version,
                    "unit": review.unit.unit_version,
                    "content_hash": content_hash,
                }
            ),
            estate_id=proposal.estate_id,
            document_id=proposal.document_id,
            source_version=proposal.source_version,
            unit_id=review.unit.unit_id,
            filename=proposal.expected_artifact,
            content_hash=content_hash,
            content_locator=f"repository:{proposal.expected_artifact}",
            status=ArtifactStatus.IN_REVIEW,
            validation_findings=findings,
            created_at=self._clock(),
        )
        self._repository.save_artifact_bundle(artifact, content)
        self._report_progress(
            progress,
            {
                "type": "document_completed",
                "document_id": proposal.document_id,
                "artifact_name": artifact.filename,
            },
        )

    @staticmethod
    def _report_progress(
        progress: TransformationProgress | None,
        event: dict[str, object],
    ) -> None:
        if progress is not None:
            progress(event)

    @staticmethod
    def _failure_detail(error: Exception) -> str:
        return str(error)

    def fail_running(self, run_id: str, detail: str) -> VersionedRecord[WorkflowRun] | None:
        """Terminalize an unexpected streamed transformation failure."""
        current = self._repository.get_run(run_id)
        if current is None or current.value.status is not WorkflowStatus.RUNNING:
            return current
        values = current.value.model_dump()
        values.update(
            {
                "status": WorkflowStatus.FAILED,
                "lease_owner": None,
                "lease_expires_at": None,
                "updated_at": self._clock(),
                "error": detail[:2000],
            }
        )
        return self._repository.save_run(
            WorkflowRun.model_validate(values),
            expected_revision=current.revision,
        )

    def _append_usage(
        self,
        run_id: str,
        proposal: TransformationProposal,
        *,
        input_tokens: int,
        output_tokens: int,
        model_calls: int,
        duration_ms: int,
    ) -> None:
        estimate = proposal.token_estimate
        self._repository.append_usage(
            TokenUsage(
                run_id=run_id,
                document_id=proposal.document_id,
                estimate_id=estimate.estimate_id,
                model_deployment=estimate.model_deployment,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model_calls=model_calls,
                duration_ms=duration_ms,
                expected_total=estimate.expected_total,
                enforced_maximum=estimate.enforced_maximum,
                recorded_at=self._clock(),
            )
        )

    def _running(
        self,
        queued: VersionedRecord[WorkflowRun],
    ) -> VersionedRecord[WorkflowRun]:
        now = self._clock()
        values = queued.value.model_dump()
        values.update(
            {
                "status": WorkflowStatus.RUNNING,
                "lease_owner": "inline-transformation",
                "lease_expires_at": now + timedelta(minutes=5),
                "updated_at": now,
            }
        )
        return self._repository.save_run(
            WorkflowRun.model_validate(values),
            expected_revision=queued.revision,
        )

    def _required_proposal(self, recommendation_id: str) -> TransformationProposal:
        proposal = self._repository.get_proposal(recommendation_id)
        if proposal is None:
            raise KeyError(f"Transformation proposal does not exist: {recommendation_id}")
        return proposal

    def _required_estate(self, proposal: TransformationProposal) -> KnowledgeEstate:
        estate = self._repository.get_estate(proposal.estate_id)
        if estate is None:
            raise KeyError(f"Knowledge estate does not exist: {proposal.estate_id}")
        return estate.value
