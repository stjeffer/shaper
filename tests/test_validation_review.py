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


def preservation_rule_ids(
    document: SourceDocument,
    source_text: str,
    candidate_text: str,
) -> set[str]:
    """Validate a candidate against a single source span."""
    span = SourceSpan(
        span_id="span-1",
        source_id=document.source_id,
        source_version=document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=document.source_id,
        source_version=document.source_version,
        canonical_questions=("What does the policy require?",),
        answer=candidate_text,
        claims=(Claim(text=candidate_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-preservation",
            model="fake",
            prompt_version="1.7",
            parameters_hash=ZERO_HASH,
        ),
    )
    return {finding.rule_id for finding in DeterministicValidator().validate(unit, [span])}


def test_given_missing_cited_span_when_validated_then_finding_blocks_publication(
    source_document: SourceDocument,
) -> None:
    # Arrange
    unit = make_unit(source_document, span_id="missing")

    # Act
    findings = DeterministicValidator().validate(unit, [make_span(source_document)])

    # Assert
    assert [finding.rule_id for finding in findings] == ["grounding.span_exists"]


def test_given_policy_summary_when_validated_then_content_loss_blocks_publication(
    source_document: SourceDocument,
) -> None:
    source_text = (
        "Employees must submit annual leave requests at least 20 working days in advance. "
        "Managers must respond within 5 working days. Employees receive 25 days of annual "
        "leave each year. Requests longer than 10 days require director approval. "
        "Emergency leave may only be approved when supporting evidence is provided. "
        "Unused leave cannot be carried forward unless HR provides written approval."
    )
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("How does annual leave work?",),
        answer="Employees should request leave in advance and speak to their manager.",
        claims=(
            Claim(
                text="Employees should request leave in advance.",
                span_ids=("span-1",),
            ),
        ),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.1",
            parameters_hash=ZERO_HASH,
        ),
    )

    findings = DeterministicValidator().validate(unit, [span])

    assert {
        "content.source_coverage",
        "content.material_fact",
        "content.operative_clause",
    }.issubset({finding.rule_id for finding in findings})


def test_given_restructured_complete_policy_when_validated_then_preservation_passes(
    source_document: SourceDocument,
) -> None:
    source_text = (
        "Employees must submit requests 20 days in advance. "
        "Managers must respond within 5 days. "
        "Unused leave cannot be carried forward without HR approval."
    )
    answer = (
        "# Annual leave requests\n"
        "- Employees must submit requests 20 days in advance.\n"
        "- Managers must respond within 5 days.\n"
        "- Unused leave cannot be carried forward without HR approval."
    )
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("How are annual leave requests handled?",),
        answer=answer,
        claims=(Claim(text=source_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.1",
            parameters_hash=ZERO_HASH,
        ),
    )

    findings = DeterministicValidator().validate(unit, [span])

    assert not [finding for finding in findings if finding.rule_id.startswith("content.")]


def test_given_compound_duty_split_into_bullets_when_validated_then_clause_passes(
    source_document: SourceDocument,
) -> None:
    source_text = (
        "The contractor must maintain insurance, shall indemnify the client against all "
        "losses, and is responsible for ensuring subcontractors comply with the policy."
    )
    answer = (
        "# Contractor duties\n"
        "- The contractor must maintain insurance.\n"
        "- The contractor shall indemnify the client against all losses.\n"
        "- The contractor is responsible for ensuring subcontractors comply with the policy."
    )
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("What must the contractor do?",),
        answer=answer,
        claims=(Claim(text=source_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.1",
            parameters_hash=ZERO_HASH,
        ),
    )

    findings = DeterministicValidator().validate(unit, [span])

    assert "content.operative_clause" not in {finding.rule_id for finding in findings}


