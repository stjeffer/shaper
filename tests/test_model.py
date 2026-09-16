"""Structured-output model gateway tests."""

from __future__ import annotations

import json

import httpx
import pytest
from openai import APIConnectionError, RateLimitError

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


class RateLimitedCompletions:
    """Raise a provider rate-limit failure."""

    def create(self, **kwargs: object) -> None:
        del kwargs
        request = httpx.Request("POST", "https://example.invalid")
        response = httpx.Response(429, request=request)
        raise RateLimitError("Rate limit reached", response=response, body=None)


class RateLimitedChat:
    """Expose rate-limited chat completions."""

    completions = RateLimitedCompletions()


class RateLimitedClient:
    """Expose a rate-limited chat boundary."""

    chat = RateLimitedChat()


class CapturingCompletions:
    """Capture Azure chat-completion parameters."""

    def __init__(
        self,
        *,
        content: str | None = "{}",
        finish_reason: str = "stop",
        refusal: str | None = None,
    ) -> None:
        self.kwargs: dict[str, object] | None = None
        self.content = content
        self.finish_reason = finish_reason
        self.refusal = refusal

    def create(self, **kwargs: object) -> object:
        self.kwargs = kwargs
        message = type(
            "Message",
            (),
            {"content": self.content, "refusal": self.refusal},
        )()
        choice = type(
            "Choice",
            (),
            {"message": message, "finish_reason": self.finish_reason},
        )()
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

    def __init__(self, completions: CapturingCompletions | None = None) -> None:
        self.completions = completions or CapturingCompletions()


class CapturingClient:
    """Expose a captured chat boundary."""

    def __init__(self, completions: CapturingCompletions | None = None) -> None:
        self.chat = CapturingChat(completions)


def configured_gateway(
    monkeypatch: pytest.MonkeyPatch,
    completions: CapturingCompletions,
) -> AzureOpenAIModelGateway:
    gateway = object.__new__(AzureOpenAIModelGateway)
    monkeypatch.setattr(gateway, "_client", CapturingClient(completions), raising=False)
    monkeypatch.setattr(gateway, "_deployment", "test-deployment", raising=False)
    monkeypatch.setattr(gateway, "_default_max_output_tokens", 8_000, raising=False)
    monkeypatch.setattr(gateway, "_reasoning_effort", "low", raising=False)
    return gateway


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
    monkeypatch.setattr(gateway, "_default_max_output_tokens", 8_000, raising=False)
    monkeypatch.setattr(gateway, "_reasoning_effort", "low", raising=False)

    with pytest.raises(ModelProviderError) as captured:
        gateway.generate(
            system_prompt=EVALUATION_PROMPT,
            prompt="test",
            schema={"type": "object"},
        )

    assert captured.value.retryable
    assert str(captured.value) == "Azure OpenAI request failed"


def test_given_provider_rate_limit_when_generated_then_error_is_actionable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gateway = object.__new__(AzureOpenAIModelGateway)
    monkeypatch.setattr(gateway, "_client", RateLimitedClient(), raising=False)
    monkeypatch.setattr(gateway, "_deployment", "test-deployment", raising=False)
    monkeypatch.setattr(gateway, "_default_max_output_tokens", 8_000, raising=False)
    monkeypatch.setattr(gateway, "_reasoning_effort", "low", raising=False)

    with pytest.raises(ModelProviderError) as captured:
        gateway.generate(
            system_prompt=EVALUATION_PROMPT,
            prompt="test",
            schema={"type": "object"},
        )

    assert captured.value.retryable
    assert str(captured.value) == (
        "Azure OpenAI rate limit was reached; retry after provider capacity resets"
    )


def test_given_caller_system_prompt_when_generated_then_azure_sends_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gateway = object.__new__(AzureOpenAIModelGateway)
    client = CapturingClient()
    monkeypatch.setattr(gateway, "_client", client, raising=False)
    monkeypatch.setattr(gateway, "_deployment", "test-deployment", raising=False)
    monkeypatch.setattr(gateway, "_default_max_output_tokens", 8_000, raising=False)
    monkeypatch.setattr(gateway, "_reasoning_effort", "low", raising=False)

    gateway.generate(
        system_prompt=EVALUATION_PROMPT,
        prompt="candidate and source",
        schema={"type": "object"},
        max_output_tokens=1_234,
    )

    assert client.chat.completions.kwargs is not None
    assert client.chat.completions.kwargs["messages"] == [
        {"role": "system", "content": EVALUATION_PROMPT},
        {"role": "user", "content": "candidate and source"},
    ]
    assert client.chat.completions.kwargs["max_completion_tokens"] == 1_234
    assert client.chat.completions.kwargs["reasoning_effort"] == "low"


@pytest.mark.parametrize(
    ("finish_reason", "refusal", "expected_message"),
    [
        ("length", None, "exhausted the approved completion limit"),
        ("content_filter", None, "content filtering prevented"),
        ("stop", "Unable to comply", "refused to produce"),
    ],
)
def test_given_incomplete_provider_outcome_when_generated_then_reason_is_explicit(
    monkeypatch: pytest.MonkeyPatch,
    finish_reason: str,
    refusal: str | None,
    expected_message: str,
) -> None:
    gateway = configured_gateway(
        monkeypatch,
        CapturingCompletions(
            content='{"status":',
            finish_reason=finish_reason,
            refusal=refusal,
        ),
    )

    with pytest.raises(ModelProviderError, match=expected_message) as captured:
        gateway.generate(
            system_prompt=EVALUATION_PROMPT,
            prompt="test",
            schema={"type": "object"},
        )

    assert not captured.value.retryable


def test_given_malformed_json_after_stop_when_generated_then_error_is_malformed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gateway = configured_gateway(
        monkeypatch,
        CapturingCompletions(content='{"status":', finish_reason="stop"),
    )

    with pytest.raises(ModelProviderError, match="malformed structured output"):
        gateway.generate(
            system_prompt=EVALUATION_PROMPT,
            prompt="test",
            schema={"type": "object"},
        )


def test_given_invalid_provider_limits_when_created_then_configuration_is_rejected() -> None:
    with pytest.raises(ValueError, match="timeout"):
        AzureOpenAIModelGateway(
            endpoint="https://example.invalid",
            api_key="test",
            deployment="test",
            request_timeout_seconds=0,
        )
    with pytest.raises(ValueError, match="output token"):
        AzureOpenAIModelGateway(
            endpoint="https://example.invalid",
            api_key="test",
            deployment="test",
            default_max_output_tokens=0,
        )
