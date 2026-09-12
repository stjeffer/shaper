"""Evidence-grounded deterministic checks for document suitability."""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from difflib import SequenceMatcher
from itertools import pairwise

from shaper.domain import (
    AuthorityStatus,
    DocumentFinding,
    DocumentFindingEvidence,
    KnowledgeDocumentProfile,
)

DOCUMENT_CHECK_CODES = (
    "external_dependency",
    "circular_reference",
    "missing_referenced_content",
    "version_ambiguity",
    "orphaned_amendment",
    "vague_quantifier",
    "discretion_clause",
    "undefined_term",
    "unclear_responsibility",
    "conflicting_numeric_value",
    "conflicting_authority",
    "terminology_drift",
    "missing_definitions",
    "missing_enumeration",
    "dangling_program",
    "unclear_source_of_truth",
    "undocumented_verbal_policy",
    "restricted_companion",
    "inconsistent_heading_hierarchy",
    "inaccessible_embedded_content",
    "repeated_variation",
    "noncanonical_duplicate",
)

BASELINE_CHECK_CODES = (
    "poor_metadata",
    "structure_gap",
    "stale",
    "long_paragraph",
    "cross_policy_reference",
    "faq_gap",
    "procedure_gap",
)

_REFERENCE = re.compile(
    r"\b(?:see|refer to|in accordance with|pursuant to|per)\s+(?:the\s+)?"
    r"(?P<target>(?:appendix|section|table)\s+[A-Z0-9.-]+|"
    r"[A-Z][A-Za-z0-9 &'/-]{2,80}(?:Policy|Procedure|Standard|Guidelines?|"
    r"Handbook|Memo|Addendum))",
    re.IGNORECASE,
)
_VERSION_MARKER = re.compile(
    r"\b(?:as of|effective|revised|updated|version|v\d+(?:\.\d+)*)\b"
    r"|(?:19|20)\d{2}-\d{2}-\d{2}",
    re.IGNORECASE,
)
_AMENDMENT = re.compile(
    r"\b(?:per|under|as stated in)\s+(?:the\s+)?"
    r"(?:Q[1-4]\s+)?(?:memo|amendment|addendum|update|all-hands)\b",
    re.IGNORECASE,
)
_VAGUE = re.compile(
    r"\b(?:approximately|generally|typically|roughly|usually|normally|"
    r"from time to time|as appropriate)\b",
    re.IGNORECASE,
)
_DISCRETION = re.compile(
    r"\b(?:at (?:the )?[\w -]+'?s discretion|case[- ]by[- ]case basis|"
    r"as determined by|where deemed appropriate)\b",
    re.IGNORECASE,
)
_PASSIVE_RESPONSIBILITY = re.compile(
    r"\b(?:will|shall|must|should|may)\s+be\s+"
    r"(?:reviewed|approved|determined|assessed|decided|considered|handled|processed)\b",
    re.IGNORECASE,
)
_AUTHORITY = re.compile(
    r"[^.!?\n]*(?:controls|prevails|overrides|supersedes|takes precedence)[^.!?\n]*[.!?]?",
    re.IGNORECASE,
)
_MISSING_ENUMERATION = re.compile(
    r"\b(?:varies|differs|depends)\s+(?:by|on)\s+"
    r"(?:state|country|region|location|jurisdiction)\b",
    re.IGNORECASE,
)
_PROGRAM = re.compile(r"\b(?:pilot|trial|temporary program|program)\b", re.IGNORECASE)
_PROGRAM_STATUS = re.compile(
    r"\b(?:ends?|expires?|until|through|active|inactive|closed|permanent|"
    r"(?:19|20)\d{2})\b",
    re.IGNORECASE,
)
_SOURCE_OF_TRUTH = re.compile(
    r"\b(?:most recent|latest)\s+(?:communication|email|memo|guidance)\s+"
    r"(?:governs|controls|prevails|applies)\b",
    re.IGNORECASE,
)
_VERBAL = re.compile(
    r"\b(?:clarified|announced|confirmed|communicated)\s+"
    r"(?:verbally|orally|in (?:an|the) all-hands)\b",
    re.IGNORECASE,
)
_RESTRICTED = re.compile(
    r"[^.!?\n]*(?:confidential|restricted|limited[- ]access|need[- ]to[- ]know)"
    r"[^.!?\n]*(?:policy|procedure|standard|guidelines?|handbook|document)[^.!?\n]*[.!?]?",
    re.IGNORECASE,
)
_EMBEDDED = re.compile(
    r"!\[\s*\]\([^)]+\)|\b(?:see|shown in)\s+(?:the\s+)?"
    r"(?:image|diagram|chart|table)\s+(?:below|above)\b",
    re.IGNORECASE,
)
_DEFINED_TERM = re.compile(
    r'(?:"(?P<quoted>[^"]{2,80})"|(?P<title>[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,2}))'
    r"\s+(?:means|refers to|is defined as)\s+(?P<definition>[^.!?\n]{4,240})",
)
_QUOTED_TERM = re.compile(r'"([^"]{2,80})"')
_NUMBER = re.compile(
    r"(?:[$£€]\s?\d[\d,.]*|\b\d+(?:\.\d+)?\s*"
    r"(?:%|percent|days?|weeks?|months?|years?|hours?|dollars?|pounds?|euros?)\b)",
    re.IGNORECASE,
)
_WORD = re.compile(r"[a-zA-Z]{3,}")
_STOP_WORDS = frozenset(
    {
        "about",
        "after",
        "before",
        "days",
        "from",
        "have",
        "must",
        "shall",
        "should",
        "that",
        "their",
        "this",
        "within",
        "with",
    }
)