def test_given_advisory_permission_and_exception_omitted_when_validated_then_each_blocks(
    source_document: SourceDocument,
) -> None:
    source_text = (
        "Employees should notify their manager before travel. "
        "They may work remotely except during security incidents. "
        "Contractors can access systems unless their credentials expire. "
        "Employees must not share badges. "
        "The May 2026 training calendar is available."
    )
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("When can employees work remotely?",),
        answer="The May 2026 training calendar is available.",
        claims=(
            Claim(
                text="The May 2026 training calendar is available.",
                span_ids=("span-1",),
            ),
        ),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.5",
            parameters_hash=ZERO_HASH,
        ),
    )

    rule_ids = {finding.rule_id for finding in DeterministicValidator().validate(unit, [span])}

    assert {
        "content.advisory_clause",
        "content.permission_clause",
        "content.prohibition_clause",
        "content.exception_clause",
        "content.operative_clause",
    } <= rule_ids


def test_given_advisory_permission_and_exception_restructured_when_validated_then_passes(
    source_document: SourceDocument,
) -> None:
    source_text = (
        "Employees should notify their manager before travel. "
        "They may work remotely except during security incidents. "
        "Contractors can access systems unless their credentials expire. "
        "Employees must not share badges. "
        "The May 2026 training calendar is available."
    )
    answer = (
        "# Travel and access\n"
        "- Employees should notify their manager before travel.\n"
        "- They may work remotely except during security incidents.\n"
        "- Contractors can access systems unless their credentials expire.\n"
        "- Employees must not share badges.\n"
        "- The May 2026 training calendar is available."
    )
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("What travel and access rules apply?",),
        answer=answer,
        claims=(Claim(text=source_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.5",
            parameters_hash=ZERO_HASH,
        ),
    )

    findings = DeterministicValidator().validate(unit, [span])

    assert not [finding for finding in findings if finding.rule_id.startswith("content.")]


def test_given_restrictive_permission_qualifier_omitted_when_validated_then_blocks(
    source_document: SourceDocument,
) -> None:
    source_text = "Employees may access records only with manager approval."
    candidate_text = "Employees may access records with manager approval."
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("When may employees access records?",),
        answer=candidate_text,
        claims=(Claim(text=candidate_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.5",
            parameters_hash=ZERO_HASH,
        ),
    )

    rule_ids = {finding.rule_id for finding in DeterministicValidator().validate(unit, [span])}

    assert "content.qualifier_clause" in rule_ids


def test_given_modal_and_qualifier_moved_to_another_clause_when_validated_then_blocks(
    source_document: SourceDocument,
) -> None:
    source_text = (
        "Employees may access records only with manager approval. "
        "Contractors may access records with security approval."
    )
    candidate_text = (
        "Employees access records with manager approval. "
        "Contractors may access records only with security approval."
    )
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("Who may access records?",),
        answer=candidate_text,
        claims=(Claim(text=candidate_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.5",
            parameters_hash=ZERO_HASH,
        ),
    )

    rule_ids = {finding.rule_id for finding in DeterministicValidator().validate(unit, [span])}

    assert "content.permission_clause" in rule_ids
    assert "content.qualifier_clause" in rule_ids


def test_given_reordered_similar_clauses_move_restrictions_when_validated_then_blocks(
    source_document: SourceDocument,
) -> None:
    source_text = (
        "Employees may access records only with manager approval. "
        "Employees can access archives with manager approval."
    )
    candidate_text = (
        "Employees may access archives only with manager approval. "
        "Employees can access records with manager approval."
    )
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("What may employees access?",),
        answer=candidate_text,
        claims=(Claim(text=candidate_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.5",
            parameters_hash=ZERO_HASH,
        ),
    )

    rule_ids = {finding.rule_id for finding in DeterministicValidator().validate(unit, [span])}

    assert "content.permission_clause" in rule_ids
    assert "content.qualifier_clause" in rule_ids


def test_given_modal_attachment_swapped_between_subjects_when_validated_then_blocks(
    source_document: SourceDocument,
) -> None:
    source_text = "Employees may submit requests. Contractors can submit requests."
    candidate_text = "Employees can submit requests. Contractors may submit requests."
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("Who may submit requests?",),
        answer=candidate_text,
        claims=(Claim(text=candidate_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.5",
            parameters_hash=ZERO_HASH,
        ),
    )

    rule_ids = {finding.rule_id for finding in DeterministicValidator().validate(unit, [span])}

    assert "content.permission_clause" in rule_ids


