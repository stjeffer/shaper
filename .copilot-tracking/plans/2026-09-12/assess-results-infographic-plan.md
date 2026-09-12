<!-- markdownlint-disable-file -->
# RPI Plan: Assess Results infographic

## Task Metadata

* Task ID: assess-results-infographic
* Task slug: assess-results-infographic
* Planning status: Ready
* Plan date: 2026-09-12
* Phase details: .copilot-tracking/details/2026-09-12/assess-results-infographic-phase-details.md
* Plan critique: .copilot-tracking/reviews/plans/2026-09-12/assess-results-infographic-plan-critique.md

## Executive Summary

Replace the Assess table's sentence-style recommendations with compact, infographic-style Results that identify the document characteristics reducing AI usefulness. The implementation will use existing typed finding codes, remove ownership from document reshaping evidence and effort, preserve the separate approval-bound transformation workflow, and make every visual result understandable without color or icon interpretation.

### User Decisions and Requirements Highlights

* Results must focus on content reshaping problems such as oversized sections and references to other documents, not accountability.
* The presentation must be infographic-like rather than a paragraph of recommendations.

### What You May Not Know

* The backend already returns typed finding codes for long paragraphs and cross-document references, so the UI does not need a new API schema. It does not currently measure heading-bounded section size.
* Missing ownership currently increases reshaping effort as well as producing the unwanted recommendation; both effects must be removed.

### Unresolved Decisions or Blockers

* None.

