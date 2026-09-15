"""Deterministic candidate validation rules."""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Sequence

from shaper.domain import AnswerUnit, FindingSeverity, SourceSpan, ValidationFinding

_WORD = re.compile(r"\b[\w'-]+\b", re.UNICODE)
_MATERIAL_FACT = re.compile(
    r"(?:[$£€]\s?\d[\d,.]*|\b\d[\d,.]*\s?(?:%|percent|days?|weeks?|months?|years?|hours?)?\b)",
    re.IGNORECASE,
)
_OPERATIVE_CLAUSE = re.compile(
    r"\b(?:must(?:\s+not)?|shall(?:\s+not)?|should(?:\s+not)?|required|prohibited|"
    r"may(?!\s+(?:\d{1,2}\b|(?:19|20)\d{2}\b))(?:\s+(?:only|not))?|"
    r"can(?:not|\s+only)?|will\s+not|is\s+responsible\s+for|unless|except)\b",
    re.IGNORECASE,
)
_MATERIAL_CLAUSE_MIN_WORDS = 3
_CLAUSE_MATCH_THRESHOLD = 0.2
_CLAUSE_PRESERVATION_THRESHOLD = 0.6
_CLAUSE_STOP_WORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "be",
        "been",
        "for",
        "has",
        "have",
        "in",
        "is",
        "it",
        "of",
        "the",
        "their",
        "to",
        "when",
        "with",
    }
)
_WORD_EQUIVALENTS = {
    "applies": "apply",
    "applicable": "apply",
    "approval": "approve",
    "approved": "approve",
    "approves": "approve",
    "became": "begin",
    "become": "begin",
    "becomes": "begin",
    "began": "begin",
    "begins": "begin",
    "beginning": "begin",
    "completed": "complete",
    "completing": "complete",
    "eligibility": "eligible",
    "employees": "employee",
    "once": "after",
    "terminated": "terminate",
    "terminates": "terminate",
    "termination": "terminate",
}
_ALIGNMENT_CONTROL_WORDS = frozenset(
    {
        "after",
        "allowed",
        "before",
        "can",
        "during",
        "may",
        "must",
        "not",
        "only",
        "permitted",
        "prohibited",
        "required",
        "shall",
        "should",
        "solely",
        "within",
    }
)
_RESTRICTIVE_QUALIFIERS = (
    (
        "only",
        re.compile(r"\b(?:only|solely)\b", re.IGNORECASE),
    ),
    (
        "minimum",
        re.compile(r"\b(?:at\s+least|no\s+less\s+than)\b", re.IGNORECASE),
    ),
    (
        "maximum",
        re.compile(r"\b(?:at\s+most|no\s+more\s+than)\b", re.IGNORECASE),
    ),
    ("before", re.compile(r"\bbefore\b", re.IGNORECASE)),
    ("after", re.compile(r"\b(?:after|once)\b", re.IGNORECASE)),
    ("within", re.compile(r"\bwithin\b", re.IGNORECASE)),
    ("during", re.compile(r"\bduring\b", re.IGNORECASE)),
)
_PERMISSION_MODAL_PATTERNS = (
    re.compile(r"\bmay(?!\s+(?:\d{1,2}\b|(?:19|20)\d{2}\b))\b", re.IGNORECASE),
    re.compile(r"\bcan\b", re.IGNORECASE),
    re.compile(r"\b(?:allowed|permitted)\b", re.IGNORECASE),
)
_OBLIGATION_MODAL_PATTERN = re.compile(
    r"\b(?:must|shall|(?<!not\s)(?<!longer\s)required|"
    r"(?<!not\s)(?<!longer\s)is\s+responsible\s+for)\b",
    re.IGNORECASE,
)
_PROHIBITION_PATTERN = re.compile(
    r"\b(?:must\s+not|shall\s+not|should\s+not|may\s+not|cannot|"
    r"will\s+not|(?<!not\s)(?<!longer\s)prohibited|not\s+allowed)\b",
    re.IGNORECASE,
)
_NEGATED_NAMED_MODAL_PATTERN = re.compile(
    r"\b(?:not|no\s+longer)\s+(?:required|prohibited|responsible\s+for)\b",
    re.IGNORECASE,
)
_PRESERVATION_CATEGORIES = (
    (
        "content.advisory_clause",
        re.compile(r"\b(?:should(?:\s+not)?|expected\s+to|recommended)\b", re.IGNORECASE),
        "advisory duties or recommendations",
    ),
    (
        "content.permission_clause",
        re.compile(
            r"\b(?:may(?!\s+(?:\d{1,2}\b|(?:19|20)\d{2}\b))|can|allowed|permitted)\b",
            re.IGNORECASE,
        ),
        "permissions",
    ),
    (
        "content.prohibition_clause",
        _PROHIBITION_PATTERN,
        "prohibitions",
    ),
    (
        "content.exception_clause",
        re.compile(r"\b(?:unless|except(?:\s+when|\s+where)?)\b", re.IGNORECASE),
        "exceptions",
    ),
)


