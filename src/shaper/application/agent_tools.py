"""Immutable read-only tools available to the shaping agent."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from types import MappingProxyType
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from shaper.domain import CollectionRole, Principal, SourceSpan


class EvidenceContext(Protocol):
    """Read-only evidence lookup boundary."""

    def spans(self, source_id: str) -> Sequence[SourceSpan]:
        """Return spans for one authorized source."""

    def taxonomy(self, collection_id: str, name: str) -> Sequence[str]:
        """Return values from an approved taxonomy."""

    def conflicts(self, collection_id: str, text: str, limit: int) -> Sequence[str]:
        """Return candidate conflict unit IDs."""


class ToolRequest(BaseModel):
    """Validated model-requested tool invocation."""

    model_config = ConfigDict(extra="forbid", strict=True)

    name: str = Field(min_length=1, max_length=64)
    arguments: dict[str, object] = Field(default_factory=dict)


class ReadOnlyToolRegistry:
    """Fixed allowlist of tenant- and collection-scoped evidence tools."""

    _ALLOWED_NAMES = frozenset({"find_conflicts", "get_neighbors", "get_span", "get_taxonomy"})

    def __init__(
        self,
        context: EvidenceContext,
        *,
        source_id: str,
        collection_id: str,
        result_limit: int = 20,
    ) -> None:
        self._context = context
        self._source_id = source_id
        self._collection_id = collection_id
        self._result_limit = result_limit
        self._handlers = MappingProxyType(
            {
                "find_conflicts": self._find_conflicts,
                "get_neighbors": self._get_neighbors,
                "get_span": self._get_span,
                "get_taxonomy": self._get_taxonomy,
            }
        )

    @property
    def names(self) -> frozenset[str]:
        """Return the immutable tool allowlist."""
        return self._ALLOWED_NAMES

    def invoke(self, request: ToolRequest, principal: Principal) -> object:
        """Authorize and execute one validated read-only tool request."""
        principal.require(self._collection_id, CollectionRole.COMPILE)
        handler = self._handlers.get(request.name)
        if handler is None:
            raise ValueError(f"Unknown or disallowed agent tool: {request.name!r}")
        return handler(request.arguments)

    def _get_span(self, arguments: Mapping[str, object]) -> dict[str, object]:
        span_id = _required_string(arguments, "span_id")
        for span in self._context.spans(self._source_id):
            if span.span_id == span_id:
                return span.model_dump(mode="json")
        raise KeyError(f"Span {span_id!r} is not available in the active source")

    def _get_neighbors(self, arguments: Mapping[str, object]) -> list[dict[str, object]]:
        span_id = _required_string(arguments, "span_id")
        radius = _bounded_integer(arguments, "radius", maximum=3)
        spans = list(self._context.spans(self._source_id))
        for index, span in enumerate(spans):
            if span.span_id == span_id:
                start = max(0, index - radius)
                end = min(len(spans), index + radius + 1)
                return [item.model_dump(mode="json") for item in spans[start:end]]
        raise KeyError(f"Span {span_id!r} is not available in the active source")

    def _get_taxonomy(self, arguments: Mapping[str, object]) -> list[str]:
        name = _required_string(arguments, "name")
        return list(self._context.taxonomy(self._collection_id, name)[: self._result_limit])

    def _find_conflicts(self, arguments: Mapping[str, object]) -> list[str]:
        text = _required_string(arguments, "text")
        requested = _bounded_integer(arguments, "limit", maximum=self._result_limit)
        return list(self._context.conflicts(self._collection_id, text, requested)[:requested])


def _required_string(arguments: Mapping[str, object], name: str) -> str:
    value = arguments.get(name)
    if not isinstance(value, str) or not value:
        raise ValueError(f"Agent tool argument {name!r} must be a non-empty string")
    return value


def _bounded_integer(arguments: Mapping[str, object], name: str, *, maximum: int) -> int:
    value = arguments.get(name)
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= maximum:
        raise ValueError(f"Agent tool argument {name!r} must be between 0 and {maximum}")
    return value
