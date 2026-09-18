"""End-to-end HTTP contracts for live knowledge-estate workflows."""

from __future__ import annotations

import asyncio
import base64
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast

from fastapi.testclient import TestClient
from mcp.shared.memory import create_connected_server_and_client_session
from mcp.types import CallToolResult
from pydantic import AnyUrl

from shaper.application.artifacts import EstateTransformationService, HtmlArtifactRenderer
from shaper.application.assessment import DocumentAssessmentService, EstateAssessmentService
from shaper.application.decisions import TransformationDecisionService
from shaper.application.document_findings import BASELINE_CHECK_CODES, DOCUMENT_CHECK_CODES
from shaper.application.estates import (
    EstateDiscoveryService,
    EstateInventoryService,
    EstateRecommendationService,
    EstateService,
    EstateSourceService,
)
from shaper.application.evaluation_sets import EvaluationSetService, suggested_evaluations
from shaper.application.jobs import CompileJobService, InMemoryJobStore
from shaper.application.orchestration import (
    AgentReadinessAgent,
    AssessmentAgent,
    GovernanceAgent,
    KnowledgeAgent,
    KnowledgeTransformationOrchestrator,
    TransformationAgent,
)
from shaper.application.ports import ModelResult
from shaper.application.query import QueryResult
from shaper.application.review import ReviewService
from shaper.application.token_estimation import TokenEstimator
from shaper.application.validation import DeterministicValidator
from shaper.domain import CollectionRole, Principal
from shaper.infrastructure.archive import ZipArchiveExpander
from shaper.infrastructure.compilation import SQLiteReviewStore
from shaper.infrastructure.parsers import SupportedDocumentParser
from shaper.infrastructure.sqlite import SQLiteEstateRepository, SQLiteStore
from shaper.interfaces.http import HttpServices, create_app
from shaper.interfaces.mcp_server import McpServices, create_mcp_server

NOW = datetime.now(UTC) + timedelta(seconds=1)


class Authenticator:
    """Return one fully authorized test principal."""

    def authenticate(self, token: str) -> Principal:
        if token != "valid":
            raise PermissionError("Invalid token")
        return Principal(
            principal_id="person-1",
            tenant_id="tenant-1",
            collection_roles={
                "collection-1": frozenset(
                    {
                        CollectionRole.ADMIN,
                        CollectionRole.COMPILE,
                        CollectionRole.QUERY,
                        CollectionRole.REVIEW,
                    }
                )
            },
        )


class CleanScanner:
    """Accept non-empty test content."""

    def scan(self, content: bytes) -> str:
        if not content:
            raise ValueError("Empty content")
        return "clean"


class GroundedModel:
    """Return one candidate grounded in the supplied source span."""

    def generate(
        self,
        *,
        system_prompt: str,
        prompt: str,
        schema: dict[str, object],
        max_output_tokens: int | None = None,
    ) -> ModelResult:
        del system_prompt, schema, max_output_tokens
        span = json.loads(prompt)["source"][0]
        return ModelResult(
            payload={
                "status": "candidate",
                "canonical_questions": ["What does the policy require?"],
                "answer": span["text"],
                "claims": [{"text": span["text"], "span_ids": [span["span_id"]]}],
                "confidence": 0.9,
            },
            response_id="response-1",
            input_tokens=12,
            output_tokens=8,
        )


class EmptyQuery:
    """Minimal query gateway for estate-focused MCP tests."""

    release_id = "release-1"

    def query(
        self,
        text: str,
        *,
        principal: Principal,
        limit: int = 10,
    ) -> tuple[QueryResult, ...]:
        del text, principal, limit
        return ()

    def explain(self, unit_id: str, *, principal: Principal) -> dict[str, object]:
        del unit_id, principal
        raise KeyError("Unit does not exist")


def test_given_substantive_source_when_evaluations_generated_then_twenty_are_distinct() -> None:
    source = "\n\n".join(
        f"## Rule {index}\n\nEmployees must complete requirement {index} before approval."
        for index in range(1, 31)
    )

    suggestions = suggested_evaluations(
        "recommendation-1",
        "document-1",
        "a" * 64,
        "Leave policy",
        source,
    )

    assert len(suggestions) == 20
    assert len({item.query for item in suggestions}) == 20
    assert all(item.ground_truth in source for item in suggestions)
    assert all(item.context == item.ground_truth for item in suggestions)
    assert all("score" not in item.model_dump() for item in suggestions)


