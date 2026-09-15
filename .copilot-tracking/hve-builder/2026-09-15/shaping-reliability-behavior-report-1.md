# HVE Artifact Test Report: Source-Preserving Policy Shaper

- Tested profile: Medium, GPT-5.6 Terra
- Run type: full with in-run evidence closure
- Behavior gate: Executed
- Fidelity: simulation
- Execution status: Complete
- Verdict: Pass
- Sandbox: cleaned up

## Summary

Nine black-box scenarios exercised complete policy preservation, missing-information
handling, narrow repair, hostile source content, declared read-only retrieval,
abstention, multiple policies, conflicting spans, and completion after a tool result.
Independent grading found no remaining prompt revision.

## Fidelity and Limitations

All responses were simulated; no native Azure OpenAI call or actual tool invocation
ran. The evidence supports prompt-contract conformance, not production latency or
target-model equivalence. One multiple-policy simulation preserved the intended
semantics but did not reproduce the provider-enforced schema exactly. Production schema
enforcement is independently covered by mechanical tests. A Medium-profile simulator
may also repair ambiguity that a lower-tier model would expose.

## Reuse Eligibility

Not applicable. This was a full run. Two initial evidence gaps were closed within the
same run by adding affected scenarios and preserving response envelopes before final
independent grading.

| Scenario | Requirement | Impact disposition | Evidence source | Grade provenance |
|---|---|---|---|---|
| SRP-01 | Complete conditional-policy preservation | Affected | Fresh simulation | Fresh grade |
| SRP-02 | Missing-information separation | Affected | Fresh simulation | Fresh grade |
| SRP-03 | Narrow targeted repair | Affected | Fresh simulation | Fresh grade |
| SRP-04 | Untrusted-source boundary | Affected | Fresh simulation | Fresh grade |
| SRP-05 | Declared read-only retrieval | Affected | Fresh simulation | Fresh grade |
| SRP-06 | Abstention without evidence or tools | Affected | Fresh simulation | Fresh grade |
| SRP-07 | Multiple-policy separation | Affected | Fresh simulation | Fresh grade |
| SRP-08 | Conflicting-source preservation | Affected | Fresh simulation | Fresh grade |
| SRP-09 | Post-tool completion | Affected | Fresh simulation | Fresh grade |

## Findings

No findings requiring correction, adjustment, deletion, improvement, or added coverage.

## Coverage

All contracted semantic behaviors represented in the accepted design were exercised.
Native provider behavior, latency, and actual tool invocation remain untested.

## Containment

The executor was read-only. Pre-run and post-run workspace status showed no unexpected
source changes from simulation. The temporary sandbox was removed after this durable
report was written.

## Satisfied-and-Skipped

None.

## Human Review

- [ ] Reviewed and validated by a qualified human reviewer
