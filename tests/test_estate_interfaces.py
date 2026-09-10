"""End-to-end HTTP contracts for live knowledge-estate workflows."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient

from shaper.application.artifacts import EstateTransformationService, HtmlArtifactRenderer
from shaper.application.assessment import DocumentAssessmentService, EstateAssessmentService
from shaper.application.decisions import TransformationDecisionService
from shaper.application.estates import (
    EstateDiscoveryService,
    EstateInventoryService,
    EstateRecommendationService,
    EstateService,
    EstateSourceService,
)
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
from shaper.application.review import ReviewService
from shaper.application.token_estimation import TokenEstimator
from shaper.application.validation import DeterministicValidator
from shaper.domain import CollectionRole, Principal
from shaper.infrastructure.archive import ZipArchiveExpander
from shaper.infrastructure.compilation import SQLiteReviewStore
from shaper.infrastructure.parsers import SupportedDocumentParser
from shaper.infrastructure.sqlite import SQLiteEstateRepository, SQLiteStore
from shaper.interfaces.http import HttpServices, create_app

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

    def generate(self, *, prompt: str, schema: dict[str, object]) -> ModelResult:
        del schema
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


def _client(path: Path) -> tuple[TestClient, SQLiteStore]:
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
    return (
        TestClient(
            create_app(
                HttpServices(
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
                    estate_repository=repository,
                    archive_expander=ZipArchiveExpander(CleanScanner()),
                )
            )
        ),
        store,
    )


def test_given_uploaded_policy_when_workflow_approved_then_html_is_published(
    tmp_path: Path,
) -> None:
    client, store = _client(tmp_path / "estate-http.db")
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
            },
        )
        assert estate_response.status_code == 201
        estate_id = estate_response.json()["value"]["estate_id"]

        upload_response = client.post(
            f"/v1/estates/{estate_id}/uploads",
            headers=headers,
            files={
                "files": (
                    "leave-policy.txt",
                    b"Employees must request annual leave from their manager.",
                    "text/plain",
                )
            },
        )
        assert upload_response.status_code == 201, upload_response.text
        document_id = upload_response.json()["documents"][0]["value"]["document_id"]

        discovery_response = client.post(
            f"/v1/estates/{estate_id}/discovery-runs",
            headers=headers,
            json={},
        )
        assert discovery_response.status_code == 200, discovery_response.text
        discovery_run_id = discovery_response.json()["run"]["value"]["run_id"]
        assert discovery_response.json()["reports"][0]["readiness_score"] >= 0

        recommendation_response = client.post(
            f"/v1/estates/{estate_id}/recommendation-runs",
            headers=headers,
            json={"discovery_run_id": discovery_run_id, "ids": [document_id]},
        )
        assert recommendation_response.status_code == 200
        proposal = recommendation_response.json()["proposals"][0]
        assert proposal["token_estimate"]["enforced_maximum"] > 0

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

        transformation_response = client.post(
            f"/v1/estates/{estate_id}/transformation-runs",
            headers=headers,
            json={"ids": [proposal["recommendation_id"]]},
        )
        assert transformation_response.status_code == 200
        assert transformation_response.json()["run"]["value"]["status"] == "completed"

        artifacts_response = client.get(
            f"/v1/estates/{estate_id}/artifacts",
            headers=headers,
        )
        artifact = artifacts_response.json()["items"][0]
        artifact_id = artifact["value"]["artifact_id"]
        assert artifact["value"]["filename"] == "shaper_leave-policy.html"

        approval_response = client.post(
            f"/v1/artifacts/{artifact_id}/approve",
            headers=headers,
            json={
                "reason": "Grounding verified",
                "expected_review_revision": 1,
                "expected_artifact_revision": artifact["revision"],
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
    finally:
        store.close()
