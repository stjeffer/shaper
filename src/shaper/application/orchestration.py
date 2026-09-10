"""Deterministic orchestration of Shaper's specialized knowledge agents."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from shaper.application.assessment import EstateAssessmentService
from shaper.domain import (
    AgentReadinessAgentResult,
    AssessmentAgentResult,
    AssessmentFindingKind,
    DimensionScore,
    DocumentReadinessReport,
    EstateAssessment,
    GovernanceAgentResult,
    KnowledgeAgentResult,
    KnowledgeDocumentProfile,
    KnowledgeTransformationAnalysis,
    ReadinessDimension,
    TransformationAgentResult,
    create_knowledge_transformation_analysis,
)

_ASSESSMENT_FINDINGS = frozenset(
    {
        AssessmentFindingKind.STALE,
        AssessmentFindingKind.MISSING_OWNER,
        AssessmentFindingKind.POOR_METADATA,
        AssessmentFindingKind.STRUCTURE_GAP,
    }
)
_KNOWLEDGE_FINDINGS = frozenset(
    {
        AssessmentFindingKind.DUPLICATE,
        AssessmentFindingKind.CONTRADICTION,
        AssessmentFindingKind.AUTHORITY_GAP,
    }
)
_GOVERNANCE_FINDINGS = frozenset(
    {
        AssessmentFindingKind.DUPLICATE,
        AssessmentFindingKind.CONTRADICTION,
        AssessmentFindingKind.STALE,
        AssessmentFindingKind.MISSING_OWNER,
        AssessmentFindingKind.AUTHORITY_GAP,
    }
)


class AssessmentAgent:
    """Audit content health without changing source content."""

    def analyze(self, assessment: EstateAssessment) -> AssessmentAgentResult:
        """Return content-health evidence from one immutable assessment."""
        return AssessmentAgentResult(
            assessment_id=assessment.assessment_id,
            content_quality=_dimension(assessment, ReadinessDimension.CONTENT_QUALITY),
            findings=tuple(
                finding for finding in assessment.findings if finding.kind in _ASSESSMENT_FINDINGS
            ),
        )


class KnowledgeAgent:
    """Identify topics, overlap, conflicts, and authority candidates."""

    def analyze(self, assessment: EstateAssessment) -> KnowledgeAgentResult:
        """Return knowledge-model evidence from one immutable assessment."""
        return KnowledgeAgentResult(
            assessment_id=assessment.assessment_id,
            knowledge_quality=_dimension(assessment, ReadinessDimension.KNOWLEDGE_QUALITY),
            topics=assessment.topics,
            findings=tuple(
                finding for finding in assessment.findings if finding.kind in _KNOWLEDGE_FINDINGS
            ),
        )


class TransformationAgent:
    """Propose transformations while preserving the human approval boundary."""

    def analyze(self, assessment: EstateAssessment) -> TransformationAgentResult:
        """Return reviewable proposals without executing estate-wide changes."""
        return TransformationAgentResult(
            assessment_id=assessment.assessment_id,
            proposals=assessment.recommendations,
            execution_note=(
                "Estate-wide recommendations are proposals only. The current compilation "
                "kernel executes a separately submitted item and publishes only after review."
            ),
        )

    def recommend(self, report: DocumentReadinessReport) -> tuple[str, ...]:
        """Map deterministic discovery evidence to bounded proposed changes."""
        actions = {
            "missing_owner": "Add accountable ownership metadata",
            "poor_metadata": "Generate structured topic and content metadata",
            "structure_gap": "Create meaningful heading structure",
            "stale": "Flag statements that require freshness confirmation",
            "long_paragraph": "Split long paragraphs into focused knowledge sections",
            "cross_policy_reference": "Resolve cross-policy references into explicit context",
            "faq_gap": "Generate grounded question and answer pairs",
            "procedure_gap": "Extract implied actions into explicit procedural steps",
        }
        proposed = tuple(actions[code] for code in report.finding_codes if code in actions)
        return proposed or ("Create a canonical agent-ready HTML knowledge asset",)


class GovernanceAgent:
    """Identify conditions for continuous knowledge-quality governance."""

    def analyze(self, assessment: EstateAssessment) -> GovernanceAgentResult:
        """Return current monitoring evidence without claiming scheduled execution."""
        return GovernanceAgentResult(
            assessment_id=assessment.assessment_id,
            monitored_findings=tuple(
                finding for finding in assessment.findings if finding.kind in _GOVERNANCE_FINDINGS
            ),
            monitored_conditions=(
                "duplication",
                "contradictions",
                "missing_ownership",
                "staleness",
                "canonical_authority",
            ),
        )


class AgentReadinessAgent:
    """Assess whether knowledge is usable by Copilot and other agents."""

    def analyze(self, assessment: EstateAssessment) -> AgentReadinessAgentResult:
        """Return readiness evidence and prioritized remediation."""
        return AgentReadinessAgentResult(
            assessment_id=assessment.assessment_id,
            overall_score=assessment.overall_score,
            evidence_coverage=assessment.coverage,
            agent_readiness=_dimension(assessment, ReadinessDimension.AGENT_READINESS),
            prioritized_recommendations=assessment.recommendations,
            limitations=assessment.limitations,
        )


class KnowledgeTransformationOrchestrator:
    """Coordinate specialist agents; Shaper itself is not an agent."""

    def __init__(
        self,
        *,
        assessments: EstateAssessmentService,
        assessment_agent: AssessmentAgent,
        knowledge_agent: KnowledgeAgent,
        transformation_agent: TransformationAgent,
        governance_agent: GovernanceAgent,
        agent_readiness_agent: AgentReadinessAgent,
    ) -> None:
        self._assessments = assessments
        self._assessment_agent = assessment_agent
        self._knowledge_agent = knowledge_agent
        self._transformation_agent = transformation_agent
        self._governance_agent = governance_agent
        self._agent_readiness_agent = agent_readiness_agent

    def analyze(
        self,
        *,
        collection_id: str,
        profiles: Sequence[KnowledgeDocumentProfile],
        assessed_at: datetime,
    ) -> KnowledgeTransformationAnalysis:
        """Run one synchronous, stateless platform analysis."""
        assessment = self._assessments.assess(
            collection_id=collection_id,
            profiles=profiles,
            assessed_at=assessed_at,
        )
        return create_knowledge_transformation_analysis(
            assessment_id=assessment.assessment_id,
            collection_id=assessment.collection_id,
            assessed_at=assessment.assessed_at,
            assessment=self._assessment_agent.analyze(assessment),
            knowledge=self._knowledge_agent.analyze(assessment),
            transformation=self._transformation_agent.analyze(assessment),
            governance=self._governance_agent.analyze(assessment),
            agent_readiness=self._agent_readiness_agent.analyze(assessment),
        )


def _dimension(
    assessment: EstateAssessment,
    dimension: ReadinessDimension,
) -> DimensionScore:
    return next(item for item in assessment.dimensions if item.dimension is dimension)
