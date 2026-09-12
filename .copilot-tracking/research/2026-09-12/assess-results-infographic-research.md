<!-- markdownlint-disable-file -->

# Task Research: assess-results-infographic

| Field | Value |
|---|---|
| Date | 2026-09-12 |
| Researcher / agent | RPI Agent using rpi-research |
| Status | Complete |
| Artifact path | .copilot-tracking/research/2026-09-12/assess-results-infographic-research.md |

## Research Brief

* What to research: How the Assess tab currently derives and presents document recommendations, and which existing document-quality signals can support infographic-style Results focused on AI-readiness problems.
* Why it matters: The current owner-oriented recommendations misrepresent the product as an accountability tool instead of helping users reshape content for AI consumption.
* Audience or intended use: Product implementation planning for users assessing a document estate.
* Scope: Assess-tab UI, assessment domain/application models, projections/API payloads, and related tests.
* Non-goals: Implementing changes, redesigning unrelated tabs, or introducing unsupported new analysis capabilities during Research.
* Criteria: Findings must cite current code and distinguish already-computed signals from signals requiring backend work.
* Requested outputs: A converged implementation direction and planning readiness assessment.
* Output mode: convergence.

## Research Parameters

| Field | Value |
|---|---|
| Research question(s) | What should replace Recommendations, and how can Results visually communicate document characteristics that reduce AI usefulness? |
| Codebase scope | src/, tests/, and directly related project documentation |
| External scope | None; repository behavior and user direction are authoritative |
| Initial internal candidate areas | Assess UI, assessment models, API/view models, assessment tests |
| Initial external candidate areas | None |
| Research posture | focused |
| Posture provenance | Default for a bounded internal feature with supplied failure evidence |
| Explicit limits / deadline | None |
| Posture-specific completion basis | Focused scope and materiality |
| Edits allowed during research? | No, research-only |
| Resolved evidence root | .copilot-tracking/ |
| Known constraints / excluded sources | Do not implement or review during Research |

## Extension Registry and Provenance

| Kind | Candidate | Match and provenance | Scoped authority or output contract | Selected / skipped reason |
|---|---|---|---|---|
| Instruction | copilot-tracking.instructions.md | Applies to the evidence path | Tracking artifact format and location | Selected |
| Skill | rpi-research | Explicit RPI phase | Three-wave research and evidence contract | Selected |
| Skill | analysis-authoring | Infographic/dashboard-adjacent description | Analytical visualization conventions | Skipped; this is an application UI, not an analytical dashboard |
| Research specialist | None | Scope is compact and locally inspectable | N/A | Skipped; direct inspection is faster and avoids duplicated context |

## User Participation and Research Decisions

| Checkpoint | Questions or no-interaction rationale | Answers / unanswered | Resulting decision or selected further research |
|---|---|---|---|
| Intake | User supplied the product correction, target tab, replacement label, visual style, and representative quality signals. | No unanswered intake question materially blocks research. | Research the current implementation and converge on a content-quality Results design. |
| Direction change | None. | None. | Preserve the stated direction. |
| Convergence | Pending completed evidence cycle. | Pending. | Pending. |

## Scope and Success Criteria

* Scope: Trace current Assess-tab data from analysis through UI and identify the smallest coherent redesign surface.
* Assumptions: The existing assessment pipeline may already expose structural metrics suitable for Results; verify rather than assume.
* Success criteria:
  * Every research question is answered or its missing evidence is named.
  * Code findings use stable evidence IDs and workspace-relative path:line locations.
  * The selected direction is implementable without retaining accountability-oriented semantics.
  * Alternatives, risks, and planning readiness are explicit.

## Task Research Requests

* Explicit requests: Replace Recommendations with Results; use an infographic style; show issues such as large sections and references to other documents; focus on factors that make content poor for AI.
* Inferred research questions: Which signals exist today, which presentation surfaces must change, and which tests define current behavior?
* Caller constraints and non-goals: This is a content-reshaping capability, not an owner/accountability tool.

## Direction Controls

| Control type | Direction or boundary | Source |
|---|---|---|
| Change | Replace Recommendations with Results. | Caller |
| Narrow | Focus results on document characteristics that reduce AI usefulness. | Caller |
| Exclude | Do not recommend adding owners or frame the feature as accountability. | Caller |
| Add | Prefer infographic-style presentation over generic recommendation text. | Caller |

## Candidate Research Areas

* Wider: locate the Assess UI and all recommendation/result data contracts.
* Deeper: trace available metrics and existing presentation/test expectations.
* Contrarian: test whether a label-only/UI-only change would be insufficient or whether new backend analysis is actually necessary.

## Research Cycle Log

### Cycle 1

* Status: Complete.
* Wider wave: Located the browser prototype, per-document report contract, discovery endpoint, assessment heuristics, and transformation mapping. The user-visible "recommendations" in the Assess/Discover table are `report.reasons`; the durable evidence is already available separately as `report.finding_codes`.
* Deeper wave: Traced rendering from discovery response into `state.reports` and `renderDocuments()`. The UI currently joins imperative reason strings into one text cell, while the report already exposes typed findings for long paragraphs, cross-policy references, structure, freshness, metadata, FAQ coverage, and procedural clarity.
* Contrarian wave: A backend schema expansion is unnecessary because typed result codes already cross the API boundary. A label-only change is insufficient because it would retain imperative recommendation prose, the owner signal, and an unscannable text block. Removing the entire downstream Recommend stage would be an unrelated workflow change; it should remain distinct from read-only assessment Results.
* Parent synthesis: Replace the table's prose Findings presentation with an accessible infographic-style Results cluster driven by `finding_codes`, remove ownership from per-document reshaping findings and effort, and retain recommendation/proposal workflow semantics outside the read-only results display.

