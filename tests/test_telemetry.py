"""Operational telemetry redaction and correlation tests."""

from __future__ import annotations

import pytest

from shaper.logging import _redact_sensitive, configure_logging
from shaper.telemetry import Telemetry


def test_given_nested_sensitive_fields_when_logged_then_values_are_redacted() -> None:
    event = {
        "event": "compile",
        "details": {"access_token": "synthetic-secret", "count": 1},
    }

    redacted = _redact_sensitive(None, "info", event)

    assert redacted["details"] == {"access_token": "[REDACTED]", "count": 1}


def test_given_unknown_correlation_field_when_bound_then_it_is_rejected() -> None:
    with (
        pytest.raises(ValueError, match="Unknown telemetry"),
        Telemetry().correlate(tenant_secret="synthetic"),
    ):
        pass


def test_given_source_text_when_event_emitted_then_telemetry_rejects_it() -> None:
    configure_logging(json_output=True)

    with pytest.raises(ValueError, match="Source text"):
        Telemetry().event("compile.started", source_text="synthetic source")
