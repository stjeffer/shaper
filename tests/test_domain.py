"""Domain invariant and schema tests."""

from __future__ import annotations

import hashlib
from datetime import datetime

import pytest
from pydantic import ValidationError

from shaper.domain import (
    AnswerUnit,
    Claim,
    CollectionRole,
    Principal,
    SourceDocument,
    SourceSpan,
)
from shaper.domain.models import Derivation
from shaper.schema import rendered_schema

ZERO_HASH = "0" * 64


def test_given_naive_source_time_when_validated_then_fails_closed(
    source_document: SourceDocument,
) -> None:
    # Arrange
    values = source_document.model_dump()
    values["observed_at"] = datetime(2026, 9, 9)

    # Act & Assert
    with pytest.raises(ValidationError, match="timezone"):
        type(source_document).model_validate(values)


def test_given_changed_span_text_when_validated_then_hash_mismatch_is_rejected() -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="hash"):
        SourceSpan(
            span_id="span-1",
            source_id="source-1",
            source_version=ZERO_HASH,
            ordinal=0,
            text="changed",
            text_hash=ZERO_HASH,
        )


def test_given_grounded_content_when_unit_created_then_identity_is_deterministic() -> None:
    # Arrange
    derivation = Derivation(
        run_id="run-1",
        model="fake-v1",
        prompt_version="1.0",
        parameters_hash=ZERO_HASH,
    )
    claim = Claim(text="Employees receive leave.", span_ids=("span-1",))

    # Act
    first = AnswerUnit.create(
        source_id="source-1",
        source_version=ZERO_HASH,
        canonical_questions=("How much leave is available?",),
        answer="Employees receive leave.",
        claims=(claim,),
        derivation=derivation,
        confidence=0.9,
    )
    second = AnswerUnit.model_validate(first.model_dump())

    # Assert
    assert (first.unit_id, first.unit_version) == (second.unit_id, second.unit_version)


def test_given_missing_collection_role_when_required_then_permission_error_is_raised() -> None:
    # Arrange
    principal = Principal(
        principal_id="person-1",
        tenant_id="tenant-1",
        collection_roles={"collection-1": frozenset({CollectionRole.QUERY})},
    )

    # Act & Assert
    with pytest.raises(PermissionError, match="compile"):
        principal.require("collection-1", CollectionRole.COMPILE)


def test_given_domain_models_when_schema_rendered_then_output_is_deterministic() -> None:
    # Act
    first = rendered_schema()
    second = rendered_schema()

    # Assert
    assert first == second
    assert hashlib.sha256(first.encode()).hexdigest() == hashlib.sha256(second.encode()).hexdigest()
