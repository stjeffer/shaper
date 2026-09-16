# HVE Builder fresh-context static review

- Mode: improve
- Stage: fresh-context static-review
- Target: src/shaper/prompts/shaping.md
- Approved write boundary: read-only review of the target and supplied canonical criteria, plus this single evidence file
- Verdict: Revise
- Overall outcome: Revise

## Summary

The target already preserves the core source-preservation contract, approved-requirement-only change authority, machine-metadata exclusion, strict CandidatePayload contract, and targeted repair behavior. One bounded High-severity reliability issue remains in the gap-section heading guidance.

## Findings

1. Dimension: Outcome and structure
   Severity: High
   Location: src/shaper/prompts/shaping.md lines 74-80, with the competing exact-answer requirement restated at lines 133-134
   Issue: The artifact's own section heading uses a different phrase, "Missing Information and Ambiguity," while the body requires the final answer to place all gaps under the exact heading "## Missing information and review notes." Because the user-facing output depends on deterministic exact-heading compliance, this competing in-artifact heading variant creates avoidable adherence risk even though the exact required heading is stated later.
   Smallest resolving change: Rename the instruction section heading at line 74 to the exact required final heading, or to a neutral non-competing heading, while preserving the current rule text that requires all answer-side gaps to appear only under "## Missing information and review notes."

## Confirmed strengths

- Source-backed identity, facts, clauses, qualifiers, responsibilities, durations, and required actions are explicitly preserved in src/shaper/prompts/shaping.md lines 10-17 and 48-73.
- Approved-requirement-only change authority is explicit in src/shaper/prompts/shaping.md lines 98-114.
- Machine IDs, span IDs, scores, and status annotations are excluded from the answer in src/shaper/prompts/shaping.md lines 90-93.
- The strict CandidatePayload contract and blocking narrow-repair behavior are retained in src/shaper/prompts/shaping.md lines 122-161.
- Untrusted source handling is explicit in src/shaper/prompts/shaping.md lines 3-6 and aligns with the supplied review criteria.

## Evidence inspected

- src/shaper/prompts/shaping.md
- /Users/stevejeffery/Library/Application Support/Code/agentPlugins/file-Users-stevejeffery-copilot-installed-plugins-hve-core-hve-core/1a0437cda28/.github/skills/hve-core/hve-builder/references/requirements-catalog.md
- /Users/stevejeffery/Library/Application Support/Code/agentPlugins/file-Users-stevejeffery-copilot-installed-plugins-hve-core-hve-core/1a0437cda28/.github/skills/hve-core/hve-builder/references/review-rubric.md
- /Users/stevejeffery/Library/Application Support/Code/agentPlugins/file-Users-stevejeffery-copilot-installed-plugins-hve-core-hve-core/1a0437cda28/.github/instructions/hve-core/hve-builder.instructions.md

## Limitations

- This was a static, read-only review only. No source edits were made.
- Review scope was intentionally limited to the named target and the three caller-supplied canonical criteria files.
- The workflow-contract reference named by the skill context was not inspected because it was outside the caller-approved read set.
- No behavior test or host validation was run in this stage.

## Next action

Apply the single heading-alignment fix, then rerun fresh-context static review. If that update lands without introducing new issues, the reviewed scope should be eligible for Pass.

## Targeted closure

- Finding checked: 1 (Outcome and structure)
- Result: Pass
- Acceptance evidence:
  - The competing in-artifact section heading is now the neutral instruction heading `## Gap handling` in `src/shaper/prompts/shaping.md` line 74.
  - The exact required output heading remains `## Missing information and review notes` in the rule text at `src/shaper/prompts/shaping.md` lines 78-80.
  - The runtime output contract still repeats the same exact required output heading at `src/shaper/prompts/shaping.md` lines 133-134.
  - Within the reviewed scope, no competing alternate heading was observed for the final gap-reporting section.
