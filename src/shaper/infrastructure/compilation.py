"""SQLite-backed compilation state and filesystem release publication."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from shaper.application.compiler import (
    CandidateStore,
    CompilationRecord,
)
from shaper.application.publication import PublishableUnit, assemble_release
from shaper.application.review import ReviewRecord, ReviewStore
from shaper.domain import AnswerUnit, ReleaseManifest, ReviewDecision
from shaper.infrastructure.filesystem_sink import FilesystemReleaseSink
from shaper.infrastructure.sqlite import SQLiteStore


class SQLiteCheckpointStore:
    """Persist the latest payload for each shaping stage."""

    def __init__(self, store: SQLiteStore) -> None:
        self._store = store

    def save(self, run_id: str, state: str, payload: str) -> None:
        """Persist one idempotent shaping checkpoint."""
        self._store.save_checkpoint(run_id, state, payload)


class SQLiteCandidateStore(CandidateStore):
    """Persist job-to-candidate associations in generic state records."""

    _CATEGORY = "compilation"

    def __init__(self, store: SQLiteStore) -> None:
        self._store = store

    def get(self, job_id: str) -> tuple[CompilationRecord, int] | None:
        """Return one candidate and storage revision."""
        stored = self._store.load_record(category=self._CATEGORY, record_id=job_id)
        if stored is None:
            return None
        payload, revision = stored
        return CompilationRecord.model_validate_json(payload), revision

    def save(
        self,
        record: CompilationRecord,
        *,
        expected_revision: int,
    ) -> tuple[CompilationRecord, int]:
        """Persist one candidate using optimistic concurrency."""
        revision = self._store.save_record(
            category=self._CATEGORY,
            record_id=record.job_id,
            payload=record.model_dump_json(),
            expected_revision=expected_revision,
        )
        return record, revision


class SQLiteReviewStore(ReviewStore):
    """Persist review records with optimistic revisions."""

    _CATEGORY = "review"

    def __init__(self, store: SQLiteStore) -> None:
        self._store = store

    def get(self, unit_id: str) -> ReviewRecord | None:
        """Return one review record."""
        stored = self._store.load_record(category=self._CATEGORY, record_id=unit_id)
        if stored is None:
            return None
        payload, _revision = stored
        value = json.loads(payload)
        return ReviewRecord(
            unit=AnswerUnit.model_validate_json(json.dumps(value["unit"])),
            revision=int(value["revision"]),
            decisions=tuple(
                ReviewDecision.model_validate_json(json.dumps(decision))
                for decision in value["decisions"]
            ),
        )

    def save(self, record: ReviewRecord, *, expected_revision: int) -> ReviewRecord:
        """Persist a review transition and return its next revision."""
        saved = ReviewRecord(
            unit=record.unit,
            revision=expected_revision + 1,
            decisions=record.decisions,
        )
        self._store.save_record(
            category=self._CATEGORY,
            record_id=record.unit.unit_id,
            payload=json.dumps(
                {
                    "unit": saved.unit.model_dump(mode="json"),
                    "revision": saved.revision,
                    "decisions": [decision.model_dump(mode="json") for decision in saved.decisions],
                },
                sort_keys=True,
                default=str,
            ),
            expected_revision=expected_revision,
        )
        return saved


class FilesystemCompilationPublisher:
    """Publish approved candidates while carrying current units forward."""

    def __init__(self, root: Path) -> None:
        self._root = root
        self._sink = FilesystemReleaseSink(root)

    def publish(self, record: CompilationRecord, approved: ReviewRecord) -> str:
        """Publish one approved candidate into a complete release snapshot."""
        if not approved.decisions:
            raise ValueError("Approved compilation has no human review decision")
        current_manifest, carried_forward = self._load_current()
        bundle = assemble_release(
            tenant_id=record.tenant_id,
            collection_id=record.collection_id,
            run_id=record.run_id,
            created_at=datetime.now(UTC),
            newly_approved=(
                PublishableUnit(
                    unit=approved.unit,
                    permission_hash=record.permission_hash,
                    approval_id=approved.decisions[-1].decision_id,
                    origin_run_id=record.run_id,
                ),
            ),
            carried_forward=carried_forward,
            previous_release_id=(None if current_manifest is None else current_manifest.release_id),
        )
        result = self._sink.publish(
            bundle,
            expected_current_hash=self._sink.current_hash(),
        )
        return result.release_id

    def _load_current(
        self,
    ) -> tuple[ReleaseManifest | None, tuple[PublishableUnit, ...]]:
        pointer_path = self._root / "current.json"
        if not pointer_path.is_file():
            return None, ()
        pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
        release_id = pointer.get("release_id")
        if not isinstance(release_id, str):
            raise ValueError("Current release pointer has no release ID")
        release_root = self._root / "releases" / release_id
        manifest = ReleaseManifest.model_validate_json(
            (release_root / "manifest.json").read_bytes()
        )
        units = tuple(
            AnswerUnit.model_validate_json(line)
            for line in (release_root / "units.jsonl").read_bytes().splitlines()
            if line
        )
        refs = {item.unit_id: item for item in manifest.units}
        carried = tuple(
            PublishableUnit(
                unit=unit,
                permission_hash=refs[unit.unit_id].permission_hash,
                approval_id=refs[unit.unit_id].approval_id,
                origin_run_id=refs[unit.unit_id].origin_run_id,
            )
            for unit in units
        )
        return manifest, carried
