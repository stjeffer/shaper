<!-- markdownlint-disable-file -->
# RPI Plan Critique: Assess Results infographic

## Metadata

* Task ID: assess-results-infographic
* Critique date: 2026-09-12
* Plan: .copilot-tracking/plans/2026-09-12/assess-results-infographic-plan.md
* Phase details: .copilot-tracking/details/2026-09-12/assess-results-infographic-phase-details.md
* Critique execution status: Complete

## Inputs and Criterion Boundary

* Task context and caller requirements: Replace useless owner/accountability recommendations in the Assess tab with infographic-style Results showing document problems for AI, including large sections and cross-document references.
* Research and evidence considered: .copilot-tracking/research/2026-09-12/assess-results-infographic-research.md.
* Decisions, dependencies, and acceptance criteria considered: All requirements, scope boundaries, phases P01-P03, tasks P01-T01 through P03-T02, declared dependencies, exact ownership removals, the two-added-test ceiling, semantic and regression coverage, and accessibility and browser acceptance criteria.
* Assessment boundary: This critique assesses only the supplied caller requirement, plan, phase details, and research. It does not independently inspect source or tests and cannot validate implementation facts beyond the supplied evidence.

## Coverage Assessment

| Requirement, research, phase, or task ID | Coverage | Evidence or concern |
|---|---|---|
| Caller: replace recommendations with infographic Results | Covered | P02-T01 and P02-T02 replace prose with code-driven, text-labelled visual items. |
| Caller: show large sections | Partial | The plan alternates between “long sections” and `long_paragraph`, while research C8 establishes only a 150-word paragraph detector. |
| Caller: show cross-document references | Covered | P02-T01 maps `cross_policy_reference` to a distinct result. |
| FR: remove owner/accountability semantics | Covered | P01-T01 removes `missing_owner` from codes, reasons, and effort; P01-T02 removes its transformation mapping; P02-T01 filters historical values while preserving estate governance. |
| FR: preserve discovery, selection, and recommendation controls | Partial | The acceptance criterion exists, but P03 does not identify a concrete interaction check for selection and Get recommendations. |
| FR: safe unknown/legacy behavior and positive state | Partial | Filtering is planned, but “No content issues detected” can overstate an unknown-code report. |
| NFR: accessible without icon or color dependence | Partial | Semantic list, visible text, and hidden decorative icons are specified, but the screen-reader acceptance claim lacks matching completion evidence. |
| NFR: narrow-layout reflow | Partial | Browser validation is required, but neither viewport sizes nor state fixtures are defined. |
| P03-T01: maximum two added tests | Partial | The two proposed additions cover owner invariance and static UI, but direct orchestration regression is left to an unspecified existing-test update. |
| P01-P03 dependencies | Covered | Backend semantics precede rendering; implementation precedes test and browser validation. |

## Verdict

* Verdict: Revise
* Rationale: The direction and removal boundaries are credible, but the candidate conflates paragraph length with the requested large-section result and leaves preservation, legacy orchestration, and accessibility/browser acceptance insufficiently decidable.

## Findings

<!-- rpi:critique id=PC-001 -->
### PC-001 [High]: The planned “large sections” result is not supported by the cited detector

* Related IDs: Caller large-sections requirement; Acceptance Criteria; research C6 and C8; P02-T01
* Evidence: .copilot-tracking/research/2026-09-12/assess-results-infographic-research.md states that `long_paragraph` uses a 150-word paragraph threshold, while .copilot-tracking/plans/2026-09-12/assess-results-infographic-plan.md promises “Long sections.”
* Concern: The plan treats a long paragraph as evidence of a large section without establishing equivalence.
* Impact: The UI could claim it detects the requested document problem when it detects a materially narrower characteristic.
* Smallest useful change: Use an accurate “long paragraph” or “oversized passage” result throughout, or add a separately researched section-size detector and its validation; do not retain the unsupported “long sections” wording.
* Action owner: Planning parent
* Exact resolving evidence: Revised requirements, result vocabulary, tasks, and acceptance criteria consistently name the supported signal, or supplied research and a planned test establish a true section-size detector.
* Decision route: Direct planner correction; the confirmed user direction does not require another user decision.

<!-- rpi:critique id=PC-002 -->
### PC-002 [Medium]: The two-test strategy does not assign proof for all changed and preserved semantics