@dataclass(frozen=True)
class _TextBlock:
    text: str
    line: int
    heading: str | None


def assess_document_findings(
    profile: KnowledgeDocumentProfile,
    peers: Sequence[KnowledgeDocumentProfile] = (),
) -> tuple[DocumentFinding, ...]:
    """Return bounded review candidates for one document and its estate peers."""
    text = profile.text
    blocks = _blocks(text)
    findings: list[DocumentFinding] = []

    references = list(_REFERENCE.finditer(text))
    if references:
        findings.append(
            _finding(
                "external_dependency",
                "External dependency",
                "The document points to material that may not be available with this source.",
                text,
                references,
            )
        )
    unresolved = [
        match for match in references if not _reference_resolves(match.group("target"), text, peers)
    ]
    if unresolved:
        findings.append(
            _finding(
                "missing_referenced_content",
                "Referenced content is missing",
                "The referenced appendix, table, section, or companion document was not found.",
                text,
                unresolved,
                severity="high",
            )
        )

    circular = _circular_reference_evidence(text)
    if circular:
        findings.append(
            _from_evidence(
                "circular_reference",
                "Circular cross-reference",
                "Two sections point to each other without defining the rule locally.",
                circular,
                severity="high",
            )
        )

    if not _VERSION_MARKER.search(text) or _mixed_versions(text):
        findings.append(
            _document_level_finding(
                "version_ambiguity",
                "Version is unclear",
                "No stable effective date was found, or multiple version markers "
                "need precedence review.",
                blocks,
            )
        )

    _append_matches(
        findings,
        text,
        "orphaned_amendment",
        "Unmerged amendment",
        "The source relies on a memo, amendment, or update that may not be merged here.",
        _AMENDMENT,
    )
    _append_matches(
        findings,
        text,
        "vague_quantifier",
        "Vague quantity",
        "The wording does not provide a concrete value an agent can apply.",
        _VAGUE,
    )
    _append_matches(
        findings,
        text,
        "discretion_clause",
        "Unrecorded discretion",
        "The rule depends on case-specific human judgment without decision criteria.",
        _DISCRETION,
    )

    undefined = _undefined_term_matches(text)
    if undefined:
        findings.append(
            _finding(
                "undefined_term",
                "Term may be undefined",
                "A policy-style term is used without a nearby explicit definition.",
                text,
                undefined,
            )
        )
    _append_matches(
        findings,
        text,
        "unclear_responsibility",
        "Responsibility is unclear",
        "A required action is written passively without naming the responsible role.",
        _PASSIVE_RESPONSIBILITY,
    )

    numeric = _numeric_conflict_evidence(profile, peers)
    if numeric:
        findings.append(
            _from_evidence(
                "conflicting_numeric_value",
                "Numeric values may conflict",
                "Similar rules contain different amounts, thresholds, or durations.",
                numeric,
                severity="high",
            )
        )

    authority = [_evidence(text, match) for match in _AUTHORITY.finditer(text)]
    if len(authority) > 1:
        findings.append(
            _from_evidence(
                "conflicting_authority",
                "Authority order may conflict",
                "Multiple precedence statements require a clear governing order.",
                authority,
                severity="high",
            )
        )

    terminology = _terminology_drift_evidence(text)
    if terminology:
        findings.append(
            _from_evidence(
                "terminology_drift",
                "Terminology may drift",
                "Different defined terms appear to describe substantially similar concepts.",
                terminology,
            )
        )

    if _missing_definitions(text):
        findings.append(
            _document_level_finding(
                "missing_definitions",
                "Definitions are missing",
                "The source refers to definitions but does not include a populated "
                "definitions section.",
                blocks,
                severity="high",
            )
        )
    _append_matches(
        findings,
        text,
        "missing_enumeration",
        "Required enumeration is missing",
        "The rule varies by jurisdiction but no explicit jurisdiction list or table is present.",
        _MISSING_ENUMERATION,
    )

    dangling = [
        match
        for match in _PROGRAM.finditer(text)
        if not _PROGRAM_STATUS.search(_containing_block(text, match.start()).text)
    ]
    if dangling:
        findings.append(
            _finding(
                "dangling_program",
                "Program status is unclear",
                "A pilot, trial, or program is mentioned without a clear end date "
                "or current status.",
                text,
                dangling,
            )
        )
    _append_matches(
        findings,
        text,
        "unclear_source_of_truth",
        "Source of truth is unclear",
        "The rule delegates authority to an unspecified latest communication.",
        _SOURCE_OF_TRUTH,
        severity="high",
    )
    _append_matches(
        findings,
        text,
        "undocumented_verbal_policy",
        "Verbal policy is not documented",
        "The source relies on a verbal clarification that is not captured as governed text.",
        _VERBAL,
        severity="high",
    )
    _append_matches(
        findings,
        text,
        "restricted_companion",
        "Companion content may be inaccessible",
        "A required companion document is described as confidential or restricted.",
        _RESTRICTED,
        severity="high",
    )

    headings = _heading_levels(text)
    if any(level > previous + 1 for previous, level in pairwise(headings)):
        findings.append(
            _document_level_finding(
                "inconsistent_heading_hierarchy",
                "Heading hierarchy is inconsistent",
                "A heading level skips its expected parent, which can impair section retrieval.",
                blocks,
            )
        )
    _append_matches(
        findings,
        text,
        "inaccessible_embedded_content",
        "Embedded content may be unreadable",
        "Meaning appears to depend on an image, diagram, chart, or unstructured table.",
        _EMBEDDED,
    )

    repeated = _repeated_variation_evidence(blocks)
    if repeated:
        findings.append(
            _from_evidence(
                "repeated_variation",
                "Repeated rules vary subtly",
                "Similar passages differ enough that retrieval may surface inconsistent wording.",
                repeated,
            )
        )

    duplicate = _peer_duplicate_evidence(profile, peers)
    if duplicate:
        findings.append(
            _from_evidence(
                "noncanonical_duplicate",
                "No canonical source is declared",
                "Substantially overlapping content exists in another source without "
                "declared authority.",
                duplicate,
                severity="high",
            )
        )
    return tuple(findings)


