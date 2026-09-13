"""Bounded, checkpointed answer-shaping loop."""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from shaper.application.agent_tools import ReadOnlyToolRegistry, ToolRequest
from shaper.application.model import PROMPT_VERSION, SHAPING_PROMPT
from shaper.application.ports import ModelGateway, Validator
from shaper.domain import (
    AnswerUnit,
    Applicability,
    Claim,
    Principal,
    SourceDocument,
    SourceSpan,
)
from shaper.domain.models import Derivation, FindingSeverity, canonical_hash


class CheckpointStore(Protocol):
    """Durable shaping checkpoint boundary."""

    def save(self, run_id: str, state: str, payload: str) -> None:
        """Persist one idempotent checkpoint."""


class CandidateClaimPayload(BaseModel):
    """JSON-compatible claim fields returned by the model."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    span_ids: tuple[str, ...] = Field(min_length=1)
    qualifiers: tuple[str, ...] = ()


class CandidatePayload(BaseModel):
    """Model-produced candidate fields before deterministic identity assignment."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["candidate", "tool", "abstain"]
    canonical_questions: tuple[str, ...] = ()
    answer: str = ""
    claims: tuple[CandidateClaimPayload, ...] = ()
    confidence: float = Field(default=0, ge=0, le=1)
    applicability: Applicability = Field(default_factory=Applicability)
    reason: str | None = None
    tool: ToolRequest | None = None


@dataclass(frozen=True)
class ShapingBudget:
    """Independent hard limits for one shaping run."""

    maximum_model_calls: int = 4
    maximum_tool_calls: int = 8
    maximum_tokens: int = 8_000
    maximum_seconds: float = 120
    maximum_candidates: int = 4


@dataclass(frozen=True)
class ShapingOutcome:
    """Terminal shaping result and accounting."""

    unit: AnswerUnit | None
    abstained: bool
    reason: str
    model_calls: int
    tool_calls: int
    input_tokens: int
    output_tokens: int

    @property
    def tokens(self) -> int:
        """Return total provider-reported token usage."""
        return self.input_tokens + self.output_tokens


class ShapingBudgetExceeded(RuntimeError):
    """Raised when any independent shaping budget is exhausted."""

    def __init__(
        self,
        message: str,
        *,
        input_tokens: int = 0,
        output_tokens: int = 0,
        model_calls: int = 0,
    ) -> None:
        super().__init__(message)
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.model_calls = model_calls


class ShapingCancelled(RuntimeError):
    """Raised when a caller cancels the shaping run."""