* Related IDs: FR preserve existing actions; P01-T02; P03-T01; P03-T02
* Evidence: .copilot-tracking/details/2026-09-12/assess-results-infographic-phase-details.md proposes two new tests for owner invariance and the static UI contract, while P01-T02 separately requires legacy `missing_owner` transformation behavior and the plan requires selection and Get recommendations to remain functional.
* Concern: “Targeted orchestration tests pass” does not identify which existing test will be updated to prove owner mapping removal, and no named validation step exercises the preserved browser controls.
* Impact: The implementation could satisfy the two new tests while retaining an owner action for legacy reports or breaking the downstream interaction wiring.
* Smallest useful change: Within the two-new-test ceiling, name the existing orchestration test to update with owner exclusion/content fallback assertions and add explicit checkbox/Get recommendations interaction checks to P03-T02 browser validation.
* Action owner: Planning parent
* Exact resolving evidence: P03 names the existing orchestration test and its assertions, and its browser checklist records successful selection and Get recommendations behavior.
* Decision route: Direct planner correction.

<!-- rpi:critique id=PC-003 -->
### PC-003 [Medium]: Accessibility and responsive validation are not reproducible enough to decide acceptance

* Related IDs: NFR accessibility; NFR narrow layout; P02-T02; P03-T02
* Evidence: .copilot-tracking/plans/2026-09-12/assess-results-infographic-plan.md requires screen-reader output and desktop/mobile screenshots; .copilot-tracking/details/2026-09-12/assess-results-infographic-phase-details.md only specifies representative viewports and says browser inspection does not claim full screen-reader conformance.
* Concern: No viewport widths, required result states, accessibility-tree checks, keyboard/zoom condition, or association check are enumerated.
* Impact: A subjective browser pass may miss clipping, lost table context, inaccessible decorative icons, or an unverified screen-reader claim.
* Smallest useful change: Define a browser checklist with exact desktop and narrow widths, 200% zoom or equivalent reflow check, issue/empty/legacy fixtures, accessibility-tree list and row association checks, and icon exclusion; align the acceptance wording with what that evidence can prove.
* Action owner: Planning parent
* Exact resolving evidence: P03-T02 contains the concrete checklist and requires recorded screenshots plus accessibility-tree observations for every named state.
* Decision route: Direct planner correction.

<!-- rpi:critique id=PC-004 -->
### PC-004 [Medium]: Unknown codes can produce a misleading all-clear result

* Related IDs: FR unknown-code handling; Acceptance Criteria; research residual uncertainty; P02-T01
* Evidence: The plan requires unknown codes to be ignored and displays “No content issues detected” when no supported issue remains.
* Concern: A report containing only an unknown future content code would be rendered as an unconditional positive state.
* Impact: Forward-compatible data could be silently misrepresented as AI-ready.
* Smallest useful change: Reserve “No content issues detected” for an actually empty or accountability-only known set; render a neutral “Additional result unavailable” state for unknown content codes, or change the all-clear copy to “No supported content issues detected.”
* Action owner: Planning parent
* Exact resolving evidence: Revised rendering rules and static UI assertions distinguish empty/accountability-only reports from reports containing unknown codes.
* Decision route: Direct planner correction.

## Strengths and Residual Risk

* The plan correctly identifies all three ownership leak paths: per-document code/reason and effort, downstream transformation mapping, and historical UI data.
* It preserves estate-wide governance and the approval-bound Recommend workflow rather than broadening the requested UI correction.
* Typed `finding_codes`, semantic list output, visible labels, hidden decorative icons, responsive wrapping, and a strict two-added-test ceiling form a bounded implementation approach.
* Presence-only indicators are an explicitly scoped residual limitation; counts and source locations remain deferred.

## Questions or Blocking Evidence Gaps

* None requiring user input. The planning parent can resolve all findings from the confirmed requirement and supplied evidence.

## Limitations

* Source, test, and runtime behavior were not independently inspected because the caller constrained the critique to supplied inputs.
* Exact colors and icons remain implementation choices subject to the stated non-color and visible-text requirements.

## Recommended Next Action

* Highest-impact finding: PC-001
* Action owner: Planning parent
* Smallest next action: Revise the plan and phase details to align the result wording and acceptance evidence with the actually supported paragraph signal, then incorporate PC-002 through PC-004 before implementation.
* User response required: No

## Relevant Artifacts

| Artifact | Description |
|---|---|
| [.copilot-tracking/plans/2026-09-12/assess-results-infographic-plan.md](.copilot-tracking/plans/2026-09-12/assess-results-infographic-plan.md) | Candidate implementation plan reviewed. |
| [.copilot-tracking/details/2026-09-12/assess-results-infographic-phase-details.md](.copilot-tracking/details/2026-09-12/assess-results-infographic-phase-details.md) | Phase and task execution details reviewed. |
| [.copilot-tracking/research/2026-09-12/assess-results-infographic-research.md](.copilot-tracking/research/2026-09-12/assess-results-infographic-research.md) | Supplied evidence boundary. |
| [.copilot-tracking/reviews/plans/2026-09-12/assess-results-infographic-plan-critique.md](.copilot-tracking/reviews/plans/2026-09-12/assess-results-infographic-plan-critique.md) | Complete final-candidate critique. |

## Next Steps

* Active planning parent should revise directly for PC-001 through PC-004; no user action is required.
