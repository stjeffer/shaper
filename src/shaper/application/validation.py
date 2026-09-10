"""Deterministic candidate validation rules."""

from __future__ import annotations

from collections.abc import Sequence

from shaper.domain import AnswerUnit, FindingSeverity, SourceSpan, ValidationFinding


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

    @staticmethod
    def _blocking(unit: AnswerUnit, rule_id: str, message: str) -> ValidationFinding:
        return ValidationFinding(
            rule_id=rule_id,
            severity=FindingSeverity.BLOCKING,
            subject_id=unit.unit_id,
            message=message,
        )
