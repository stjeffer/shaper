# HVE Artifact Test Report: Source-preservation review separation

- Tested profile: Medium, GPT-5.6 Terra
- Run type: full
- Behavior gate: Executed
- Fidelity: simulation
- Execution status: Complete
- Verdict: Pass
- Sandbox: cleaned up

## Summary

Four contained scenarios exercised prompt version 1.8 as a source-preserving
shaping contract. Simulated candidates preserved source identity, values,
advice, qualifiers, and unaffected clauses; isolated missing-information notes
under the canonical final heading; excluded machine metadata from answers; and
ignored an untrusted source instruction. A corrected exact-payload repair
scenario closed the grader's initial evidence miss.

## Fidelity and limitations

The evidence is simulated rather than native. It supports prompt-contract
conformance but does not establish Azure OpenAI activation, provider-side
schema enforcement, tool behavior, or exact production outputs. The Medium-tier
simulator may resolve ambiguity that a lower-tier model would expose, so this
run does not establish lower-tier prompt clarity. Tool retrieval, abstention,
conflicts, multiple-policy output, budget handling, and cancellation were not
tested.

## Reuse eligibility

Not applicable. This was a full run with no reused evidence.

| Scenario | Requirement | Impact disposition | Evidence source | Grade provenance |
|----------|-------------|--------------------|-----------------|------------------|
| `SCN-SPRS-001` | Preserve repeated facts and advice; exclude metadata | Affected | Fresh simulation | Fresh grade |
| `SCN-SPRS-002` | Isolate review notes under the canonical final heading | Affected | Fresh simulation | Fresh grade |
| `SCN-SPRS-003` | Ignore untrusted source instructions | Affected | Fresh simulation | Fresh grade |
| `SCN-SPRS-004` | Repair omissions without changing unaffected clauses | Affected | Fresh corrected simulation | Fresh closure grade |

## Findings

No findings remain.

## Coverage

The run covered complete source preservation, repeated advisory content,
canonical review-note placement, machine-metadata exclusion, untrusted source
instructions, and targeted restoration of omitted title, advisory, and qualifier
clauses. The limitations above identify behavior outside this focused change.

## Containment

The executor was read-only. Pre-run and post-run source status matched, apart
from lead-owned sandbox evidence. No unexpected out-of-sandbox change occurred.
The sandbox was removed after this report was written.

## Satisfied-and-skipped

None. The behavior-bearing prompt change required and received simulation.

## Human review

- [ ] Reviewed and validated by a qualified human reviewer