def _client(
    path: Path,
) -> tuple[TestClient, SQLiteStore, SQLiteEstateRepository, HttpServices]:
    store = SQLiteStore(path)
    store.connect()
    store.migrate()
    repository = SQLiteEstateRepository(store)
    parser = SupportedDocumentParser()
    assessments = EstateAssessmentService()
    orchestrator = KnowledgeTransformationOrchestrator(
        assessments=assessments,
        assessment_agent=AssessmentAgent(),
        knowledge_agent=KnowledgeAgent(),
        transformation_agent=TransformationAgent(),
        governance_agent=GovernanceAgent(),
        agent_readiness_agent=AgentReadinessAgent(),
    )
    reviews = ReviewService(SQLiteReviewStore(store))
    services = HttpServices(
        jobs=CompileJobService(InMemoryJobStore()),
        authenticator=Authenticator(),
        estates=EstateService(repository, clock=lambda: NOW),
        estate_sources=EstateSourceService(repository, clock=lambda: NOW),
        estate_inventory=EstateInventoryService(
            repository,
            parser=parser,
            clock=lambda: NOW,
        ),
        discovery=EstateDiscoveryService(
            repository,
            documents=DocumentAssessmentService(),
            orchestrator=orchestrator,
            clock=lambda: NOW,
        ),
        recommendations=EstateRecommendationService(
            repository,
            transformation_agent=TransformationAgent(),
            estimator=TokenEstimator(model_deployment="test-model"),
            clock=lambda: NOW,
        ),
        decisions=TransformationDecisionService(
            repository,
            clock=lambda: NOW,
        ),
        transformations=EstateTransformationService(
            repository,
            model=GroundedModel(),
            validator=DeterministicValidator(),
            reviews=reviews,
            renderer=HtmlArtifactRenderer(),
            clock=lambda: NOW,
        ),
        evaluation_sets=EvaluationSetService(repository),
        estate_repository=repository,
        archive_expander=ZipArchiveExpander(CleanScanner()),
        malware_scanner=CleanScanner(),
    )
    client = TestClient(create_app(services))
    return (
        client,
        store,
        repository,
        services,
    )


def _structured(result: CallToolResult) -> dict[str, object]:
    payload = result.structuredContent
    assert isinstance(payload, dict)
    return payload


