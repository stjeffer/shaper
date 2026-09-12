<!-- markdownlint-disable-file -->
# RPI Changes: Filter legacy Result count

## Metadata

* Task ID: filter-legacy-result-count
* Related plan: .copilot-tracking/plans/2026-09-12/filter-legacy-result-count-plan.md
* Phase details: .copilot-tracking/details/2026-09-12/filter-legacy-result-count-phase-details.md
* Implementation date: 2026-09-12

## Execution Status

* Status: Complete
* Declared invocation scope: Full plan
* Completed scope markers: P01, P01-T01, P01-T02
* All remaining active-plan markers: None
* Status basis: Shared classification, regression coverage, automated validation, and rendered count verification are complete.

## Execution Summary

Row rendering and aggregate counting now share one pure classifier. Accountability-only legacy codes contribute zero, supported codes count individually, and any number of unknown codes contribute one generic result per document.

## Completed Work

### Shared result classification

* Related phase or task: P01-T01.
* Files: prototype/copilot-studio-knowledge-compiler/app.js.
* What changed and why: Extracted `classifyResults()` and reused it for row rendering and aggregate counting, removing duplicated raw-code semantics.
* Completion evidence: Rendered fixture with three supported codes, one empty report, one owner-only legacy report, and two unknown codes produced aggregate count 4 with row counts 3/1/1/1.
* Validation: Passed automated and browser checks.

### Existing-test regression lock

* Related phase or task: P01-T02.
* Files: tests/test_architecture.py.
* What changed and why: Extended the existing static Results contract test to require aggregate use of `classifyResults()`.
* Completion evidence: Full test suite passes without adding a test case.
* Validation: Passed.

## Implementation-Time Plan and Detail Updates

* None.

## Validation Record

| Check | Scope | Status | Evidence or reason |
|---|---|---|---|
| Full pytest | Entire repository | Passed | 150 tests passed; five pre-existing SWIG deprecation warnings. |
| Ruff and formatting | Entire repository | Passed | All checks passed; 83 files formatted. |
| mypy | Source and tests | Passed | No issues in 83 source files. |
| JavaScript and diff | Changed browser code and working diff | Passed | `node --check` and `git diff --check` passed. |
| Browser fixture | Legacy and unknown aggregate semantics | Passed | Results found = 4 for 3 supported + 0 empty + 0 owner-only + 1 unknown fallback. |

## Pre-Review Reconciliation

* Plan markers and phase details: Complete and current.
* Completed-work evidence and handoff prose: Current.
* Validation, blockers, remaining work, and follow-up items: Passed, none, none, and none.
* Review readiness: Ready.

## Blockers

* None.

## Remaining Work

* None.

## Follow-Up Items

* Canonical plan list: .copilot-tracking/plans/2026-09-12/filter-legacy-result-count-plan.md, `## Follow-Up Items`
* None.

## Return-to-Caller State

* Implementation execution status: Complete
* Declared scope and markers: Full plan; P01, P01-T01, and P01-T02 complete.
* Validation coverage: Full automated checks and rendered aggregate fixture passed.
* Blockers: None.
* Current plan and detail updates: None.
* Planning and critique state: Ready; critique passed.
* Follow-up items: None.
* Review readiness or no-handoff reason: Ready for Review.
* Continuation owner: Confirmed automatic RPI Agent parent.
