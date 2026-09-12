<!-- markdownlint-disable-file -->
# RPI Changes: Knowledge Estate Workflow Redesign

## Metadata

* Task ID: knowledge-estate-workflow-redesign
* Related plan: .copilot-tracking/plans/2026-09-10/knowledge-estate-workflow-redesign-plan.md
* Phase details: .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md
* Implementation date: 2026-09-10

## Execution Status

* Status: Partial
* Declared invocation scope: Full plan
* Completed scope markers: P01-P06, P01-T01 through P06-T04, and P07-T02
* All remaining active-plan markers: P07, P07-T01, and P07-T03
* Status basis: The live estate workflow and signed-out authentication shell are deployed; production identity and authenticated browser evidence remain active-plan work.

## Execution Summary

Implementation is active. The approved outcome preserves the five-agent architecture and substantially replaces the demo-first UI with a durable estate workflow.

## Active Work

### Align the Hosted Workspace with Copilot Studio

* Active phase or task: P06-T03 remediation within the full-plan implementation
* Intended result: Match the supplied Copilot Studio shell and modal references with an icon rail, rounded application frame, task-named tabs, list/table surfaces, large-radius dialog, consistent Fluent inputs, non-obscuring busy states, and durable estate-stage deep links.
* Current blockers: None

### Deploy and Prove the Azure Workflow

* Active phase or task: P07-T01
* Intended result: Reconcile production PostgreSQL identity with the plan's passwordless target and complete the authenticated estate-workspace browser journey.

### Reconcile Durable APIs, Live Product Experience, and Deployment Proof

* Active phase or task: P06-T01 through P07-T03
* Intended result: Verify the landed persistence, protected resources, browser identity, live UI, infrastructure, documentation, and deployment evidence against every remaining plan marker.
* Current blockers: None

## Completed Work

### Define the Knowledge Estate Domain

* Related phase or task: P01-T01
* Files: src/shaper/domain/estate.py, src/shaper/domain/__init__.py, tests/test_estate_domain.py
* What changed and why: Established version-pinned records and fail-closed naming, lifecycle, estimate, and decision invariants.
* Completion evidence: Seven domain tests passed.
* Validation: Passed

### Define Repository and Orchestration Ports

* Related phase or task: P01-T02
* Files: src/shaper/application/estates.py, src/shaper/infrastructure/sqlite.py, tests/test_estates.py
* What changed and why: Added optimistic lifecycle and complete estate-workflow persistence ports plus a SQLite local adapter while retaining the existing stateless five-agent orchestration.
* Completion evidence: Estate service, architecture, and orchestration regression tests passed.
* Validation: Passed

### Register Sources and Build the Document Inventory

* Related phase or task: P02, P02-T01, P02-T02, P02-T03
* Files: src/shaper/application/estates.py, src/shaper/application/ports.py, src/shaper/infrastructure/archive.py, src/shaper/infrastructure/uploads.py, src/shaper/infrastructure/sharepoint.py, src/shaper/infrastructure/sqlite.py, tests/test_archive.py, tests/test_estates.py
* What changed and why: Added typed source registration, atomic multi-file inventory, bounded ZIP expansion, source withdrawal, Graph content transfer, durable delta checkpoints, and explicit connector diagnostics.
* Completion evidence: Mixed sources produce independent records; accepted ZIP entries become inventory rows; malicious ZIP cases fail closed; Graph success and missing-consent states persist truthfully.
* Validation: 40 focused tests passed; changed Python passed Ruff and strict mypy.

### Run Multi-Agent Discovery

* Related phase or task: P03, P03-T01, P03-T02
* Files: src/shaper/domain/assessment.py, src/shaper/domain/estate.py, src/shaper/application/assessment.py, src/shaper/application/estates.py, src/shaper/infrastructure/sqlite.py, tests/test_assessment.py, tests/test_estates.py
* What changed and why: Added document-scoped readiness and effort scoring, long-paragraph and cross-policy evidence, durable leased discovery runs, partial failure accounting, lease recovery, and persisted outputs from all five specialist agents.
* Completion evidence: Every current fixture document produces a version-pinned report, the orchestrated result retains all five roles, and discovery has no model dependency.
* Validation: 31 focused tests passed; changed Python passed Ruff and strict mypy.

