"""Advisory model-assisted candidate quality evaluation."""

from __future__ import annotations

import json
from collections.abc import Sequence

from pydantic import BaseModel, ConfigDict, Field

from shaper.application.ports import ModelGateway
from shaper.domain import AnswerUnit, SourceSpan
from shaper.domain.models import canonical_hash

RUBRIC_VERSION = "1.0"


class QualityScores(BaseModel):
    """Bounded advisory quality scores."""

    model_config = ConfigDict(extra="forbid")

    groundedness: float = Field(ge=0, le=1)
    completeness: float = Field(ge=0, le=1)
    qualifier_coverage: float = Field(ge=0, le=1)
    abstention_quality: float = Field(ge=0, le=1)
    task_adherence: float = Field(ge=0, le=1)
    rationale_summary: str = Field(min_length=1, max_length=1000)


class EvaluationEvidence(BaseModel):
    """Pinned evaluator result used as review evidence, never authority."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    evaluator: str
    rubric_version: str
    input_hash: str
    response_id: str
    scores: QualityScores


class ModelAssistedEvaluator:
    """Evaluate semantic quality through the configured model gateway."""

    def __init__(self, gateway: ModelGateway, *, evaluator_name: str) -> None:
        self._gateway = gateway
        self._evaluator_name = evaluator_name

    def evaluate(
        self,
        unit: AnswerUnit,
        spans: Sequence[SourceSpan],
    ) -> EvaluationEvidence:
        """Return recorded advisory evidence or raise an explicit provider error."""
        evaluation_input = {
            "unit": unit.model_dump(mode="json"),
            "source_spans": [span.model_dump(mode="json") for span in spans],
            "rubric": {
                "version": RUBRIC_VERSION,
                "criteria": [
                    "groundedness",
                    "completeness",
                    "qualifier_coverage",
                    "abstention_quality",
                    "task_adherence",
                ],
            },
        }
        result = self._gateway.generate(
            prompt=json.dumps(evaluation_input, sort_keys=True),
            schema=QualityScores.model_json_schema(),
        )
        return EvaluationEvidence(
            evaluator=self._evaluator_name,
            rubric_version=RUBRIC_VERSION,
            input_hash=canonical_hash(evaluation_input),
            response_id=result.response_id,
            scores=QualityScores.model_validate(result.payload),
        )
