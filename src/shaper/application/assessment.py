"""Deterministic, read-only assessment of normalized enterprise content estates."""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Iterable, Sequence
from datetime import datetime

from shaper.domain.assessment import (
    AssessmentCoverage,
    AssessmentFinding,
    AssessmentFindingKind,
    AssessmentMetric,
    AuthorityStatus,
    DimensionScore,
    EstateAssessment,
    InterventionKind,
    InterventionRecommendation,
    KnowledgeDocumentProfile,
    MetricName,
    ReadinessDimension,
    TopicCluster,
    TransformationMode,
    create_estate_assessment,
)
from shaper.domain.estate import DocumentReadinessReport, EffortBand
from shaper.domain.models import FindingSeverity, canonical_hash

_WORD = re.compile(r"[a-zA-Z0-9]+")
_SENTENCE = re.compile(r"[^.!?]+[.!?]?")
_HEADING = re.compile(r"(?m)^(?:#{1,6}\s+|[A-Z][A-Z0-9 &/-]{3,}$)")
_NUMBERED_STEP = re.compile(r"(?m)^\s*(?:\d+[.)]|step\s+\d+)", re.IGNORECASE)
_PROCEDURAL_CUE = re.compile(r"\b(?:must|should|submit|complete|step|procedure)\b", re.IGNORECASE)
_STOP_WORDS = frozenset(
    {"a", "an", "and", "for", "guide", "of", "policy", "procedure", "the", "to", "v"}
)
_STALE_DAYS = 1_095
_DUPLICATE_THRESHOLD = 0.75
_CROSS_POLICY_REFERENCE = re.compile(
    r"\b(?:see|refer to|in accordance with)\b[^.\n]{0,100}"
    r"\b(?:policy|procedure|standard)\b",
    re.IGNORECASE,
)
_LONG_PARAGRAPH_WORDS = 150


class DocumentAssessmentService:
    """Build transparent readiness and effort evidence for one document."""

    def report(
        self,
        *,
        run_id: str,
        estate_id: str,
        source_version: str,
        profile: KnowledgeDocumentProfile,
        assessed_at: datetime,
    ) -> DocumentReadinessReport:
        """Return one deterministic report without invoking a model."""
        scores = (
            _structure_score(profile),
            _readability_score(profile.text),
            _metadata_score(profile),
            _freshness_score(profile, assessed_at),
            _retrieval_score(profile),
            _procedure_score(profile) if _PROCEDURAL_CUE.search(profile.text) else None,
            _faq_score(profile),
            _chunking_score(profile.text),
        )
        available = tuple(score for score in scores if score is not None)
        finding_codes = self._finding_codes(profile, assessed_at)
        effort_points = min(
            100,
            round(100 - sum(available) / len(available)) + 10 * len(finding_codes),
        )
        readiness_score = round(sum(available) / len(available), 1)
        identity = {
            "run_id": run_id,
            "document_id": profile.document_id,
            "source_version": source_version,
            "readiness_score": readiness_score,
            "effort_points": effort_points,
        }
        return DocumentReadinessReport(
            report_id=canonical_hash(identity),
            run_id=run_id,
            estate_id=estate_id,
            document_id=profile.document_id,
            source_version=source_version,
            readiness_score=readiness_score,
            evidence_coverage=round(100 * len(available) / len(scores), 1),
            effort_points=effort_points,
            effort_band=(
                EffortBand.LOW
                if effort_points <= 30
                else EffortBand.MEDIUM
                if effort_points <= 65
                else EffortBand.HIGH
            ),
            reasons=self._reasons(finding_codes),
            finding_codes=finding_codes,
            agent_roles=(
                "Assessment Agent",
                "Knowledge Agent",
                "Transformation Agent",
                "Governance Agent",
                "Agent Readiness Agent",
            ),
            assessed_at=assessed_at,
        )

    @staticmethod
    def _finding_codes(
        profile: KnowledgeDocumentProfile,
        assessed_at: datetime,
    ) -> tuple[str, ...]:
        codes = []
        if len(profile.metadata) < 2:
            codes.append(AssessmentFindingKind.POOR_METADATA.value)
        if _structure_score(profile) < 50:
            codes.append(AssessmentFindingKind.STRUCTURE_GAP.value)
        if (assessed_at - profile.modified_at).days > _STALE_DAYS:
            codes.append(AssessmentFindingKind.STALE.value)
        if _long_paragraphs(profile.text):
            codes.append(AssessmentFindingKind.LONG_PARAGRAPH.value)
        if _CROSS_POLICY_REFERENCE.search(profile.text):
            codes.append(AssessmentFindingKind.CROSS_POLICY_REFERENCE.value)
        if _faq_score(profile) == 0:
            codes.append(AssessmentFindingKind.FAQ_GAP.value)
        if _PROCEDURAL_CUE.search(profile.text) and _procedure_score(profile) == 0:
            codes.append(AssessmentFindingKind.PROCEDURE_GAP.value)
        return tuple(codes)

    @staticmethod
    def _reasons(codes: Sequence[str]) -> tuple[str, ...]:
        labels = {
            AssessmentFindingKind.POOR_METADATA.value: "Add core topic and content metadata.",
            AssessmentFindingKind.STRUCTURE_GAP.value: "Introduce meaningful document structure.",
            AssessmentFindingKind.STALE.value: "Review the source for freshness.",
            AssessmentFindingKind.LONG_PARAGRAPH.value: (
                "Break long paragraphs into focused sections."
            ),
            AssessmentFindingKind.CROSS_POLICY_REFERENCE.value: (
                "Resolve opaque cross-policy references."
            ),
            AssessmentFindingKind.FAQ_GAP.value: "Add question-shaped retrieval coverage.",
            AssessmentFindingKind.PROCEDURE_GAP.value: (
                "Extract implied actions into explicit steps."
            ),
        }
        return tuple(labels[code] for code in codes) or (
            "No high-priority reshaping gaps detected.",
        )


