"""Normalize connector content into immutable source documents and spans."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import BinaryIO

from shaper.application.ports import DocumentParser
from shaper.domain import PermissionSnapshot, SourceDocument, SourceSpan


@dataclass(frozen=True)
class IngestedDocument:
    """Normalized source document and its ordered evidence spans."""

    document: SourceDocument
    spans: tuple[SourceSpan, ...]


def ingest_content(
    *,
    source_id: str,
    tenant_id: str,
    collection_id: str,
    title: str,
    media_type: str,
    stream: BinaryIO,
    permission_hash: str,
    parser: DocumentParser,
    observed_at: datetime | None = None,
    maximum_bytes: int = 50 * 1024 * 1024,
) -> IngestedDocument:
    """Read bounded content and normalize it through the selected parser."""
    content = stream.read(maximum_bytes + 1)
    if len(content) > maximum_bytes:
        raise ValueError(f"Source {source_id!r} exceeds the {maximum_bytes}-byte parser limit")
    if not content:
        raise ValueError(f"Source {source_id!r} is empty")
    content_hash = hashlib.sha256(content).hexdigest()
    timestamp = observed_at or datetime.now(UTC)
    document = SourceDocument(
        source_id=source_id,
        source_version=content_hash,
        content_hash=content_hash,
        tenant_id=tenant_id,
        collection_id=collection_id,
        title=title,
        media_type=media_type,
        observed_at=timestamp,
        permission=PermissionSnapshot(
            permission_hash=permission_hash,
            captured_at=timestamp,
        ),
    )
    spans = tuple(parser.parse(document, content))
    if not spans:
        raise ValueError(f"Source {source_id!r} produced no readable source spans")
    return IngestedDocument(document=document, spans=spans)