### Recommend, Estimate, and Decide

* Related phase or task: P04, P04-T01, P04-T02, P04-T03
* Files: src/shaper/domain/estate.py, src/shaper/application/orchestration.py, src/shaper/application/estates.py, src/shaper/application/token_estimation.py, src/shaper/application/decisions.py, tests/test_token_estimation.py, tests/test_decisions.py, tests/test_estates.py
* What changed and why: Added selection validation, deterministic Transformation Agent proposals, immutable range estimates and hard caps, and append-only exact-version decisions distinct from output review.
* Completion evidence: Selected proposal count matches selected documents; declines and stale evidence cannot authorize execution.
* Validation: 28 focused tests passed; changed Python passed Ruff and strict mypy.

### Transform Approved Content and Publish Artifacts

* Related phase or task: P05, P05-T01, P05-T02, P05-T03
* Files: src/shaper/domain/estate.py, src/shaper/application/shaping.py, src/shaper/application/artifacts.py, src/shaper/application/estates.py, src/shaper/infrastructure/sqlite.py, tests/test_artifacts.py, tests/test_shaping.py
* What changed and why: Enforced exact approval at the model boundary, split actual input/output accounting, closed provider-response budget overshoot, rendered escaped semantic HTML, and retained separate output review before artifact publication.
* Completion evidence: Declined proposals make zero model calls and create no artifact; an approved proposal creates usage and an in-review artifact that becomes retrievable only after separate review.
* Validation: 18 focused transformation and publication tests passed; changed Python passed Ruff and strict mypy.

### Expose the Live Estate Workflow and Optional Evaluations

* Related phase or task: P06, P06-T01 through P06-T04, and P07-T02
* Files: src/shaper/domain/estate.py, src/shaper/application/estates.py, src/shaper/application/artifacts.py, src/shaper/interfaces/http.py, src/shaper/infrastructure/postgres.py, prototype/copilot-studio-knowledge-compiler/, README.md, docs/
* What changed and why: Added PostgreSQL-backed estate APIs, interactive Entra browser identity, the live estate workspace, and an estate-level opt-in that generates versioned citation-coverage, structure, and validation evaluations for reshaped artifacts.
* Completion evidence: The checkbox is present at estate creation and transformation, the setting persists through optimistic estate updates, disabled estates create no evaluation, enabled estates expose evaluations in artifact records and through the evaluation API, and superseded PostgreSQL transactions no longer block revision startup.
* Validation: 148 tests passed at 78.52% coverage; Ruff, formatting, strict mypy, schema, JavaScript, shell, Bicep, and diff checks passed.

### Deploy the Evaluation Option, Authentication Flow, and Redesigned Workspace

* Related phase or task: P07-T03 deployment evidence
* Deployment: Revision `ca-shaper-dev--0000034`, image digest `sha256:fff80671139a4cce3bd3db32fc9f36121b65ab5360327938a76f3607932a6abf`
* Evidence: Revision is Healthy, RunningAtMaxScale, and receives 100% traffic; `/health/ready` reports every dependency ready. Anonymous `/concept/` returns the data-free shell, `/v1/session` remains protected, and a browser reaches the Microsoft Entra sign-in page through the explicit UI bootstrap.
* Authentication correction: The Entra application now enables ID-token issuance because Container Apps authentication requests the hybrid `code id_token` response type. Deployment automation preserves this setting, preventing the post-sign-in 401 caused by the incomplete application registration.
* Redirect-loop correction: The UI no longer probes the unavailable token-store-backed `/.auth/me` endpoint. It checks `/v1/session`, prevents `fetch` from following browser-only authentication redirects across origins, and converts the resulting 401 or opaque redirect into one top-level Entra navigation.
* Workspace redesign: Matched the user-supplied Copilot Studio screenshots with an 88 px icon rail, rounded application frame, Segoe web type ramp, purple primary actions, segmented task tabs, rounded list/table containers, light-gray work cards, and a large 32 px-radius modal with spacious header, 48 px inputs, structured options, and separated footer actions. The estate flow now uses task names (Sources, Assess, Approve, Outputs), direct estate-stage URLs survive initialization, and busy feedback no longer fades the full workspace. Shaper retains its own product identity rather than copying protected Microsoft artwork. The design remains responsive and preserves named controls, autofocus, landmark structure, visible focus, reduced motion, loading, access, empty, error, and approval states.
* Remaining acceptance boundary: PostgreSQL currently uses a protected password secret rather than the plan's passwordless application identity, and the post-authentication estate workspace requires user validation.

