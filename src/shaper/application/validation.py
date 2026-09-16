"""Deterministic candidate validation rules."""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Sequence

from shaper.application.document_findings import unsafe_source_content_matches
from shaper.domain import AnswerUnit, FindingSeverity, SourceSpan, ValidationFinding

_WORD = re.compile(r"\b[\w'-]+\b", re.UNICODE)
_MATERIAL_FACT = re.compile(
    r"(?:[$£€]\s?\d[\d,.]*|\b\d[\d,.]*(?!\s*\(\s*[a-z]\s*\))\s?"
    r"(?:%|percent|days?|weeks?|months?|years?|hours?)?\b)",
    re.IGNORECASE,
)
_LEADING_ENUMERATOR = re.compile(r"(?im)^\s*(?:#{1,6}\s*)?(?:(?:step|question)\s+)?\d+[.):]\s+")
_REVIEW_NOTES_HEADING = re.compile(r"(?im)^#{1,6}\s+missing information and review notes\s*$")
_REVIEW_NOTE_ITEM = re.compile(
    r"^\s*[-*]\s+(?:missing|ambiguity|conflict|unresolved reference|review required):\s+\S",
    re.IGNORECASE,
)
_INTENTIONAL_EXCLUSION_NOTE = "Review required: Intentional exclusion: "
_POLICY_DECLARATION = re.compile(
    r"\b(?:employees?|managers?|supervisors?|contractors?|hr|human resources|"
    r"(?:the\s+)?(?:company|organization|employer|department|team))\b"
    r"(?:\s+[\w'-]+){0,3}\s+"
    r"(?:approve|submit|receive|retain|provide|enroll|access|complete|follow|"
    r"notify|request|review|pay|reimburse|apply|use|work)\b",
    re.IGNORECASE,
)
_POLICY_STATUS = re.compile(
    r"\b(?:employees?|managers?|supervisors?|contractors?|hr|human resources|"
    r"(?:the\s+)?(?:company|organization|employer|department|team))\b"
    r"(?:\s+[\w'-]+){0,3}\s+"
    r"(?:are|become|remain)\s+(?:eligible|ineligible|available|unavailable)\b",
    re.IGNORECASE,
)
_POLICY_APPLICABILITY = re.compile(
    r"\b(?:benefit|policy|coverage|plan|program)\b(?:\s+[\w'-]+){0,3}\s+appl(?:y|ies)\b",
    re.IGNORECASE,
)
_POLICY_PASSIVE_OUTCOME = re.compile(
    r"\b(?:claims?|benefits?|expenses?|payments?|reimbursements?|requests?|applications?)\b"
    r"(?:\s+[\w'-]+){0,3}\s+"
    r"(?:are|is|were|was)\s+"
    r"(?:paid|approved|processed|provided|reimbursed|granted|denied)\b",
    re.IGNORECASE,
)
_RHETORICAL_OR_PROMOTIONAL_CLAUSE = re.compile(
    r"\b(?:we(?:'re| are)\s+confident|you(?:'ll| will)\s+agree|"
    r"explore\s+everything\s+(?:below|above)|sets?\s+the\s+standard|"
    r"best[- ]in[- ]class|industry[- ]leading|one\s+of\s+the\s+best|"
    r"ranked\s+among\s+the\s+most)\b",
    re.IGNORECASE,
)
_IDENTIFIER = re.compile(r"\b\d{3,5}\s*\(\s*[a-z]\s*\)", re.IGNORECASE)
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
        *,
        approved_source_exclusions: Sequence[str] = (),
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
        findings.extend(self._exclusion_findings(unit, approved_source_exclusions))
        preservation_source = _without_excluded_slices(source_text, approved_source_exclusions)
        findings.extend(
            self._preservation_findings(
                unit,
                preservation_source,
                approved_source_exclusions=approved_source_exclusions,
            )
        )
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

    def _exclusion_findings(
        self,
        unit: AnswerUnit,
        approved_source_exclusions: Sequence[str],
    ) -> Sequence[ValidationFinding]:
        """Require every authorized source exclusion to be audited and absent from policy."""
        if not approved_source_exclusions:
            return ()
        findings: list[ValidationFinding] = []
        substantive = _normalized_prose(_substantive_answer(unit.answer))
        review_notes = _review_notes(unit.answer)
        for exclusion in approved_source_exclusions:
            if _normalized_prose(exclusion) in substantive:
                findings.append(
                    self._blocking(
                        unit,
                        "content.approved_exclusion_retained",
                        "The reshaped document retains an approved exclusion in substantive "
                        f"policy: {exclusion[:120]}",
                    )
                )
            expected_note = f"{_INTENTIONAL_EXCLUSION_NOTE}{exclusion}"
            if not any(line.strip() == f"- {expected_note}" for line in review_notes.splitlines()):
                findings.append(
                    self._blocking(
                        unit,
                        "content.approved_exclusion_note",
                        "The reshaped document omits the required intentional-exclusion "
                        f"review note: {exclusion[:120]}",
                    )
                )
        unsafe_retention = unsafe_source_content_matches(_substantive_answer(unit.answer))
        if unsafe_retention:
            _, retained, _ = unsafe_retention[0]
            findings.append(
                self._blocking(
                    unit,
                    "content.approved_exclusion_retained",
                    "The reshaped document retains or rewrites unsafe excluded content in "
                    f"substantive policy: {retained[:120]}",
                )
            )
        return tuple(findings)

    def _preservation_findings(
        self,
        unit: AnswerUnit,
        source_text: str,
        *,
        approved_source_exclusions: Sequence[str] = (),
    ) -> Sequence[ValidationFinding]:
        """Block candidates that compress or omit material source content."""
        findings: list[ValidationFinding] = []
        review_notes_issue = _review_notes_structure_issue(unit.answer)
        if review_notes_issue is not None:
            findings.append(
                ValidationFinding(
                    rule_id="content.review_notes_structure",
                    severity=FindingSeverity.WARNING,
                    subject_id=unit.unit_id,
                    message=review_notes_issue,
                    remedy="Use one final review-notes section with labelled bullet items",
                )
            )
        review_notes_policy_issue = _review_notes_policy_issue(
            unit.answer,
            approved_source_exclusions=approved_source_exclusions,
        )
        if review_notes_policy_issue is not None:
            findings.append(
                ValidationFinding(
                    rule_id="content.review_notes_policy",
                    severity=FindingSeverity.WARNING,
                    subject_id=unit.unit_id,
                    message=review_notes_policy_issue,
                    remedy=(
                        "Keep review notes non-policy and preserve policy in the substantive answer"
                    ),
                )
            )
        answer_text = _substantive_answer(unit.answer)
        source_words = [word.casefold() for word in _WORD.findall(source_text)]
        answer_words = [word.casefold() for word in _WORD.findall(answer_text)]
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

        source_facts = _material_facts(source_text)
        answer_facts = _material_facts(answer_text)
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
        introduced_facts = sorted(answer_facts - source_facts)
        if introduced_facts:
            findings.append(
                self._blocking(
                    unit,
                    "content.material_fact",
                    "The reshaped document introduces source-unsupported values or durations: "
                    f"{', '.join(introduced_facts[:8])}",
                )
            )
        source_identifiers = _identifiers(source_text)
        answer_identifiers = _identifiers(answer_text)
        missing_identifiers = sorted(source_identifiers - answer_identifiers)
        introduced_identifiers = sorted(answer_identifiers - source_identifiers)
        if missing_identifiers or introduced_identifiers:
            detail = (
                f"omits source identifiers: {', '.join(missing_identifiers[:8])}"
                if missing_identifiers
                else "introduces source-unsupported identifiers: "
                f"{', '.join(introduced_identifiers[:8])}"
            )
            findings.append(
                self._blocking(
                    unit,
                    "content.identifier",
                    f"The reshaped document {detail}",
                )
            )

        answer_words_set = {word.casefold() for word in _WORD.findall(answer_text)}
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
        answer_clauses = _split_clauses(answer_text)
        reassigned_fact_clause = next(
            (
                source_clause
                for source_index, source_clause in enumerate(source_clauses)
                if (source_clause_facts := _material_facts(source_clause))
                and not source_clause_facts
                <= set().union(
                    *(
                        _material_facts(candidate_clause)
                        for candidate_clause in _matching_clauses(
                            source_clause,
                            answer_clauses,
                            source_clauses,
                        )
                    )
                )
            ),
            None,
        )
        if reassigned_fact_clause is not None and not missing_facts:
            findings.append(
                self._blocking(
                    unit,
                    "content.material_fact",
                    "The reshaped document changes or relocates source values or durations. "
                    f"Source clause to preserve: {reassigned_fact_clause[:120]}",
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
            other_source_words = set().union(
                *(
                    _meaningful_words(other_clause)
                    for other_index, other_clause in enumerate(source_clauses)
                    if other_index != source_index
                )
            )
            distinguishing_words = clause_words - other_source_words
            candidate_matches = _related_answer_clauses(
                clause,
                answer_clauses,
                source_clauses,
            )
            clause_preserved = any(
                _word_coverage(clause_words, _meaningful_words(candidate_clause))
                >= _CLAUSE_PRESERVATION_THRESHOLD
                and (
                    not distinguishing_words
                    or _word_coverage(
                        distinguishing_words,
                        _meaningful_words(candidate_clause),
                    )
                    >= _CLAUSE_PRESERVATION_THRESHOLD
                )
                for candidate_clause in candidate_matches
            )
            if not clause_preserved and len(source_clauses) == 1:
                pooled_answer_words = set().union(
                    *(_meaningful_words(answer_clause) for answer_clause in answer_clauses)
                )
                clause_preserved = _word_coverage(
                    clause_words, pooled_answer_words
                ) >= _CLAUSE_PRESERVATION_THRESHOLD and (
                    not distinguishing_words
                    or _word_coverage(distinguishing_words, pooled_answer_words)
                    >= _CLAUSE_PRESERVATION_THRESHOLD
                )
            if not clause_preserved:
                omitted_material_clauses.append(clause[:120])
        if omitted_material_clauses:
            findings.append(
                ValidationFinding(
                    rule_id="content.material_clause",
                    severity=FindingSeverity.WARNING,
                    subject_id=unit.unit_id,
                    message=(
                        "The reshaped document omits or materially rewrites a substantive "
                        f"source clause: {omitted_material_clauses[0]}"
                    ),
                    remedy="Review semantic completeness against the source evidence",
                )
            )
        for rule_id, pattern, label in _PRESERVATION_CATEGORIES:
            omitted_category_clause = next(
                (
                    source_clause
                    for source_index, source_clause in enumerate(source_clauses)
                    if _has_policy_bearing_anchor(source_clause)
                    and pattern.search(source_clause)
                    and not _preserves_pattern(
                        source_clause,
                        answer_clauses,
                        source_clauses,
                        pattern,
                    )
                ),
                None,
            )
            if omitted_category_clause is not None:
                findings.append(
                    self._blocking(
                        unit,
                        rule_id,
                        f"The reshaped document omits source {label}. "
                        f"Source clause to preserve: {omitted_category_clause[:120]}",
                    )
                )
        permission_modal_changed = any(
            _pattern_association_changed(
                pattern,
                source_clauses,
                answer_clauses,
            )
            for pattern in _PERMISSION_MODAL_PATTERNS
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
        obligation_modal_changed = _pattern_association_changed(
            _OBLIGATION_MODAL_PATTERN,
            source_clauses,
            answer_clauses,
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
        prohibition_changed = _pattern_association_changed(
            _PROHIBITION_PATTERN,
            source_clauses,
            answer_clauses,
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
        named_modal_negation_changed = _pattern_association_changed(
            _NEGATED_NAMED_MODAL_PATTERN,
            source_clauses,
            answer_clauses,
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
            changed_qualifier_clause = next(
                (
                    source_clause
                    for source_index, source_clause in enumerate(source_clauses)
                    if _has_policy_bearing_anchor(source_clause)
                    and pattern.search(source_clause)
                    and not _preserves_pattern(
                        source_clause,
                        answer_clauses,
                        source_clauses,
                        pattern,
                    )
                ),
                None,
            )
            if changed_qualifier_clause is not None or _pattern_association_changed(
                pattern,
                source_clauses,
                answer_clauses,
                policy_anchor_required=True,
            ):
                excerpt = (
                    f" Source clause to preserve: {changed_qualifier_clause[:120]}"
                    if changed_qualifier_clause is not None
                    else ""
                )
                findings.append(
                    self._blocking(
                        unit,
                        "content.qualifier_clause",
                        f"The reshaped document changes or omits a source {label} restriction."
                        f"{excerpt}",
                    )
                )
        return tuple(findings)

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
            r"(?<=[.!?])\s+|\n+|;\s+|"
            r",\s+(?:and|but|while|whereas)\s+(?=[\w'-]+\s+(?:must|shall|should|"
            r"may|can|will|is|are|has|have|receive|receives|access|submit|submits)\b)|"
            r"\s+(?:while|whereas)\s+(?=[\w'-]+\s+(?:must|shall|should|may|can|will|"
            r"is|are|has|have|receive|receives|access|submit|submits)\b)|"
            r"(?:,\s+(?:and\s+)?|\s+and\s+)(?=(?:must|shall|"
            r"should|may|can|is\s+responsible\s+for)\b)",
            text,
            flags=re.IGNORECASE,
        )
        if clause.strip()
    ]


def _substantive_answer(answer: str) -> str:
    review_notes = _REVIEW_NOTES_HEADING.search(answer)
    if review_notes is None:
        return answer
    return answer[: review_notes.start()].rstrip()


def _review_notes(answer: str) -> str:
    review_notes = _REVIEW_NOTES_HEADING.search(answer)
    return "" if review_notes is None else answer[review_notes.end() :]


def _without_excluded_slices(source_text: str, exclusions: Sequence[str]) -> str:
    for exclusion in exclusions:
        source_text = source_text.replace(exclusion, "")
    return source_text


def _review_notes_structure_issue(answer: str) -> str | None:
    headings = tuple(_REVIEW_NOTES_HEADING.finditer(answer))
    if not headings:
        return None
    if len(headings) > 1:
        return "The reshaped document contains more than one review-notes section"
    notes = answer[headings[0].end() :].strip()
    if not notes:
        return "The reshaped document has an empty review-notes section"
    if re.search(r"(?m)^#{1,6}\s+", notes):
        return "The reshaped document places another section after review notes"
    for line in notes.splitlines():
        if not line.strip():
            continue
        if not _REVIEW_NOTE_ITEM.match(line):
            return (
                "Review notes must use labelled bullet items and contain no "
                "source-backed policy content"
            )
    return None


def _review_notes_policy_issue(
    answer: str,
    *,
    approved_source_exclusions: Sequence[str],
) -> str | None:
    approved_audit_notes = {
        _normalized_prose(f"- {_INTENTIONAL_EXCLUSION_NOTE}{exclusion}")
        for exclusion in approved_source_exclusions
    }
    for line in _review_notes(answer).splitlines():
        stripped = line.strip()
        if not stripped or _normalized_prose(stripped) in approved_audit_notes:
            continue
        note = re.sub(r"^[-*]\s+[^:]+:\s*", "", stripped)
        if (
            _MATERIAL_FACT.search(note)
            or _OPERATIVE_CLAUSE.search(note)
            or _POLICY_DECLARATION.search(note)
            or any(pattern.search(note) for _, pattern in _RESTRICTIVE_QUALIFIERS)
        ):
            return (
                "Review notes cannot introduce or restate policy values, duties, permissions, "
                "prohibitions, or restrictive qualifiers"
            )
    return None


def _material_facts(text: str) -> set[str]:
    without_enumerators = _LEADING_ENUMERATOR.sub("", text)
    return {
        re.sub(r"[\s,]+", "", fact.casefold())
        for fact in _MATERIAL_FACT.findall(without_enumerators)
    }


def _identifiers(text: str) -> set[str]:
    return {re.sub(r"\s+", "", identifier.casefold()) for identifier in _IDENTIFIER.findall(text)}


def _normalized_prose(text: str) -> str:
    return " ".join(text.casefold().split())


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


def _word_coverage(required_words: set[str], candidate_words: set[str]) -> float:
    if not required_words:
        return 1.0
    return len(required_words.intersection(candidate_words)) / len(required_words)


def _matching_clauses(
    source_clause: str,
    candidate_clauses: Sequence[str],
    peer_source_clauses: Sequence[str] = (),
    identity_threshold: float = _CLAUSE_PRESERVATION_THRESHOLD,
) -> tuple[str, ...]:
    source_identity_words = _identity_words(source_clause, peer_source_clauses)
    return tuple(
        candidate_clause
        for candidate_clause in candidate_clauses
        if _is_policy_clause(candidate_clause)
        and _clause_overlap(source_clause, candidate_clause) >= _CLAUSE_MATCH_THRESHOLD
        and _word_coverage(
            source_identity_words,
            _meaningful_words(candidate_clause) - _ALIGNMENT_CONTROL_WORDS,
        )
        >= identity_threshold
    )


def _identity_words(source_clause: str, peer_source_clauses: Sequence[str]) -> set[str]:
    source_words = _meaningful_words(source_clause) - _ALIGNMENT_CONTROL_WORDS
    other_source_words = set().union(
        *(
            _meaningful_words(peer_clause) - _ALIGNMENT_CONTROL_WORDS
            for peer_clause in peer_source_clauses
            if peer_clause != source_clause
        )
    )
    distinguishing_words = source_words - other_source_words
    return distinguishing_words or source_words


def _related_answer_clauses(
    source_clause: str,
    answer_clauses: Sequence[str],
    source_clauses: Sequence[str],
    identity_threshold: float = _CLAUSE_PRESERVATION_THRESHOLD,
) -> tuple[str, ...]:
    return _matching_clauses(
        source_clause,
        answer_clauses,
        source_clauses,
        identity_threshold,
    )


def _preserves_pattern(
    source_clause: str,
    answer_clauses: Sequence[str],
    source_clauses: Sequence[str],
    pattern: re.Pattern[str],
) -> bool:
    return any(
        pattern.search(candidate_clause)
        for candidate_clause in _related_answer_clauses(
            source_clause,
            answer_clauses,
            source_clauses,
            identity_threshold=0.75,
        )
    )


def _pattern_association_changed(
    pattern: re.Pattern[str],
    source_clauses: Sequence[str],
    answer_clauses: Sequence[str],
    *,
    policy_anchor_required: bool = False,
) -> bool:
    policy_filter = _has_policy_bearing_anchor if policy_anchor_required else _is_policy_clause
    source_policy_clauses = tuple(
        source_clause for source_clause in source_clauses if policy_filter(source_clause)
    )
    answer_policy_clauses = tuple(
        answer_clause for answer_clause in answer_clauses if policy_filter(answer_clause)
    )
    if any(
        pattern.search(source_clause)
        and not _preserves_pattern(
            source_clause,
            answer_policy_clauses,
            source_policy_clauses,
            pattern,
        )
        for source_index, source_clause in enumerate(source_clauses)
        if policy_filter(source_clause)
    ):
        return True
    return any(
        pattern.search(answer_clause)
        and not any(
            pattern.search(source_clause)
            and answer_clause
            in _matching_clauses(
                source_clause,
                (answer_clause,),
                source_policy_clauses,
                identity_threshold=0.75,
            )
            for source_clause in source_policy_clauses
        )
        for answer_clause in answer_policy_clauses
    )


def _is_policy_clause(clause: str) -> bool:
    return not clause.rstrip().endswith(("?", ":"))


def _has_policy_bearing_anchor(clause: str) -> bool:
    """Exclude rhetorical and promotional prose from qualifier checks."""
    if clause.lstrip().startswith("#") or clause.rstrip().endswith("?"):
        return False
    return bool(clause.strip()) and not _RHETORICAL_OR_PROMOTIONAL_CLAUSE.search(clause)


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
