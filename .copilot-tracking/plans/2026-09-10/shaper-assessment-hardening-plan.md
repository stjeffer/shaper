<!-- markdownlint-disable-file -->
# RPI Plan: Shaper Assessment Hardening

## Metadata

* Task ID: shaper-assessment-hardening
* Task slug: shaper-assessment-hardening
* Planning status: Ready
* Plan date: 2026-09-10
* Parent task: shaper-knowledge-transformation-platform
* Research: .copilot-tracking/research/2026-09-10/shaper-assessment-hardening-research.md
* Phase details: .copilot-tracking/details/2026-09-10/shaper-assessment-hardening-phase-details.md
* Planned critique: .copilot-tracking/reviews/plans/2026-09-10/shaper-assessment-hardening-plan-critique.md

## Executive Summary

Resolve RV-001 through RV-004 as one bounded reliability and accessibility
increment. Enforce aware assessment times at the application boundary, preserve
coverage semantics for unassessable text, make both schema invocation forms
execute and publish current models, and retain keyboard focus at the approval
transition. Add focused regression tests and rerun the complete validation set.

## User Decisions and Requirements

* The automatic RPI session selected the highest-ranked Review follow-up because
  the user was unavailable at the checkpoint.
* Preserve the accepted Knowledge Transformation Platform direction.
* Resolve all four medium Review findings without adding product scope.
* Do not run another Review for closure of findings from the parent task.

## Goals

* Reject timezone-naive assessment times explicitly for HTTP and direct callers.
* Treat unassessable readability as unavailable evidence rather than an exception.
* Publish assessment contracts in the canonical generated schema.
* Preserve keyboard focus when the approval confirmation replaces its trigger.

## Scope and Non-Goals

In scope:

* src/shaper/application/assessment.py
* src/shaper/interfaces/http.py when explicit error mapping is required
* src/shaper/schema.py and schemas/v1/domain.schema.json
* prototype/copilot-studio-knowledge-compiler/index.html and app.js
* Focused semantic, interface, schema, and interaction regression coverage

Out of scope:

* Metric calibration or threshold changes
* New connectors, distributed processing, or transformation modes
* Product redesign or dependency additions
* Changes to source mutation or publication policy

## Functional Requirements

* A timezone-naive `assessed_at` fails before date arithmetic.
* The HTTP endpoint returns a validation-class response rather than HTTP 500 for
  a naive assessment time.
* A profile with no word-bearing sentence completes with readability unavailable
  and reduced assessment coverage.
* `python -m shaper.schema` and `shaper-schema` both call the same generator.
* The generated domain snapshot contains `EstateAssessment` and
  `KnowledgeDocumentProfile`.
* Preparing approval moves focus to the revealed confirmation and keeps the live
  announcement.

## Non-Functional Requirements

* Existing assessable profile scores remain unchanged.
* Error handling uses narrow validation paths without broad exception catches.
* No new dependencies are introduced.
* The generated schema remains deterministic.
* Focus has a visible indicator and is exposed in the accessibility tree.

## Acceptance Criteria

* Direct service and HTTP tests reproduce and close RV-001.
* An unavailable-readability test closes RV-002 and verifies reduced coverage.
* Both schema command forms pass and the snapshot contains both public contracts.
* A browser interaction assertion confirms the approval confirmation owns focus.
* Ruff format and lint, mypy, full pytest with coverage, schema checks, Bicep
  compilation, JavaScript syntax, axe, reduced motion, and 320-pixel reflow pass.
* No parent Review is repeated.

## Sources

* .copilot-tracking/reviews/logs/2026-09-10/shaper-knowledge-transformation-platform-review.md
* .copilot-tracking/research/2026-09-10/shaper-assessment-hardening-research.md
* src/shaper/application/assessment.py
* src/shaper/interfaces/http.py
* src/shaper/schema.py
* prototype/copilot-studio-knowledge-compiler/app.js

## Phase Checklist

<!-- rpi:phase id=P01 -->
### [x] P01: Harden assessment input semantics

<!-- rpi:task id=P01-T01 -->
#### [x] P01-T01: Enforce aware assessment time

Add service-boundary validation and explicit HTTP regression coverage so all
callers fail before date arithmetic.

<!-- rpi:task id=P01-T02 -->
#### [x] P01-T02: Preserve unavailable readability

Aggregate only assessable readability values and emit the existing unavailable
metric shape when an estate has none.

<!-- rpi:phase id=P02 -->
### [x] P02: Repair canonical schema publication

<!-- rpi:task id=P02-T01 -->
#### [x] P02-T01: Execute and regenerate both schema paths

Add the module entrypoint, regenerate the snapshot, and prove module and console
invocations use current models.

<!-- rpi:phase id=P03 -->
### [x] P03: Restore approval focus and validate

<!-- rpi:task id=P03-T01 -->
#### [x] P03-T01: Move focus to approval confirmation

Make the revealed state programmatically focusable and focus it before hiding
the initiating control.

<!-- rpi:task id=P03-T02 -->
#### [x] P03-T02: Run focused and full validation

Run regression tests and the complete parent validation matrix, including
dynamic accessibility evidence.

## Dependencies and Change Budget

* Existing Pydantic, FastAPI, pytest, schema, and static concept patterns only.
* Test ownership: tests/test_assessment.py and tests/test_interfaces.py; browser
  interaction evidence for the static concept.
* Exact removals: None.
* Maximum production additions: 35 lines excluding generated schema.
* Maximum test additions: 4 focused cases.
* Maximum dependencies: Zero.
* Canonical generated target: schemas/v1/domain.schema.json.

## Critique Disposition

* One final-candidate critique completed with a Pass verdict and no actionable findings.

## Follow-Up Items

* Parent calibration, connector, managed-processing, and broader transformation
  work remain outside this child task.

## Handoff

* Planned changes record:
  .copilot-tracking/changes/2026-09-10/shaper-assessment-hardening-changes.md
* Ready phase or task: Review.
* Blockers: None.
