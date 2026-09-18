"""Operator CLI for the local and hosted Shaper service."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

import typer
import uvicorn

from shaper.application.artifacts import EstateTransformationService, HtmlArtifactRenderer
from shaper.application.assessment import DocumentAssessmentService, EstateAssessmentService
from shaper.application.compiler import CompilationService
from shaper.application.decisions import TransformationDecisionService
from shaper.application.demo import DemoAnalysisService
from shaper.application.estates import (
    EstateDiscoveryService,
    EstateInventoryService,
    EstateRecommendationService,
    EstateRepository,
    EstateService,
    EstateSourceService,
)
from shaper.application.evaluation_sets import EvaluationSetService
from shaper.application.jobs import (
    CompileJobDispatcher,
    CompileJobService,
    CompileJobWorker,
    JobStore,
)
from shaper.application.model import AzureOpenAIModelGateway
from shaper.application.orchestration import (
    AgentReadinessAgent,
    AssessmentAgent,
    GovernanceAgent,
    KnowledgeAgent,
    KnowledgeTransformationOrchestrator,
    TransformationAgent,
)
from shaper.application.passage_reshape import PassageReshapeService
from shaper.application.review import ReviewService, ReviewStore
from shaper.application.token_estimation import TokenEstimator
from shaper.application.validation import DeterministicValidator
from shaper.config import ModelProvider, RuntimeProfile, Settings
from shaper.domain import CollectionGrant, CollectionRole
from shaper.infrastructure.archive import ZipArchiveExpander
from shaper.infrastructure.compilation import (
    FilesystemCompilationPublisher,
    SQLiteCandidateStore,
    SQLiteCheckpointStore,
    SQLiteReviewStore,
)
from shaper.infrastructure.parsers import SupportedDocumentParser
from shaper.infrastructure.postgres import (
    PostgresEstateRepository,
    PostgresJobStore,
    PostgresRecordStore,
    PostgresReviewStore,
)
from shaper.infrastructure.projection import ReloadingQueryService
from shaper.infrastructure.sqlite import SQLiteEstateRepository, SQLiteStore
from shaper.infrastructure.uploads import ClamdScanner, FileUploadStore
from shaper.interfaces.auth import (
    McpOIDCTokenVerifier,
    OIDCAuthenticator,
    RequestPrincipalResolver,
    current_mcp_principal,
)
from shaper.interfaces.hosted import create_hosted_app
from shaper.interfaces.http import HttpServices
from shaper.interfaces.mcp_server import McpAuth, McpServices, create_mcp_server
from shaper.logging import configure_logging

app = typer.Typer(no_args_is_help=True, pretty_exceptions_show_locals=False)


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Bind host."),
    port: int = typer.Option(8000, min=1, max=65535, help="Bind port."),
) -> None:
    """Run authenticated HTTP and MCP services in one process."""
    settings = Settings()
    if (
        settings.oidc_issuer is None
        or settings.oidc_audience is None
        or settings.public_url is None
        or settings.collection_id is None
    ):
        raise typer.BadParameter(
            "OIDC issuer, audience, public URL, and collection ID are required to serve requests"
        )
    configure_logging()
    store = SQLiteStore(
        ":memory:" if settings.profile is RuntimeProfile.PRODUCTION else settings.database_path,
        journal_mode=settings.sqlite_journal_mode.value,
    )
    store.connect()
    store.migrate()
    postgres_store: PostgresRecordStore | None = None
    estate_repository: EstateRepository
    job_store: JobStore
    review_store: ReviewStore
    if settings.profile is RuntimeProfile.PRODUCTION:
        if settings.postgres_url is None:
            raise typer.BadParameter("Production estate persistence requires PostgreSQL")
        postgres_store = PostgresRecordStore(settings.postgres_url.get_secret_value())
        postgres_store.connect()
        postgres_store.migrate()
        estate_repository = PostgresEstateRepository(postgres_store)
        job_store = PostgresJobStore(postgres_store)
        review_store = PostgresReviewStore(postgres_store)
    else:
        estate_repository = SQLiteEstateRepository(store)
        job_store = store
        review_store = SQLiteReviewStore(store)
    if (
        settings.bootstrap_tenant_id is not None
        and settings.bootstrap_principal_id is not None
        and settings.collection_id is not None
    ):
        estate_repository.save_grant(
            CollectionGrant(
                grant_id=(
                    f"grant-{settings.bootstrap_tenant_id}-"
                    f"{settings.bootstrap_principal_id}-{settings.collection_id}"
                ),
                tenant_id=settings.bootstrap_tenant_id,
                principal_id=settings.bootstrap_principal_id,
                collection_id=settings.collection_id,
                roles=frozenset(
                    {
                        CollectionRole.ADMIN,
                        CollectionRole.COMPILE,
                        CollectionRole.QUERY,
                        CollectionRole.REVIEW,
                    }
                ),
                created_at=datetime.now(UTC),
            )
        )
    jobs = CompileJobService(job_store)
    authenticator = OIDCAuthenticator(
        issuer=settings.oidc_issuer,
        audience=settings.oidc_audience,
    )
    query = ReloadingQueryService(
        settings.release_root,
        collection_id=settings.collection_id,
    )
    scanner = ClamdScanner(settings.clamd_host, settings.clamd_port)
    uploads = FileUploadStore(
        settings.upload_root,
        scanner=scanner,
    )
    if (
        settings.model_provider is not ModelProvider.AZURE_OPENAI
        or settings.azure_openai_endpoint is None
        or settings.azure_openai_deployment is None
    ):
        raise typer.BadParameter("Hosted compilation requires the Azure OpenAI model provider")
    model = AzureOpenAIModelGateway(
        endpoint=settings.azure_openai_endpoint,
        api_key=(
            None
            if settings.azure_openai_api_key is None
            else settings.azure_openai_api_key.get_secret_value()
        ),
        deployment=settings.azure_openai_deployment,
        use_managed_identity=settings.azure_openai_use_managed_identity,
    )
    parser = SupportedDocumentParser()
    validator = DeterministicValidator()
    reviews = ReviewService(review_store)
    compilation = CompilationService(
        jobs=job_store,
        uploads=uploads,
        parser=parser,
        model=model,
        validator=validator,
        checkpoints=SQLiteCheckpointStore(store),
        candidates=SQLiteCandidateStore(store),
        reviews=reviews,
        publisher=FilesystemCompilationPublisher(settings.release_root),
    )
    dispatcher = CompileJobDispatcher(
        job_store,
        CompileJobWorker(job_store, compilation.compile),
    )
    assessments = EstateAssessmentService()
    orchestrator = KnowledgeTransformationOrchestrator(
        assessments=assessments,
        assessment_agent=AssessmentAgent(),
        knowledge_agent=KnowledgeAgent(),
        transformation_agent=TransformationAgent(),
        governance_agent=GovernanceAgent(),
        agent_readiness_agent=AgentReadinessAgent(),
    )
    estate_service = EstateService(estate_repository, clock=lambda: datetime.now(UTC))
    source_service = EstateSourceService(
        estate_repository,
        clock=lambda: datetime.now(UTC),
    )
    inventory_service = EstateInventoryService(
        estate_repository,
        parser=parser,
        clock=lambda: datetime.now(UTC),
    )
    discovery_service = EstateDiscoveryService(
        estate_repository,
        documents=DocumentAssessmentService(),
        orchestrator=orchestrator,
        clock=lambda: datetime.now(UTC),
    )
    recommendation_service = EstateRecommendationService(
        estate_repository,
        transformation_agent=TransformationAgent(),
        estimator=TokenEstimator(
            model_deployment=settings.azure_openai_deployment,
            platform_maximum=settings.transformation_token_limit,
        ),
        clock=lambda: datetime.now(UTC),
    )
    decision_service = TransformationDecisionService(
        estate_repository,
        clock=lambda: datetime.now(UTC),
    )
    transformation_service = EstateTransformationService(
        estate_repository,
        model=model,
        validator=validator,
        reviews=reviews,
        renderer=HtmlArtifactRenderer(),
        clock=lambda: datetime.now(UTC),
    )
    passage_reshape_service = PassageReshapeService(
        estate_repository,
        estates=estate_service,
        model=model,
    )
    evaluation_set_service = EvaluationSetService(estate_repository)
    http_services = HttpServices(
        jobs=jobs,
        authenticator=authenticator,
        query=query,
        uploads=uploads,
        compilation=compilation,
        assessments=assessments,
        orchestrator=orchestrator,
        demo_analysis=DemoAnalysisService(orchestrator),
        principal_resolver=RequestPrincipalResolver(
            authenticator=authenticator,
            grants=estate_repository,
            trust_ingress_identity=settings.trust_ingress_identity,
        ),
        estates=estate_service,
        estate_sources=source_service,
        estate_inventory=inventory_service,
        discovery=discovery_service,
        recommendations=recommendation_service,
        decisions=decision_service,
        transformations=transformation_service,
        evaluation_sets=evaluation_set_service,
        passage_reshape=passage_reshape_service,
        estate_repository=estate_repository,
        archive_expander=ZipArchiveExpander(scanner),
        malware_scanner=scanner,
        readiness=lambda: {
            "state_store": store.is_ready(),
            "estate_store": (
                store.is_ready() if postgres_store is None else postgres_store.is_ready()
            ),
            "malware_scanner": scanner.is_ready(),
            "compile_worker": dispatcher.is_ready(),
        },
        concept_root=Path("/app/prototype/copilot-studio-knowledge-compiler"),
    )
    mcp_server = create_mcp_server(
        McpServices(
            jobs=jobs,
            query=query,
            principal=current_mcp_principal,
            estates=estate_service,
            estate_sources=source_service,
            discovery=discovery_service,
            recommendations=recommendation_service,
            decisions=decision_service,
            transformations=transformation_service,
            estate_repository=estate_repository,
            evaluation_sets=evaluation_set_service,
        ),
        auth=McpAuth(
            issuer_url=settings.oidc_issuer,
            resource_server_url=f"{settings.public_url.rstrip('/')}/mcp/",
            token_verifier=McpOIDCTokenVerifier(authenticator),
        ),
    )

    def shutdown() -> None:
        dispatcher.stop()
        if postgres_store is not None:
            postgres_store.close()
        store.close()

    hosted_app = create_hosted_app(
        http_services,
        mcp_server,
        on_startup=dispatcher.start,
        on_shutdown=shutdown,
    )
    uvicorn.run(hosted_app, host=host, port=port)


def main() -> int:
    """Run the Typer application with standard exit behavior."""
    try:
        app()
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
