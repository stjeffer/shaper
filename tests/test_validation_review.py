"""Independent validation and review lifecycle tests."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime

import pytest

from shaper.application.review import (
    InMemoryReviewStore,
    ReviewConflictError,
    ReviewPolicy,
    ReviewService,
    RiskTier,
)
from shaper.application.validation import DeterministicValidator
from shaper.domain import (
    AnswerUnit,
    Claim,
    CollectionRole,
    Principal,
    ReviewDecision,
    SourceDocument,
    SourceSpan,
    UnitState,
)
from shaper.domain.models import Derivation, ReviewOutcome

ZERO_HASH = "0" * 64


def make_unit(document: SourceDocument, span_id: str = "span-1") -> AnswerUnit:
    """Create a candidate linked to the source fixture."""
    return AnswerUnit.create(
        source_id=document.source_id,
        source_version=document.source_version,
        canonical_questions=("How much leave is available?",),
        answer="Employees receive leave.",
        claims=(Claim(text="Employees receive leave.", span_ids=(span_id,)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.0",
            parameters_hash=ZERO_HASH,
        ),
    )


def make_span(document: SourceDocument) -> SourceSpan:
    """Create a source span."""
    text = "Employees receive leave."
    return SourceSpan(
        span_id="span-1",
        source_id=document.source_id,
        source_version=document.source_version,
        ordinal=0,
        text=text,
        text_hash=hashlib.sha256(text.encode()).hexdigest(),
    )


def reviewer() -> Principal:
    """Return a review-authorized principal."""
    return Principal(
        principal_id="reviewer-1",
        tenant_id="tenant-1",
        collection_roles={"collection-1": frozenset({CollectionRole.REVIEW})},
    )


def decision(unit: AnswerUnit, expected_revision: int) -> ReviewDecision:
    """Return an approval decision."""
    return ReviewDecision(
        decision_id="decision-1",
        unit_id=unit.unit_id,
        unit_version=unit.unit_version,
        outcome=ReviewOutcome.APPROVE,
        actor=reviewer(),
        reason="Evidence supports the answer.",
        expected_revision=expected_revision,
        decided_at=datetime(2026, 9, 9, tzinfo=UTC),
    )


def test_given_missing_cited_span_when_validated_then_finding_blocks_publication(
    source_document: SourceDocument,
) -> None:
    # Arrange
    unit = make_unit(source_document, span_id="missing")

    # Act
    findings = DeterministicValidator().validate(unit, [make_span(source_document)])

    # Assert
    assert [finding.rule_id for finding in findings] == ["grounding.span_exists"]


def test_given_valid_candidate_when_reviewed_then_only_human_approval_is_publishable(
    source_document: SourceDocument,
) -> None:
    # Arrange
    unit = make_unit(source_document)
    store = InMemoryReviewStore()
    service = ReviewService(store)
    submitted = service.submit(unit, [])

    # Act
    approved = service.decide(
        decision(unit, submitted.revision),
        expected_revision=submitted.revision,
    )

    # Assert
    assert approved.unit.state is UnitState.APPROVED
    assert service.publishable(unit.unit_id, risk=RiskTier.POLICY_RULE)


def test_given_stale_review_revision_when_approved_then_conflict_is_explicit(
    source_document: SourceDocument,
) -> None:
    # Arrange
    unit = make_unit(source_document)
    service = ReviewService(InMemoryReviewStore())
    submitted = service.submit(unit, [])

    # Act & Assert
    with pytest.raises(ReviewConflictError, match="Stale"):
        service.decide(decision(unit, submitted.revision), expected_revision=0)


def test_given_unapproved_thresholds_when_policy_checked_then_all_units_require_review(
    source_document: SourceDocument,
) -> None:
    # Arrange
    unit = make_unit(source_document)

    # Act
    required = ReviewPolicy().requires_review(unit, RiskTier.LOW_RISK_FAQ)

    # Assert
    assert required is True
