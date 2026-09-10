"""Idempotent compile-job submission, quotas, status, and cancellation."""

from __future__ import annotations

import threading
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Protocol

from shaper.domain import (
    CollectionRole,
    CompileJob,
    JobState,
    OutputRef,
    Principal,
    SourceRef,
)


class JobStore(Protocol):
    """Compile-job repository boundary."""

    def create(self, job: CompileJob) -> CompileJob:
        """Create or return an idempotent job."""

    def get(self, job_id: str) -> CompileJob | None:
        """Return a job by ID."""

    def save(self, job: CompileJob, *, expected_revision: int) -> CompileJob:
        """Persist an optimistic job state update."""

    def values(self) -> tuple[CompileJob, ...]:
        """Return current jobs for bounded quota accounting."""


class JobConflictError(RuntimeError):
    """Raised for stale or invalid job state changes."""


class QuotaExceededError(RuntimeError):
    """Raised when server-side compile quotas reject a request."""


class InMemoryJobStore:
    """Thread-safe local job repository."""

    def __init__(self) -> None:
        self._jobs: dict[str, CompileJob] = {}
        self._idempotency: dict[tuple[str, str, str], str] = {}
        self._lock = threading.Lock()

    def create(self, job: CompileJob) -> CompileJob:
        """Create or return the prior idempotent submission."""
        key = (job.tenant_id, job.collection_id, job.idempotency_key)
        with self._lock:
            existing_id = self._idempotency.get(key)
            if existing_id is not None:
                return self._jobs[existing_id]
            self._jobs[job.job_id] = job
            self._idempotency[key] = job.job_id
            return job

    def get(self, job_id: str) -> CompileJob | None:
        """Return a job by ID."""
        return self._jobs.get(job_id)

    def save(self, job: CompileJob, *, expected_revision: int) -> CompileJob:
        """Update a job only at its current revision."""
        with self._lock:
            current = self._jobs.get(job.job_id)
            if current is None:
                raise KeyError(f"Compile job does not exist: {job.job_id}")
            if current.revision != expected_revision:
                raise JobConflictError(
                    f"Stale job revision: expected {expected_revision}, current {current.revision}"
                )
            values = job.model_dump()
            values["revision"] = current.revision + 1
            values["updated_at"] = datetime.now(UTC)
            saved = CompileJob.model_validate(values)
            self._jobs[job.job_id] = saved
            return saved

    def values(self) -> tuple[CompileJob, ...]:
        """Return a stable snapshot of current jobs."""
        return tuple(self._jobs.values())


@dataclass(frozen=True)
class CompileQuota:
    """Server-enforced compile submission and activity limits."""

    active_per_collection: int = 1
    active_per_principal: int = 2
    submissions_per_day: int = 10
    aggregate_token_budget: int = 1_000_000


