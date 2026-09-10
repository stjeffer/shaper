"""Authorized bounded hybrid retrieval and explanation."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol

from shaper.application.ports import EmbeddingProvider, LexicalIndex, VectorIndex
from shaper.domain import AnswerUnit, CollectionRole, Principal


@dataclass(frozen=True)
class QueryResult:
    """Ranked answer unit and retrieval evidence."""

    unit: AnswerUnit
    score: float
    lexical_rank: int | None
    vector_rank: int | None
    coverage_warning: str | None


class QueryGateway(Protocol):
    """Current-release query and explanation boundary."""

    @property
    def release_id(self) -> str:
        """Return the active immutable release identifier."""

    def query(
        self,
        text: str,
        *,
        principal: Principal,
        limit: int = 10,
    ) -> Sequence[QueryResult]:
        """Return authorized answer units."""

    def explain(self, unit_id: str, *, principal: Principal) -> dict[str, object]:
        """Return bounded derivation evidence."""


class QueryService:
    """Apply authorization before bounded hybrid retrieval."""

    def __init__(
        self,
        *,
        units: Mapping[str, AnswerUnit],
        lexical: LexicalIndex,
        vector: VectorIndex,
        embeddings: EmbeddingProvider,
        collection_id: str,
        release_id: str,
    ) -> None:
        self._units = units
        self._lexical = lexical
        self._vector = vector
        self._embeddings = embeddings
        self._collection_id = collection_id
        self._release_id = release_id

    @property
    def release_id(self) -> str:
        """Return the immutable release pinned by this query projection."""
        return self._release_id

    def query(
        self,
        text: str,
        *,
        principal: Principal,
        limit: int = 10,
    ) -> Sequence[QueryResult]:
        """Return authorized reciprocal-rank-fused evidence."""
        principal.require(self._collection_id, CollectionRole.QUERY)
        bounded_limit = min(max(limit, 1), 50)
        lexical = list(self._lexical.query(text, limit=bounded_limit * 2))
        query_vector = self._embeddings.embed([text])[0]
        vector = list(self._vector.query(query_vector, limit=bounded_limit * 2))
        scores: dict[str, float] = {}
        for rank, unit_id in enumerate(lexical, start=1):
            if unit_id in self._units:
                scores[unit_id] = scores.get(unit_id, 0) + 1 / (60 + rank)
        for rank, unit_id in enumerate(vector, start=1):
            if unit_id in self._units:
                scores[unit_id] = scores.get(unit_id, 0) + 1 / (60 + rank)
        ranked = sorted(scores, key=lambda unit_id: (-scores[unit_id], unit_id))[:bounded_limit]
        if not ranked:
            return []
        warning = (
            "No lexical match; verify semantic result against source." if not lexical else None
        )
        return [
            QueryResult(
                unit=self._units[unit_id],
                score=scores[unit_id],
                lexical_rank=_rank(lexical, unit_id),
                vector_rank=_rank(vector, unit_id),
                coverage_warning=warning,
            )
            for unit_id in ranked
        ]

    def explain(self, unit_id: str, *, principal: Principal) -> dict[str, object]:
        """Return bounded derivation and source references for one unit."""
        principal.require(self._collection_id, CollectionRole.QUERY)
        unit = self._units.get(unit_id)
        if unit is None:
            raise KeyError(f"Unit does not exist in release {self._release_id}: {unit_id}")
        return {
            "release_id": self._release_id,
            "unit_id": unit.unit_id,
            "unit_version": unit.unit_version,
            "source_id": unit.source_id,
            "source_version": unit.source_version,
            "claims": [
                {"text": claim.text, "span_ids": list(claim.span_ids)} for claim in unit.claims
            ],
            "conflicts": list(unit.conflict_unit_ids),
            "derivation": unit.derivation.model_dump(mode="json"),
        }


def _rank(values: Sequence[str], unit_id: str) -> int | None:
    try:
        return values.index(unit_id) + 1
    except ValueError:
        return None
