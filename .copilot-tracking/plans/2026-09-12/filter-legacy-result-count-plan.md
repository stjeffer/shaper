<!-- markdownlint-disable-file -->
# RPI Plan: Filter legacy Result count

## Task Metadata

* Task ID: filter-legacy-result-count
* Task slug: filter-legacy-result-count
* Planning status: Ready
* Plan date: 2026-09-12
* Phase details: .copilot-tracking/details/2026-09-12/filter-legacy-result-count-phase-details.md
* Plan critique: .copilot-tracking/reviews/plans/2026-09-12/filter-legacy-result-count-plan-critique.md

## Executive Summary

Make the aggregate Results count use the same presentation classification as document rows, so legacy accountability-only codes remain excluded and unknown future codes remain visible as one unresolved result.

### User Decisions and Requirements Highlights

* Results must be content-focused and must not reintroduce owner/accountability signals.

### What You May Not Know

* The row renderer already behaves correctly; only the aggregate count duplicates raw-code logic.

### Unresolved Decisions or Blockers

* None.

## User Decisions and Requirements

* Fix the review finding selected at the automatic follow-up checkpoint.
* Keep ownership excluded from Results.
* Preserve honest handling of unknown future result codes.

## Goals

* Make row and summary result semantics consistent through one classifier.

## Scope and Non-Goals

### In Scope

* Browser-side result classification, rendering, summary count, and static regression assertion.

### Non-Goals

* Backend schema or analyzer changes.
* New visual design.

## Functional Requirements

* One classifier must return presentable supported results plus at most one unknown fallback.
  * Observable acceptance criteria: `missing_owner` contributes zero; one or more unknown codes contribute one.
* Row rendering and aggregate counting must consume that classifier.
  * Observable acceptance criteria: An accountability-only legacy report shows a clear row and does not increment Results found.

## Non-Functional Requirements

* Classification must remain deterministic and side-effect free.
  * Objective threshold or evaluation condition: Identical code arrays produce identical result arrays.
  * Observable acceptance criteria: Existing static and browser behavior remain unchanged except the corrected count.

## Acceptance Criteria

* `missing_owner` is excluded from row and aggregate results.
* Unknown codes produce one generic result per document in row and aggregate count.
* Existing supported codes retain one result each.
* Existing automated validation passes.

## Implementation Context Record

| Context item | Current artifact or record |
|---|---|
| Plan | .copilot-tracking/plans/2026-09-12/filter-legacy-result-count-plan.md |
| Phase details | .copilot-tracking/details/2026-09-12/filter-legacy-result-count-phase-details.md |
| Latest critique | .copilot-tracking/reviews/plans/2026-09-12/filter-legacy-result-count-plan-critique.md with Pass verdict |
| Relevant research | .copilot-tracking/research/2026-09-12/filter-legacy-result-count-research.md |
| Changes-record role | .copilot-tracking/changes/2026-09-12/filter-legacy-result-count-changes.md |
| Planning execution and readiness | Complete and implementation-ready |
| Continuation context | Automatic RPI parent |

## Sources

* RV-001 in .copilot-tracking/reviews/logs/2026-09-12/assess-results-infographic-review.md.
* Existing `documentResults()` and `renderDiscoverySummary()` implementation.

## Phase Checklist

<!-- rpi:phase id=P01 -->
### [x] P01: Unify Results classification

* Intent: Correct the legacy aggregate count without changing visual or backend behavior.
* Dependencies: None.

<!-- rpi:task id=P01-T01 -->
#### [x] P01-T01: Extract and reuse presentable result classification

* Requirement and evidence: RV-001.
* Expected result: Row and summary derive from the same supported/unknown/accountability rules.
* Detail section: P01-T01 in .copilot-tracking/details/2026-09-12/filter-legacy-result-count-phase-details.md

<!-- rpi:task id=P01-T02 -->
#### [x] P01-T02: Extend static regression coverage and validate

* Requirement and evidence: The current static UI test already owns the Results source contract.
* Expected result: No new test case; extend the existing test and run targeted/full checks.
* Detail section: P01-T02 in .copilot-tracking/details/2026-09-12/filter-legacy-result-count-phase-details.md

## Dependencies

* Existing browser result presentation metadata.

## Critique Disposition

| Critique run and finding | Disposition | Plan response or residual risk |
|---|---|---|
| Complete critique | Resolved | Pass with no findings. |

## Follow-Up Items

* None.

## Handoff

* Implementation artifact: .copilot-tracking/changes/2026-09-12/filter-legacy-result-count-changes.md
* Ready phase or task: Review
* Remaining provisional question or blocker: None
