"""FastAPI adapter for jobs, query, explanation, and health."""

from __future__ import annotations

import hashlib
import json
import logging
from collections.abc import Callable, Iterator, Mapping
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from queue import Empty, Queue
from threading import Event, Thread
from urllib.parse import quote

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    Response,
    StreamingResponse,
)
from fastapi.staticfiles import StaticFiles
from jwt import PyJWTError
from pydantic import BaseModel, ConfigDict, Field

from shaper.application.artifacts import EstateTransformationService
from shaper.application.assessment import EstateAssessmentService
from shaper.application.compiler import CompilationService
from shaper.application.decisions import (
    DecisionConflictError,
    StaleProposalError,
    TransformationDecisionService,
)
from shaper.application.demo import DemoAnalysisResult, DemoAnalysisService
from shaper.application.document_findings import ASSESSMENT_CHECKS
from shaper.application.estates import (
    EstateArchivedError,
    EstateDiscoveryService,
    EstateInventoryService,
    EstateRecommendationService,
    EstateRepository,
    EstateService,
    EstateSourceService,
    InventoryInput,
    VersionedRecord,
    summarize_estate_assessment,
)
from shaper.application.jobs import (
    CompileJobService,
    JobConflictError,
    QuotaExceededError,
)
from shaper.application.orchestration import KnowledgeTransformationOrchestrator
from shaper.application.ports import MalwareScanner
from shaper.application.query import QueryGateway
from shaper.application.regression import (
    ImprovementReport,
    PairedCaseOutcome,
    compare_paired_answer_pass_rates,
)
from shaper.application.review import ReviewConflictError
from shaper.domain import (
    CollectionRole,
    CompileJob,
    DecisionOutcome,
    EstateAssessment,
    EstateDocument,
    EstateSourceKind,
    KnowledgeDocumentProfile,
    KnowledgeTransformationAnalysis,
    OutputRef,
    Principal,
    SharePointCredentialMode,
    SourceRef,
)
from shaper.infrastructure.archive import ZipArchiveExpander
from shaper.infrastructure.sqlite import ConcurrencyError
from shaper.infrastructure.uploads import (
    FileUploadStore,
    ScannerUnavailableError,
    UploadRejectedError,
)
from shaper.interfaces.auth import Authenticator, RequestPrincipalResolver

LOGGER = logging.getLogger(__name__)


class CompileRequest(BaseModel):
    """HTTP compile submission."""

    model_config = ConfigDict(extra="forbid")

    source: dict[str, object]
    output: dict[str, object]
    idempotency_key: str = Field(min_length=1, max_length=128)
    model_token_budget: int = Field(gt=0)


