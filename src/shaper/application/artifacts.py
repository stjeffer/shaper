"""Approved transformation, safe HTML rendering, and artifact publication."""

from __future__ import annotations

import hashlib
import html
import time
import uuid
from collections.abc import Callable, Sequence
from datetime import datetime, timedelta

from shaper.application.agent_tools import EvidenceContext, ReadOnlyToolRegistry
from shaper.application.estates import EstateRepository, EstateService, VersionedRecord
from shaper.application.ports import ModelGateway, Validator
from shaper.application.review import ReviewRecord, ReviewService
from shaper.application.shaping import (
    CheckpointStore,
    ShapingBudget,
    ShapingBudgetExceeded,
    ShapingCancelled,
    ShapingLoop,
)
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
    TransformationEvaluation,
    TransformationProposal,
    ValidationFinding,
    WorkflowKind,
    WorkflowRun,
    WorkflowStatus,
)
from shaper.domain.models import ReviewOutcome, canonical_hash


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
            '<section aria-labelledby="summary"><h2 id="summary">Canonical guidance</h2>'
            f"<p>{html.escape(unit.answer)}</p></section>\n"
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


class ArtifactEvaluator:
    """Score generated structure and citation coverage without claiming correctness."""

    VERSION = "1.0"
    LIMITATIONS = (
        "Deterministic checks do not establish factual correctness or policy authority.",
        "Citation coverage confirms references exist, not that every claim is entailed.",
    )

    def evaluate(
        self,
        *,
        unit: AnswerUnit,
        spans: Sequence[SourceSpan],
        findings: Sequence[ValidationFinding],
        evaluated_at: datetime,
    ) -> TransformationEvaluation:
        """Return a transparent, versioned evaluation for one generated unit."""
        span_ids = {span.span_id for span in spans}
        cited_claims = sum(
            1 for claim in unit.claims if claim.span_ids and set(claim.span_ids).issubset(span_ids)
        )
        citation_score = round(100 * cited_claims / len(unit.claims)) if unit.claims else 0
        structure_checks = (
            bool(unit.answer.strip()),
            bool(unit.canonical_questions),
            bool(unit.claims),
            all(question.strip() for question in unit.canonical_questions),
        )
        structure_score = round(100 * sum(structure_checks) / len(structure_checks))
        blocking = sum(1 for finding in findings if finding.severity.value == "blocking")
        warnings = sum(1 for finding in findings if finding.severity.value == "warning")
        validation_score = 0 if blocking else 80 if warnings else 100
        overall_score = round(
            (citation_score * 0.45) + (structure_score * 0.25) + (validation_score * 0.30)
        )
        identity = {
            "unit_version": unit.unit_version,
            "evaluator_version": self.VERSION,
            "citation_coverage_score": citation_score,
            "structure_score": structure_score,
            "validation_score": validation_score,
            "blocking_findings": blocking,
            "warning_findings": warnings,
        }
        return TransformationEvaluation(
            evaluation_id=canonical_hash(identity),
            evaluator_version=self.VERSION,
            citation_coverage_score=citation_score,
            structure_score=structure_score,
            validation_score=validation_score,
            overall_score=overall_score,
            blocking_findings=blocking,
            warning_findings=warnings,
            passed=blocking == 0,
            limitations=self.LIMITATIONS,
            evaluated_at=evaluated_at,
        )


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
        evaluator: ArtifactEvaluator | None = None,
        monotonic: Callable[[], float] = time.monotonic,
        id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._repository = repository
        self._model = model
        self._validator = validator
        self._reviews = reviews
        self._renderer = renderer
        self._clock = clock
        self._evaluator = evaluator or ArtifactEvaluator()
        self._monotonic = monotonic
        self._id_factory = id_factory or (lambda: uuid.uuid4().hex)

    def start(
        self,
        recommendation_ids: Sequence[str],
        *,
        principal: Principal,
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
        completed = []
        failed = []
        for proposal in proposals:
            try:
                self._transform(running.value.run_id, proposal, principal)
                completed.append(proposal.document_id)
            except (
                KeyError,
                PermissionError,
                ValueError,
                ShapingBudgetExceeded,
                ShapingCancelled,
            ):
                failed.append(proposal.document_id)
        values = running.value.model_dump()
        values.update(
            {
                "status": (
                    WorkflowStatus.FAILED
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
                "error": "No approved proposal could be transformed." if not completed else None,
            }
        )
        return self._repository.save_run(
            WorkflowRun.model_validate(values),
            expected_revision=running.revision,
        )

    def approve(
        self,
        artifact_id: str,
        *,
        principal: Principal,
        reason: str,
        expected_review_revision: int,
        expected_artifact_revision: int,
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
        content = self._repository.load_artifact_content(artifact_id)
        if hashlib.sha256(content).hexdigest() != artifact.value.content_hash:
            raise ValueError("Artifact content hash does not match its manifest")
        return content

    def evaluation(
        self,
        artifact_id: str,
        *,
        principal: Principal,
    ) -> TransformationEvaluation:
        """Return the generated evaluation to an authorized reviewer."""
        artifact = self._repository.get_artifact(artifact_id)
        if artifact is None:
            raise KeyError(f"Knowledge artifact does not exist: {artifact_id}")
        estate = self._repository.get_estate(artifact.value.estate_id)
        if estate is None:
            raise KeyError(f"Knowledge estate does not exist: {artifact.value.estate_id}")
        EstateService._authorize(estate.value, principal, CollectionRole.REVIEW)
        if artifact.value.evaluation is None:
            raise KeyError(f"Knowledge artifact has no evaluation: {artifact_id}")
        return artifact.value.evaluation

    def _transform(
        self,
        run_id: str,
        proposal: TransformationProposal,
        principal: Principal,
    ) -> None:
        decision = self._repository.latest_decision(proposal.document_id)
        if decision is None or not decision.permits(proposal):
            raise PermissionError("Transformation requires a current exact approval")
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
        started = self._monotonic()
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
                budget=ShapingBudget(maximum_tokens=proposal.token_estimate.enforced_maximum),
                monotonic=self._monotonic,
            ).run(
                run_id=f"{run_id}:{document.value.document_id}",
                document=source,
                spans=(span,),
                principal=principal,
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
        findings = self._validator.validate(outcome.unit, (span,))
        review = self._reviews.submit(outcome.unit, findings)
        evaluated_at = self._clock()
        evaluation = self._evaluator.evaluate(
            unit=review.unit,
            spans=(span,),
            findings=findings,
            evaluated_at=evaluated_at,
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
            evaluation=evaluation,
            created_at=evaluated_at,
        )
        self._repository.save_artifact_bundle(artifact, content)

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
