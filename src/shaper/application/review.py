"""Human review policy and optimistic-concurrency state transitions."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from shaper.domain import (
    AnswerUnit,
    CollectionRole,
    FindingSeverity,
    Principal,
    ReviewDecision,
    UnitState,
    ValidationFinding,
)
from shaper.domain.models import ReviewOutcome, canonical_hash


class ReviewConflictError(RuntimeError):
    """Raised for stale or invalid review transitions."""


class RiskTier(StrEnum):
    """Review-policy risk tiers."""

    POLICY_RULE = "policy_rule"
    CONFLICTED = "conflicted"
    LOW_CONFIDENCE = "low_confidence"
    STANDARD = "standard"
    LOW_RISK_FAQ = "low_risk_faq"


@dataclass(frozen=True)
class ReviewRecord:
    """Current unit state and immutable decision history."""

    unit: AnswerUnit
    revision: int
    decisions: tuple[ReviewDecision, ...] = ()


class ReviewStore(Protocol):
    """Review persistence boundary."""

    def get(self, unit_id: str) -> ReviewRecord | None:
        """Return the current review record."""

    def save(self, record: ReviewRecord, *, expected_revision: int) -> ReviewRecord:
        """Persist an optimistic state transition."""


class InMemoryReviewStore:
    """Deterministic review store for local operation and contract tests."""

    def __init__(self) -> None:
        self._records: dict[str, ReviewRecord] = {}

    def get(self, unit_id: str) -> ReviewRecord | None:
        """Return a current record."""
        return self._records.get(unit_id)

    def save(self, record: ReviewRecord, *, expected_revision: int) -> ReviewRecord:
        """Save only when the expected revision is current."""
        current = self._records.get(record.unit.unit_id)
        current_revision = 0 if current is None else current.revision
        if current_revision != expected_revision:
            raise ReviewConflictError(
                f"Stale review revision: expected {expected_revision}, current {current_revision}"
            )
        saved = ReviewRecord(
            unit=record.unit,
            revision=current_revision + 1,
            decisions=record.decisions,
        )
        self._records[record.unit.unit_id] = saved
        return saved


@dataclass(frozen=True)
class ReviewPolicy:
    """Collection review policy with safe initial defaults."""

    thresholds_approved: bool = False
    standard_sample_rate: float = 0.20
    low_risk_sample_rate: float = 0.10

    def __post_init__(self) -> None:
        if self.standard_sample_rate < 0.20:
            raise ValueError("Standard-risk sample rate cannot be below 20 percent")
        if self.low_risk_sample_rate < 0.10:
            raise ValueError("Low-risk FAQ sample rate cannot be below 10 percent")

    def requires_review(self, unit: AnswerUnit, risk: RiskTier) -> bool:
        """Return whether this unit must receive human review."""
        if not self.thresholds_approved:
            return True
        if risk in {RiskTier.POLICY_RULE, RiskTier.CONFLICTED, RiskTier.LOW_CONFIDENCE}:
            return True
        rate = self.standard_sample_rate if risk is RiskTier.STANDARD else self.low_risk_sample_rate
        bucket = int(canonical_hash({"unit_id": unit.unit_id})[:8], 16) / 0xFFFFFFFF
        return bucket < rate


class ReviewService:
    """Apply review transitions without allowing the candidate producer to self-approve."""

    def __init__(self, store: ReviewStore, policy: ReviewPolicy | None = None) -> None:
        self._store = store
        self._policy = policy or ReviewPolicy()

    def submit(
        self,
        unit: AnswerUnit,
        findings: Sequence[ValidationFinding],
    ) -> ReviewRecord:
        """Route a candidate to review or quarantine."""
        state = (
            UnitState.QUARANTINED
            if any(finding.severity is FindingSeverity.BLOCKING for finding in findings)
            else UnitState.IN_REVIEW
        )
        updated = _with_state(unit, state)
        return self._store.save(ReviewRecord(updated, 0), expected_revision=0)

    def get(self, unit_id: str) -> ReviewRecord:
        """Return one current review record."""
        return self._record(unit_id)

    def decide(
        self,
        decision: ReviewDecision,
        *,
        expected_revision: int,
    ) -> ReviewRecord:
        """Authorize and apply one human review decision."""
        decision.actor.require(
            self._collection_id(decision.actor),
            CollectionRole.REVIEW,
        )
        record = self._record(decision.unit_id)
        if record.revision != expected_revision:
            raise ReviewConflictError(
                f"Stale review revision: expected {expected_revision}, current {record.revision}"
            )
        if record.unit.unit_version != decision.unit_version:
            raise ReviewConflictError("Review decision targets a stale unit version")
        target = {
            ReviewOutcome.APPROVE: UnitState.APPROVED,
            ReviewOutcome.REJECT: UnitState.REJECTED,
            ReviewOutcome.SUPERSEDE: UnitState.SUPERSEDED,
            ReviewOutcome.WITHDRAW: UnitState.WITHDRAWN,
        }[decision.outcome]
        if target is UnitState.APPROVED and record.unit.state is not UnitState.IN_REVIEW:
            raise ReviewConflictError("Only an in-review unit can be approved")
        updated = ReviewRecord(
            unit=_with_state(record.unit, target),
            revision=record.revision,
            decisions=(*record.decisions, decision),
        )
        return self._store.save(updated, expected_revision=expected_revision)

    def invalidate(
        self,
        unit_id: str,
        *,
        withdrawn: bool,
        expected_revision: int,
    ) -> ReviewRecord:
        """Supersede changed-source units or withdraw deleted/out-of-scope units."""
        record = self._record(unit_id)
        target = UnitState.WITHDRAWN if withdrawn else UnitState.SUPERSEDED
        return self._store.save(
            ReviewRecord(_with_state(record.unit, target), record.revision, record.decisions),
            expected_revision=expected_revision,
        )

    def publishable(self, unit_id: str, *, risk: RiskTier) -> bool:
        """Return whether validation and review policy permit publication."""
        record = self._record(unit_id)
        if record.unit.state is not UnitState.APPROVED:
            return False
        return not self._policy.requires_review(record.unit, risk) or bool(record.decisions)

    def _record(self, unit_id: str) -> ReviewRecord:
        record = self._store.get(unit_id)
        if record is None:
            raise KeyError(f"Review unit does not exist: {unit_id}")
        return record

    @staticmethod
    def _collection_id(actor: Principal) -> str:
        if len(actor.collection_roles) != 1:
            raise PermissionError("Reviewer identity must resolve to exactly one collection")
        return next(iter(actor.collection_roles))


def _with_state(unit: AnswerUnit, state: UnitState) -> AnswerUnit:
    values = unit.model_dump()
    values["state"] = state
    return AnswerUnit.model_validate(values)
