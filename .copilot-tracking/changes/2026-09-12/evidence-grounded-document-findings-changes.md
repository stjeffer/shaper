<!-- markdownlint-disable-file -->
# RPI Changes: Evidence-grounded document findings

## Metadata

* Task ID: evidence-grounded-document-findings
* Plan: .copilot-tracking/plans/2026-09-12/evidence-grounded-document-findings-plan.md
* Details: .copilot-tracking/details/2026-09-12/evidence-grounded-document-findings-phase-details.md
* Implementation date: 2026-09-12

## Execution Status

* Status: Complete
* Declared scope: Full plan
* Completed markers: P01 through P04
* Remaining markers: None

## Active Work

### Commit, deploy, and verify

* Active marker: P04-T03
* Result: Committed the reviewed implementation, deployed immutable image
  `shaper:20260912-7bbaba0`, and verified the live workflow.
* Current blockers: None

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

### Resolve review findings

* Moved the document viewer function to module scope so the delegated click
  handler can invoke it.
* Extended existing tests with exact detector-catalog equality plus missing,
  cross-estate, deleted, and stale-version retrieval assertions.
* Reused the existing Result-card visual system for high-severity findings and
  changed normalized source content from a monospace code font to the interface
  font.

### Align Assess with Fluent 2

* Replaced the dense finding-card wall with compact, nested disclosures and
  calm text-based severity labels.
* Added labelled readiness progress indicators, restrained summary metrics, and
  an explanatory review note.
* Converted document rows into responsive cards at narrow widths while
  retaining the semantic table structure.
* Removed alarm-style exclamation icons from finding summaries and rows.

### Deploy and verify

* Committed the feature as `7bbaba0`.
* Built image `crshaperdevi5e45vhjjbud6.azurecr.io/shaper:20260912-7bbaba0`
  with digest
  `sha256:28557e9227e9a3734c49da9cc516fdfe8e8361e092afd0a4eacac4bd69da2a33`.
* Deployed healthy revision `ca-shaper-dev--r7bbaba0` with 100 percent traffic.
* Verified liveness, readiness, `/concept/`, dialog loading and closure, keyboard
  focus return, evidence semantics, and a 375-pixel viewport.
* Deployed the final visual alignment as image
  `crshaperdevi5e45vhjjbud6.azurecr.io/shaper:20260912-0057364`, digest
  `sha256:fd4f476fc0cd5007dddab30d8aaee9bc2d0865ceb5ff161095b34c31b2ce9dea`,
  on healthy revision `ca-shaper-dev--r0057364` with 100 percent traffic.
* Deployed the Fluent redesign as image
  `crshaperdevi5e45vhjjbud6.azurecr.io/shaper:20260912-d67d2f6`, digest
  `sha256:ec32cf25333cd7c32bbf8e5ddc7569695baf7108347a3fba0f553bffbac80ced`,
  on healthy revision `ca-shaper-dev--rd67d2f6` with 100 percent traffic.

## Validation

* `PYTHONPATH=src uv run pytest`: passed, 175 tests
* `uv run ruff check .`: passed
* `uv run ruff format --check .`: passed
* `PYTHONPATH=src uv run mypy`: passed, 84 source files
* `PYTHONPATH=src uv run shaper-schema --check`: passed
* `node --check prototype/copilot-studio-knowledge-compiler/app.js`: passed
* `git diff --check`: passed
* Rendered browser workflow: passed
* Keyboard disclosure and nested evidence interaction: passed
* 320-pixel reflow, text spacing, focus visibility, and forced colors: passed
* Azure liveness and readiness: passed

## Remaining Work

None.

## Review Readiness

Review executed once. Findings RV-001 and RV-002 were implemented and validated
as later work; a second Review was not required.
