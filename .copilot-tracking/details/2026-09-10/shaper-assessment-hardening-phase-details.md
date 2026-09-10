<!-- markdownlint-disable-file -->
# RPI Phase Details: Shaper Assessment Hardening

## Metadata

* Task ID: shaper-assessment-hardening
* Plan: .copilot-tracking/plans/2026-09-10/shaper-assessment-hardening-plan.md
* Research: .copilot-tracking/research/2026-09-10/shaper-assessment-hardening-research.md

## Planning State

* Interpreted goal: Close RV-001 through RV-004 without widening product scope.
* Evidence readiness: Root causes and expected regression states are confirmed.
* Active boundary: Assessment validation and optional metrics, schema execution
  and snapshot, final approval focus, and targeted validation.
* Unresolved decisions or blockers: None.

<!-- rpi:phase id=P01 -->
## P01: Harden assessment input semantics

<!-- rpi:task id=P01-T01 -->
### P01-T01: Enforce aware assessment time

Validate `assessed_at` in the application service before any scoring or finding
calculation. Use the existing validation response convention at the HTTP
boundary. Completion requires a direct-call failure and an HTTP 422 regression
for a naive ISO timestamp.

<!-- rpi:task id=P01-T02 -->
### P01-T02: Preserve unavailable readability

Allow each profile's readability result to be absent when no word-bearing
sentence exists. Average only available values. When no profile is assessable,
emit the existing unavailable metric representation so the dimension score
excludes it and assessment coverage falls. Completion requires unchanged normal
scores and an explicit punctuation-only regression.

<!-- rpi:phase id=P02 -->
## P02: Repair canonical schema publication

<!-- rpi:task id=P02-T01 -->
### P02-T01: Execute and regenerate both schema paths

Add a standard module guard that exits through `main`, then generate the
canonical snapshot from current source. Completion requires both invocation
forms to detect drift, both to pass against the regenerated file, and explicit
presence of the two assessment model names.

<!-- rpi:phase id=P03 -->
## P03: Restore approval focus and validate

<!-- rpi:task id=P03-T01 -->
### P03-T01: Move focus to approval confirmation

Make the confirmation container focusable without adding it to normal tab order.
Reveal it, focus it, then hide the initiating button. Retain the polite live
announcement. Completion requires the computed active element to be the
confirmation and a visible focus style.

<!-- rpi:task id=P03-T02 -->
### P03-T02: Run focused and full validation

Run the smallest focused tests first, then Ruff, mypy, full pytest with coverage,
both schema commands, Bicep compilation, JavaScript syntax, axe, keyboard
interaction, reduced motion, and 320-pixel reflow. Record failures honestly and
do not run a second parent Review.

## Completion Evidence Contract

* P01 owns service and HTTP regression evidence.
* P02 owns deterministic generated-schema evidence.
* P03 owns dynamic focus and complete repository validation.
* The changes record reconciles all markers and any justified divergence.
