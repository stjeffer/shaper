"""Immutable models and invariants for the knowledge lifecycle."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import PurePosixPath
from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)
from pydantic_core import to_jsonable_python

SCHEMA_VERSION = "1.0"
Identifier = Annotated[str, StringConstraints(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._:-]{0,127}$")]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[a-f0-9]{64}$")]


def utc_now() -> datetime:
    """Return the current UTC time."""
    return datetime.now(UTC)


def canonical_hash(value: Any) -> str:
    """Hash a JSON-compatible value using canonical serialization."""
    payload = json.dumps(
        to_jsonable_python(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


class DomainModel(BaseModel):
    """Base for immutable, strict domain contracts."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class SourceKind(StrEnum):
    """Supported source connector kinds."""

    SHAREPOINT = "sharepoint"
    UPLOAD = "upload"


class OutputKind(StrEnum):
    """Supported release sink kinds."""

    FILESYSTEM = "filesystem"
    SHAREPOINT = "sharepoint"


class UnitState(StrEnum):
    """Evidence-unit lifecycle states."""

    CANDIDATE = "candidate"
    QUARANTINED = "quarantined"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    WITHDRAWN = "withdrawn"


class JobState(StrEnum):
    """Compile-job lifecycle states."""

    QUEUED = "queued"
    RUNNING = "running"
    AWAITING_REVIEW = "awaiting_review"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"
    FAILED = "failed"
    COMPLETED = "completed"
    COMPLETED_NOT_CURRENT = "completed_not_current"


class CollectionRole(StrEnum):
    """Collection-scoped authorization roles."""

    QUERY = "query"
    COMPILE = "compile"
    REVIEW = "review"
    ADMIN = "admin"


class FindingSeverity(StrEnum):
    """Validation finding severity."""

    INFO = "info"
    WARNING = "warning"
    BLOCKING = "blocking"


class ReviewOutcome(StrEnum):
    """Human review outcomes."""

    APPROVE = "approve"
    REJECT = "reject"
    SUPERSEDE = "supersede"
    WITHDRAW = "withdraw"


class SourceRef(DomainModel):
    """Caller-supplied reference to a source collection or staged asset."""

    tenant_id: Identifier
    collection_id: Identifier
    kind: SourceKind
    locator: str = Field(min_length=1, max_length=2048)


class OutputRef(DomainModel):
    """Validated reference to a configured release destination."""

    kind: OutputKind
    root_id: Identifier
    relative_path: str = Field(default="", max_length=512)

    @field_validator("relative_path")
    @classmethod
    def validate_relative_path(cls, value: str) -> str:
        path = PurePosixPath(value)
        if path.is_absolute() or ".." in path.parts or "\\" in value:
            raise ValueError("Output path must be a safe POSIX-relative path")
        return value


class Tenant(DomainModel):
    """Tenant authorization boundary."""

    tenant_id: Identifier
    display_name: str = Field(min_length=1, max_length=200)


class Collection(DomainModel):
    """Permission-homogeneous source and output boundary."""

    collection_id: Identifier
    tenant_id: Identifier
    display_name: str = Field(min_length=1, max_length=200)
    source: SourceRef
    output: OutputRef

    @model_validator(mode="after")
    def validate_boundary(self) -> Collection:
        if self.source.tenant_id != self.tenant_id:
            raise ValueError("Collection and source tenant IDs must match")
        if self.source.collection_id != self.collection_id:
            raise ValueError("Collection and source collection IDs must match")
        return self


class Principal(DomainModel):
    """OIDC-derived principal and its explicit collection roles."""

    principal_id: Identifier
    tenant_id: Identifier
    collection_roles: dict[Identifier, frozenset[CollectionRole]] = Field(default_factory=dict)

    def require(self, collection_id: str, role: CollectionRole) -> None:
        """Raise when the principal lacks a required collection role."""
        roles = self.collection_roles.get(collection_id, frozenset())
        if role not in roles and CollectionRole.ADMIN not in roles:
            raise PermissionError(
                f"Principal {self.principal_id!r} lacks {role.value!r} on "
                f"collection {collection_id!r}"
            )


