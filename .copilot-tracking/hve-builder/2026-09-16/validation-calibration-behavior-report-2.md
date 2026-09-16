<!-- markdownlint-disable-file -->

# HVE Artifact Test Report: validation calibration

* Tested profile: Medium, GPT-5.6 Terra
* Run type: full
* Behavior gate: Executed
* Fidelity: simulation
* Execution status: Complete
* Verdict: Pass
* Target: src/shaper/prompts/shaping.md
* Prompt version: 2.2
* Prompt SHA-256: `84b72380ac4e0a35d81056bf3b48f14801429aa6a738f129301d3f5669409798`
* Sandbox: cleaned up

## Summary

Prompt 2.2 passed ten fresh black-box scenarios. The evidence covers source-faithful
initial shaping, narrow approved exclusions, adjacent-policy preservation, malformed
exclusion abstention, true semantic repair, blocking-only repair feedback, review-note
discipline, genuine policy qualifiers, non-invention, grounding, and strict response
schema invariants.

## Findings

| # | Action | Scenario | Severity | Evidence | Resolution |
|---|--------|----------|----------|----------|------------|
| None | None | S01-S10 | None | Ten scenarios passed independent grading | None |

## Coverage

| Scenario | Behavior | Verdict |
|----------|----------|---------|
| S01 | Preserve 6%, monthly scope, and written manager approval | Pass |
| S02 | Exclude and audit exact unsupported promotion | Pass |
| S03 | Exclude AI directive while preserving adjacent employee policy | Pass |
| S04 | Abstain generically on malformed exclusion authority | Pass |
| S05 | Replace invented 45% with source-backed 50% | Pass |
| S06 | Restore omitted manager-approval duty without advisory repair | Pass |
| S07 | Keep review notes absent or final and non-policy | Pass |
| S08 | Preserve `only after` access qualification | Pass |
| S09 | Avoid invented deadlines, values, and outcomes | Pass |
| S10 | Satisfy CandidatePayload status and schema invariants | Pass |

## Fidelity and Limitations

The run used contained literal simulation with GPT-5.6 Terra. It supports prompt
conformance claims, not native Azure OpenAI structured-output reliability. Read-only
tool acquisition, cross-document conflicts, multiple-policy splitting, and provider
retry budgets were not exercised because those surfaces did not change.

The first executor return was discarded before grading because the harness omitted the
runtime CandidatePayload schema. The complete suite was rerun with that schema. S05 and
S06 were then rerun with exact source span IDs after the compact design omitted those
fixture details. Only the fully specified returns were graded.

One grader initially resolved `shaping.md` from another worktree and blocked on an
incorrect hash. A correction grader used the authoritative absolute release path and
confirmed the final hash before independently passing S01-S10.

## Containment

Simulation workers were read-only. They did not invoke tools, access the network,
publish, deploy, or edit source files. The temporary sandbox was removed after the
durable report was written.

## Human Review

* [ ] Reviewed and validated by a qualified human reviewer