def test_given_mandatory_duty_weakened_to_permission_when_validated_then_blocks(
    source_document: SourceDocument,
) -> None:
    source_text = "Employees must submit requests."
    candidate_text = "Employees may submit requests."
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("Must employees submit requests?",),
        answer=candidate_text,
        claims=(Claim(text=candidate_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.5",
            parameters_hash=ZERO_HASH,
        ),
    )

    rule_ids = {finding.rule_id for finding in DeterministicValidator().validate(unit, [span])}

    assert "content.operative_clause" in rule_ids
    assert "content.permission_clause" in rule_ids


def test_given_mandatory_duty_reversed_to_prohibition_when_validated_then_blocks(
    source_document: SourceDocument,
) -> None:
    source_text = "Employees must submit requests."
    candidate_text = "Employees must not submit requests."
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("Must employees submit requests?",),
        answer=candidate_text,
        claims=(Claim(text=candidate_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.5",
            parameters_hash=ZERO_HASH,
        ),
    )

    rule_ids = {finding.rule_id for finding in DeterministicValidator().validate(unit, [span])}

    assert "content.prohibition_clause" in rule_ids


@pytest.mark.parametrize(
    ("source_text", "candidate_text", "expected_rule"),
    [
        (
            "Employees are required to submit timesheets.",
            "Employees are not required to submit timesheets.",
            "content.operative_clause",
        ),
        (
            "Employees are prohibited from sharing badges.",
            "Employees are not prohibited from sharing badges.",
            "content.prohibition_clause",
        ),
    ],
)
def test_given_named_modality_negated_when_validated_then_blocks(
    source_document: SourceDocument,
    source_text: str,
    candidate_text: str,
    expected_rule: str,
) -> None:
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("What rule applies?",),
        answer=candidate_text,
        claims=(Claim(text=candidate_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.5",
            parameters_hash=ZERO_HASH,
        ),
    )

    rule_ids = {finding.rule_id for finding in DeterministicValidator().validate(unit, [span])}

    assert expected_rule in rule_ids


@pytest.mark.parametrize(
    ("source_text", "candidate_text"),
    [
        (
            "Employees are required to submit timesheets.",
            "Employees are no longer required to submit timesheets.",
        ),
        (
            "Employees are prohibited from sharing badges.",
            "Employees are no longer prohibited from sharing badges.",
        ),
    ],
)
def test_given_named_modality_changed_to_no_longer_when_validated_then_blocks(
    source_document: SourceDocument,
    source_text: str,
    candidate_text: str,
) -> None:
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("What rule applies?",),
        answer=candidate_text,
        claims=(Claim(text=candidate_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.5",
            parameters_hash=ZERO_HASH,
        ),
    )

    rule_ids = {finding.rule_id for finding in DeterministicValidator().validate(unit, [span])}

    assert "content.operative_clause" in rule_ids


@pytest.mark.parametrize(
    ("source_text", "candidate_text"),
    [
        (
            "Employees will not disclose confidential records.",
            "Employees will disclose confidential records.",
        ),
        (
            "Employees will disclose approved records.",
            "Employees will not disclose approved records.",
        ),
    ],
)
def test_given_will_not_polarity_reversed_when_validated_then_blocks(
    source_document: SourceDocument,
    source_text: str,
    candidate_text: str,
) -> None:
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("May employees disclose records?",),
        answer=candidate_text,
        claims=(Claim(text=candidate_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.5",
            parameters_hash=ZERO_HASH,
        ),
    )

    rule_ids = {finding.rule_id for finding in DeterministicValidator().validate(unit, [span])}

    assert "content.prohibition_clause" in rule_ids


def test_given_temporal_attachment_swapped_between_conditions_when_validated_then_blocks(
    source_document: SourceDocument,
) -> None:
    source_text = (
        "Employees submit requests before manager approval. "
        "Employees submit reports after training."
    )
    candidate_text = (
        "Employees submit requests after manager approval. "
        "Employees submit reports before training."
    )
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("When do employees submit requests and reports?",),
        answer=candidate_text,
        claims=(Claim(text=candidate_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.5",
            parameters_hash=ZERO_HASH,
        ),
    )

    rule_ids = {finding.rule_id for finding in DeterministicValidator().validate(unit, [span])}

    assert "content.qualifier_clause" in rule_ids


