"""Structured-output model gateways."""

from __future__ import annotations

import copy
import json
import logging
from collections.abc import Iterable
from typing import Literal

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import APIConnectionError, AzureOpenAI, OpenAIError

from shaper.application.ports import ModelResult

logger = logging.getLogger(__name__)


class ModelProviderError(RuntimeError):
    """Explicit model provider failure with retry classification."""

    def __init__(self, message: str, *, retryable: bool) -> None:
        super().__init__(message)
        self.retryable = retryable


def strict_response_schema(schema: dict[str, object]) -> dict[str, object]:
    """Return an OpenAI strict-mode schema without mutating the domain schema."""
    strict_schema = copy.deepcopy(schema)

    def require_all_properties(value: object) -> None:
        if isinstance(value, dict):
            properties = value.get("properties")
            if isinstance(properties, dict):
                value["required"] = list(properties)
                value["additionalProperties"] = False
            for nested in value.values():
                require_all_properties(nested)
        elif isinstance(value, list):
            for nested in value:
                require_all_properties(nested)

    require_all_properties(strict_schema)
    return strict_schema


class DeterministicModelGateway:
    """Sequence-backed fake for local tests and gate mechanics."""

    def __init__(self, payloads: Iterable[dict[str, object]]) -> None:
        self._payloads = iter(payloads)
        self.calls = 0

    def generate(
        self,
        *,
        system_prompt: str,
        prompt: str,
        schema: dict[str, object],
        max_output_tokens: int | None = None,
    ) -> ModelResult:
        """Return the next configured response."""
        del system_prompt, prompt, schema, max_output_tokens
        self.calls += 1
        try:
            payload = next(self._payloads)
        except StopIteration as error:
            raise ModelProviderError(
                "Deterministic model has no configured response", retryable=False
            ) from error
        return ModelResult(
            payload=payload,
            response_id=f"fake-{self.calls}",
            input_tokens=10,
            output_tokens=10,
        )


class AzureOpenAIModelGateway:
    """Azure OpenAI structured-output adapter."""

    def __init__(
        self,
        *,
        endpoint: str,
        api_key: str | None,
        deployment: str,
        use_managed_identity: bool = False,
        api_version: str = "2024-10-21",
        request_timeout_seconds: float = 90,
        default_max_output_tokens: int = 8_000,
        reasoning_effort: Literal["minimal", "low", "medium", "high"] = "low",
    ) -> None:
        if request_timeout_seconds <= 0:
            raise ValueError("Azure OpenAI request timeout must be positive")
        if default_max_output_tokens <= 0:
            raise ValueError("Azure OpenAI output token limit must be positive")
        if use_managed_identity:
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(),
                "https://cognitiveservices.azure.com/.default",
            )
            self._client = AzureOpenAI(
                azure_endpoint=endpoint,
                azure_ad_token_provider=token_provider,
                api_version=api_version,
                timeout=request_timeout_seconds,
            )
        elif api_key is not None:
            self._client = AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=api_key,
                api_version=api_version,
                timeout=request_timeout_seconds,
            )
        else:
            raise ValueError("Azure OpenAI requires an API key or managed identity")
        self._deployment = deployment
        self._default_max_output_tokens = default_max_output_tokens
        self._reasoning_effort = reasoning_effort

    def generate(
        self,
        *,
        system_prompt: str,
        prompt: str,
        schema: dict[str, object],
        max_output_tokens: int | None = None,
    ) -> ModelResult:
        """Request one schema-constrained model response."""
        try:
            response = self._client.chat.completions.create(
                model=self._deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "shaping_response",
                        "strict": True,
                        "schema": strict_response_schema(schema),
                    },
                },
                max_completion_tokens=(
                    self._default_max_output_tokens
                    if max_output_tokens is None
                    else max_output_tokens
                ),
                reasoning_effort=self._reasoning_effort,
            )
            choice = response.choices[0]
            content = choice.message.content
            usage = response.usage
            completion_details = None if usage is None else usage.completion_tokens_details
            logger.info(
                "Azure OpenAI completion response_id=%s finish_reason=%s "
                "content_characters=%d prompt_tokens=%s completion_tokens=%s "
                "reasoning_tokens=%s refusal=%s",
                response.id,
                choice.finish_reason,
                0 if content is None else len(content),
                None if usage is None else usage.prompt_tokens,
                None if usage is None else usage.completion_tokens,
                (None if completion_details is None else completion_details.reasoning_tokens),
                bool(getattr(choice.message, "refusal", None)),
            )
            if choice.finish_reason == "length":
                raise ModelProviderError(
                    "Azure OpenAI exhausted the approved completion limit before "
                    "producing structured output; retry requires a newly estimated "
                    "and approved budget",
                    retryable=False,
                )
            if choice.finish_reason == "content_filter":
                raise ModelProviderError(
                    "Azure OpenAI content filtering prevented structured output",
                    retryable=False,
                )
            refusal = getattr(choice.message, "refusal", None)
            if refusal:
                raise ModelProviderError(
                    "Azure OpenAI refused to produce structured output",
                    retryable=False,
                )
            if content is None:
                raise ModelProviderError("Model returned no structured content", retryable=False)
            return ModelResult(
                payload=json.loads(content),
                response_id=response.id,
                input_tokens=0 if usage is None else usage.prompt_tokens,
                output_tokens=0 if usage is None else usage.completion_tokens,
            )
        except ModelProviderError:
            raise
        except OpenAIError as error:
            status_code = getattr(error, "status_code", None)
            retryable = isinstance(error, APIConnectionError) or (
                isinstance(status_code, int)
                and (status_code in {408, 409, 429} or status_code >= 500)
            )
            raise ModelProviderError(
                "Azure OpenAI request failed",
                retryable=retryable,
            ) from error
        except (json.JSONDecodeError, IndexError, KeyError, TypeError, ValueError) as error:
            raise ModelProviderError(
                "Azure OpenAI returned malformed structured output",
                retryable=False,
            ) from error
