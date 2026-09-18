"""Thin MCP tools and resources over shared application services."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import TypeVar

from mcp.server.auth.provider import TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import AnyHttpUrl
from pydantic_core import to_jsonable_python

from shaper.application.artifacts import EstateTransformationService
from shaper.application.decisions import TransformationDecisionService
from shaper.application.document_findings import ASSESSMENT_CHECKS
from shaper.application.estates import (
    EstateDiscoveryService,
    EstateRecommendationService,
    EstateRepository,
    EstateService,
    EstateSourceService,
    VersionedRecord,
    summarize_estate_assessment,
)
from shaper.application.evaluation_sets import EvaluationSetService
from shaper.application.jobs import CompileJobService
from shaper.application.query import QueryGateway
from shaper.domain import (
    DecisionOutcome,
    EstateSourceKind,
    OutputRef,
    Principal,
    SharePointCredentialMode,
    SourceRef,
    WorkflowKind,
)
from shaper.interfaces.presenters import finding_report_payload

READ_ONLY = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)
MUTATING = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=False,
)
IDEMPOTENT_MUTATION = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)
RecordT = TypeVar("RecordT")


@dataclass(frozen=True)
class McpServices:
    """Application services exposed through MCP."""

    jobs: CompileJobService
    query: QueryGateway
    principal: Callable[[], Principal]
    estates: EstateService | None = None
    estate_sources: EstateSourceService | None = None
    discovery: EstateDiscoveryService | None = None
    recommendations: EstateRecommendationService | None = None
    decisions: TransformationDecisionService | None = None
    transformations: EstateTransformationService | None = None
    estate_repository: EstateRepository | None = None
    evaluation_sets: EvaluationSetService | None = None


@dataclass(frozen=True)
class McpAuth:
    """MCP resource-server authentication configuration."""

    issuer_url: str
    resource_server_url: str
    token_verifier: TokenVerifier


def create_mcp_server(services: McpServices, *, auth: McpAuth | None = None) -> FastMCP:
    """Create the grounded knowledge and governed Knowledge Estate MCP surface."""
    server = FastMCP(
        name="shaper",
        instructions=(
            "Query source-grounded evidence and operate governed Knowledge Estate "
            "assessment, recommendation, transformation, review, and publication workflows."
        ),
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

    @server.tool(name="knowledge.query", annotations=READ_ONLY, structured_output=True)
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

    @server.tool(name="knowledge.explain", annotations=READ_ONLY, structured_output=True)
    def knowledge_explain(unit_id: str) -> dict[str, object]:
        """Explain one answer unit from source and derivation evidence."""
        return services.query.explain(unit_id, principal=services.principal())

    @server.tool(
        name="knowledge.compile",
        annotations=IDEMPOTENT_MUTATION,
        structured_output=True,
    )
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

    @server.tool(name="knowledge.job_status", annotations=READ_ONLY, structured_output=True)
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

    estate_dependencies = (
        services.estates,
        services.estate_sources,
        services.discovery,
        services.recommendations,
        services.decisions,
        services.transformations,
        services.estate_repository,
        services.evaluation_sets,
    )
    if all(item is None for item in estate_dependencies):
        return server
    if any(item is None for item in estate_dependencies):
        raise ValueError("Knowledge Estate MCP services must be configured together")

    estates = services.estates
    estate_sources = services.estate_sources
    discovery = services.discovery
    recommendations = services.recommendations
    decisions = services.decisions
    transformations = services.transformations
    repository = services.estate_repository
    evaluation_sets = services.evaluation_sets
    assert estates is not None
    assert estate_sources is not None
    assert discovery is not None
    assert recommendations is not None
    assert decisions is not None
    assert transformations is not None
    assert repository is not None
    assert evaluation_sets is not None

    @server.tool(name="estate.assessment_checks", annotations=READ_ONLY, structured_output=True)
    def estate_assessment_checks() -> dict[str, object]:
        """List the deterministic checks used by Knowledge Estate discovery."""
        return {
            "items": [asdict(check) for check in ASSESSMENT_CHECKS],
            "total": len(ASSESSMENT_CHECKS),
            "method": "deterministic",
        }

    @server.tool(name="estate.list", annotations=READ_ONLY, structured_output=True)
    def estate_list(collection_id: str) -> dict[str, object]:
        """List authorized Knowledge Estates and current assessment coverage."""
        records = estates.list(collection_id, principal=services.principal())
        items: list[dict[str, object]] = []
        for record in records:
            payload = _versioned_payload(record)
            payload.update(
                to_jsonable_python(
                    asdict(summarize_estate_assessment(repository, record.value.estate_id))
                )
            )
            items.append(payload)
        return {"items": items}

    @server.tool(name="estate.get", annotations=READ_ONLY, structured_output=True)
    def estate_get(estate_id: str) -> dict[str, object]:
        """Return one authorized Knowledge Estate and its current revision."""
        return _versioned_payload(estates.get(estate_id, principal=services.principal()))

    @server.tool(name="estate.create", annotations=MUTATING, structured_output=True)
    def estate_create(
        collection_id: str,
        name: str,
        description: str = "",
        artifact_name_template: str = "shaper_{source_stem}.html",
        generate_evaluations: bool = False,
    ) -> dict[str, object]:
        """Create an estate; repeated calls create distinct estates."""
        return _versioned_payload(
            estates.create(
                principal=services.principal(),
                collection_id=collection_id,
                name=name,
                description=description,
                artifact_name_template=artifact_name_template,
                generate_evaluations=generate_evaluations,
            )
        )

    @server.tool(name="estate.update", annotations=MUTATING, structured_output=True)
    def estate_update(
        estate_id: str,
        expected_revision: int,
        name: str,
        description: str,
        artifact_name_template: str,
        generate_evaluations: bool,
    ) -> dict[str, object]:
        """Update an estate using its exact current revision."""
        return _versioned_payload(
            estates.update(
                estate_id,
                principal=services.principal(),
                expected_revision=expected_revision,
                name=name,
                description=description,
                artifact_name_template=artifact_name_template,
                generate_evaluations=generate_evaluations,
            )
        )

    @server.tool(name="estate.source.list", annotations=READ_ONLY, structured_output=True)
    def estate_source_list(estate_id: str) -> dict[str, object]:
        """List registered sources for an authorized estate."""
        return {
            "items": [
                _versioned_payload(item)
                for item in estate_sources.list(estate_id, principal=services.principal())
            ]
        }

    @server.tool(name="estate.source.register", annotations=MUTATING, structured_output=True)
    def estate_source_register(
        estate_id: str,
        kind: str,
        display_name: str,
        locator: str,
        credential_mode: str = "delegated_user",
    ) -> dict[str, object]:
        """Register a URL or SharePoint source without claiming synchronization."""
        source_kind = EstateSourceKind(kind)
        if source_kind not in {EstateSourceKind.URL, EstateSourceKind.SHAREPOINT}:
            raise ValueError("MCP source registration accepts only url or sharepoint")
        return _versioned_payload(
            estate_sources.register(
                estate_id,
                principal=services.principal(),
                kind=source_kind,
                display_name=display_name,
                locator=locator,
                credential_mode=SharePointCredentialMode(credential_mode),
            )
        )

    @server.tool(name="estate.document.list", annotations=READ_ONLY, structured_output=True)
    def estate_document_list(estate_id: str) -> dict[str, object]:
        """List current documents and source-retention availability."""
        estates.get(estate_id, principal=services.principal())
        items: list[dict[str, object]] = []
        for record in repository.list_documents(estate_id):
            payload = _versioned_payload(record)
            payload["source_retained"] = repository.has_document_source(
                record.value.document_id,
                record.value.source_version,
            )
            items.append(payload)
        return {"items": items}

    @server.tool(name="estate.run.list", annotations=READ_ONLY, structured_output=True)
    def estate_run_list(estate_id: str) -> dict[str, object]:
        """List persisted workflow runs for an authorized estate."""
        estates.get(estate_id, principal=services.principal())
        return {
            "items": [
                _versioned_payload(item) for item in repository.list_runs(estate_id)
            ]
        }

    @server.tool(name="estate.discovery.start", annotations=MUTATING, structured_output=True)
    def estate_discovery_start(estate_id: str) -> dict[str, object]:
        """Run deterministic discovery; repeated calls create distinct runs."""
        run = discovery.start(estate_id, principal=services.principal())
        return {
            "run": _versioned_payload(run),
            "reports": [
                finding_report_payload(report)
                for report in discovery.reports(
                    run.value.run_id,
                    principal=services.principal(),
                )
            ],
        }

    @server.tool(name="estate.discovery.reports", annotations=READ_ONLY, structured_output=True)
    def estate_discovery_reports(estate_id: str, run_id: str) -> dict[str, object]:
        """Return findings and agent-impact evidence from one discovery run."""
        run = discovery.get(run_id, principal=services.principal())
        if run.value.estate_id != estate_id:
            raise KeyError("Discovery run does not belong to this estate")
        return {
            "items": [
                finding_report_payload(report)
                for report in discovery.reports(run_id, principal=services.principal())
            ]
        }

    @server.tool(
        name="estate.recommendation.start",
        annotations=MUTATING,
        structured_output=True,
    )
    def estate_recommendation_start(
        estate_id: str,
        discovery_run_id: str,
        document_ids: list[str],
    ) -> dict[str, object]:
        """Create proposals from selected discovery evidence."""
        discovery_run = discovery.get(discovery_run_id, principal=services.principal())
        if discovery_run.value.estate_id != estate_id:
            raise KeyError("Discovery run does not belong to this estate")
        run = recommendations.start(
            discovery_run_id,
            document_ids,
            principal=services.principal(),
        )
        return {
            "run": _versioned_payload(run),
            "proposals": [
                _jsonable(item)
                for item in recommendations.proposals(
                    run.value.run_id,
                    principal=services.principal(),
                )
            ],
        }

    @server.tool(name="estate.proposal.list", annotations=READ_ONLY, structured_output=True)
    def estate_proposal_list(estate_id: str, run_id: str) -> dict[str, object]:
        """List exact transformation proposals for one recommendation run."""
        run = repository.get_run(run_id)
        if (
            run is None
            or run.value.estate_id != estate_id
            or run.value.kind is not WorkflowKind.RECOMMEND
        ):
            raise KeyError("Recommendation run does not belong to this estate")
        return {
            "items": [
                _jsonable(item)
                for item in recommendations.proposals(
                    run_id,
                    principal=services.principal(),
                )
            ]
        }

    @server.tool(name="estate.proposal.decide", annotations=MUTATING, structured_output=True)
    def estate_proposal_decide(
        recommendation_id: str,
        outcome: str,
        reason: str,
        expected_current_decision_id: str | None = None,
    ) -> dict[str, object]:
        """Record a review-authorized decision on the exact current proposal."""
        return _jsonable(
            decisions.decide(
                recommendation_id,
                principal=services.principal(),
                outcome=DecisionOutcome(outcome),
                reason=reason,
                expected_current_decision_id=expected_current_decision_id,
            )
        )

    @server.tool(name="estate.decision.list", annotations=READ_ONLY, structured_output=True)
    def estate_decision_list(estate_id: str) -> dict[str, object]:
        """List current proposal decisions for an authorized estate."""
        estates.get(estate_id, principal=services.principal())
        current = tuple(
            decision
            for document in repository.list_documents(estate_id)
            if (decision := repository.latest_decision(document.value.document_id))
            is not None
        )
        return {"items": [_jsonable(item) for item in current]}

    @server.tool(
        name="estate.transformation.start",
        annotations=MUTATING,
        structured_output=True,
    )
    def estate_transformation_start(
        estate_id: str,
        recommendation_id: str,
        enforce_preservation_checks: bool = False,
    ) -> dict[str, object]:
        """Transform one approved proposal; inspect runs before retrying."""
        proposal = repository.get_proposal(recommendation_id)
        if proposal is None or proposal.estate_id != estate_id:
            raise KeyError("Recommendation does not belong to this estate")
        run = transformations.start(
            [recommendation_id],
            principal=services.principal(),
            enforce_preservation_checks=enforce_preservation_checks,
        )
        return {
            "run": _versioned_payload(run),
            "artifacts": [
                _jsonable(item) for item in repository.list_artifacts(estate_id)
            ],
            "usage": [
                _jsonable(item) for item in repository.list_usage(run.value.run_id)
            ],
        }

    @server.tool(name="estate.artifact.list", annotations=READ_ONLY, structured_output=True)
    def estate_artifact_list(estate_id: str) -> dict[str, object]:
        """List artifact metadata and validation findings for an authorized estate."""
        estates.get(estate_id, principal=services.principal())
        records = tuple(
            record
            for item in repository.list_artifacts(estate_id)
            if (record := repository.get_artifact(item.artifact_id)) is not None
        )
        return {"items": [_versioned_payload(item) for item in records]}

    @server.tool(name="estate.artifact.review", annotations=READ_ONLY, structured_output=True)
    def estate_artifact_review(artifact_id: str) -> dict[str, object]:
        """Return current review, artifact revisions, and finding identities."""
        review, artifact = transformations.review_status(
            artifact_id,
            principal=services.principal(),
        )
        return {
            "review": _jsonable(review),
            "artifact": _versioned_payload(artifact),
            "required_acknowledged_finding_ids": sorted(
                finding.rule_id for finding in artifact.value.validation_findings
            ),
        }

    @server.tool(name="estate.artifact.approve", annotations=MUTATING, structured_output=True)
    def estate_artifact_approve(
        artifact_id: str,
        reason: str,
        expected_review_revision: int,
        expected_artifact_revision: int,
        acknowledged_finding_ids: list[str],
    ) -> dict[str, object]:
        """Approve an exact artifact revision after acknowledging every finding."""
        review, artifact = transformations.approve(
            artifact_id,
            principal=services.principal(),
            reason=reason,
            expected_review_revision=expected_review_revision,
            expected_artifact_revision=expected_artifact_revision,
            acknowledged_finding_ids=acknowledged_finding_ids,
        )
        return {
            "review": _jsonable(review),
            "artifact": _versioned_payload(artifact),
        }

    @server.tool(name="estate.evaluation.list", annotations=READ_ONLY, structured_output=True)
    def estate_evaluation_list(
        estate_id: str,
        recommendation_run_id: str,
    ) -> dict[str, object]:
        """Generate up to 20 distinct source-grounded evaluation questions."""
        result = evaluation_sets.generate(
            estate_id,
            recommendation_run_id,
            principal=services.principal(),
        )
        return result.model_dump(mode="json")

    @server.resource(
        "estate://documents/{estate_id}/{document_id}/{source_version}",
        mime_type="text/plain",
    )
    def estate_document_resource(
        estate_id: str,
        document_id: str,
        source_version: str,
    ) -> str:
        """Return normalized text for the exact current source version."""
        estates.get(estate_id, principal=services.principal())
        document = repository.get_document(document_id)
        if (
            document is None
            or document.value.estate_id != estate_id
            or document.value.deleted
        ):
            raise KeyError(f"Estate document does not exist: {document_id}")
        if document.value.source_version != source_version:
            raise ValueError("Requested source version is not current")
        return repository.load_document_content(document_id, source_version)

    @server.resource(
        "estate://artifacts/{artifact_id}/preview",
        mime_type="text/html",
    )
    def estate_artifact_preview_resource(artifact_id: str) -> bytes:
        """Return hash-verified generated HTML to an authorized reviewer."""
        return transformations.preview(artifact_id, principal=services.principal())

    @server.resource(
        "estate://artifacts/{artifact_id}/content",
        mime_type="text/html",
    )
    def estate_artifact_content_resource(artifact_id: str) -> bytes:
        """Return exact hash-verified bytes for an approved artifact."""
        return transformations.content(artifact_id, principal=services.principal())

    return server


def _jsonable(value: object) -> dict[str, object]:
    payload = to_jsonable_python(value)
    if not isinstance(payload, dict):
        raise TypeError("MCP response value must serialize to an object")
    return payload


def _versioned_payload(record: VersionedRecord[RecordT]) -> dict[str, object]:
    return {"value": _jsonable(record.value), "revision": record.revision}
