"""Hybrid retrieval authorization and ranking tests."""

from __future__ import annotations

from shaper.application.query import QueryService
from shaper.domain import CollectionRole, Principal, SourceDocument
from shaper.infrastructure.indexes import (
    FeatureHashEmbedding,
    InMemoryVectorIndex,
    SQLiteLexicalIndex,
)
from tests.test_validation_review import make_unit


def principal(*roles: CollectionRole) -> Principal:
    """Return a principal with selected collection roles."""
    return Principal(
        principal_id="person-1",
        tenant_id="tenant-1",
        collection_roles={"collection-1": frozenset(roles)},
    )


def service(document: SourceDocument) -> QueryService:
    """Build a complete local query projection."""
    unit = make_unit(document)
    lexical = SQLiteLexicalIndex()
    lexical.build([(unit.unit_id, unit.canonical_questions[0], unit.answer, unit.claims[0].text)])
    embeddings = FeatureHashEmbedding(dimensions=32)
    vector = InMemoryVectorIndex()
    vector.build([(unit.unit_id, embeddings.embed([unit.answer])[0])])
    return QueryService(
        units={unit.unit_id: unit},
        lexical=lexical,
        vector=vector,
        embeddings=embeddings,
        collection_id="collection-1",
        release_id="release-1",
    )


def test_given_authorized_query_when_searched_then_grounded_unit_is_returned(
    source_document: SourceDocument,
) -> None:
    # Act
    results = service(source_document).query(
        "employees leave",
        principal=principal(CollectionRole.QUERY),
    )

    # Assert
    assert results[0].unit.source_id == source_document.source_id


def test_given_question_punctuation_when_searched_then_fts_syntax_is_safe(
    source_document: SourceDocument,
) -> None:
    # Act
    results = service(source_document).query(
        "How much leave do employees receive?",
        principal=principal(CollectionRole.QUERY),
    )

    # Assert
    assert results[0].unit.source_id == source_document.source_id


def test_given_missing_query_role_when_searched_then_access_fails_before_ranking(
    source_document: SourceDocument,
) -> None:
    # Arrange
    query = service(source_document)

    # Act & Assert
    try:
        query.query("leave", principal=principal(CollectionRole.COMPILE))
    except PermissionError as error:
        assert "query" in str(error)
    else:
        raise AssertionError("Unauthorized query unexpectedly succeeded")
