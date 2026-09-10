"""FastAPI adapter for jobs, query, explanation, and health."""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator, Mapping
from dataclasses import asdict, dataclass
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile, status
from fastapi.staticfiles import StaticFiles
from jwt import PyJWTError
from pydantic import BaseModel, ConfigDict, Field

from shaper.application.compiler import CompilationService
from shaper.application.jobs import (
    CompileJobService,
    JobConflictError,
    QuotaExceededError,
)
from shaper.application.query import QueryGateway
from shaper.application.review import ReviewConflictError
from shaper.domain import CompileJob, OutputRef, Principal, SourceRef
from shaper.infrastructure.uploads import (
    FileUploadStore,
    ScannerUnavailableError,
    UploadRejectedError,
)
from shaper.interfaces.auth import Authenticator


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


@dataclass(frozen=True)
class HttpServices:
    """Application services exposed through HTTP."""

    jobs: CompileJobService
    authenticator: Authenticator
    query: QueryGateway | None = None
    uploads: FileUploadStore | None = None
    compilation: CompilationService | None = None
    readiness: Callable[[], Mapping[str, bool]] | None = None
    concept_root: Path | None = None


def create_app(services: HttpServices) -> FastAPI:
    """Create the HTTP service without global mutable dependencies."""
    app = FastAPI(title="Shaper", version="0.1.0")

    def principal(authorization: str = Header()) -> Principal:
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