class ShapingLoop:
    """Coordinate bounded context acquisition, candidate repair, and abstention."""

    def __init__(
        self,
        *,
        model: ModelGateway,
        tools: ReadOnlyToolRegistry,
        validator: Validator,
        checkpoints: CheckpointStore,
        budget: ShapingBudget | None = None,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        self._model = model
        self._tools = tools
        self._validator = validator
        self._checkpoints = checkpoints
        self._budget = budget or ShapingBudget()
        self._monotonic = monotonic

    def run(
        self,
        *,
        run_id: str,
        document: SourceDocument,
        spans: Sequence[SourceSpan],
        principal: Principal,
        transformation_requirements: Sequence[str] = (),
        cancelled: Callable[[], bool] = lambda: False,
    ) -> ShapingOutcome:
        """Run until one valid candidate, an abstention, cancellation, or hard limit."""
        started = self._monotonic()
        model_calls = 0
        tool_calls = 0
        input_tokens = 0
        output_tokens = 0
        candidates = 0
        context: list[object] = [span.model_dump(mode="json") for span in spans]
        feedback: list[str] = []

        while True:
            self._guard(
                started=started,
                model_calls=model_calls,
                tool_calls=tool_calls,
                tokens=input_tokens + output_tokens,
                candidates=candidates,
                cancelled=cancelled,
            )
            prompt = json.dumps(
                {
                    "instructions": SHAPING_PROMPT,
                    "source": context,
                    "approved_transformation_requirements": list(transformation_requirements),
                    "validation_feedback": feedback,
                    "allowed_tools": sorted(self._tools.names),
                },
                sort_keys=True,
            )
            result = self._model.generate(
                prompt=prompt, schema=CandidatePayload.model_json_schema()
            )
            model_calls += 1
            input_tokens += result.input_tokens
            output_tokens += result.output_tokens
            if input_tokens + output_tokens > self._budget.maximum_tokens:
                self._checkpoints.save(
                    run_id,
                    "budget_exhausted",
                    json.dumps(
                        {
                            "input_tokens": input_tokens,
                            "output_tokens": output_tokens,
                            "model_calls": model_calls,
                        },
                        sort_keys=True,
                    ),
                )
                raise ShapingBudgetExceeded(
                    "Shaping token budget exhausted after provider response: "
                    f"{input_tokens + output_tokens} of {self._budget.maximum_tokens}",
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    model_calls=model_calls,
                )
            self._checkpoints.save(
                run_id,
                "model_response",
                json.dumps({"response_id": result.response_id, "calls": model_calls}),
            )
            try:
                payload = CandidatePayload.model_validate_json(json.dumps(result.payload))
            except ValidationError as error:
                feedback = [f"Response schema validation failed: {error.error_count()} errors"]
                continue
            if payload.status == "abstain":
                reason = payload.reason or "Model abstained without a reason"
                self._checkpoints.save(run_id, "abstained", json.dumps({"reason": reason}))
                return ShapingOutcome(
                    None,
                    True,
                    reason,
                    model_calls,
                    tool_calls,
                    input_tokens,
                    output_tokens,
                )
            if payload.status == "tool":
                if payload.tool is None:
                    feedback = ["Tool response requires a tool request"]
                    continue
                tool_calls += 1
                tool_result = self._tools.invoke(payload.tool, principal)
                context.append({"tool": payload.tool.name, "result": tool_result})
                self._checkpoints.save(
                    run_id,
                    "tool_result",
                    json.dumps({"name": payload.tool.name, "calls": tool_calls}),
                )
                continue
            if payload.status != "candidate":
                feedback = [f"Unsupported response status: {payload.status!r}"]
                continue
            candidates += 1
            unit = AnswerUnit.create(
                source_id=document.source_id,
                source_version=document.source_version,
                canonical_questions=payload.canonical_questions,
                answer=payload.answer,
                claims=tuple(
                    Claim(
                        text=claim.text,
                        span_ids=claim.span_ids,
                        qualifiers=claim.qualifiers,
                    )
                    for claim in payload.claims
                ),
                applicability=payload.applicability,
                confidence=payload.confidence,
                derivation=Derivation(
                    run_id=run_id,
                    model="configured-model",
                    prompt_version=PROMPT_VERSION,
                    parameters_hash=canonical_hash({"temperature": 0}),
                ),
            )
            findings = self._validator.validate(unit, spans)
            blocking = [
                finding.message
                for finding in findings
                if finding.severity is FindingSeverity.BLOCKING
            ]
            if blocking:
                feedback = blocking
                self._checkpoints.save(
                    run_id,
                    "candidate_rejected",
                    json.dumps({"unit_id": unit.unit_id, "findings": blocking}),
                )
                continue
            self._checkpoints.save(
                run_id,
                "candidate_accepted",
                json.dumps({"unit_id": unit.unit_id, "unit_version": unit.unit_version}),
            )
            return ShapingOutcome(
                unit,
                False,
                "candidate accepted",
                model_calls,
                tool_calls,
                input_tokens,
                output_tokens,
            )

    def _guard(
        self,
        *,
        started: float,
        model_calls: int,
        tool_calls: int,
        tokens: int,
        candidates: int,
        cancelled: Callable[[], bool],
    ) -> None:
        if cancelled():
            raise ShapingCancelled("Shaping run was cancelled before the next model action")
        elapsed = self._monotonic() - started
        limits = (
            ("candidates", candidates, self._budget.maximum_candidates),
            ("model calls", model_calls, self._budget.maximum_model_calls),
            ("tool calls", tool_calls, self._budget.maximum_tool_calls),
            ("tokens", tokens, self._budget.maximum_tokens),
        )
        for name, current, maximum in limits:
            if current >= maximum:
                raise ShapingBudgetExceeded(
                    f"Shaping {name} budget exhausted: {current} of {maximum}"
                )
        if elapsed >= self._budget.maximum_seconds:
            raise ShapingBudgetExceeded(
                f"Shaping elapsed-time budget exhausted: {elapsed:.3f} seconds"
            )
