"""Specialist-agent orchestration tests."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from shaper.application.assessment import EstateAssessmentService
from shaper.application.orchestration import (
    AgentReadinessAgent,
    AssessmentAgent,
    GovernanceAgent,
    KnowledgeAgent,
    KnowledgeTransformationOrchestrator,
    TransformationAgent,
)
from shaper.domain import (
    KnowledgeTransformationAnalysis,
    SpecialistAgentRole,
)
from tests.test_assessment import ASSESSED_AT, travel_estate


def orchestrator(
    assessments: EstateAssessmentService | None = None,
) -> KnowledgeTransformationOrchestrator:
    """Create the deterministic platform orchestrator."""
    return KnowledgeTransformationOrchestrator(
        assessments=assessments or EstateAssessmentService(),
        assessment_agent=AssessmentAgent(),
        knowledge_agent=KnowledgeAgent(),
        transformation_agent=TransformationAgent(),
        governance_agent=GovernanceAgent(),
        agent_readiness_agent=AgentReadinessAgent(),
    )


def test_given_estate_when_analyzed_then_all_specialist_roles_share_evidence() -> None:
    # Act
    analysis = orchestrator().analyze(
        collection_id="policies",
        profiles=travel_estate(),
        assessed_at=ASSESSED_AT,
    )
    results = (
        analysis.assessment,
        analysis.knowledge,
        analysis.transformation,
        analysis.governance,
        analysis.agent_readiness,
    )

    # Assert
    assert {result.role for result in results} == set(SpecialistAgentRole)
    assert {result.assessment_id for result in results} == {analysis.assessment_id}
    assert analysis == orchestrator().analyze(
        collection_id="policies",
        profiles=travel_estate(),
        assessed_at=ASSESSED_AT,
    )


def test_transformation_agent_returns_proposals_without_execution() -> None:
    # Act
    analysis = orchestrator().analyze(
        collection_id="policies",
        profiles=travel_estate(),
        assessed_at=ASSESSED_AT,
    )

    # Assert
    assert analysis.transformation.proposals
    assert analysis.transformation.proposal_only
    assert not analysis.transformation.execution_available
    assert all(item.approval_required for item in analysis.transformation.proposals)


def test_given_current_mvp_when_governance_agent_runs_then_schedule_is_not_claimed() -> None:
    # Act
    governance = (
        orchestrator()
        .analyze(
            collection_id="policies",
            profiles=travel_estate(),
            assessed_at=ASSESSED_AT,
        )
        .governance
    )

    # Assert
    assert not governance.recurring_monitoring_configured
    assert set(governance.monitored_conditions) == {
        "duplication",
        "contradictions",
        "missing_ownership",
        "staleness",
        "canonical_authority",
    }


def test_given_tampered_analysis_when_validated_then_content_address_is_rejected() -> None:
    # Arrange
    analysis = orchestrator().analyze(
        collection_id="policies",
        profiles=travel_estate(),
        assessed_at=ASSESSED_AT,
    )
    payload = analysis.model_dump(mode="json")
    payload["analysis_id"] = "0" * 64

    # Act and assert
    with pytest.raises(ValidationError, match="Analysis ID does not match"):
        KnowledgeTransformationAnalysis.model_validate_json(json.dumps(payload))
