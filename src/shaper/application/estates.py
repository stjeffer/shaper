"""Application boundaries for persistent knowledge-estate workflows."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
from io import BytesIO
from typing import Generic, Protocol, TypeVar
from uuid import uuid4

from shaper.application.assessment import DocumentAssessmentService
from shaper.application.document_findings import BASELINE_CHECK_CODES, DOCUMENT_CHECK_CODES
from shaper.application.ingestion import ingest_content
from shaper.application.orchestration import (
    KnowledgeTransformationOrchestrator,
    TransformationAgent,
)
from shaper.application.ports import DocumentParser, SourceConnector
from shaper.application.token_estimation import TokenEstimateLimitError, TokenEstimator
from shaper.domain import (
    AuthorityStatus,
    CollectionGrant,
    CollectionRole,
    DocumentReadinessReport,
    EstateDocument,
    EstateSource,
    EstateSourceKind,
    EstateStatus,
    KnowledgeArtifact,
    KnowledgeDocumentProfile,
    KnowledgeEstate,
    KnowledgeTransformationAnalysis,
    Principal,
    PurgeTombstone,
    SharePointCredentialMode,
    SourceRef,
    SourceSpan,
    SourceSyncStatus,
    TokenUsage,
    TransformationDecision,
    TransformationProposal,
    WorkflowKind,
    WorkflowRun,
    WorkflowStatus,
    safe_artifact_name,
)
from shaper.domain.models import SourceKind, canonical_hash

RecordT = TypeVar("RecordT")


@dataclass(frozen=True)
class VersionedRecord(Generic[RecordT]):
    """One immutable record and its optimistic repository revision."""

    value: RecordT
    revision: int


class EstateLifecycleRepository(Protocol):
    """Minimum persistence contract for estate lifecycle operations."""

    def create_estate(self, estate: KnowledgeEstate) -> VersionedRecord[KnowledgeEstate]:
        """Create one estate."""

    def get_estate(self, estate_id: str) -> VersionedRecord[KnowledgeEstate] | None:
        """Load one estate."""

    def list_estates(self, collection_id: str) -> Sequence[VersionedRecord[KnowledgeEstate]]:
        """List estates in an authorization boundary."""

    def save_estate(
        self,
        estate: KnowledgeEstate,
        *,
        expected_revision: int,
    ) -> VersionedRecord[KnowledgeEstate]:
        """Compare and save one estate."""


class EstateRepository(EstateLifecycleRepository, Protocol):
    """Complete persistence contract owned by the estate application layer."""

    def save_source(
        self,
        source: EstateSource,
        *,
        expected_revision: int | None = None,
    ) -> VersionedRecord[EstateSource]:
        """Create or compare and save one source."""

    def get_source(self, source_id: str) -> VersionedRecord[EstateSource] | None:
        """Load one source."""

    def list_sources(self, estate_id: str) -> Sequence[VersionedRecord[EstateSource]]:
        """List estate sources."""

    def save_document(
        self,
        document: EstateDocument,
        *,
        expected_revision: int | None = None,
    ) -> VersionedRecord[EstateDocument]:
        """Create or compare and save one immutable document version."""

    def get_document(self, document_id: str) -> VersionedRecord[EstateDocument] | None:
        """Load one document."""

    def list_documents(self, estate_id: str) -> Sequence[VersionedRecord[EstateDocument]]:
        """List estate documents."""

    def save_document_content(
        self,
        document_id: str,
        source_version: str,
        text: str,
    ) -> None:
        """Store extracted source text for deterministic analysis."""

    def load_document_content(self, document_id: str, source_version: str) -> str:
        """Load exact-version extracted text."""

    def load_document_source(self, document_id: str, source_version: str) -> bytes:
        """Load the exact immutable source bytes for a document version."""

    def has_document_source(self, document_id: str, source_version: str) -> bool:
        """Return whether exact source bytes are retained for a document version."""

    def save_inventory(
        self,
        items: Sequence[PreparedInventoryItem],
        *,
        expected_revisions: Mapping[str, int | None] | None = None,
    ) -> Sequence[VersionedRecord[EstateDocument]]:
        """Atomically save inventory rows, source bytes, and extracted text."""

    def save_run(
        self,
        run: WorkflowRun,
        *,
        expected_revision: int | None = None,
    ) -> VersionedRecord[WorkflowRun]:
        """Create or compare and save one workflow run."""

    def get_run(self, run_id: str) -> VersionedRecord[WorkflowRun] | None:
        """Load one workflow run."""

    def list_runs(self, estate_id: str) -> Sequence[VersionedRecord[WorkflowRun]]:
        """List estate workflow runs."""

    def append_report(self, report: DocumentReadinessReport) -> None:
        """Append an immutable readiness report."""

    def list_reports(self, run_id: str) -> Sequence[DocumentReadinessReport]:
        """List reports created by a discovery run."""

    def save_analysis(self, run_id: str, analysis: KnowledgeTransformationAnalysis) -> None:
        """Persist the distinct five-agent discovery evidence."""

    def load_analysis(self, run_id: str) -> KnowledgeTransformationAnalysis | None:
        """Load the discovery analysis for one run."""

    def append_proposal(self, proposal: TransformationProposal) -> None:
        """Append an immutable recommendation."""

    def get_proposal(self, recommendation_id: str) -> TransformationProposal | None:
        """Load one recommendation."""

    def list_proposals(self, run_id: str) -> Sequence[TransformationProposal]:
        """List recommendations created by a run."""

    def append_decision(self, decision: TransformationDecision) -> None:
        """Append one auditable pre-transformation decision."""

    def latest_decision(self, document_id: str) -> TransformationDecision | None:
        """Load the latest decision for a document."""

    def append_usage(self, usage: TokenUsage) -> None:
        """Append actual provider usage."""

    def list_usage(self, run_id: str) -> Sequence[TokenUsage]:
        """List provider usage for one transformation run."""

    def append_artifact(self, artifact: KnowledgeArtifact) -> None:
        """Append one immutable generated artifact manifest."""

    def get_artifact(self, artifact_id: str) -> VersionedRecord[KnowledgeArtifact] | None:
        """Load one artifact record."""

    def save_artifact(
        self,
        artifact: KnowledgeArtifact,
        *,
        expected_revision: int,
    ) -> VersionedRecord[KnowledgeArtifact]:
        """Compare and save artifact review state."""

    def save_artifact_content(self, artifact_id: str, content: bytes) -> None:
        """Persist immutable artifact bytes."""

    def load_artifact_content(self, artifact_id: str) -> bytes:
        """Load immutable artifact bytes."""

    def save_artifact_bundle(self, artifact: KnowledgeArtifact, content: bytes) -> None:
        """Atomically persist one manifest and its immutable bytes."""

    def save_shaping_checkpoint(self, run_id: str, state: str, payload: str) -> None:
        """Persist the latest safe model-loop checkpoint."""

    def list_artifacts(self, estate_id: str) -> Sequence[KnowledgeArtifact]:
        """List estate artifacts."""

    def save_grant(self, grant: CollectionGrant) -> None:
        """Create or replace one internal collection grant."""

    def grants_for(self, tenant_id: str, principal_id: str) -> Sequence[CollectionGrant]:
        """Resolve a principal's internal collection grants."""

    def purge_estate(self, estate_id: str, tombstone: PurgeTombstone) -> None:
        """Delete content-bearing records and retain only a tombstone."""


