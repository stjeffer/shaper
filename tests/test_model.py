"""Structured-output model gateway tests."""

from __future__ import annotations

import json

import httpx
import pytest
from openai import APIConnectionError

from shaper.application.model import (
    AzureOpenAIModelGateway,
    ModelProviderError,
    strict_response_schema,
)
from shaper.application.shaping import CandidatePayload
from shaper.prompts import EVALUATION_PROMPT


class FailingCompletions:
    """Raise a provider transport failure."""

    def create(self, **kwargs: object) -> None:
        del kwargs
        raise APIConnectionError(request=httpx.Request("POST", "https://example.invalid"))


class FailingChat:
    """Expose failing chat completions."""

    completions = FailingCompletions()


class FailingClient:
    """Expose a failing chat boundary."""

    chat = FailingChat()


class CapturingCompletions:
    """Capture Azure chat-completion parameters."""

    def __init__(self) -> None:
        self.kwargs: dict[str, object] | None = None

    def create(self, **kwargs: object) -> object:
        self.kwargs = kwargs
        message = type("Message", (), {"content": "{}"})()
        choice = type("Choice", (), {"message": message})()
        return type(
            "Response",
            (),
            {
                "choices": [choice],
                "id": "response-1",
                "usage": None,
            },
        )()


class CapturingChat:
    """Expose capturing chat completions."""

    def __init__(self) -> None:
        self.completions = CapturingCompletions()


class CapturingClient:
    """Expose a captured chat boundary."""

    def __init__(self) -> None:
        self.chat = CapturingChat()


def test_given_optional_nested_fields_when_schema_strict_then_all_properties_are_required() -> None:
    # Arrange
    schema = CandidatePayload.model_json_schema()

    # Act
    strict_schema = strict_response_schema(schema)
    definitions = strict_schema["$defs"]
    original_definitions = schema["$defs"]
    assert isinstance(definitions, dict)
    assert isinstance(original_definitions, dict)
    applicability = definitions["Applicability"]
    tool_arguments = definitions["ToolArguments"]
    original_applicability = original_definitions["Applicability"]
    assert isinstance(applicability, dict)
    assert isinstance(tool_arguments, dict)
    assert isinstance(original_applicability, dict)
    required = applicability["required"]
    properties = applicability["properties"]
    assert isinstance(required, list)
    assert isinstance(properties, dict)

    # Assert
    assert set(required) == set(properties)
    assert applicability["additionalProperties"] is False
    assert tool_arguments["additionalProperties"] is False
    assert "required" not in original_applicability


def test_given_provider_json_arrays_when_parsed_then_strict_tuples_are_preserved() -> None:
    # Arrange
    provider_payload = {
        "status": "candidate",
        "canonical_questions": ["Who is covered?"],
        "answer": "Employees are covered.",
        "claims": [
            {
                "text": "Employees are covered.",
                "span_ids": ["span-1"],
                "qualifiers": [],
            }
        ],
        "confidence": 0.9,
        "applicability": {
            "audiences": ["employees"],
            "jurisdictions": [],
            "effective_from": None,
            "effective_until": None,
        },
        "reason": None,
        "tool": None,
    }

    # Act
    candidate = CandidatePayload.model_validate_json(json.dumps(provider_payload))

    # Assert
    assert candidate.applicability.audiences == ("employees",)


def test_given_openai_transport_failure_when_generated_then_error_is_classified(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gateway = object.__new__(AzureOpenAIModelGateway)
    monkeypatch.setattr(gateway, "_client", FailingClient(), raising=False)
    monkeypatch.setattr(gateway, "_deployment", "test-deployment", raising=False)

    with pytest.raises(ModelProviderError) as captured:
        gateway.generate(
            system_prompt=EVALUATION_PROMPT,
            prompt="test",
            schema={"type": "object"},
        )

    assert captured.value.retryable
    assert str(captured.value) == "Azure OpenAI request failed"


def test_given_caller_system_prompt_when_generated_then_azure_sends_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gateway = object.__new__(AzureOpenAIModelGateway)
    client = CapturingClient()
    monkeypatch.setattr(gateway, "_client", client, raising=False)
    monkeypatch.setattr(gateway, "_deployment", "test-deployment", raising=False)

    gateway.generate(
        system_prompt=EVALUATION_PROMPT,
        prompt="candidate and source",
        schema={"type": "object"},
    )

    assert client.chat.completions.kwargs is not None
    assert client.chat.completions.kwargs["messages"] == [
        {"role": "system", "content": EVALUATION_PROMPT},
        {"role": "user", "content": "candidate and source"},
    ]