def baseline_document_findings(
    profile: KnowledgeDocumentProfile,
    codes: Sequence[str],
) -> tuple[DocumentFinding, ...]:
    """Attach source evidence to the established readiness findings."""
    blocks = _blocks(profile.text)
    opening = blocks[:1]
    definitions: dict[str, tuple[str, str, str, Sequence[_TextBlock]]] = {
        "poor_metadata": (
            "Limited metadata",
            "Core topic and content metadata is incomplete.",
            "info",
            opening,
        ),
        "structure_gap": (
            "Weak structure",
            "Headings or focused content sections are missing.",
            "info",
            opening,
        ),
        "stale": (
            "Freshness risk",
            "The source is beyond the three-year review threshold.",
            "warning",
            opening,
        ),
        "faq_gap": (
            "No question coverage",
            "No FAQ or question-shaped content was detected.",
            "info",
            opening,
        ),
        "procedure_gap": (
            "Implicit procedure",
            "Procedural language is not organized into explicit steps.",
            "warning",
            tuple(
                block
                for block in blocks
                if re.search(
                    r"\b(?:must|should|submit|complete|step|procedure)\b",
                    block.text,
                    re.IGNORECASE,
                )
            )[:1],
        ),
        "long_paragraph": (
            "Long paragraph",
            "A passage exceeds 150 words and may reduce retrieval precision.",
            "warning",
            tuple(block for block in blocks if len(block.text.split()) > 150)[:4],
        ),
        "cross_policy_reference": (
            "Document reference",
            "A reference to another governed source needs explicit context.",
            "warning",
            tuple(
                _containing_block(profile.text, match.start())
                for match in _REFERENCE.finditer(profile.text)
            )[:4],
        ),
    }
    findings = []
    for code in codes:
        definition = definitions.get(code)
        if definition is None:
            continue
        label, explanation, severity, evidence_blocks = definition
        findings.append(
            DocumentFinding(
                code=code,
                label=label,
                explanation=explanation,
                severity=severity,
                evidence=tuple(
                    DocumentFindingEvidence(
                        quote=_bounded_quote(block.text),
                        location=_location(block.line, block.heading),
                    )
                    for block in evidence_blocks
                ),
            )
        )
    return tuple(findings)