class EstateAssessmentStatus(StrEnum):
    """Current-version assessment coverage for one estate."""

    NO_DOCUMENTS = "no_documents"
    NOT_ASSESSED = "not_assessed"
    PARTIALLY_ASSESSED = "partially_assessed"
    ASSESSED = "assessed"


@dataclass(frozen=True)
class EstateAssessmentSummary:
    """Assessment coverage for current, non-deleted estate documents."""

    document_count: int
    assessed_document_count: int
    assessment_status: EstateAssessmentStatus


def summarize_estate_assessment(
    repository: EstateRepository,
    estate_id: str,
) -> EstateAssessmentSummary:
    """Summarize reports that match each document's current source version."""
    documents = tuple(
        record.value for record in repository.list_documents(estate_id) if not record.value.deleted
    )
    if not documents:
        return EstateAssessmentSummary(0, 0, EstateAssessmentStatus.NO_DOCUMENTS)

    current_versions = {document.document_id: document.source_version for document in documents}
    assessed_document_ids: set[str] = set()
    for run_record in repository.list_runs(estate_id):
        run = run_record.value
        if run.kind is not WorkflowKind.DISCOVER or run.status not in {
            WorkflowStatus.COMPLETED,
            WorkflowStatus.PARTIAL,
        }:
            continue
        for report in repository.list_reports(run.run_id):
            if current_versions.get(report.document_id) == report.source_version:
                assessed_document_ids.add(report.document_id)

    assessed_count = len(assessed_document_ids)
    if assessed_count == 0:
        assessment_status = EstateAssessmentStatus.NOT_ASSESSED
    elif assessed_count < len(documents):
        assessment_status = EstateAssessmentStatus.PARTIALLY_ASSESSED
    else:
        assessment_status = EstateAssessmentStatus.ASSESSED
    return EstateAssessmentSummary(
        document_count=len(documents),
        assessed_document_count=assessed_count,
        assessment_status=assessment_status,
    )


