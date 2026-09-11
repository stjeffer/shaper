"""PostgreSQL persistence for production knowledge-estate records."""

from __future__ import annotations

import json
import threading
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from typing import Any, cast

import psycopg
from psycopg import Connection
from psycopg.rows import dict_row

from shaper.application.jobs import JobConflictError
from shaper.application.review import ReviewConflictError, ReviewRecord
from shaper.domain import AnswerUnit, CompileJob, ReviewDecision
from shaper.infrastructure.sqlite import (
    ConcurrencyError,
    SQLiteEstateRepository,
    SQLiteStore,
)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS records (
    category TEXT NOT NULL,
    record_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    revision INTEGER NOT NULL CHECK (revision > 0),
    PRIMARY KEY (category, record_id)
);
CREATE INDEX IF NOT EXISTS ix_records_category
    ON records(category, record_id);
"""


class _Cursor:
    def __init__(self, cursor: psycopg.Cursor[dict[str, Any]]) -> None:
        self._cursor = cursor

    def fetchone(self) -> dict[str, Any] | None:
        return self._cursor.fetchone()

    def fetchall(self) -> list[dict[str, Any]]:
        return self._cursor.fetchall()


class _TransactionConnection:
    def __init__(self, connection: Connection[dict[str, Any]]) -> None:
        self._connection = connection

    def execute(
        self,
        statement: str,
        parameters: Sequence[object] = (),
    ) -> _Cursor:
        translated = statement.replace("?", "%s")
        return _Cursor(self._connection.execute(translated, parameters))


class PostgresRecordStore:
    """Small optimistic record store with explicit transaction ownership."""

    def __init__(self, connection_url: str) -> None:
        if not connection_url.startswith(("postgresql://", "postgres://")):
            raise ValueError("PostgreSQL connection URL must use postgresql://")
        self._connection_url = connection_url
        self._connection: Connection[dict[str, Any]] | None = None
        self._lock = threading.RLock()

    def connect(self) -> None:
        """Open one bounded application connection."""
        if self._connection is None:
            self._connection = psycopg.connect(
                self._connection_url,
                row_factory=dict_row,
                connect_timeout=10,
                autocommit=True,
            )

    def close(self) -> None:
        """Close the active connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    @property
    def connection(self) -> Connection[dict[str, Any]]:
        if self._connection is None:
            raise RuntimeError("PostgreSQL store is not connected; call connect() first")
        return self._connection

    def migrate(self) -> None:
        """Create the generic optimistic record schema."""
        with self.transaction() as connection:
            existing = connection.execute(
                "SELECT to_regclass('public.records') AS record_table"
            ).fetchone()
            if existing is not None and existing["record_table"] is not None:
                return
            for statement in _SCHEMA.split(";"):
                if statement.strip():
                    connection.execute(statement)

    def is_ready(self) -> bool:
        """Return whether PostgreSQL can execute a probe."""
        try:
            with self._lock:
                row = self.connection.execute("SELECT 1 AS ready").fetchone()
                return row is not None and int(row["ready"]) == 1
        except (RuntimeError, psycopg.Error):
            return False

    @contextmanager
    def transaction(self) -> Iterator[_TransactionConnection]:
        """Commit related writes or roll them back together."""
        with self._lock, self.connection.transaction():
            yield _TransactionConnection(self.connection)

    def load_record(
        self,
        *,
        category: str,
        record_id: str,
    ) -> tuple[str, int] | None:
        with self._lock:
            row = self.connection.execute(
                "SELECT payload, revision FROM records WHERE category = %s AND record_id = %s",
                (category, record_id),
            ).fetchone()
        if row is None:
            return None
        return str(row["payload"]), int(row["revision"])

    def save_record(
        self,
        *,
        category: str,
        record_id: str,
        payload: str,
        expected_revision: int | None,
    ) -> int:
        with self.transaction() as connection:
            row = connection.execute(
                "SELECT revision FROM records WHERE category = ? AND record_id = ? FOR UPDATE",
                (category, record_id),
            ).fetchone()
            if row is None:
                if expected_revision not in (None, 0):
                    raise ConcurrencyError("Cannot update a record that does not exist")
                connection.execute(
                    "INSERT INTO records(category, record_id, payload, revision) "
                    "VALUES (?, ?, ?, 1)",
                    (category, record_id, payload),
                )
                return 1
            current_revision = int(row["revision"])
            if expected_revision == 0:
                raise ConcurrencyError("Record already exists")
            if expected_revision is not None and expected_revision != current_revision:
                raise ConcurrencyError(
                    f"Stale record revision: expected {expected_revision}, "
                    f"current {current_revision}"
                )
            revision = current_revision + 1
            connection.execute(
                "UPDATE records SET payload = ?, revision = ? WHERE category = ? AND record_id = ?",
                (payload, revision, category, record_id),
            )
            return revision

    def list_records(self, *, category: str) -> tuple[tuple[str, str, int], ...]:
        with self._lock:
            rows = self.connection.execute(
                "SELECT record_id, payload, revision FROM records "
                "WHERE category = %s ORDER BY record_id",
                (category,),
            ).fetchall()
        return tuple(
            (str(row["record_id"]), str(row["payload"]), int(row["revision"])) for row in rows
        )