def test_given_staged_document_when_mcp_workflow_runs_then_approved_bytes_are_available(
    tmp_path: Path,
) -> None:
    client, store, repository, http_services = _client(tmp_path / "estate-mcp.db")
    assert http_services.estates is not None
    assert http_services.estate_sources is not None
    assert http_services.discovery is not None
    assert http_services.recommendations is not None
    assert http_services.decisions is not None
    assert http_services.transformations is not None
    assert http_services.evaluation_sets is not None
    server = create_mcp_server(
        McpServices(
            jobs=http_services.jobs,
            query=EmptyQuery(),
            principal=lambda: Authenticator().authenticate("valid"),
            estates=http_services.estates,
            estate_sources=http_services.estate_sources,
            discovery=http_services.discovery,
            recommendations=http_services.recommendations,
            decisions=http_services.decisions,
            transformations=http_services.transformations,
            estate_repository=repository,
            evaluation_sets=http_services.evaluation_sets,
        )
    )

    async def run_workflow() -> None:
        async with create_connected_server_and_client_session(server._mcp_server) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = {tool.name for tool in tools.tools}
            assert {
                "knowledge.query",
                "knowledge.explain",
                "knowledge.compile",
                "knowledge.job_status",
                "estate.assessment_checks",
                "estate.list",
                "estate.get",
                "estate.create",
                "estate.update",
                "estate.source.list",
                "estate.source.register",
                "estate.document.list",
                "estate.run.list",
                "estate.discovery.start",
                "estate.discovery.reports",
                "estate.recommendation.start",
                "estate.proposal.list",
                "estate.proposal.decide",
                "estate.decision.list",
                "estate.transformation.start",
                "estate.artifact.list",
                "estate.artifact.review",
                "estate.artifact.approve",
                "estate.evaluation.list",
            } <= names
            transform_tool = next(
                tool for tool in tools.tools if tool.name == "estate.transformation.start"
            )
            assert transform_tool.annotations is not None
            assert transform_tool.annotations.idempotentHint is False

            created = _structured(
                await session.call_tool(
                    "estate.create",
                    {
                        "collection_id": "collection-1",
                        "name": "MCP policy estate",
                        "description": "MCP parity test",
                        "generate_evaluations": True,
                    },
                )
            )
            estate_id = str(created["value"]["estate_id"])  # type: ignore[index]
            upload = client.post(
                f"/v1/estates/{estate_id}/uploads",
                headers={"Authorization": "Bearer " + "valid"},
                files={
                    "files": (
                        "leave-policy.md",
                        (
                            b"# Leave policy\n\nEmployees must request annual leave "
                            b"from their manager."
                        ),
                        "text/markdown",
                    )
                },
            )
            assert upload.status_code == 201, upload.text
            document = upload.json()["documents"][0]["value"]

            discovery_result = _structured(
                await session.call_tool("estate.discovery.start", {"estate_id": estate_id})
            )
            assert discovery_result["reports"]
            report = discovery_result["reports"][0]  # type: ignore[index]
            assert report["findings"]
            assert all(finding["agent_impact"] for finding in report["findings"])
            assert "readiness_score" not in report
            discovery_run_id = discovery_result["run"]["value"]["run_id"]  # type: ignore[index]

            recommendation_result = _structured(
                await session.call_tool(
                    "estate.recommendation.start",
                    {
                        "estate_id": estate_id,
                        "discovery_run_id": discovery_run_id,
                        "document_ids": [document["document_id"]],
                    },
                )
            )
            recommendation_run_id = recommendation_result["run"]["value"]["run_id"]  # type: ignore[index]
            proposal = recommendation_result["proposals"][0]  # type: ignore[index]

            evaluations = _structured(
                await session.call_tool(
                    "estate.evaluation.list",
                    {
                        "estate_id": estate_id,
                        "recommendation_run_id": recommendation_run_id,
                    },
                )
            )
            assert 0 < len(evaluations["items"]) <= 20  # type: ignore[arg-type]
            assert "score" not in json.dumps(evaluations)

            await session.call_tool(
                "estate.proposal.decide",
                {
                    "recommendation_id": proposal["recommendation_id"],
                    "outcome": "approve",
                    "reason": "Approved through MCP parity test",
                    "expected_current_decision_id": None,
                },
            )
            transformation = _structured(
                await session.call_tool(
                    "estate.transformation.start",
                    {
                        "estate_id": estate_id,
                        "recommendation_id": proposal["recommendation_id"],
                        "enforce_preservation_checks": False,
                    },
                )
            )
            assert transformation["run"]["value"]["status"] == "completed"  # type: ignore[index]

            artifacts = _structured(
                await session.call_tool("estate.artifact.list", {"estate_id": estate_id})
            )
            artifact = artifacts["items"][0]  # type: ignore[index]
            artifact_id = artifact["value"]["artifact_id"]
            review = _structured(
                await session.call_tool(
                    "estate.artifact.review",
                    {"artifact_id": artifact_id},
                )
            )
            review_record = cast(dict[str, object], review["review"])
            artifact_record = cast(dict[str, object], review["artifact"])
            preview = await session.read_resource(
                AnyUrl(f"estate://artifacts/{artifact_id}/preview")
            )
            assert preview.contents

            approval = _structured(
                await session.call_tool(
                    "estate.artifact.approve",
                    {
                        "artifact_id": artifact_id,
                        "reason": "Grounding and findings reviewed",
                        "expected_review_revision": review_record["revision"],
                        "expected_artifact_revision": artifact_record["revision"],
                        "acknowledged_finding_ids": review[
                            "required_acknowledged_finding_ids"
                        ],
                    },
                )
            )
            assert approval["artifact"]["value"]["status"] == "approved"  # type: ignore[index]

            approved = await session.read_resource(
                AnyUrl(f"estate://artifacts/{artifact_id}/content")
            )
            assert approved.contents
            blob = approved.contents[0]
            assert hasattr(blob, "blob")
            decoded = base64.b64decode(blob.blob)
            rest_download = client.get(
                f"/v1/artifacts/{artifact_id}/download",
                headers={"Authorization": "Bearer " + "valid"},
            )
            assert rest_download.status_code == 200
            assert decoded == rest_download.content

    try:
        asyncio.run(run_workflow())
    finally:
        store.close()


