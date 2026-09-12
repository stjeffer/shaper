<!-- markdownlint-disable-file -->
# RPI Plan: Evidence-grounded document findings

## Task Metadata

* Task ID: evidence-grounded-document-findings
* Mode: Automatic
* Status: Complete
* Research: .copilot-tracking/research/2026-09-12/evidence-grounded-document-findings-research.md
* Details: .copilot-tracking/details/2026-09-12/evidence-grounded-document-findings-phase-details.md
* Critique: .copilot-tracking/reviews/plans/2026-09-12/evidence-grounded-document-findings-plan-critique.md
* Changes: .copilot-tracking/changes/2026-09-12/evidence-grounded-document-findings-changes.md

## Executive Summary

Replace code-only document reports with evidence-grounded, reviewable findings.
Every requested suitability check will run for each document, findings will quote
the triggering source text and location, and content owners can open the full
normalized document before selecting it for recommendations and approval.
Heuristic semantic findings remain explicitly review-required.

## User Decisions and Requirements

* Assess newly uploaded documents for suitability as agent-grounding sources.
* Check every supplied structural, ambiguity, contradiction, incompleteness,
  provenance, authority, formatting, and retrieval-unfriendly condition.
* Show the actual document content associated with each problem.
* Let content owners review findings and approve proposed changes.
* Avoid low-score reports that provide only generic reasons and no findings.

## Goals

* Make assessment evidence specific, inspectable, and traceable to source text.
* Cover the full caller-supplied issue taxonomy.
* Preserve the existing recommendation and human approval workflow.
* Explain fast deterministic execution truthfully.

## Scope and Non-Goals

In scope:

* Additive report and evidence models
* Structural-context preservation for new uploads
* Per-document and peer-aware candidate detectors
* Authenticated normalized-content retrieval
* Evidence-rich Assess UI and full-document dialog
* Recommendation mappings, regression tests, documentation, and Azure deployment

Out of scope:

* Autonomous legal or policy conclusions
* A general-purpose semantic contradiction model
* Artificial delays or progress animation unrelated to actual work
* Reprocessing historical document versions without a new discovery run

## Functional Requirements

* FR01: Each report records the complete check catalog that ran.
* FR02: Each detected issue records a code, label, explanation, review-required
  state, and bounded evidence excerpts with locations.
* FR03: The detector catalog covers every issue named by the caller.
* FR04: Cross-document checks receive peer profiles and can identify unresolved
  references, conflicting numbers, and noncanonical repeated content.
* FR05: Legacy `finding_codes` and `reasons` remain populated.
* FR06: Authorized users can retrieve the exact normalized content for a current
  document version.
* FR07: The Assess UI displays evidence inline and opens full content on demand.
* FR08: Selected documents continue into recommendation, decision, and
  transformation without bypassing human approval.
* FR09: The stable detector catalog contains:
  `external_dependency`, `circular_reference`,
  `missing_referenced_content`, `version_ambiguity`, `orphaned_amendment`,
  `vague_quantifier`, `discretion_clause`, `undefined_term`,
  `unclear_responsibility`, `conflicting_numeric_value`,
  `conflicting_authority`, `terminology_drift`, `missing_definitions`,
  `missing_enumeration`, `dangling_program`, `unclear_source_of_truth`,
  `undocumented_verbal_policy`, `restricted_companion`,
  `inconsistent_heading_hierarchy`, `inaccessible_embedded_content`,
  `repeated_variation`, and `noncanonical_duplicate`.

## Non-Functional Requirements

* NFR01: Findings use bounded deterministic work over the existing 100,000
  character input limit.
* NFR02: Heuristic findings use candidate language and never claim certainty.
* NFR03: Full content is not duplicated into report records or fetched until
  requested.
* NFR04: Existing persisted reports remain readable through additive defaults.
* NFR05: Evidence controls and dialogs are keyboard and screen-reader usable.
* NFR06: No broad exception handling or silent fallback is introduced.

## Acceptance Criteria

