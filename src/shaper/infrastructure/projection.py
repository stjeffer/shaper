"""Load and verify the current filesystem release for authorized retrieval."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from pathlib import Path

from shaper.application.publication import ReleaseBundle, verify_release
from shaper.application.query import QueryResult, QueryService
from shaper.domain import AnswerUnit, Principal, ReleaseManifest
from shaper.infrastructure.indexes import (
    FeatureHashEmbedding,
    InMemoryVectorIndex,
    SQLiteLexicalIndex,
)


def load_query_service(root: Path, *, collection_id: str) -> QueryService:
    """Build a complete query projection from an integrity-checked current release."""
    pointer_path = root / "current.json"
    if not pointer_path.is_file():
        return _build_query((), collection_id=collection_id, release_id="none")
    pointer_bytes = pointer_path.read_bytes()
    pointer = json.loads(pointer_bytes)
    release_id = pointer.get("release_id")
    manifest_hash = pointer.get("manifest_hash")
    if not isinstance(release_id, str) or not isinstance(manifest_hash, str):
        raise ValueError("Current release pointer is malformed")
    release_root = root / "releases" / release_id
    manifest_bytes = (release_root / "manifest.json").read_bytes()
    if hashlib.sha256(manifest_bytes).hexdigest() != manifest_hash:
        raise ValueError("Current release manifest does not match its pointer hash")
    manifest = ReleaseManifest.model_validate_json(manifest_bytes)
    if manifest.release_id != release_id:
        raise ValueError("Current release pointer and manifest IDs differ")
    if manifest.collection_id != collection_id:
        raise ValueError(
            f"Current release belongs to collection {manifest.collection_id!r}, "
            f"not configured collection {collection_id!r}"
        )
    artifacts = {name: (release_root / name).read_bytes() for name in manifest.artifact_hashes}
    verify_release(ReleaseBundle(manifest=manifest, artifacts=artifacts))
    units = tuple(
        AnswerUnit.model_validate_json(line)
        for line in artifacts["units.jsonl"].splitlines()
        if line
    )
    return _build_query(units, collection_id=collection_id, release_id=release_id)


class ReloadingQueryService:
    """Reload the integrity-checked current release for each operation."""

    def __init__(self, root: Path, *, collection_id: str) -> None:
        self._root = root
        self._collection_id = collection_id

    @property
    def release_id(self) -> str:
        """Return the current immutable release identifier."""
        return self._load().release_id

    def query(
        self,
        text: str,
        *,
        principal: Principal,
        limit: int = 10,
    ) -> Sequence[QueryResult]:
        """Query the latest integrity-checked release."""
        return self._load().query(text, principal=principal, limit=limit)

    def explain(self, unit_id: str, *, principal: Principal) -> dict[str, object]:
        """Explain a unit from the latest integrity-checked release."""
        return self._load().explain(unit_id, principal=principal)

    def _load(self) -> QueryService:
        return load_query_service(self._root, collection_id=self._collection_id)


def _build_query(
    units: tuple[AnswerUnit, ...],
    *,
    collection_id: str,
    release_id: str,
) -> QueryService:
    lexical = SQLiteLexicalIndex()
    lexical.build(
        [
            (
                unit.unit_id,
                unit.canonical_questions[0],
                unit.answer,
                " ".join(claim.text for claim in unit.claims),
            )
            for unit in units
        ]
    )
    embeddings = FeatureHashEmbedding()
    vector = InMemoryVectorIndex()
    vector.build([(unit.unit_id, embeddings.embed([unit.answer])[0]) for unit in units])
    return QueryService(
        units={unit.unit_id: unit for unit in units},
        lexical=lexical,
        vector=vector,
        embeddings=embeddings,
        collection_id=collection_id,
        release_id=release_id,
    )