def test_given_uploaded_policy_when_workflow_approved_then_html_is_published(
    tmp_path: Path,
) -> None:
    client, store, repository, _services = _client(tmp_path / "estate-http.db")
    headers = {"Authorization": "Bearer valid"}
    try:
        estate_response = client.post(
            "/v1/estates",
            headers=headers,
            json={
                "collection_id": "collection-1",
                "name": "Policy estate",
                "description": "Current people policies",
                "artifact_name_template": "shaper_{source_stem}.html",
                "generate_evaluations": True,
            },
        )
        assert estate_response.status_code == 201
        estate_id = estate_response.json()["value"]["estate_id"]

        upload_response = client.post(
            f"/v1/estates/{estate_id}/uploads",
            headers=headers,
            files={
                "files": (
                    "leave-policy.md",
                    b"# Leave policy\n\nEmployees must request annual leave from their manager.",
                    "text/markdown",
                )
            },
        )
        assert upload_response.status_code == 201, upload_response.text
        uploaded_document = upload_response.json()["documents"][0]["value"]
        document_id = uploaded_document["document_id"]
        source_version = uploaded_document["source_version"]

        content_response = client.get(
            f"/v1/estates/{estate_id}/documents/{document_id}/content",
            params={"source_version": source_version},
            headers=headers,
        )
        stale_content_response = client.get(
            f"/v1/estates/{estate_id}/documents/{document_id}/content",
            params={"source_version": "0" * 64},
            headers=headers,
        )
        assert content_response.status_code == 200
        assert content_response.text.startswith("# Leave policy")
        assert stale_content_response.status_code == 422
        assert (
            client.get(
                f"/v1/estates/{estate_id}/documents/missing-document/content",
                params={"source_version": source_version},
                headers=headers,
            ).status_code
            == 404
        )

        other_estate = client.post(
            "/v1/estates",
            headers=headers,
            json={
                "collection_id": "collection-1",
                "name": "Other estate",
                "description": "",
                "artifact_name_template": "shaper_{source_stem}.html",
            },
        ).json()
        assert (
            client.get(
                f"/v1/estates/{other_estate['value']['estate_id']}/documents/{document_id}/content",
                params={"source_version": source_version},
                headers=headers,
            ).status_code
            == 404
        )

        discovery_response = client.post(
            f"/v1/estates/{estate_id}/discovery-runs",
            headers=headers,
            json={},
        )
        assert discovery_response.status_code == 200, discovery_response.text
        discovery_run_id = discovery_response.json()["run"]["value"]["run_id"]
        report = discovery_response.json()["reports"][0]
        assert "readiness_score" not in report
        assert len(report["checks_completed"]) == 31
        assert all(finding["evidence"] for finding in report["findings"])
        assert all(finding["agent_impact"] for finding in report["findings"])

        source_response = client.get(
            f"/v1/estates/{estate_id}/documents/{document_id}/source",
            params={"source_version": source_version},
            headers=headers,
        )
        assert source_response.status_code == 200
        assert source_response.content == (
            b"# Leave policy\n\nEmployees must request annual leave from their manager."
        )
        assert source_response.headers["content-disposition"].startswith("attachment;")

        recommendation_response = client.post(
            f"/v1/estates/{estate_id}/recommendation-runs",
            headers=headers,
            json={"discovery_run_id": discovery_run_id, "ids": [document_id]},
        )
        assert recommendation_response.status_code == 200
        proposal = recommendation_response.json()["proposals"][0]
        assert proposal["token_estimate"]["enforced_maximum"] > 0
        assert "/100" not in proposal["rationale"]
        assert "content finding" in proposal["rationale"]
        assert "effort" not in proposal["rationale"]

        evaluation_response = client.get(
            f"/v1/estates/{estate_id}/evaluations",
            params={
                "recommendation_run_id": recommendation_response.json()["run"]["value"][
                    "run_id"
                ]
            },
            headers=headers,
        )
        assert evaluation_response.status_code == 200
        assert evaluation_response.json()["items"]
        assert len(evaluation_response.json()["items"]) <= 20
        assert "score" not in evaluation_response.text

        decision_response = client.put(
            f"/v1/proposals/{proposal['recommendation_id']}/decision",
            headers=headers,
            json={
                "outcome": "approve",
                "reason": "Approved for test transformation",
                "expected_current_decision_id": None,
            },
        )
        assert decision_response.status_code == 200
        assert decision_response.json()["outcome"] == "approve"
        assert decision_response.json()["document_id"] == document_id

        transformation_response = client.post(
            f"/v1/estates/{estate_id}/transformation-runs/stream",
            headers=headers,
            json={"ids": [proposal["recommendation_id"]]},
        )
        assert transformation_response.status_code == 200
        transformation_events = [
            json.loads(line) for line in transformation_response.text.splitlines() if line.strip()
        ]
        assert transformation_events[-1]["type"] == "run_completed"
        assert transformation_events[-1]["status"] == "completed"
        assert {
            event.get("check")
            for event in transformation_events
            if event["type"] == "check_updated"
        } == {"reshape", "source_preservation", "grounding", "quality"}

        artifacts_response = client.get(
            f"/v1/estates/{estate_id}/artifacts",
            headers=headers,
        )
        artifact = artifacts_response.json()["items"][0]
        artifact_id = artifact["value"]["artifact_id"]
        assert artifact["value"]["filename"] == "shaper_leave-policy.html"
        assert "evaluation" not in artifact["value"]
        preview_response = client.get(
            f"/v1/artifacts/{artifact_id}/preview",
            headers=headers,
        )
        assert preview_response.status_code == 200
        assert "<!doctype html>" in preview_response.text
        review_response = client.get(
            f"/v1/artifacts/{artifact_id}/review",
            headers=headers,
        )
        assert review_response.status_code == 200
        review_status = review_response.json()
        assert review_status["artifact"]["revision"] == artifact["revision"]
        assert (
            client.get(
                f"/v1/artifacts/{artifact_id}/content",
                headers=headers,
            ).status_code
            == 403
        )
        assert (
            client.get(
                f"/v1/artifacts/{artifact_id}/download",
                headers=headers,
            ).status_code
            == 403
        )
        assert "evaluation" not in artifact["value"]

        approval_response = client.post(
            f"/v1/artifacts/{artifact_id}/approve",
            headers=headers,
            json={
                "reason": "Grounding verified",
                "expected_review_revision": review_status["review"]["revision"],
                "expected_artifact_revision": review_status["artifact"]["revision"],
                "acknowledged_finding_ids": review_status[
                    "required_acknowledged_finding_ids"
                ],
            },
        )
        assert approval_response.status_code == 200

        content_response = client.get(
            f"/v1/artifacts/{artifact_id}/content",
            headers=headers,
        )
        assert content_response.status_code == 200
        assert "<!doctype html>" in content_response.text
        assert "Employees must request annual leave" in content_response.text
        download_response = client.get(
            f"/v1/artifacts/{artifact_id}/download",
            headers=headers,
        )
        assert download_response.status_code == 200
        assert download_response.content == content_response.content
        assert download_response.headers["content-type"].startswith("text/html")
        assert (
            download_response.headers["content-disposition"]
            == "attachment; filename*=UTF-8''shaper_leave-policy.html"
        )
        assert download_response.headers["x-content-type-options"] == "nosniff"

        store.connection.execute(
            "DELETE FROM records WHERE category = 'document_source' AND record_id = ?",
            (f"{document_id}:{source_version}",),
        )
        legacy_documents = client.get(
            f"/v1/estates/{estate_id}/documents",
            headers=headers,
        )
        assert legacy_documents.json()["items"][0]["source_retained"] is False
        legacy_source = client.get(
            f"/v1/estates/{estate_id}/documents/{document_id}/source",
            params={"source_version": source_version},
            headers=headers,
        )
        assert legacy_source.status_code == 409
        assert "re-upload" in legacy_source.json()["detail"]

        document_record = repository.get_document(document_id)
        assert document_record is not None
        removal_response = client.delete(
            f"/v1/estates/{estate_id}/documents/{document_id}",
            params={"expected_revision": document_record.revision},
            headers=headers,
        )
        assert removal_response.status_code == 200
        assert removal_response.json()["value"]["deleted"] is True
        assert removal_response.json()["revision"] == document_record.revision + 1
        assert (
            client.get(
                f"/v1/estates/{estate_id}/documents/{document_id}/content",
                params={"source_version": source_version},
                headers=headers,
            ).status_code
            == 404
        )
    finally:
        store.close()


