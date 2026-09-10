"""Structured logging configuration that excludes source content by default."""

from __future__ import annotations

import logging
from collections.abc import Mapping, MutableMapping, Sequence
from typing import Any

import structlog

_SENSITIVE_KEYS = frozenset(
    {"authorization", "credential", "password", "secret", "source_text", "token"}
)


def _redact_sensitive(
    _logger: Any,
    _method_name: str,
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    for key in tuple(event_dict):
        normalized = key.lower()
        if normalized in _SENSITIVE_KEYS or normalized.endswith(("_token", "_secret", "_password")):
            event_dict[key] = "[REDACTED]"
        else:
            event_dict[key] = _redact_value(event_dict[key])
    return event_dict


def _redact_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            key: (
                "[REDACTED]"
                if str(key).lower() in _SENSITIVE_KEYS
                or str(key).lower().endswith(("_token", "_secret", "_password"))
                else _redact_value(item)
            )
            for key, item in value.items()
        }
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return [_redact_value(item) for item in value]
    return value


def configure_logging(*, level: int = logging.INFO, json_output: bool = True) -> None:
    """Configure standard-library and structlog output."""
    logging.basicConfig(level=level, format="%(message)s", force=True)
    renderer = (
        structlog.processors.JSONRenderer() if json_output else structlog.dev.ConsoleRenderer()
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            _redact_sensitive,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
