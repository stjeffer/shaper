"""Model-assisted evaluation evidence tests."""

from __future__ import annotations

from shaper.application.evaluation import ModelAssistedEvaluator
from shaper.application.model import DeterministicModelGateway
from shaper.domain import SourceDocument
from tests.test_validation_review import make_span, make_unit


def test_given_evaluator_scores_when_evaluated_then_identity_and_input_are_pinned(
    source_document: SourceDocument,
) -> None:
    # Arrange
    gateway = DeterministicModelGateway(
        [
            {
                "groundedness": 1.0,
                "completeness": 0.9,
                "qualifier_coverage": 0.8,
                "abstention_quality": 1.0,
                "task_adherence": 1.0,
                "rationale_summary": "Claims are supported.",
            }
        ]
    )

    # Act
    result = ModelAssistedEvaluator(gateway, evaluator_name="fake-evaluator").evaluate(
        make_unit(source_document),
        [make_span(source_document)],
    )

    # Assert
    assert result.evaluator == "fake-evaluator"
    assert len(result.input_hash) == 64
