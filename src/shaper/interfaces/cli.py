"""Operator CLI for the local and hosted Shaper service."""

from __future__ import annotations

import sys
from pathlib import Path

import typer
import uvicorn

from shaper.application.compiler import CompilationService
from shaper.application.jobs import (
    CompileJobDispatcher,
    CompileJobService,
    CompileJobWorker,
)
from shaper.application.model import AzureOpenAIModelGateway
from shaper.application.review import ReviewService
from shaper.application.validation import DeterministicValidator
from shaper.config import ModelProvider, Settings
from shaper.infrastructure.compilation import (
    FilesystemCompilationPublisher,
    SQLiteCandidateStore,
    SQLiteCheckpointStore,
    SQLiteReviewStore,
)
from shaper.infrastructure.parsers import SupportedDocumentParser
from shaper.infrastructure.projection import ReloadingQueryService
from shaper.infrastructure.sqlite import SQLiteStore
from shaper.infrastructure.uploads import ClamdScanner, FileUploadStore
from shaper.interfaces.auth import (
    McpOIDCTokenVerifier,
    OIDCAuthenticator,
    current_mcp_principal,
)
from shaper.interfaces.hosted import create_hosted_app
from shaper.interfaces.http import HttpServices
from shaper.interfaces.mcp_server import McpAuth, McpServices, create_mcp_server
from shaper.logging import configure_logging

app = typer.Typer(no_args_is_help=True)


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
        settings.database_path,
        journal_mode=settings.sqlite_journal_mode.value,
    )
    store.connect()
    store.migrate()
    jobs = CompileJobService(store)
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
    compilation = CompilationService(
        jobs=store,
        uploads=uploads,
        parser=SupportedDocumentParser(),
        model=model,
        validator=DeterministicValidator(),
        checkpoints=SQLiteCheckpointStore(store),
        candidates=SQLiteCandidateStore(store),
        reviews=ReviewService(SQLiteReviewStore(store)),
        publisher=FilesystemCompilationPublisher(settings.release_root),
    )
    dispatcher = CompileJobDispatcher(
        store,
        CompileJobWorker(store, compilation.compile),
    )
    http_services = HttpServices(
        jobs=jobs,
        authenticator=authenticator,
        query=query,
        uploads=uploads,
        compilation=compilation,
        readiness=lambda: {
            "state_store": store.is_ready(),
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
        ),
        auth=McpAuth(
            issuer_url=settings.oidc_issuer,
            resource_server_url=f"{settings.public_url.rstrip('/')}/mcp/",
            token_verifier=McpOIDCTokenVerifier(authenticator),
        ),
    )

    def shutdown() -> None:
        dispatcher.stop()
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