class EstateAssessmentService:
    """Compute explainable heuristic scores and review-required interventions."""

    limitations = (
        "This Agent Readiness Score is an uncalibrated deterministic heuristic, not accuracy.",
        "Similarity and contradiction findings are candidates that require human review.",
        "Authority is based only on declared source status and is never inferred from recency.",
        "Unavailable metrics reduce assessment coverage and are excluded from score means.",
    )

    def assess(
        self,
        *,
        collection_id: str,
        profiles: Sequence[KnowledgeDocumentProfile],
        assessed_at: datetime,
    ) -> EstateAssessment:
        """Assess normalized profiles without changing their source content."""
        if assessed_at.tzinfo is None or assessed_at.utcoffset() is None:
            raise ValueError("Assessment time must include a timezone")
        if not profiles:
            raise ValueError("Estate assessment requires at least one document profile")
        if len(profiles) > 500:
            raise ValueError("Estate assessment accepts at most 500 document profiles")
        document_ids = [profile.document_id for profile in profiles]
        if len(document_ids) != len(set(document_ids)):
            raise ValueError("Estate assessment document IDs must be unique")

        token_sets = {profile.document_id: _tokens(profile.text) for profile in profiles}
        duplicates = _duplicate_pairs(profiles, token_sets)
        contradictions = _contradictions(profiles)
        topics = _topic_clusters(profiles, token_sets)
        dimensions = (
            self._content_quality(profiles, assessed_at),
            self._knowledge_quality(profiles, duplicates, contradictions),
            self._agent_readiness(profiles, duplicates, contradictions),
        )
        metrics = [metric for dimension in dimensions for metric in dimension.metrics]
        available = sum(metric.score is not None for metric in metrics)
        coverage = AssessmentCoverage(
            available_metric_count=available,
            unavailable_metric_count=len(metrics) - available,
            coverage_percent=round(100 * available / len(metrics), 1),
        )
        findings = _findings(profiles, assessed_at, duplicates, contradictions, topics)
        recommendations = _recommendations(profiles, findings, topics)
        return create_estate_assessment(
            collection_id=collection_id,
            assessed_at=assessed_at,
            document_count=len(profiles),
            overall_score=round(sum(item.score for item in dimensions) / len(dimensions), 1),
            coverage=coverage,
            dimensions=dimensions,
            findings=findings,
            topics=topics,
            recommendations=recommendations,
            limitations=self.limitations,
        )

    def _content_quality(
        self,
        profiles: Sequence[KnowledgeDocumentProfile],
        assessed_at: datetime,
    ) -> DimensionScore:
        metrics = (
            _metric(
                MetricName.STRUCTURE,
                _mean(_structure_score(profile) for profile in profiles),
                "Measures headings and paragraph structure across the assessed documents.",
                profiles,
            ),
            _metric(
                MetricName.READABILITY,
                _mean_available(_readability_score(profile.text) for profile in profiles),
                "Measures average sentence length; it does not judge writing quality.",
                profiles,
            ),
            _metric(
                MetricName.METADATA_COMPLETENESS,
                _mean(_metadata_score(profile) for profile in profiles),
                "Measures core topic and content metadata coverage.",
                profiles,
            ),
            _metric(
                MetricName.FRESHNESS,
                _mean(_freshness_score(profile, assessed_at) for profile in profiles),
                "Measures age against a three-year stale-content review threshold.",
                profiles,
            ),
        )
        return _dimension(ReadinessDimension.CONTENT_QUALITY, metrics)

    def _knowledge_quality(
        self,
        profiles: Sequence[KnowledgeDocumentProfile],
        duplicates: Sequence[tuple[str, str, float]],
        contradictions: Sequence[tuple[str, tuple[KnowledgeDocumentProfile, ...]]],
    ) -> DimensionScore:
        duplicate_score = None
        if len(profiles) > 1:
            possible_pairs = len(profiles) * (len(profiles) - 1) / 2
            duplicate_score = 100 * (1 - len(duplicates) / possible_pairs)
        comparable_terms = _comparable_assertion_terms(profiles)
        contradiction_score = None
        if comparable_terms:
            contradiction_score = 100 * (1 - len(contradictions) / len(comparable_terms))
        metrics = (
            _metric(
                MetricName.DUPLICATION,
                duplicate_score,
                "Measures candidate high-overlap document pairs; unavailable for one document.",
                profiles,
            ),
            _metric(
                MetricName.CONTRADICTIONS,
                contradiction_score,
                (
                    "Compares normalized business-term assertions; unavailable "
                    "without comparable terms."
                ),
                profiles,
            ),
            _metric(
                MetricName.AUTHORITY,
                _mean(_authority_score(profile) for profile in profiles),
                "Measures explicitly declared authority, never inferred authority.",
                profiles,
            ),
            _metric(
                MetricName.COVERAGE,
                100 * sum(bool(profile.topic) for profile in profiles) / len(profiles),
                "Measures explicit business-topic coverage.",
                profiles,
            ),
        )
        return _dimension(ReadinessDimension.KNOWLEDGE_QUALITY, metrics)

    def _agent_readiness(
        self,
        profiles: Sequence[KnowledgeDocumentProfile],
        duplicates: Sequence[tuple[str, str, float]],
        contradictions: Sequence[tuple[str, tuple[KnowledgeDocumentProfile, ...]]],
    ) -> DimensionScore:
        procedural = [profile for profile in profiles if _PROCEDURAL_CUE.search(profile.text)]
        procedure_score = None
        if procedural:
            procedure_score = _mean(_procedure_score(profile) for profile in procedural)
        consistency_inputs = []
        if len(profiles) > 1:
            possible_pairs = len(profiles) * (len(profiles) - 1) / 2
            consistency_inputs.append(100 * (1 - len(duplicates) / possible_pairs))
        comparable_terms = _comparable_assertion_terms(profiles)
        if comparable_terms:
            consistency_inputs.append(100 * (1 - len(contradictions) / len(comparable_terms)))
        semantic_consistency = _mean(consistency_inputs) if consistency_inputs else None
        metrics = (
            _metric(
                MetricName.RETRIEVAL_EFFECTIVENESS,
                _mean(_retrieval_score(profile) for profile in profiles),
                (
                    "Measures titles, topics, metadata, and bounded text structure "
                    "as retrieval signals."
                ),
                profiles,
            ),
            _metric(
                MetricName.PROCEDURAL_CLARITY,
                procedure_score,
                (
                    "Measures explicit steps in procedural content; unavailable "
                    "when none is identified."
                ),
                procedural,
            ),
            _metric(
                MetricName.FAQ_COVERAGE,
                _mean(_faq_score(profile) for profile in profiles),
                "Measures explicit FAQ assets and question-shaped content.",
                profiles,
            ),
            _metric(
                MetricName.CHUNKING_SUITABILITY,
                _mean(_chunking_score(profile.text) for profile in profiles),
                "Measures whether paragraph sizes support bounded retrieval chunks.",
                profiles,
            ),
            _metric(
                MetricName.SEMANTIC_CONSISTENCY,
                semantic_consistency,
                "Combines assessable duplication and normalized-assertion consistency signals.",
                profiles,
            ),
        )
        return _dimension(ReadinessDimension.AGENT_READINESS, metrics)


