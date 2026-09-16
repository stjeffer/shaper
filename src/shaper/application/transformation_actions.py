"""Deterministic transformation actions and source-exclusion authority."""

from __future__ import annotations

from collections.abc import Sequence

from shaper.domain import DocumentReadinessReport

TRANSFORMATION_ACTIONS = {
    "poor_metadata": "Preserve existing metadata and flag missing metadata for human completion",
    "structure_gap": "Reformat source-supported content with meaningful heading structure",
    "stale": "Flag statements that require freshness confirmation",
    "long_paragraph": "Split source-supported long paragraphs into focused knowledge sections",
    "cross_policy_reference": (
        "Preserve cross-policy references and label missing context without inventing it"
    ),
    "faq_gap": "Reformat source-supported content into grounded question and answer pairs",
    "procedure_gap": (
        "Reformat source-supported actions into procedural steps without inferring "
        "order, owners, or criteria"
    ),
    "external_dependency": "Label required external context as unresolved without inventing it",
    "circular_reference": "Preserve and flag circular references for human review",
    "missing_referenced_content": (
        "Label unresolved referenced material without adding unsupported content"
    ),
    "version_ambiguity": "Preserve and flag ambiguous versions without choosing precedence",
    "orphaned_amendment": (
        "Preserve amendment text and flag its unresolved relationship to the source"
    ),
    "vague_quantifier": "Preserve and flag vague quantities without inventing thresholds",
    "discretion_clause": "Preserve discretionary language and flag missing decision criteria",
    "undefined_term": "Flag undefined terms without inventing definitions",
    "unclear_responsibility": (
        "Flag unclear responsibility without inventing an owner or decision criteria"
    ),
    "conflicting_numeric_value": (
        "Preserve and flag conflicting values without selecting an approved rule"
    ),
    "conflicting_authority": (
        "Preserve and flag conflicting authorities without inventing precedence"
    ),
    "terminology_drift": (
        "Preserve terminology variations and flag possible equivalence without normalizing terms"
    ),
    "missing_definitions": "Flag missing definitions without creating them",
    "missing_enumeration": "Flag incomplete enumerations without adding unsupported items",
    "dangling_program": "Flag missing program status or end dates without inventing them",
    "unclear_source_of_truth": "Flag the unclear source of truth without selecting one",
    "undocumented_verbal_policy": (
        "Flag undocumented verbal guidance without incorporating unsupported policy"
    ),
    "restricted_companion": (
        "Preserve and flag inaccessible companion dependencies without replacing them"
    ),
    "inconsistent_heading_hierarchy": "Normalize heading levels for reliable chunking",
    "inaccessible_embedded_content": (
        "Preserve references to embedded content and flag unavailable embedded content"
    ),
    "repeated_variation": (
        "Preserve repeated variations and flag their differences without consolidating them"
    ),
    "noncanonical_duplicate": (
        "Flag noncanonical duplicate content without selecting a source of truth"
    ),
    "source_authored_ai_directive": (
        "Exclude the exact source-authored AI assistant or summarizer directive and add a "
        "review note"
    ),
    "unsupported_comparative_claim": (
        "Exclude the exact unsupported comparative, benchmarking, or research claim and add "
        "a review note"
    ),
}

EXCLUSION_CAPABLE_ACTIONS = {
    code: TRANSFORMATION_ACTIONS[code]
    for code in ("source_authored_ai_directive", "unsupported_comparative_claim")
}


def recommend_transformation_actions(report: DocumentReadinessReport) -> tuple[str, ...]:
    """Map discovery codes to stable, reviewable transformation actions."""
    proposed = tuple(
        dict.fromkeys(
            TRANSFORMATION_ACTIONS[code]
            for code in report.finding_codes
            if code in TRANSFORMATION_ACTIONS
        )
    )
    return proposed or (
        "Reformat source-supported content as a canonical agent-ready HTML knowledge asset",
    )


def derive_approved_source_exclusions(
    report: DocumentReadinessReport,
    *,
    source_version: str,
    source_text: str,
    approved_actions: Sequence[str],
) -> tuple[str, ...]:
    """Return exact source quotes that a matching approved proposal may exclude."""
    if report.source_version != source_version:
        return ()
    approved = set(approved_actions)
    exclusions: list[str] = []
    for finding in report.findings:
        action = EXCLUSION_CAPABLE_ACTIONS.get(finding.code)
        if finding.code not in report.finding_codes or action is None or action not in approved:
            continue
        for evidence in finding.evidence:
            if source_text.count(evidence.quote) == 1:
                exclusions.append(evidence.quote)
    return tuple(dict.fromkeys(exclusions))
