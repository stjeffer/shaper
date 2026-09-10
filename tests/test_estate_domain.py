"""Knowledge-estate domain contract tests."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from shaper.domain import (
    DecisionOutcome,
    DocumentReadinessReport,
    EffortBand,
    EstateDocument,
    TokenEstimate,
    TransformationDecision,
    TransformationProposal,
    safe_artifact_name,
)
from shaper.domain.models import canonical_hash

NOW = datetime(2026, 9, 10, tzinfo=UTC)
ZERO_HASH = "0" * 64


def _estimate() -> TokenEstimate:
    return TokenEstimate(
        estimate_id="1" * 64,
        model_deployment="gpt-5-mini",
        estimator_version="1.0",
        input_min=100,
        input_max=120,
        output_min=30,
        output_max=50,
        expected_total=150,
        enforced_maximum=200,
        assumptions=("One canonical HTML output",),
        confidence=0.8,
    )


def _proposal() -> TransformationProposal:
    return TransformationProposal(
        recommendation_id="2" * 64,
        recommendation_version="3" * 64,
        run_id="run-1",
        discovery_run_id="discover-1",
        estate_id="estate-1",
        document_id="document-1",
        source_version=ZERO_HASH,
        report_id="4" * 64,
        proposed_changes=("Improve headings",),
        rationale="The document has a flat structure.",
        risk="Source meaning must remain unchanged.",
        effort_points=42,
        evidence_ids=("report-1",),
        expected_artifact="shaper_policy.html",
        token_estimate=_estimate(),
        created_at=NOW,
    )


def test_given_unsafe_source_name_when_rendering_artifact_then_fails_closed() -> None:
    # Act & Assert
    with pytest.raises(ValueError, match="safe"):
        safe_artifact_name("CON.docx")


def test_given_filename_collision_when_rendering_artifact_then_suffix_is_deterministic() -> None:
    # Act
    result = safe_artifact_name("Travel policy.docx", collision_suffix="source-42")

    # Assert
    assert result == "shaper_Travel_policy-source-42.html"


def test_given_mismatched_source_version_when_document_created_then_rejected() -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="content hash"):
        EstateDocument(
            document_id="document-1",
            estate_id="estate-1",
            source_id="source-1",
            source_version=ZERO_HASH,
            content_hash="1" * 64,
            title="Travel",
            filename="travel.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            content_locator="asset-1",
            modified_at=NOW,
            discovered_at=NOW,
        )


def test_given_invalid_token_range_when_estimate_created_then_rejected() -> None:
    # Arrange
    values = _estimate().model_dump()
    values["input_min"] = 121

    # Act & Assert
    with pytest.raises(ValidationError, match="minimums"):
        TokenEstimate.model_validate(values)


def test_given_matching_approval_when_checked_then_exact_proposal_is_permitted() -> None:
    # Arrange
    proposal = _proposal()
    decision = TransformationDecision(
        decision_id="decision-1",
        estate_id=proposal.estate_id,
        document_id=proposal.document_id,
        source_version=proposal.source_version,
        recommendation_version=proposal.recommendation_version,
        estimate_id=proposal.token_estimate.estimate_id,
        estimator_version=proposal.token_estimate.estimator_version,
        model_deployment=proposal.token_estimate.model_deployment,
        outcome=DecisionOutcome.APPROVE,
        reason="Proceed with the bounded proposal.",
        decided_by="person-1",
        decided_at=NOW,
    )

    # Act & Assert
    assert decision.permits(proposal)


def test_given_changed_estimate_when_approval_checked_then_permission_is_invalidated() -> None:
    # Arrange
    proposal = _proposal()
    decision = TransformationDecision(
        decision_id="decision-1",
        estate_id=proposal.estate_id,
        document_id=proposal.document_id,
        source_version=proposal.source_version,
        recommendation_version=proposal.recommendation_version,
        estimate_id="f" * 64,
        estimator_version=proposal.token_estimate.estimator_version,
        model_deployment=proposal.token_estimate.model_deployment,
        outcome=DecisionOutcome.APPROVE,
        reason="Proceed with the bounded proposal.",
        decided_by="person-1",
        decided_at=NOW,
    )

    # Act & Assert
    assert not decision.permits(proposal)


def test_given_effort_points_when_report_created_then_band_must_match() -> None:
    # Arrange
    identity = {
        "run_id": "run-1",
        "document_id": "document-1",
        "source_version": ZERO_HASH,
        "readiness_score": 52.0,
        "effort_points": 70,
    }

    # Act
    report = DocumentReadinessReport(
        report_id=canonical_hash(identity),
        run_id="run-1",
        estate_id="estate-1",
        document_id="document-1",
        source_version=ZERO_HASH,
        readiness_score=52.0,
        effort_points=70,
        effort_band=EffortBand.HIGH,
        evidence_coverage=100,
        reasons=("Long paragraphs require restructuring.",),
        finding_codes=("long_paragraph",),
        agent_roles=("Assessment Agent", "Agent Readiness Agent"),
        assessed_at=NOW,
    )

    # Assert
    assert report.effort_band is EffortBand.HIGH