* AC01: A representative document triggers all supplied issue categories with
  quoted evidence or an explicit document-level absence location.
* AC02: Findings include stable normalized line or section locations.
* AC03: A low score cannot show an empty Results list when supported report
  findings exist.
* AC04: The UI shows the number of checks completed, finding evidence, and a
  full-content viewer.
* AC05: Unknown legacy codes remain visible through the generic compatibility
  result.
* AC06: The authorized content endpoint rejects cross-estate and missing
  documents and source-version mismatches.
* AC07: Existing approval and transformation tests remain green.
* AC08: Full tests, Ruff, formatting, mypy, schema, JavaScript, browser, and Azure
  health validation pass.

## Phase Checklist

<!-- P01 -->
### [x] P01: Preserve and model evidence

<!-- P01-T01 -->
#### [x] P01-T01: Add structured finding and evidence contracts

<!-- P01-T02 -->
#### [x] P01-T02: Preserve heading and table context for new uploads

Preserve real heading text in normalized content. Do not inject synthetic page,
table, row, or block labels into text consumed by transformation.

<!-- P02 -->
### [x] P02: Implement the complete detector catalog

<!-- P02-T01 -->
#### [x] P02-T01: Add structural, referential, ambiguity, and completeness checks

<!-- P02-T02 -->
#### [x] P02-T02: Add contradiction, provenance, authority, and retrieval checks

<!-- P02-T03 -->
#### [x] P02-T03: Pass peer profiles and map findings to proposed changes

Refactor discovery into two passes: collect every readable profile first, then
generate each report with the complete peer set. Unreadable documents remain in
the run's failed set.

<!-- P03 -->
### [x] P03: Expose evidence to content owners

<!-- P03-T01 -->
#### [x] P03-T01: Add authorized normalized-content retrieval

Require the report's exact `source_version` and reject a mismatch.

<!-- P03-T02 -->
#### [x] P03-T02: Render evidence-rich Results and a full-document viewer

<!-- P03-T03 -->
#### [x] P03-T03: Explain deterministic check completion and uncertainty

<!-- P04 -->
### [x] P04: Validate, document, and deploy

<!-- P04-T01 -->
#### [x] P04-T01: Add bounded semantic and integration tests

<!-- P04-T02 -->
#### [x] P04-T02: Update the feature guide and run full validation

<!-- P04-T03 -->
#### [x] P04-T03: Commit, deploy to Azure, and verify the live workflow

## Dependencies

* P02 depends on P01.
* P03 depends on P01 and the report shape from P02.
* P04 depends on P01 through P03.

## Test Ownership

* `tests/test_assessment.py`: one parameterized detector-catalog test that asserts
  equality with the complete FR09 catalog, plus one peer-aware conflict test.
* `tests/test_estate_interfaces.py`: one authorized content-endpoint test.
* `tests/test_architecture.py`: extend the current Results UI contract test.
* `tests/test_parsers.py` or existing inventory test: one structural-context
  preservation assertion.
* Maximum new test functions: four.
* Exact removals: none.

## Risks and Mitigations

* Linguistic false positives: quote evidence and mark findings for review.
* Missing semantic contradictions: state deterministic limitations and avoid an
  all-clear claim beyond completed checks.
* Large content exposure: authorize by estate and fetch only on demand.
* Compatibility drift: retain legacy fields and additive defaults.
* UI density: use expandable evidence and a dedicated content dialog.

## Critique Disposition

* PC-001: Applied. P02-T03 now requires complete-profile two-pass discovery.
* PC-002: Applied. FR09 and the parameterized test own the exact 22-code catalog.
* PC-003: Applied. P03-T01 and AC06 require source-version-pinned retrieval.
* PC-004: Applied. P01-T02 preserves real headings without synthetic location
  markers in transformation text.
* Final-candidate critique execution: Complete
* Verdict after direct corrections: Ready

## Follow-Up Items

* Consider a separately evaluated model-assisted semantic contradiction lane
  after a representative human-labelled dataset exists.

## Handoff

Ready for automatic implementation. No user decision or blocker remains.
