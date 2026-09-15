# HVE Builder Static Review Log

- Mode: `review` (static review only)
- Scope: reviewed `src/shaper/prompts/shaping.md` only
- Canonical criteria: `requirements-catalog.md`, `review-rubric.md`
- Source edits: none
- Exploration, diffs, and author reasoning: not used

## Artifact under review

`src/shaper/prompts/shaping.md`

Purpose assessed: generate a complete, source-preserving, agent-ready Markdown document; retain supported policy substance; prohibit invention; separate source-backed content from missing information; enforce schema/tool/citation/untrusted-content boundaries; and perform one narrow repair when `rejected_candidate`, `validation_feedback`, and `validation_findings` are supplied.

## Dimensions assessed

- Architecture fit — Pass
- Outcome and structure — Pass
- Emphasis calibration — Pass
- Tool and output schemas — Revise
- Evaluation hooks — Pass
- Safety and enforcement — Pass
- Portability and maintenance — Pass
- Stale-pattern absence — Pass
- Other rubric dimensions — Not applicable to this single prompt artifact or not evidenced within the approved read set

## Findings

### F1 — High — Tool and output schemas
- Location: `src/shaper/prompts/shaping.md:25-27`, `src/shaper/prompts/shaping.md:100-104`
- What is wrong: the workflow says to "use a declared read-only tool to fetch" missing evidence, while the runtime contract says to return only schema-conforming outputs and to return a `tool` status when missing evidence is obtainable through `allowed_tools`. That splits the missing-evidence path between direct tool use and schema-only signaling, weakening the strict schema/tool boundary this artifact is supposed to preserve.
- Why it matters: callers that expect schema-only responses can receive behavior that steps outside the declared output contract, reducing reliability at exactly the point where the prompt handles incomplete evidence.
- Smallest concrete change: rewrite step 1 so it aligns with the runtime contract: when missing evidence is obtainable through declared read-only tools, return the `tool` response only; otherwise return `abstain`.
- Criteria: review-rubric `Tool and output schemas`; requirements-catalog §6 `Strict schema conformance`, `Handle refusals and out-of-schema input`.

## Verdict

**Revise**

The artifact is otherwise well-aligned to its source-preservation, anti-invention, citation, ambiguity, and narrow-repair goals, but F1 is a high-severity protocol inconsistency in a core boundary condition.

## Targeted closure check

- Original finding checked: `F1 — High — Tool and output schemas`
- Scope: closure only for `src/shaper/prompts/shaping.md:25-27` and `src/shaper/prompts/shaping.md:100-104` from the original review
- Source edits in this run: none

### Closure result

**Pass**

- `src/shaper/prompts/shaping.md:25-27` now routes missing evidence through a schema-conforming `tool` return with a request for a declared read-only tool, and otherwise requires `abstain`; it no longer claims direct tool execution.
- `src/shaper/prompts/shaping.md:101-104` keeps the runtime boundary explicit: return `tool` only for declared read-only tools in `allowed_tools`, never request undeclared or write actions, and resolve follow-up with `candidate` or `abstain`.
- Abstention behavior is retained at `src/shaper/prompts/shaping.md:79-81`, `99-100`, and `109-111`.