def test_given_estate_documents_when_listed_then_current_assessment_coverage_is_reported(
    tmp_path: Path,
) -> None:
    client, store, _repository, _services = _client(tmp_path / "estate-summary-http.db")
    headers = {"Authorization": "Bearer " + "valid"}
    try:
        created = client.post(
            "/v1/estates",
            headers=headers,
            json={
                "collection_id": "collection-1",
                "name": "Assessment coverage",
                "description": "",
                "artifact_name_template": "shaper_{source_stem}.html",
            },
        ).json()
        estate_id = created["value"]["estate_id"]

        empty_summary = client.get(
            "/v1/estates",
            params={"collection_id": "collection-1"},
            headers=headers,
        ).json()["items"][0]
        assert empty_summary["document_count"] == 0
        assert empty_summary["assessed_document_count"] == 0
        assert empty_summary["assessment_status"] == "no_documents"

        first_upload = client.post(
            f"/v1/estates/{estate_id}/uploads",
            headers=headers,
            files={
                "files": (
                    "first-policy.md",
                    b"# First policy\n\nEmployees must follow the published steps.",
                    "text/markdown",
                )
            },
        )
        assert first_upload.status_code == 201
        unassessed_summary = client.get(
            "/v1/estates",
            params={"collection_id": "collection-1"},
            headers=headers,
        ).json()["items"][0]
        assert unassessed_summary["document_count"] == 1
        assert unassessed_summary["assessed_document_count"] == 0
        assert unassessed_summary["assessment_status"] == "not_assessed"

        discovery = client.post(
            f"/v1/estates/{estate_id}/discovery-runs",
            headers=headers,
            json={},
        )
        assert discovery.status_code == 200
        assessed_summary = client.get(
            "/v1/estates",
            params={"collection_id": "collection-1"},
            headers=headers,
        ).json()["items"][0]
        assert assessed_summary["assessed_document_count"] == 1
        assert assessed_summary["assessment_status"] == "assessed"

        second_upload = client.post(
            f"/v1/estates/{estate_id}/uploads",
            headers=headers,
            files={
                "files": (
                    "second-policy.md",
                    b"# Second policy\n\nManagers should review requests.",
                    "text/markdown",
                )
            },
        )
        assert second_upload.status_code == 201
        partial_summary = client.get(
            "/v1/estates",
            params={"collection_id": "collection-1"},
            headers=headers,
        ).json()["items"][0]
        assert partial_summary["document_count"] == 2
        assert partial_summary["assessed_document_count"] == 1
        assert partial_summary["assessment_status"] == "partially_assessed"
    finally:
        store.close()


