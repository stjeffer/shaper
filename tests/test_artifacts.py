"""Approved transformation and safe HTML artifact tests."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from shaper.application.artifacts import EstateTransformationService, HtmlArtifactRenderer
from shaper.application.ports import ModelResult
from shaper.application.review import ReviewService
from shaper.application.token_estimation import ESTIMATOR_VERSION
from shaper.application.validation import DeterministicValidator
from shaper.domain import (
    CollectionRole,
    DecisionOutcome,
    EstateDocument,
    KnowledgeEstate,
    Principal,
    TokenEstimate,
    TransformationDecision,
    TransformationProposal,
)
from shaper.infrastructure.compilation import SQLiteReviewStore
from shaper.infrastructure.sqlite import SQLiteEstateRepository, SQLiteStore

NOW = datetime(2026, 9, 10, tzinfo=UTC)
ZERO_HASH = "0" * 64


class GroundedModel:
    """Return one answer grounded in the supplied source span."""

    def __init__(self) -> None:
        self.calls = 0

    def generate(self, *, prompt: str, schema: dict[str, object]) -> ModelResult:
        del schema
        self.calls += 1
        span = json.loads(prompt)["source"][0]
        return ModelResult(
            payload={
                "status": "candidate",
                "canonical_questions": ["What does the policy say?"],
                "answer": span["text"],
                "claims": [{"text": span["text"], "span_ids": [span["span_id"]]}],
                "confidence": 0.9,
            },
            response_id="response-1",
            input_tokens=12,
            output_tokens=8,
        )


def _principal() -> Principal:
    return Principal(
        principal_id="person-1",
        tenant_id="tenant-1",
        collection_roles={
            "collection-1": frozenset(
                {CollectionRole.COMPILE, CollectionRole.QUERY, CollectionRole.REVIEW}
            )
        },
    )


def _setup(
    path: Path,
    *,
    approved: bool,
    generate_evaluations: bool = True,
    estimator_version: str = ESTIMATOR_VERSION,
) -> tuple[SQLiteStore, SQLiteEstateRepository, TransformationProposal]:
    store = SQLiteStore(path)
    store.connect()
    store.migrate()
    repository = SQLiteEstateRepository(store)
    repository.create_estate(
        KnowledgeEstate(
            estate_id="estate-1",
            collection_id="collection-1",
            tenant_id="tenant-1",
            name="Policy estate",
            generate_evaluations=generate_evaluations,
            created_at=NOW,
            updated_at=NOW,
        )
    )
    repository.save_document(
        EstateDocument(
            document_id="document-1",
            estate_id="estate-1",
            source_id="source-1",
            source_version=ZERO_HASH,
            content_hash=ZERO_HASH,
            title="Policy <script>alert(1)</script>",
            filename="policy.md",
            media_type="text/markdown",
            content_locator="repository:document-1",
            modified_at=NOW,
            discovered_at=NOW,
        )
    )
    repository.save_document_content(
        "document-1",
        ZERO_HASH,
        "Employees receive leave. <script>alert(1)</script>",
    )
    estimate = TokenEstimate(
        estimate_id="1" * 64,
        model_deployment="gpt-5-mini",
        estimator_version=estimator_version,
        input_min=100,
        input_max=120,
        output_min=30,
        output_max=50,
        expected_total=150,
        enforced_maximum=200,
        assumptions=("Deterministic approximation",),
        confidence=0.65,
    )
    proposal = TransformationProposal(
        recommendation_id="2" * 64,
        recommendation_version="3" * 64,
        run_id="recommend-1",
        discovery_run_id="discover-1",
        estate_id="estate-1",
        document_id="document-1",
        source_version=ZERO_HASH,
        report_id="4" * 64,
        proposed_changes=("Generate FAQ",),
        rationale="FAQ coverage is absent.",
        risk="Output requires review.",
        effort_points=30,
        evidence_ids=("4" * 64,),
        expected_artifact="shaper_policy.html",
        token_estimate=estimate,
        created_at=NOW,
    )
    repository.append_proposal(proposal)
    repository.append_decision(
        TransformationDecision(
            decision_id="decision-1",
            estate_id="estate-1",
            document_id="document-1",
            source_version=ZERO_HASH,
            recommendation_version=proposal.recommendation_version,
            estimate_id=estimate.estimate_id,
            estimator_version=estimate.estimator_version,
            model_deployment=estimate.model_deployment,
            outcome=DecisionOutcome.APPROVE if approved else DecisionOutcome.DECLINE,
            reason="Test decision",
            decided_by="person-1",
            decided_at=NOW,
        )
    )
    return store, repository, proposal


def test_given_declined_proposal_when_transformation_starts_then_model_is_not_called(
    tmp_path: Path,
) -> None:
    # Arrange
    store, repository, proposal = _setup(tmp_path / "state.db", approved=False)
    model = GroundedModel()
    service = EstateTransformationService(
        repository,
        model=model,
        validator=DeterministicValidator(),
        reviews=ReviewService(SQLiteReviewStore(store)),
        renderer=HtmlArtifactRenderer(),
        clock=lambda: NOW,
        id_factory=lambda: "one",
    )
    try:
        # Act
        run = service.start((proposal.recommendation_id,), principal=_principal())

        # Assert
        assert run.value.status.value == "failed"
        assert run.value.error == ("document-1: Transformation requires a current exact approval")
        assert model.calls == 0
        assert not repository.list_artifacts("estate-1")
    finally:
        store.close()


def test_given_outdated_estimate_when_transformation_starts_then_new_approval_is_required(
    tmp_path: Path,
) -> None:
    # Arrange
    store, repository, proposal = _setup(
        tmp_path / "state.db",
        approved=True,
        estimator_version="1.0",
    )
    model = GroundedModel()
    service = EstateTransformationService(
        repository,
        model=model,
        validator=DeterministicValidator(),
        reviews=ReviewService(SQLiteReviewStore(store)),
        renderer=HtmlArtifactRenderer(),
        clock=lambda: NOW,
        id_factory=lambda: "one",
    )
    try:
        # Act
        run = service.start((proposal.recommendation_id,), principal=_principal())

        # Assert
        assert run.value.status.value == "failed"
        assert run.value.error is not None
        assert "Token estimate v1.0 is outdated" in run.value.error
        assert "request recommendations again" in run.value.error
        assert model.calls == 0
    finally:
        store.close()


def test_given_approved_proposal_when_reviewed_then_safe_artifact_and_usage_publish(
    tmp_path: Path,
) -> None:
    # Arrange
    store, repository, proposal = _setup(tmp_path / "state.db", approved=True)
    model = GroundedModel()
    service = EstateTransformationService(
        repository,
        model=model,
        validator=DeterministicValidator(),
        reviews=ReviewService(SQLiteReviewStore(store)),
        renderer=HtmlArtifactRenderer(),
        clock=lambda: NOW,
        monotonic=iter((0.0, 0.1, 0.2, 0.3)).__next__,
        id_factory=iter(("run", "review")).__next__,
    )
    try:
        # Act
        run = service.start((proposal.recommendation_id,), principal=_principal())
        artifact = repository.list_artifacts("estate-1")[0]
        preview = service.preview(artifact.artifact_id, principal=_principal())
        review, published = service.approve(
            artifact.artifact_id,
            principal=_principal(),
            reason="Grounding verified.",
            expected_review_revision=1,
            expected_artifact_revision=1,
        )
        content = service.content(artifact.artifact_id, principal=_principal())

        # Assert
        assert run.value.status.value == "completed"
        assert review.unit.state.value == "approved"
        assert published.value.status.value == "approved"
        assert repository.list_usage(run.value.run_id)[0].total_tokens == 20
        assert artifact.evaluation is not None
        assert artifact.evaluation.passed
        assert artifact.evaluation.overall_score == 100
        assert preview == content
        assert b"&lt;script&gt;" in content
        assert b"<script>" not in content
    finally:
        store.close()


def test_given_evaluations_disabled_when_transformed_then_artifact_has_no_evaluation(
    tmp_path: Path,
) -> None:
    store, repository, proposal = _setup(
        tmp_path / "state.db",
        approved=True,
        generate_evaluations=False,
    )
    service = EstateTransformationService(
        repository,
        model=GroundedModel(),
        validator=DeterministicValidator(),
        reviews=ReviewService(SQLiteReviewStore(store)),
        renderer=HtmlArtifactRenderer(),
        clock=lambda: NOW,
        id_factory=lambda: "run",
    )
    try:
        service.start((proposal.recommendation_id,), principal=_principal())
        artifact = repository.list_artifacts("estate-1")[0]

        assert artifact.evaluation is None
        with pytest.raises(KeyError, match="no evaluation"):
            service.evaluation(artifact.artifact_id, principal=_principal())
    finally:
        store.close()
