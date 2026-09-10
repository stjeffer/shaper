"""Structured-output model gateway tests."""

from __future__ import annotations

import json

from shaper.application.model import strict_response_schema
from shaper.application.shaping import CandidatePayload


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
