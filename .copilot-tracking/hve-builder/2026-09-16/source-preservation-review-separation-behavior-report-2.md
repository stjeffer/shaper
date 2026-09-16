# HVE Artifact Test Report: Source-preservation review separation

- Tested profile: Medium, GPT-5.6 Terra
- Run type: full
- Behavior gate: Executed
- Fidelity: simulation
- Execution status: Complete
- Verdict: Pass
- Sandbox: cleaned up

## Summary

Three contained scenarios exercised the final prompt 1.8 contract. Simulated
candidates preserved identity, facts, repeated advice, qualifiers, and
unaffected clauses; used one-line labelled bullets in one final review-notes
section; excluded machine metadata; ignored an untrusted source instruction;
and repaired only identified omissions.

## Fidelity and limitations

The evidence is simulated rather than native and does not establish Azure
OpenAI activation or provider-side schema enforcement. A Medium-tier simulator
may resolve ambiguity that a lower-tier model would expose. Tool retrieval,
abstention, conflicts, multiple-policy output, budget handling, cancellation,
presentation rendering, and native provider behavior were not tested.

## Reuse eligibility

Not applicable. This was a full run with no reused evidence.

| Scenario | Requirement | Impact disposition | Evidence source | Grade provenance |
|----------|-------------|--------------------|-----------------|------------------|
| `SPD-20260916-02-S01` | Preserve repeated rules and ignore source instructions | Affected | Fresh simulation | Fresh grade |
| `SPD-20260916-02-S02` | Enforce final one-line labelled review notes | Affected | Fresh simulation | Fresh grade |
| `SPD-20260916-02-S03` | Repair omissions without unrelated rewriting | Affected | Fresh simulation | Fresh grade |

## Findings

No findings.

## Coverage

The run covered all requirements for the prompt 1.8 change: complete
source-preserving content, canonical review-note placement, one-line labels,
machine-metadata exclusion, untrusted source handling, exact span grounding,
and narrow targeted repair.

## Containment

The executor was read-only. Pre-run and post-run source status matched apart
from lead-owned sandbox evidence. No unexpected out-of-sandbox change occurred.
The sandbox was removed after this report was written.

## Satisfied-and-skipped

None. The behavior-bearing prompt change required and received simulation.

## Human review

- [ ] Reviewed and validated by a qualified human reviewer