def _metric(
    name: MetricName,
    score: float | None,
    explanation: str,
    profiles: Iterable[KnowledgeDocumentProfile],
) -> AssessmentMetric:
    return AssessmentMetric(
        name=name,
        score=None if score is None else round(max(0, min(100, score)), 1),
        explanation=explanation,
        evidence_document_ids=tuple(sorted(profile.document_id for profile in profiles)),
    )


def _dimension(
    dimension: ReadinessDimension,
    metrics: tuple[AssessmentMetric, ...],
) -> DimensionScore:
    available = [metric.score for metric in metrics if metric.score is not None]
    return DimensionScore(
        dimension=dimension,
        score=round(sum(available) / len(available), 1),
        coverage_percent=round(100 * len(available) / len(metrics), 1),
        metrics=metrics,
    )


def _tokens(text: str) -> frozenset[str]:
    return frozenset(word.casefold() for word in _WORD.findall(text) if len(word) > 2)


def _mean(values: Iterable[float]) -> float:
    items = tuple(values)
    if not items:
        raise ValueError("A metric mean requires at least one value")
    return sum(items) / len(items)


def _mean_available(values: Iterable[float | None]) -> float | None:
    items = tuple(value for value in values if value is not None)
    return None if not items else _mean(items)


def _structure_score(profile: KnowledgeDocumentProfile) -> float:
    headings = len(_HEADING.findall(profile.text))
    paragraphs = sum(bool(part.strip()) for part in profile.text.split("\n\n"))
    if headings >= 2:
        return 100
    if headings == 1:
        return 75
    if paragraphs >= 3:
        return 50
    return 25