class PermissionSnapshot(DomainModel):
    """Hash-pinned permission state used for carry-forward decisions."""

    permission_hash: Sha256
    captured_at: datetime
    homogeneous: Literal[True] = True

    @field_validator("captured_at")
    @classmethod
    def require_aware_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Timestamp must include a timezone")
        return value


class SourceDocument(DomainModel):
    """Immutable source version normalized across connectors."""

    schema_version: Literal["1.0"] = "1.0"
    source_id: Identifier
    source_version: Sha256
    content_hash: Sha256
    tenant_id: Identifier
    collection_id: Identifier
    title: str = Field(min_length=1, max_length=500)
    media_type: str = Field(min_length=1, max_length=200)
    observed_at: datetime
    permission: PermissionSnapshot

    @field_validator("observed_at")
    @classmethod
    def require_aware_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Timestamp must include a timezone")
        return value

    @model_validator(mode="after")
    def validate_hashes(self) -> SourceDocument:
        if self.source_version != self.content_hash:
            raise ValueError("Source version must equal the semantic content hash")
        return self


class SourceSpan(DomainModel):
    """Ordered, addressable source evidence."""

    span_id: Identifier
    source_id: Identifier
    source_version: Sha256
    ordinal: int = Field(ge=0)
    text: str = Field(min_length=1)
    text_hash: Sha256
    heading_path: tuple[str, ...] = ()
    location: dict[str, int | str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_text_hash(self) -> SourceSpan:
        if hashlib.sha256(self.text.encode()).hexdigest() != self.text_hash:
            raise ValueError("Span text hash does not match text")
        return self


class Applicability(DomainModel):
    """Audience, jurisdiction, and temporal applicability."""

    audiences: tuple[str, ...] = ()
    jurisdictions: tuple[str, ...] = ()
    effective_from: datetime | None = None
    effective_until: datetime | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> Applicability:
        for value in (self.effective_from, self.effective_until):
            if value is not None and (value.tzinfo is None or value.utcoffset() is None):
                raise ValueError("Applicability timestamps must include a timezone")
        if (
            self.effective_from is not None
            and self.effective_until is not None
            and self.effective_until <= self.effective_from
        ):
            raise ValueError("Applicability end must be after its start")
        return self


class Claim(DomainModel):
    """Answer claim grounded in one or more exact source spans."""

    text: str = Field(min_length=1)
    span_ids: tuple[Identifier, ...] = Field(min_length=1)
    qualifiers: tuple[str, ...] = ()


class Derivation(DomainModel):
    """Pinned agent and prompt provenance."""

    run_id: Identifier
    model: str = Field(min_length=1)
    prompt_version: str = Field(min_length=1)
    parameters_hash: Sha256


class AnswerUnit(DomainModel):
    """Versioned answer-ready derivative with complete grounding."""

    schema_version: Literal["1.0"] = "1.0"
    unit_id: Identifier
    unit_version: Sha256
    source_id: Identifier
    source_version: Sha256
    canonical_questions: tuple[str, ...] = Field(min_length=1)
    answer: str = Field(min_length=1)
    claims: tuple[Claim, ...] = Field(min_length=1)
    applicability: Applicability = Field(default_factory=Applicability)
    derivation: Derivation
    state: UnitState = UnitState.CANDIDATE
    confidence: float = Field(ge=0, le=1)
    conflict_unit_ids: tuple[Identifier, ...] = ()

    def version_payload(self) -> dict[str, Any]:
        """Return fields that define semantic unit version identity."""
        return self.model_dump(
            mode="json",
            exclude={"unit_version", "state"},
        )

    @model_validator(mode="after")
    def validate_identity(self) -> AnswerUnit:
        expected_id = canonical_hash(
            {
                "source_id": self.source_id,
                "questions": sorted(self.canonical_questions),
            }
        )[:32]
        if self.unit_id != expected_id:
            raise ValueError("Unit ID does not match its stable derivation key")
        expected_version = canonical_hash(self.version_payload())
        if self.unit_version != expected_version:
            raise ValueError("Unit version does not match canonical unit content")
        return self

    @classmethod
    def create(
        cls,
        *,
        source_id: str,
        source_version: str,
        canonical_questions: tuple[str, ...],
        answer: str,
        claims: tuple[Claim, ...],
        derivation: Derivation,
        confidence: float,
        applicability: Applicability | None = None,
    ) -> AnswerUnit:
        """Create an answer unit with deterministic identity and version."""
        unit_id = canonical_hash(
            {"source_id": source_id, "questions": sorted(canonical_questions)}
        )[:32]
        values: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "unit_id": unit_id,
            "source_id": source_id,
            "source_version": source_version,
            "canonical_questions": canonical_questions,
            "answer": answer,
            "claims": claims,
            "applicability": applicability or Applicability(),
            "derivation": derivation,
            "state": UnitState.CANDIDATE,
            "confidence": confidence,
            "conflict_unit_ids": (),
        }
        values["unit_version"] = canonical_hash(
            {key: value for key, value in values.items() if key not in {"unit_version", "state"}}
        )
        return cls.model_validate(values)


