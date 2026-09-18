"""Estate application boundary tests."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from datetime import UTC, datetime
from pathlib import Path

import pytest

from shaper.application.assessment import DocumentAssessmentService, EstateAssessmentService
from shaper.application.document_findings import BASELINE_CHECK_CODES, DOCUMENT_CHECK_CODES
from shaper.application.estates import (
    EstateArchivedError,
    EstateDiscoveryService,
    EstateInventoryService,
    EstateRecommendationService,
    EstateService,
    EstateSourceService,
    InventoryInput,
    VersionedRecord,
)
from shaper.application.orchestration import (
    AgentReadinessAgent,
    AssessmentAgent,
    GovernanceAgent,
    KnowledgeAgent,
    KnowledgeTransformationOrchestrator,
    TransformationAgent,
)
from shaper.application.ports import SourceChange
from shaper.application.token_estimation import TokenEstimator
from shaper.domain import (
    CollectionRole,
    EstateSourceKind,
    KnowledgeEstate,
    PermissionSnapshot,
    Principal,
    SharePointCredentialMode,
    SourceDocument,
    SourceRef,
)
from shaper.infrastructure.parsers import SupportedDocumentParser
from shaper.infrastructure.sqlite import ConcurrencyError, SQLiteEstateRepository, SQLiteStore

NOW = datetime(2026, 9, 10, tzinfo=UTC)


class SharePointConnector:
    """Connector fake that returns one downloaded file."""

    def changes(
        self,
        source: SourceRef,
        *,
        checkpoint: str | None,
    ) -> Iterator[SourceChange]:
        yield SourceChange(
            kind="changed",
            document=SourceDocument(
                source_id="item-1",
                source_version="a" * 64,
                content_hash="a" * 64,
                tenant_id=source.tenant_id,
                collection_id=source.collection_id,
                title="Policy.txt",
                media_type="text/plain",
                observed_at=NOW,
                permission=PermissionSnapshot(
                    permission_hash="b" * 64,
                    captured_at=NOW,
                ),
            ),
            source_id="item-1",
            checkpoint="delta-1",
            content=b"Employees receive leave.",
        )


class UnauthorizedConnector:
    """Connector fake that reports missing Graph authorization."""

    def changes(
        self,
        source: SourceRef,
        *,
        checkpoint: str | None,
    ) -> Iterator[SourceChange]:
        del source, checkpoint
        raise PermissionError("Graph consent is missing")
        yield


class FakeEstateRepository:
    """Small optimistic repository fake for service behavior."""

    def __init__(self) -> None:
        self.records: dict[str, VersionedRecord[KnowledgeEstate]] = {}

    def create_estate(self, estate: KnowledgeEstate) -> VersionedRecord[KnowledgeEstate]:
        if estate.estate_id in self.records:
            raise ValueError("Estate already exists")
        record = VersionedRecord(estate, 1)
        self.records[estate.estate_id] = record
        return record

    def get_estate(self, estate_id: str) -> VersionedRecord[KnowledgeEstate] | None:
        return self.records.get(estate_id)

    def list_estates(self, collection_id: str) -> Sequence[VersionedRecord[KnowledgeEstate]]:
        return tuple(
            record
            for record in self.records.values()
            if record.value.collection_id == collection_id
        )

    def save_estate(
        self,
        estate: KnowledgeEstate,
        *,
        expected_revision: int,
    ) -> VersionedRecord[KnowledgeEstate]:
        current = self.records[estate.estate_id]
        if expected_revision != current.revision:
            raise ConcurrencyError("Stale estate revision")
        record = VersionedRecord(estate, current.revision + 1)
        self.records[estate.estate_id] = record
        return record


def _principal(*roles: CollectionRole) -> Principal:
    return Principal(
        principal_id="person-1",
        tenant_id="tenant-1",
        collection_roles={"collection-1": frozenset(roles)},
    )


def _persistent_services(
    path: Path,
) -> tuple[SQLiteStore, EstateService, EstateSourceService, EstateInventoryService]:
    store = SQLiteStore(path)
    store.connect()
    store.migrate()
    repository = SQLiteEstateRepository(store)
    source_ids = iter(("one", "two", "three", "four", "five", "six", "seven"))
    return (
        store,
        EstateService(repository, clock=lambda: NOW, id_factory=lambda: "estate"),
        EstateSourceService(repository, clock=lambda: NOW, id_factory=lambda: next(source_ids)),
        EstateInventoryService(
            repository,
            parser=SupportedDocumentParser(),
            clock=lambda: NOW,
        ),
    )


def _discovery(store: SQLiteStore) -> EstateDiscoveryService:
    repository = SQLiteEstateRepository(store)
    return EstateDiscoveryService(
        repository,
        documents=DocumentAssessmentService(),
        orchestrator=KnowledgeTransformationOrchestrator(
            assessments=EstateAssessmentService(),
            assessment_agent=AssessmentAgent(),
            knowledge_agent=KnowledgeAgent(),
            transformation_agent=TransformationAgent(),
            governance_agent=GovernanceAgent(),
            agent_readiness_agent=AgentReadinessAgent(),
        ),
        clock=lambda: NOW,
        id_factory=lambda: "one",
    )


def _service(repository: FakeEstateRepository) -> EstateService:
    return EstateService(repository, clock=lambda: NOW, id_factory=lambda: "one")


def test_given_compile_role_when_estate_created_then_collection_boundary_is_retained() -> None:
    # Arrange
    repository = FakeEstateRepository()

    # Act
    result = _service(repository).create(
        principal=_principal(CollectionRole.COMPILE),
        collection_id="collection-1",
        name="Policy estate",
    )

    # Assert
    assert (result.value.estate_id, result.value.collection_id, result.revision) == (
        "estate-one",
        "collection-1",
        1,
    )


def test_given_stale_revision_when_estate_updated_then_conflict_is_explicit() -> None:
    # Arrange
    repository = FakeEstateRepository()
    service = _service(repository)
    estate = service.create(
        principal=_principal(CollectionRole.COMPILE),
        collection_id="collection-1",
        name="Policy estate",
    )

    # Act & Assert
    with pytest.raises(ConcurrencyError, match="Stale"):
        service.update(
            estate.value.estate_id,
            principal=_principal(CollectionRole.COMPILE),
            expected_revision=estate.revision - 1,
            name="New name",
            description="",
            artifact_name_template="shaper_{source_stem}.html",
        )


def test_given_archived_estate_when_updated_then_mutation_is_rejected() -> None:
    # Arrange
    repository = FakeEstateRepository()
    service = _service(repository)
    estate = service.create(
        principal=_principal(CollectionRole.COMPILE),
        collection_id="collection-1",
        name="Policy estate",
    )
    archived = service.archive(
        estate.value.estate_id,
        principal=_principal(CollectionRole.ADMIN),
        expected_revision=estate.revision,
    )

    # Act & Assert
    with pytest.raises(EstateArchivedError, match="archived"):
        service.update(
            archived.value.estate_id,
            principal=_principal(CollectionRole.COMPILE),
            expected_revision=archived.revision,
            name="New name",
            description="",
            artifact_name_template="shaper_{source_stem}.html",
        )


def test_given_query_role_when_estates_listed_then_other_tenant_is_not_disclosed() -> None:
    # Arrange
    repository = FakeEstateRepository()
    service = _service(repository)
    service.create(
        principal=_principal(CollectionRole.COMPILE),
        collection_id="collection-1",
        name="Policy estate",
    )
    repository.records["estate-other"] = VersionedRecord(
        KnowledgeEstate(
            estate_id="estate-other",
            collection_id="collection-1",
            tenant_id="tenant-2",
            name="Private estate",
            created_at=NOW,
            updated_at=NOW,
        ),
        1,
    )

    # Act
    result = service.list(
        "collection-1",
        principal=_principal(CollectionRole.QUERY),
    )

    # Assert
    assert [item.value.estate_id for item in result] == ["estate-one"]


def test_given_mixed_sources_when_registered_then_states_are_truthful_and_independent(
    tmp_path: Path,
) -> None:
    # Arrange
    store, estates, sources, _ = _persistent_services(tmp_path / "state.db")
    caller = _principal(CollectionRole.COMPILE, CollectionRole.QUERY)
    estate = estates.create(
        principal=caller,
        collection_id="collection-1",
        name="Policy estate",
    )
    try:
        # Act
        upload = sources.register(
            estate.value.estate_id,
            principal=caller,
            kind=EstateSourceKind.UPLOAD,
            display_name="Travel policy",
            locator="asset:one",
        )
        sharepoint = sources.register(
            estate.value.estate_id,
            principal=caller,
            kind=EstateSourceKind.SHAREPOINT,
            display_name="HR site",
            locator="https://contoso.sharepoint.com/sites/hr",
            credential_mode=SharePointCredentialMode.APPLICATION,
        )

        # Assert
        registered = sources.list(estate.value.estate_id, principal=caller)
        assert [item.value.kind for item in registered] == [
            upload.value.kind,
            sharepoint.value.kind,
        ]
        assert all(
            item.value.status.value == "pending"
            for item in sources.list(estate.value.estate_id, principal=caller)
        )
        assert (
            sharepoint.value.status_detail
            == "Registration only. SharePoint synchronization is not configured; "
            "upload files to add content."
        )
        assert sharepoint.value.credential_mode is SharePointCredentialMode.APPLICATION
        for kind, locator in (
            (EstateSourceKind.URL, "https://example.com/knowledge"),
            (EstateSourceKind.UPLOAD, "asset:invalidupload"),
            (EstateSourceKind.ZIP, "asset:invalidzip"),
        ):
            with pytest.raises(
                ValueError,
                match="Application credentials are supported only for SharePoint sources",
            ):
                sources.register(
                    estate.value.estate_id,
                    principal=caller,
                    kind=kind,
                    display_name="Invalid app-authenticated source",
                    locator=locator,
                    credential_mode=SharePointCredentialMode.APPLICATION,
                )
    finally:
        store.close()


def test_given_scanned_files_when_ingested_then_each_file_becomes_inventory(
    tmp_path: Path,
) -> None:
    # Arrange
    store, estates, sources, inventory = _persistent_services(tmp_path / "state.db")
    caller = _principal(CollectionRole.COMPILE)
    estate = estates.create(
        principal=caller,
        collection_id="collection-1",
        name="Policy estate",
    )
    source = sources.register(
        estate.value.estate_id,
        principal=caller,
        kind=EstateSourceKind.ZIP,
        display_name="Policy bundle",
        locator="asset:bundle",
    )
    try:
        # Act
        documents = inventory.ingest(
            source.value.source_id,
            (
                InventoryInput("travel.md", "text/markdown", b"# Travel\n\nBook centrally.", NOW),
                InventoryInput("leave.txt", "text/plain", b"Employees receive leave.", NOW),
            ),
            principal=caller,
        )

        # Assert
        assert {item.value.filename for item in documents} == {"travel.md", "leave.txt"}
        repository = SQLiteEstateRepository(store)
        travel = next(item.value for item in documents if item.value.filename == "travel.md")
        assert (
            repository.load_document_source(travel.document_id, travel.source_version)
            == b"# Travel\n\nBook centrally."
        )
        assert repository.load_document_content(travel.document_id, travel.source_version) == (
            "# Travel\n\nBook centrally."
        )
    finally:
        store.close()


def test_given_active_document_when_removed_then_it_is_withdrawn_and_provenance_remains(
    tmp_path: Path,
) -> None:
    # Arrange
    store, estates, sources, inventory = _persistent_services(tmp_path / "state.db")
    caller = _principal(CollectionRole.ADMIN, CollectionRole.COMPILE)
    estate = estates.create(
        principal=caller,
        collection_id="collection-1",
        name="Policy estate",
    )
    source = sources.register(
        estate.value.estate_id,
        principal=caller,
        kind=EstateSourceKind.UPLOAD,
        display_name="Policy documents",
        locator="asset:policies",
    )
    documents = inventory.ingest(
        source.value.source_id,
        (
            InventoryInput("travel.md", "text/markdown", b"Book centrally.", NOW),
            InventoryInput("leave.md", "text/markdown", b"Request leave.", NOW),
        ),
        principal=caller,
    )
    travel, leave = documents
    repository = SQLiteEstateRepository(store)
    try:
        # Act & Assert
        with pytest.raises(PermissionError):
            inventory.remove(
                estate.value.estate_id,
                travel.value.document_id,
                expected_revision=travel.revision,
                principal=_principal(CollectionRole.QUERY),
            )

        removed = inventory.remove(
            estate.value.estate_id,
            travel.value.document_id,
            expected_revision=travel.revision,
            principal=caller,
        )
        assert removed.value.deleted is True
        assert removed.revision == travel.revision + 1
        assert repository.has_document_source(
            travel.value.document_id,
            travel.value.source_version,
        )
        assert (
            inventory.remove(
                estate.value.estate_id,
                travel.value.document_id,
                expected_revision=travel.revision,
                principal=caller,
            )
            == removed
        )

        archived = estates.archive(
            estate.value.estate_id,
            principal=caller,
            expected_revision=estate.revision,
        )
        with pytest.raises(EstateArchivedError, match="archived"):
            inventory.remove(
                archived.value.estate_id,
                leave.value.document_id,
                expected_revision=leave.revision,
                principal=caller,
            )
    finally:
        store.close()


def test_given_exact_confirmation_when_purged_then_only_tombstone_remains(
    tmp_path: Path,
) -> None:
    # Arrange
    store, estates, sources, _ = _persistent_services(tmp_path / "state.db")
    caller = _principal(CollectionRole.ADMIN, CollectionRole.COMPILE)
    estate = estates.create(
        principal=caller,
        collection_id="collection-1",
        name="Policy estate",
    )
    sources.register(
        estate.value.estate_id,
        principal=caller,
        kind=EstateSourceKind.UPLOAD,
        display_name="Policy",
        locator="asset:one",
    )
    try:
        # Act
        sources.purge(
            estate.value.estate_id,
            principal=caller,
            confirmation="Policy estate",
            reason="Test cleanup",
        )

        # Assert
        assert store.load_record(
            category="purge_tombstone",
            record_id=estate.value.estate_id,
        )
        assert not store.list_records(category="knowledge_estate")
        assert not store.list_records(category="estate_source")
    finally:
        store.close()


def test_given_sharepoint_changes_when_synchronized_then_inventory_and_checkpoint_persist(
    tmp_path: Path,
) -> None:
    # Arrange
    store, estates, sources, inventory = _persistent_services(tmp_path / "state.db")
    caller = _principal(CollectionRole.COMPILE)
    estate = estates.create(
        principal=caller,
        collection_id="collection-1",
        name="Policy estate",
    )
    source = sources.register(
        estate.value.estate_id,
        principal=caller,
        kind=EstateSourceKind.SHAREPOINT,
        display_name="HR site",
        locator="https://contoso.sharepoint.com/sites/hr",
    )
    try:
        # Act
        synchronized = sources.synchronize_sharepoint(
            source.value.source_id,
            principal=caller,
            connector=SharePointConnector(),
            inventory=inventory,
        )

        # Assert
        assert (synchronized.value.status.value, synchronized.value.checkpoint) == (
            "ready",
            "delta-1",
        )
    finally:
        store.close()


def test_given_missing_graph_consent_when_synchronized_then_authorization_is_explicit(
    tmp_path: Path,
) -> None:
    # Arrange
    store, estates, sources, inventory = _persistent_services(tmp_path / "state.db")
    caller = _principal(CollectionRole.COMPILE)
    estate = estates.create(
        principal=caller,
        collection_id="collection-1",
        name="Policy estate",
    )
    source = sources.register(
        estate.value.estate_id,
        principal=caller,
        kind=EstateSourceKind.SHAREPOINT,
        display_name="HR site",
        locator="https://contoso.sharepoint.com/sites/hr",
    )
    try:
        # Act & Assert
        with pytest.raises(PermissionError, match="consent"):
            sources.synchronize_sharepoint(
                source.value.source_id,
                principal=caller,
                connector=UnauthorizedConnector(),
                inventory=inventory,
            )
        persisted = SQLiteEstateRepository(store).get_source(source.value.source_id)
        assert persisted is not None
        assert persisted.value.status.value == "authorization_required"
    finally:
        store.close()


def test_given_inventory_when_discovery_runs_then_reports_and_five_agent_evidence_persist(
    tmp_path: Path,
) -> None:
    # Arrange
    store, estates, sources, inventory = _persistent_services(tmp_path / "state.db")
    caller = _principal(CollectionRole.COMPILE, CollectionRole.QUERY)
    estate = estates.create(
        principal=caller,
        collection_id="collection-1",
        name="Policy estate",
    )
    source = sources.register(
        estate.value.estate_id,
        principal=caller,
        kind=EstateSourceKind.UPLOAD,
        display_name="Travel policy",
        locator="asset:travel",
    )
    inventory.ingest(
        source.value.source_id,
        (
            InventoryInput(
                "travel.md",
                "text/markdown",
                b"# Travel\n\nEmployees must book centrally.",
                NOW,
            ),
        ),
        principal=caller,
    )
    try:
        # Act
        run = _discovery(store).start(estate.value.estate_id, principal=caller)

        # Assert
        repository = SQLiteEstateRepository(store)
        assert run.value.status.value == "completed"
        assert len(repository.list_reports(run.value.run_id)) == 1
        analysis = repository.load_analysis(run.value.run_id)
        assert analysis is not None
        assert (
            len(
                {
                    analysis.assessment.role,
                    analysis.knowledge.role,
                    analysis.transformation.role,
                    analysis.governance.role,
                    analysis.agent_readiness.role,
                }
            )
            == 5
        )
    finally:
        store.close()


def test_given_selected_discovered_document_when_recommended_then_one_estimate_is_created(
    tmp_path: Path,
) -> None:
    # Arrange
    store, estates, sources, inventory = _persistent_services(tmp_path / "state.db")
    caller = _principal(CollectionRole.COMPILE, CollectionRole.QUERY)
    estate = estates.create(
        principal=caller,
        collection_id="collection-1",
        name="Policy estate",
    )
    source = sources.register(
        estate.value.estate_id,
        principal=caller,
        kind=EstateSourceKind.UPLOAD,
        display_name="Travel policy",
        locator="asset:travel",
    )
    documents = inventory.ingest(
        source.value.source_id,
        (
            InventoryInput(
                "travel.md",
                "text/markdown",
                b"Employees must book centrally and retain receipts.",
                NOW,
            ),
        ),
        principal=caller,
    )
    discovery = _discovery(store).start(estate.value.estate_id, principal=caller)
    recommendations = EstateRecommendationService(
        SQLiteEstateRepository(store),
        transformation_agent=TransformationAgent(),
        estimator=TokenEstimator(model_deployment="gpt-5-mini"),
        clock=lambda: NOW,
        id_factory=lambda: "one",
    )
    try:
        # Act
        run = recommendations.start(
            discovery.value.run_id,
            (documents[0].value.document_id,),
            principal=caller,
        )
        proposals = recommendations.proposals(run.value.run_id, principal=caller)

        # Assert
        assert [item.document_id for item in proposals] == [documents[0].value.document_id]
        assert proposals[0].token_estimate.enforced_maximum > 0
        assert proposals[0].expected_artifact == "shaper_travel.html"
    finally:
        store.close()


def test_given_all_selected_documents_changed_when_recommended_then_run_fails_clearly(
    tmp_path: Path,
) -> None:
    # Arrange
    store, estates, sources, inventory = _persistent_services(tmp_path / "state.db")
    caller = _principal(CollectionRole.COMPILE, CollectionRole.QUERY)
    estate = estates.create(
        principal=caller,
        collection_id="collection-1",
        name="Policy estate",
    )
    source = sources.register(
        estate.value.estate_id,
        principal=caller,
        kind=EstateSourceKind.UPLOAD,
        display_name="Travel policy",
        locator="asset:travel",
    )
    documents = inventory.ingest(
        source.value.source_id,
        (
            InventoryInput(
                "travel.md",
                "text/markdown",
                b"Employees must book centrally.",
                NOW,
            ),
        ),
        principal=caller,
    )
    discovery = _discovery(store).start(estate.value.estate_id, principal=caller)
    inventory.ingest(
        source.value.source_id,
        (
            InventoryInput(
                "travel.md",
                "text/markdown",
                b"Employees must book centrally and retain receipts.",
                NOW,
            ),
        ),
        principal=caller,
    )
    recommendations = EstateRecommendationService(
        SQLiteEstateRepository(store),
        transformation_agent=TransformationAgent(),
        estimator=TokenEstimator(model_deployment="gpt-5-mini"),
        clock=lambda: NOW,
        id_factory=lambda: "stale",
    )
    try:
        # Act
        run = recommendations.start(
            discovery.value.run_id,
            (documents[0].value.document_id,),
            principal=caller,
        )

        # Assert
        assert run.value.status.value == "failed"
        assert run.value.completed_document_ids == ()
        assert run.value.failed_document_ids == (documents[0].value.document_id,)
        assert run.value.error is not None
        assert "Run discovery again" in run.value.error
        assert recommendations.proposals(run.value.run_id, principal=caller) == ()
    finally:
        store.close()


def test_given_discovery_without_current_checks_when_recommended_then_run_requires_rediscovery(
    tmp_path: Path,
) -> None:
    store, estates, sources, inventory = _persistent_services(tmp_path / "state.db")
    caller = _principal(CollectionRole.COMPILE, CollectionRole.QUERY)
    estate = estates.create(
        principal=caller,
        collection_id="collection-1",
        name="Policy estate",
    )
    source = sources.register(
        estate.value.estate_id,
        principal=caller,
        kind=EstateSourceKind.UPLOAD,
        display_name="Travel policy",
        locator="asset:travel",
    )
    documents = inventory.ingest(
        source.value.source_id,
        (InventoryInput("travel.md", "text/markdown", b"Employees must book centrally.", NOW),),
        principal=caller,
    )
    discovery = _discovery(store).start(estate.value.estate_id, principal=caller)
    repository = SQLiteEstateRepository(store)
    report = repository.list_reports(discovery.value.run_id)[0]
    stale_report = report.model_copy(update={"checks_completed": BASELINE_CHECK_CODES})
    store.save_record(
        category="readiness_report",
        record_id=stale_report.report_id,
        payload=stale_report.model_dump_json(),
        expected_revision=1,
    )
    recommendations = EstateRecommendationService(
        repository,
        transformation_agent=TransformationAgent(),
        estimator=TokenEstimator(model_deployment="gpt-5-mini"),
        clock=lambda: NOW,
        id_factory=lambda: "stale-checks",
    )
    try:
        run = recommendations.start(
            discovery.value.run_id,
            (documents[0].value.document_id,),
            principal=caller,
        )

        assert stale_report.checks_completed != (*BASELINE_CHECK_CODES, *DOCUMENT_CHECK_CODES)
        assert run.value.status.value == "failed"
        assert run.value.failed_document_ids == (documents[0].value.document_id,)
        assert run.value.error is not None
        assert "Run discovery again" in run.value.error
        assert recommendations.proposals(run.value.run_id, principal=caller) == ()
    finally:
        store.close()


def test_given_source_exceeds_quota_when_recommended_then_run_preserves_quota_guidance(
    tmp_path: Path,
) -> None:
    # Arrange
    store, estates, sources, inventory = _persistent_services(tmp_path / "state.db")
    caller = _principal(CollectionRole.COMPILE, CollectionRole.QUERY)
    estate = estates.create(
        principal=caller,
        collection_id="collection-1",
        name="Policy estate",
    )
    source = sources.register(
        estate.value.estate_id,
        principal=caller,
        kind=EstateSourceKind.UPLOAD,
        display_name="Travel policy",
        locator="asset:travel",
    )
    documents = inventory.ingest(
        source.value.source_id,
        (
            InventoryInput(
                "travel.md",
                "text/markdown",
                b"Employees must book centrally.",
                NOW,
            ),
        ),
        principal=caller,
    )
    discovery = _discovery(store).start(estate.value.estate_id, principal=caller)
    recommendations = EstateRecommendationService(
        SQLiteEstateRepository(store),
        transformation_agent=TransformationAgent(),
        estimator=TokenEstimator(model_deployment="gpt-5-mini", platform_maximum=1),
        clock=lambda: NOW,
        id_factory=lambda: "quota",
    )
    try:
        # Act
        run = recommendations.start(
            discovery.value.run_id,
            (documents[0].value.document_id,),
            principal=caller,
        )

        # Assert
        assert run.value.status.value == "failed"
        assert run.value.completed_document_ids == ()
        assert run.value.failed_document_ids == (documents[0].value.document_id,)
        assert run.value.error is not None
        assert "narrow or split the source document" in run.value.error
        assert "Run discovery again" not in run.value.error
    finally:
        store.close()


def test_given_one_source_exceeds_quota_when_recommended_then_partial_run_is_actionable(
    tmp_path: Path,
) -> None:
    # Arrange
    store, estates, sources, inventory = _persistent_services(tmp_path / "state.db")
    caller = _principal(CollectionRole.COMPILE, CollectionRole.QUERY)
    estate = estates.create(
        principal=caller,
        collection_id="collection-1",
        name="Policy estate",
    )
    source = sources.register(
        estate.value.estate_id,
        principal=caller,
        kind=EstateSourceKind.UPLOAD,
        display_name="Travel policy",
        locator="asset:travel",
    )
    documents = inventory.ingest(
        source.value.source_id,
        (
            InventoryInput(
                "travel.md",
                "text/markdown",
                b"Employees must book centrally.",
                NOW,
            ),
            InventoryInput(
                "expenses.md",
                "text/markdown",
                ("word " * 5_000).encode(),
                NOW,
            ),
        ),
        principal=caller,
    )
    discovery = _discovery(store).start(estate.value.estate_id, principal=caller)
    recommendations = EstateRecommendationService(
        SQLiteEstateRepository(store),
        transformation_agent=TransformationAgent(),
        estimator=TokenEstimator(model_deployment="gpt-5-mini", platform_maximum=30_000),
        clock=lambda: NOW,
        id_factory=lambda: "partial-quota",
    )
    try:
        # Act
        run = recommendations.start(
            discovery.value.run_id,
            tuple(document.value.document_id for document in documents),
            principal=caller,
        )

        # Assert
        assert run.value.status.value == "partial"
        assert run.value.completed_document_ids == (documents[0].value.document_id,)
        assert run.value.failed_document_ids == (documents[1].value.document_id,)
        assert run.value.error is not None
        assert "narrow or split the source document" in run.value.error
    finally:
        store.close()