def _readability_score(text: str) -> float | None:
    sentences = [sentence for sentence in _SENTENCE.findall(text) if _WORD.search(sentence)]
    if not sentences:
        return None
    average_words = _mean(len(_WORD.findall(sentence)) for sentence in sentences)
    if average_words <= 20:
        return 100
    if average_words <= 30:
        return 75
    if average_words <= 40:
        return 50
    return 25


def _metadata_score(profile: KnowledgeDocumentProfile) -> float:
    return min(100, 25 * len(profile.metadata))


def _freshness_score(profile: KnowledgeDocumentProfile, assessed_at: datetime) -> float:
    age_days = (assessed_at - profile.modified_at).days
    if age_days < 0:
        raise ValueError(f"Document {profile.document_id!r} modification time is in the future")
    if age_days <= 365:
        return 100
    if age_days <= _STALE_DAYS:
        return 60
    return 20


def _authority_score(profile: KnowledgeDocumentProfile) -> float:
    return {
        AuthorityStatus.AUTHORITATIVE: 100,
        AuthorityStatus.CANDIDATE: 50,
        AuthorityStatus.UNKNOWN: 0,
    }[profile.authority]


def _retrieval_score(profile: KnowledgeDocumentProfile) -> float:
    signals = (
        bool(profile.title),
        bool(profile.topic),
        bool(profile.metadata),
        bool(_HEADING.search(profile.text)),
    )
    return 25 * sum(signals)


def _procedure_score(profile: KnowledgeDocumentProfile) -> float:
    explicit_steps = max(profile.procedure_step_count, len(_NUMBERED_STEP.findall(profile.text)))
    return min(100, explicit_steps * 25)


def _faq_score(profile: KnowledgeDocumentProfile) -> float:
    questions = profile.text.count("?")
    return min(100, max(profile.faq_count, questions) * 25)


def _chunking_score(text: str) -> float:
    lengths = [len(part.strip()) for part in text.split("\n\n") if part.strip()]
    suitable = sum(80 <= length <= 1_500 for length in lengths)
    return 100 * suitable / len(lengths)


def _long_paragraphs(text: str) -> tuple[str, ...]:
    return tuple(
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if len(_WORD.findall(paragraph)) > _LONG_PARAGRAPH_WORDS
    )


