"""Pre-transformation human decision service."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from uuid import uuid4

from shaper.application.estates import EstateRepository, EstateService
from shaper.domain import (
    CollectionRole,
    DecisionOutcome,
    Principal,
    TransformationDecision,
    TransformationProposal,
)


class TransformationDecisionService:
    """Record immutable decisions separately from post-output review."""

    def __init__(
        self,
        repository: EstateRepository,
        *,
        clock: Callable[[], datetime],
        id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._repository = repository
        self._clock = clock
        self._id_factory = id_factory or (lambda: uuid4().hex)

    def decide(
        self,
        recommendation_id: str,
        *,
        principal: Principal,
        outcome: DecisionOutcome,
        reason: str,
        expected_current_decision_id: str | None,
    ) -> TransformationDecision:
        """Approve or decline the exact current proposal using optimistic intent."""
        proposal = self._proposal(recommendation_id)
        estate = self._repository.get_estate(proposal.estate_id)
        if estate is None:
            raise KeyError(f"Knowledge estate does not exist: {proposal.estate_id}")
        EstateService._authorize(estate.value, principal, CollectionRole.REVIEW)
        EstateService.require_active(estate.value)
        document = self._repository.get_document(proposal.document_id)
        if (
            document is None
            or document.value.deleted
            or document.value.source_version != proposal.source_version
        ):
            raise StaleProposalError(
                "The source document changed or was withdrawn after recommendation"
            )
        current = self._repository.latest_decision(proposal.document_id)
        current_id = None if current is None else current.decision_id
        if current_id != expected_current_decision_id:
            raise DecisionConflictError(
                f"Decision changed: expected {expected_current_decision_id!r}, "
                f"current {current_id!r}"
            )
        estimate = proposal.token_estimate
        decision = TransformationDecision(
            decision_id=f"decision-{self._id_factory()}",
            estate_id=proposal.estate_id,
            document_id=proposal.document_id,
            source_version=proposal.source_version,
            recommendation_version=proposal.recommendation_version,
            estimate_id=estimate.estimate_id,
            estimator_version=estimate.estimator_version,
            model_deployment=estimate.model_deployment,
            outcome=outcome,
            reason=reason,
            decided_by=principal.principal_id,
            decided_at=self._clock(),
        )
        self._repository.append_decision(decision)
        return decision

    def current(
        self,
        recommendation_id: str,
        *,
        principal: Principal,
    ) -> tuple[TransformationDecision | None, bool]:
        """Return the latest decision and whether it still authorizes the proposal."""
        proposal = self._proposal(recommendation_id)
        estate = self._repository.get_estate(proposal.estate_id)
        if estate is None:
            raise KeyError(f"Knowledge estate does not exist: {proposal.estate_id}")
        EstateService._authorize(estate.value, principal, CollectionRole.QUERY)
        decision = self._repository.latest_decision(proposal.document_id)
        return decision, decision.permits(proposal) if decision is not None else False

    def _proposal(self, recommendation_id: str) -> TransformationProposal:
        proposal = self._repository.get_proposal(recommendation_id)
        if proposal is None:
            raise KeyError(f"Transformation proposal does not exist: {recommendation_id}")
        return proposal


class DecisionConflictError(RuntimeError):
    """Raised when decision state changed since the caller last read it."""


class StaleProposalError(RuntimeError):
    """Raised when proposal evidence no longer matches the current source."""