class AgentRun(DomainModel):
    """Reconstructable bounded shaping run."""

    run_id: Identifier
    job_id: Identifier
    source_id: Identifier
    model: str
    prompt_version: str
    input_hash: Sha256
    started_at: datetime
    completed_at: datetime | None = None
    tool_calls: int = Field(default=0, ge=0)
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    estimated_cost: float = Field(default=0, ge=0)
    abstained: bool = False


class ValidationFinding(DomainModel):
    """Independent validation evidence."""

    rule_id: Identifier
    severity: FindingSeverity
    subject_id: Identifier
    message: str = Field(min_length=1)
    evidence_span_ids: tuple[Identifier, ...] = ()
    remedy: str | None = None


class ReviewDecision(DomainModel):
    """Immutable human review decision."""

    decision_id: Identifier
    unit_id: Identifier
    unit_version: Sha256
    outcome: ReviewOutcome
    actor: Principal
    reason: str = Field(min_length=1)
    expected_revision: int = Field(ge=0)
    decided_at: datetime


class CompileJob(DomainModel):
    """Durable, idempotent compile job."""

    job_id: Identifier
    tenant_id: Identifier
    collection_id: Identifier
    idempotency_key: Identifier
    submitted_by: Identifier
    requested_token_budget: int = Field(gt=0)
    source: SourceRef
    output: OutputRef
    state: JobState = JobState.QUEUED
    revision: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    diagnostic: str | None = None


class ReleaseUnitRef(DomainModel):
    """Unit entry in a complete active-corpus release."""

    unit_id: Identifier
    unit_version: Sha256
    source_id: Identifier
    source_version: Sha256
    permission_hash: Sha256
    approval_id: Identifier
    origin_run_id: Identifier
    artifact_hash: Sha256


class ReleaseManifest(DomainModel):
    """Integrity-checkable immutable release snapshot."""

    schema_version: Literal["1.0"] = "1.0"
    release_id: Identifier
    tenant_id: Identifier
    collection_id: Identifier
    created_at: datetime
    run_id: Identifier
    units: tuple[ReleaseUnitRef, ...]
    artifact_hashes: dict[str, Sha256]
    previous_release_id: Identifier | None = None

    @model_validator(mode="after")
    def require_unique_units(self) -> ReleaseManifest:
        unit_ids = [unit.unit_id for unit in self.units]
        if len(unit_ids) != len(set(unit_ids)):
            raise ValueError("Release manifest contains duplicate unit IDs")
        return self
