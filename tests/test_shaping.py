"""Bounded shaping-loop tests."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence

import pytest

from shaper.application.agent_tools import ReadOnlyToolRegistry
from shaper.application.model import DeterministicModelGateway
from shaper.application.ports import ModelResult
from shaper.application.shaping import (
    ShapingBudget,
    ShapingBudgetExceeded,
    ShapingLoop,
    ShapingOutcome,
)
from shaper.domain import (
    AnswerUnit,
    CollectionRole,
    FindingSeverity,
    Principal,
    SourceDocument,
    SourceSpan,
    ValidationFinding,
)
from shaper.prompts import SHAPING_PROMPT


class Context:
    """Read-only evidence fake."""

    def __init__(self, spans: Sequence[SourceSpan]) -> None:
        self._spans = spans

    def spans(self, source_id: str) -> Sequence[SourceSpan]:
        return [span for span in self._spans if span.source_id == source_id]

    def taxonomy(self, collection_id: str, name: str) -> Sequence[str]:
        del collection_id, name
        return []

    def conflicts(self, collection_id: str, text: str, limit: int) -> Sequence[str]:
        del collection_id, text, limit
        return []


class Validator:
    """Validator fake that can reject a fixed number of candidates."""

    def __init__(self, rejections: int = 0) -> None:
        self._rejections = rejections
        self.seen_span_ids: tuple[str, ...] = ()

    def validate(
        self,
        unit: AnswerUnit,
        spans: Sequence[SourceSpan],
    ) -> Sequence[ValidationFinding]:
        self.seen_span_ids = tuple(span.span_id for span in spans)
        if self._rejections:
            self._rejections -= 1
            return [
                ValidationFinding(
                    rule_id="grounding",
                    severity=FindingSeverity.BLOCKING,
                    subject_id=unit.unit_id,
                    message="Repair grounding",
                )
            ]
        return []


class Checkpoints:
    """Append-only checkpoint fake."""

    def __init__(self) -> None:
        self.states: list[str] = []

    def save(self, run_id: str, state: str, payload: str) -> None:
        del run_id, payload
        self.states.append(state)


def candidate_payload() -> dict[str, object]:
    """Return a grounded candidate model response."""
    return {
        "status": "candidate",
        "canonical_questions": ["How much leave is available?"],
        "answer": "Employees receive leave.",
        "claims": [{"text": "Employees receive leave.", "span_ids": ["span-1"]}],
        "confidence": 0.9,
    }


def run_loop(
    payloads: Sequence[dict[str, object]],
    document: SourceDocument,
    span: SourceSpan,
    *,
    validator: Validator | None = None,
    budget: ShapingBudget | None = None,
    context_spans: Sequence[SourceSpan] | None = None,
) -> tuple[ShapingOutcome, Checkpoints]:
    """Run the shaping loop with deterministic adapters."""
    checkpoints = Checkpoints()
    loop = ShapingLoop(
        model=DeterministicModelGateway(payloads),
        tools=ReadOnlyToolRegistry(
            Context(context_spans or [span]),
            source_id=document.source_id,
            collection_id=document.collection_id,
        ),
        validator=validator or Validator(),
        checkpoints=checkpoints,
        budget=budget,
    )
    principal = Principal(
        principal_id="person-1",
        tenant_id=document.tenant_id,
        collection_roles={document.collection_id: frozenset({CollectionRole.COMPILE})},
    )
    return (
        loop.run(
            run_id="run-1",
            document=document,
            spans=[span],
            principal=principal,
        ),
        checkpoints,
    )


@pytest.fixture
def source_span(source_document: SourceDocument) -> SourceSpan:
    """Return a span linked to the source fixture."""
    text = "Employees receive leave."
    return SourceSpan(
        span_id="span-1",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=0,
        text=text,
        text_hash=hashlib.sha256(text.encode()).hexdigest(),
    )


def test_given_grounded_response_when_shaped_then_candidate_is_accepted(
    source_document: SourceDocument,
    source_span: SourceSpan,
) -> None:
    # Act
    outcome, checkpoints = run_loop([candidate_payload()], source_document, source_span)

    # Assert
    assert outcome.unit is not None
    assert checkpoints.states[-1] == "candidate_accepted"


def test_given_tool_span_when_candidate_is_validated_then_tool_evidence_is_available(
    source_document: SourceDocument,
    source_span: SourceSpan,
) -> None:
    neighbor_text = "Security approval is required."
    neighbor = SourceSpan(
        span_id="span-2",
        source_id=source_document.source_id,
        source_version=source_document.source_version,
        ordinal=1,
        text=neighbor_text,
        text_hash=hashlib.sha256(neighbor_text.encode()).hexdigest(),
    )
    tool_request: dict[str, object] = {
        "status": "tool",
        "tool": {"name": "get_span", "arguments": {"span_id": "span-2"}},
    }
    candidate = candidate_payload()
    candidate["claims"] = [{"text": "Security approval is required.", "span_ids": ["span-2"]}]
    validator = Validator()

    outcome, _ = run_loop(
        [tool_request, candidate],
        source_document,
        source_span,
        validator=validator,
        context_spans=[source_span, neighbor],
    )

    assert outcome.unit is not None
    assert validator.seen_span_ids == ("span-1", "span-2")


def test_given_blocking_feedback_when_shaped_then_candidate_is_repaired(
    source_document: SourceDocument,
    source_span: SourceSpan,
) -> None:
    # Act
    outcome, checkpoints = run_loop(
        [candidate_payload(), candidate_payload()],
        source_document,
        source_span,
        validator=Validator(rejections=1),
    )

    # Assert
    assert outcome.model_calls == 2
    assert "candidate_rejected" in checkpoints.states


def test_given_three_rejected_candidates_when_shaped_then_fourth_candidate_can_pass(
    source_document: SourceDocument,
    source_span: SourceSpan,
) -> None:
    outcome, checkpoints = run_loop(
        [candidate_payload() for _ in range(4)],
        source_document,
        source_span,
        validator=Validator(rejections=3),
    )

    assert outcome.model_calls == 4
    assert checkpoints.states.count("candidate_rejected") == 3
    assert checkpoints.states[-1] == "candidate_accepted"


def test_given_requirements_when_shaped_then_prompt_contains_approved_changes(
    source_document: SourceDocument,
    source_span: SourceSpan,
) -> None:
    class CapturingModel:
        def __init__(self) -> None:
            self.prompt = ""
            self.system_prompt = ""

        def generate(
            self, *, system_prompt: str, prompt: str, schema: dict[str, object]
        ) -> ModelResult:
            del schema
            self.prompt = prompt
            self.system_prompt = system_prompt
            return DeterministicModelGateway([candidate_payload()]).generate(
                system_prompt=system_prompt,
                prompt=prompt,
                schema={},
            )

    model = CapturingModel()
    checkpoints = Checkpoints()
    loop = ShapingLoop(
        model=model,
        tools=ReadOnlyToolRegistry(
            Context([source_span]),
            source_id=source_document.source_id,
            collection_id=source_document.collection_id,
        ),
        validator=Validator(),
        checkpoints=checkpoints,
    )
    principal = Principal(
        principal_id="person-1",
        tenant_id=source_document.tenant_id,
        collection_roles={source_document.collection_id: frozenset({CollectionRole.COMPILE})},
    )

    loop.run(
        run_id="run-1",
        document=source_document,
        spans=[source_span],
        principal=principal,
        transformation_requirements=("Add descriptive headings",),
    )

    assert json.loads(model.prompt)["approved_transformation_requirements"] == [
        "Add descriptive headings"
    ]
    assert "instructions" not in json.loads(model.prompt)
    assert model.system_prompt == SHAPING_PROMPT


def test_given_abstention_when_shaped_then_no_candidate_is_returned(
    source_document: SourceDocument,
    source_span: SourceSpan,
) -> None:
    # Act
    outcome, _ = run_loop(
        [{"status": "abstain", "reason": "Insufficient evidence"}],
        source_document,
        source_span,
    )

    # Assert
    assert outcome.abstained is True
    assert outcome.unit is None


def test_given_exhausted_model_budget_when_shaped_then_failure_is_explicit(
    source_document: SourceDocument,
    source_span: SourceSpan,
) -> None:
    # Act & Assert
    with pytest.raises(ShapingBudgetExceeded, match="model calls"):
        run_loop(
            [{"status": "invalid"}],
            source_document,
            source_span,
            budget=ShapingBudget(maximum_model_calls=1),
        )


def test_given_provider_response_over_token_cap_when_valid_then_it_is_not_accepted(
    source_document: SourceDocument,
    source_span: SourceSpan,
) -> None:
    # Act & Assert
    with pytest.raises(ShapingBudgetExceeded, match="provider response") as captured:
        run_loop(
            [candidate_payload()],
            source_document,
            source_span,
            budget=ShapingBudget(maximum_tokens=1),
        )
    assert captured.value.input_tokens + captured.value.output_tokens > 1
