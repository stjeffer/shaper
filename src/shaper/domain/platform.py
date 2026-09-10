"""Immutable contracts for coordinated knowledge transformation analysis."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal, Self

from pydantic import Field, field_validator, model_validator

from shaper.domain.assessment import (
    AssessmentCoverage,
    AssessmentFinding,
    DimensionScore,
    InterventionRecommendation,
    ReadinessDimension,
    TopicCluster,
)
from shaper.domain.models import SCHEMA_VERSION, DomainModel, Identifier, Sha256, canonical_hash


class SpecialistAgentRole(StrEnum):
    """Bounded capability roles coordinated by the Shaper platform."""

    ASSESSMENT = "assessment"
    KNOWLEDGE = "knowledge"
    TRANSFORMATION = "transformation"
    GOVERNANCE = "governance"
    AGENT_READINESS = "agent_readiness"


class AssessmentAgentResult(DomainModel):
    """Content-health evidence produced by the Assessment Agent."""

    role: Literal[SpecialistAgentRole.ASSESSMENT] = SpecialistAgentRole.ASSESSMENT
    assessment_id: Sha256
    content_quality: DimensionScore
    findings: tuple[AssessmentFinding, ...]

    @model_validator(mode="after")
    def validate_dimension(self) -> Self:
        if self.content_quality.dimension is not ReadinessDimension.CONTENT_QUALITY:
            raise ValueError("Assessment Agent result requires the content-quality dimension")
        return self


class KnowledgeAgentResult(DomainModel):
    """Topics and knowledge-quality evidence produced by the Knowledge Agent."""

    role: Literal[SpecialistAgentRole.KNOWLEDGE] = SpecialistAgentRole.KNOWLEDGE
    assessment_id: Sha256
    knowledge_quality: DimensionScore
    topics: tuple[TopicCluster, ...]
    findings: tuple[AssessmentFinding, ...]

    @model_validator(mode="after")
    def validate_dimension(self) -> Self:
        if self.knowledge_quality.dimension is not ReadinessDimension.KNOWLEDGE_QUALITY:
            raise ValueError("Knowledge Agent result requires the knowledge-quality dimension")
        return self


class TransformationAgentResult(DomainModel):
    """Human-governed transformation proposals, never autonomous source changes."""

    role: Literal[SpecialistAgentRole.TRANSFORMATION] = SpecialistAgentRole.TRANSFORMATION
    assessment_id: Sha256
    proposals: tuple[InterventionRecommendation, ...]
    proposal_only: Literal[True] = True
    execution_available: Literal[False] = False
    execution_note: str = Field(min_length=1, max_length=1000)


class GovernanceAgentResult(DomainModel):
    """Knowledge-health conditions available for governance monitoring."""

    role: Literal[SpecialistAgentRole.GOVERNANCE] = SpecialistAgentRole.GOVERNANCE
    assessment_id: Sha256
    monitored_findings: tuple[AssessmentFinding, ...]
    monitored_conditions: tuple[str, ...] = Field(min_length=1)
    recurring_monitoring_configured: Literal[False] = False


class AgentReadinessAgentResult(DomainModel):
    """Evidence answering whether content is ready for agent consumption."""

    role: Literal[SpecialistAgentRole.AGENT_READINESS] = SpecialistAgentRole.AGENT_READINESS
    assessment_id: Sha256
    overall_score: float = Field(ge=0, le=100)
    evidence_coverage: AssessmentCoverage
    agent_readiness: DimensionScore
    prioritized_recommendations: tuple[InterventionRecommendation, ...]
    limitations: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_dimension(self) -> Self:
        if self.agent_readiness.dimension is not ReadinessDimension.AGENT_READINESS:
            raise ValueError("Agent Readiness Agent result requires its readiness dimension")
        return self


class KnowledgeTransformationAnalysis(DomainModel):
    """One content-addressed analysis coordinated by the Shaper platform."""

    schema_version: Literal["1.0"] = "1.0"
    analysis_id: Sha256
    assessment_id: Sha256
    collection_id: Identifier
    assessed_at: datetime
    assessment: AssessmentAgentResult
    knowledge: KnowledgeAgentResult
    transformation: TransformationAgentResult
    governance: GovernanceAgentResult
    agent_readiness: AgentReadinessAgentResult

    @field_validator("assessed_at")
    @classmethod
    def require_aware_assessment_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Platform analysis time must include a timezone")
        return value

    @model_validator(mode="after")
    def validate_analysis(self) -> Self:
        results = (
            self.assessment,
            self.knowledge,
            self.transformation,
            self.governance,
            self.agent_readiness,
        )
        if {result.role for result in results} != set(SpecialistAgentRole):
            raise ValueError("Platform analysis must contain each specialist agent exactly once")
        if any(result.assessment_id != self.assessment_id for result in results):
            raise ValueError("Specialist agent results must reference one assessment")
        expected_id = canonical_hash(self.model_dump(mode="json", exclude={"analysis_id"}))
        if self.analysis_id != expected_id:
            raise ValueError("Analysis ID does not match canonical analysis content")
        return self


def create_knowledge_transformation_analysis(
    **values: Any,
) -> KnowledgeTransformationAnalysis:
    """Create a content-addressed platform analysis."""
    payload = {"schema_version": SCHEMA_VERSION, **values}
    payload["analysis_id"] = canonical_hash(payload)
    return KnowledgeTransformationAnalysis.model_validate(payload)
