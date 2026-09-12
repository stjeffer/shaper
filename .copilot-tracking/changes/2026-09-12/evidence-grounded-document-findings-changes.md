<!-- markdownlint-disable-file -->
# RPI Changes: Evidence-grounded document findings

## Metadata

* Task ID: evidence-grounded-document-findings
* Plan: .copilot-tracking/plans/2026-09-12/evidence-grounded-document-findings-plan.md
* Details: .copilot-tracking/details/2026-09-12/evidence-grounded-document-findings-phase-details.md
* Implementation date: 2026-09-12

## Execution Status

* Status: Implementation complete, pending review and deployment
* Declared scope: Full plan
* Completed markers: P01 through P03, P04-T01, P04-T02
* Remaining markers: P04-T03

## Active Work

### Commit, deploy, and verify

* Active marker: P04-T03
* Intended result: Commit the reviewed implementation, deploy an immutable image,
  and verify the healthy live workflow.
* Current blockers: Post-implementation review has not run.

## Completed Work

### Preserve and model evidence

* Added backward-compatible finding and evidence contracts.
* Preserved real heading context in normalized content without introducing
  synthetic parser locations into transformation input.

### Implement the complete detector catalog

* Added the stable 22-code detector catalog across structural, ambiguity,
  contradiction, incompleteness, provenance, authority, formatting, and
  retrieval risks.
* Refactored discovery into profile collection followed by peer-aware assessment.
* Added proposed-change mappings while retaining legacy report fields.

### Expose evidence to content owners

* Added source-version-pinned normalized-content retrieval.
* Added expandable quotes, locations, explanations, review-required labels,
  completed-check counts, and the full-document dialog.
* Preserved document selection and human approval boundaries.

### Validate and document

* Added one parameterized detector test covering all 22 codes.
* Extended the estate workflow test for structured evidence, heading-preserving
  content retrieval, and stale-version rejection.
* Extended the static UI contract.
* Updated the feature guide.

## Validation

* `PYTHONPATH=src uv run pytest`: passed, 175 tests
* `uv run ruff check .`: passed
* `uv run ruff format --check .`: passed
* `PYTHONPATH=src uv run mypy`: passed, 84 source files
* `PYTHONPATH=src uv run shaper-schema --check`: passed
* `node --check prototype/copilot-studio-knowledge-compiler/app.js`: passed
* `git diff --check`: passed

## Remaining Work

* Complete post-implementation review
* Commit and deploy the reviewed implementation
* Verify the Azure revision and live workflow

## Review Readiness

Ready for the single post-implementation review.