## Implementation-Time Plan and Detail Updates

### Copilot Studio Appearance Requirement

* Affected plan area or markers: User Decisions and Requirements, P06-T03, P07-T03
* What changed: The hosted interface now explicitly targets a similar information hierarchy and interaction vocabulary to Microsoft Copilot Studio rather than only applying general Fluent colors and type.
* Why: The user confirmed that general Microsoft styling is insufficient and the product must look the same as, or similar to, Copilot Studio.
* Triggering evidence: User feedback and supplied live-workspace screenshot on 2026-09-11
* User answer or decision: Use a Copilot Studio-like application shell and appearance.
* Reconciliation performed: Updated the current requirement, P06-T03 expected result and detail boundary, and browser validation expectation while preserving the approved workflow and no-new-framework boundary.
* Planning and critique state: Implementation-ready; the existing critique remains historical and is not repeated.

### Copilot Studio Modal and Input Reference

* Affected plan area or markers: P06-T03 remediation
* What changed: The user added a fifth visual reference showing Copilot Studio's large centered modal, rounded container, muted backdrop, spacious header and body, large-radius input fields, close action, and separated footer.
* Why: The deployed create-estate form still used the earlier compact generic dialog treatment.
* Triggering evidence: `docs/Screenshots/Screenshot 2026-09-11 at 14.25.23.png`
* User answer or decision: Update the modal and input form to match the supplied screenshot.
* Reconciliation performed: Scoped the correction to the existing create-estate dialog without changing its domain fields, validation, or submit behavior.
* Planning and critique state: Implementation-ready; no new planning decision or critique is required.

### Copilot Studio Rail Action and Publish-Button Reference

* Affected plan area or markers: P06-T03 remediation
* What changed: The user identified the inactive rail control, removed the need for portfolio search, and supplied a close crop of Copilot Studio's Publish button.
* Why: A current-page navigation link appears inert on the estate list, the small estate collection does not need search, and the solid-purple New estate action does not match the reference's pale lavender pill treatment.
* Triggering evidence: User feedback and `docs/Screenshots/Screenshot 2026-09-11 at 14.40.19.png`
* User answer or decision: Make the rail action functional, remove search, and copy the supplied Publish-button branding for New estate.
* Reconciliation performed: Scoped the correction to the portfolio rail and creation entry point without changing estate creation behavior. A subsequent user adjustment also reduced the estate-list header, row, icon, and column dimensions.
* Planning and critique state: Implementation-ready; no new planning decision or critique is required.

### Compact Estate Source Workspace

* Affected plan area or markers: P06-T03 remediation
* What changed: The user supplied the rendered estate Sources screen and requested less vertical scrolling plus non-boilerplate dropdown and upload controls.
* Why: Large top spacing, stage spacing, card padding, fields, and upload target push Registered sources below the fold; the native select chrome and generic drop target do not match the supplied Copilot Studio references.
* Triggering evidence: User feedback and `docs/Screenshots/Screenshot 2026-09-11 at 14.54.04.png`
* User answer or decision: Compact the estate workspace and restyle the select and upload controls.
* Reconciliation performed: Scoped the change to density and control presentation; source kinds, accepted file types, validation, and submission behavior remain unchanged.
* Planning and critique state: Implementation-ready; no new planning decision or critique is required.
* Implementation: Reduced workspace, estate-heading, workflow, panel, card, field, and section spacing; added a custom select chevron; and replaced the generic upload glyph with a compact Shaper-branded upload treatment.
* Responsive evidence: At 1600 by 900 pixels, Registered sources begins at 657 pixels and the complete source-entry panel is visible; at 390 pixels, the two cards reflow to one column with body width equal to viewport width.
* Validation: Seven targeted architecture tests passed; JavaScript syntax, state JSON, and `git diff --check` passed; browser inspection confirmed an accessible named combobox and file input.
* Deployment: Revision `ca-shaper-dev--0000035`, image digest `sha256:b80efb41555d59d1e063ac149fa42412086776b4f59fd650617913ba094f37a4`.
* Live evidence: Revision is Healthy, RunningAtMaxScale, and receives 100% traffic; readiness dependencies report ready, live HTML references `20260911-ui9`, and anonymous direct-route startup reaches one Entra sign-in flow.

