<!-- markdownlint-disable-file -->
# Task Research: filter-legacy-result-count

| Field | Value |
|---|---|
| Date | 2026-09-12 |
| Researcher / agent | RPI Agent |
| Status | Complete |
| Artifact path | .copilot-tracking/research/2026-09-12/filter-legacy-result-count-research.md |

## Research Brief

* What to research: Whether existing evidence is sufficient to resolve RV-001 without new investigation.
* Why it matters: Legacy accountability-only reports can increment the aggregate Results count while their row correctly shows no content issues.
* Scope: Result classification and summary counting in the browser prototype.
* Non-goals: New result types, report schema changes, or redesign.
* Output mode: convergence.

## Research Disposition

* Disposition: satisfied-and-skipped.
* Evidence: RV-001 identifies the exact divergent paths in `documentResults()` and `renderDiscoverySummary()`, and the existing UI contract test owns static regression coverage.
* Planning Readiness: Ready.

## Current Decisions

* Reuse one content-focused result classifier for row rendering and aggregate counting.
* Continue ignoring `missing_owner`; count unknown future codes as one displayable unresolved result, matching the row.

## Risks and Residual Uncertainty

* None material. The change is local and deterministic.

## Self-Check

* [x] Existing evidence directly identifies the defect and correction.
* [x] No new research cycle is needed.
* [x] Planning readiness is supported.
