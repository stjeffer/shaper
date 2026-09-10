"""Hosted compilation workflow and persistence tests."""

from __future__ import annotations

import json
from pathlib import Path

from shaper.application.compiler import CompilationService
from shaper.application.jobs import CompileJobService, CompileJobWorker
from shaper.application.ports import ModelResult
from shaper.application.review import ReviewService
from shaper.application.validation import DeterministicValidator
from shaper.domain import (
    CollectionRole,
    JobState,
    OutputRef,
    Principal,
    SourceRef,
)
from shaper.domain.models import OutputKind, SourceKind, UnitState
from shaper.infrastructure.compilation import (
    FilesystemCompilationPublisher,
    SQLiteCandidateStore,
    SQLiteCheckpointStore,
    SQLiteReviewStore,
)
from shaper.infrastructure.parsers import SupportedDocumentParser
from shaper.infrastructure.sqlite import SQLiteStore
from shaper.infrastructure.uploads import FileUploadStore


class Scanner:
    """Deterministic clean-file scanner."""

    def scan(self, content: bytes) -> str:
        del content
        return "clean"


class GroundedModel:
    """Create a candidate grounded in the first prompt span."""

    def generate(self, *, prompt: str, schema: dict[str, object]) -> ModelResult:
        del schema
        span = json.loads(prompt)["source"][0]
        return ModelResult(
            payload={
                "status": "candidate",
                "canonical_questions": ["What leave is available?"],
                "answer": span["text"],
                "claims": [{"text": span["text"], "span_ids": [span["span_id"]]}],
                "confidence": 0.95,
            },
            response_id="response-1",
            input_tokens=10,
            output_tokens=10,
        )


def _principal(*roles: CollectionRole) -> Principal:
    return Principal(
        principal_id="person-1",
        tenant_id="tenant-1",
        collection_roles={"collection-1": frozenset(roles)},
    )


def _submit_job(
    jobs: CompileJobService,
    uploads: FileUploadStore,
    *,
    key: str,
) -> str:
    principal = _principal(CollectionRole.COMPILE)
    asset = uploads.stage(
        [b"Employees receive 25 days of annual leave."],
        supplied_filename=f"{key}.txt",
        media_type="text/plain",
        principal=principal,
        collection_id="collection-1",
    )
    job = jobs.submit(
        principal=principal,
        source=SourceRef(
            tenant_id="tenant-1",
            collection_id="collection-1",
            kind=SourceKind.UPLOAD,
            locator=asset.asset_id,
        ),
        output=OutputRef(kind=OutputKind.FILESYSTEM, root_id="local"),
        idempotency_key=key,
        requested_token_budget=100,
    )
    return job.job_id


def test_given_uploaded_document_when_approved_then_release_is_published(tmp_path: Path) -> None:
    store = SQLiteStore(tmp_path / "state.db")
    store.connect()
    store.migrate()
    uploads = FileUploadStore(tmp_path / "uploads", scanner=Scanner())
    jobs = CompileJobService(store)
    candidates = SQLiteCandidateStore(store)
    reviews = ReviewService(SQLiteReviewStore(store))
    compiler = CompilationService(
        jobs=store,
        uploads=uploads,
        parser=SupportedDocumentParser(),
        model=GroundedModel(),
        validator=DeterministicValidator(),
        checkpoints=SQLiteCheckpointStore(store),
        candidates=candidates,
        reviews=reviews,
        publisher=FilesystemCompilationPublisher(tmp_path / "releases"),
    )
    job_id = _submit_job(jobs, uploads, key="first")

    awaiting_review = CompileJobWorker(store, compiler.compile).run(job_id)
    review = compiler.review_status(
        job_id,
        principal=_principal(CollectionRole.REVIEW),
    )
    approved, release_id = compiler.approve(
        job_id,
        principal=_principal(CollectionRole.REVIEW),
        reason="Evidence and answer verified.",
        expected_revision=review.revision,
    )

    assert awaiting_review.state is JobState.AWAITING_REVIEW
    assert approved.unit.state is UnitState.APPROVED
    completed = store.get(job_id)
    saved_candidate = candidates.get(job_id)
    assert completed is not None
    assert saved_candidate is not None
    assert completed.state is JobState.COMPLETED
    assert saved_candidate[0].release_id == release_id
    assert (tmp_path / "releases" / "current.json").is_file()
    store.close()


def test_given_current_release_when_second_unit_published_then_units_are_carried_forward(
    tmp_path: Path,
) -> None:
    store = SQLiteStore(tmp_path / "state.db")
    store.connect()
    store.migrate()
    uploads = FileUploadStore(tmp_path / "uploads", scanner=Scanner())
    jobs = CompileJobService(store)
    reviews = ReviewService(SQLiteReviewStore(store))
    compiler = CompilationService(
        jobs=store,
        uploads=uploads,
        parser=SupportedDocumentParser(),
        model=GroundedModel(),
        validator=DeterministicValidator(),
        checkpoints=SQLiteCheckpointStore(store),
        candidates=SQLiteCandidateStore(store),
        reviews=reviews,
        publisher=FilesystemCompilationPublisher(tmp_path / "releases"),
    )

    for key in ("first", "second"):
        job_id = _submit_job(jobs, uploads, key=key)
        CompileJobWorker(store, compiler.compile).run(job_id)
        review = compiler.review_status(job_id, principal=_principal(CollectionRole.REVIEW))
        compiler.approve(
            job_id,
            principal=_principal(CollectionRole.REVIEW),
            reason="Verified.",
            expected_revision=review.revision,
        )

    pointer = json.loads((tmp_path / "releases" / "current.json").read_text())
    units = (tmp_path / "releases" / "releases" / pointer["release_id"] / "units.jsonl").read_text()
    assert len(units.splitlines()) == 2
    store.close()
