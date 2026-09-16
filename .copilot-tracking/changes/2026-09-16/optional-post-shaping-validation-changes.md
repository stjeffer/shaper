<!-- markdownlint-disable-file -->
# RPI Changes: Optional post-shaping validation

## Metadata

* Task ID: optional-post-shaping-validation
* Related plan: .copilot-tracking/plans/2026-09-16/optional-post-shaping-validation-plan.md
* Phase details: .copilot-tracking/details/2026-09-16/optional-post-shaping-validation-phase-details.md
* Implementation date: 2026-09-16

## Execution Status

* Status: Complete
* Declared invocation scope: Full plan
* Completed scope markers: P01, P01-T01, P01-T02, P02, P02-T01, P02-T02, P03-T01, P03-T02
* All remaining active-plan markers: None
* Status basis: Implementation, documentation, validation, and production release are complete.

## Execution Summary

The transformation API now defaults to advisory preservation validation. The
run-level browser option can request strict repair behavior, while integrity
failures remain non-bypassable. Retained findings are stored on artifacts, shown
to reviewers, and acknowledged during publication approval.

## Completed Work

### Separated generation integrity from preservation review

* Related phase or task: P01-T01
* Files: src/shaper/application/validation.py, src/shaper/application/shaping.py
* What changed and why: Added an explicit integrity allowlist and advisory conversion so preservation heuristics cannot destroy an otherwise integrity-valid candidate.
* Completion evidence: Shaping regressions cover bypassed preservation findings and retained source-version failures.
* Validation: Targeted tests passed.

### Wired the real run-level control

* Related phase or task: P01-T02
* Files: src/shaper/interfaces/http.py, src/shaper/application/artifacts.py, prototype/copilot-studio-knowledge-compiler/app.js, prototype/copilot-studio-knowledge-compiler/index.html
* What changed and why: The checkbox now sends transformation-run authority and no longer updates estate evaluation settings.
* Completion evidence: Both transformation endpoints use the new request contract.
* Validation: Python interface tests and JavaScript syntax checks passed.

### Persisted findings and governed approval

* Related phase or task: P02-T01, P02-T02
* Files: src/shaper/domain/estate.py, src/shaper/application/artifacts.py, prototype/copilot-studio-knowledge-compiler/app.js
* What changed and why: Generated artifacts carry review findings, the browser presents them without score cards, and approval must acknowledge the exact rule set.
* Completion evidence: Artifact regression creates a reviewable artifact from a lossy candidate when preservation repair is disabled.
* Validation: Targeted artifact tests passed.

### Removed artifact scores and aligned documentation

* Related phase or task: P03-T02
* Files: prototype/copilot-studio-knowledge-compiler/app.js, src/shaper/application/artifacts.py, src/shaper/interfaces/http.py, docs/architecture.md, docs/features.md, docs/deployment.md, docs/operations.md
* What changed and why: Removed score cards, score generation, and the score endpoint; documented findings-led review, optional repair, integrity controls, and publication acknowledgment.
* Completion evidence: Artifact payloads omit legacy evaluations and all affected documents describe the same lifecycle.
* Validation: Full repository gates passed.

### Released the advisory-first workflow

* Related phase or task: P03-T03
* Files: Production image and Azure Container Apps revision
* What changed and why: Published the immutable application image and routed production traffic to the matching healthy revision.
* Completion evidence: Revision ca-shaper-dev--4626fa5 ran one healthy replica at 100 percent traffic using digest sha256:b89944c227659a1941bcca863aa27d821effbb2feac2709f831e0c943da93725.
* Validation: Live and ready endpoints passed; readiness confirmed state, estate, malware-scanner, and compile-worker dependencies.

## Implementation-Time Plan and Detail Updates

### Recorded the approved advisory-first lifecycle

* Affected plan area or markers: P01, P02, P03
* What changed: Created the current-state plan and phase details from the completed research decision.
* Why: Implementation began from a research artifact before marker-based plan files existed.
* Triggering evidence: The browser checkbox controlled estate evaluations while shaping validation remained unconditional.
* User answer or decision: Implement autonomously and do not finish until validated and deployed.
* Reconciliation performed: Requirements, phases, task markers, dependencies, and release work are current.
* Planning and critique state: Approved intent is current; no new material decision is needed.

## Validation Record

| Check | Scope | Status | Evidence or reason |
|---|---|---|---|
| Pytest | Transformation, shaping, and HTTP tests | Passed | Targeted suite passed before final documentation batch. |
| Ruff | Changed Python files | Passed | Initial unused import corrected; rerun pending final batch. |
| JavaScript syntax | Browser application | Passed | node --check completed successfully. |
| Full Python suite | Repository | Passed | 321 tests passed with 81.88% coverage. |
| Ruff format and lint | Repository | Passed | 86 files formatted; all checks passed. |
| Strict mypy | Repository | Passed | No issues in 86 source files. |
| Schema drift | Domain contracts | Passed | shaper-schema check passed. |
| Node tests and syntax | Browser application | Passed | Four tests and JavaScript syntax passed. |
| Shell and whitespace | Deployment and repository | Passed | bash -n and git diff --check passed. |

## Pre-Review Reconciliation

* Plan markers and phase details: Complete.
* Completed-work evidence and handoff prose: Current.
* Validation, blockers, remaining work, and follow-up items: Current; no remaining work.
* Review readiness: Ready.

## Blockers

* None.

## Remaining Work

* None.

## Follow-Up Items

* Canonical plan list: .copilot-tracking/plans/2026-09-16/optional-post-shaping-validation-plan.md, `## Follow-Up Items`
* None.

## Return-to-Caller State

* Implementation execution status: Complete
* Declared scope and markers: Full plan; all P01, P02, and P03 markers complete.
* Validation coverage: All repository gates passed.
* Blockers: None.
* Current plan and detail updates: Advisory-first lifecycle recorded.
* Planning and critique state: Ready to continue implementation.
* Follow-up items: None.
* Review readiness or no-handoff reason: Ready for review.
* Continuation owner: Current implementation agent.
