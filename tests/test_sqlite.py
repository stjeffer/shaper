"""SQLite repository contract tests."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest

from shaper.application.jobs import CompileJobService, QuotaExceededError
from shaper.domain import CollectionRole, CompileJob, OutputRef, Principal, SourceRef
from shaper.domain.models import OutputKind, SourceKind
from shaper.infrastructure.sqlite import ConcurrencyError, SQLiteStore


@pytest.fixture
def store(tmp_path: Path) -> Generator[SQLiteStore, None, None]:
    """Return a migrated file-backed store."""
    value = SQLiteStore(tmp_path / "state.db")
    value.connect()
    value.migrate()
    yield value
    value.close()


def make_job(*, job_id: str = "job-1") -> CompileJob:
    """Create a valid compile job."""
    return CompileJob(
        job_id=job_id,
        tenant_id="tenant-1",
        collection_id="collection-1",
        idempotency_key="request-1",
        submitted_by="person-1",
        requested_token_budget=100,
        source=SourceRef(
            tenant_id="tenant-1",
            collection_id="collection-1",
            kind=SourceKind.UPLOAD,
            locator="asset-1",
        ),
        output=OutputRef(kind=OutputKind.FILESYSTEM, root_id="local"),
    )


def test_given_same_idempotency_key_when_created_twice_then_original_job_is_returned(
    store: SQLiteStore,
) -> None:
    # Arrange
    original = make_job()
    duplicate = make_job(job_id="job-2")

    # Act
    store.create_job(original)
    result = store.create_job(duplicate)

    # Assert
    assert result.job_id == original.job_id


def test_given_transaction_error_when_writing_then_changes_are_rolled_back(
    store: SQLiteStore,
) -> None:
    # Act & Assert
    with pytest.raises(RuntimeError, match="stop"), store.transaction() as connection:
        connection.execute(
            "INSERT INTO records(category, record_id, payload) VALUES ('test', 'one', '{}')"
        )
        raise RuntimeError("stop")
    assert store.connection.execute("SELECT COUNT(*) FROM records").fetchone()[0] == 0


def test_given_stale_revision_when_record_updated_then_conflict_is_explicit(
    store: SQLiteStore,
) -> None:
    # Arrange
    revision = store.save_record(
        category="review",
        record_id="unit-1",
        payload="{}",
        expected_revision=0,
    )

    # Act & Assert
    with pytest.raises(ConcurrencyError, match="Stale"):
        store.save_record(
            category="review",
            record_id="unit-1",
            payload="{}",
            expected_revision=revision - 1,
        )


def test_given_service_restart_when_job_active_then_persisted_quota_is_enforced(
    store: SQLiteStore,
) -> None:
    caller = Principal(
        principal_id="person-1",
        tenant_id="tenant-1",
        collection_roles={"collection-1": frozenset({CollectionRole.COMPILE})},
    )
    first = make_job()
    CompileJobService(store).submit(
        principal=caller,
        source=first.source,
        output=first.output,
        idempotency_key="first",
        requested_token_budget=100,
    )

    with pytest.raises(QuotaExceededError, match="Collection"):
        CompileJobService(store).submit(
            principal=caller,
            source=first.source,
            output=first.output,
            idempotency_key="second",
            requested_token_budget=100,
        )


def test_given_delete_journal_mode_when_connected_then_wal_files_are_not_used(
    tmp_path: Path,
) -> None:
    store = SQLiteStore(tmp_path / "shared-state.db", journal_mode="DELETE")
    store.connect()
    try:
        assert store.connection.execute("PRAGMA journal_mode").fetchone()[0] == "delete"
    finally:
        store.close()
