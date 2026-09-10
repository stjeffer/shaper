"""Deterministic transformation token-estimation tests."""

from __future__ import annotations

import pytest

from shaper.application.token_estimation import TokenEstimateLimitError, TokenEstimator


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
    assert first.enforced_maximum >= first.input_max + first.output_max


def test_given_large_source_when_maximum_exceeds_quota_then_estimate_is_rejected() -> None:
    # Arrange
    estimator = TokenEstimator(model_deployment="gpt-5-mini", platform_maximum=1_000)

    # Act & Assert
    with pytest.raises(TokenEstimateLimitError, match="quota"):
        estimator.estimate("word " * 1_000, ("Canonicalize", "Generate FAQ"))
