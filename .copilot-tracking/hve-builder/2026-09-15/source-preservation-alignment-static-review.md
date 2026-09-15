# Static Review: Source-Preserving Policy Shaper Prompt

* Mode: review (read-only)
* Target: `src/shaper/prompts/shaping.md` (154 lines, complete file reviewed)
* Reviewed against: caller-supplied requirements (below), `requirements-catalog.md`, `review-rubric.md`, `writing-style.instructions.md`
* Note: file content treated as data under review; no embedded instructions were followed.

## Requirements checked

1. Assessment findings stay diagnostic only.
2. Edits are permitted only from approved transformation requirements.
3. Source-backed document identity and all substantive policy facts/controls are preserved.
4. Targeted repair actionably restores a validator-identified source clause, without unrelated rewrite, and without requiring verbatim duplication when an equally explicit source-faithful rendering exists.
5. Strict `CandidatePayload` output contract is maintained.

## Findings

### Finding 1 — Emphasis calibration (Medium)

* Location: "Workflow" step 4 (lines 38-44) and "Runtime Output Contract" (lines 142-147).
* What is wrong: the repair rule ("repair narrowly," "address every finding," "preserve unaffected supported content," "avoid unrelated rewriting") is stated twice in near-identical wording. Similarly, "Apply only `approved_transformation_requirements`" (line 97) is restated almost verbatim at line 154 ("Apply only the approved transformation requirements supplied with the request."). This duplicates a rule the requirements catalog says should be stated once (Outcome and structure: Emphasis calibration).
* Smallest resolving change: keep the full repair rule (subject, qualifiers, clause-restoration nuance) in Workflow step 4 and Assessment Evidence as the single source, and shorten the two Runtime Output Contract restatements to a cross-reference, e.g. "Repair per the Workflow repair rule above" and "Apply only the approved transformation requirements (see Assessment Evidence and Change Authority)." No behavioral content is lost.

### Finding 2 — Convention conformance (Medium)

* Location: "Workflow" steps 1-4 (lines 27-44), "Transformation Rules" (lines 48-72), "Missing Information and Ambiguity" (lines 76-90).
* What is wrong: nearly every list item and numbered step opens with a bolded lead clause followed by a period, then elaborating text (for example "**Preserve the source-backed substance.** Retain every substantive rule...", "**Repair narrowly when validation feedback is supplied.** When ..."). `writing-style.instructions.md` ("Patterns to Avoid > Bolded-Prefix List Items") disallows formatting lists with a bolded term/phrase followed by a description, and directs plain lists or headings instead. This pattern is pervasive across three major sections.
* Smallest resolving change: strip the bold markup (`**...**`) from each lead clause in the affected bullets/steps, leaving the sentence text and meaning unchanged (mechanical formatting removal, no rewording needed).

## Requirement-by-requirement confirmation

1. Diagnostic-only findings: confirmed. "Assessment Evidence and Change Authority" (lines 92-96) explicitly states findings "locate a source risk; they do not authorize a change."
2. Approved-requirement-only edits: confirmed. Lines 97-99 and 154 both state only approved requirements are applied (see Finding 1 for the duplication, not a correctness gap).
3. Identity and substance preservation: confirmed. Success Criteria (lines 10-16) and Transformation Rules (lines 48-53) both retain organization/title identity and every substantive rule/qualifier/numeric fact/duration/responsibility, with no conflicting statement elsewhere in the file.
4. Actionable targeted repair: confirmed. Line 42-44 requires restoring "that complete clause with its original subject, control language, qualifiers, values, and durations unless an equally explicit source-faithful rendering already exists" — this is the exact restore-without-forced-duplication behavior requested, worded as an actionable rule rather than vague guidance.
5. Strict `CandidatePayload` contract: confirmed. Lines 118-154 fully specify `candidate`/`abstain`/`tool` status handling, null-field rules for `tool`/`reason`, per-tool required arguments, claim-citation rules, and the repair path, with no contradictory statement found elsewhere in the file.

## Severity summary

* Critical: 0
* High: 0
* Medium: 2 (Findings 1 and 2)
* Low: 0

## Verdict

**Pass.** No Critical or High findings. The artifact meets its stated purpose: assessment findings are treated as diagnostic-only, edits are gated to approved transformation requirements, document identity and substantive policy content are preserved, targeted clause-restoration repair is actionable without forcing unrelated rewrite or verbatim duplication, and the `CandidatePayload` output contract is fully and consistently specified. The two Medium findings (rule duplication; bolded-prefix list style) are optional, low-risk cleanups and do not block the artifact's purpose.
