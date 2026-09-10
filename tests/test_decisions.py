"""Pre-transformation decision service tests."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from shaper.application.decisions import (
    DecisionConflictError,
    StaleProposalError,
    TransformationDecisionService,
)
from shaper.domain import (
    CollectionRole,
    DecisionOutcome,
    EstateDocument,
    KnowledgeEstate,
    Principal,
    TokenEstimate,
    TransformationProposal,
)
from shaper.infrastructure.sqlite import SQLiteEstateRepository, SQLiteStore

NOW = datetime(2026, 9, 10, tzinfo=UTC)
ZERO_HASH = "0" * 64


def _setup(path: Path) -> tuple[SQLiteStore, SQLiteEstateRepository, TransformationProposal]:
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
            title="Policy",
            filename="policy.md",
            media_type="text/markdown",
            content_locator="repository:document-1",
            modified_at=NOW,
            discovered_at=NOW,
        )
    )
    estimate = TokenEstimate(
        estimate_id="1" * 64,
        model_deployment="gpt-5-mini",
        estimator_version="1.0",
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
    return store, repository, proposal


def _principal() -> Principal:
    return Principal(
        principal_id="person-1",
        tenant_id="tenant-1",
        collection_roles={
            "collection-1": frozenset({CollectionRole.QUERY, CollectionRole.REVIEW})
        },
    )


def test_given_current_proposal_when_approved_then_exact_authorization_is_queryable(
    tmp_path: Path,
) -> None:
    # Arrange
    store, repository, proposal = _setup(tmp_path / "state.db")
    service = TransformationDecisionService(
        repository,
        clock=lambda: NOW,
        id_factory=lambda: "one",
    )
    try:
        # Act
        decision = service.decide(
            proposal.recommendation_id,
            principal=_principal(),
            outcome=DecisionOutcome.APPROVE,
            reason="Proceed",
            expected_current_decision_id=None,
        )

        # Assert
        assert decision.permits(proposal)
        assert service.current(proposal.recommendation_id, principal=_principal())[1]
    finally:
        store.close()


def test_given_declined_proposal_when_queried_then_it_is_not_runnable(tmp_path: Path) -> None:
    # Arrange
    store, repository, proposal = _setup(tmp_path / "state.db")
    service = TransformationDecisionService(
        repository,
        clock=lambda: NOW,
        id_factory=lambda: "one",
    )
    try:
        # Act
        decision = service.decide(
            proposal.recommendation_id,
            principal=_principal(),
            outcome=DecisionOutcome.DECLINE,
            reason="Do not change this guidance",
            expected_current_decision_id=None,
        )

        # Assert
        assert not decision.permits(proposal)
    finally:
        store.close()


def test_given_changed_source_when_approved_then_stale_proposal_is_rejected(
    tmp_path: Path,
) -> None:
    # Arrange
    store, repository, proposal = _setup(tmp_path / "state.db")
    current = repository.get_document("document-1")
    assert current is not None
    values = current.value.model_dump()
    values.update({"source_version": "f" * 64, "content_hash": "f" * 64})
    repository.save_document(
        EstateDocument.model_validate(values),
        expected_revision=current.revision,
    )
    service = TransformationDecisionService(repository, clock=lambda: NOW)
    try:
        # Act & Assert
        with pytest.raises(StaleProposalError, match="changed"):
            service.decide(
                proposal.recommendation_id,
                principal=_principal(),
                outcome=DecisionOutcome.APPROVE,
                reason="Proceed",
                expected_current_decision_id=None,
            )
    finally:
        store.close()


def test_given_stale_expected_decision_when_deciding_then_conflict_is_explicit(
    tmp_path: Path,
) -> None:
    # Arrange
    store, repository, proposal = _setup(tmp_path / "state.db")
    service = TransformationDecisionService(
        repository,
        clock=lambda: NOW,
        id_factory=lambda: "one",
    )
    service.decide(
        proposal.recommendation_id,
        principal=_principal(),
        outcome=DecisionOutcome.DECLINE,
        reason="Wait",
        expected_current_decision_id=None,
    )
    try:
        # Act & Assert
        with pytest.raises(DecisionConflictError, match="Decision changed"):
            service.decide(
                proposal.recommendation_id,
                principal=_principal(),
                outcome=DecisionOutcome.APPROVE,
                reason="Proceed",
                expected_current_decision_id=None,
            )
    finally:
        store.close()
