"""Immutable contracts for knowledge-estate workflows."""

from __future__ import annotations

import re
from datetime import datetime
from enum import StrEnum
from pathlib import PurePosixPath
from typing import Self
from urllib.parse import urlparse

from pydantic import Field, field_validator, model_validator

from shaper.domain.models import (
    CollectionRole,
    DomainModel,
    Identifier,
    Sha256,
    ValidationFinding,
    canonical_hash,
)

DEFAULT_ARTIFACT_TEMPLATE = "shaper_{source_stem}.html"
_RESERVED_STEMS = {
    "aux",
    "com1",
    "com2",
    "com3",
    "com4",
    "com5",
    "com6",
    "com7",
    "com8",
    "com9",
    "con",
    "lpt1",
    "lpt2",
    "lpt3",
    "lpt4",
    "lpt5",
    "lpt6",
    "lpt7",
    "lpt8",
    "lpt9",
    "nul",
    "prn",
}
_SAFE_FILENAME = re.compile(r"[^a-zA-Z0-9._-]+")


class EstateStatus(StrEnum):
    """Lifecycle state for a user-managed estate."""

    ACTIVE = "active"
    ARCHIVED = "archived"


class EstateSourceKind(StrEnum):
    """Supported source registrations."""

    SHAREPOINT = "sharepoint"
    URL = "url"
    UPLOAD = "upload"
    ZIP = "zip"


class SharePointCredentialMode(StrEnum):
    """Identity used when synchronizing a SharePoint source."""

    DELEGATED_USER = "delegated_user"
    APPLICATION = "application"


class SourceSyncStatus(StrEnum):
    """Truthful connector state shown to users."""

    PENDING = "pending"
    SYNCING = "syncing"
    READY = "ready"
    AUTHORIZATION_REQUIRED = "authorization_required"
    FAILED = "failed"
    DELETED = "deleted"


class WorkflowKind(StrEnum):
    """Durable estate workflow kinds."""

    DISCOVER = "discover"
    RECOMMEND = "recommend"
    TRANSFORM = "transform"


class WorkflowStatus(StrEnum):
    """Recoverable workflow execution states."""

    QUEUED = "queued"
    RUNNING = "running"
    PARTIAL = "partial"
    COMPLETED = "completed"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"
    FAILED = "failed"


