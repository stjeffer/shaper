"""HTTP and MCP interface contract tests."""

from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient
from mcp.shared.memory import create_connected_server_and_client_session

from shaper.application.assessment import EstateAssessmentService
from shaper.application.demo import DemoAnalysisService
from shaper.application.jobs import CompileJobService, InMemoryJobStore
from shaper.application.orchestration import (
    AgentReadinessAgent,
    AssessmentAgent,
    GovernanceAgent,
    KnowledgeAgent,
    KnowledgeTransformationOrchestrator,
    TransformationAgent,
)
from shaper.domain import CollectionRole, Principal, SourceDocument
from shaper.infrastructure.uploads import FileUploadStore
from shaper.interfaces.hosted import create_hosted_app
from shaper.interfaces.http import HttpServices, create_app
from shaper.interfaces.mcp_server import McpServices, create_mcp_server
from tests.test_query import principal as query_principal
from tests.test_query import service as query_service


class Authenticator:
    """Deterministic HTTP authenticator."""

    def __init__(self, principal: Principal) -> None:
        self._principal = principal

    def authenticate(self, token: str) -> Principal:
        if token != "valid":
            raise PermissionError("invalid token")
        return self._principal


class CleanScanner:
    """Deterministic clean upload scanner."""

    def scan(self, content: bytes) -> str:
        assert content
        return "clean"


def compile_principal() -> Principal:
    """Return a principal with all interface roles."""
    return Principal(
        principal_id="person-1",
        tenant_id="tenant-1",
        collection_roles={
            "collection-1": frozenset(
                {CollectionRole.COMPILE, CollectionRole.QUERY, CollectionRole.REVIEW}
            )
        },
    )


def platform_orchestrator(
    assessments: EstateAssessmentService,
) -> KnowledgeTransformationOrchestrator:
    """Create the deterministic platform orchestrator."""
    return KnowledgeTransformationOrchestrator(
        assessments=assessments,
        assessment_agent=AssessmentAgent(),
        knowledge_agent=KnowledgeAgent(),
        transformation_agent=TransformationAgent(),
        governance_agent=GovernanceAgent(),
        agent_readiness_agent=AgentReadinessAgent(),
    )


def test_given_compile_request_when_authorized_then_job_is_accepted() -> None:
    # Arrange
    app = create_app(
        HttpServices(
            jobs=CompileJobService(InMemoryJobStore()),
            authenticator=Authenticator(compile_principal()),
        )
    )
    client = TestClient(app)

    # Act
    response = client.post(
        "/v1/jobs",
        headers={"Authorization": "Bearer valid"},
        json={
            "source": {
                "tenant_id": "tenant-1",
                "collection_id": "collection-1",
                "kind": "upload",
                "locator": "asset-1",
            },
            "output": {"kind": "filesystem", "root_id": "local", "relative_path": ""},
            "idempotency_key": "request-1",
            "model_token_budget": 1000,
        },
    )

    # Assert
    assert response.status_code == 202
    assert response.json()["state"] == "queued"