def _duplicate_pairs(
    profiles: Sequence[KnowledgeDocumentProfile],
    token_sets: dict[str, frozenset[str]],
) -> tuple[tuple[str, str, float], ...]:
    pairs: list[tuple[str, str, float]] = []
    for index, left in enumerate(profiles):
        for right in profiles[index + 1 :]:
            left_tokens = token_sets[left.document_id]
            right_tokens = token_sets[right.document_id]
            union = left_tokens | right_tokens
            similarity = len(left_tokens & right_tokens) / len(union) if union else 0
            if similarity >= _DUPLICATE_THRESHOLD:
                pairs.append((left.document_id, right.document_id, round(similarity * 100, 1)))
    return tuple(pairs)


def _comparable_assertion_terms(profiles: Sequence[KnowledgeDocumentProfile]) -> frozenset[str]:
    counts: dict[str, set[str]] = defaultdict(set)
    for profile in profiles:
        for assertion in profile.assertions:
            counts[assertion.term.casefold()].add(profile.document_id)
    return frozenset(term for term, document_ids in counts.items() if len(document_ids) > 1)


def _contradictions(
    profiles: Sequence[KnowledgeDocumentProfile],
) -> tuple[tuple[str, tuple[KnowledgeDocumentProfile, ...]], ...]:
    by_term: dict[str, dict[str, KnowledgeDocumentProfile]] = defaultdict(dict)
    values: dict[str, set[str]] = defaultdict(set)
    for profile in profiles:
        for assertion in profile.assertions:
            term = assertion.term.casefold()
            by_term[term][profile.document_id] = profile
            values[term].add(assertion.value.casefold())
    return tuple(
        (term, tuple(sorted(by_term[term].values(), key=lambda item: item.document_id)))
        for term in sorted(values)
        if len(by_term[term]) > 1 and len(values[term]) > 1
    )


def _topic_label(profile: KnowledgeDocumentProfile) -> str:
    if profile.topic:
        return profile.topic
    words = [
        word
        for word in (item.casefold() for item in _WORD.findall(profile.title))
        if word not in _STOP_WORDS and not word.isdigit()
    ]
    return " ".join(words[:2]).title() or "Unclassified"


def _topic_clusters(
    profiles: Sequence[KnowledgeDocumentProfile],
    token_sets: dict[str, frozenset[str]],
) -> tuple[TopicCluster, ...]:
    grouped: dict[str, list[KnowledgeDocumentProfile]] = defaultdict(list)
    for profile in profiles:
        grouped[_topic_label(profile)].append(profile)
    clusters = []
    for topic, documents in sorted(grouped.items()):
        overlaps = []
        for index, left in enumerate(documents):
            for right in documents[index + 1 :]:
                left_tokens = token_sets[left.document_id]
                right_tokens = token_sets[right.document_id]
                union = left_tokens | right_tokens
                overlaps.append(100 * len(left_tokens & right_tokens) / len(union) if union else 0)
        overlap = _mean(overlaps) if overlaps else 0
        recommendation = (
            "Review for one canonical knowledge source."
            if overlap >= 60 and len(documents) > 1
            else "Retain as a governed business topic."
        )
        clusters.append(
            TopicCluster(
                topic=topic,
                document_ids=tuple(sorted(document.document_id for document in documents)),
                overlap_percent=round(overlap, 1),
                recommendation=recommendation,
            )
        )
    return tuple(clusters)


