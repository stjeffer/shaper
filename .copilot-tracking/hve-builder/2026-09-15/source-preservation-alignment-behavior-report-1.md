# HVE Artifact Test Report: Source-Preservation Alignment

- Tested profile: Medium, GPT-5.6 Terra
- Run type: full with targeted evidence closure
- Behavior gate: Executed
- Fidelity: simulation
- Execution status: Complete
- Verdict: Pass
- Sandbox: cleaned up

## Summary

Two black-box scenarios exercised initial policy shaping and one narrow,
validator-directed repair. The simulated outputs preserved document identity,
subjects, controls, temporal qualifiers, advisory direction, and numeric facts.
They applied only approved transformation requirements and returned strict
candidate payloads. Independent grading passed after the complete payloads and
schema-validation evidence were persisted.

## Fidelity and limitations

The evidence demonstrates simulated prompt conformance at the Medium profile. It
does not establish native Azure activation, provider-side structured-output
enforcement, tool behavior, abstention, conflicting-evidence handling,
multiple-policy output, or complete production-schema interoperability.

The Medium-tier simulator may resolve ambiguity that a lower-tier model could
expose. This run does not establish unambiguous behavior at lower tiers.

## Reuse eligibility

Not applicable. This was a full run. The same execution evidence received a
targeted closure regrade after its complete payloads and schema trace were added
to the test log.

| Scenario | Requirement | Impact disposition | Evidence source | Grade provenance |
|---|---|---|---|---|
| SCN-SHAPE-001 | Initial shaping and approved authority | Fresh execution | Simulation | Fresh grade |
| SCN-SHAPE-002 | Targeted repair and source preservation | Fresh execution | Simulation | Fresh grade |

## Findings

No findings remain open. HVE-BEH-001 was closed after both simulated payloads and
their representative strict-schema validation were persisted.

## Coverage

The run covered initial shaping, diagnostic-only assessment evidence,
approved-requirement authority, organization and title retention, advisory and
mandatory controls, `after` and `during` qualifiers, numeric duration
preservation, unaffected-content retention, and narrow repair.

## Containment

The simulator was read-only. Pre-run and post-run workspace status showed no
unexpected source mutation. The lead wrote only HVE evidence and removed the
temporary sandbox after composing this report.

## Satisfied-and-skipped

None.

## Human review

- [ ] Reviewed and validated by a qualified human reviewer