class QueryRequest(BaseModel):
    """HTTP query request."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=4000)
    limit: int = Field(default=10, ge=1, le=50)


class ApprovalRequest(BaseModel):
    """Human approval for one compiled candidate."""

    model_config = ConfigDict(extra="forbid")

    reason: str = Field(min_length=1, max_length=2000)
    expected_revision: int = Field(ge=1)


class AssessmentRequest(BaseModel):
    """Bounded read-only estate assessment request."""

    model_config = ConfigDict(extra="forbid")

    collection_id: str = Field(min_length=1, max_length=128)
    assessed_at: datetime
    profiles: tuple[dict[str, object], ...] = Field(min_length=1, max_length=500)


class ImprovementRequest(BaseModel):
    """Paired baseline and shaped evaluation request."""

    model_config = ConfigDict(extra="forbid")

    collection_id: str = Field(min_length=1, max_length=128)
    outcomes: tuple[PairedCaseOutcome, ...] = Field(min_length=1, max_length=500)
    dataset_reviewed: bool = False
    confidence_level: float = Field(default=0.95, gt=0.5, lt=1)


class EstateCreateRequest(BaseModel):
    """Create a named knowledge estate."""

    model_config = ConfigDict(extra="forbid")

    collection_id: str = Field(min_length=1, max_length=128)
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    artifact_name_template: str = Field(
        default="shaper_{source_stem}.html",
        max_length=200,
    )
    generate_evaluations: bool = False


class EstateUpdateRequest(BaseModel):
    """Update estate display and artifact settings."""

    model_config = ConfigDict(extra="forbid")

    expected_revision: int = Field(ge=1)
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    artifact_name_template: str = Field(max_length=200)
    generate_evaluations: bool


class SourceCreateRequest(BaseModel):
    """Register a typed estate source."""

    model_config = ConfigDict(extra="forbid")

    kind: EstateSourceKind
    display_name: str = Field(min_length=1, max_length=300)
    locator: str = Field(min_length=1, max_length=2048)
    credential_mode: SharePointCredentialMode = SharePointCredentialMode.DELEGATED_USER


class SelectionRequest(BaseModel):
    """Select identifiers for a bounded workflow run."""

    model_config = ConfigDict(extra="forbid")

    ids: tuple[str, ...] = Field(min_length=1, max_length=100)


class RecommendationRequest(SelectionRequest):
    """Select discovered documents for recommendation."""

    discovery_run_id: str = Field(min_length=1, max_length=128)


class DecisionRequest(BaseModel):
    """Record one pre-transformation decision."""

    model_config = ConfigDict(extra="forbid")

    outcome: DecisionOutcome
    reason: str = Field(min_length=1, max_length=1000)
    expected_current_decision_id: str | None = Field(default=None, max_length=128)


class ArtifactApprovalRequest(BaseModel):
    """Approve one generated artifact after output review."""

    model_config = ConfigDict(extra="forbid")

    reason: str = Field(min_length=1, max_length=1000)
    expected_review_revision: int = Field(ge=1)
    expected_artifact_revision: int = Field(ge=1)


class PurgeRequest(BaseModel):
    """Confirm destructive estate purge."""

    model_config = ConfigDict(extra="forbid")

    confirmation: str = Field(min_length=1, max_length=200)
    reason: str = Field(min_length=1, max_length=500)


class ArchiveRequest(BaseModel):
    """Archive an estate using optimistic concurrency."""

    model_config = ConfigDict(extra="forbid")

    expected_revision: int = Field(ge=1)


@dataclass(frozen=True)
class HttpServices:
    """Application services exposed through HTTP."""

    jobs: CompileJobService
    authenticator: Authenticator
    query: QueryGateway | None = None
    uploads: FileUploadStore | None = None
    compilation: CompilationService | None = None
    assessments: EstateAssessmentService | None = None
    orchestrator: KnowledgeTransformationOrchestrator | None = None
    demo_analysis: DemoAnalysisService | None = None
    readiness: Callable[[], Mapping[str, bool]] | None = None
    concept_root: Path | None = None
    principal_resolver: RequestPrincipalResolver | None = None
    estates: EstateService | None = None
    estate_sources: EstateSourceService | None = None
    estate_inventory: EstateInventoryService | None = None
    discovery: EstateDiscoveryService | None = None
    recommendations: EstateRecommendationService | None = None
    decisions: TransformationDecisionService | None = None
    transformations: EstateTransformationService | None = None
    estate_repository: EstateRepository | None = None
    archive_expander: ZipArchiveExpander | None = None
    malware_scanner: MalwareScanner | None = None
    max_upload_bytes: int = 25 * 1024 * 1024


def create_app(services: HttpServices) -> FastAPI:
    """Create the HTTP service without global mutable dependencies."""
    app = FastAPI(title="Shaper", version="0.1.0")

    @app.exception_handler(KeyError)
    async def key_error_handler(_request: object, error: KeyError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(error)})

    @app.exception_handler(PermissionError)
    async def permission_error_handler(
        _request: object,
        error: PermissionError,
    ) -> JSONResponse:
        return JSONResponse(status_code=403, content={"detail": str(error)})

    @app.exception_handler(ValueError)
    async def value_error_handler(_request: object, error: ValueError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(error)})

    async def conflict_handler(_request: object, error: Exception) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(error)})

    for conflict_type in (
        ConcurrencyError,
        DecisionConflictError,
        ReviewConflictError,
        StaleProposalError,
        EstateArchivedError,
    ):
        app.add_exception_handler(conflict_type, conflict_handler)

    @app.exception_handler(UploadRejectedError)
    async def upload_rejected_handler(
        _request: object,
        error: UploadRejectedError,
    ) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(error)})

    @app.exception_handler(ScannerUnavailableError)
    async def scanner_unavailable_handler(
        _request: object,
        error: ScannerUnavailableError,
    ) -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": str(error)})

    def _bearer_principal(authorization: str = Header()) -> Principal:
        prefix = "Bearer "
        if not authorization.startswith(prefix):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header must use Bearer authentication",
            )
        try:
            return services.authenticator.authenticate(authorization.removeprefix(prefix))
        except (PermissionError, PyJWTError) as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Bearer token is invalid",
            ) from error

    def principal(
        authorization: str | None = Header(default=None),
        ingress_principal: str | None = Header(
            default=None,
            alias="X-MS-CLIENT-PRINCIPAL",
        ),
    ) -> Principal:
        try:
            if services.principal_resolver is not None:
                return services.principal_resolver.resolve(
                    authorization=authorization,
                    ingress_principal=ingress_principal,
                )
            if authorization is None:
                raise PermissionError("Authentication is required")
            return _bearer_principal(authorization)
        except (PermissionError, PyJWTError) as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(error),
            ) from error

    @app.get("/health/live")
    def live() -> dict[str, str]:
        return {"status": "live"}

    @app.get("/health/ready")
    def ready() -> dict[str, object]:
        dependencies = {} if services.readiness is None else dict(services.readiness())
        if not all(dependencies.values()):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"status": "not_ready", "dependencies": dependencies},
            )
        return {"status": "ready", "dependencies": dependencies}

    @app.get("/v1/demo/analysis")
    def demo_analysis() -> DemoAnalysisResult:
        if services.demo_analysis is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Live sample analysis is not configured",
            )
        return services.demo_analysis.get()

    if all(
        service is not None
        for service in (
            services.estates,
            services.estate_sources,
            services.estate_inventory,
            services.discovery,
            services.recommendations,
            services.decisions,
            services.transformations,
            services.estate_repository,
        )
    ):
        estate_service = services.estates
        source_service = services.estate_sources
        inventory_service = services.estate_inventory
        discovery_service = services.discovery
        recommendation_service = services.recommendations
        decision_service = services.decisions
        transformation_service = services.transformations
        estate_repository = services.estate_repository
        assert estate_service is not None
        assert source_service is not None
        assert inventory_service is not None
        assert discovery_service is not None
        assert recommendation_service is not None
        assert decision_service is not None
        assert transformation_service is not None
        assert estate_repository is not None

        @app.get("/v1/session")
        def get_session(actor: Principal = Depends(principal)) -> dict[str, object]:
            return {
                "subject": actor.principal_id,
                "tenantId": actor.tenant_id,
                "collectionRoles": dict(actor.collection_roles),
                "hasGrant": bool(actor.collection_roles),
            }

        @app.get("/v1/assessment-checks")
        def list_assessment_checks(
            actor: Principal = Depends(principal),
        ) -> dict[str, object]:
            del actor
            return {
                "items": [asdict(check) for check in ASSESSMENT_CHECKS],
                "total": len(ASSESSMENT_CHECKS),
                "method": "deterministic",
            }

        @app.get("/v1/estates")
        def list_estates(
            collection_id: str,
            actor: Principal = Depends(principal),
        ) -> dict[str, object]:
            records = estate_service.list(collection_id, principal=actor)
            items = []
            for record in records:
                payload = _versioned_payload(record)
                payload.update(
                    asdict(
                        summarize_estate_assessment(
                            estate_repository,
                            record.value.estate_id,
                        )
                    )
                )
                items.append(payload)
            return {"items": items}

        @app.post("/v1/estates", status_code=status.HTTP_201_CREATED)
        def create_estate(
            request: EstateCreateRequest,
            actor: Principal = Depends(principal),
        ) -> dict[str, object]:
            record = estate_service.create(
                principal=actor,
                collection_id=request.collection_id,
                name=request.name,
                description=request.description,
                artifact_name_template=request.artifact_name_template,
                generate_evaluations=request.generate_evaluations,
            )
            return _versioned_payload(record)

        @app.get("/v1/estates/{estate_id}")
        def get_estate(
            estate_id: str,
            actor: Principal = Depends(principal),
        ) -> dict[str, object]:
            return _versioned_payload(estate_service.get(estate_id, principal=actor))

        @app.put("/v1/estates/{estate_id}")
        def update_estate(
            estate_id: str,
            request: EstateUpdateRequest,
            actor: Principal = Depends(principal),
        ) -> dict[str, object]:
            record = estate_service.update(
                estate_id=estate_id,
                principal=actor,
                expected_revision=request.expected_revision,
                name=request.name,
                description=request.description,
                artifact_name_template=request.artifact_name_template,
                generate_evaluations=request.generate_evaluations,
            )
            return _versioned_payload(record)

        @app.post("/v1/estates/{estate_id}/archive")
        def archive_estate(
            estate_id: str,
            request: ArchiveRequest,
            actor: Principal = Depends(principal),
        ) -> dict[str, object]:
            return _versioned_payload(
                estate_service.archive(
                    estate_id=estate_id,
                    principal=actor,
                    expected_revision=request.expected_revision,
                )
            )

        @app.post("/v1/estates/{estate_id}/purge")
        def purge_estate(
            estate_id: str,
            request: PurgeRequest,
            actor: Principal = Depends(principal),
        ) -> dict[str, object]:
            estate = estate_service.get(estate_id, principal=actor)
            expected = f"PURGE {estate.value.name}"
            if request.confirmation != expected:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Confirmation must equal '{expected}'",
                )
            tombstone = source_service.purge(
                estate_id=estate_id,
                principal=actor,
                confirmation=estate.value.name,
                reason=request.reason,
            )
            return {"purged": True, "tombstone": jsonable_encoder(tombstone)}

        @app.get("/v1/estates/{estate_id}/sources")
        def list_sources(
            estate_id: str,
            actor: Principal = Depends(principal),
        ) -> dict[str, object]:
            items = source_service.list(estate_id, principal=actor)
            return {"items": [_versioned_payload(item) for item in items]}

        @app.post(
            "/v1/estates/{estate_id}/sources",
            status_code=status.HTTP_201_CREATED,
        )
        def create_source(
            estate_id: str,
            request: SourceCreateRequest,
            actor: Principal = Depends(principal),
        ) -> dict[str, object]:
            item = source_service.register(
                estate_id=estate_id,
                principal=actor,
                kind=request.kind,
                display_name=request.display_name,
                locator=request.locator,
                credential_mode=request.credential_mode,
            )
            return _versioned_payload(item)

        @app.get("/v1/estates/{estate_id}/documents")
        def list_documents(
            estate_id: str,
            actor: Principal = Depends(principal),
        ) -> dict[str, object]:
            estate_service.get(estate_id, principal=actor)
            items = estate_repository.list_documents(estate_id)
            payloads = []
            for item in items:
                payload = _versioned_payload(item)
                payload["source_retained"] = estate_repository.has_document_source(
                    item.value.document_id,
                    item.value.source_version,
                )
                payloads.append(payload)
            return {"items": payloads}

        @app.delete("/v1/estates/{estate_id}/documents/{document_id}")
        def remove_document(
            estate_id: str,
            document_id: str,
            expected_revision: int,
            actor: Principal = Depends(principal),
        ) -> dict[str, object]:
            return _versioned_payload(
                inventory_service.remove(
                    estate_id,
                    document_id,
                    expected_revision=expected_revision,
                    principal=actor,
                )
            )

        @app.get(
            "/v1/estates/{estate_id}/documents/{document_id}/content",
            response_class=PlainTextResponse,
        )
        def get_document_content(
            estate_id: str,
            document_id: str,
            source_version: str,
            actor: Principal = Depends(principal),
        ) -> PlainTextResponse:
            estate_service.get(estate_id, principal=actor)
            document = estate_repository.get_document(document_id)
            if document is None or document.value.estate_id != estate_id or document.value.deleted:
                raise KeyError(f"Estate document does not exist: {document_id}")
            if document.value.source_version != source_version:
                raise ValueError("Requested source version is not current")
            content = estate_repository.load_document_content(document_id, source_version)
            return PlainTextResponse(content)

        @app.get("/v1/estates/{estate_id}/documents/{document_id}/source")
        def get_document_source(
            estate_id: str,
            document_id: str,
            source_version: str,
            actor: Principal = Depends(principal),
        ) -> Response:
            estate_service.get(estate_id, principal=actor)
            document = estate_repository.get_document(document_id)
            if document is None or document.value.estate_id != estate_id or document.value.deleted:
                raise KeyError(f"Estate document does not exist: {document_id}")
            if document.value.source_version != source_version:
                raise ValueError("Requested source version is not current")
            if not estate_repository.has_document_source(document_id, source_version):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "The original file was ingested before source retention was enabled; "
                        "re-upload it to retain and download the exact source"
                    ),
                )
            content = estate_repository.load_document_source(document_id, source_version)
            filename = quote(document.value.filename, safe="")
            return Response(
                content,
                media_type=document.value.media_type,
                headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
            )

        @app.post("/v1/estates/{estate_id}/discovery-runs")
        def start_discovery(
            estate_id: str,
            actor: Principal = Depends(principal),
        ) -> dict[str, object]:
            run = discovery_service.start(estate_id, principal=actor)
            return {
                "run": _versioned_payload(run),
                "reports": [
                    jsonable_encoder(report)
                    for report in discovery_service.reports(
                        run.value.run_id,
                        principal=actor,
                    )
                ],
            }

        @app.get("/v1/estates/{estate_id}/discovery-reports")
        def list_discovery_reports(
            estate_id: str,
            run_id: str,
            actor: Principal = Depends(principal),
        ) -> dict[str, object]:
            run = discovery_service.get(run_id, principal=actor)
            if run.value.estate_id != estate_id:
                raise KeyError("Discovery run does not belong to this estate")
            reports = discovery_service.reports(run_id, principal=actor)
            return {"items": [jsonable_encoder(report) for report in reports]}

        @app.get("/v1/estates/{estate_id}/runs")
        def list_runs(
            estate_id: str,
            actor: Principal = Depends(principal),
        ) -> dict[str, object]:
            estate_service.get(estate_id, principal=actor)
            runs = estate_repository.list_runs(estate_id)
            return {"items": [_versioned_payload(item) for item in runs]}

        @app.post(
            "/v1/estates/{estate_id}/uploads",
            status_code=status.HTTP_201_CREATED,
        )
        async def upload_estate_content(
            estate_id: str,
            files: list[UploadFile] = File(...),
            actor: Principal = Depends(principal),
        ) -> dict[str, object]:
            if not files:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="At least one file is required",
                )
            registered_sources: list[dict[str, object]] = []
            documents: list[VersionedRecord[EstateDocument]] = []
            for upload in files:
                filename = upload.filename or "upload"
                content = await _read_upload(
                    upload,
                    max_bytes=services.max_upload_bytes,
                )
                is_zip = filename.casefold().endswith(".zip")
                source = source_service.register(
                    principal=actor,
                    estate_id=estate_id,
                    kind=EstateSourceKind.ZIP if is_zip else EstateSourceKind.UPLOAD,
                    display_name=filename,
                    locator=(
                        "asset:" + hashlib.sha256(filename.encode("utf-8") + content).hexdigest()
                    ),
                )
                registered_sources.append(_versioned_payload(source))
                if is_zip:
                    if services.archive_expander is None:
                        raise HTTPException(
                            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="ZIP expansion is unavailable",
                        )
                    staged = services.archive_expander.expand(content)
                    items = tuple(
                        InventoryInput(
                            filename=member.path,
                            media_type=member.media_type,
                            content=member.content,
                        )
                        for member in staged
                    )
                else:
                    if services.malware_scanner is None:
                        raise HTTPException(
                            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Upload scanning is unavailable",
                        )
                    services.malware_scanner.scan(content)
                    items = (
                        InventoryInput(
                            filename=filename,
                            media_type=upload.content_type or "application/octet-stream",
                            content=content,
                        ),
                    )
                documents.extend(
                    inventory_service.ingest(
                        source.value.source_id,
                        items,
                        principal=actor,
                    )
                )
            return {
                "sources": registered_sources,
                "documents": [_versioned_payload(item) for item in documents],
            }

        @app.post("/v1/estates/{estate_id}/recommendation-runs")
        def start_recommendations(
            estate_id: str,
            request: RecommendationRequest,
            actor: Principal = Depends(principal),
        ) -> dict[str, object]:
            discovery_run = discovery_service.get(
                request.discovery_run_id,
                principal=actor,
            )
            if discovery_run.value.estate_id != estate_id:
                raise KeyError("Discovery run does not belong to this estate")
            run = recommendation_service.start(
                request.discovery_run_id,
                request.ids,
                principal=actor,
            )
            return {
                "run": _versioned_payload(run),
                "proposals": [
                    jsonable_encoder(proposal)
                    for proposal in recommendation_service.proposals(
                        run.value.run_id,
                        principal=actor,
                    )
                ],
            }

        @app.get("/v1/estates/{estate_id}/proposals")
        def list_proposals(
            estate_id: str,
            run_id: str,
            actor: Principal = Depends(principal),
        ) -> dict[str, object]:
            run = estate_repository.get_run(run_id)
            if run is None or run.value.estate_id != estate_id:
                raise KeyError("Recommendation run does not belong to this estate")
            proposals = recommendation_service.proposals(run_id, principal=actor)
            return {"items": [jsonable_encoder(item) for item in proposals]}

        @app.put("/v1/proposals/{proposal_id}/decision")
        def decide_proposal(
            proposal_id: str,
            request: DecisionRequest,
            actor: Principal = Depends(principal),
        ) -> dict[str, object]:
            decision = decision_service.decide(
                proposal_id,
                principal=actor,
                outcome=request.outcome,
                reason=request.reason,
                expected_current_decision_id=request.expected_current_decision_id,
            )
            return _versioned_payload(decision)

        @app.get("/v1/estates/{estate_id}/decisions")
        def list_decisions(
            estate_id: str,
            actor: Principal = Depends(principal),
        ) -> dict[str, object]:
            estate_service.get(estate_id, principal=actor)
            decisions = tuple(
                decision
                for document in estate_repository.list_documents(estate_id)
                if (decision := estate_repository.latest_decision(document.value.document_id))
                is not None
            )
            return {"items": [jsonable_encoder(item) for item in decisions]}

        @app.post("/v1/estates/{estate_id}/transformation-runs")
        def start_transformations(
            estate_id: str,
            request: SelectionRequest,
            actor: Principal = Depends(principal),
        ) -> dict[str, object]:
            proposals = tuple(estate_repository.get_proposal(item) for item in request.ids)
            if any(proposal is None or proposal.estate_id != estate_id for proposal in proposals):
                raise KeyError("A recommendation does not belong to this estate")
            run = transformation_service.start(request.ids, principal=actor)
            return {
                "run": _versioned_payload(run),
                "artifacts": [
                    jsonable_encoder(artifact)
                    for artifact in estate_repository.list_artifacts(estate_id)
                ],
                "usage": [
                    jsonable_encoder(item)
                    for item in estate_repository.list_usage(run.value.run_id)
                ],
            }

        @app.post("/v1/estates/{estate_id}/transformation-runs/stream")
        def stream_transformations(
            estate_id: str,
            request: SelectionRequest,
            actor: Principal = Depends(principal),
        ) -> StreamingResponse:
            proposals = tuple(estate_repository.get_proposal(item) for item in request.ids)
            if any(proposal is None or proposal.estate_id != estate_id for proposal in proposals):
                raise KeyError("A recommendation does not belong to this estate")

            def events() -> Iterator[str]:
                event_queue: Queue[dict[str, object] | None] = Queue()
                cancel_event = Event()
                active_run_id: str | None = None

                def report(event: dict[str, object]) -> None:
                    nonlocal active_run_id
                    if event.get("type") == "run_started":
                        run_id = event.get("run_id")
                        if isinstance(run_id, str):
                            active_run_id = run_id
                    event_queue.put(event)

                def transform() -> None:
                    try:
                        transformation_service.start(
                            request.ids,
                            principal=actor,
                            progress=report,
                            cancelled=cancel_event.is_set,
                        )
                    except Exception as error:
                        LOGGER.exception("Transformation stream failed")
                        if active_run_id is not None:
                            try:
                                transformation_service.fail_running(
                                    active_run_id,
                                    "Transformation stopped unexpectedly. Review service logs "
                                    "before retrying.",
                                )
                            except Exception:
                                LOGGER.exception("Could not terminalize failed transformation")
                        event_queue.put(
                            {
                                "type": "run_failed",
                                "detail": str(error),
                            }
                        )
                    finally:
                        event_queue.put(None)

                worker = Thread(
                    target=transform,
                    name=f"transform-{estate_id}",
                    daemon=True,
                )
                worker.start()
                try:
                    while True:
                        try:
                            event = event_queue.get(timeout=0.25)
                        except Empty:
                            yield "\n"
                            continue
                        if event is None:
                            break
                        yield f"{json.dumps(jsonable_encoder(event), sort_keys=True)}\n"
                finally:
                    cancel_event.set()
                    worker.join(timeout=1)

            return StreamingResponse(events(), media_type="application/x-ndjson")

        @app.get("/v1/estates/{estate_id}/artifacts")
        def list_artifacts(
            estate_id: str,
            actor: Principal = Depends(principal),
        ) -> dict[str, object]:
            estate_service.get(estate_id, principal=actor)
            artifacts = estate_repository.list_artifacts(estate_id)
            records = tuple(
                record
                for item in artifacts
                if (record := estate_repository.get_artifact(item.artifact_id)) is not None
            )
            return {"items": [_versioned_payload(item) for item in records]}

        @app.post("/v1/artifacts/{artifact_id}/approve")
        def approve_artifact(
            artifact_id: str,
            request: ArtifactApprovalRequest,
            actor: Principal = Depends(principal),
        ) -> dict[str, object]:
            review, artifact = transformation_service.approve(
                artifact_id,
                principal=actor,
                reason=request.reason,
                expected_review_revision=request.expected_review_revision,
                expected_artifact_revision=request.expected_artifact_revision,
            )
            return {
                "review": jsonable_encoder(review),
                "artifact": _versioned_payload(artifact),
            }

        @app.get("/v1/artifacts/{artifact_id}/evaluation")
        def get_artifact_evaluation(
            artifact_id: str,
            actor: Principal = Depends(principal),
        ) -> dict[str, object]:
            evaluation = transformation_service.evaluation(
                artifact_id,
                principal=actor,
            )
            payload: dict[str, object] = evaluation.model_dump(mode="json")
            return payload

        @app.get("/v1/artifacts/{artifact_id}/preview")
        def get_artifact_preview(
            artifact_id: str,
            actor: Principal = Depends(principal),
        ) -> HTMLResponse:
            content = transformation_service.preview(artifact_id, principal=actor)
            return HTMLResponse(
                content=content.decode("utf-8"),
                headers={
                    "Content-Security-Policy": ("default-src 'none'; style-src 'unsafe-inline'")
                },
            )

        @app.get("/v1/artifacts/{artifact_id}/content")
        def get_artifact_content(
            artifact_id: str,
            actor: Principal = Depends(principal),
        ) -> HTMLResponse:
            content = transformation_service.content(artifact_id, principal=actor)
            return HTMLResponse(
                content=content.decode("utf-8"),
                headers={
                    "Content-Security-Policy": ("default-src 'none'; style-src 'unsafe-inline'")
                },
            )

    @app.post("/v1/assessments")
    def assess(
        request: AssessmentRequest,
        caller: Principal = Depends(principal),
    ) -> EstateAssessment:
        if services.assessments is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Estate assessment is not configured",
            )
        try:
            caller.require(request.collection_id, CollectionRole.COMPILE)
            return services.assessments.assess(
                collection_id=request.collection_id,
                profiles=_assessment_profiles(request),
                assessed_at=request.assessed_at,
            )
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(error),
            ) from error
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(error),
            ) from error

    @app.post("/v1/platform/analyses")
    def analyze_platform(
        request: AssessmentRequest,
        caller: Principal = Depends(principal),
    ) -> KnowledgeTransformationAnalysis:
        if services.orchestrator is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Knowledge transformation orchestration is not configured",
            )
        try:
            caller.require(request.collection_id, CollectionRole.COMPILE)
            return services.orchestrator.analyze(
                collection_id=request.collection_id,
                profiles=_assessment_profiles(request),
                assessed_at=request.assessed_at,
            )
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(error),
            ) from error
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(error),
            ) from error

    @app.post("/v1/evaluations/improvement")
    def evaluate_improvement(
        request: ImprovementRequest,
        caller: Principal = Depends(principal),
    ) -> ImprovementReport:
        try:
            caller.require(request.collection_id, CollectionRole.COMPILE)
            return compare_paired_answer_pass_rates(
                request.outcomes,
                dataset_reviewed=request.dataset_reviewed,
                confidence_level=request.confidence_level,
            )
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(error),
            ) from error
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(error),
            ) from error

    @app.post("/v1/jobs", status_code=status.HTTP_202_ACCEPTED)
    def submit(
        request: CompileRequest,
        caller: Principal = Depends(principal),
    ) -> CompileJob:
        try:
            return services.jobs.submit(
                principal=caller,
                source=SourceRef.model_validate_json(json.dumps(request.source)),
                output=OutputRef.model_validate_json(json.dumps(request.output)),
                idempotency_key=request.idempotency_key,
                requested_token_budget=request.model_token_budget,
            )
        except (PermissionError, QuotaExceededError) as error:
            code = (
                status.HTTP_403_FORBIDDEN
                if isinstance(error, PermissionError)
                else status.HTTP_429_TOO_MANY_REQUESTS
            )
            raise HTTPException(status_code=code, detail=str(error)) from error

    @app.post("/v1/uploads", status_code=status.HTTP_201_CREATED)
    def upload(
        collection_id: str = Form(min_length=1),
        document: UploadFile = File(),
        caller: Principal = Depends(principal),
    ) -> dict[str, object]:
        if services.uploads is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Direct upload storage is not configured",
            )

        def chunks() -> Iterator[bytes]:
            while chunk := document.file.read(1024 * 1024):
                yield chunk

        try:
            asset = services.uploads.stage(
                chunks(),
                supplied_filename=document.filename or "",
                media_type=document.content_type or "application/octet-stream",
                principal=caller,
                collection_id=collection_id,
            )
        except ScannerUnavailableError as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(error),
            ) from error
        except UploadRejectedError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(error),
            ) from error
        finally:
            document.file.close()
        return asdict(asset)

    @app.get("/v1/jobs/{job_id}")
    def job_status(job_id: str, caller: Principal = Depends(principal)) -> CompileJob:
        try:
            return services.jobs.status(job_id, principal=caller)
        except KeyError as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
        except PermissionError as error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error

    @app.post("/v1/jobs/{job_id}/cancel")
    def cancel(job_id: str, caller: Principal = Depends(principal)) -> CompileJob:
        try:
            return services.jobs.cancel(job_id, principal=caller)
        except KeyError as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
        except PermissionError as error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
        except JobConflictError as error:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error

    @app.get("/v1/jobs/{job_id}/review")
    def review_status(
        job_id: str,
        caller: Principal = Depends(principal),
    ) -> dict[str, object]:
        if services.compilation is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Hosted compilation is not configured",
            )
        try:
            review = services.compilation.review_status(job_id, principal=caller)
        except KeyError as error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(error),
            ) from error
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(error),
            ) from error
        return {
            "unit": review.unit.model_dump(mode="json"),
            "revision": review.revision,
            "decisions": [decision.model_dump(mode="json") for decision in review.decisions],
        }

    @app.post("/v1/jobs/{job_id}/review/approve")
    def approve(
        job_id: str,
        request: ApprovalRequest,
        caller: Principal = Depends(principal),
    ) -> dict[str, object]:
        if services.compilation is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Hosted compilation is not configured",
            )
        try:
            review, release_id = services.compilation.approve(
                job_id,
                principal=caller,
                reason=request.reason,
                expected_revision=request.expected_revision,
            )
        except KeyError as error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(error),
            ) from error
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(error),
            ) from error
        except (JobConflictError, ReviewConflictError) as error:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(error),
            ) from error
        return {
            "unit": review.unit.model_dump(mode="json"),
            "revision": review.revision,
            "release_id": release_id,
        }

    @app.post("/v1/query")
    def query(
        request: QueryRequest,
        caller: Principal = Depends(principal),
    ) -> list[dict[str, object]]:
        if services.query is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No current release is indexed",
            )
        try:
            results = services.query.query(request.text, principal=caller, limit=request.limit)
        except PermissionError as error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
        return [
            {
                "unit": result.unit.model_dump(mode="json"),
                "score": result.score,
                "lexical_rank": result.lexical_rank,
                "vector_rank": result.vector_rank,
                "coverage_warning": result.coverage_warning,
                "release_id": services.query.release_id,
            }
            for result in results
        ]

    @app.get("/v1/units/{unit_id}/explain")
    def explain(unit_id: str, caller: Principal = Depends(principal)) -> dict[str, object]:
        if services.query is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No current release is indexed",
            )
        try:
            return services.query.explain(unit_id, principal=caller)
        except KeyError as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
        except PermissionError as error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error

    if services.concept_root is not None:
        concept_root = services.concept_root.resolve()
        if not (concept_root / "index.html").is_file():
            raise ValueError(f"Concept root has no index.html: {concept_root}")
        app.mount(
            "/concept",
            StaticFiles(directory=concept_root, html=True),
            name="copilot-studio-concept",
        )

    return app


def _assessment_profiles(
    request: AssessmentRequest,
) -> tuple[KnowledgeDocumentProfile, ...]:
    return tuple(
        KnowledgeDocumentProfile.model_validate_json(json.dumps(profile))
        for profile in request.profiles
    )


def _versioned_payload(record: object) -> dict[str, object]:
    payload = jsonable_encoder(record)
    if not isinstance(payload, dict):
        raise TypeError("Versioned record did not encode as an object")
    return payload


async def _read_upload(upload: UploadFile, *, max_bytes: int) -> bytes:
    content = bytearray()
    while chunk := await upload.read(1024 * 1024):
        content.extend(chunk)
        if len(content) > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Upload exceeds the {max_bytes}-byte limit",
            )
    return bytes(content)