def test_given_unchanged_temporal_clauses_reordered_when_validated_then_passes(
    source_document: SourceDocument,
) -> None:
    source_text = (
        "Employees submit requests before manager approval. "
        "Employees submit reports after training."
    )
    candidate_text = (
        "Employees submit reports after training. "
        "Employees submit requests before manager approval."
    )
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("When do employees submit requests and reports?",),
        answer=candidate_text,
        claims=(Claim(text=candidate_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.5",
            parameters_hash=ZERO_HASH,
        ),
    )

    rule_ids = {finding.rule_id for finding in DeterministicValidator().validate(unit, [span])}

    assert "content.qualifier_clause" not in rule_ids


def test_given_similar_control_only_clauses_reordered_when_validated_then_passes(
    source_document: SourceDocument,
) -> None:
    source_text = "Employees may submit requests. Employees can submit requests."
    candidate_text = "Employees can submit requests. Employees may submit requests."
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("How can employees submit requests?",),
        answer=candidate_text,
        claims=(Claim(text=candidate_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.5",
            parameters_hash=ZERO_HASH,
        ),
    )

    rule_ids = {finding.rule_id for finding in DeterministicValidator().validate(unit, [span])}

    assert "content.permission_clause" not in rule_ids


def test_given_substantive_declarative_clause_omitted_when_validated_then_blocks(
    source_document: SourceDocument,
) -> None:
    source_text = (
        "The benefit applies to permanent employees in the United Kingdom. "
        "New employees become eligible after completing probation. "
        "Coverage ends when employment terminates."
    )
    candidate_text = "The benefit applies to permanent employees in the United Kingdom."
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("Who receives the benefit?",),
        answer=candidate_text,
        claims=(Claim(text=candidate_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.5",
            parameters_hash=ZERO_HASH,
        ),
    )

    rule_ids = {finding.rule_id for finding in DeterministicValidator().validate(unit, [span])}

    assert "content.material_clause" in rule_ids


def test_given_short_temporal_condition_omitted_when_validated_then_blocks(
    source_document: SourceDocument,
) -> None:
    source_text = (
        "The benefit applies to permanent employees during probation. "
        "The benefit applies to permanent employees after probation."
    )
    candidate_text = (
        "The benefit applies to permanent employees. "
        "The benefit applies to permanent employees after probation."
    )
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("When does the benefit apply?",),
        answer=candidate_text,
        claims=(Claim(text=candidate_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.5",
            parameters_hash=ZERO_HASH,
        ),
    )

    rule_ids = {finding.rule_id for finding in DeterministicValidator().validate(unit, [span])}

    assert "content.qualifier_clause" in rule_ids


def test_given_repeated_vocabulary_hides_omitted_condition_when_validated_then_blocks(
    source_document: SourceDocument,
) -> None:
    source_text = (
        "The benefit applies to permanent employees in the United Kingdom. "
        "The benefit applies to permanent employees after completing probation."
    )
    candidate_text = "The benefit applies to permanent employees in the United Kingdom."
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("Who receives the benefit?",),
        answer=candidate_text,
        claims=(Claim(text=candidate_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.5",
            parameters_hash=ZERO_HASH,
        ),
    )

    rule_ids = {finding.rule_id for finding in DeterministicValidator().validate(unit, [span])}

    assert "content.material_clause" in rule_ids


def test_given_one_candidate_clause_for_two_subjects_when_validated_then_omission_blocks(
    source_document: SourceDocument,
) -> None:
    source_text = (
        "Employees receive the benefit in the United Kingdom. "
        "Contractors receive the benefit in the United Kingdom."
    )
    candidate_text = "Employees receive the benefit in the United Kingdom."
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("Who receives the benefit?",),
        answer=candidate_text,
        claims=(Claim(text=candidate_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.5",
            parameters_hash=ZERO_HASH,
        ),
    )

    rule_ids = {finding.rule_id for finding in DeterministicValidator().validate(unit, [span])}

    assert "content.material_clause" in rule_ids


