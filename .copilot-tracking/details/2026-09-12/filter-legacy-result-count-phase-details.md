<!-- markdownlint-disable-file -->
# RPI Phase Details: Filter legacy Result count

## Metadata

* Task ID: filter-legacy-result-count
* Task slug: filter-legacy-result-count
* Related plan: .copilot-tracking/plans/2026-09-12/filter-legacy-result-count-plan.md
* Evidence sources: RV-001 and .copilot-tracking/research/2026-09-12/filter-legacy-result-count-research.md

## Phase Index

| Phase ID | Name | Status | Detail sections |
|---|---|---|---|
| P01 | Unify Results classification | Complete | P01, P01-T01, P01-T02 |

<!-- rpi:phase id=P01 -->
## P01: Unify Results classification

### Context

Rows classify codes for display, while the summary counts raw codes. This duplicates semantics and exposes legacy accountability codes only in the count.

### Intent

Create one pure classification helper and reuse it in both consumers.

### Boundaries

* Included: app.js classification/render/count logic and existing static UI test.
* Excluded: CSS, markup, backend, and new test cases.

### Likely Targets

* prototype/copilot-studio-knowledge-compiler/app.js
* tests/test_architecture.py

### Dependencies

* None.

### Validation Expectations

* Existing full validation remains green.
* Static test confirms row and summary share the helper.

### Completion Evidence

* Diff inspection and passing tests.

### Unresolved Items

* None.

<!-- rpi:task id=P01-T01 -->
### P01-T01: Extract and reuse presentable result classification

#### Context

Supported codes count individually, accountability-only codes count zero, and any number of unknown codes collapse to one generic result per document.

#### Intent

Centralize those rules.

#### Boundaries

* Included: Pure helper plus two consumers.
* Excluded: Presentation metadata changes.

#### Likely Targets

* prototype/copilot-studio-knowledge-compiler/app.js

#### Dependencies

* None.

#### Validation Expectations

* No duplicated raw `finding_codes.length` summary logic remains.

#### Completion Evidence

* Source diff and test assertion.

#### Unresolved Items

* None.

<!-- rpi:task id=P01-T02 -->
### P01-T02: Extend static regression coverage and validate

#### Context

The existing Results UI test can assert shared classifier usage without adding another test.

#### Intent

Lock the correction and run repository-native checks.

#### Boundaries

* Included: Existing test extension and full checks.
* Excluded: New dependencies or browser redesign.

#### Likely Targets

* tests/test_architecture.py

#### Dependencies

* P01-T01.

#### Validation Expectations

* Targeted and full tests, Ruff, formatting, mypy, JavaScript syntax, and diff whitespace pass.

#### Completion Evidence

* Recorded command results.

#### Unresolved Items

* None.