class DeterministicValidator:
    """Apply ordered fail-closed rules without model calls."""

    def validate(
        self,
        unit: AnswerUnit,
        spans: Sequence[SourceSpan],
    ) -> Sequence[ValidationFinding]:
        """Return source, grounding, qualifier, and conflict findings."""
        findings: list[ValidationFinding] = []
        span_by_id = {span.span_id: span for span in spans}
        if not spans:
            findings.append(self._blocking(unit, "source.spans", "No source spans are available"))
            return findings
        for span in spans:
            if span.source_id != unit.source_id or span.source_version != unit.source_version:
                findings.append(
                    self._blocking(
                        unit,
                        "source.version",
                        "Candidate source identity does not match the supplied evidence",
                    )
                )
                break
        for claim_index, claim in enumerate(unit.claims):
            missing = sorted(set(claim.span_ids) - span_by_id.keys())
            if missing:
                findings.append(
                    ValidationFinding(
                        rule_id="grounding.span_exists",
                        severity=FindingSeverity.BLOCKING,
                        subject_id=unit.unit_id,
                        message=(
                            f"Claim {claim_index} cites unavailable spans: {', '.join(missing)}"
                        ),
                        evidence_span_ids=tuple(missing),
                        remedy="Cite only exact spans from the active source version",
                    )
                )
        source_text = "\n".join(span.text for span in spans)
        findings.extend(self._preservation_findings(unit, source_text))
        if len(set(unit.canonical_questions)) != len(unit.canonical_questions):
            findings.append(
                self._blocking(
                    unit,
                    "identity.duplicate_question",
                    "Canonical questions must be unique",
                )
            )
        if unit.conflict_unit_ids:
            findings.append(
                ValidationFinding(
                    rule_id="conflict.detected",
                    severity=FindingSeverity.WARNING,
                    subject_id=unit.unit_id,
                    message="Candidate has potentially conflicting evidence units",
                    remedy="Route the conflict set to human review",
                )
            )
        return tuple(findings)

    def _preservation_findings(
        self,
        unit: AnswerUnit,
        source_text: str,
    ) -> Sequence[ValidationFinding]:
        """Block candidates that compress or omit material source content."""
        findings: list[ValidationFinding] = []
        source_words = [word.casefold() for word in _WORD.findall(source_text)]
        answer_words = [word.casefold() for word in _WORD.findall(unit.answer)]
        if len(source_words) >= 40:
            source_counts = Counter(source_words)
            answer_counts = Counter(answer_words)
            retained = sum(min(count, answer_counts[word]) for word, count in source_counts.items())
            coverage = retained / len(source_words)
            if coverage < 0.7:
                findings.append(
                    ValidationFinding(
                        rule_id="content.source_coverage",
                        severity=FindingSeverity.WARNING,
                        subject_id=unit.unit_id,
                        message=(
                            "The reshaped document retains only "
                            f"{coverage:.0%} of source wording; review semantic completeness"
                        ),
                        remedy=(
                            "Confirm that clearer wording preserves every supported rule, "
                            "restriction, exception, qualifier, and required action"
                        ),
                    )
                )

        source_facts = {
            self._normalize_material_fact(fact) for fact in _MATERIAL_FACT.findall(source_text)
        }
        answer_facts = {
            self._normalize_material_fact(fact) for fact in _MATERIAL_FACT.findall(unit.answer)
        }
        missing_facts = sorted(source_facts - answer_facts)
        if missing_facts:
            findings.append(
                self._blocking(
                    unit,
                    "content.material_fact",
                    "The reshaped document omits source values or durations: "
                    f"{', '.join(missing_facts[:8])}",
                )
            )

        answer_words_set = {word.casefold() for word in _WORD.findall(unit.answer)}
        omitted_clauses = []
        for clause in re.split(r"(?<=[.!?])\s+|\n+", source_text):
            if not _OPERATIVE_CLAUSE.search(clause):
                continue
            clause_words = {word.casefold() for word in _WORD.findall(clause)}
            if not clause_words:
                continue
            overlap = len(clause_words.intersection(answer_words_set)) / len(clause_words)
            if overlap < 0.6:
                omitted_clauses.append(clause[:120])
        if omitted_clauses:
            findings.append(
                self._blocking(
                    unit,
                    "content.operative_clause",
                    "The reshaped document omits or materially rewrites an operative clause: "
                    f"{omitted_clauses[0]}",
                )
            )
        source_clauses = _split_clauses(source_text)
        answer_clauses = _split_clauses(unit.answer)
        aligned_answer_clauses = _align_clauses(source_clauses, answer_clauses)
        reassigned_facts = any(
            {self._normalize_material_fact(fact) for fact in _MATERIAL_FACT.findall(source_clause)}
            != {
                self._normalize_material_fact(fact)
                for fact in _MATERIAL_FACT.findall(aligned_answer_clauses[source_index])
            }
            for source_index, source_clause in enumerate(source_clauses)
        )
        if reassigned_facts and not missing_facts:
            findings.append(
                self._blocking(
                    unit,
                    "content.material_fact",
                    "The reshaped document changes or relocates source values or durations",
                )
            )
        material_clauses = [
            (source_index, clause)
            for source_index, clause in enumerate(source_clauses)
            if len(_meaningful_words(clause)) >= _MATERIAL_CLAUSE_MIN_WORDS
        ]
        omitted_material_clauses = []
        for source_index, clause in material_clauses:
            clause_words = _meaningful_words(clause)
            related_answer_words = _meaningful_words(aligned_answer_clauses[source_index])
            overlap = len(clause_words.intersection(related_answer_words)) / len(clause_words)
            other_source_words = set().union(
                *(
                    _meaningful_words(other_clause)
                    for other_index, other_clause in enumerate(source_clauses)
                    if other_index != source_index
                )
            )
            distinguishing_words = clause_words - other_source_words
            distinguishing_coverage = (
                len(distinguishing_words.intersection(related_answer_words))
                / len(distinguishing_words)
                if distinguishing_words
                else 1.0
            )
            if (
                overlap < _CLAUSE_PRESERVATION_THRESHOLD
                or distinguishing_coverage < _CLAUSE_PRESERVATION_THRESHOLD
            ):
                omitted_material_clauses.append(clause[:120])
        if omitted_material_clauses:
            findings.append(
                self._blocking(
                    unit,
                    "content.material_clause",
                    "The reshaped document omits or materially rewrites a substantive "
                    f"source clause: {omitted_material_clauses[0]}",
                )
            )
        for rule_id, pattern, label in _PRESERVATION_CATEGORIES:
            omitted_category = any(
                pattern.search(source_clause)
                and not pattern.search(aligned_answer_clauses[source_index])
                for source_index, source_clause in enumerate(source_clauses)
            )
            if omitted_category:
                findings.append(
                    self._blocking(
                        unit,
                        rule_id,
                        f"The reshaped document omits source {label}",
                    )
                )
        permission_modal_changed = any(
            bool(pattern.search(aligned_answer_clauses[source_index]))
            != bool(pattern.search(source_clause))
            for pattern in _PERMISSION_MODAL_PATTERNS
            for source_index, source_clause in enumerate(source_clauses)
        )
        if permission_modal_changed and not any(
            finding.rule_id == "content.permission_clause" for finding in findings
        ):
            findings.append(
                self._blocking(
                    unit,
                    "content.permission_clause",
                    "The reshaped document changes or relocates a source permission modality",
                )
            )
        obligation_modal_changed = any(
            bool(_OBLIGATION_MODAL_PATTERN.search(aligned_answer_clauses[source_index]))
            != bool(_OBLIGATION_MODAL_PATTERN.search(source_clause))
            for source_index, source_clause in enumerate(source_clauses)
        )
        if obligation_modal_changed and not any(
            finding.rule_id == "content.operative_clause" for finding in findings
        ):
            findings.append(
                self._blocking(
                    unit,
                    "content.operative_clause",
                    "The reshaped document changes or relocates a mandatory source duty",
                )
            )
        prohibition_changed = any(
            bool(_PROHIBITION_PATTERN.search(aligned_answer_clauses[source_index]))
            != bool(_PROHIBITION_PATTERN.search(source_clause))
            for source_index, source_clause in enumerate(source_clauses)
        )
        if prohibition_changed and not any(
            finding.rule_id == "content.prohibition_clause" for finding in findings
        ):
            findings.append(
                self._blocking(
                    unit,
                    "content.prohibition_clause",
                    "The reshaped document reverses or relocates a source prohibition",
                )
            )
        named_modal_negation_changed = any(
            bool(_NEGATED_NAMED_MODAL_PATTERN.search(aligned_answer_clauses[source_index]))
            != bool(_NEGATED_NAMED_MODAL_PATTERN.search(source_clause))
            for source_index, source_clause in enumerate(source_clauses)
        )
        if named_modal_negation_changed:
            findings.append(
                self._blocking(
                    unit,
                    "content.operative_clause",
                    "The reshaped document changes the polarity of a named source modality",
                )
            )
        for label, pattern in _RESTRICTIVE_QUALIFIERS:
            omitted_qualifier = any(
                bool(pattern.search(aligned_answer_clauses[source_index]))
                != bool(pattern.search(source_clause))
                for source_index, source_clause in enumerate(source_clauses)
            )
            if omitted_qualifier:
                findings.append(
                    self._blocking(
                        unit,
                        "content.qualifier_clause",
                        f"The reshaped document omits a source {label} restriction",
                    )
                )
        return tuple(findings)

    @staticmethod
    def _normalize_material_fact(value: str) -> str:
        return re.sub(r"[\s,]+", "", value.casefold())

    @staticmethod
    def _blocking(unit: AnswerUnit, rule_id: str, message: str) -> ValidationFinding:
        return ValidationFinding(
            rule_id=rule_id,
            severity=FindingSeverity.BLOCKING,
            subject_id=unit.unit_id,
            message=message,
        )


