"""Read-only sample estate for the publicly testable product experience."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from shaper.application.orchestration import KnowledgeTransformationOrchestrator
from shaper.domain import (
    AuthorityStatus,
    BusinessAssertion,
    KnowledgeDocumentProfile,
    KnowledgeTransformationAnalysis,
)
from shaper.domain.models import DomainModel, Identifier


class DemoSourceEvidence(DomainModel):
    """Public metadata for one fixed source used by the live sample."""

    document_id: Identifier
    title: str
    content_type: str
    modified_at: datetime
    owner: str | None
    topic: str | None
    authority: AuthorityStatus


class DemoAnalysisResult(DomainModel):
    """Live sample inputs paired with the analysis they produced."""

    sample_kind: Literal["server_owned_fixed_sample"] = "server_owned_fixed_sample"
    sources: tuple[DemoSourceEvidence, ...]
    analysis: KnowledgeTransformationAnalysis


class DemoAnalysisService:
    """Run the real platform orchestrator over fixed, non-customer sample data."""

    def __init__(self, orchestrator: KnowledgeTransformationOrchestrator) -> None:
        profiles = _sample_profiles()
        self._result = DemoAnalysisResult(
            sources=tuple(
                DemoSourceEvidence(
                    document_id=profile.document_id,
                    title=profile.title,
                    content_type=profile.metadata.get("type", "Document"),
                    modified_at=profile.modified_at,
                    owner=profile.owner,
                    topic=profile.topic,
                    authority=profile.authority,
                )
                for profile in profiles
            ),
            analysis=orchestrator.analyze(
                collection_id="faqifier",
                profiles=profiles,
                assessed_at=datetime(2026, 9, 10, 10, 30, tzinfo=UTC),
            ),
        )

    def get(self) -> DemoAnalysisResult:
        """Return the immutable sample inputs and analysis."""
        return self._result


def _sample_profiles() -> tuple[KnowledgeDocumentProfile, ...]:
    return (
        KnowledgeDocumentProfile(
            document_id="travel-policy-v4",
            title="Travel Policy v4",
            text=(
                "# Travel policy\n\nEmployees must submit expenses within 30 days.\n\n"
                "1. Obtain manager approval.\n2. Submit receipts through the expense system."
            ),
            modified_at=datetime(2026, 7, 1, tzinfo=UTC),
            owner="Finance",
            metadata={"department": "Finance", "type": "Policy"},
            topic="Travel",
            authority=AuthorityStatus.AUTHORITATIVE,
            faq_count=2,
            procedure_step_count=2,
            assertions=(
                BusinessAssertion(
                    term="approval threshold",
                    value="GBP 100",
                    provenance="Travel Policy v4, approval section",
                ),
            ),
        ),
        KnowledgeDocumentProfile(
            document_id="emea-travel-rules",
            title="EMEA Travel Rules",
            text=(
                "TRAVEL RULES\n\nEmployees must submit expenses within thirty days. "
                "Manager approval is required before booking."
            ),
            modified_at=datetime(2022, 1, 1, tzinfo=UTC),
            owner=None,
            metadata={},
            topic="Travel",
            authority=AuthorityStatus.CANDIDATE,
            assertions=(
                BusinessAssertion(
                    term="approval threshold",
                    value="GBP 50",
                    provenance="EMEA Travel Rules, approval section",
                ),
            ),
        ),
        KnowledgeDocumentProfile(
            document_id="new-starter-faq",
            title="New Starter FAQ",
            text=(
                "# New starter questions\n\nWho orders my equipment? Your manager "
                "submits the request. Where do I complete training? Use the learning portal."
            ),
            modified_at=datetime(2025, 11, 20, tzinfo=UTC),
            owner="People Operations",
            metadata={"department": "HR", "type": "FAQ"},
            topic="Employee onboarding",
            authority=AuthorityStatus.CANDIDATE,
            faq_count=8,
        ),
    )
