<!-- markdownlint-disable-file -->
# RPI Plan Critique: Filter legacy Result count

## Metadata

* Task ID: filter-legacy-result-count
* Critique date: 2026-09-12
* Plan: .copilot-tracking/plans/2026-09-12/filter-legacy-result-count-plan.md
* Phase details: .copilot-tracking/details/2026-09-12/filter-legacy-result-count-phase-details.md
* Critique execution status: Complete

## Inputs and Criterion Boundary

* Task context and caller requirements: Shared classification must exclude `missing_owner` from row and aggregate counts, count each supported code, collapse all unknown codes to one generic result per document, add no new test case, and preserve existing behavior.
* Research and evidence considered: .copilot-tracking/research/2026-09-12/filter-legacy-result-count-research.md and RV-001 in .copilot-tracking/reviews/logs/2026-09-12/assess-results-infographic-review.md.
* Decisions, dependencies, and acceptance criteria considered: The supplied direction fixes RV-001 through one pure classifier used by row rendering and summary counting; the existing static UI test is extended rather than adding a test case; repository-native targeted and full validation must pass.
* Assessment boundary: This critique assesses only the supplied plan, phase details, research, RV-001, and caller requirements. It can judge implementation readiness and validation intent, but not implementation correctness before a diff and command results exist.

## Coverage Assessment

| Requirement, research, phase, or task ID | Coverage | Evidence or concern |
|---|---|---|
| Caller requirement: exclude `missing_owner` | Covered | The plan acceptance criteria exclude it from row and aggregate results; P01-T01 assigns both consumers to the shared classifier. |
| Caller requirement: count supported codes individually | Covered | The plan acceptance criteria and P01-T01 context explicitly preserve one result per supported code. |
| Caller requirement: collapse unknown codes per document | Covered | The functional and acceptance criteria require at most one generic unknown result per document, including when multiple unknown codes occur. |
| Caller requirement: add no new test case | Covered | P01-T02 explicitly extends the existing Results UI test and excludes new test cases. |
| Caller requirement: preserve existing behavior | Covered | Scope excludes presentation metadata and redesign; the non-functional acceptance criterion limits observable change to the corrected count; P01-T02 requires targeted and full repository-native checks. |
| RV-001 | Covered | P01-T01 centralizes the divergent row and aggregate paths identified by RV-001, and P01-T02 adds a regression assertion in existing coverage. |
| P01-T01 dependencies and completion | Covered | The task is local, has no prerequisite, identifies the implementation target, prohibits duplicated raw-length summary logic, and requires source/test evidence. |
| P01-T02 dependencies and completion | Covered | It depends on P01-T01 and names targeted/full tests, Ruff, formatting, mypy, JavaScript syntax, and whitespace validation. |

## Verdict

* Verdict: Pass
* Rationale: The plan and details directly encode every supplied classification rule, route both row and aggregate behavior through one pure helper, honor the no-new-test-case constraint, and define proportionate regression and repository-wide validation. The evidence identifies the exact defect and leaves no decision-critical gap.

## Findings

* No actionable findings.

## Strengths and Residual Risk

* The planned helper makes the aggregate count a consequence of the same presentable-result array used by rows, preventing future semantic drift between the two consumers.
* Supported, accountability-only, and unknown classifications are stated independently, including the per-document cardinality of the unknown fallback.
* Validation extends an existing test case and combines source-contract checks with the repository's full automated checks, preserving the caller's explicit testing boundary.
* Residual implementation risk is limited to faithfully encoding the stated classifier and is adequately gated by diff inspection and the specified validation.

## Questions or Blocking Evidence Gaps

* None.

## Limitations

* No implementation diff or post-change command output was in scope; those are appropriately required as completion evidence rather than prerequisites to this planning verdict.

## Recommended Next Action

* Highest-impact finding: None.
* Action owner: Planning parent.
* Smallest next action: Finalize the candidate and dispatch P01-T01 followed by P01-T02.
* User response required: No.

## Relevant Artifacts

| Artifact | Description |
|---|---|
| [.copilot-tracking/plans/2026-09-12/filter-legacy-result-count-plan.md](.copilot-tracking/plans/2026-09-12/filter-legacy-result-count-plan.md) | Final-candidate implementation plan assessed by this critique. |
| [.copilot-tracking/details/2026-09-12/filter-legacy-result-count-phase-details.md](.copilot-tracking/details/2026-09-12/filter-legacy-result-count-phase-details.md) | Task boundaries, dependencies, validation, and completion evidence. |
| [.copilot-tracking/research/2026-09-12/filter-legacy-result-count-research.md](.copilot-tracking/research/2026-09-12/filter-legacy-result-count-research.md) | Converged evidence and classification decisions. |
| [.copilot-tracking/reviews/logs/2026-09-12/assess-results-infographic-review.md](.copilot-tracking/reviews/logs/2026-09-12/assess-results-infographic-review.md) | Source review containing RV-001. |
| [.copilot-tracking/reviews/plans/2026-09-12/filter-legacy-result-count-plan-critique.md](.copilot-tracking/reviews/plans/2026-09-12/filter-legacy-result-count-plan-critique.md) | This complete final-candidate critique. |

## Next Steps

No user action is required. The active planning parent can finalize the plan and continue to implementation.