def _findings(
    profiles: Sequence[KnowledgeDocumentProfile],
    assessed_at: datetime,
    duplicates: Sequence[tuple[str, str, float]],
    contradictions: Sequence[tuple[str, tuple[KnowledgeDocumentProfile, ...]]],
    topics: Sequence[TopicCluster],
) -> tuple[AssessmentFinding, ...]:
    findings: list[AssessmentFinding] = []

    def add(
        kind: AssessmentFindingKind,
        severity: FindingSeverity,
        title: str,
        detail: str,
        document_ids: tuple[str, ...],
        provenance: tuple[str, ...] = (),
    ) -> None:
        finding_id = canonical_hash(
            {"kind": kind, "documents": document_ids, "detail": detail, "provenance": provenance}
        )[:32]
        findings.append(
            AssessmentFinding(
                finding_id=finding_id,
                kind=kind,
                severity=severity,
                title=title,
                detail=detail,
                evidence_document_ids=document_ids,
                assertion_provenance=provenance,
            )
        )

    for profile in profiles:
        if profile.owner is None:
            add(
                AssessmentFindingKind.MISSING_OWNER,
                FindingSeverity.WARNING,
                "Document has no declared owner",
                f"{profile.title} requires an accountable owner.",
                (profile.document_id,),
            )
        if (assessed_at - profile.modified_at).days > _STALE_DAYS:
            add(
                AssessmentFindingKind.STALE,
                FindingSeverity.WARNING,
                "Document requires freshness review",
                f"{profile.title} is older than the three-year review threshold.",
                (profile.document_id,),
            )
        if len(profile.metadata) < 2:
            add(
                AssessmentFindingKind.POOR_METADATA,
                FindingSeverity.INFO,
                "Metadata coverage is limited",
                f"{profile.title} has fewer than two metadata fields.",
                (profile.document_id,),
            )
        if _structure_score(profile) < 50:
            add(
                AssessmentFindingKind.STRUCTURE_GAP,
                FindingSeverity.INFO,
                "Document structure limits agent use",
                f"{profile.title} has no detectable heading or multi-paragraph structure.",
                (profile.document_id,),
            )
        if _long_paragraphs(profile.text):
            add(
                AssessmentFindingKind.LONG_PARAGRAPH,
                FindingSeverity.WARNING,
                "Long paragraph limits retrieval precision",
                f"{profile.title} contains paragraphs longer than {_LONG_PARAGRAPH_WORDS} words.",
                (profile.document_id,),
            )
        if _CROSS_POLICY_REFERENCE.search(profile.text):
            add(
                AssessmentFindingKind.CROSS_POLICY_REFERENCE,
                FindingSeverity.WARNING,
                "Cross-policy reference requires resolution",
                f"{profile.title} contains an opaque reference to another governed source.",
                (profile.document_id,),
            )
        if _faq_score(profile) == 0:
            add(
                AssessmentFindingKind.FAQ_GAP,
                FindingSeverity.INFO,
                "No FAQ coverage detected",
                f"{profile.title} has no explicit FAQ assets or question-shaped content.",
                (profile.document_id,),
            )
        if _PROCEDURAL_CUE.search(profile.text) and _procedure_score(profile) == 0:
            add(
                AssessmentFindingKind.PROCEDURE_GAP,
                FindingSeverity.WARNING,
                "Procedural content lacks explicit steps",
                f"{profile.title} contains procedural language without detectable steps.",
                (profile.document_id,),
            )

    for left, right, overlap in duplicates:
        add(
            AssessmentFindingKind.DUPLICATE,
            FindingSeverity.WARNING,
            "High-overlap documents require review",
            f"Documents share {overlap:.1f}% of normalized terms; similarity is not proof.",
            (left, right),
        )
    for term, documents in contradictions:
        provenance = tuple(
            sorted(
                assertion.provenance
                for document in documents
                for assertion in document.assertions
                if assertion.term.casefold() == term
            )
        )
        add(
            AssessmentFindingKind.CONTRADICTION,
            FindingSeverity.BLOCKING,
            "Business-term assertions conflict",
            f"Normalized assertions for {term!r} contain different values.",
            tuple(document.document_id for document in documents),
            provenance,
        )
    for topic in topics:
        topic_documents = [
            profile for profile in profiles if profile.document_id in topic.document_ids
        ]
        if len(topic_documents) > 1 and not any(
            profile.authority is AuthorityStatus.AUTHORITATIVE for profile in topic_documents
        ):
            add(
                AssessmentFindingKind.AUTHORITY_GAP,
                FindingSeverity.WARNING,
                "Business topic has no declared authority",
                f"{topic.topic} has multiple sources and no explicitly authoritative document.",
                topic.document_ids,
            )
    return tuple(
        sorted(findings, key=lambda item: (-_severity_rank(item.severity), item.finding_id))
    )


def _severity_rank(severity: FindingSeverity) -> int:
    return {
        FindingSeverity.INFO: 1,
        FindingSeverity.WARNING: 2,
        FindingSeverity.BLOCKING: 3,
    }[severity]


