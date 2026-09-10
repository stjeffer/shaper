"""Transactional SQLite state repositories and migrations."""

from __future__ import annotations

import base64
import sqlite3
import threading
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import TypeVar

from shaper.application.estates import EstateRepository, VersionedRecord
from shaper.application.jobs import JobConflictError
from shaper.domain import (
    CollectionGrant,
    CompileJob,
    DocumentReadinessReport,
    EstateDocument,
    EstateSource,
    KnowledgeArtifact,
    KnowledgeEstate,
    KnowledgeTransformationAnalysis,
    PurgeTombstone,
    TokenUsage,
    TransformationDecision,
    TransformationProposal,
    WorkflowRun,
)
from shaper.domain.models import DomainModel

RecordModel = TypeVar("RecordModel", bound=DomainModel)

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

    def list_records(self, *, category: str) -> tuple[tuple[str, str, int], ...]:
        """Return stable generic records for one category."""
        with self._lock:
            rows = self.connection.execute(
                "SELECT record_id, payload, revision FROM records "
                "WHERE category = ? ORDER BY record_id",
                (category,),
            ).fetchall()
        return tuple(
            (str(row["record_id"]), str(row["payload"]), int(row["revision"])) for row in rows
        )


class SQLiteEstateRepository(EstateRepository):
    """Estate repository backed by the local generic-record table."""

    _PURGE_CATEGORIES = (
        "estate_source",
        "estate_document",
        "document_content",
        "estate_run",
        "readiness_report",
        "estate_analysis",
        "transformation_proposal",
        "transformation_decision",
        "token_usage",
        "knowledge_artifact",
    )

    def __init__(self, store: SQLiteStore) -> None:
        self._store = store

    def create_estate(self, estate: KnowledgeEstate) -> VersionedRecord[KnowledgeEstate]:
        return self._save("knowledge_estate", estate.estate_id, estate)

    def get_estate(self, estate_id: str) -> VersionedRecord[KnowledgeEstate] | None:
        return self._load("knowledge_estate", estate_id, KnowledgeEstate)

    def list_estates(self, collection_id: str) -> tuple[VersionedRecord[KnowledgeEstate], ...]:
        return tuple(
            record
            for record in self._list("knowledge_estate", KnowledgeEstate)
            if record.value.collection_id == collection_id
        )

    def save_estate(
        self,
        estate: KnowledgeEstate,
        *,
        expected_revision: int,
    ) -> VersionedRecord[KnowledgeEstate]:
        return self._save(
            "knowledge_estate",
            estate.estate_id,
            estate,
            expected_revision=expected_revision,
        )

    def save_source(
        self,
        source: EstateSource,
        *,
        expected_revision: int | None = None,
    ) -> VersionedRecord[EstateSource]:
        return self._save(
            "estate_source",
            source.source_id,
            source,
            expected_revision=expected_revision,
        )

    def get_source(self, source_id: str) -> VersionedRecord[EstateSource] | None:
        return self._load("estate_source", source_id, EstateSource)

    def list_sources(self, estate_id: str) -> tuple[VersionedRecord[EstateSource], ...]:
        return tuple(
            record
            for record in self._list("estate_source", EstateSource)
            if record.value.estate_id == estate_id
        )

    def save_document(
        self,
        document: EstateDocument,
        *,
        expected_revision: int | None = None,
    ) -> VersionedRecord[EstateDocument]:
        return self._save(
            "estate_document",
            document.document_id,
            document,
            expected_revision=expected_revision,
        )

    def get_document(self, document_id: str) -> VersionedRecord[EstateDocument] | None:
        return self._load("estate_document", document_id, EstateDocument)

    def list_documents(self, estate_id: str) -> tuple[VersionedRecord[EstateDocument], ...]:
        return tuple(
            record
            for record in self._list("estate_document", EstateDocument)
            if record.value.estate_id == estate_id
        )

    def save_document_content(
        self,
        document_id: str,
        source_version: str,
        text: str,
    ) -> None:
        if not text.strip():
            raise ValueError("Document content cannot be empty")
        self._store.save_record(
            category="document_content",
            record_id=f"{document_id}:{source_version}",
            payload=text,
            expected_revision=0,
        )

    def load_document_content(self, document_id: str, source_version: str) -> str:
        record = self._store.load_record(
            category="document_content",
            record_id=f"{document_id}:{source_version}",
        )
        if record is None:
            raise KeyError(f"Document content does not exist: {document_id}@{source_version}")
        return record[0]

    def save_inventory(
        self,
        items: Sequence[tuple[EstateDocument, str]],
    ) -> tuple[VersionedRecord[EstateDocument], ...]:
        """Atomically save inventory rows and exact-version normalized text."""
        saved: list[VersionedRecord[EstateDocument]] = []
        with self._store.transaction() as connection:
            for document, text in items:
                if not text.strip():
                    raise ValueError("Document content cannot be empty")
                row = connection.execute(
                    "SELECT revision, payload FROM records "
                    "WHERE category = 'estate_document' AND record_id = ?",
                    (document.document_id,),
                ).fetchone()
                revision = 1 if row is None else int(row["revision"]) + 1
                if row is None:
                    connection.execute(
                        "INSERT INTO records(category, record_id, payload, revision) "
                        "VALUES ('estate_document', ?, ?, ?)",
                        (document.document_id, document.model_dump_json(), revision),
                    )
                elif (
                    EstateDocument.model_validate_json(str(row["payload"])).source_version
                    != document.source_version
                ):
                    connection.execute(
                        "UPDATE records SET payload = ?, revision = ? "
                        "WHERE category = 'estate_document' AND record_id = ?",
                        (document.model_dump_json(), revision, document.document_id),
                    )
                else:
                    revision = int(row["revision"])
                content_id = f"{document.document_id}:{document.source_version}"
                connection.execute(
                    "INSERT INTO records(category, record_id, payload, revision) "
                    "VALUES ('document_content', ?, ?, 1) "
                    "ON CONFLICT(category, record_id) DO NOTHING",
                    (content_id, text),
                )
                saved.append(VersionedRecord(document, revision))
        return tuple(saved)

    def save_run(
        self,
        run: WorkflowRun,
        *,
        expected_revision: int | None = None,
    ) -> VersionedRecord[WorkflowRun]:
        return self._save(
            "estate_run",
            run.run_id,
            run,
            expected_revision=expected_revision,
        )

    def get_run(self, run_id: str) -> VersionedRecord[WorkflowRun] | None:
        return self._load("estate_run", run_id, WorkflowRun)

    def list_runs(self, estate_id: str) -> tuple[VersionedRecord[WorkflowRun], ...]:
        return tuple(
            record
            for record in self._list("estate_run", WorkflowRun)
            if record.value.estate_id == estate_id
        )

    def append_report(self, report: DocumentReadinessReport) -> None:
        self._save("readiness_report", report.report_id, report)

    def list_reports(self, run_id: str) -> tuple[DocumentReadinessReport, ...]:
        return tuple(
            record.value
            for record in self._list("readiness_report", DocumentReadinessReport)
            if record.value.run_id == run_id
        )

    def save_analysis(self, run_id: str, analysis: KnowledgeTransformationAnalysis) -> None:
        self._save("estate_analysis", run_id, analysis)

    def load_analysis(self, run_id: str) -> KnowledgeTransformationAnalysis | None:
        record = self._load("estate_analysis", run_id, KnowledgeTransformationAnalysis)
        return None if record is None else record.value

    def append_proposal(self, proposal: TransformationProposal) -> None:
        self._save("transformation_proposal", proposal.recommendation_id, proposal)

    def get_proposal(self, recommendation_id: str) -> TransformationProposal | None:
        record = self._load(
            "transformation_proposal",
            recommendation_id,
            TransformationProposal,
        )
        return None if record is None else record.value

    def list_proposals(self, run_id: str) -> tuple[TransformationProposal, ...]:
        return tuple(
            record.value
            for record in self._list("transformation_proposal", TransformationProposal)
            if record.value.run_id == run_id
        )

    def append_decision(self, decision: TransformationDecision) -> None:
        self._save("transformation_decision", decision.decision_id, decision)

    def latest_decision(self, document_id: str) -> TransformationDecision | None:
        matches = [
            record.value
            for record in self._list("transformation_decision", TransformationDecision)
            if record.value.document_id == document_id
        ]
        return max(matches, key=lambda item: item.decided_at) if matches else None

    def append_usage(self, usage: TokenUsage) -> None:
        self._save(
            "token_usage",
            f"{usage.run_id}:{usage.document_id}",
            usage,
        )

    def list_usage(self, run_id: str) -> tuple[TokenUsage, ...]:
        return tuple(
            record.value
            for record in self._list("token_usage", TokenUsage)
            if record.value.run_id == run_id
        )

    def append_artifact(self, artifact: KnowledgeArtifact) -> None:
        self._save("knowledge_artifact", artifact.artifact_id, artifact)

    def get_artifact(self, artifact_id: str) -> VersionedRecord[KnowledgeArtifact] | None:
        return self._load("knowledge_artifact", artifact_id, KnowledgeArtifact)

    def save_artifact(
        self,
        artifact: KnowledgeArtifact,
        *,
        expected_revision: int,
    ) -> VersionedRecord[KnowledgeArtifact]:
        return self._save(
            "knowledge_artifact",
            artifact.artifact_id,
            artifact,
            expected_revision=expected_revision,
        )

    def save_artifact_content(self, artifact_id: str, content: bytes) -> None:
        self._store.save_record(
            category="artifact_content",
            record_id=artifact_id,
            payload=base64.b64encode(content).decode("ascii"),
            expected_revision=0,
        )

    def load_artifact_content(self, artifact_id: str) -> bytes:
        record = self._store.load_record(category="artifact_content", record_id=artifact_id)
        if record is None:
            raise KeyError(f"Artifact content does not exist: {artifact_id}")
        return base64.b64decode(record[0], validate=True)

    def save_artifact_bundle(self, artifact: KnowledgeArtifact, content: bytes) -> None:
        with self._store.transaction() as connection:
            connection.execute(
                "INSERT INTO records(category, record_id, payload, revision) VALUES (?, ?, ?, 1)",
                (
                    "knowledge_artifact",
                    artifact.artifact_id,
                    artifact.model_dump_json(),
                ),
            )
            connection.execute(
                "INSERT INTO records(category, record_id, payload, revision) VALUES (?, ?, ?, 1)",
                (
                    "artifact_content",
                    artifact.artifact_id,
                    base64.b64encode(content).decode("ascii"),
                ),
            )

    def save_shaping_checkpoint(self, run_id: str, state: str, payload: str) -> None:
        record_id = f"{run_id}:{state}"
        current = self._store.load_record(category="shaping_checkpoint", record_id=record_id)
        self._store.save_record(
            category="shaping_checkpoint",
            record_id=record_id,
            payload=payload,
            expected_revision=0 if current is None else current[1],
        )

    def list_artifacts(self, estate_id: str) -> tuple[KnowledgeArtifact, ...]:
        return tuple(
            record.value
            for record in self._list("knowledge_artifact", KnowledgeArtifact)
            if record.value.estate_id == estate_id
        )

    def save_grant(self, grant: CollectionGrant) -> None:
        record_id = f"{grant.tenant_id}:{grant.principal_id}:{grant.collection_id}"
        current = self._store.load_record(category="collection_grant", record_id=record_id)
        self._store.save_record(
            category="collection_grant",
            record_id=record_id,
            payload=grant.model_dump_json(),
            expected_revision=0 if current is None else current[1],
        )

    def grants_for(self, tenant_id: str, principal_id: str) -> tuple[CollectionGrant, ...]:
        return tuple(
            record.value
            for record in self._list("collection_grant", CollectionGrant)
            if record.value.tenant_id == tenant_id and record.value.principal_id == principal_id
        )

    def purge_estate(self, estate_id: str, tombstone: PurgeTombstone) -> None:
        with self._store.transaction() as connection:
            document_rows = connection.execute(
                "SELECT record_id FROM records WHERE category = 'estate_document' "
                "AND payload LIKE ?",
                (f'%"estate_id":"{estate_id}"%',),
            ).fetchall()
            document_ids = tuple(str(row["record_id"]) for row in document_rows)
            run_rows = connection.execute(
                "SELECT record_id FROM records WHERE category = 'estate_run' AND payload LIKE ?",
                (f'%"estate_id":"{estate_id}"%',),
            ).fetchall()
            run_ids = tuple(str(row["record_id"]) for row in run_rows)
            artifact_rows = connection.execute(
                "SELECT record_id FROM records WHERE category = 'knowledge_artifact' "
                "AND payload LIKE ?",
                (f'%"estate_id":"{estate_id}"%',),
            ).fetchall()
            artifact_ids = tuple(str(row["record_id"]) for row in artifact_rows)
            for category in self._PURGE_CATEGORIES:
                rows = connection.execute(
                    "SELECT record_id, payload FROM records WHERE category = ?",
                    (category,),
                ).fetchall()
                for row in rows:
                    payload = str(row["payload"])
                    if f'"estate_id":"{estate_id}"' in payload:
                        connection.execute(
                            "DELETE FROM records WHERE category = ? AND record_id = ?",
                            (category, str(row["record_id"])),
                        )
            for document_id in document_ids:
                connection.execute(
                    "DELETE FROM records WHERE category = 'document_content' AND record_id LIKE ?",
                    (f"{document_id}:%",),
                )
                connection.execute(
                    "DELETE FROM records WHERE category = 'token_usage' AND record_id LIKE ?",
                    (f"%:{document_id}",),
                )
            for run_id in run_ids:
                connection.execute(
                    "DELETE FROM records WHERE category = 'token_usage' AND record_id LIKE ?",
                    (f"{run_id}:%",),
                )
                connection.execute(
                    "DELETE FROM records WHERE category = 'shaping_checkpoint' "
                    "AND record_id LIKE ?",
                    (f"{run_id}:%",),
                )
            for artifact_id in artifact_ids:
                connection.execute(
                    "DELETE FROM records WHERE category = 'artifact_content' AND record_id = ?",
                    (artifact_id,),
                )
            connection.execute(
                "DELETE FROM records WHERE category = 'knowledge_estate' AND record_id = ?",
                (estate_id,),
            )
            connection.execute(
                "INSERT INTO records(category, record_id, payload, revision) VALUES (?, ?, ?, 1)",
                ("purge_tombstone", estate_id, tombstone.model_dump_json()),
            )

    def _save(
        self,
        category: str,
        record_id: str,
        value: RecordModel,
        *,
        expected_revision: int | None = 0,
    ) -> VersionedRecord[RecordModel]:
        revision = self._store.save_record(
            category=category,
            record_id=record_id,
            payload=value.model_dump_json(),
            expected_revision=expected_revision,
        )
        return VersionedRecord(value=value, revision=revision)

    def _load(
        self,
        category: str,
        record_id: str,
        model: type[RecordModel],
    ) -> VersionedRecord[RecordModel] | None:
        record = self._store.load_record(category=category, record_id=record_id)
        if record is None:
            return None
        payload, revision = record
        return VersionedRecord(value=model.model_validate_json(payload), revision=revision)

    def _list(
        self,
        category: str,
        model: type[RecordModel],
    ) -> tuple[VersionedRecord[RecordModel], ...]:
        return tuple(
            VersionedRecord(value=model.model_validate_json(payload), revision=revision)
            for _, payload, revision in self._store.list_records(category=category)
        )
