"""Shared deterministic domain fixtures."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime

import pytest

from shaper.domain import PermissionSnapshot, SourceDocument

ZERO_HASH = "0" * 64


@pytest.fixture
def source_document() -> SourceDocument:
    """Return a valid source document."""
    content_hash = hashlib.sha256(b"policy").hexdigest()
    return SourceDocument(
        source_id="source-1",
        source_version=content_hash,
        content_hash=content_hash,
        tenant_id="tenant-1",
        collection_id="collection-1",
        title="Policy",
        media_type="text/plain",
        observed_at=datetime(2026, 9, 9, tzinfo=UTC),
        permission=PermissionSnapshot(
            permission_hash=ZERO_HASH,
            captured_at=datetime(2026, 9, 9, tzinfo=UTC),
        ),
    )
