"""Thin MCP tools and resources over shared application services."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass

from mcp.server.auth.provider import TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP
from pydantic import AnyHttpUrl

from shaper.application.jobs import CompileJobService
from shaper.application.query import QueryGateway
from shaper.domain import OutputRef, Principal, SourceRef


@dataclass(frozen=True)
class McpServices:
    """Application services exposed through MCP."""

    jobs: CompileJobService
    query: QueryGateway
    principal: Callable[[], Principal]


@dataclass(frozen=True)
class McpAuth:
    """MCP resource-server authentication configuration."""

    issuer_url: str
    resource_server_url: str
    token_verifier: TokenVerifier


def create_mcp_server(services: McpServices, *, auth: McpAuth | None = None) -> FastMCP:
    """Create the four planned tools and three resource families."""
    server = FastMCP(
        name="shaper",
        instructions="Query source-grounded evidence and submit bounded compile jobs.",
        streamable_http_path="/",
        stateless_http=True,
        json_response=True,
        token_verifier=None if auth is None else auth.token_verifier,
        auth=(
            None
            if auth is None
            else AuthSettings(
                issuer_url=AnyHttpUrl(auth.issuer_url),
                resource_server_url=AnyHttpUrl(auth.resource_server_url),
            )
        ),
    )

    @server.tool(name="knowledge.query", structured_output=True)
    def knowledge_query(text: str, limit: int = 10) -> dict[str, object]:
        """Query the current authorized evidence release."""
        results = services.query.query(text, principal=services.principal(), limit=limit)
        return {
            "release_id": services.query.release_id,
            "results": [
                {
                    "unit": result.unit.model_dump(mode="json"),
                    "score": result.score,
                    "coverage_warning": result.coverage_warning,
                }
                for result in results
            ],
        }

    @server.tool(name="knowledge.explain", structured_output=True)
    def knowledge_explain(unit_id: str) -> dict[str, object]:
        """Explain one answer unit from source and derivation evidence."""
        return services.query.explain(unit_id, principal=services.principal())

    @server.tool(name="knowledge.compile", structured_output=True)
    def knowledge_compile(
        source: dict[str, object],
        output: dict[str, object],
        idempotency_key: str,
        model_token_budget: int,
    ) -> dict[str, object]:
        """Submit a compile-by-reference request requiring host confirmation."""
        job = services.jobs.submit(
            principal=services.principal(),
            source=SourceRef.model_validate_json(json.dumps(source)),
            output=OutputRef.model_validate_json(json.dumps(output)),
            idempotency_key=idempotency_key,
            requested_token_budget=model_token_budget,
        )
        return {
            "job": job.model_dump(mode="json"),
            "confirmation_required": True,
            "destructive": False,
        }

    @server.tool(name="knowledge.job_status", structured_output=True)
    def knowledge_job_status(job_id: str) -> dict[str, object]:
        """Return authorized compile-job status."""
        return services.jobs.status(job_id, principal=services.principal()).model_dump(mode="json")

    @server.resource("knowledge://units/{unit_id}", mime_type="application/json")
    def unit_resource(unit_id: str) -> str:
        """Return one versioned evidence unit."""
        return json.dumps(
            services.query.explain(unit_id, principal=services.principal()),
            sort_keys=True,
        )

    @server.resource("knowledge://sources/{source_id}", mime_type="application/json")
    def source_resource(source_id: str) -> str:
        """Return bounded source identity for units in the active release."""
        units = [
            result.unit
            for result in services.query.query(
                source_id,
                principal=services.principal(),
                limit=50,
            )
            if result.unit.source_id == source_id
        ]
        return json.dumps(
            {
                "source_id": source_id,
                "source_versions": sorted({unit.source_version for unit in units}),
                "unit_ids": sorted(unit.unit_id for unit in units),
            },
            sort_keys=True,
        )

    @server.resource("knowledge://releases/{release_id}", mime_type="application/json")
    def release_resource(release_id: str) -> str:
        """Return active release identity without exposing storage paths."""
        if release_id != services.query.release_id:
            raise KeyError(f"Release is not active: {release_id}")
        return json.dumps({"release_id": release_id, "status": "current"}, sort_keys=True)

    return server
