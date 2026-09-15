"""Model-assisted evaluation evidence tests."""

from __future__ import annotations

from shaper.application.evaluation import ModelAssistedEvaluator
from shaper.application.ports import ModelResult
from shaper.domain import SourceDocument
from shaper.prompts import EVALUATION_PROMPT
from tests.test_validation_review import make_span, make_unit


class CapturingGateway:
    """Capture the evaluator's selected system prompt."""

    def __init__(self) -> None:
        self.system_prompt = ""

    def generate(
        self,
        *,
        system_prompt: str,
        prompt: str,
        schema: dict[str, object],
        max_output_tokens: int | None = None,
    ) -> ModelResult:
        del prompt, schema, max_output_tokens
        self.system_prompt = system_prompt
        return ModelResult(
            payload={
                "groundedness": 1.0,
                "completeness": 0.9,
                "qualifier_coverage": 0.8,
                "abstention_quality": 1.0,
                "task_adherence": 1.0,
                "rationale_summary": "Claims are supported.",
            },
            response_id="response-1",
            input_tokens=10,
            output_tokens=10,
        )


def test_given_evaluator_scores_when_evaluated_then_identity_and_input_are_pinned(
    source_document: SourceDocument,
) -> None:
    # Arrange
    gateway = CapturingGateway()

    # Act
    result = ModelAssistedEvaluator(gateway, evaluator_name="fake-evaluator").evaluate(
        make_unit(source_document),
        [make_span(source_document)],
    )

    # Assert
    assert result.evaluator == "fake-evaluator"
    assert len(result.input_hash) == 64
    assert gateway.system_prompt == EVALUATION_PROMPT
