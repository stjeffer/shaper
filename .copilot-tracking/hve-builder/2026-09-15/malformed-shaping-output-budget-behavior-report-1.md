# HVE Artifact Test Report: Shaping Prompt 1.6

- Tested profile: Medium / GPT-5.6 Terra
- Run type: full
- Behavior gate: Executed
- Fidelity: simulation
- Execution status: Complete
- Verdict: Pass
- Sandbox: cleaned up

## Summary

The shaping prompt was exercised through contained literal simulation for initial
transformation, targeted repair, declared tool and abstain branches, and distinct
policy handling. The evidence supports the diagnostic-versus-authoritative
boundary and the version 1.6 concise-claims contract. Independent grading found no
remaining findings.

## Fidelity and limitations

Instruction following, authority separation, preservation, concise provenance
claims, repair scope, and response shapes were simulated. Representative response
structures also passed the repository's `CandidatePayload` validation. Azure
generation, actual tool invocation, deterministic validator decisions, budgets,
cancellation, and retry behavior were not observed. This run does not establish
native Azure reliability or lower-tier prompt clarity.

## Reuse eligibility

Not applicable. The claims contract changed from version 1.5, so this was a full
run with fresh design, execution, and grading.

| Scenario | Requirement | Impact disposition | Evidence source | Grade provenance |
|----------|-------------|--------------------|-----------------|------------------|
| HBT-SHAPING-1.6-ISO-001 | R1-R5, R7-R8 | Affected | Fresh simulation | Fresh grade |
| HBT-SHAPING-1.6-ISO-002 | R2, R5-R6, R8 | Affected | Fresh simulation | Fresh grade |
| HBT-SHAPING-1.6-ISO-003 | R2, R8-R9 | Affected | Fresh simulation and schema validation | Fresh grade |
| HBT-SHAPING-1.6-ISO-004 | R2, R5, R8, R10 | Affected | Fresh simulation and schema validation | Fresh grade |

## Findings

None.

## Coverage

All R1-R10 requirements passed. The run covered findings as diagnostic evidence,
approved requirements as the sole change authority, preservation of unresolved
gaps, grounded restructuring, concise exact-span claims, targeted repair,
untrusted source instructions, schema-valid response branches, tool/abstain
selection, and distinct-policy separation.

Provider finish-reason classification, live completion-token behavior, actual tool
continuation, and deterministic preservation implementation were validated outside
this prompt behavior gate or remain native integration concerns.

## Containment

Pre-run and post-run status retained the two pre-existing staged user assets and
the implementation changes. Simulators wrote no files and performed no external
or target-declared actions. The lead created and then removed only the dedicated
sandbox evidence.

## Satisfied-and-skipped

None.

## Correction closure

Static review identified that status-specific fields and tool arguments were
advisory rather than fully runtime-enforced. The correction added matching
`CandidatePayload` and `ToolRequest` validators and made every tool's required
arguments explicit in the prompt.

The prior report was Complete/Pass with no open behavior finding, and design
`HBTD-SHAPING-1.6-ISO-001`, profile, model, modality, and simulation fidelity were
unchanged. The output-contract change affected R8 in every scenario and R9 in
Scenario 003; those behaviors were freshly simulated. All candidate, tool, and
abstain traces passed the corrected field contract, and no R1-R7 or R10 regression
was observed. Independent final static closure returned Pass. The overall behavior
verdict remains Pass.

## Human review

- [ ] Reviewed and validated by a qualified human reviewer
