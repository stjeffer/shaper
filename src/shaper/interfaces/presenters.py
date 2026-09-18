"""Shared public response projections."""

from __future__ import annotations

from pydantic_core import to_jsonable_python


def finding_report_payload(value: object) -> dict[str, object]:
    """Return the findings-led public report without an internal readiness score."""
    payload = to_jsonable_python(value)
    if not isinstance(payload, dict):
        raise TypeError("Discovery report did not encode as an object")
    payload.pop("readiness_score", None)
    return payload