class PostgresEstateRepository(SQLiteEstateRepository):
    """Reuse repository serialization over the PostgreSQL record-store contract."""

    def __init__(self, store: PostgresRecordStore) -> None:
        super().__init__(cast(SQLiteStore, store))


class PostgresJobStore:
    """Durable compile-job persistence over the production record store."""

    def __init__(self, store: PostgresRecordStore) -> None:
        self._store = store

    def create(self, job: CompileJob) -> CompileJob:
        for current in self.values():
            if (
                current.tenant_id,
                current.collection_id,
                current.idempotency_key,
            ) == (job.tenant_id, job.collection_id, job.idempotency_key):
                return current
        self._store.save_record(
            category="compile_job",
            record_id=job.job_id,
            payload=job.model_dump_json(),
            expected_revision=0,
        )
        return job

    def get(self, job_id: str) -> CompileJob | None:
        record = self._store.load_record(category="compile_job", record_id=job_id)
        return None if record is None else CompileJob.model_validate_json(record[0])

    def save(self, job: CompileJob, *, expected_revision: int) -> CompileJob:
        current = self.get(job.job_id)
        if current is None:
            raise KeyError(f"Compile job does not exist: {job.job_id}")
        if current.revision != expected_revision:
            raise JobConflictError(
                f"Stale job revision: expected {expected_revision}, current {current.revision}"
            )
        values = job.model_dump()
        values["revision"] = current.revision + 1
        saved = CompileJob.model_validate(values)
        self._store.save_record(
            category="compile_job",
            record_id=job.job_id,
            payload=saved.model_dump_json(),
            expected_revision=expected_revision + 1,
        )
        return saved

    def values(self) -> tuple[CompileJob, ...]:
        return tuple(
            CompileJob.model_validate_json(payload)
            for _, payload, _ in self._store.list_records(category="compile_job")
        )


class PostgresReviewStore:
    """Durable output-review state over the production record store."""

    def __init__(self, store: PostgresRecordStore) -> None:
        self._store = store

    def get(self, unit_id: str) -> ReviewRecord | None:
        record = self._store.load_record(category="output_review", record_id=unit_id)
        if record is None:
            return None
        payload = json.loads(record[0])
        if not isinstance(payload, dict):
            raise ValueError("Stored output review must be an object")
        decisions = payload.get("decisions", [])
        if not isinstance(decisions, list):
            raise ValueError("Stored output review decisions must be an array")
        return ReviewRecord(
            unit=AnswerUnit.model_validate(payload.get("unit")),
            revision=record[1],
            decisions=tuple(ReviewDecision.model_validate(item) for item in decisions),
        )

    def save(self, record: ReviewRecord, *, expected_revision: int) -> ReviewRecord:
        current = self.get(record.unit.unit_id)
        current_revision = 0 if current is None else current.revision
        if current_revision != expected_revision:
            raise ReviewConflictError(
                f"Stale review revision: expected {expected_revision}, current {current_revision}"
            )
        payload = json.dumps(
            {
                "unit": record.unit.model_dump(mode="json"),
                "decisions": [decision.model_dump(mode="json") for decision in record.decisions],
            },
            separators=(",", ":"),
            sort_keys=True,
        )
        revision = self._store.save_record(
            category="output_review",
            record_id=record.unit.unit_id,
            payload=payload,
            expected_revision=expected_revision,
        )
        return ReviewRecord(
            unit=record.unit,
            revision=revision,
            decisions=record.decisions,
        )