def test_given_one_source_list_expanded_to_exact_bullets_when_validated_then_passes(
    source_document: SourceDocument,
) -> None:
    source_text = (
        "Employees receive health insurance, pension contributions, dental coverage, "
        "and vision coverage."
    )
    candidate_text = (
        "Employees receive:\n"
        "- Health insurance.\n"
        "- Pension contributions.\n"
        "- Dental coverage.\n"
        "- Vision coverage."
    )
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("What benefits do employees receive?",),
        answer=candidate_text,
        claims=(Claim(text=source_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.5",
            parameters_hash=ZERO_HASH,
        ),
    )

    rule_ids = {finding.rule_id for finding in DeterministicValidator().validate(unit, [span])}

    assert "content.material_clause" not in rule_ids


def test_given_list_fragments_mask_omitted_scope_when_validated_then_blocks(
    source_document: SourceDocument,
) -> None:
    source_text = (
        "Employees receive health insurance, pension contributions, dental coverage, "
        "and vision coverage. "
        "Employees receive health insurance in the United Kingdom."
    )
    candidate_text = (
        "Employees receive:\n"
        "- Health insurance.\n"
        "- Pension contributions.\n"
        "- Dental coverage.\n"
        "- Vision coverage."
    )
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("What benefits do employees receive?",),
        answer=candidate_text,
        claims=(Claim(text=candidate_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.5",
            parameters_hash=ZERO_HASH,
        ),
    )

    rule_ids = {finding.rule_id for finding in DeterministicValidator().validate(unit, [span])}

    assert "content.material_clause" in rule_ids


def test_given_governing_modal_repeated_across_bullets_when_validated_then_passes(
    source_document: SourceDocument,
) -> None:
    source_text = "Employees must submit forms and receipts."
    candidate_text = (
        "Employees must submit:\n- Employees must submit forms.\n- Employees must submit receipts."
    )
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("What must employees submit?",),
        answer=candidate_text,
        claims=(Claim(text=source_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.5",
            parameters_hash=ZERO_HASH,
        ),
    )

    rule_ids = {finding.rule_id for finding in DeterministicValidator().validate(unit, [span])}

    assert "content.operative_clause" not in rule_ids


def test_given_faithful_eligibility_paraphrase_when_validated_then_material_clause_passes(
    source_document: SourceDocument,
) -> None:
    source_text = "New employees become eligible after completing probation."
    candidate_text = "Eligibility begins once probation has been completed."
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("When does eligibility begin?",),
        answer=candidate_text,
        claims=(Claim(text=candidate_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.5",
            parameters_hash=ZERO_HASH,
        ),
    )

    rule_ids = {finding.rule_id for finding in DeterministicValidator().validate(unit, [span])}

    assert "content.material_clause" not in rule_ids


def test_given_regular_inflection_paraphrase_when_validated_then_material_clause_passes(
    source_document: SourceDocument,
) -> None:
    source_text = "Employees submit requests after manager approval."
    candidate_text = "An employee submits a request once a manager approves it."
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("When does an employee submit a request?",),
        answer=candidate_text,
        claims=(Claim(text=candidate_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.5",
            parameters_hash=ZERO_HASH,
        ),
    )

    rule_ids = {finding.rule_id for finding in DeterministicValidator().validate(unit, [span])}

    assert "content.material_clause" not in rule_ids
    assert "content.qualifier_clause" not in rule_ids


def test_given_shorter_number_omitted_when_validated_then_material_fact_blocks(
    source_document: SourceDocument,
) -> None:
    source_text = "Managers respond within 5 days. Employees receive 25 days annual leave."
    answer = "Employees receive 25 days annual leave."
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("How much annual leave do employees receive?",),
        answer=answer,
        claims=(Claim(text=answer, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.1",
            parameters_hash=ZERO_HASH,
        ),
    )

    findings = DeterministicValidator().validate(unit, [span])

    assert "content.material_fact" in {finding.rule_id for finding in findings}


