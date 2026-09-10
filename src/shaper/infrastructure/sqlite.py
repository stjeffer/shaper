"""Transactional SQLite state repositories and migrations."""

from __future__ import annotations

import sqlite3
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from shaper.application.jobs import JobConflictError
from shaper.domain import CompileJob

_MIGRATIONS = (
    """
    CREATE TABLE IF NOT EXISTS schema_migrations (
        version INTEGER PRIMARY KEY,
        applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS jobs (
        job_id TEXT PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        collection_id TEXT NOT NULL,
        idempotency_key TEXT NOT NULL,
        payload TEXT NOT NULL,
        revision INTEGER NOT NULL DEFAULT 0,
        UNIQUE (tenant_id, collection_id, idempotency_key)
    );
    CREATE TABLE IF NOT EXISTS records (
        category TEXT NOT NULL,
        record_id TEXT NOT NULL,
        payload TEXT NOT NULL,
        revision INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (category, record_id)
    );
    CREATE TABLE IF NOT EXISTS checkpoints (
        job_id TEXT NOT NULL,
        stage TEXT NOT NULL,
        payload TEXT NOT NULL,
        PRIMARY KEY (job_id, stage),
        FOREIGN KEY (job_id) REFERENCES jobs(job_id)
    );
    CREATE TABLE IF NOT EXISTS outbox (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT NOT NULL,
        payload TEXT NOT NULL,
        dispatched_at TEXT
    );
    """,
)


class ConcurrencyError(RuntimeError):
    """Raised when an optimistic write uses a stale revision."""


class SQLiteStore:
    """Local durable state with explicit transaction ownership."""

    def __init__(self, path: Path | str, *, journal_mode: str = "WAL") -> None:
        normalized_mode = journal_mode.upper()
        if normalized_mode not in {"DELETE", "WAL"}:
            raise ValueError("SQLite journal mode must be DELETE or WAL")
        self._path = str(path)
        self._journal_mode = normalized_mode
        self._connection: sqlite3.Connection | None = None
        self._lock = threading.RLock()

    def connect(self) -> None:
        """Open the store and configure safe local defaults."""
        if self._connection is not None:
            return
        connection = sqlite3.connect(
            self._path,
            isolation_level=None,
            check_same_thread=False,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        if self._path != ":memory:":
            connection.execute(f"PRAGMA journal_mode = {self._journal_mode}")
        self._connection = connection

    def close(self) -> None:
        """Close the active connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    @property
    def connection(self) -> sqlite3.Connection:
        """Return the active connection or raise an actionable error."""
        if self._connection is None:
            raise RuntimeError("SQLite store is not connected; call connect() first")
        return self._connection

    def migrate(self) -> None:
        """Apply every migration exactly once."""
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations "
            "(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
        )
        applied = {
            int(row[0]) for row in self.connection.execute("SELECT version FROM schema_migrations")
        }
        for version, migration in enumerate(_MIGRATIONS, start=1):
            if version in applied:
                continue
            with self.transaction() as connection:
                connection.executescript(migration)
                connection.execute(
                    "INSERT INTO schema_migrations(version) VALUES (?)",
                    (version,),
                )

    def is_ready(self) -> bool:
        """Return whether the connected database can execute a probe."""
        try:
            with self._lock:
                row = self.connection.execute("SELECT 1").fetchone()
                return row is not None and int(row[0]) == 1
        except (RuntimeError, sqlite3.Error):
            return False

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        """Commit related writes or roll them back together."""
        with self._lock:
            connection = self.connection
            connection.execute("BEGIN IMMEDIATE")
            try:
                yield connection
            except BaseException:
                connection.rollback()
                raise
            else:
                connection.commit()

    def create(self, job: CompileJob) -> CompileJob:
        """Create or return an idempotent compile job."""
        return self.create_job(job)

    def get(self, job_id: str) -> CompileJob | None:
        """Return a compile job by ID."""
        return self.get_job(job_id)

    def save(self, job: CompileJob, *, expected_revision: int) -> CompileJob:
        """Persist an optimistic compile-job update."""
        with self.transaction() as connection:
            row = connection.execute(
                "SELECT revision FROM jobs WHERE job_id = ?",
                (job.job_id,),
            ).fetchone()
            if row is None:
                raise KeyError(f"Compile job does not exist: {job.job_id}")
            current_revision = int(row["revision"])
            if current_revision != expected_revision:
                raise JobConflictError(
                    f"Stale job revision: expected {expected_revision}, current {current_revision}"
                )
            values = job.model_dump()
            values["revision"] = current_revision + 1
            values["updated_at"] = datetime.now(UTC)
            saved = CompileJob.model_validate(values)
            connection.execute(
                "UPDATE jobs SET payload = ?, revision = ? WHERE job_id = ?",
                (saved.model_dump_json(), saved.revision, saved.job_id),
            )
            return saved

    def values(self) -> tuple[CompileJob, ...]:
        """Return a stable snapshot of compile jobs."""
        with self._lock:
            rows = self.connection.execute("SELECT payload FROM jobs ORDER BY job_id").fetchall()
        return tuple(CompileJob.model_validate_json(row["payload"]) for row in rows)

    def create_job(self, job: CompileJob) -> CompileJob:
        """Create a job or return the existing idempotent submission."""
        payload = job.model_dump_json()
        with self.transaction() as connection:
            existing = connection.execute(
                "SELECT payload FROM jobs WHERE tenant_id = ? AND collection_id = ? "
                "AND idempotency_key = ?",
                (job.tenant_id, job.collection_id, job.idempotency_key),
            ).fetchone()
            if existing is not None:
                return CompileJob.model_validate_json(existing["payload"])
            connection.execute(
                "INSERT INTO jobs(job_id, tenant_id, collection_id, idempotency_key, payload) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    job.job_id,
                    job.tenant_id,
                    job.collection_id,
                    job.idempotency_key,
                    payload,
                ),
            )
            connection.execute(
                "INSERT INTO outbox(topic, payload) VALUES (?, ?)",
                ("job.created", payload),
            )
        return job

    def get_job(self, job_id: str) -> CompileJob | None:
        """Return a job by ID."""
        with self._lock:
            row = self.connection.execute(
                "SELECT payload FROM jobs WHERE job_id = ?",
                (job_id,),
            ).fetchone()
        return None if row is None else CompileJob.model_validate_json(row["payload"])

    def save_checkpoint(self, job_id: str, stage: str, payload: str) -> None:
        """Upsert one reconstructable job checkpoint."""
        with self.transaction() as connection:
            connection.execute(
                "INSERT INTO checkpoints(job_id, stage, payload) VALUES (?, ?, ?) "
                "ON CONFLICT(job_id, stage) DO UPDATE SET payload = excluded.payload",
                (job_id, stage, payload),
            )

    def load_record(self, *, category: str, record_id: str) -> tuple[str, int] | None:
        """Return a generic record payload and revision."""
        with self._lock:
            row = self.connection.execute(
                "SELECT payload, revision FROM records WHERE category = ? AND record_id = ?",
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
        """Insert or update a record using optimistic concurrency."""
        with self.transaction() as connection:
            row = connection.execute(
                "SELECT revision FROM records WHERE category = ? AND record_id = ?",
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
            current = int(row["revision"])
            if expected_revision != current:
                raise ConcurrencyError(
                    f"Stale {category!r} revision: expected {expected_revision}, current {current}"
                )
            next_revision = current + 1
            connection.execute(
                "UPDATE records SET payload = ?, revision = ? WHERE category = ? AND record_id = ?",
                (payload, next_revision, category, record_id),
            )
            return next_revision
