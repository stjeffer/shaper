"""Protocols implemented by infrastructure adapters."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from contextlib import AbstractContextManager
from dataclasses import dataclass
from datetime import datetime
from typing import BinaryIO, Protocol, TypeVar

from shaper.domain import (
    AnswerUnit,
    CompileJob,
    Principal,
    ReleaseManifest,
    SourceDocument,
    SourceRef,
    SourceSpan,
    ValidationFinding,
)

T = TypeVar("T")


@dataclass(frozen=True)
class SourceChange:
    """Normalized connector change event."""

    kind: str
    document: SourceDocument | None
    source_id: str
    checkpoint: str
    content: bytes | None = None


@dataclass(frozen=True)
class ModelResult:
    """Provider-neutral structured model result."""

    payload: dict[str, object]
    response_id: str
    input_tokens: int
    output_tokens: int


@dataclass(frozen=True)
class UploadAssetMetadata:
    """Metadata required to ingest one authorized scanned upload."""

    asset_id: str
    filename: str
    media_type: str


class SourceConnector(Protocol):
    """Read source changes from a configured boundary."""

    def changes(self, source: SourceRef, *, checkpoint: str | None) -> Iterator[SourceChange]:
        """Yield normalized source changes."""


class UploadStore(Protocol):
    """Store and retrieve scanned upload assets."""

    def describe(self, asset_id: str, principal: Principal) -> UploadAssetMetadata:
        """Return authorized metadata for one scanned upload."""

    def open_asset(
        self,
        asset_id: str,
        principal: Principal,
    ) -> AbstractContextManager[BinaryIO]:
        """Open an authorized, scanned asset."""


class MalwareScanner(Protocol):
    """Scan untrusted upload bytes before they can become source content."""

    def scan(self, content: bytes) -> str:
        """Return a stable scan engine result of ``clean`` or ``infected``."""


class DocumentParser(Protocol):
    """Parse a source into immutable spans."""

    def parse(self, document: SourceDocument, content: bytes) -> Sequence[SourceSpan]:
        """Return ordered source spans."""


class ModelGateway(Protocol):
    """Generate schema-constrained model output."""

    def generate(self, *, prompt: str, schema: dict[str, object]) -> ModelResult:
        """Generate one structured result or raise an explicit provider error."""


class AgentTool(Protocol):
    """Typed, read-only agent capability."""

    @property
    def name(self) -> str:
        """Return the immutable tool name."""

    def invoke(self, arguments: dict[str, object], principal: Principal) -> object:
        """Invoke the tool inside an authorization boundary."""


class Validator(Protocol):
    """Validate a candidate independently of its producer."""

    def validate(
        self,
        unit: AnswerUnit,
        spans: Sequence[SourceSpan],
    ) -> Sequence[ValidationFinding]:
        """Return typed findings."""


class Evaluator(Protocol):
    """Produce advisory model-assisted quality evidence."""

    def evaluate(self, unit: AnswerUnit, spans: Sequence[SourceSpan]) -> dict[str, float]:
        """Return named quality scores."""


class ReviewRepository(Protocol):
    """Persist review state with optimistic concurrency."""

    def save(self, unit: AnswerUnit, *, expected_revision: int) -> int:
        """Persist a state change and return its revision."""


class ReleaseSink(Protocol):
    """Publish immutable complete release snapshots."""

    def publish(self, manifest: ReleaseManifest, artifacts: dict[str, bytes]) -> None:
        """Publish artifacts with the manifest committed last."""


class EmbeddingProvider(Protocol):
    """Create embeddings for query and indexing."""

    def embed(self, texts: Sequence[str]) -> Sequence[Sequence[float]]:
        """Return one vector per input text."""


class LexicalIndex(Protocol):
    """Bounded lexical retrieval projection."""

    def query(self, text: str, *, limit: int) -> Sequence[str]:
        """Return ranked unit IDs."""


class VectorIndex(Protocol):
    """Bounded vector retrieval projection."""

    def query(self, vector: Sequence[float], *, limit: int) -> Sequence[str]:
        """Return ranked unit IDs."""


class IdentityProvider(Protocol):
    """Validate caller identity."""

    def authenticate(self, token: str) -> Principal:
        """Return a validated principal."""


class Clock(Protocol):
    """Injectable time source."""

    def now(self) -> datetime:
        """Return an aware UTC timestamp."""


class JobRepository(Protocol):
    """Durable compile-job persistence."""

    def create(self, job: CompileJob) -> CompileJob:
        """Create or return an idempotent job."""

    def get(self, job_id: str) -> CompileJob | None:
        """Return a job by ID."""


class Transaction(Protocol):
    """Explicit transaction boundary."""

    def __enter__(self) -> Transaction:
        """Begin a transaction."""

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> bool:
        """Commit on success and roll back on error."""

    def add_outbox(self, topic: str, payload: str) -> None:
        """Append an event in the active transaction."""

    def save_all(self, records: Iterable[T]) -> None:
        """Persist a related record group atomically."""
