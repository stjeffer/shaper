<!-- markdownlint-disable-file -->

# Behavior Evidence Review: validation calibration

* Target prompt version: 2.2
* Target SHA-256: `84b72380ac4e0a35d81056bf3b48f14801429aa6a738f129301d3f5669409798`
* Profile: Medium, GPT-5.6 Terra
* Fidelity: simulation
* Verdict: Pass
* Scenario results: 10 Pass, 0 Revise, 0 Blocked

The independent grader confirmed that S01-S10 satisfy the complete mapped behavior
requirements. The prior hash blocker was caused by wrong-worktree resolution and was
cleared using the authoritative absolute target provenance.

## Action Categories

| Category | Count |
|----------|------:|
| Must fix | 0 |
| Should fix | 0 |
| Consider | 0 |

## Limitations

Evidence is contained simulation rather than native Azure OpenAI execution. Tool
acquisition, cross-document conflict handling, multiple-policy splitting, provider
reliability, and runtime budgets were not tested.
