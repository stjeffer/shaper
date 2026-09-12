"""Estate assessment domain and service tests."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from shaper.application.assessment import DocumentAssessmentService, EstateAssessmentService
from shaper.application.document_findings import (
    DOCUMENT_CHECK_CODES,
    assess_document_findings,
)
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
    assert all(finding.evidence for finding in report.findings)
    assert all(finding.agent_impact for finding in report.findings)


@pytest.mark.parametrize(
    ("expected_code", "text", "peer_text"),
    (
        ("external_dependency", "See the Global Travel Policy.", None),
        (
            "circular_reference",
            "# Section A\n\nSee Section B.\n\n# Section B\n\nSee Section A.",
            None,
        ),
        ("missing_referenced_content", "See Appendix C for the complete table.", None),
        ("version_ambiguity", "Employees submit requests to HR.", None),
        ("orphaned_amendment", "Per the Q2 memo, this rule has changed.", None),
        ("vague_quantifier", "Requests are generally completed approximately weekly.", None),
        ("discretion_clause", "Exceptions are granted at the manager's discretion.", None),
        (
            "undefined_term",
            'An "Exempt Employee" may apply. Each "Exempt Employee" must register.',
            None,
        ),
        ("unclear_responsibility", "The request will be reviewed within 30 days.", None),
        (
            "conflicting_numeric_value",
            "Employees submit expenses within 30 days. Employees submit expenses within 60 days.",
            None,
        ),
        (
            "conflicting_authority",
            "The handbook controls all requests. The local addendum overrides the handbook.",
            None,
        ),
        (
            "terminology_drift",
            '"Complaint" means a report of workplace misconduct. '
            '"Covered Report" means a report of workplace misconduct.',
            None,
        ),
        ("missing_definitions", "Terms are defined in the Definitions section.", None),
        ("missing_enumeration", "Leave entitlement varies by state.", None),
        ("dangling_program", "The travel pilot applies to contractors.", None),
        (
            "unclear_source_of_truth",
            "The most recent communication governs this policy.",
            None,
        ),
        (
            "undocumented_verbal_policy",
            "The exception was clarified verbally in an all-hands.",
            None,
        ),
        (
            "restricted_companion",
            "The confidential Severance Guidelines document contains the required rule.",
            None,
        ),
        (
            "inconsistent_heading_hierarchy",
            "# Policy\n\nCurrent rule.\n\n### Exceptions\n\nSpecial rule.",
            None,
        ),
        ("inaccessible_embedded_content", "See the chart below.\n\n![](chart.png)", None),
        (
            "repeated_variation",
            "Employees must submit travel expenses within 30 calendar days.\n\n"
            "Employees should submit travel expenses within 30 working days.",
            None,
        ),
        (
            "noncanonical_duplicate",
            "Employees submit approved travel expenses through the finance portal.",
            "Employees submit approved travel expenses through the finance portal.",
        ),
    ),
)
def test_given_requested_document_risk_when_checked_then_evidence_is_reported(
    expected_code: str,
    text: str,
    peer_text: str | None,
) -> None:
    # Arrange
    assert DOCUMENT_CHECK_CODES == (
        "external_dependency",
        "circular_reference",
        "missing_referenced_content",
        "version_ambiguity",
        "orphaned_amendment",
        "vague_quantifier",
        "discretion_clause",
        "undefined_term",
        "unclear_responsibility",
        "conflicting_numeric_value",
        "conflicting_authority",
        "terminology_drift",
        "missing_definitions",
        "missing_enumeration",
        "dangling_program",
        "unclear_source_of_truth",
        "undocumented_verbal_policy",
        "restricted_companion",
        "inconsistent_heading_hierarchy",
        "inaccessible_embedded_content",
        "repeated_variation",
        "noncanonical_duplicate",
    )
    current = profile("current", text=text)
    peers = () if peer_text is None else (profile("peer", text=peer_text),)

    # Act
    findings = assess_document_findings(current, peers)

    # Assert
    finding = next(item for item in findings if item.code == expected_code)
    assert finding.review_required
    assert finding.evidence
    assert finding.agent_impact


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
