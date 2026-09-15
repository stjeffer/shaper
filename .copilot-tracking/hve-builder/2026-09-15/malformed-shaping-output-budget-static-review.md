# Static Review: Shaping Prompt 1.6

- Mode: improve
- Profile/model: Medium / GPT-5.6 Terra
- Target: `src/shaper/prompts/shaping.md`
- Related contracts: `CandidatePayload` and `ToolRequest`
- Verdict: Pass

## Scope

The review covered diagnostic versus approved authority, preservation and repair
instructions, concise source-block provenance, status-specific output fields, and
tool-specific arguments. It also checked alignment between prompt instructions
and runtime validation.

## Findings

None remain.

Two High findings raised during review were corrected before closure:

1. `CandidatePayload` status-specific fields and nullability are now explicit in
   the prompt and enforced at runtime.
2. Each read-only tool now declares and validates its required arguments, bounded
   integer ranges, and unused null arguments.

## Closure evidence

The final independent closure review confirmed no Critical or High contradiction
between the prompt, `CandidatePayload`, and `ToolRequest`.

## Limitations

This was a read-only static review. Runtime behavior is covered separately by the
version 1.6 behavior report and repository tests.
