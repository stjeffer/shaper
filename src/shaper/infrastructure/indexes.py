"""Local lexical, embedding, and vector reference adapters."""

from __future__ import annotations

import hashlib
import math
import sqlite3
import threading
from collections.abc import Sequence

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI


class FeatureHashEmbedding:
    """Deterministic feature hashing for local retrieval mechanics only."""

    def __init__(self, dimensions: int = 256) -> None:
        if dimensions <= 0:
            raise ValueError("Embedding dimensions must be positive")
        self._dimensions = dimensions

    def embed(self, texts: Sequence[str]) -> Sequence[Sequence[float]]:
        """Create normalized token feature vectors."""
        vectors: list[list[float]] = []
        for text in texts:
            vector = [0.0] * self._dimensions
            for token in text.lower().split():
                digest = hashlib.sha256(token.encode()).digest()
                index = int.from_bytes(digest[:4]) % self._dimensions
                vector[index] += -1.0 if digest[4] & 1 else 1.0
            norm = math.sqrt(sum(value * value for value in vector))
            vectors.append(vector if norm == 0 else [value / norm for value in vector])
        return vectors


class AzureOpenAIEmbedding:
    """Live semantic embedding adapter."""

    def __init__(
        self,
        *,
        endpoint: str,
        api_key: str | None,
        deployment: str,
        use_managed_identity: bool = False,
    ) -> None:
        if use_managed_identity:
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(),
                "https://cognitiveservices.azure.com/.default",
            )
            self._client = AzureOpenAI(
                azure_endpoint=endpoint,
                azure_ad_token_provider=token_provider,
                api_version="2024-10-21",
            )
        elif api_key is not None:
            self._client = AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=api_key,
                api_version="2024-10-21",
            )
        else:
            raise ValueError("Azure OpenAI requires an API key or managed identity")
        self._deployment = deployment

    def embed(self, texts: Sequence[str]) -> Sequence[Sequence[float]]:
        """Return Azure OpenAI embeddings in input order."""
        response = self._client.embeddings.create(model=self._deployment, input=list(texts))
        return [item.embedding for item in sorted(response.data, key=lambda item: item.index)]


class SQLiteLexicalIndex:
    """FTS5 index rebuilt from each complete release."""

    def __init__(self) -> None:
        self._connection = sqlite3.connect(":memory:", check_same_thread=False)
        self._lock = threading.Lock()
        self._connection.execute(
            "CREATE VIRTUAL TABLE units USING fts5(unit_id UNINDEXED, title, answer, claims)"
        )

    def build(self, records: Sequence[tuple[str, str, str, str]]) -> None:
        """Replace the index with a complete release projection."""
        with self._lock, self._connection:
            self._connection.execute("DELETE FROM units")
            self._connection.executemany(
                "INSERT INTO units(unit_id, title, answer, claims) VALUES (?, ?, ?, ?)",
                records,
            )

    def query(self, text: str, *, limit: int) -> Sequence[str]:
        """Return BM25-ranked unit IDs."""
        if not text.strip() or limit <= 0:
            return []
        with self._lock:
            rows = self._connection.execute(
                "SELECT unit_id FROM units WHERE units MATCH ? ORDER BY bm25(units) LIMIT ?",
                (text, limit),
            ).fetchall()
        return [str(row[0]) for row in rows]


class InMemoryVectorIndex:
    """Bounded cosine-similarity reference vector index."""

    def __init__(self) -> None:
        self._vectors: dict[str, tuple[float, ...]] = {}

    def build(self, records: Sequence[tuple[str, Sequence[float]]]) -> None:
        """Replace vectors with a complete release projection."""
        self._vectors = {unit_id: tuple(vector) for unit_id, vector in records}

    def query(self, vector: Sequence[float], *, limit: int) -> Sequence[str]:
        """Return cosine-ranked unit IDs."""
        query_norm = math.sqrt(sum(value * value for value in vector))
        if query_norm == 0 or limit <= 0:
            return []
        scored = []
        for unit_id, candidate in self._vectors.items():
            candidate_norm = math.sqrt(sum(value * value for value in candidate))
            if candidate_norm == 0 or len(candidate) != len(vector):
                continue
            score = sum(left * right for left, right in zip(vector, candidate, strict=True))
            scored.append((score / (query_norm * candidate_norm), unit_id))
        return [unit_id for _, unit_id in sorted(scored, reverse=True)[:limit]]
