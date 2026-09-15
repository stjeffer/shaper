"""Bounded, checkpointed answer-shaping loop."""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Literal, Protocol, Self

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from shaper.application.agent_tools import ReadOnlyToolRegistry, ToolRequest
from shaper.application.ports import ModelGateway, Validator
from shaper.domain import (
    AnswerUnit,
    Applicability,
    Claim,
    DocumentFinding,
    Principal,
    SourceDocument,
    SourceSpan,
    ValidationFinding,
)
from shaper.domain.models import Derivation, FindingSeverity, canonical_hash
from shaper.prompts import PROMPT_VERSION, SHAPING_PROMPT


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

    @model_validator(mode="after")
    def validate_status_fields(self) -> Self:
        if self.status == "candidate":
            if not self.answer or not self.canonical_questions or not self.claims:
                raise ValueError("Candidate response requires an answer, questions, and claims")
            if self.reason is not None or self.tool is not None:
                raise ValueError("Candidate response cannot include reason or tool")
        elif self.status == "tool":
            if self.tool is None:
                raise ValueError("Tool response requires a tool request")
            if self.answer or self.canonical_questions or self.claims or self.reason is not None:
                raise ValueError("Tool response cannot include candidate or abstain fields")
        else:
            if not self.reason:
                raise ValueError("Abstain response requires a reason")
            if self.answer or self.canonical_questions or self.claims or self.tool is not None:
                raise ValueError("Abstain response cannot include candidate or tool fields")
        return self


@dataclass(frozen=True)
class ShapingBudget:
    """Independent hard limits for one shaping run."""

    maximum_model_calls: int = 2
    maximum_tool_calls: int = 8
    maximum_tokens: int = 8_000
    maximum_seconds: float = 300
    maximum_candidates: int = 2


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


class ShapingValidationError(ShapingBudgetExceeded):
    """Raised when the initial candidate and targeted repair both fail validation."""


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
        on_model_attempt: Callable[[int, int], None] | None = None,
        on_validation_failure: (
            Callable[[int, int, Sequence[ValidationFinding]], None] | None
        ) = None,
        maximum_output_tokens: int | None = None,
    ) -> None:
        self._model = model
        self._tools = tools
        self._validator = validator
        self._checkpoints = checkpoints
        self._budget = budget or ShapingBudget()
        self._monotonic = monotonic
        self._on_model_attempt = on_model_attempt
        self._on_validation_failure = on_validation_failure
        self._maximum_output_tokens = maximum_output_tokens

    def run(
        self,
        *,
        run_id: str,
        document: SourceDocument,
        spans: Sequence[SourceSpan],
        principal: Principal,
        transformation_requirements: Sequence[str] = (),
        assessment_findings: Sequence[DocumentFinding] = (),
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
        evidence_spans = {span.span_id: span for span in spans}
        feedback: list[str] = []
        validation_findings: list[dict[str, object]] = []
        rejected_candidate: dict[str, object] | None = None
        previous_rejection: tuple[tuple[str, str], ...] | None = None

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
                    "source": context,
                    "approved_transformation_requirements": list(transformation_requirements),
                    "assessment_findings": [
                        finding.model_dump(mode="json") for finding in assessment_findings
                    ],
                    "validation_feedback": feedback,
                    "validation_findings": validation_findings,
                    "rejected_candidate": rejected_candidate,
                    "allowed_tools": sorted(self._tools.names),
                },
                sort_keys=True,
            )
            if self._on_model_attempt is not None:
                self._on_model_attempt(model_calls + 1, self._budget.maximum_model_calls)
            result = self._model.generate(
                system_prompt=SHAPING_PROMPT,
                prompt=prompt,
                schema=CandidatePayload.model_json_schema(),
                max_output_tokens=self._maximum_output_tokens,
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
                validation_findings = []
                rejected_candidate = None
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
                    validation_findings = []
                    rejected_candidate = None
                    continue
                tool_calls += 1
                tool_result = self._tools.invoke(payload.tool, principal)
                context.append({"tool": payload.tool.name, "result": tool_result})
                for span in _tool_source_spans(payload.tool, tool_result, document):
                    existing = evidence_spans.get(span.span_id)
                    if existing is not None and existing != span:
                        raise RuntimeError(
                            f"Tool returned conflicting evidence for span {span.span_id!r}"
                        )
                    evidence_spans[span.span_id] = span
                self._checkpoints.save(
                    run_id,
                    "tool_result",
                    json.dumps({"name": payload.tool.name, "calls": tool_calls}),
                )
                continue
            if payload.status != "candidate":
                feedback = [f"Unsupported response status: {payload.status!r}"]
                validation_findings = []
                rejected_candidate = None
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
            findings = self._validator.validate(
                unit,
                tuple(sorted(evidence_spans.values(), key=lambda span: span.ordinal)),
            )
            blocking = [
                finding for finding in findings if finding.severity is FindingSeverity.BLOCKING
            ]
            if blocking:
                feedback = [finding.message for finding in blocking]
                validation_findings = [
                    {
                        "rule_id": finding.rule_id,
                        "message": finding.message,
                        "remedy": finding.remedy,
                        "evidence_span_ids": list(finding.evidence_span_ids),
                    }
                    for finding in blocking
                ]
                rejected_candidate = payload.model_dump(mode="json")
                rejection = tuple((finding.rule_id, finding.message) for finding in blocking)
                self._checkpoints.save(
                    run_id,
                    "candidate_rejected",
                    json.dumps(
                        {
                            "unit_id": unit.unit_id,
                            "findings": validation_findings,
                            "candidate": rejected_candidate,
                        },
                        sort_keys=True,
                    ),
                )
                if self._on_validation_failure is not None:
                    self._on_validation_failure(
                        candidates,
                        self._budget.maximum_candidates,
                        blocking,
                    )
                repeated = rejection == previous_rejection
                previous_rejection = rejection
                if (
                    repeated
                    or candidates >= self._budget.maximum_candidates
                    or model_calls >= self._budget.maximum_model_calls
                ):
                    prefix = (
                        "Targeted repair repeated the same blocking findings"
                        if repeated
                        else "Targeted repair did not pass source-preservation checks"
                    )
                    detail = "; ".join(
                        f"{finding.rule_id}: {finding.message}" for finding in blocking
                    )
                    raise ShapingValidationError(
                        f"{prefix}: {detail}",
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        model_calls=model_calls,
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


def _tool_source_spans(
    request: ToolRequest,
    result: object,
    document: SourceDocument,
) -> tuple[SourceSpan, ...]:
    if request.name == "get_span":
        serialized_spans = (result,)
    elif request.name == "get_neighbors":
        if not isinstance(result, list):
            raise RuntimeError("get_neighbors returned an invalid source-span collection")
        serialized_spans = tuple(result)
    else:
        return ()

    spans: list[SourceSpan] = []
    for serialized in serialized_spans:
        try:
            span = SourceSpan.model_validate_json(json.dumps(serialized))
        except ValidationError as error:
            raise RuntimeError(f"{request.name} returned invalid source-span evidence") from error
        if span.source_id != document.source_id or span.source_version != document.source_version:
            raise RuntimeError(
                f"{request.name} returned evidence outside the active source version"
            )
        spans.append(span)
    return tuple(spans)
