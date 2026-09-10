"""Immutable contracts for estate discovery and agent-readiness assessment."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal, Self

from pydantic import Field, field_validator, model_validator

from shaper.domain.models import (
    SCHEMA_VERSION,
    DomainModel,
    FindingSeverity,
    Identifier,
    Sha256,
    canonical_hash,
)


class AuthorityStatus(StrEnum):
    """Declared authority state for one source document."""

    AUTHORITATIVE = "authoritative"
    CANDIDATE = "candidate"
    UNKNOWN = "unknown"


class ReadinessDimension(StrEnum):
    """Top-level agent-readiness assessment dimensions."""

    CONTENT_QUALITY = "content_quality"
    KNOWLEDGE_QUALITY = "knowledge_quality"
    AGENT_READINESS = "agent_readiness"


class MetricName(StrEnum):
    """Explainable component metrics used by the assessment heuristic."""

    STRUCTURE = "structure"
    READABILITY = "readability"
    METADATA_COMPLETENESS = "metadata_completeness"
    FRESHNESS = "freshness"
    DUPLICATION = "duplication"
    CONTRADICTIONS = "contradictions"
    AUTHORITY = "authority"
    COVERAGE = "coverage"
    RETRIEVAL_EFFECTIVENESS = "retrieval_effectiveness"
    PROCEDURAL_CLARITY = "procedural_clarity"
    FAQ_COVERAGE = "faq_coverage"
    CHUNKING_SUITABILITY = "chunking_suitability"
    SEMANTIC_CONSISTENCY = "semantic_consistency"


class AssessmentFindingKind(StrEnum):
    """Candidate estate conditions that require attention or review."""

    DUPLICATE = "duplicate"
    STALE = "stale"
    MISSING_OWNER = "missing_owner"
    POOR_METADATA = "poor_metadata"
    CONTRADICTION = "contradiction"
    AUTHORITY_GAP = "authority_gap"
    STRUCTURE_GAP = "structure_gap"
    FAQ_GAP = "faq_gap"
    PROCEDURE_GAP = "procedure_gap"
    LONG_PARAGRAPH = "long_paragraph"
    CROSS_POLICY_REFERENCE = "cross_policy_reference"


class InterventionKind(StrEnum):
    """Remediation interventions supported by the product brief."""

    CONSOLIDATE_DUPLICATE_CONTENT = "consolidate_duplicate_content"
    IDENTIFY_AUTHORITATIVE_VERSIONS = "identify_authoritative_versions"
    ARCHIVE_REDUNDANT_MATERIAL = "archive_redundant_material"
    MODERNIZE_DOCUMENT_STRUCTURE = "modernize_document_structure"
    GENERATE_METADATA = "generate_metadata"
    GENERATE_EXECUTIVE_SUMMARIES = "generate_executive_summaries"
    GENERATE_FAQS = "generate_faqs"
    EXTRACT_PROCEDURES = "extract_procedures"
    CREATE_AGENT_KNOWLEDGE_PACKS = "create_agent_knowledge_packs"
    CREATE_CANONICAL_BUSINESS_GUIDANCE = "create_canonical_business_guidance"


class TransformationMode(StrEnum):
    """Human-approved transformation modes."""

    SAFE = "safe"
    GUIDED_REWRITE = "guided_rewrite"
    KNOWLEDGE_CONSOLIDATION = "knowledge_consolidation"


class BusinessAssertion(DomainModel):
    """Normalized business-term assertion with source provenance."""

    term: str = Field(min_length=1, max_length=200)
    value: str = Field(min_length=1, max_length=2000)
    provenance: str = Field(min_length=1, max_length=500)


class KnowledgeDocumentProfile(DomainModel):
    """Bounded normalized input for read-only estate assessment."""

    document_id: Identifier
    title: str = Field(min_length=1, max_length=500)
    text: str = Field(min_length=1, max_length=100_000)
    modified_at: datetime
    owner: str | None = Field(default=None, max_length=200)
    metadata: dict[str, str] = Field(default_factory=dict, max_length=50)
    topic: str | None = Field(default=None, max_length=200)
    authority: AuthorityStatus = AuthorityStatus.UNKNOWN
    faq_count: int = Field(default=0, ge=0, le=10_000)
    procedure_step_count: int = Field(default=0, ge=0, le=10_000)
    assertions: tuple[BusinessAssertion, ...] = Field(default=(), max_length=200)

    @field_validator("modified_at")
    @classmethod
    def require_aware_modified_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Document modification time must include a timezone")
        return value

    @model_validator(mode="after")
    def require_unique_assertions(self) -> Self:
        keys = [(assertion.term.casefold(), assertion.provenance) for assertion in self.assertions]
        if len(keys) != len(set(keys)):
            raise ValueError("Document assertions must have unique term and provenance pairs")
        return self


class AssessmentMetric(DomainModel):
    """One transparent readiness metric, including unavailable evidence."""

    name: MetricName
    score: float | None = Field(default=None, ge=0, le=100)
    explanation: str = Field(min_length=1, max_length=1000)
    evidence_document_ids: tuple[Identifier, ...] = ()


class DimensionScore(DomainModel):
    """Aggregate score and evidence coverage for one readiness dimension."""

    dimension: ReadinessDimension
    score: float = Field(ge=0, le=100)
    coverage_percent: float = Field(ge=0, le=100)
    metrics: tuple[AssessmentMetric, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_aggregate(self) -> Self:
        available = [metric.score for metric in self.metrics if metric.score is not None]
        if not available:
            raise ValueError("A readiness dimension requires at least one available metric")
        expected_score = round(sum(available) / len(available), 1)
        expected_coverage = round(100 * len(available) / len(self.metrics), 1)
        if self.score != expected_score:
            raise ValueError("Dimension score must equal the mean of available metrics")
        if self.coverage_percent != expected_coverage:
            raise ValueError("Dimension coverage must reflect available metrics")
        return self


class AssessmentCoverage(DomainModel):
    """Completeness of the evidence used to calculate readiness."""

    available_metric_count: int = Field(ge=1)
    unavailable_metric_count: int = Field(ge=0)
    coverage_percent: float = Field(ge=0, le=100)

    @model_validator(mode="after")
    def validate_coverage(self) -> Self:
        total = self.available_metric_count + self.unavailable_metric_count
        expected = round(100 * self.available_metric_count / total, 1)
        if self.coverage_percent != expected:
            raise ValueError("Assessment coverage must reflect available metrics")
        return self


class AssessmentFinding(DomainModel):
    """Evidence-linked candidate condition that never mutates source content."""

    finding_id: Identifier
    kind: AssessmentFindingKind
    severity: FindingSeverity
    title: str = Field(min_length=1, max_length=300)
    detail: str = Field(min_length=1, max_length=2000)
    evidence_document_ids: tuple[Identifier, ...] = Field(min_length=1)
    assertion_provenance: tuple[str, ...] = ()
    review_required: Literal[True] = True


class TopicCluster(DomainModel):
    """Related documents and their observed lexical overlap."""

    topic: str = Field(min_length=1, max_length=200)
    document_ids: tuple[Identifier, ...] = Field(min_length=1)
    overlap_percent: float = Field(ge=0, le=100)
    recommendation: str = Field(min_length=1, max_length=1000)


class InterventionRecommendation(DomainModel):
    """Prioritized, human-approved remediation option."""

    recommendation_id: Identifier
    kind: InterventionKind
    priority: int = Field(ge=1)
    rationale: str = Field(min_length=1, max_length=1000)
    document_ids: tuple[Identifier, ...] = Field(min_length=1)
    supported_modes: tuple[TransformationMode, ...] = Field(min_length=1)
    approval_required: Literal[True] = True


class EstateAssessment(DomainModel):
    """Immutable read-only analysis of one normalized content estate."""

    schema_version: Literal["1.0"] = "1.0"
    assessment_id: Sha256
    collection_id: Identifier
    assessed_at: datetime
    document_count: int = Field(ge=1, le=500)
    overall_score: float = Field(ge=0, le=100)
    coverage: AssessmentCoverage
    dimensions: tuple[DimensionScore, ...] = Field(min_length=3, max_length=3)
    findings: tuple[AssessmentFinding, ...]
    topics: tuple[TopicCluster, ...]
    recommendations: tuple[InterventionRecommendation, ...]
    limitations: tuple[str, ...] = Field(min_length=1)

    @field_validator("assessed_at")
    @classmethod
    def require_aware_assessment_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Assessment time must include a timezone")
        return value

    def identity_payload(self) -> dict[str, Any]:
        """Return the fields that define immutable assessment identity."""
        return self.model_dump(mode="json", exclude={"assessment_id"})

    @model_validator(mode="after")
    def validate_assessment(self) -> Self:
        dimensions = {score.dimension for score in self.dimensions}
        if dimensions != set(ReadinessDimension):
            raise ValueError("Assessment must contain each readiness dimension exactly once")
        expected_score = round(
            sum(dimension.score for dimension in self.dimensions) / len(self.dimensions),
            1,
        )
        if self.overall_score != expected_score:
            raise ValueError("Overall score must equal the mean of readiness dimensions")
        metrics = [metric for dimension in self.dimensions for metric in dimension.metrics]
        available = sum(metric.score is not None for metric in metrics)
        if (
            self.coverage.available_metric_count != available
            or self.coverage.unavailable_metric_count != len(metrics) - available
        ):
            raise ValueError("Assessment coverage counts do not match dimension metrics")
        if self.assessment_id != canonical_hash(self.identity_payload()):
            raise ValueError("Assessment ID does not match canonical assessment content")
        return self


def create_estate_assessment(**values: Any) -> EstateAssessment:
    """Create an estate assessment with deterministic canonical identity."""
    payload = {"schema_version": SCHEMA_VERSION, **values}
    payload["assessment_id"] = canonical_hash(payload)
    return EstateAssessment.model_validate(payload)