### UI Scope Confirmation

* Affected plan area or markers: User Decisions and Requirements, P06-T03, P06-T04
* What changed: No plan change was required; the approved plan already treats the UI as a substantial live workflow redesign.
* Why: The user explicitly emphasized that the UI needs major change when authorizing implementation.
* Triggering evidence: User implementation invocation on 2026-09-10
* User answer or decision: Build the full plan and substantially change the UI.
* Reconciliation performed: Existing goals, FR-15, FR-16, P06-T03, P06-T04, and AC-14-AC-15 already cover the direction.
* Planning and critique state: Implementation-ready; PC-001-PC-015 remain resolved.

## Validation Record

| Check | Scope | Status | Evidence or reason |
|---|---|---|---|
| Pre-implementation plan and state | Full plan | Passed | Plan is Ready, 27 plan/detail markers align, and all critique findings are resolved. |
| Estate domain tests | P01-T01 | Passed | 7 tests passed. |
| Ruff | P01-T01 | Passed | Changed domain and test files pass. |
| Strict mypy | P01-T01 | Passed | Changed domain and test files pass. |
| Estate services and orchestration | P01-T02 | Passed | 21 focused tests passed across estate, orchestration, and architecture behavior. |
| Source inventory and ZIP safety | P02 | Passed | 40 focused tests passed. |
| Ruff and strict mypy | P01-P02 | Passed | Changed Python and focused tests pass. |
| Deterministic discovery | P03 | Passed | 31 focused tests passed; all five agent roles persisted. |
| Ruff and strict mypy | P03 | Passed | Changed discovery files pass. |
| Recommendation and decisions | P04 | Passed | 28 focused tests passed. |
| Approved transformation and artifacts | P05 | Passed | 18 focused tests passed. |
| Ruff and strict mypy | P04-P05 | Passed | Changed recommendation and transformation files pass. |
| Full pytest and coverage | P01-P07 | Passed | 148 tests passed; total coverage 78.52% exceeds 75%. |
| Static and build validation | P06-P07 | Passed | Ruff, formatting, strict mypy, schema, JavaScript syntax, shell syntax, Bicep build, and diff checks passed. |
| Azure revision | P07-T03 | Partial | Revision 0000035 is healthy with 100% traffic and RunningAtMaxScale. The compact screenshot-aligned Sources workspace, branded select/upload controls, shell and modal, functional rail creation action, Publish-branded New estate action, compact estate rows, direct-stage routing, single session probe, protected API boundary, Entra redirect, active client credential, callback URI, and ID-token issuance pass; final product-owner visual validation and the complete post-authentication estate journey remain open. |

## Pre-Review Reconciliation

* Plan markers and phase details: P01-P06 and P07-T02 are current; P07-T01 and P07-T03 remain open.
* Completed-work evidence and handoff prose: Current through the optional evaluation and signed-out authentication-shell deployment.
* Validation, blockers, remaining work, and follow-up items: Local validation, Azure health, public-shell delivery, API protection, and the Entra redirect pass; passwordless PostgreSQL identity and post-authentication hosted-browser evidence remain.
* Review readiness: Not ready; implementation is active.

## Blockers

* None

## Remaining Work

* P07, P07-T01, and P07-T03

## Follow-Up Items

* Canonical plan list: .copilot-tracking/plans/2026-09-10/knowledge-estate-workflow-redesign-plan.md, `## Follow-Up Items`
* Existing connector, calibration, resilience, and browser-regression follow-ups remain outside this implementation.

## Return-to-Caller State

* Implementation execution status: Partial
* Declared scope and markers: Full plan; no completed markers yet
* Validation coverage: Pre-implementation artifact validation only
* Blockers: None
* Current plan and detail updates: UI emphasis recorded without changing scope
* Planning and critique state: Ready; PC-001-PC-015 resolved
* Follow-up items: Unchanged from plan
* Review readiness or no-handoff reason: Not ready; implementation is active
* Continuation owner: User for standalone RPI
