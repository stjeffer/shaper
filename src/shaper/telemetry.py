"""Structured operational telemetry with bounded correlation context."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

import structlog
from structlog.contextvars import bound_contextvars

_CORRELATION_FIELDS = frozenset(
    {
        "request_id",
        "job_id",
        "source_id",
        "agent_run_id",
        "candidate_id",
        "release_id",
    }
)


class Telemetry:
    """Emit redaction-processed events and scoped correlation identifiers."""

    def __init__(self) -> None:
        self._logger = structlog.get_logger("shaper")

    @contextmanager
    def correlate(self, **identifiers: str) -> Iterator[None]:
        """Bind only declared correlation fields for the current operation."""
        unknown = set(identifiers) - _CORRELATION_FIELDS
        if unknown:
            raise ValueError(f"Unknown telemetry correlation fields: {sorted(unknown)}")
        with bound_contextvars(**identifiers):
            yield

    def event(self, name: str, **fields: object) -> None:
        """Emit one named structured event without source bodies."""
        if not name:
            raise ValueError("Telemetry event name cannot be empty")
        if "source_text" in fields:
            raise ValueError("Source text cannot be supplied to operational telemetry")
        self._logger.info(name, **fields)