For current user input, see [User Decisions and Requirements](#user-decisions-and-requirements).

## User Decisions and Requirements

* Replace recommendations in the Assess tab with Results.
* Results should use an infographic style.
* Results should illustrate document characteristics that need resolving for AI use, including large content blocks and references to other documents. The current supported large-content signal is a paragraph longer than 150 words.
* Do not present owner/accountability actions as content-quality work.
* Preserve the application's purpose as reshaping content for AI.

## Goals

* Make per-document AI-readiness problems immediately scannable.
* Align result semantics and reshaping effort with content quality rather than governance ownership.
* Reuse the existing report contract and visual language to keep the change bounded and maintainable.

## Scope and Non-Goals

### In Scope

* Per-document discovery assessment semantics in `DocumentAssessmentService`.
* The Assess/Discover document table heading and result renderer.
* Responsive, accessible visual styling for result indicators.
* Targeted backend and static UI regression coverage.

### Non-Goals

* Removing or redesigning the downstream Recommend/approval workflow.
* Changing estate-wide governance findings or public report schemas.
* Adding counts or locations for each issue when the current report only exposes presence.
* Redesigning unrelated tabs or navigation labels.

## Functional Requirements

* Document readiness must not emit `missing_owner` as a reshaping finding or use ownership in metadata completeness, readiness, or effort.
  * Observable acceptance criteria: An ownerless otherwise-identical document has the same per-document readiness report as one with an owner, excluding document identity.
* The Assess table must label the final column Results and render typed result indicators from `finding_codes`.
  * Observable acceptance criteria: Long paragraphs and cross-document references appear as separate, concise visual results.
* The Results renderer must ignore accountability-only legacy codes, preserve unknown future codes as a generic unresolved result, and show a clear positive state only when no content issue codes remain.
  * Observable acceptance criteria: A report containing only `missing_owner` displays "No content issues detected"; a report containing an unknown code displays "Additional issue detected"; neither displays an owner prompt.
* Existing discovery, selection, and downstream recommendation actions must continue to work.
  * Observable acceptance criteria: Existing document checkboxes and Get recommendations behavior remain wired to the same controls.

## Non-Functional Requirements

* Results must be accessible without relying on icon shape or color.
  * Objective threshold or evaluation condition: Every result has visible text; decorative icons are hidden from assistive technology; the Results cell has meaningful list semantics.
  * Operating condition or verification approach: Static source inspection plus rendered browser accessibility/visual validation.
  * Observable acceptance criteria: The accessibility tree exposes the Results cell as a labelled list within its document row, includes each visible result label, and excludes decorative icons.
* Results must reflow in narrow layouts without horizontal content clipping beyond the table's existing scroll container.
  * Objective threshold or evaluation condition: Indicators wrap within the Results cell at desktop and narrow viewport widths.
  * Operating condition or verification approach: Browser screenshots at representative desktop and mobile widths.
  * Observable acceptance criteria: Result labels remain readable and do not overlap.
* Existing deterministic assessment behavior must remain stable except for the intentional removal of ownership from document reshaping.
  * Objective threshold or evaluation condition: Targeted assessment and orchestration tests pass.
  * Observable acceptance criteria: Existing content-quality findings and effort-band validation remain green.

## Acceptance Criteria

* The table heading reads Results rather than Findings.
* Per-document results are separate visual indicators, not joined imperative sentences.
* Long paragraphs and document references have distinct indicators.
* Missing ownership is absent from per-document Results, recommendations, and reshaping effort.
* Supported structure, freshness, metadata, FAQ, and procedural issues remain represented.
* A document with no supported content issues has a clear positive result state.
* The infographic remains understandable through text and semantic structure with color removed.
* Targeted tests, lint/format checks, and the defined desktop, narrow, zoom, accessibility-tree, selection, and recommendation-flow browser checks pass.

## Implementation Context Record

| Context item | Current artifact or record |
|---|---|
| Plan | .copilot-tracking/plans/2026-09-12/assess-results-infographic-plan.md |
| Phase details | .copilot-tracking/details/2026-09-12/assess-results-infographic-phase-details.md |
| Latest critique | .copilot-tracking/reviews/plans/2026-09-12/assess-results-infographic-plan-critique.md with Revise verdict; all PC-001-PC-004 findings resolved directly |
| Relevant research | .copilot-tracking/research/2026-09-12/assess-results-infographic-research.md |
| Changes-record role | .copilot-tracking/changes/2026-09-12/assess-results-infographic-changes.md is created by implementation |
| Planning execution and readiness | Complete and implementation-ready after one final-candidate critique |
| Continuation context | Automatic RPI parent continues to implementation |

## Sources

* Caller request: Defines Results semantics, infographic presentation, representative issues, and the accountability exclusion.
* .copilot-tracking/research/2026-09-12/assess-results-infographic-research.md: Establishes existing data contracts, current rendering behavior, alternatives, and readiness.
* prototype/copilot-studio-knowledge-compiler/index.html: Defines the Assess/Discover table and workflow controls.
* prototype/copilot-studio-knowledge-compiler/app.js: Defines current report rendering and summary behavior.
* src/shaper/application/assessment.py: Defines per-document findings, reasons, and effort.
* src/shaper/application/orchestration.py: Defines downstream transformation actions.

## Phase Checklist

<!-- rpi:phase id=P01 -->
### [x] P01: Align reshaping evidence with content quality

* Intent: Remove accountability-only ownership from per-document AI-readiness findings and effort without changing estate-wide governance assessment.
* Dependencies: Existing deterministic report contract and tests.

<!-- rpi:task id=P01-T01 -->
#### [x] P01-T01: Remove ownership from per-document discovery findings

* Requirement and evidence: User excludes owner/accountability actions; research C5 and C7 show `missing_owner` leaks into findings, reasons, and effort.
* Expected result: `DocumentAssessmentService` no longer emits or explains missing ownership, and shared metadata scoring measures content metadata only.
* Detail section: P01-T01 in .copilot-tracking/details/2026-09-12/assess-results-infographic-phase-details.md

<!-- rpi:task id=P01-T02 -->
#### [x] P01-T02: Remove ownership from per-document transformation actions

* Requirement and evidence: User excludes owner actions from reshaping; research C10 shows a second mapping can reintroduce it downstream.
* Expected result: `TransformationAgent.recommend()` never proposes adding ownership metadata.
* Detail section: P01-T02 in .copilot-tracking/details/2026-09-12/assess-results-infographic-phase-details.md

<!-- rpi:phase id=P02 -->
### [x] P02: Render accessible infographic Results

* Intent: Replace prose findings with compact, semantic, code-driven result indicators.
* Dependencies: P01 semantics and existing `finding_codes`.

<!-- rpi:task id=P02-T01 -->
#### [x] P02-T01: Rename and render the Results surface

* Requirement and evidence: User requests Results; research C2, C3, C5, and C9 show the exact heading and typed input.
* Expected result: The final column is Results; each supported code renders one visual item; unknown codes render one generic unresolved item; accountability-only legacy codes remain hidden.
* Detail section: P02-T01 in .copilot-tracking/details/2026-09-12/assess-results-infographic-phase-details.md

<!-- rpi:task id=P02-T02 -->
#### [x] P02-T02: Style responsive and accessible result indicators

* Requirement and evidence: User requests infographic style; accessibility requires visible text, semantic grouping, non-color cues, and reflow.
* Expected result: Results wrap cleanly, distinguish issue categories visually, and retain meaning without color or icons.
* Detail section: P02-T02 in .copilot-tracking/details/2026-09-12/assess-results-infographic-phase-details.md

<!-- rpi:phase id=P03 -->
### [x] P03: Lock behavior and validate the rendered outcome

* Intent: Prove the semantic removal, static UI contract, and actual browser presentation.
* Dependencies: P01 and P02 complete.

<!-- rpi:task id=P03-T01 -->
#### [x] P03-T01: Add targeted regression tests

* Requirement and evidence: Tests must distinguish intentional ownership removal from preserved content findings.
* Expected result: Maximum two added test cases: one backend owner-invariance test and one static UI contract test. Extend the existing transformation-agent proposal test with a legacy `missing_owner` fallback assertion.
* Detail section: P03-T01 in .copilot-tracking/details/2026-09-12/assess-results-infographic-phase-details.md

<!-- rpi:task id=P03-T02 -->
#### [x] P03-T02: Run targeted and visual validation

* Requirement and evidence: Static tests cannot decide adaptive rendering or conveyed visual hierarchy.
* Expected result: Targeted pytest and repository lint/format commands pass. Browser checks at 1280px, 320px, and 200% zoom cover issue, empty, accountability-only legacy, and unknown-code states; inspect list/row association and decorative-icon exclusion; exercise document selection and Get recommendations.
* Detail section: P03-T02 in .copilot-tracking/details/2026-09-12/assess-results-infographic-phase-details.md

## Dependencies

* Existing `DocumentReadinessReport.finding_codes`: canonical UI input; no schema migration is planned.
* Existing prototype static serving: required for browser validation.
* Existing project pytest and formatting/lint commands: validation must use repository-native tooling.

## Critique Disposition

| Critique run and finding | Disposition | Plan response or residual risk |
|---|---|---|
| PC-001 | Resolved | Replaced unsupported "large section" claims with the existing long-paragraph/oversized-passage signal and explicitly documented the detector boundary. |
| PC-002 | Resolved | Assigned legacy mapping coverage to the existing transformation-agent test and added explicit browser interaction checks. |
| PC-003 | Resolved | Defined exact viewport, zoom, fixture-state, accessibility-tree, and interaction evidence. |
| PC-004 | Resolved | Unknown codes produce a generic unresolved result; only empty or accountability-only reports receive the positive state. |

## Follow-Up Items

* Exact issue counts and source locations: outside current report contract; consider only if presence indicators prove insufficient.

## Handoff

* Implementation artifact: .copilot-tracking/changes/2026-09-12/assess-results-infographic-changes.md
* Ready phase or task: Review
* Remaining provisional question or blocker: None