def _split_clauses(text: str) -> list[str]:
    return [
        clause.strip()
        for clause in re.split(
            r"(?<=[.!?])\s+|\n+|(?:,\s+(?:and\s+)?|\s+and\s+)(?=(?:must|shall|"
            r"should|may|can|is\s+responsible\s+for)\b)",
            text,
            flags=re.IGNORECASE,
        )
        if clause.strip()
    ]


def _meaningful_words(text: str) -> set[str]:
    normalized = {_normalize_word(word) for word in _WORD.findall(text)}
    return normalized - _CLAUSE_STOP_WORDS


def _normalize_word(word: str) -> str:
    normalized = word.casefold()
    equivalent = _WORD_EQUIVALENTS.get(normalized)
    if equivalent is not None:
        return equivalent
    if len(normalized) > 3 and normalized.endswith("s") and not normalized.endswith("ss"):
        return normalized[:-1]
    return normalized


def _clause_overlap(source_clause: str, candidate_clause: str) -> float:
    source_words = _meaningful_words(source_clause) - _ALIGNMENT_CONTROL_WORDS
    if not source_words:
        return 0.0
    candidate_words = _meaningful_words(candidate_clause) - _ALIGNMENT_CONTROL_WORDS
    return len(source_words.intersection(candidate_words)) / len(source_words)


