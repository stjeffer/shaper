"""Estate assessment domain and service tests."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from shaper.application.assessment import DocumentAssessmentService, EstateAssessmentService
from shaper.domain import (
    AssessmentFindingKind,
    AuthorityStatus,
    BusinessAssertion,
    InterventionKind,
    KnowledgeDocumentProfile,
    ReadinessDimension,
)

ASSESSED_AT = datetime(2026, 9, 10, tzinfo=UTC)


def profile(
    document_id: str,
    *,
    title: str = "Travel policy",
    text: str = "# Travel\n\nEmployees must submit expenses within 30 days.",
    modified_at: datetime = datetime(2026, 7, 1, tzinfo=UTC),
    owner: str | None = "Finance",
    metadata: dict[str, str] | None = None,
    topic: str | None = "Travel",
    authority: AuthorityStatus = AuthorityStatus.CANDIDATE,
    faq_count: int = 0,
    procedure_step_count: int = 0,
    assertions: tuple[BusinessAssertion, ...] = (),
) -> KnowledgeDocumentProfile:
    """Create one bounded assessment profile."""
    return KnowledgeDocumentProfile(
        document_id=document_id,
        title=title,
        text=text,
        modified_at=modified_at,
        owner=owner,
        metadata=metadata if metadata is not None else {"department": "Finance", "type": "Policy"},
        topic=topic,
        authority=authority,
        faq_count=faq_count,
        procedure_step_count=procedure_step_count,
        assertions=assertions,
    )


def travel_estate() -> tuple[KnowledgeDocumentProfile, ...]:
    """Create an estate with overlap, staleness, and a normalized contradiction."""
    return (
        profile(
            "travel-v4",
            authority=AuthorityStatus.AUTHORITATIVE,
            faq_count=2,
            procedure_step_count=2,
            assertions=(
                BusinessAssertion(
                    term="approval threshold",
                    value="GBP 100",
                    provenance="Travel policy v4, Expenses section",
                ),
            ),
        ),
        profile(
            "travel-emea",
            modified_at=datetime(2022, 1, 1, tzinfo=UTC),
            owner=None,
            metadata={},
            assertions=(
                BusinessAssertion(
                    term="approval threshold",
                    value="GBP 50",
                    provenance="EMEA travel rules, Approval section",
                ),
            ),
        ),
    )


def test_given_same_profiles_when_assessed_twice_then_result_is_deterministic() -> None:
    # Arrange
    service = EstateAssessmentService()
    profiles = travel_estate()

    # Act
    first = service.assess(
        collection_id="policies",
        profiles=profiles,
        assessed_at=ASSESSED_AT,
    )
    second = service.assess(
        collection_id="policies",
        profiles=profiles,
        assessed_at=ASSESSED_AT,
    )

    # Assert
    assert first == second


def test_given_assessable_estate_when_scored_then_all_dimensions_and_coverage_are_exposed() -> None:
    # Act
    assessment = EstateAssessmentService().assess(
        collection_id="policies",
        profiles=(profile("single"),),
        assessed_at=ASSESSED_AT,
    )

    # Assert
    assert {item.dimension for item in assessment.dimensions} == set(ReadinessDimension)
    assert 0 < assessment.coverage.coverage_percent < 100
    assert "not accuracy" in assessment.limitations[0]


def test_given_conflicting_assertions_when_assessed_then_provenance_requires_review() -> None:
    # Act
    assessment = EstateAssessmentService().assess(
        collection_id="policies",
        profiles=travel_estate(),
        assessed_at=ASSESSED_AT,
    )
    contradiction = next(
        item for item in assessment.findings if item.kind is AssessmentFindingKind.CONTRADICTION
    )

    # Assert
    assert contradiction.review_required
    assert contradiction.assertion_provenance == (
        "EMEA travel rules, Approval section",
        "Travel policy v4, Expenses section",
    )


def test_given_estate_gaps_when_assessed_then_ranked_interventions_cover_product_actions() -> None:
    # Act
    assessment = EstateAssessmentService().assess(
        collection_id="policies",
        profiles=travel_estate(),
        assessed_at=ASSESSED_AT,
    )

    # Assert
    kinds = {item.kind for item in assessment.recommendations}
    assert InterventionKind.IDENTIFY_AUTHORITATIVE_VERSIONS in kinds
    assert InterventionKind.GENERATE_METADATA in kinds
    assert InterventionKind.CREATE_AGENT_KNOWLEDGE_PACKS in kinds
    assert [item.priority for item in assessment.recommendations] == list(
        range(1, len(assessment.recommendations) + 1)
    )


def test_given_duplicate_document_ids_when_assessed_then_request_is_rejected() -> None:
    # Arrange
    duplicate = profile("same")

    # Act and assert
    with pytest.raises(ValueError, match="document IDs must be unique"):
        EstateAssessmentService().assess(
            collection_id="policies",
            profiles=(duplicate, duplicate),
            assessed_at=ASSESSED_AT,
        )


def test_given_naive_modification_time_when_profile_created_then_validation_fails() -> None:
    # Act and assert
    with pytest.raises(ValidationError, match="must include a timezone"):
        profile("policy", modified_at=datetime(2026, 1, 1))


def test_given_naive_assessment_time_when_assessed_then_validation_fails() -> None:
    # Act and assert
    with pytest.raises(ValueError, match="Assessment time must include a timezone"):
        EstateAssessmentService().assess(
            collection_id="policies",
            profiles=(profile("policy"),),
            assessed_at=datetime(2026, 9, 10),
        )


def test_given_unassessable_readability_when_assessed_then_coverage_is_reduced() -> None:
    # Act
    assessment = EstateAssessmentService().assess(
        collection_id="policies",
        profiles=(profile("symbols", text="!!!"),),
        assessed_at=ASSESSED_AT,
    )
    content_quality = next(
        item
        for item in assessment.dimensions
        if item.dimension is ReadinessDimension.CONTENT_QUALITY
    )
    readability = next(
        metric for metric in content_quality.metrics if metric.name.value == "readability"
    )

    # Assert
    assert readability.score is None
    assert content_quality.coverage_percent == 75
    assert assessment.coverage.unavailable_metric_count > 0


def test_given_future_document_when_assessed_then_invalid_evidence_is_rejected() -> None:
    # Arrange
    future = profile("future", modified_at=datetime(2027, 1, 1, tzinfo=UTC))

    # Act and assert
    with pytest.raises(ValueError, match="modification time is in the future"):
        EstateAssessmentService().assess(
            collection_id="policies",
            profiles=(future,),
            assessed_at=ASSESSED_AT,
        )


def test_given_long_paragraph_and_policy_reference_when_reported_then_effort_is_explained() -> None:
    # Arrange
    text = (
        "# Expenses\n\n"
        + " ".join(["Employees must retain evidence"] * 80)
        + ". Refer to the Global Travel Policy."
    )

    # Act
    report = DocumentAssessmentService().report(
        run_id="discover-1",
        estate_id="estate-1",
        source_version="0" * 64,
        profile=profile("expenses", text=text, owner=None, metadata={}),
        assessed_at=ASSESSED_AT,
    )

    # Assert
    assert {"long_paragraph", "cross_policy_reference"}.issubset(report.finding_codes)
    assert report.effort_points > 30
    assert report.reasons


def test_given_ownerless_document_when_reported_then_reshaping_evidence_is_unchanged() -> None:
    # Arrange
    service = DocumentAssessmentService()

    # Act
    owned = service.report(
        run_id="discover-1",
        estate_id="estate-1",
        source_version="0" * 64,
        profile=profile("owned"),
        assessed_at=ASSESSED_AT,
    )
    ownerless = service.report(
        run_id="discover-1",
        estate_id="estate-1",
        source_version="0" * 64,
        profile=profile("ownerless", owner=None),
        assessed_at=ASSESSED_AT,
    )

    # Assert
    assert ownerless.model_dump(exclude={"report_id", "document_id"}) == owned.model_dump(
        exclude={"report_id", "document_id"}
    )
