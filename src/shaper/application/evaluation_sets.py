"""Deterministic, source-grounded evaluation question generation."""

from __future__ import annotations

import re
from collections.abc import Sequence

from pydantic import BaseModel, ConfigDict

from shaper.application.estates import EstateRepository, EstateService
from shaper.domain import CollectionRole, Principal, WorkflowKind

EVALUATION_QUESTION_TARGET = 20
MAX_PASSAGE_CHARACTERS = 1000
MIN_PASSAGE_CHARACTERS = 20
_EXCLUDED_KEYWORDS = frozenset(
    {
        "about",
        "after",
        "before",
        "from",
        "have",
        "must",
        "shall",
        "that",
        "their",
        "there",
        "these",
        "this",
        "with",
    }
)


class EvaluationSuggestion(BaseModel):
    """One source-grounded candidate question for downstream evaluation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    document_id: str
    source_version: str
    source_reference: str
    query: str
    ground_truth: str
    context: str
    keywords: tuple[str, ...]
    foundry_evaluators: tuple[str, ...] = (
        "groundedness",
        "relevance",
        "completeness",
    )
    copilot_studio_methods: tuple[str, ...] = (
        "General quality",
        "Compare meaning",
        "Keyword match",
    )
    needs_sme_review: bool = True


class EvaluationSet(BaseModel):
    """A bounded evaluation set and any source-specific generation errors."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    estate_id: str
    recommendation_run_id: str
    target: int = EVALUATION_QUESTION_TARGET
    items: tuple[EvaluationSuggestion, ...]
    errors: tuple[str, ...] = ()


class EvaluationSetService:
    """Generate evaluation questions from current proposal source versions."""

    def __init__(self, repository: EstateRepository) -> None:
        self._repository = repository

    def generate(
        self,
        estate_id: str,
        recommendation_run_id: str,
        *,
        principal: Principal,
    ) -> EvaluationSet:
        """Return a balanced, deterministic set for one recommendation run."""
        estate = self._repository.get_estate(estate_id)
        if estate is None:
            raise KeyError(f"Knowledge estate does not exist: {estate_id}")
        EstateService._authorize(estate.value, principal, CollectionRole.QUERY)
        run = self._repository.get_run(recommendation_run_id)
        if (
            run is None
            or run.value.estate_id != estate_id
            or run.value.kind is not WorkflowKind.RECOMMEND
        ):
            raise KeyError("Recommendation run does not belong to this estate")

        candidates: list[EvaluationSuggestion] = []
        errors: list[str] = []
        for proposal in self._repository.list_proposals(recommendation_run_id):
            document = self._repository.get_document(proposal.document_id)
            if (
                document is None
                or document.value.deleted
                or document.value.source_version != proposal.source_version
            ):
                errors.append(
                    f"The current source document for {proposal.expected_artifact} is unavailable."
                )
                continue
            try:
                source_text = self._repository.load_document_content(
                    document.value.document_id,
                    document.value.source_version,
                )
            except KeyError:
                errors.append(
                    f"Suggestions for {document.value.title} could not be created because "
                    "the source text is unavailable."
                )
                continue
            candidates.extend(
                suggested_evaluations(
                    proposal.recommendation_id,
                    document.value.document_id,
                    document.value.source_version,
                    document.value.title,
                    source_text,
                )
            )

        return EvaluationSet(
            estate_id=estate_id,
            recommendation_run_id=recommendation_run_id,
            items=tuple(_round_robin(candidates, EVALUATION_QUESTION_TARGET)),
            errors=tuple(errors),
        )


def suggested_evaluations(
    recommendation_id: str,
    document_id: str,
    source_version: str,
    document_title: str,
    source_text: str,
) -> tuple[EvaluationSuggestion, ...]:
    """Generate up to the target number of distinct questions for one document."""
    candidates: list[EvaluationSuggestion] = []
    seen_questions: set[str] = set()
    for heading, passage in _evaluation_passages(source_text):
        keywords = _evaluation_keywords(passage)
        fallback = " ".join(passage.split()[:7])
        detail = ", ".join(keywords[:3]) or fallback
        topic = f"{heading}: {detail}" if heading else detail
        query = f"What does {document_title} say about {topic}?"
        normalized = query.casefold()
        if normalized in seen_questions:
            continue
        seen_questions.add(normalized)
        candidates.append(
            EvaluationSuggestion(
                id=f"{recommendation_id}-evaluation-{len(candidates) + 1}",
                document_id=document_id,
                source_version=source_version,
                source_reference=f"{document_id}@{source_version}",
                query=query,
                ground_truth=passage,
                context=passage,
                keywords=tuple(_evaluation_keywords(f"{heading} {passage}")),
            )
        )
    return tuple(_evenly_select(candidates, EVALUATION_QUESTION_TARGET))


def _evaluation_passages(source_text: str) -> tuple[tuple[str, str], ...]:
    passages: list[tuple[str, str]] = []
    heading = ""
    for part in (item.strip() for item in re.split(r"\n\s*\n", source_text)):
        if not part:
            continue
        heading_match = re.match(r"^#{1,6}\s+([^\n]+)(?:\n+([\s\S]+))?$", part)
        content = part
        if heading_match:
            heading = heading_match.group(1).strip()
            content = (heading_match.group(2) or "").strip()
            if not content:
                continue
        passages.extend((heading, passage) for passage in _sentence_passages(content))

    seen: set[str] = set()
    unique: list[tuple[str, str]] = []
    for passage_heading, passage_text in passages:
        key = f"{passage_heading}\n{passage_text}".casefold()
        if key in seen:
            continue
        seen.add(key)
        unique.append((passage_heading, passage_text))
    return tuple(unique)


def _sentence_passages(content: str) -> tuple[str, ...]:
    passages: list[str] = []
    for raw_line in content.splitlines():
        line = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", raw_line).strip()
        if not line:
            continue
        pending = ""
        sentences = re.findall(r"[^.!?]+[.!?]+|[^.!?]+$", line) or [line]
        for sentence in sentences:
            value = sentence.strip()
            if not value:
                continue
            pending = f"{pending} {value}".strip()
            if len(pending) >= MIN_PASSAGE_CHARACTERS:
                passages.append(pending[:MAX_PASSAGE_CHARACTERS])
                pending = ""
        if pending and passages:
            combined = f"{passages[-1]} {pending}"
            if len(combined) <= MAX_PASSAGE_CHARACTERS:
                passages[-1] = combined
    return tuple(passages)


def _evaluation_keywords(passage: str) -> tuple[str, ...]:
    words = re.findall(r"[a-z][a-z-]{3,}", passage.casefold())
    return tuple(
        dict.fromkeys(word for word in words if word not in _EXCLUDED_KEYWORDS)
    )[:5]


def _evenly_select(
    items: Sequence[EvaluationSuggestion],
    limit: int,
) -> Sequence[EvaluationSuggestion]:
    if len(items) <= limit:
        return items
    return tuple(items[index * len(items) // limit] for index in range(limit))


def _round_robin(
    suggestions: Sequence[EvaluationSuggestion],
    limit: int,
) -> Sequence[EvaluationSuggestion]:
    by_document: dict[str, list[EvaluationSuggestion]] = {}
    for suggestion in suggestions:
        by_document.setdefault(suggestion.document_id, []).append(suggestion)
    selected: list[EvaluationSuggestion] = []
    offset = 0
    while len(selected) < limit:
        added = False
        for document_suggestions in by_document.values():
            if len(selected) >= limit:
                break
            if offset < len(document_suggestions):
                selected.append(document_suggestions[offset])
                added = True
        if not added:
            break
        offset += 1
    return tuple(selected)