def _align_clauses(source_clauses: Sequence[str], candidate_clauses: Sequence[str]) -> list[str]:
    aligned_parts: list[list[str]] = [[] for _ in source_clauses]
    full_pairs = sorted(
        (
            (
                _clause_overlap(source_clause, candidate_clause),
                _control_similarity(source_clause, candidate_clause),
                source_index,
                candidate_index,
            )
            for source_index, source_clause in enumerate(source_clauses)
            for candidate_index, candidate_clause in enumerate(candidate_clauses)
            if len(_meaningful_words(candidate_clause)) >= _MATERIAL_CLAUSE_MIN_WORDS
            and _clause_overlap(source_clause, candidate_clause) >= _CLAUSE_PRESERVATION_THRESHOLD
        ),
        reverse=True,
    )
    assigned_sources: set[int] = set()
    assigned_candidates: set[int] = set()
    for _, _, source_index, candidate_index in full_pairs:
        if source_index in assigned_sources or candidate_index in assigned_candidates:
            continue
        aligned_parts[source_index].append(candidate_clauses[candidate_index])
        assigned_sources.add(source_index)
        assigned_candidates.add(candidate_index)

    for candidate_index, candidate_clause in enumerate(candidate_clauses):
        if candidate_index in assigned_candidates:
            continue
        overlap, _, source_index = max(
            (
                (
                    _clause_overlap(source_clause, candidate_clause),
                    _control_similarity(source_clause, candidate_clause),
                    source_index,
                )
                for source_index, source_clause in enumerate(source_clauses)
            ),
            default=(0.0, 0, 0),
        )
        if overlap < _CLAUSE_MATCH_THRESHOLD:
            continue
        aligned_parts[source_index].append(candidate_clause)
    return ["\n".join(parts) for parts in aligned_parts]


def _control_similarity(source_clause: str, candidate_clause: str) -> int:
    patterns = (
        _OBLIGATION_MODAL_PATTERN,
        _PROHIBITION_PATTERN,
        _NEGATED_NAMED_MODAL_PATTERN,
        *_PERMISSION_MODAL_PATTERNS,
        *(pattern for _, pattern in _RESTRICTIVE_QUALIFIERS),
    )
    return sum(
        1
        for pattern in patterns
        if pattern.search(source_clause) and pattern.search(candidate_clause)
    )