class EstateService:
    """Authorize and coordinate estate lifecycle transitions."""

    def __init__(
        self,
        repository: EstateLifecycleRepository,
        *,
        clock: Callable[[], datetime],
        id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._repository = repository
        self._clock = clock
        self._id_factory = id_factory or (lambda: uuid4().hex)

    def create(
        self,
        *,
        principal: Principal,
        collection_id: str,
        name: str,
        description: str = "",
        artifact_name_template: str = "shaper_{source_stem}.html",
        generate_evaluations: bool = False,
    ) -> VersionedRecord[KnowledgeEstate]:
        """Create an active estate inside an authorized collection."""
        principal.require(collection_id, CollectionRole.COMPILE)
        now = self._clock()
        return self._repository.create_estate(
            KnowledgeEstate(
                estate_id=f"estate-{self._id_factory()}",
                collection_id=collection_id,
                tenant_id=principal.tenant_id,
                name=name,
                description=description,
                artifact_name_template=artifact_name_template,
                generate_evaluations=generate_evaluations,
                created_at=now,
                updated_at=now,
            )
        )

    def get(self, estate_id: str, *, principal: Principal) -> VersionedRecord[KnowledgeEstate]:
        """Load an authorized estate."""
        record = self._require_estate(estate_id)
        self._authorize(record.value, principal, CollectionRole.QUERY)
        return record

    def list(
        self,
        collection_id: str,
        *,
        principal: Principal,
    ) -> Sequence[VersionedRecord[KnowledgeEstate]]:
        """List estates inside one authorized collection."""
        principal.require(collection_id, CollectionRole.QUERY)
        return tuple(
            item
            for item in self._repository.list_estates(collection_id)
            if item.value.tenant_id == principal.tenant_id
        )

    def update(
        self,
        estate_id: str,
        *,
        principal: Principal,
        expected_revision: int,
        name: str,
        description: str,
        artifact_name_template: str,
        generate_evaluations: bool = False,
    ) -> VersionedRecord[KnowledgeEstate]:
        """Update mutable estate settings using optimistic concurrency."""
        record = self._require_estate(estate_id)
        self._authorize(record.value, principal, CollectionRole.COMPILE)
        self.require_active(record.value)
        values = record.value.model_dump()
        values.update(
            {
                "name": name,
                "description": description,
                "artifact_name_template": artifact_name_template,
                "generate_evaluations": generate_evaluations,
                "updated_at": self._clock(),
            }
        )
        return self._repository.save_estate(
            KnowledgeEstate.model_validate(values),
            expected_revision=expected_revision,
        )

    def archive(
        self,
        estate_id: str,
        *,
        principal: Principal,
        expected_revision: int,
    ) -> VersionedRecord[KnowledgeEstate]:
        """Archive an estate while retaining read access."""
        record = self._require_estate(estate_id)
        self._authorize(record.value, principal, CollectionRole.ADMIN)
        self.require_active(record.value)
        now = self._clock()
        values = record.value.model_dump()
        values.update(
            {
                "status": EstateStatus.ARCHIVED,
                "archived_at": now,
                "updated_at": now,
            }
        )
        return self._repository.save_estate(
            KnowledgeEstate.model_validate(values),
            expected_revision=expected_revision,
        )

    @staticmethod
    def require_active(estate: KnowledgeEstate) -> None:
        """Reject mutations against archived estates."""
        if estate.status is EstateStatus.ARCHIVED:
            raise EstateArchivedError(f"Knowledge estate is archived: {estate.estate_id}")

    def _require_estate(self, estate_id: str) -> VersionedRecord[KnowledgeEstate]:
        record = self._repository.get_estate(estate_id)
        if record is None:
            raise KeyError(f"Knowledge estate does not exist: {estate_id}")
        return record

    @staticmethod
    def _authorize(
        estate: KnowledgeEstate,
        principal: Principal,
        role: CollectionRole,
    ) -> None:
        if estate.tenant_id != principal.tenant_id:
            raise PermissionError("Knowledge estate belongs to another tenant")
        principal.require(estate.collection_id, role)


class EstateArchivedError(RuntimeError):
    """Raised when a caller attempts to mutate an archived estate."""


class EstateSourceService:
    """Manage typed source registrations and destructive estate lifecycle actions."""

    def __init__(
        self,
        repository: EstateRepository,
        *,
        clock: Callable[[], datetime],
        id_factory: Callable[[], str] | None = None,
        purge_bytes: Callable[[str], None] | None = None,
    ) -> None:
        self._repository = repository
        self._clock = clock
        self._id_factory = id_factory or (lambda: uuid4().hex)
        self._purge_bytes = purge_bytes or (lambda _: None)

    def register(
        self,
        estate_id: str,
        *,
        principal: Principal,
        kind: EstateSourceKind,
        display_name: str,
        locator: str,
        credential_mode: SharePointCredentialMode = SharePointCredentialMode.DELEGATED_USER,
    ) -> VersionedRecord[EstateSource]:
        """Register a unique source without claiming it is connected."""
        estate = self._active_estate(estate_id, principal, CollectionRole.COMPILE)
        if any(
            item.value.kind is kind and item.value.locator == locator
            for item in self._repository.list_sources(estate_id)
        ):
            raise ValueError("This source is already registered with the estate")
        now = self._clock()
        status_detail = None
        if kind is EstateSourceKind.URL:
            status_detail = (
                "Registration only. URL ingestion is not configured; upload files to add content."
            )
        elif kind is EstateSourceKind.SHAREPOINT:
            status_detail = (
                "Registration only. SharePoint synchronization is not configured; "
                "upload files to add content."
            )
        return self._repository.save_source(
            EstateSource(
                source_id=f"source-{self._id_factory()}",
                estate_id=estate.value.estate_id,
                kind=kind,
                display_name=display_name,
                locator=locator,
                credential_mode=credential_mode,
                status=SourceSyncStatus.PENDING,
                status_detail=status_detail,
                created_at=now,
                updated_at=now,
            )
        )

    def list(
        self,
        estate_id: str,
        *,
        principal: Principal,
    ) -> Sequence[VersionedRecord[EstateSource]]:
        """List sources for an authorized estate."""
        self._estate(estate_id, principal, CollectionRole.QUERY)
        return self._repository.list_sources(estate_id)

    def remove(
        self,
        source_id: str,
        *,
        principal: Principal,
        expected_revision: int,
    ) -> VersionedRecord[EstateSource]:
        """Mark a source deleted without falsifying document provenance."""
        source = self._repository.get_source(source_id)
        if source is None:
            raise KeyError(f"Estate source does not exist: {source_id}")
        self._active_estate(source.value.estate_id, principal, CollectionRole.COMPILE)
        values = source.value.model_dump()
        values.update(
            {
                "status": SourceSyncStatus.DELETED,
                "status_detail": "Source registration removed by a user.",
                "updated_at": self._clock(),
            }
        )
        return self._repository.save_source(
            EstateSource.model_validate(values),
            expected_revision=expected_revision,
        )

    def synchronize_sharepoint(
        self,
        source_id: str,
        *,
        principal: Principal,
        connector: SourceConnector,
        inventory: EstateInventoryService,
    ) -> VersionedRecord[EstateSource]:
        """Synchronize one registered SharePoint source from its durable checkpoint."""
        source = self._repository.get_source(source_id)
        if source is None:
            raise KeyError(f"Estate source does not exist: {source_id}")
        if source.value.kind is not EstateSourceKind.SHAREPOINT:
            raise ValueError("Only SharePoint sources can use SharePoint synchronization")
        estate = self._active_estate(
            source.value.estate_id,
            principal,
            CollectionRole.COMPILE,
        )
        syncing = self._save_status(
            source,
            SourceSyncStatus.SYNCING,
            detail="Enumerating SharePoint changes.",
        )
        reference = SourceRef(
            tenant_id=estate.value.tenant_id,
            collection_id=estate.value.collection_id,
            kind=SourceKind.SHAREPOINT,
            locator=source.value.locator,
        )
        try:
            changes = tuple(connector.changes(reference, checkpoint=source.value.checkpoint))
            inputs = tuple(
                InventoryInput(
                    filename=change.document.title,
                    media_type=change.document.media_type,
                    content=self._required_content(change.content),
                    modified_at=change.document.observed_at,
                    logical_id=change.source_id,
                )
                for change in changes
                if change.kind == "changed" and change.document is not None
            )
            if inputs:
                inventory.ingest(source_id, inputs, principal=principal)
            for change in changes:
                if change.kind == "withdrawn":
                    inventory.withdraw(source_id, change.source_id, principal=principal)
            checkpoint = changes[-1].checkpoint if changes else source.value.checkpoint
            return self._save_status(
                syncing,
                SourceSyncStatus.READY,
                detail=f"Synchronized {len(inputs)} changed document(s).",
                checkpoint=checkpoint,
            )
        except PermissionError:
            self._save_status(
                syncing,
                SourceSyncStatus.AUTHORIZATION_REQUIRED,
                detail="Microsoft Graph application authorization is required for this source.",
            )
            raise
        except (ConnectionError, TimeoutError, ValueError):
            self._save_status(
                syncing,
                SourceSyncStatus.FAILED,
                detail="SharePoint synchronization failed; inspect the connector error.",
            )
            raise

    def purge(
        self,
        estate_id: str,
        *,
        principal: Principal,
        confirmation: str,
        reason: str,
    ) -> PurgeTombstone:
        """Purge estate content only after exact-name administrator confirmation."""
        estate = self._estate(estate_id, principal, CollectionRole.ADMIN)
        if confirmation != estate.value.name:
            raise ValueError("Purge confirmation must exactly match the estate name")
        tombstone = PurgeTombstone(
            estate_id=estate_id,
            collection_id=estate.value.collection_id,
            purged_by=principal.principal_id,
            purged_at=self._clock(),
            reason=reason,
        )
        self._purge_bytes(estate_id)
        self._repository.purge_estate(estate_id, tombstone)
        return tombstone

    def _active_estate(
        self,
        estate_id: str,
        principal: Principal,
        role: CollectionRole,
    ) -> VersionedRecord[KnowledgeEstate]:
        estate = self._estate(estate_id, principal, role)
        EstateService.require_active(estate.value)
        return estate

    def _estate(
        self,
        estate_id: str,
        principal: Principal,
        role: CollectionRole,
    ) -> VersionedRecord[KnowledgeEstate]:
        estate = self._repository.get_estate(estate_id)
        if estate is None:
            raise KeyError(f"Knowledge estate does not exist: {estate_id}")
        EstateService._authorize(estate.value, principal, role)
        return estate

    def _save_status(
        self,
        source: VersionedRecord[EstateSource],
        status: SourceSyncStatus,
        *,
        detail: str,
        checkpoint: str | None = None,
    ) -> VersionedRecord[EstateSource]:
        values = source.value.model_dump()
        values.update(
            {
                "status": status,
                "status_detail": detail,
                "checkpoint": checkpoint if checkpoint is not None else source.value.checkpoint,
                "updated_at": self._clock(),
            }
        )
        return self._repository.save_source(
            EstateSource.model_validate(values),
            expected_revision=source.revision,
        )

    @staticmethod
    def _required_content(content: bytes | None) -> bytes:
        if content is None:
            raise ValueError("SharePoint change did not include downloaded content")
        return content


def _normalized_content(spans: Sequence[SourceSpan]) -> str:
    """Preserve real heading context without adding synthetic parser locations."""
    parts: list[str] = []
    previous_headings: tuple[str, ...] = ()
    for span in spans:
        common = 0
        for previous, current in zip(previous_headings, span.heading_path, strict=False):
            if previous != current:
                break
            common += 1
        parts.extend(
            f"{'#' * (level + 1)} {heading}"
            for level, heading in enumerate(span.heading_path[common:], start=common)
        )
        parts.append(span.text)
        previous_headings = span.heading_path
    return "\n\n".join(parts)


@dataclass(frozen=True)
class InventoryInput:
    """One already-scanned file prepared for inventory creation."""

    filename: str
    media_type: str
    content: bytes
    modified_at: datetime | None = None
    owner: str | None = None
    logical_id: str | None = None


@dataclass(frozen=True)
class PreparedInventoryItem:
    """One immutable source version and its derived extracted text."""

    document: EstateDocument
    source_content: bytes
    extracted_text: str


class EstateInventoryService:
    """Preserve scanned files and extract text into immutable document versions."""

    def __init__(
        self,
        repository: EstateRepository,
        *,
        parser: DocumentParser,
        clock: Callable[[], datetime],
    ) -> None:
        self._repository = repository
        self._parser = parser
        self._clock = clock

    def ingest(
        self,
        source_id: str,
        items: Sequence[InventoryInput],
        *,
        principal: Principal,
        require_new: bool = False,
        expected_revisions: Mapping[str, int | None] | None = None,
    ) -> Sequence[VersionedRecord[EstateDocument]]:
        """Validate every file, then atomically save the complete inventory batch."""
        source = self._repository.get_source(source_id)
        if source is None:
            raise KeyError(f"Estate source does not exist: {source_id}")
        estate = self._repository.get_estate(source.value.estate_id)
        if estate is None:
            raise KeyError(f"Knowledge estate does not exist: {source.value.estate_id}")
        EstateService._authorize(estate.value, principal, CollectionRole.COMPILE)
        EstateService.require_active(estate.value)
        if source.value.status is SourceSyncStatus.DELETED:
            raise ValueError("Deleted sources cannot add inventory")
        if not items:
            raise ValueError("Inventory ingestion requires at least one file")
        prepared = [self._prepare(estate.value, source.value, item) for item in items]
        revisions = dict(expected_revisions or {})
        if require_new:
            revisions.update({item.document.document_id: None for item in prepared})
        return self._repository.save_inventory(
            prepared,
            expected_revisions=revisions or None,
        )

    def withdraw(
        self,
        source_id: str,
        logical_id: str,
        *,
        principal: Principal,
    ) -> VersionedRecord[EstateDocument] | None:
        """Mark a withdrawn connector item without deleting its provenance."""
        source = self._repository.get_source(source_id)
        if source is None:
            raise KeyError(f"Estate source does not exist: {source_id}")
        estate = self._repository.get_estate(source.value.estate_id)
        if estate is None:
            raise KeyError(f"Knowledge estate does not exist: {source.value.estate_id}")
        EstateService._authorize(estate.value, principal, CollectionRole.COMPILE)
        EstateService.require_active(estate.value)
        document = self._repository.get_document(self.document_id(source_id, logical_id))
        if document is None:
            return None
        values = document.value.model_dump()
        values["deleted"] = True
        return self._repository.save_document(
            EstateDocument.model_validate(values),
            expected_revision=document.revision,
        )

    def remove(
        self,
        estate_id: str,
        document_id: str,
        *,
        expected_revision: int,
        principal: Principal,
    ) -> VersionedRecord[EstateDocument]:
        """Remove a document from active use while retaining its provenance."""
        estate = self._repository.get_estate(estate_id)
        if estate is None:
            raise KeyError(f"Knowledge estate does not exist: {estate_id}")
        EstateService._authorize(estate.value, principal, CollectionRole.COMPILE)
        EstateService.require_active(estate.value)
        document = self._repository.get_document(document_id)
        if document is None or document.value.estate_id != estate_id:
            raise KeyError(f"Estate document does not exist: {document_id}")
        if document.value.deleted:
            return document
        return self._repository.save_document(
            document.value.model_copy(update={"deleted": True}),
            expected_revision=expected_revision,
        )

    @staticmethod
    def document_id(source_id: str, logical_id: str) -> str:
        """Return a stable document identity for one logical source item."""
        return f"doc-{canonical_hash({'source': source_id, 'path': logical_id})[:32]}"

    def _prepare(
        self,
        estate: KnowledgeEstate,
        source: EstateSource,
        item: InventoryInput,
    ) -> PreparedInventoryItem:
        logical_id = item.logical_id or item.filename
        document_id = self.document_id(source.source_id, logical_id)
        modified_at = item.modified_at or self._clock()
        ingested = ingest_content(
            source_id=document_id,
            tenant_id=estate.tenant_id,
            collection_id=estate.collection_id,
            title=item.filename,
            media_type=item.media_type,
            stream=BytesIO(item.content),
            permission_hash=canonical_hash(
                {"estate": estate.estate_id, "source": source.source_id}
            ),
            parser=self._parser,
            observed_at=modified_at,
        )
        extracted_text = _normalized_content(ingested.spans)
        document = EstateDocument(
            document_id=document_id,
            estate_id=estate.estate_id,
            source_id=source.source_id,
            source_version=ingested.document.source_version,
            content_hash=ingested.document.content_hash,
            title=item.filename,
            filename=item.filename,
            media_type=item.media_type,
            content_locator=f"repository-source:{document_id}:{ingested.document.source_version}",
            modified_at=modified_at,
            discovered_at=self._clock(),
            owner=item.owner,
        )
        return PreparedInventoryItem(
            document=document,
            source_content=item.content,
            extracted_text=extracted_text,
        )


class EstateDiscoveryService:
    """Execute durable deterministic discovery over current document versions."""

    def __init__(
        self,
        repository: EstateRepository,
        *,
        documents: DocumentAssessmentService,
        orchestrator: KnowledgeTransformationOrchestrator,
        clock: Callable[[], datetime],
        id_factory: Callable[[], str] | None = None,
        lease_duration: timedelta = timedelta(minutes=5),
    ) -> None:
        self._repository = repository
        self._documents = documents
        self._orchestrator = orchestrator
        self._clock = clock
        self._id_factory = id_factory or (lambda: uuid4().hex)
        self._lease_duration = lease_duration

    def start(
        self,
        estate_id: str,
        *,
        principal: Principal,
        worker_id: str = "inline-discovery",
    ) -> VersionedRecord[WorkflowRun]:
        """Create and execute one reconstructable discovery run."""
        estate = self._active_estate(estate_id, principal)
        inventory = tuple(
            item for item in self._repository.list_documents(estate_id) if not item.value.deleted
        )
        if not inventory:
            raise ValueError("Discovery requires at least one current document")
        if len(inventory) > 500:
            raise ValueError(
                "Discovery accepts at most 500 documents; narrow the estate source set"
            )
        now = self._clock()
        queued = self._repository.save_run(
            WorkflowRun(
                run_id=f"discover-{self._id_factory()}",
                estate_id=estate_id,
                kind=WorkflowKind.DISCOVER,
                status=WorkflowStatus.QUEUED,
                requested_document_ids=tuple(item.value.document_id for item in inventory),
                created_at=now,
                updated_at=now,
            )
        )
        running = self._lease(queued, worker_id=worker_id)
        return self._execute(running, estate.value, inventory)

    def get(
        self,
        run_id: str,
        *,
        principal: Principal,
    ) -> VersionedRecord[WorkflowRun]:
        """Load an authorized discovery run."""
        run = self._repository.get_run(run_id)
        if run is None or run.value.kind is not WorkflowKind.DISCOVER:
            raise KeyError(f"Discovery run does not exist: {run_id}")
        self._estate(run.value.estate_id, principal, CollectionRole.QUERY)
        return run

    def reports(
        self,
        run_id: str,
        *,
        principal: Principal,
    ) -> Sequence[DocumentReadinessReport]:
        """List document reports from an authorized discovery run."""
        self.get(run_id, principal=principal)
        return self._repository.list_reports(run_id)

    def recover_expired(
        self,
        run_id: str,
        *,
        principal: Principal,
        worker_id: str,
    ) -> VersionedRecord[WorkflowRun]:
        """Resume an expired running lease from persisted reports."""
        current = self.get(run_id, principal=principal)
        now = self._clock()
        if (
            current.value.status is not WorkflowStatus.RUNNING
            or current.value.lease_expires_at is None
            or current.value.lease_expires_at > now
        ):
            raise ValueError("Discovery run does not have an expired running lease")
        values = current.value.model_dump()
        values.update(
            {
                "attempt": current.value.attempt + 1,
                "lease_owner": worker_id,
                "lease_expires_at": now + self._lease_duration,
                "updated_at": now,
            }
        )
        resumed = self._repository.save_run(
            WorkflowRun.model_validate(values),
            expected_revision=current.revision,
        )
        estate = self._active_estate(current.value.estate_id, principal)
        inventory = tuple(
            item
            for item in self._repository.list_documents(current.value.estate_id)
            if item.value.document_id in current.value.requested_document_ids
        )
        return self._execute(resumed, estate.value, inventory)

    def _execute(
        self,
        running: VersionedRecord[WorkflowRun],
        estate: KnowledgeEstate,
        inventory: Sequence[VersionedRecord[EstateDocument]],
    ) -> VersionedRecord[WorkflowRun]:
        existing = {
            report.document_id: report
            for report in self._repository.list_reports(running.value.run_id)
        }
        profiles: list[KnowledgeDocumentProfile] = []
        profile_documents: list[tuple[KnowledgeDocumentProfile, EstateDocument]] = []
        completed: list[str] = []
        failed: list[str] = []
        for record in inventory:
            document = record.value
            try:
                profile = self._profile(document)
                profiles.append(profile)
                profile_documents.append((profile, document))
                completed.append(document.document_id)
            except (KeyError, ValueError):
                failed.append(document.document_id)
        for profile, document in profile_documents:
            if document.document_id not in existing:
                self._repository.append_report(
                    self._documents.report(
                        run_id=running.value.run_id,
                        estate_id=estate.estate_id,
                        source_version=document.source_version,
                        profile=profile,
                        assessed_at=self._clock(),
                        peers=tuple(
                            peer for peer in profiles if peer.document_id != profile.document_id
                        ),
                    )
                )
        analysis: KnowledgeTransformationAnalysis | None = None
        if profiles:
            analysis = self._orchestrator.analyze(
                collection_id=estate.collection_id,
                profiles=profiles,
                assessed_at=self._clock(),
            )
            self._repository.save_analysis(running.value.run_id, analysis)
        status = (
            WorkflowStatus.FAILED
            if not profiles
            else WorkflowStatus.PARTIAL
            if failed
            else WorkflowStatus.COMPLETED
        )
        values = running.value.model_dump()
        values.update(
            {
                "status": status,
                "completed_document_ids": tuple(completed),
                "failed_document_ids": tuple(failed),
                "checkpoint": None if analysis is None else analysis.analysis_id,
                "error": "No documents could be assessed." if not profiles else None,
                "lease_owner": None,
                "lease_expires_at": None,
                "updated_at": self._clock(),
            }
        )
        return self._repository.save_run(
            WorkflowRun.model_validate(values),
            expected_revision=running.revision,
        )

    def _profile(self, document: EstateDocument) -> KnowledgeDocumentProfile:
        text = self._repository.load_document_content(
            document.document_id,
            document.source_version,
        )
        return KnowledgeDocumentProfile(
            document_id=document.document_id,
            title=document.title,
            text=text,
            modified_at=document.modified_at,
            owner=document.owner,
            metadata=document.metadata,
            topic=document.metadata.get("topic"),
            authority=AuthorityStatus.UNKNOWN,
        )

    def _lease(
        self,
        queued: VersionedRecord[WorkflowRun],
        *,
        worker_id: str,
    ) -> VersionedRecord[WorkflowRun]:
        now = self._clock()
        values = queued.value.model_dump()
        values.update(
            {
                "status": WorkflowStatus.RUNNING,
                "lease_owner": worker_id,
                "lease_expires_at": now + self._lease_duration,
                "updated_at": now,
            }
        )
        return self._repository.save_run(
            WorkflowRun.model_validate(values),
            expected_revision=queued.revision,
        )

    def _active_estate(
        self,
        estate_id: str,
        principal: Principal,
    ) -> VersionedRecord[KnowledgeEstate]:
        estate = self._estate(estate_id, principal, CollectionRole.COMPILE)
        EstateService.require_active(estate.value)
        return estate

    def _estate(
        self,
        estate_id: str,
        principal: Principal,
        role: CollectionRole,
    ) -> VersionedRecord[KnowledgeEstate]:
        estate = self._repository.get_estate(estate_id)
        if estate is None:
            raise KeyError(f"Knowledge estate does not exist: {estate_id}")
        EstateService._authorize(estate.value, principal, role)
        return estate


class EstateRecommendationService:
    """Create detailed selection-scoped proposals without model execution."""

    def __init__(
        self,
        repository: EstateRepository,
        *,
        transformation_agent: TransformationAgent,
        estimator: TokenEstimator,
        clock: Callable[[], datetime],
        id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._repository = repository
        self._transformation_agent = transformation_agent
        self._estimator = estimator
        self._clock = clock
        self._id_factory = id_factory or (lambda: uuid4().hex)

    def start(
        self,
        discovery_run_id: str,
        document_ids: Sequence[str],
        *,
        principal: Principal,
    ) -> VersionedRecord[WorkflowRun]:
        """Create one proposal per valid selected document."""
        discovery = self._repository.get_run(discovery_run_id)
        if (
            discovery is None
            or discovery.value.kind is not WorkflowKind.DISCOVER
            or discovery.value.status not in {WorkflowStatus.COMPLETED, WorkflowStatus.PARTIAL}
        ):
            raise ValueError("Recommendations require a completed discovery run")
        estate = self._repository.get_estate(discovery.value.estate_id)
        if estate is None:
            raise KeyError(f"Knowledge estate does not exist: {discovery.value.estate_id}")
        EstateService._authorize(estate.value, principal, CollectionRole.COMPILE)
        EstateService.require_active(estate.value)
        selected = tuple(document_ids)
        if not selected or len(selected) > 100:
            raise ValueError("Recommendation runs require between 1 and 100 documents")
        if len(selected) != len(set(selected)):
            raise ValueError("Recommendation document selections must be unique")
        now = self._clock()
        queued = self._repository.save_run(
            WorkflowRun(
                run_id=f"recommend-{self._id_factory()}",
                estate_id=estate.value.estate_id,
                kind=WorkflowKind.RECOMMEND,
                status=WorkflowStatus.QUEUED,
                requested_document_ids=selected,
                created_at=now,
                updated_at=now,
            )
        )
        running = self._running(queued)
        reports = {
            report.document_id: report for report in self._repository.list_reports(discovery_run_id)
        }
        completed = []
        failed = []
        quota_failures = []
        evidence_failures = []
        output_names: set[str] = set()
        for document_id in selected:
            try:
                document_record = self._repository.get_document(document_id)
                report = reports.get(document_id)
                if document_record is None or report is None:
                    raise ValueError("Selected document is absent from discovery evidence")
                document = document_record.value
                if document.deleted or report.source_version != document.source_version:
                    raise ValueError(
                        "Selected document is withdrawn or has changed since discovery"
                    )
                if report.checks_completed != (*BASELINE_CHECK_CODES, *DOCUMENT_CHECK_CODES):
                    raise ValueError(
                        "Discovery report is stale; run discovery again before requesting "
                        "recommendations"
                    )
                changes = self._transformation_agent.recommend(report)
                text = self._repository.load_document_content(
                    document.document_id,
                    document.source_version,
                )
                estimate = self._estimator.estimate(
                    text,
                    changes,
                    assessment_findings=report.findings,
                )
                output_name = safe_artifact_name(
                    document.filename,
                    template=estate.value.artifact_name_template,
                )
                if output_name.casefold() in output_names:
                    output_name = safe_artifact_name(
                        document.filename,
                        template=estate.value.artifact_name_template,
                        collision_suffix=document.document_id[-8:],
                    )
                output_names.add(output_name.casefold())
                version_inputs = {
                    "document_id": document.document_id,
                    "source_version": document.source_version,
                    "report_id": report.report_id,
                    "changes": changes,
                    "estimate_id": estimate.estimate_id,
                    "expected_artifact": output_name,
                }
                recommendation_version = canonical_hash(version_inputs)
                self._repository.append_proposal(
                    TransformationProposal(
                        recommendation_id=canonical_hash(
                            {
                                "run_id": running.value.run_id,
                                "document_id": document.document_id,
                            }
                        ),
                        recommendation_version=recommendation_version,
                        run_id=running.value.run_id,
                        discovery_run_id=discovery_run_id,
                        estate_id=estate.value.estate_id,
                        document_id=document.document_id,
                        source_version=document.source_version,
                        report_id=report.report_id,
                        proposed_changes=changes,
                        rationale=(
                            f"Discovery found {len(report.findings)} content "
                            f"{'finding' if len(report.findings) == 1 else 'findings'} "
                            "that may affect agent responses."
                        ),
                        risk=(
                            "Generated content must remain grounded in this exact source version "
                            "and requires separate output review."
                        ),
                        effort_points=report.effort_points,
                        evidence_ids=(report.report_id,),
                        expected_artifact=output_name,
                        token_estimate=estimate,
                        created_at=self._clock(),
                    )
                )
                completed.append(document_id)
            except TokenEstimateLimitError as quota_error:
                failed.append(document_id)
                quota_failures.append(str(quota_error))
            except (KeyError, ValueError):
                failed.append(document_id)
                evidence_failures.append(document_id)
        values = running.value.model_dump()
        if failed and not completed:
            status = WorkflowStatus.FAILED
            if quota_failures and not evidence_failures:
                error = f"No improvement plans were created. {quota_failures[0]}."
            elif evidence_failures and not quota_failures:
                error = (
                    "No improvement plans were created because every selected document "
                    "was absent from the discovery evidence or changed after discovery. "
                    "Run discovery again, then reselect the documents."
                )
            else:
                error = (
                    "No improvement plans were created. Some documents changed after "
                    "discovery, and others exceed the transformation quota. Run discovery "
                    "again and narrow or split oversized sources."
                )
        elif failed:
            status = WorkflowStatus.PARTIAL
            reasons = []
            if evidence_failures:
                reasons.append("the source changed or its discovery evidence was unavailable")
            if quota_failures:
                reasons.append(quota_failures[0].removesuffix("."))
            error = (
                f"{len(failed)} selected document"
                f"{' was' if len(failed) == 1 else 's were'} skipped: "
                f"{'; '.join(reasons)}."
            )
        else:
            status = WorkflowStatus.COMPLETED
            error = None
        values.update(
            {
                "status": status,
                "completed_document_ids": tuple(completed),
                "failed_document_ids": tuple(failed),
                "error": error,
                "lease_owner": None,
                "lease_expires_at": None,
                "updated_at": self._clock(),
            }
        )
        return self._repository.save_run(
            WorkflowRun.model_validate(values),
            expected_revision=running.revision,
        )

    def proposals(
        self,
        run_id: str,
        *,
        principal: Principal,
    ) -> Sequence[TransformationProposal]:
        """List authorized proposals created by a recommendation run."""
        run = self._repository.get_run(run_id)
        if run is None or run.value.kind is not WorkflowKind.RECOMMEND:
            raise KeyError(f"Recommendation run does not exist: {run_id}")
        estate = self._repository.get_estate(run.value.estate_id)
        if estate is None:
            raise KeyError(f"Knowledge estate does not exist: {run.value.estate_id}")
        EstateService._authorize(estate.value, principal, CollectionRole.QUERY)
        return self._repository.list_proposals(run_id)

    def _running(
        self,
        queued: VersionedRecord[WorkflowRun],
    ) -> VersionedRecord[WorkflowRun]:
        now = self._clock()
        values = queued.value.model_dump()
        values.update(
            {
                "status": WorkflowStatus.RUNNING,
                "lease_owner": "inline-recommendation",
                "lease_expires_at": now + timedelta(minutes=5),
                "updated_at": now,
            }
        )
        return self._repository.save_run(
            WorkflowRun.model_validate(values),
            expected_revision=queued.revision,
        )