def _append_matches(
    findings: list[DocumentFinding],
    text: str,
    code: str,
    label: str,
    explanation: str,
    pattern: re.Pattern[str],
    *,
    severity: str = "warning",
) -> None:
    matches = list(pattern.finditer(text))
    if matches:
        findings.append(_finding(code, label, explanation, text, matches, severity=severity))


def _finding(
    code: str,
    label: str,
    explanation: str,
    text: str,
    matches: Sequence[re.Match[str]],
    *,
    severity: str = "warning",
) -> DocumentFinding:
    return _from_evidence(
        code,
        label,
        explanation,
        [_evidence(text, match) for match in matches[:4]],
        severity=severity,
    )


def _from_evidence(
    code: str,
    label: str,
    explanation: str,
    evidence: Sequence[DocumentFindingEvidence],
    *,
    severity: str = "warning",
) -> DocumentFinding:
    return DocumentFinding(
        code=code,
        label=label,
        explanation=explanation,
        severity=severity,
        evidence=tuple(evidence[:4]),
    )


def _document_level_finding(
    code: str,
    label: str,
    explanation: str,
    blocks: Sequence[_TextBlock],
    *,
    severity: str = "warning",
) -> DocumentFinding:
    evidence: tuple[DocumentFindingEvidence, ...] = ()
    if blocks:
        first = blocks[0]
        evidence = (
            DocumentFindingEvidence(
                quote=_bounded_quote(first.text),
                location=_location(first.line, first.heading, prefix="Document-level check"),
            ),
        )
    return DocumentFinding(
        code=code,
        label=label,
        explanation=explanation,
        severity=severity,
        evidence=evidence,
    )


def _evidence(text: str, match: re.Match[str]) -> DocumentFindingEvidence:
    block = _containing_block(text, match.start())
    return DocumentFindingEvidence(
        quote=_bounded_quote(block.text),
        location=_location(block.line, block.heading),
    )


