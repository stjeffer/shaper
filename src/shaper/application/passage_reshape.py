"""Focused single-passage reshaping for the assessment review workspace."""

from __future__ import annotations

from dataclasses import dataclass

from shaper.application.document_findings import ASSESSMENT_CHECKS
from shaper.application.estates import EstateRepository, EstateService
from shaper.application.ports import ModelGateway
from shaper.domain import CollectionRole, Principal
from shaper.prompts import PASSAGE_RESHAPE_PROMPT

MAX_PASSAGE_CHARACTERS = 4000
MAX_CONTEXT_CHARACTERS = 6000

PASSAGE_RESHAPE_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "replacement": {
            "type": "string",
            "description": "The rewritten passage, plain text, ready to replace the original.",
        },
        "rationale": {
            "type": "string",
            "description": (
                "One or two sentences explaining what changed and any detail a human "
                "must still supply."
            ),
        },
    },
}

_CHECK_LABELS = {check.code: check for check in ASSESSMENT_CHECKS}


@dataclass(frozen=True)
class PassageSuggestion:
    """A model-suggested replacement for one reviewed passage."""

    replacement: str
    rationale: str
    finding_code: str | None
    source_version: str
    response_id: str
    input_tokens: int
    output_tokens: int


class PassageReshapeService:
    """Suggest a replacement for one evidence passage without mutating the source."""

    def __init__(
        self,
        repository: EstateRepository,
        *,
        estates: EstateService,
        model: ModelGateway,
        max_output_tokens: int = 900,
    ) -> None:
        self._repository = repository
        self._estates = estates
        self._model = model
        self._max_output_tokens = max_output_tokens

    def suggest(
        self,
        *,
        estate_id: str,
        document_id: str,
        source_version: str,
        finding_code: str | None,
        passage: str,
        principal: Principal,
    ) -> PassageSuggestion:
        """Return a suggested rewrite for one passage of a current document version."""
        estate = self._estates.get(estate_id, principal=principal)
        principal.require(estate.value.collection_id, CollectionRole.COMPILE)

        cleaned = passage.strip()
        if not cleaned:
            raise ValueError("Passage text is required")
        if len(cleaned) > MAX_PASSAGE_CHARACTERS:
            raise ValueError(
                f"Passage exceeds the {MAX_PASSAGE_CHARACTERS} character reshaping limit"
            )

        document = self._repository.get_document(document_id)
        if document is None or document.value.estate_id != estate_id or document.value.deleted:
            raise KeyError(f"Estate document does not exist: {document_id}")
        if document.value.source_version != source_version:
            raise ValueError("Requested source version is not current")

        content = self._repository.load_document_content(document_id, source_version)
        context = content[:MAX_CONTEXT_CHARACTERS]

        check = _CHECK_LABELS.get(finding_code or "")
        concern = (
            f"{check.label}: {check.what_it_checks} {check.agent_impact}"
            if check is not None
            else "The passage weakens agent retrieval."
        )

        prompt = (
            f"Document title: {document.value.title}\n"
            f"Assessment concern: {concern}\n\n"
            "Surrounding document text (context only, do not rewrite it):\n"
            f"{context}\n\n"
            "Passage to rewrite:\n"
            f"{cleaned}\n"
        )

        result = self._model.generate(
            system_prompt=PASSAGE_RESHAPE_PROMPT,
            prompt=prompt,
            schema=PASSAGE_RESHAPE_SCHEMA,
            max_output_tokens=self._max_output_tokens,
        )
        replacement = str(result.payload.get("replacement", "")).strip()
        rationale = str(result.payload.get("rationale", "")).strip()
        if not replacement:
            raise ValueError("The model returned no replacement text for this passage")

        return PassageSuggestion(
            replacement=replacement,
            rationale=rationale,
            finding_code=finding_code,
            source_version=source_version,
            response_id=result.response_id,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
        )