class CompileJobService:
    """Authorize, quota, and persist compile jobs."""

    _ACTIVE = frozenset(
        {
            JobState.QUEUED,
            JobState.RUNNING,
            JobState.AWAITING_REVIEW,
            JobState.CANCELLING,
        }
    )

    def __init__(
        self,
        store: JobStore,
        *,
        quota: CompileQuota | None = None,
        now: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._store = store
        self._quota = quota or CompileQuota()
        self._now = now
        self._lock = threading.Lock()

    def submit(
        self,
        *,
        principal: Principal,
        source: SourceRef,
        output: OutputRef,
        idempotency_key: str,
        requested_token_budget: int,
    ) -> CompileJob:
        """Create an authorized idempotent compile job after quota checks."""
        principal.require(source.collection_id, CollectionRole.COMPILE)
        if principal.tenant_id != source.tenant_id:
            raise PermissionError("Compile source belongs to another tenant")
        with self._lock:
            existing = next(
                (
                    job
                    for job in self._store.values()
                    if job.tenant_id == source.tenant_id
                    and job.collection_id == source.collection_id
                    and job.idempotency_key == idempotency_key
                ),
                None,
            )
            if existing is not None:
                return existing
            self._enforce_quota(principal, source.collection_id, requested_token_budget)
            now = self._now()
            job = CompileJob(
                job_id=uuid.uuid4().hex,
                tenant_id=source.tenant_id,
                collection_id=source.collection_id,
                idempotency_key=idempotency_key,
                submitted_by=principal.principal_id,
                requested_token_budget=requested_token_budget,
                source=source,
                output=output,
                created_at=now,
                updated_at=now,
            )
            return self._store.create(job)

    def status(self, job_id: str, *, principal: Principal) -> CompileJob:
        """Return an authorized job status."""
        job = self._required(job_id)
        if principal.tenant_id != job.tenant_id:
            raise PermissionError("Compile job belongs to another tenant")
        roles = principal.collection_roles.get(job.collection_id, frozenset())
        if not roles.intersection(
            {CollectionRole.COMPILE, CollectionRole.ADMIN, CollectionRole.REVIEW}
        ):
            raise PermissionError("Principal cannot inspect this compile job")
        return job

    def cancel(self, job_id: str, *, principal: Principal) -> CompileJob:
        """Request cancellation without producing success-shaped partial output."""
        job = self.status(job_id, principal=principal)
        principal.require(job.collection_id, CollectionRole.COMPILE)
        if job.state not in {JobState.QUEUED, JobState.RUNNING}:
            raise JobConflictError(f"Job in state {job.state.value!r} cannot be cancelled")
        values = job.model_dump()
        values["state"] = JobState.CANCELLING
        return self._store.save(
            CompileJob.model_validate(values),
            expected_revision=job.revision,
        )

    def _required(self, job_id: str) -> CompileJob:
        job = self._store.get(job_id)
        if job is None:
            raise KeyError(f"Compile job does not exist: {job_id}")
        return job

    def _enforce_quota(
        self,
        principal: Principal,
        collection_id: str,
        requested_tokens: int,
    ) -> None:
        if not 0 < requested_tokens <= self._quota.aggregate_token_budget:
            raise QuotaExceededError("Requested model-token budget is invalid or exceeds the cap")
        jobs = self._store.values()
        active_collection = sum(
            job.collection_id == collection_id and job.state in self._ACTIVE for job in jobs
        )
        if active_collection >= self._quota.active_per_collection:
            raise QuotaExceededError("Collection already has the maximum active compile jobs")
        active_principal = sum(
            job.state in self._ACTIVE and job.submitted_by == principal.principal_id for job in jobs
        )
        if active_principal >= self._quota.active_per_principal:
            raise QuotaExceededError("Principal already has the maximum active compile jobs")
        cutoff = self._now() - timedelta(hours=24)
        submissions = sum(
            job.submitted_by == principal.principal_id and job.created_at >= cutoff for job in jobs
        )
        if submissions >= self._quota.submissions_per_day:
            raise QuotaExceededError("Principal exceeded the rolling 24-hour submission quota")
        reserved = sum(job.requested_token_budget for job in jobs if job.state in self._ACTIVE)
        if reserved + requested_tokens > self._quota.aggregate_token_budget:
            raise QuotaExceededError("Aggregate active model-token budget would be exceeded")


class CompileJobWorker:
    """Run one queued job through an injected checkpointed compiler."""

    def __init__(
        self,
        store: JobStore,
        execute: Callable[[CompileJob], JobState | None],
    ) -> None:
        self._store = store
        self._execute = execute

    def run(self, job_id: str) -> CompileJob:
        """Execute one job and persist explicit terminal state."""
        job = self._store.get(job_id)
        if job is None:
            raise KeyError(f"Compile job does not exist: {job_id}")
        if job.state is not JobState.QUEUED:
            raise JobConflictError(f"Only a queued job can run, not {job.state.value!r}")
        running = self._transition(job, JobState.RUNNING)
        try:
            result = self._execute(running)
        except Exception as error:
            failed_values = running.model_dump()
            failed_values["state"] = JobState.FAILED
            failed_values["diagnostic"] = f"{type(error).__name__}: {error}"
            return self._store.save(
                CompileJob.model_validate(failed_values),
                expected_revision=running.revision,
            )
        return self._transition(running, result or JobState.COMPLETED)

    def _transition(self, job: CompileJob, state: JobState) -> CompileJob:
        values = job.model_dump()
        values["state"] = state
        return self._store.save(
            CompileJob.model_validate(values),
            expected_revision=job.revision,
        )


class CompileJobDispatcher:
    """Continuously consume durable queued jobs in one hosted process."""

    def __init__(
        self,
        store: JobStore,
        worker: CompileJobWorker,
        *,
        poll_seconds: float = 0.1,
    ) -> None:
        if poll_seconds <= 0:
            raise ValueError("Dispatcher poll interval must be positive")
        self._store = store
        self._worker = worker
        self._poll_seconds = poll_seconds
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._failure: BaseException | None = None

    def start(self) -> None:
        """Start one background consumer."""
        if self._thread is not None:
            raise RuntimeError("Compile dispatcher is already started")
        self._thread = threading.Thread(
            target=self._run,
            name="shaper-compile-dispatcher",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        """Stop the consumer and wait for its current action."""
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=10)

    def is_ready(self) -> bool:
        """Return whether the dispatcher is alive and has not failed."""
        return self._thread is not None and self._thread.is_alive() and self._failure is None

    def _run(self) -> None:
        try:
            while not self._stop.is_set():
                queued = next(
                    (job for job in self._store.values() if job.state is JobState.QUEUED),
                    None,
                )
                if queued is None:
                    self._stop.wait(self._poll_seconds)
                    continue
                self._worker.run(queued.job_id)
        except BaseException as error:
            self._failure = error