class EffortBand(StrEnum):
    """Human-readable effort classification."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DecisionOutcome(StrEnum):
    """Pre-transformation human decisions."""

    APPROVE = "approve"
    DECLINE = "decline"
    WITHDRAW = "withdraw"


class DecisionStatus(StrEnum):
    """Validity of a pinned transformation decision."""

    CURRENT = "current"
    STALE = "stale"
    SUPERSEDED = "superseded"


class ArtifactStatus(StrEnum):
    """Publication state for one generated artifact."""

    GENERATED = "generated"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"


def _aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Timestamp must include a timezone")
    return value


def safe_artifact_name(
    source_name: str,
    *,
    template: str = DEFAULT_ARTIFACT_TEMPLATE,
    collision_suffix: str | None = None,
) -> str:
    """Render a safe deterministic HTML artifact name."""
    if template.count("{source_stem}") != 1 or PurePosixPath(template).name != template:
        raise ValueError("Artifact template must be a filename containing one {source_stem}")
    source_stem = PurePosixPath(source_name.replace("\\", "/")).stem
    source_stem = _SAFE_FILENAME.sub("_", source_stem).strip(" ._-")
    if not source_stem or source_stem.casefold() in _RESERVED_STEMS:
        raise ValueError("Source name cannot produce a safe artifact filename")
    if collision_suffix is not None:
        suffix = _SAFE_FILENAME.sub("", collision_suffix)
        if not suffix:
            raise ValueError("Collision suffix must contain safe filename characters")
        source_stem = f"{source_stem}-{suffix}"
    filename = template.format(source_stem=source_stem)
    path = PurePosixPath(filename)
    if (
        path.name != filename
        or path.suffix.casefold() != ".html"
        or path.stem.casefold() in _RESERVED_STEMS
    ):
        raise ValueError("Artifact template must produce a safe HTML filename")
    return filename


class KnowledgeEstate(DomainModel):
    """Named aggregate of source registrations inside a collection."""

    estate_id: Identifier
    collection_id: Identifier
    tenant_id: Identifier
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    artifact_name_template: str = Field(default=DEFAULT_ARTIFACT_TEMPLATE, max_length=200)
    generate_evaluations: bool = False
    status: EstateStatus = EstateStatus.ACTIVE
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None = None

    @field_validator("created_at", "updated_at", "archived_at")
    @classmethod
    def require_aware_time(cls, value: datetime | None) -> datetime | None:
        return None if value is None else _aware(value)

    @field_validator("artifact_name_template")
    @classmethod
    def require_safe_template(cls, value: str) -> str:
        safe_artifact_name("example.docx", template=value)
        return value

    @model_validator(mode="after")
    def validate_lifecycle(self) -> Self:
        if self.updated_at < self.created_at:
            raise ValueError("Estate updated time cannot precede creation")
        if (self.status is EstateStatus.ARCHIVED) != (self.archived_at is not None):
            raise ValueError("Archived estates require archived_at and active estates forbid it")
        return self


class EstateSource(DomainModel):
    """One typed input registered with an estate."""

    source_id: Identifier
    estate_id: Identifier
    kind: EstateSourceKind
    display_name: str = Field(min_length=1, max_length=300)
    locator: str = Field(min_length=1, max_length=2048)
    credential_mode: SharePointCredentialMode = SharePointCredentialMode.DELEGATED_USER
    status: SourceSyncStatus = SourceSyncStatus.PENDING
    checkpoint: str | None = Field(default=None, max_length=4096)
    status_detail: str | None = Field(default=None, max_length=1000)
    created_at: datetime
    updated_at: datetime

    @field_validator("created_at", "updated_at")
    @classmethod
    def require_aware_time(cls, value: datetime) -> datetime:
        return _aware(value)

    @model_validator(mode="after")
    def validate_locator(self) -> Self:
        if (
            self.kind is not EstateSourceKind.SHAREPOINT
            and self.credential_mode is not SharePointCredentialMode.DELEGATED_USER
        ):
            raise ValueError("Application credentials are supported only for SharePoint sources")
        if self.kind in {EstateSourceKind.UPLOAD, EstateSourceKind.ZIP}:
            if (
                not self.locator.startswith("asset:")
                or not self.locator.removeprefix("asset:").isalnum()
            ):
                raise ValueError("Upload and ZIP sources require an opaque asset locator")
            return self
        parsed = urlparse(self.locator)
        if parsed.scheme != "https" or not parsed.hostname:
            raise ValueError("URL sources require an absolute HTTPS locator")
        if self.kind is EstateSourceKind.SHAREPOINT and (
            not parsed.hostname.casefold().endswith(".sharepoint.com")
            or not parsed.path.startswith(("/sites/", "/teams/"))
        ):
            raise ValueError("SharePoint sources require a supported site or team URL")
        return self


class EstateDocument(DomainModel):
    """Immutable discovered version of one individual source document."""

    document_id: Identifier
    estate_id: Identifier
    source_id: Identifier
    source_version: Sha256
    content_hash: Sha256
    title: str = Field(min_length=1, max_length=500)
    filename: str = Field(min_length=1, max_length=500)
    media_type: str = Field(min_length=1, max_length=200)
    content_locator: str = Field(min_length=1, max_length=2048)
    modified_at: datetime
    discovered_at: datetime
    owner: str | None = Field(default=None, max_length=200)
    metadata: dict[str, str] = Field(default_factory=dict, max_length=50)
    deleted: bool = False

    @field_validator("modified_at", "discovered_at")
    @classmethod
    def require_aware_time(cls, value: datetime) -> datetime:
        return _aware(value)

    @model_validator(mode="after")
    def validate_version(self) -> Self:
        if self.source_version != self.content_hash:
            raise ValueError("Source version must equal the content hash")
        safe_artifact_name(self.filename)
        return self


class WorkflowRun(DomainModel):
    """Durable, pollable execution record."""

    run_id: Identifier
    estate_id: Identifier
    kind: WorkflowKind
    status: WorkflowStatus
    requested_document_ids: tuple[Identifier, ...] = ()
    completed_document_ids: tuple[Identifier, ...] = ()
    failed_document_ids: tuple[Identifier, ...] = ()
    checkpoint: str | None = Field(default=None, max_length=4096)
    error: str | None = Field(default=None, max_length=2000)
    attempt: int = Field(default=1, ge=1)
    lease_owner: str | None = Field(default=None, max_length=200)
    lease_expires_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    @field_validator("created_at", "updated_at", "lease_expires_at")
    @classmethod
    def require_aware_time(cls, value: datetime | None) -> datetime | None:
        return None if value is None else _aware(value)

    @model_validator(mode="after")
    def validate_document_sets(self) -> Self:
        requested = set(self.requested_document_ids)
        completed = set(self.completed_document_ids)
        failed = set(self.failed_document_ids)
        if len(requested) != len(self.requested_document_ids):
            raise ValueError("Requested document IDs must be unique")
        if not completed.isdisjoint(failed):
            raise ValueError("Completed and failed document IDs must be disjoint")
        if requested and not completed.union(failed).issubset(requested):
            raise ValueError("Run results must belong to requested documents")
        has_lease = self.lease_owner is not None or self.lease_expires_at is not None
        if self.status is WorkflowStatus.RUNNING and not (
            self.lease_owner and self.lease_expires_at
        ):
            raise ValueError("Running workflows require a complete lease")
        if self.status is not WorkflowStatus.RUNNING and has_lease:
            raise ValueError("Only running workflows may retain a lease")
        return self


class DocumentFindingEvidence(DomainModel):
    """Bounded source evidence for one document finding."""

    quote: str = Field(min_length=1, max_length=500)
    location: str = Field(min_length=1, max_length=200)


class DocumentFinding(DomainModel):
    """Reviewable document-suitability finding with source evidence."""

    code: str = Field(min_length=1, max_length=100)
    label: str = Field(min_length=1, max_length=200)
    explanation: str = Field(min_length=1, max_length=1000)
    agent_impact: str | None = Field(default=None, min_length=1, max_length=1000)
    severity: str = Field(pattern=r"^(info|warning|high)$")
    review_required: bool = True
    evidence: tuple[DocumentFindingEvidence, ...] = Field(default=(), max_length=4)


class DocumentReadinessReport(DomainModel):
    """Per-document deterministic discovery result."""

    report_id: Sha256
    run_id: Identifier
    estate_id: Identifier
    document_id: Identifier
    source_version: Sha256
    readiness_score: float = Field(ge=0, le=100)
    evidence_coverage: float = Field(ge=0, le=100)
    effort_points: int = Field(ge=0, le=100)
    effort_band: EffortBand
    reasons: tuple[str, ...] = Field(min_length=1, max_length=50)
    finding_codes: tuple[str, ...] = Field(default=(), max_length=50)
    findings: tuple[DocumentFinding, ...] = Field(default=(), max_length=50)
    checks_completed: tuple[str, ...] = Field(default=(), max_length=50)
    agent_roles: tuple[str, ...] = Field(min_length=1, max_length=5)
    assessed_at: datetime

    @field_validator("assessed_at")
    @classmethod
    def require_aware_time(cls, value: datetime) -> datetime:
        return _aware(value)

    @model_validator(mode="after")
    def validate_identity_and_effort(self) -> Self:
        expected = canonical_hash(
            {
                "run_id": self.run_id,
                "document_id": self.document_id,
                "source_version": self.source_version,
                "readiness_score": self.readiness_score,
                "effort_points": self.effort_points,
            }
        )
        if self.report_id != expected:
            raise ValueError("Readiness report ID must match its immutable inputs")
        expected_band = (
            EffortBand.LOW
            if self.effort_points <= 30
            else EffortBand.MEDIUM
            if self.effort_points <= 65
            else EffortBand.HIGH
        )
        if self.effort_band is not expected_band:
            raise ValueError("Effort band must match effort points")
        return self


class TokenEstimate(DomainModel):
    """Immutable deterministic token estimate for one proposal."""

    estimate_id: Sha256
    model_deployment: str = Field(min_length=1, max_length=200)
    estimator_version: str = Field(min_length=1, max_length=50)
    prompt_hash: Sha256 | None = None
    input_min: int = Field(ge=0)
    input_max: int = Field(ge=0)
    output_min: int = Field(ge=0)
    output_max: int = Field(ge=0)
    expected_total: int = Field(ge=0)
    enforced_maximum: int = Field(gt=0)
    assumptions: tuple[str, ...] = Field(min_length=1, max_length=20)
    confidence: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def validate_ranges(self) -> Self:
        if self.input_min > self.input_max or self.output_min > self.output_max:
            raise ValueError("Token estimate minimums cannot exceed maximums")
        minimum_total = self.input_min + self.output_min
        maximum_total = self.input_max + self.output_max
        if not minimum_total <= self.expected_total <= maximum_total:
            raise ValueError("Expected total must fall within the estimated range")
        if self.enforced_maximum < maximum_total:
            raise ValueError("Enforced maximum cannot be lower than the estimated maximum")
        return self


class TransformationProposal(DomainModel):
    """Versioned proposed intervention for one document."""

    recommendation_id: Sha256
    recommendation_version: Sha256
    run_id: Identifier
    discovery_run_id: Identifier
    estate_id: Identifier
    document_id: Identifier
    source_version: Sha256
    report_id: Sha256
    proposed_changes: tuple[str, ...] = Field(min_length=1, max_length=20)
    rationale: str = Field(min_length=1, max_length=2000)
    risk: str = Field(min_length=1, max_length=1000)
    effort_points: int = Field(ge=0, le=100)
    evidence_ids: tuple[Identifier, ...] = Field(min_length=1, max_length=50)
    expected_artifact: str = Field(min_length=1, max_length=500)
    token_estimate: TokenEstimate
    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def require_aware_time(cls, value: datetime) -> datetime:
        return _aware(value)


class TransformationDecision(DomainModel):
    """Human decision pinned to every transformation-changing input."""

    decision_id: Identifier
    estate_id: Identifier
    document_id: Identifier
    source_version: Sha256
    recommendation_version: Sha256
    estimate_id: Sha256
    estimator_version: str = Field(min_length=1, max_length=50)
    model_deployment: str = Field(min_length=1, max_length=200)
    outcome: DecisionOutcome
    status: DecisionStatus = DecisionStatus.CURRENT
    reason: str = Field(min_length=1, max_length=1000)
    decided_by: Identifier
    decided_at: datetime

    @field_validator("decided_at")
    @classmethod
    def require_aware_time(cls, value: datetime) -> datetime:
        return _aware(value)

    def permits(self, proposal: TransformationProposal) -> bool:
        """Return whether this decision authorizes the exact proposal."""
        estimate = proposal.token_estimate
        return (
            self.status is DecisionStatus.CURRENT
            and self.outcome is DecisionOutcome.APPROVE
            and self.estate_id == proposal.estate_id
            and self.document_id == proposal.document_id
            and self.source_version == proposal.source_version
            and self.recommendation_version == proposal.recommendation_version
            and self.estimate_id == estimate.estimate_id
            and self.estimator_version == estimate.estimator_version
            and self.model_deployment == estimate.model_deployment
        )


class TokenUsage(DomainModel):
    """Actual provider usage retained separately from its estimate."""

    run_id: Identifier
    document_id: Identifier
    estimate_id: Sha256
    model_deployment: str = Field(min_length=1, max_length=200)
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    model_calls: int = Field(ge=0)
    duration_ms: int = Field(ge=0)
    expected_total: int = Field(ge=0)
    enforced_maximum: int = Field(gt=0)
    recorded_at: datetime

    @field_validator("recorded_at")
    @classmethod
    def require_aware_time(cls, value: datetime) -> datetime:
        return _aware(value)

    @property
    def total_tokens(self) -> int:
        """Return provider-reported total usage."""
        return self.input_tokens + self.output_tokens

    @property
    def variance_tokens(self) -> int:
        """Return signed difference from the retained expected estimate."""
        return self.total_tokens - self.expected_total

    @property
    def variance_percent(self) -> float | None:
        """Return signed percentage variance when the estimate was non-zero."""
        if self.expected_total == 0:
            return None
        return round(100 * self.variance_tokens / self.expected_total, 1)


class TransformationEvaluation(DomainModel):
    """Deterministic quality evaluation for one reshaped knowledge artifact."""

    evaluation_id: Sha256
    evaluator_version: str = Field(min_length=1, max_length=50)
    citation_coverage_score: int = Field(ge=0, le=100)
    structure_score: int = Field(ge=0, le=100)
    validation_score: int = Field(ge=0, le=100)
    overall_score: int = Field(ge=0, le=100)
    blocking_findings: int = Field(ge=0)
    warning_findings: int = Field(ge=0)
    passed: bool
    limitations: tuple[str, ...] = Field(min_length=1)
    evaluated_at: datetime

    @field_validator("evaluated_at")
    @classmethod
    def require_aware_time(cls, value: datetime) -> datetime:
        return _aware(value)


class KnowledgeArtifact(DomainModel):
    """Hash-verified named HTML output for one approved source version."""

    artifact_id: Sha256
    estate_id: Identifier
    document_id: Identifier
    source_version: Sha256
    unit_id: Identifier
    filename: str = Field(min_length=1, max_length=500)
    content_hash: Sha256
    content_locator: str = Field(min_length=1, max_length=2048)
    status: ArtifactStatus = ArtifactStatus.GENERATED
    approval_id: Identifier | None = None
    evaluation: TransformationEvaluation | None = Field(default=None, exclude=True)
    validation_findings: tuple[ValidationFinding, ...] = ()
    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def require_aware_time(cls, value: datetime) -> datetime:
        return _aware(value)

    @field_validator("filename")
    @classmethod
    def require_safe_filename(cls, value: str) -> str:
        if safe_artifact_name(value, template="{source_stem}.html") != value:
            raise ValueError("Artifact filename must already be normalized and safe")
        return value

    @model_validator(mode="after")
    def validate_approval(self) -> Self:
        if (self.status is ArtifactStatus.APPROVED) != (self.approval_id is not None):
            raise ValueError("Approved artifacts require an approval ID and other states forbid it")
        return self


class CollectionGrant(DomainModel):
    """Persistent mapping from an interactive identity to collection roles."""

    grant_id: Identifier
    tenant_id: Identifier
    principal_id: Identifier
    collection_id: Identifier
    roles: frozenset[CollectionRole] = Field(min_length=1)
    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def require_aware_time(cls, value: datetime) -> datetime:
        return _aware(value)


class PurgeTombstone(DomainModel):
    """Minimal non-content audit record left after a confirmed purge."""

    estate_id: Identifier
    collection_id: Identifier
    purged_by: Identifier
    purged_at: datetime
    reason: str = Field(min_length=1, max_length=500)

    @field_validator("purged_at")
    @classmethod
    def require_aware_time(cls, value: datetime) -> datetime:
        return _aware(value)
