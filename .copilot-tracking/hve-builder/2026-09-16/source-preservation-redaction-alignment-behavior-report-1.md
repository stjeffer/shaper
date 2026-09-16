<!-- markdownlint-disable-file -->

# HVE Artifact Test Report: source-preservation redaction alignment

* Tested profile: Medium, GPT-5.6 Terra
* Run type: correction with eligible full-run reuse
* Behavior gate: Executed
* Fidelity: simulation
* Execution status: Complete
* Verdict: Pass
* Sandbox: cleaned up

## Summary

Prompt 2.1 was validated against 16 black-box scenarios at Medium profile. The
prompt-only change from 2.0 fixed invalid exclusion authority handling. Scenario
SCN-010 was freshly simulated and independently graded. The remaining 15
scenarios reused eligible full-run evidence because the fixed generic abstention
reason cannot affect their paths. The combined evidence passed exact approved
exclusion, adjacent policy preservation, source-directive resistance,
non-invention, review-note safety, targeted repair, abstention, every declared
read-only tool path, tool-result consumption, document identity, conflict
handling, unresolved references, and multiple policy blocks.

## Fidelity and limitations

The run used contained literal simulation with GPT-5.6 Terra. It supports prompt
contract and instruction-clarity claims, not native Azure OpenAI activation,
structured-output reliability, validator behavior, or tool execution. A
Medium-tier simulator may resolve ambiguity that a lower-tier model would not.
Multilingual behavior and native cross-document conflict retrieval were not
tested.

## Reuse eligibility

The final prompt SHA-256 is
`e916cc68d63a6e1d8d15f68c9247b72a8c9b54fe0ee7ca292ab2b19cc0bb30bb`.
The 2.0 full-run evidence remained eligible for SCN-001 through SCN-009 and
SCN-011 through SCN-016. The 2.1 change affected only the reason returned when
approved exclusion authority does not match the supplied source, so SCN-010 was
rerun and regraded against the final hash.

| Scenario | Requirement | Impact disposition | Evidence source | Grade provenance |
|----------|-------------|--------------------|-----------------|------------------|
| SCN-001 through SCN-009 | Unchanged prompt paths | unaffected and reused | eligible 2.0 full-run payloads | prior independent grade |
| SCN-010 | Invalid exclusion authority | affected and freshly executed | final 2.1 correction payload | fresh independent grade |
| SCN-011 through SCN-016 | Unchanged prompt paths | unaffected and reused | eligible 2.0 full-run payloads | prior independent grade |

## Findings

| # | Action | Mapped dimension | Artifact | Profile | Evidence class | Severity | Evidence | Resolving change |
|---|--------|------------------|----------|---------|----------------|----------|----------|------------------|
| None | None | None | shaping prompt 2.1 | Medium | simulation | None | All scenarios passed | None |

## Coverage

The run covered candidate, tool, and abstain statuses; exact and invalid
exclusion authority; source-authored directives; unsupported comparisons;
unapproved preservation; invented review-note policy; source-faithful repair;
unresolved references; conflicting values; all four read-only tools; returned
tool evidence; source identity; and multiple policies.

SCN-010 returned `abstain`, empty answer, question, and claim fields, confidence
`0`, no tool request, and the exact generic reason `Approved exclusion authority
does not match the supplied source.` The response did not repeat, quote,
paraphrase, or audit the unauthorized exclusion text.

## Containment

The simulation worker was read-only. The lead owned sandbox evidence writes.
Pre-run and post-run source status showed no unexpected executor changes.

## Satisfied-and-skipped

None.

## Human review

* [ ] Reviewed and validated by a qualified human reviewer
