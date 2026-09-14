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
    r"\b(?:must|must not|shall|shall not|required|prohibited|may only|cannot|"
    r"will not|is responsible for)\b",
    re.IGNORECASE,
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
                    self._blocking(
                        unit,
                        "content.source_coverage",
                        "The reshaped document retains only "
                        f"{coverage:.0%} of source wording; preserve the complete document "
                        "instead of summarizing it",
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
