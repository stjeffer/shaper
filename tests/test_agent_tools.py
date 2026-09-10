"""Read-only shaping tool capability tests."""

from __future__ import annotations

import hashlib
from collections.abc import Sequence

import pytest

from shaper.application.agent_tools import ReadOnlyToolRegistry, ToolRequest
from shaper.domain import CollectionRole, Principal, SourceSpan


class Context:
    """In-memory evidence context."""

    def __init__(self, spans: Sequence[SourceSpan]) -> None:
        self._spans = spans

    def spans(self, source_id: str) -> Sequence[SourceSpan]:
        return [span for span in self._spans if span.source_id == source_id]

    def taxonomy(self, collection_id: str, name: str) -> Sequence[str]:
        return [f"{collection_id}:{name}:approved"]

    def conflicts(self, collection_id: str, text: str, limit: int) -> Sequence[str]:
        del collection_id, text
        return ["unit-conflict"][:limit]


def make_span() -> SourceSpan:
    """Return one source span."""
    text = "Employees receive leave."
    return SourceSpan(
        span_id="span-1",
        source_id="source-1",
        source_version="0" * 64,
        ordinal=0,
        text=text,
        text_hash=hashlib.sha256(text.encode()).hexdigest(),
    )


def principal(*roles: CollectionRole) -> Principal:
    """Return a principal with selected roles."""
    return Principal(
        principal_id="person-1",
        tenant_id="tenant-1",
        collection_roles={"collection-1": frozenset(roles)},
    )


def test_given_registry_when_inspected_then_only_read_only_tools_are_exposed() -> None:
    # Arrange
    registry = ReadOnlyToolRegistry(
        Context([make_span()]),
        source_id="source-1",
        collection_id="collection-1",
    )

    # Assert
    assert registry.names == {
        "find_conflicts",
        "get_neighbors",
        "get_span",
        "get_taxonomy",
    }


def test_given_unknown_tool_when_invoked_then_adapter_is_not_called() -> None:
    # Arrange
    registry = ReadOnlyToolRegistry(
        Context([make_span()]),
        source_id="source-1",
        collection_id="collection-1",
    )

    # Act & Assert
    with pytest.raises(ValueError, match="disallowed"):
        registry.invoke(
            ToolRequest(name="publish_release"),
            principal(CollectionRole.COMPILE),
        )


def test_given_query_only_principal_when_tool_invoked_then_authorization_fails() -> None:
    # Arrange
    registry = ReadOnlyToolRegistry(
        Context([make_span()]),
        source_id="source-1",
        collection_id="collection-1",
    )

    # Act & Assert
    with pytest.raises(PermissionError, match="compile"):
        registry.invoke(
            ToolRequest(name="get_span", arguments={"span_id": "span-1"}),
            principal(CollectionRole.QUERY),
        )