def _blocks(text: str) -> tuple[_TextBlock, ...]:
    blocks: list[_TextBlock] = []
    heading: str | None = None
    lines = text.splitlines()
    paragraph: list[str] = []
    start_line = 1
    for line_number, line in enumerate([*lines, ""], start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            if paragraph:
                blocks.append(_TextBlock(" ".join(paragraph), start_line, heading))
                paragraph.clear()
            heading = stripped.lstrip("#").strip() or heading
            continue
        if stripped:
            if not paragraph:
                start_line = line_number
            paragraph.append(stripped)
        elif paragraph:
            blocks.append(_TextBlock(" ".join(paragraph), start_line, heading))
            paragraph.clear()
    return tuple(blocks)


def _containing_block(text: str, offset: int) -> _TextBlock:
    consumed = 0
    for block in _blocks(text):
        index = text.find(block.text, consumed)
        if index < 0:
            continue
        consumed = index + len(block.text)
        if index <= offset <= consumed:
            return block
    line = text.count("\n", 0, offset) + 1
    return _TextBlock(text[max(0, offset - 120) : offset + 240], line, None)


def _location(line: int, heading: str | None, *, prefix: str | None = None) -> str:
    parts = [part for part in (prefix, heading, f"line {line}") if part]
    return " · ".join(parts)


def _bounded_quote(text: str) -> str:
    normalized = " ".join(text.split())
    return normalized if len(normalized) <= 500 else normalized[:497].rstrip() + "..."


def _reference_resolves(
    target: str,
    text: str,
    peers: Sequence[KnowledgeDocumentProfile],
) -> bool:
    normalized = target.casefold()
    if normalized.startswith(("appendix ", "section ", "table ")):
        occurrences = [
            match.start() for match in re.finditer(re.escape(target), text, re.IGNORECASE)
        ]
        return len(occurrences) > 1 or bool(re.search(rf"(?im)^#+\s*{re.escape(target)}\s*$", text))
    target_words = {word.casefold() for word in _WORD.findall(target)}
    return any(
        len(target_words & {word.casefold() for word in _WORD.findall(peer.title)})
        >= max(1, len(target_words) - 1)
        for peer in peers
    )


def _circular_reference_evidence(text: str) -> tuple[DocumentFindingEvidence, ...]:
    sections: dict[str, tuple[str, int]] = {}
    current: str | None = None
    content: list[str] = []
    start = 1
    for line_number, line in enumerate([*text.splitlines(), "# END"], start=1):
        if line.lstrip().startswith("#"):
            if current is not None:
                sections[current] = (" ".join(content), start)
            current = line.lstrip("#").strip().casefold()
            content = []
            start = line_number
        elif current is not None:
            content.append(line)
    for left, (left_text, left_line) in sections.items():
        for right, (right_text, right_line) in sections.items():
            if left >= right:
                continue
            if re.search(rf"\b{re.escape(right)}\b", left_text, re.IGNORECASE) and re.search(
                rf"\b{re.escape(left)}\b", right_text, re.IGNORECASE
            ):
                return (
                    DocumentFindingEvidence(
                        quote=_bounded_quote(left_text),
                        location=_location(left_line, left),
                    ),
                    DocumentFindingEvidence(
                        quote=_bounded_quote(right_text),
                        location=_location(right_line, right),
                    ),
                )
    return ()


def _mixed_versions(text: str) -> bool:
    versions = set(
        match.casefold()
        for match in re.findall(
            r"\b(?:version|v)\s*\d+(?:\.\d+)*\b|\b(?:19|20)\d{2}-\d{2}-\d{2}\b",
            text,
            re.IGNORECASE,
        )
    )
    return len(versions) > 1 and not re.search(
        r"\b(?:supersedes|replaces|current version)\b", text, re.IGNORECASE
    )


def _undefined_term_matches(text: str) -> list[re.Match[str]]:
    defined = {
        (match.group("quoted") or match.group("title")).casefold()
        for match in _DEFINED_TERM.finditer(text)
    }
    return [
        match
        for match in _QUOTED_TERM.finditer(text)
        if match.group(1).casefold() not in defined
        and len(re.findall(re.escape(match.group(0)), text, re.IGNORECASE)) > 1
    ]


def _missing_definitions(text: str) -> bool:
    references_definitions = bool(
        re.search(r"\b(?:defined in|see|refer to)\s+(?:the\s+)?definitions?\b", text, re.IGNORECASE)
    )
    has_section = bool(re.search(r"(?im)^#{1,6}\s+definitions?\s*$", text))
    return references_definitions and not has_section


def _heading_levels(text: str) -> tuple[int, ...]:
    return tuple(
        len(match.group("marks")) for match in re.finditer(r"(?m)^(?P<marks>#{1,6})\s+\S", text)
    )


def _sentence_matches(text: str) -> tuple[tuple[str, int], ...]:
    return tuple(
        (match.group(0).strip(), match.start())
        for match in re.finditer(r"[^.!?\n]+[.!?]?", text)
        if match.group(0).strip()
    )


def _comparison_key(sentence: str) -> set[str]:
    without_numbers = _NUMBER.sub("", sentence)
    return {
        word.casefold()
        for word in _WORD.findall(without_numbers)
        if word.casefold() not in _STOP_WORDS
    }


def _numeric_conflict_evidence(
    profile: KnowledgeDocumentProfile,
    peers: Sequence[KnowledgeDocumentProfile],
) -> tuple[DocumentFindingEvidence, ...]:
    candidates: list[tuple[str, KnowledgeDocumentProfile, int]] = []
    for current in (profile, *peers):
        for sentence, offset in _sentence_matches(current.text):
            numbers = "|".join(match.group(0).casefold() for match in _NUMBER.finditer(sentence))
            if numbers:
                candidates.append((sentence, current, offset))
    for index, (left, left_profile, left_offset) in enumerate(candidates):
        left_key = _comparison_key(left)
        for right, right_profile, right_offset in candidates[index + 1 :]:
            if left_profile.document_id == right_profile.document_id and left == right:
                continue
            right_key = _comparison_key(right)
            union = left_key | right_key
            similarity = len(left_key & right_key) / len(union) if union else 0
            if similarity < 0.55 or set(_NUMBER.findall(left)) == set(_NUMBER.findall(right)):
                continue
            return (
                DocumentFindingEvidence(
                    quote=_bounded_quote(left),
                    location=f"{left_profile.title} · "
                    f"line {left_profile.text.count(chr(10), 0, left_offset) + 1}",
                ),
                DocumentFindingEvidence(
                    quote=_bounded_quote(right),
                    location=f"{right_profile.title} · "
                    f"line {right_profile.text.count(chr(10), 0, right_offset) + 1}",
                ),
            )
    return ()


def _terminology_drift_evidence(text: str) -> tuple[DocumentFindingEvidence, ...]:
    definitions = list(_DEFINED_TERM.finditer(text))
    for index, left in enumerate(definitions):
        left_term = (left.group("quoted") or left.group("title")).casefold()
        left_definition = left.group("definition")
        for right in definitions[index + 1 :]:
            right_term = (right.group("quoted") or right.group("title")).casefold()
            if left_term == right_term:
                continue
            ratio = SequenceMatcher(
                None, left_definition.casefold(), right.group("definition").casefold()
            ).ratio()
            if ratio >= 0.65:
                return (_evidence(text, left), _evidence(text, right))
    return ()


def _repeated_variation_evidence(
    blocks: Sequence[_TextBlock],
) -> tuple[DocumentFindingEvidence, ...]:
    for index, left in enumerate(blocks):
        if len(left.text.split()) < 8:
            continue
        for right in blocks[index + 1 :]:
            ratio = SequenceMatcher(None, left.text.casefold(), right.text.casefold()).ratio()
            if 0.72 <= ratio < 0.98:
                return (
                    DocumentFindingEvidence(
                        quote=_bounded_quote(left.text),
                        location=_location(left.line, left.heading),
                    ),
                    DocumentFindingEvidence(
                        quote=_bounded_quote(right.text),
                        location=_location(right.line, right.heading),
                    ),
                )
    return ()


def _peer_duplicate_evidence(
    profile: KnowledgeDocumentProfile,
    peers: Sequence[KnowledgeDocumentProfile],
) -> tuple[DocumentFindingEvidence, ...]:
    profile_words = set(word.casefold() for word in _WORD.findall(profile.text))
    for peer in peers:
        if peer.document_id == profile.document_id:
            continue
        peer_words = set(word.casefold() for word in _WORD.findall(peer.text))
        union = profile_words | peer_words
        overlap = len(profile_words & peer_words) / len(union) if union else 0
        if (
            overlap >= 0.65
            and profile.authority is not AuthorityStatus.AUTHORITATIVE
            and peer.authority is not AuthorityStatus.AUTHORITATIVE
        ):
            return (
                DocumentFindingEvidence(
                    quote=_bounded_quote(profile.text),
                    location=f"{profile.title} · document opening",
                ),
                DocumentFindingEvidence(
                    quote=_bounded_quote(peer.text),
                    location=f"{peer.title} · document opening",
                ),
            )
    return ()
