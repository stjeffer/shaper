"""Deterministic transformation token-estimation tests."""

from __future__ import annotations

import pytest

from shaper.application.token_estimation import (
    ESTIMATED_MODEL_CALLS,
    ESTIMATOR_VERSION,
    TokenEstimateLimitError,
    TokenEstimator,
)
from shaper.domain import DocumentFinding, DocumentFindingEvidence


def test_given_equivalent_inputs_when_estimated_then_range_and_identity_are_stable() -> None:
    # Arrange
    estimator = TokenEstimator(model_deployment="gpt-5-mini")

    # Act
    first = estimator.estimate("Employees receive leave.", ("Generate FAQ",))
    second = estimator.estimate("Employees receive leave.", ("Generate FAQ",))

    # Assert
    assert first == second
    assert first.input_min <= first.input_max
    assert first.output_min <= first.output_max
    assert first.estimator_version == ESTIMATOR_VERSION == "1.7"
    assert first.prompt_hash is not None
    assert ESTIMATED_MODEL_CALLS == 2
    assert first.enforced_maximum >= ESTIMATED_MODEL_CALLS * (first.input_max + first.output_max)
    assert first.enforced_maximum >= (2 * first.input_max) + (3 * first.output_max)
    assert first.output_max >= 2_100
    assert "reasoning-token reserve" in first.assumptions[2]
    assert "one targeted repair attempt" in first.assumptions[-1]


def test_given_assessment_evidence_when_estimated_then_request_overhead_is_reserved() -> None:
    estimator = TokenEstimator(model_deployment="gpt-5-mini")
    finding = DocumentFinding(
        code="procedure_gap",
        label="Implicit procedure",
        explanation="Procedural language is not organized into explicit steps.",
        agent_impact="The agent may present an unreliable sequence.",
        severity="warning",
        evidence=(DocumentFindingEvidence(quote="Submit the form.", location="line 4"),),
    )

    without_findings = estimator.estimate("Submit the form.", ("Reformat as steps",))
    with_findings = estimator.estimate(
        "Submit the form.",
        ("Reformat as steps",),
        assessment_findings=(finding,),
    )

    assert with_findings.input_min > without_findings.input_min
    assert with_findings.input_max > without_findings.input_max
    assert with_findings.estimate_id != without_findings.estimate_id


def test_given_large_source_when_maximum_exceeds_quota_then_estimate_is_rejected() -> None:
    # Arrange
    estimator = TokenEstimator(model_deployment="gpt-5-mini", platform_maximum=1_000)

    # Act & Assert
    with pytest.raises(TokenEstimateLimitError, match="quota"):
        estimator.estimate("word " * 1_000, ("Canonicalize", "Generate FAQ"))


def test_given_typical_long_policy_when_default_limit_used_then_estimate_is_allowed() -> None:
    estimator = TokenEstimator(model_deployment="gpt-5-mini")

    estimate = estimator.estimate(
        "Employees must retain receipt evidence before reimbursement. " * 1_000,
        ("Restructure long passages for retrieval.",),
    )

    assert estimate.enforced_maximum > 100_000
    assert estimate.enforced_maximum <= 200_000