def _recommendations(
    profiles: Sequence[KnowledgeDocumentProfile],
    findings: Sequence[AssessmentFinding],
    topics: Sequence[TopicCluster],
) -> tuple[InterventionRecommendation, ...]:
    by_kind: dict[AssessmentFindingKind, set[str]] = defaultdict(set)
    for finding in findings:
        by_kind[finding.kind].update(finding.evidence_document_ids)
    candidates: list[tuple[InterventionKind, set[str], tuple[TransformationMode, ...], str]] = []

    def add(
        kind: InterventionKind,
        source_kinds: tuple[AssessmentFindingKind, ...],
        modes: tuple[TransformationMode, ...],
        rationale: str,
        *,
        fallback_ids: Iterable[str] = (),
    ) -> None:
        document_ids = set(fallback_ids)
        for source_kind in source_kinds:
            document_ids.update(by_kind[source_kind])
        if document_ids:
            candidates.append((kind, document_ids, modes, rationale))

    add(
        InterventionKind.IDENTIFY_AUTHORITATIVE_VERSIONS,
        (AssessmentFindingKind.CONTRADICTION, AssessmentFindingKind.AUTHORITY_GAP),
        (TransformationMode.SAFE, TransformationMode.KNOWLEDGE_CONSOLIDATION),
        "Review conflicting or overlapping sources and explicitly confirm authority.",
    )
    add(
        InterventionKind.CONSOLIDATE_DUPLICATE_CONTENT,
        (AssessmentFindingKind.DUPLICATE,),
        (TransformationMode.KNOWLEDGE_CONSOLIDATION,),
        "Consolidate high-overlap candidates only after human comparison.",
    )
    add(
        InterventionKind.ARCHIVE_REDUNDANT_MATERIAL,
        (AssessmentFindingKind.STALE, AssessmentFindingKind.DUPLICATE),
        (TransformationMode.GUIDED_REWRITE, TransformationMode.KNOWLEDGE_CONSOLIDATION),
        "Propose archival for reviewed stale or redundant material.",
    )
    add(
        InterventionKind.MODERNIZE_DOCUMENT_STRUCTURE,
        (AssessmentFindingKind.STRUCTURE_GAP,),
        (TransformationMode.GUIDED_REWRITE,),
        "Improve headings and sections while preserving source meaning.",
    )
    add(
        InterventionKind.GENERATE_METADATA,
        (AssessmentFindingKind.MISSING_OWNER, AssessmentFindingKind.POOR_METADATA),
        (TransformationMode.SAFE, TransformationMode.GUIDED_REWRITE),
        "Generate metadata suggestions for human approval.",
    )
    add(
        InterventionKind.GENERATE_FAQS,
        (AssessmentFindingKind.FAQ_GAP,),
        (TransformationMode.SAFE,),
        "Create grounded FAQ assets without changing original documents.",
    )
    add(
        InterventionKind.EXTRACT_PROCEDURES,
        (AssessmentFindingKind.PROCEDURE_GAP,),
        (TransformationMode.SAFE, TransformationMode.GUIDED_REWRITE),
        "Extract explicit procedures and route them for review.",
    )
    all_ids = {profile.document_id for profile in profiles}
    add(
        InterventionKind.GENERATE_EXECUTIVE_SUMMARIES,
        (),
        (TransformationMode.SAFE,),
        "Create source-grounded topic and executive summaries.",
        fallback_ids=all_ids,
    )
    add(
        InterventionKind.CREATE_AGENT_KNOWLEDGE_PACKS,
        (),
        (TransformationMode.SAFE, TransformationMode.KNOWLEDGE_CONSOLIDATION),
        "Package reviewed outputs for Copilot and agent consumption.",
        fallback_ids=all_ids,
    )
    multi_source_topics = {
        document_id
        for topic in topics
        if len(topic.document_ids) > 1
        for document_id in topic.document_ids
    }
    add(
        InterventionKind.CREATE_CANONICAL_BUSINESS_GUIDANCE,
        (),
        (TransformationMode.KNOWLEDGE_CONSOLIDATION,),
        "Create one reviewed canonical source for multi-document business topics.",
        fallback_ids=multi_source_topics,
    )
    recommendations = []
    for priority, (kind, document_ids, modes, rationale) in enumerate(candidates, start=1):
        sorted_ids = tuple(sorted(document_ids))
        recommendations.append(
            InterventionRecommendation(
                recommendation_id=canonical_hash(
                    {"kind": kind, "documents": sorted_ids, "modes": modes}
                )[:32],
                kind=kind,
                priority=priority,
                rationale=rationale,
                document_ids=sorted_ids,
                supported_modes=modes,
            )
        )
    return tuple(recommendations)
