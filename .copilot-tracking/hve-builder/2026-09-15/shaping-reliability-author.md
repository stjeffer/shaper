# shaping reliability author log

- Date: 2026-09-15
- Mode: improve
- Approved write boundary:
  - `src/shaper/prompts/shaping.md`
  - `.copilot-tracking/hve-builder/2026-09-15/shaping-reliability-author.md`
- Target architecture preserved: single runtime Markdown prompt resource

## Baseline

The prior prompt optimized for decisive end-user answer shaping. It forced direct verdicts,
anti-mirroring, and concise user-facing outputs while already preserving the runtime schema,
untrusted-content boundary, tool rules, validation-feedback repair loop, approved-requirements
boundary, and exact span-citation requirement.

## Changes applied

1. Reframed the outcome so success is a complete source-preserving, agent-ready Markdown document.
2. Added explicit success criteria requiring retention of substantive rules, restrictions,
   exceptions, qualifiers, numeric facts, durations, responsibilities, and required actions.
3. Reworked the workflow to:
   - treat supplied content strictly as evidence,
   - identify complete source-backed content,
   - allow clearer headings, grounded Q&A, and explicit procedures only when supported,
   - repair rejected candidates narrowly from structured validation findings.
4. Replaced forced direct-verdict and anti-mirroring guidance with preservation-first rules that
   forbid yes/no compression, forced brevity, or structure changes when those would hide supported
   detail.
5. Added a dedicated missing-information and ambiguity section that:
   - separates source-backed content from gaps,
   - forbids inventing missing definitions, owners, dates, criteria, referenced content,
     conflict resolutions, or policy,
   - requires explicit flagging of omissions, unresolved ambiguity, and conflicts,
   - requires abstention when no faithful output is possible.
6. Preserved and tightened the runtime output contract for `candidate`, `abstain`, `tool`,
   `allowed_tools`, `validation_feedback`, `canonical_questions`, exact span citations, and the
   approved transformation requirements boundary.

## Static review

Pass. The revised prompt is outcome-first, keeps the strict runtime schema contract, preserves the
untrusted-content boundary, keeps tool use read-only and declared, and adds the requested narrow
repair behavior without widening scope.

## Validation

- `git diff --check -- src/shaper/prompts/shaping.md` — Passed
- Direct prompt text assertions against `src/shaper/prompts/shaping.md` — Passed
- `python3 -m pytest tests/test_prompts.py ...` — Not run successfully; host `pytest` module is
  unavailable
- Import-based prompt loading check through `shaper.prompts` — Not run successfully; host
  dependency `pydantic` is unavailable

## Notes

- Existing user-staged files were left untouched.
- Only the approved prompt file and this author log were written.