def test_given_authenticated_user_when_checks_requested_then_full_catalog_is_returned(
    tmp_path: Path,
) -> None:
    client, store, _repository, _services = _client(tmp_path / "assessment-checks-http.db")
    try:
        response = client.get(
            "/v1/assessment-checks",
            headers={"Authorization": "Bearer " + "valid"},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["method"] == "deterministic"
        assert payload["total"] == 31
        assert {item["code"] for item in payload["items"]} == set(
            DOCUMENT_CHECK_CODES + BASELINE_CHECK_CODES
        )
        assert all(item["what_it_checks"] for item in payload["items"])
        assert all(item["agent_impact"] for item in payload["items"])
    finally:
        store.close()


def test_given_active_estate_when_archived_and_purged_then_lifecycle_is_enforced(
    tmp_path: Path,
) -> None:
    # Arrange
    client, store, _repository, _services = _client(tmp_path / "estate-lifecycle-http.db")
    headers = {"Authorization": "Bearer " + "valid"}
    try:
        created = client.post(
            "/v1/estates",
            headers=headers,
            json={
                "collection_id": "collection-1",
                "name": "Retention estate",
                "description": "",
                "artifact_name_template": "shaper_{source_stem}.html",
            },
        ).json()
        estate_id = created["value"]["estate_id"]

        # Act
        archived = client.post(
            f"/v1/estates/{estate_id}/archive",
            headers=headers,
            json={"expected_revision": created["revision"]},
        )
        rejected_mutation = client.post(
            f"/v1/estates/{estate_id}/sources",
            headers=headers,
            json={
                "kind": "url",
                "display_name": "Blocked source",
                "locator": "https://example.com/blocked",
            },
        )
        purged = client.post(
            f"/v1/estates/{estate_id}/purge",
            headers=headers,
            json={"confirmation": "PURGE Retention estate", "reason": "Retention expired"},
        )
        missing = client.get(f"/v1/estates/{estate_id}", headers=headers)

        # Assert
        assert archived.status_code == 200
        assert archived.json()["value"]["status"] == "archived"
        assert rejected_mutation.status_code == 409
        assert purged.status_code == 200
        assert purged.json()["purged"] is True
        assert missing.status_code == 404
    finally:
        store.close()
