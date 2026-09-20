"""Persistence and confidence comparison for document collaboration."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from shaper.application.assessment import DocumentAssessmentService
from shaper.application.estates import (
    EstateInventoryService,
    EstateRepository,
    EstateService,
    InventoryInput,
    PreparedInventoryItem,
    VersionedRecord,
)
from shaper.domain import (
    AuthorityStatus,
    CollectionRole,
    EstateDocument,
    KnowledgeDocumentProfile,
    KnowledgeEstate,
    Principal,
)

MAX_WORKING_COPY_CHARACTERS = 100_000


@dataclass(frozen=True)
class ConfidenceComparison:
    """Deterministic AI usability confidence comparison."""

    original: float
    revised: float
    delta: float
    direction: str


class DocumentCollaborationService:
    """Save revised text and compare its deterministic AI usability confidence."""

    def __init__(
        self,
        repository: EstateRepository,
        *,
        estates: EstateService,
        inventory: EstateInventoryService,
        assessments: DocumentAssessmentService,
        clock: Callable[[], datetime],
    ) -> None:
        self._repository = repository
        self._estates = estates
        self._inventory = inventory
        self._assessments = assessments
        self._clock = clock

    def save(
        self,
        *,
        estate_id: str,
        document_id: str,
        source_version: str,
        content: str,
        principal: Principal,
    ) -> VersionedRecord[EstateDocument]:
        """Save the working copy as a new immutable version of the current document."""
        estate, document_record, cleaned = self._validated(
            estate_id=estate_id,
            document_id=document_id,
            source_version=source_version,
            content=content,
            principal=principal,
        )
        document = document_record.value
        source_content = cleaned.encode("utf-8")
        version = hashlib.sha256(source_content).hexdigest()
        now = self._clock()
        filename = document.filename
        title = document.title
        media_type = document.media_type
        if document.media_type not in {"text/plain", "text/markdown"}:
            filename = f"{Path(document.filename).stem}-revised.txt"
            title = filename
            media_type = "text/plain"
        revised = EstateDocument.model_validate(
            {
                **document.model_dump(),
                "filename": filename,
                "title": title,
                "source_version": version,
                "content_hash": version,
                "media_type": media_type,
                "content_locator": f"repository-source:{document_id}:{version}",
                "modified_at": now,
                "discovered_at": now,
                "metadata": {
                    **document.metadata,
                    "collaboration_revision": "true",
                    "original_media_type": document.metadata.get(
                        "original_media_type", document.media_type
                    ),
                },
            }
        )
        return self._repository.save_inventory(
            (
                PreparedInventoryItem(
                    document=revised,
                    source_content=source_content,
                    extracted_text=cleaned,
                ),
            ),
            expected_revisions={document_id: document_record.revision},
        )[0]

    def save_as(
        self,
        *,
        estate_id: str,
        document_id: str,
        source_version: str,
        filename: str,
        content: str,
        principal: Principal,
    ) -> VersionedRecord[EstateDocument]:
        """Save the working copy as a new text document in the same source."""
        _estate, document_record, cleaned = self._validated(
            estate_id=estate_id,
            document_id=document_id,
            source_version=source_version,
            content=content,
            principal=principal,
        )
        document = document_record.value
        target = filename.strip()
        if not target:
            raise ValueError("A filename is required")
        if not target.casefold().endswith((".txt", ".md")):
            target += ".txt"
        media_type = "text/markdown" if target.casefold().endswith(".md") else "text/plain"
        return self._inventory.ingest(
            document.source_id,
            (
                InventoryInput(
                    filename=target,
                    media_type=media_type,
                    content=cleaned.encode("utf-8"),
                    logical_id=target,
                ),
            ),
            principal=principal,
            require_new=True,
            expected_revisions={document_id: document_record.revision},
        )[0]

    def compare_confidence(
        self,
        *,
        estate_id: str,
        document_id: str,
        source_version: str,
        content: str,
        principal: Principal,
    ) -> ConfidenceComparison:
        """Compare current and revised text using the deterministic assessment model."""
        estate, document_record, cleaned = self._validated(
            estate_id=estate_id,
            document_id=document_id,
            source_version=source_version,
            content=content,
            principal=principal,
            role=CollectionRole.QUERY,
            require_current=False,
        )
        document = document_record.value
        original_text = self._repository.load_document_content(document_id, source_version)
        original = self._score(estate.value.estate_id, document, original_text, "original")
        revised = self._score(estate.value.estate_id, document, cleaned, "working-copy")
        delta = round(revised - original, 1)
        direction = "improved" if delta > 0 else "regressed" if delta < 0 else "unchanged"
        return ConfidenceComparison(original, revised, delta, direction)

    def _score(
        self,
        estate_id: str,
        document: EstateDocument,
        text: str,
        label: str,
    ) -> float:
        report = self._assessments.report(
            run_id=f"collaboration-{label}",
            estate_id=estate_id,
            source_version=hashlib.sha256(text.encode("utf-8")).hexdigest(),
            profile=KnowledgeDocumentProfile(
                document_id=document.document_id,
                title=document.title,
                text=text,
                modified_at=document.modified_at,
                owner=document.owner,
                metadata=document.metadata,
                topic=document.metadata.get("topic"),
                authority=AuthorityStatus.UNKNOWN,
            ),
            assessed_at=self._clock(),
        )
        return report.readiness_score

    def _validated(
        self,
        *,
        estate_id: str,
        document_id: str,
        source_version: str,
        content: str,
        principal: Principal,
        role: CollectionRole = CollectionRole.COMPILE,
        require_current: bool = True,
    ) -> tuple[
        VersionedRecord[KnowledgeEstate],
        VersionedRecord[EstateDocument],
        str,
    ]:
        estate = self._estates.get(estate_id, principal=principal)
        principal.require(estate.value.collection_id, role)
        EstateService.require_active(estate.value)
        document = self._repository.get_document(document_id)
        if document is None or document.value.estate_id != estate_id or document.value.deleted:
            raise KeyError(f"Estate document does not exist: {document_id}")
        if require_current and document.value.source_version != source_version:
            raise ValueError("Requested source version is not current")
        if not require_current:
            self._repository.load_document_content(document_id, source_version)
        if not content.strip():
            raise ValueError("Revised document text is required")
        if len(content) > MAX_WORKING_COPY_CHARACTERS:
            raise ValueError(
                f"Revised document exceeds the {MAX_WORKING_COPY_CHARACTERS} character limit"
            )
        return estate, document, content