## Evidence Log

| ID | Location | Evidence | Supports |
|---|---|---|---|
| C1 | prototype/copilot-studio-knowledge-compiler/index.html:202 | The read-only discovery panel is the document-assessment surface and renders all inventoried documents in a table. | Scope of the requested Assess-tab change |
| C2 | prototype/copilot-studio-knowledge-compiler/index.html:225 | The final document column is currently labelled Findings. | Presentation surface to rename Results |
| C3 | prototype/copilot-studio-knowledge-compiler/app.js:386 | Each report's imperative `reasons` strings are concatenated into an unstructured text cell. | Root cause of recommendation-like, low-signal presentation |
| C4 | prototype/copilot-studio-knowledge-compiler/app.js:400 | The page already uses metric cards for an estate-level visual summary. | Existing visual language that per-document results can extend |
| C5 | src/shaper/application/assessment.py:114 | Per-document reports expose deterministic `finding_codes`; missing owner is currently included alongside content-quality findings. | Available typed result data and accountability leakage |
| C6 | src/shaper/application/assessment.py:127 | Long paragraphs and cross-policy references are already detected and emitted as result codes. | Requested result examples require no new analyzer |
| C7 | src/shaper/application/assessment.py:138 | `reasons` converts result codes into imperative recommendations, including "Add an accountable owner." | User-reported mismatch |
| C8 | src/shaper/application/assessment.py:470 | Chunking suitability measures paragraph-sized content and long paragraphs use a 150-word threshold. | Existing AI-readiness basis for section-size results |
| C9 | src/shaper/domain/estate.py:314 | `DocumentReadinessReport` already transports both `reasons` and `finding_codes`. | UI can migrate without a schema change |
| C10 | src/shaper/application/orchestration.py:94 | Downstream transformation proposals independently map finding codes to proposed changes. | Results display can change without removing the approval workflow |
| C11 | tests/test_assessment.py:221 | Tests already prove that long paragraphs and policy references are detected together. | Existing regression foundation |

## Findings Mapped to Questions and Evidence

* What should replace Recommendations/Findings? An accessible Results cluster composed of compact visual issue indicators, each with an icon, concise label, and assistive text, driven by `finding_codes` (C2, C3, C5, C9).
* Which requested signals exist? Oversized content (`long_paragraph`) and references to other documents (`cross_policy_reference`) are already detected, as are structure, metadata, freshness, FAQ, and procedure gaps (C5, C6, C8).
* Is backend work required? A contract expansion is not required. Backend behavior should be narrowed to remove `missing_owner` from per-document findings so ownership does not inflate reshaping effort or generate a transformation action (C5, C7, C10).
* What remains distinct? The downstream Recommend stage creates approval-bound transformation proposals; it is not the read-only assessment result display and should remain intact (C10).

## Key Discoveries

* ✅ Evidence-backed finding: the product already has the exact typed signals needed for infographic results; the UI discards their structure by rendering `reasons` as prose (C3, C5, C6, C9).
* ✅ Evidence-backed finding: missing ownership is counted as document reshaping effort and presented as a content recommendation, directly causing the mismatch identified by the caller (C5, C7).
* ✅ Evidence-backed finding: existing metric-card and badge styles provide a repository-consistent base for compact result indicators (C4).

## Alternatives and Decision State

| Alternative | Decision | Rationale |
|---|---|---|
| Rename Findings to Results but keep `reasons` prose | Rejected | Leaves the recommendation semantics, owner prompt, and poor scanability unchanged (C3, C7). |
| Add a new backend result DTO with counts and display labels | Deferred | Typed `finding_codes` already provide a stable presentation input; avoid redundant schema and coupling (C5, C9). |
| Replace the per-document prose with code-driven visual result indicators and remove ownership from reshaping evidence | Selected | Directly addresses the user need with existing evidence and a bounded UI/backend change (C3, C5, C6, C9). |
| Remove the downstream Recommend workflow | Rejected | It serves a separate approval-bound transformation purpose and is outside the read-only assessment display (C10). |

## Open Questions, Risks, and Residual Uncertainty

* Visual indicators must not rely on color or icons alone; each requires visible text and an accessible description.
* The result set may become dense. Use compact wrapping indicators and a clear "No issues detected" state rather than a fixed-width chart.
* Existing reports persisted before the change may still contain `missing_owner`; the renderer should ignore that code defensively so historical data does not reintroduce accountability content.
* `reasons` remains in the report contract for compatibility, but the Assess UI should stop using it.

## Current Decisions

* Treat ownership recommendations as out of scope for Assess results.
* Prefer existing assessment evidence where it accurately represents AI-readiness problems.

## Unresolved Decisions

* Exact colors/icons are an implementation detail, but must follow the existing visual system and accessibility requirements.

## Potential Next Research

* If users later need magnitude (for example, exact long-paragraph counts rather than presence), research a versioned report-detail contract. Current evidence supports presence indicators only.

## Planning Readiness

* Status: Ready.
* Reason: The selected approach is supported by existing report codes, bounded UI surfaces, current style primitives, and tests (C2-C11). No unresolved product decision blocks planning.

## Research Disposition

* Disposition: executed.
* Status: Complete.

## Self-Check

* [x] Research brief and boundaries are complete.
* [x] Wider, deeper, and contrarian waves are complete in order.
* [x] Material findings cite stable evidence IDs.
* [x] Alternatives and risks are recorded.
* [x] Planning readiness is evidence-backed.