def test_given_material_facts_swapped_between_subjects_when_validated_then_blocks(
    source_document: SourceDocument,
) -> None:
    source_text = "Employees receive 25 days leave. Contractors receive 10 days leave."
    candidate_text = "Employees receive 10 days leave. Contractors receive 25 days leave."
    span = SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=source_text,
        text_hash=hashlib.sha256(source_text.encode()).hexdigest(),
    )
    unit = AnswerUnit.create(
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        canonical_questions=("How much leave is provided?",),
        answer=candidate_text,
        claims=(Claim(text=candidate_text, span_ids=("span-1",)),),
        confidence=0.9,
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.5",
            parameters_hash=ZERO_HASH,
        ),
    )

    rule_ids = {finding.rule_id for finding in DeterministicValidator().validate(unit, [span])}

    assert "content.material_fact" in rule_ids


def test_given_merged_source_clauses_when_all_subjects_are_retained_then_passes(
    source_document: SourceDocument,
) -> None:
    source_text = (
        "Employees may access records only with manager approval. "
        "Contractors can access archives after security approval."
    )
    candidate_text = (
        "Employees may access records only with manager approval, while contractors can "
        "access archives after security approval."
    )

    rule_ids = preservation_rule_ids(source_document, source_text, candidate_text)

    assert not {
        "content.material_clause",
        "content.permission_clause",
        "content.qualifier_clause",
    }.intersection(rule_ids)


@pytest.mark.parametrize(
    ("source_text", "candidate_text", "expected_rule"),
    [
        (
            "Employees receive 10 vacation days. Contractors receive 20 vacation days.",
            "Employees receive 20 vacation days, while contractors receive 10 vacation days.",
            "content.material_fact",
        ),
        (
            "Employees may access records only with manager approval. "
            "Contractors can access archives after security approval.",
            "Employees may access archives after security approval, while contractors can "
            "access records only with manager approval.",
            "content.qualifier_clause",
        ),
        (
            "Employees must submit the form. Contractors must not submit the form.",
            "Employees must not submit the form; contractors must submit the form.",
            "content.prohibition_clause",
        ),
    ],
)
def test_given_merged_clause_swaps_source_attributes_when_validated_then_blocks(
    source_document: SourceDocument,
    source_text: str,
    candidate_text: str,
    expected_rule: str,
) -> None:
    rule_ids = preservation_rule_ids(source_document, source_text, candidate_text)

    assert expected_rule in rule_ids


def test_given_reordered_qa_with_advisory_and_temporal_qualifiers_then_passes(
    source_document: SourceDocument,
) -> None:
    source_text = (
        "Meridian Holdings — Employee Benefits Handbook\n"
        "Employees should contact HR after enrollment changes. "
        "Employees should retain receipts during claims review."
    )
    candidate_text = (
        "# Meridian Holdings — Employee Benefits Handbook\n"
        "## What should employees retain during claims review?\n"
        "Employees should retain receipts during claims review.\n"
        "## What should employees do after enrollment changes?\n"
        "Employees should contact HR after enrollment changes."
    )

    rule_ids = preservation_rule_ids(source_document, source_text, candidate_text)

    assert not {
        "content.material_clause",
        "content.advisory_clause",
        "content.qualifier_clause",
    }.intersection(rule_ids)


def test_given_added_list_numbering_when_policy_facts_are_unchanged_then_passes(
    source_document: SourceDocument,
) -> None:
    source_text = "Employees submit a request. Managers review the request."
    candidate_text = "1. Employees submit a request.\n2. Managers review the request."

    rule_ids = preservation_rule_ids(source_document, source_text, candidate_text)

    assert "content.material_fact" not in rule_ids


def test_given_source_unsupported_number_when_validated_then_blocks(
    source_document: SourceDocument,
) -> None:
    source_text = "Employees submit a request. Managers review the request."
    candidate_text = "Employees submit a request. Managers review it within 5 days."

    rule_ids = preservation_rule_ids(source_document, source_text, candidate_text)

    assert "content.material_fact" in rule_ids


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