def test_given_profiles_when_authorized_then_estate_assessment_is_returned() -> None:
    # Arrange
    client = TestClient(
        create_app(
            HttpServices(
                jobs=CompileJobService(InMemoryJobStore()),
                authenticator=Authenticator(compile_principal()),
                assessments=EstateAssessmentService(),
            )
        )
    )

    # Act
    response = client.post(
        "/v1/assessments",
        headers={"Authorization": "Bearer " + "valid"},
        json={
            "collection_id": "collection-1",
            "assessed_at": "2026-09-10T08:00:00Z",
            "profiles": [
                {
                    "document_id": "policy-1",
                    "title": "Travel policy",
                    "text": "# Travel\n\nEmployees must submit expenses.",
                    "modified_at": "2026-08-01T08:00:00Z",
                    "owner": None,
                    "metadata": {},
                    "topic": "Travel",
                    "authority": "unknown",
                    "faq_count": 0,
                    "procedure_step_count": 0,
                    "assertions": [],
                }
            ],
        },
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["document_count"] == 1
    assert response.json()["coverage"]["unavailable_metric_count"] > 0
    assert "not accuracy" in response.json()["limitations"][0]


def test_given_public_demo_when_requested_then_real_platform_analysis_is_returned() -> None:
    # Arrange
    assessments = EstateAssessmentService()
    orchestrator = platform_orchestrator(assessments)
    client = TestClient(
        create_app(
            HttpServices(
                jobs=CompileJobService(InMemoryJobStore()),
                authenticator=Authenticator(compile_principal()),
                assessments=assessments,
                orchestrator=orchestrator,
                demo_analysis=DemoAnalysisService(orchestrator),
            )
        )
    )

    # Act
    response = client.get("/v1/demo/analysis")
    repeated_response = client.get("/v1/demo/analysis")

    # Assert
    assert response.status_code == 200
    assert repeated_response.json() == response.json()
    body = response.json()
    assert body["sample_kind"] == "server_owned_fixed_sample"
    assert [source["title"] for source in body["sources"]] == [
        "Travel Policy v4",
        "EMEA Travel Rules",
        "New Starter FAQ",
    ]
    assert body["sources"][0]["authority"] == "authoritative"
    analysis = body["analysis"]
    assert analysis["collection_id"] == "faqifier"
    assert analysis["knowledge"]["topics"]
    assert analysis["transformation"]["proposals"]
    assert analysis["transformation"]["proposal_only"]
    assert not analysis["governance"]["recurring_monitoring_configured"]


def test_given_profiles_when_platform_analyzed_then_agent_results_share_assessment() -> None:
    # Arrange
    assessments = EstateAssessmentService()
    client = TestClient(
        create_app(
            HttpServices(
                jobs=CompileJobService(InMemoryJobStore()),
                authenticator=Authenticator(compile_principal()),
                assessments=assessments,
                orchestrator=platform_orchestrator(assessments),
            )
        )
    )
    payload = {
        "collection_id": "collection-1",
        "assessed_at": "2026-09-10T08:00:00Z",
        "profiles": [
            {
                "document_id": "policy-1",
                "title": "Travel policy",
                "text": "# Travel\n\nEmployees must submit expenses.",
                "modified_at": "2026-08-01T08:00:00Z",
                "owner": None,
                "metadata": {},
                "topic": "Travel",
                "authority": "unknown",
                "faq_count": 0,
                "procedure_step_count": 0,
                "assertions": [],
            }
        ],
    }

    # Act
    assessment = client.post(
        "/v1/assessments",
        headers={"Authorization": "Bearer valid"},
        json=payload,
    )
    analysis = client.post(
        "/v1/platform/analyses",
        headers={"Authorization": "Bearer valid"},
        json=payload,
    )
    unauthenticated = client.post("/v1/platform/analyses", json=payload)

    # Assert
    assert assessment.status_code == 200
    assert analysis.status_code == 200
    assert unauthenticated.status_code != 200
    body = analysis.json()
    assert body["assessment_id"] == assessment.json()["assessment_id"]
    assert {
        body[name]["role"]
        for name in (
            "assessment",
            "knowledge",
            "transformation",
            "governance",
            "agent_readiness",
        )
    } == {
        "assessment",
        "knowledge",
        "transformation",
        "governance",
        "agent_readiness",
    }


def test_given_naive_assessment_time_when_requested_then_validation_error_is_returned() -> None:
    # Arrange
    client = TestClient(
        create_app(
            HttpServices(
                jobs=CompileJobService(InMemoryJobStore()),
                authenticator=Authenticator(compile_principal()),
                assessments=EstateAssessmentService(),
            )
        )
    )

    # Act
    response = client.post(
        "/v1/assessments",
        headers={"Authorization": "Bearer " + "valid"},
        json={
            "collection_id": "collection-1",
            "assessed_at": "2026-09-10T08:00:00",
            "profiles": [
                {
                    "document_id": "policy-1",
                    "title": "Travel policy",
                    "text": "Employees must submit expenses.",
                    "modified_at": "2026-08-01T08:00:00Z",
                }
            ],
        },
    )

    # Assert
    assert response.status_code == 422
    assert response.json()["detail"] == "Assessment time must include a timezone"


def test_given_paired_evaluation_when_authorized_then_improvement_report_is_returned() -> None:
    client = TestClient(
        create_app(
            HttpServices(
                jobs=CompileJobService(InMemoryJobStore()),
                authenticator=Authenticator(compile_principal()),
            )
        )
    )

    response = client.post(
        "/v1/evaluations/improvement",
        headers={"Authorization": "Bearer " + "valid"},
        json={
            "collection_id": "collection-1",
            "outcomes": [
                {
                    "case_id": f"case-{index}",
                    "baseline_passed": index < 18,
                    "shaped_passed": index < 24,
                }
                for index in range(30)
            ],
            "dataset_reviewed": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["absolute_improvement_percentage_points"] == 20
    assert response.json()["claim_status"] == "eligible_for_reviewed_claim"


def test_given_assessment_without_compile_role_when_requested_then_forbidden() -> None:
    # Arrange
    caller = Principal(
        principal_id="person-1",
        tenant_id="tenant-1",
        collection_roles={"collection-1": frozenset({CollectionRole.QUERY})},
    )
    client = TestClient(
        create_app(
            HttpServices(
                jobs=CompileJobService(InMemoryJobStore()),
                authenticator=Authenticator(caller),
                assessments=EstateAssessmentService(),
            )
        )
    )

    # Act
    response = client.post(
        "/v1/assessments",
        headers={"Authorization": "Bearer " + "valid"},
        json={
            "collection_id": "collection-1",
            "assessed_at": "2026-09-10T08:00:00Z",
            "profiles": [
                {
                    "document_id": "policy-1",
                    "title": "Policy",
                    "text": "Current policy.",
                    "modified_at": "2026-08-01T08:00:00Z",
                }
            ],
        },
    )

    # Assert
    assert response.status_code == 403


def test_given_unconfigured_assessment_when_requested_then_service_is_unavailable() -> None:
    # Arrange
    client = TestClient(
        create_app(
            HttpServices(
                jobs=CompileJobService(InMemoryJobStore()),
                authenticator=Authenticator(compile_principal()),
            )
        )
    )

    # Act
    response = client.post(
        "/v1/assessments",
        headers={"Authorization": "Bearer " + "valid"},
        json={
            "collection_id": "collection-1",
            "assessed_at": "2026-09-10T08:00:00Z",
            "profiles": [
                {
                    "document_id": "policy-1",
                    "title": "Policy",
                    "text": "Current policy.",
                    "modified_at": "2026-08-01T08:00:00Z",
                }
            ],
        },
    )

    # Assert
    assert response.status_code == 503


def test_given_invalid_bearer_token_when_requested_then_http_returns_unauthorized() -> None:
    # Arrange
    app = create_app(
        HttpServices(
            jobs=CompileJobService(InMemoryJobStore()),
            authenticator=Authenticator(compile_principal()),
        )
    )

    # Act
    response = TestClient(app).get(
        "/v1/jobs/missing",
        headers={"Authorization": "Bearer invalid"},
    )

    # Assert
    assert response.status_code == 401


def test_given_current_release_when_queried_then_http_returns_result_and_explanation(
    source_document: SourceDocument,
) -> None:
    query = query_service(source_document)
    client = TestClient(
        create_app(
            HttpServices(
                jobs=CompileJobService(InMemoryJobStore()),
                authenticator=Authenticator(
                    query_principal(CollectionRole.QUERY),
                ),
                query=query,
            )
        )
    )

    response = client.post(
        "/v1/query",
        headers={"Authorization": "Bearer valid"},
        json={"text": "employees leave"},
    )
    unit_id = response.json()[0]["unit"]["unit_id"]
    explanation = client.get(
        f"/v1/units/{unit_id}/explain",
        headers={"Authorization": "Bearer valid"},
    )

    assert response.status_code == 200
    assert explanation.status_code == 200
    assert explanation.json()["release_id"] == "release-1"


def test_given_clean_document_when_uploaded_then_opaque_asset_is_returned(
    tmp_path: Path,
) -> None:
    client = TestClient(
        create_app(
            HttpServices(
                jobs=CompileJobService(InMemoryJobStore()),
                authenticator=Authenticator(compile_principal()),
                uploads=FileUploadStore(tmp_path, scanner=CleanScanner()),
            )
        )
    )

    response = client.post(
        "/v1/uploads",
        headers={"Authorization": "Bearer valid"},
        data={"collection_id": "collection-1"},
        files={"document": ("policy.txt", b"synthetic policy", "text/plain")},
    )

    assert response.status_code == 201
    assert response.json()["scan_result"] == "clean"
    assert (tmp_path / response.json()["asset_id"] / "content").is_file()


def test_given_failed_dependency_when_ready_then_http_returns_not_ready() -> None:
    app = create_app(
        HttpServices(
            jobs=CompileJobService(InMemoryJobStore()),
            authenticator=Authenticator(compile_principal()),
            readiness=lambda: {"state_store": True, "malware_scanner": False},
        )
    )

    response = TestClient(app).get("/health/ready")

    assert response.status_code == 503
    assert response.json()["detail"]["dependencies"]["malware_scanner"] is False


def test_given_concept_assets_when_hosted_then_prototype_is_served(tmp_path: Path) -> None:
    concept_root = tmp_path / "concept"
    concept_root.mkdir()
    (concept_root / "index.html").write_text("<title>Concept</title>", encoding="utf-8")
    (concept_root / "app.js").write_text("const ready = true;", encoding="utf-8")
    app = create_app(
        HttpServices(
            jobs=CompileJobService(InMemoryJobStore()),
            authenticator=Authenticator(compile_principal()),
            concept_root=concept_root,
        )
    )

    client = TestClient(app)

    assert client.get("/concept/").text == "<title>Concept</title>"
    assert client.get("/concept/app.js").text == "const ready = true;"


def test_given_mcp_server_when_listed_then_only_planned_tools_are_exposed(
    source_document: SourceDocument,
) -> None:
    # Arrange
    server = create_mcp_server(
        McpServices(
            jobs=CompileJobService(InMemoryJobStore()),
            query=query_service(source_document),
            principal=lambda: query_principal(
                CollectionRole.QUERY,
                CollectionRole.COMPILE,
            ),
        )
    )

    # Act
    tools = asyncio.run(server.list_tools())

    # Assert
    assert {tool.name for tool in tools} == {
        "knowledge.compile",
        "knowledge.explain",
        "knowledge.job_status",
        "knowledge.query",
    }


def test_given_mcp_server_when_initialized_then_real_sdk_client_lists_tools(
    source_document: SourceDocument,
) -> None:
    async def use_client() -> set[str]:
        server = create_mcp_server(
            McpServices(
                jobs=CompileJobService(InMemoryJobStore()),
                query=query_service(source_document),
                principal=lambda: query_principal(CollectionRole.QUERY),
            )
        )
        async with create_connected_server_and_client_session(server._mcp_server) as session:
            await session.initialize()
            result = await session.list_tools()
            return {tool.name for tool in result.tools}

    assert asyncio.run(use_client()) == {
        "knowledge.compile",
        "knowledge.explain",
        "knowledge.job_status",
        "knowledge.query",
    }


def test_given_combined_host_when_started_then_http_and_mcp_share_one_lifespan(
    source_document: SourceDocument,
) -> None:
    stopped: list[bool] = []
    mcp_server = create_mcp_server(
        McpServices(
            jobs=CompileJobService(InMemoryJobStore()),
            query=query_service(source_document),
            principal=lambda: query_principal(CollectionRole.QUERY),
        )
    )
    app = create_hosted_app(
        HttpServices(
            jobs=CompileJobService(InMemoryJobStore()),
            authenticator=Authenticator(compile_principal()),
        ),
        mcp_server,
        on_shutdown=lambda: stopped.append(True),
    )

    with TestClient(app) as client:
        assert client.get("/health/live").json() == {"status": "live"}

    assert stopped == [True]
