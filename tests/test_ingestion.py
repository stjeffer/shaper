"""Direct-upload and normalization tests."""

from __future__ import annotations

import io
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from shaper.application.ingestion import ingest_content
from shaper.domain import CollectionRole, Principal
from shaper.infrastructure.parsers import SupportedDocumentParser
from shaper.infrastructure.uploads import (
    FileUploadStore,
    ScannerUnavailableError,
    UploadRejectedError,
)


class Scanner:
    """Deterministic scanner fake."""

    def __init__(self, result: str = "clean") -> None:
        self.result = result

    def scan(self, content: bytes) -> str:
        return self.result


@pytest.fixture
def principal() -> Principal:
    """Return a compile-authorized principal."""
    return Principal(
        principal_id="person-1",
        tenant_id="tenant-1",
        collection_roles={"collection-1": frozenset({CollectionRole.COMPILE})},
    )


def test_given_clean_upload_when_staged_then_supplied_name_is_not_persisted(
    tmp_path: Path,
    principal: Principal,
) -> None:
    # Arrange
    store = FileUploadStore(tmp_path, scanner=Scanner())

    # Act
    asset = store.stage(
        [b"# Policy\n\nEmployees receive leave."],
        supplied_filename="sensitive-policy.md",
        media_type="text/markdown",
        principal=principal,
        collection_id="collection-1",
    )

    # Assert
    assert "sensitive-policy" not in (tmp_path / asset.asset_id / "metadata.json").read_text()


@pytest.mark.parametrize(
    ("filename", "media_type", "content"),
    [
        ("policy.exe.pdf", "application/pdf", b"%PDF-content"),
        ("policy.pdf", "text/plain", b"%PDF-content"),
        ("policy.pdf", "application/pdf", b"not-pdf"),
        ("policy.txt", "text/plain", b"binary\x00content"),
    ],
)
def test_given_invalid_metadata_or_signature_when_staged_then_upload_is_rejected(
    tmp_path: Path,
    principal: Principal,
    filename: str,
    media_type: str,
    content: bytes,
) -> None:
    # Arrange
    store = FileUploadStore(tmp_path, scanner=Scanner())

    # Act & Assert
    with pytest.raises(UploadRejectedError):
        store.stage(
            [content],
            supplied_filename=filename,
            media_type=media_type,
            principal=principal,
            collection_id="collection-1",
        )


def test_given_unknown_scanner_result_when_staged_then_upload_fails_closed(
    tmp_path: Path,
    principal: Principal,
) -> None:
    # Arrange
    store = FileUploadStore(tmp_path, scanner=Scanner("unavailable"))

    # Act & Assert
    with pytest.raises(ScannerUnavailableError):
        store.stage(
            [b"policy"],
            supplied_filename="policy.txt",
            media_type="text/plain",
            principal=principal,
            collection_id="collection-1",
        )


def test_given_expired_asset_when_opened_then_access_is_rejected(
    tmp_path: Path,
    principal: Principal,
) -> None:
    # Arrange
    created = datetime(2026, 9, 9, tzinfo=UTC)
    store = FileUploadStore(tmp_path, scanner=Scanner(), retention=timedelta(hours=1))
    asset = store.stage(
        [b"policy"],
        supplied_filename="policy.txt",
        media_type="text/plain",
        principal=principal,
        collection_id="collection-1",
        now=created,
    )

    # Act & Assert
    with (
        pytest.raises(UploadRejectedError, match="expired"),
        store.open_asset(
            asset.asset_id,
            principal,
            now=created + timedelta(hours=2),
        ),
    ):
        pass


def test_given_upload_content_when_ingested_then_source_and_spans_share_version() -> None:
    # Arrange
    stream = io.BytesIO(b"# Leave\n\nEmployees receive leave.")

    # Act
    result = ingest_content(
        source_id="source-1",
        tenant_id="tenant-1",
        collection_id="collection-1",
        title="Policy",
        media_type="text/markdown",
        stream=stream,
        permission_hash="0" * 64,
        parser=SupportedDocumentParser(),
    )

    # Assert
    assert result.spans[0].source_version == result.document.source_version
