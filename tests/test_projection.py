"""Current release projection loading and integrity tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from shaper.domain import CollectionRole, SourceDocument
from shaper.infrastructure.filesystem_sink import FilesystemReleaseSink
from shaper.infrastructure.projection import load_query_service
from tests.test_publication import bundle
from tests.test_query import principal


def test_given_current_release_when_loaded_then_query_projection_is_complete(
    tmp_path: Path,
    source_document: SourceDocument,
) -> None:
    release = bundle(source_document, run_id="projection")
    FilesystemReleaseSink(tmp_path).publish(release, expected_current_hash=None)

    query = load_query_service(tmp_path, collection_id="collection-1")

    assert query.release_id == release.manifest.release_id
    assert query.query("leave", principal=principal(CollectionRole.QUERY))


def test_given_tampered_release_when_loaded_then_startup_fails(
    tmp_path: Path,
    source_document: SourceDocument,
) -> None:
    release = bundle(source_document, run_id="tampered")
    FilesystemReleaseSink(tmp_path).publish(release, expected_current_hash=None)
    artifact = tmp_path / "releases" / release.manifest.release_id / "units.jsonl"
    artifact.write_text("{}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="hash mismatch"):
        load_query_service(tmp_path, collection_id="collection-1")
