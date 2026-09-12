# Delete Knowledge Estate Plan

## Metadata

* Task ID: delete-knowledge-estate
* Status: Ready

## Executive Summary

Add an administrator-only Delete estate action to the estate workspace. Require exact-name confirmation in an accessible modal, reuse the existing purge API, and return the user to an updated estate portfolio after successful deletion.

## Sources

* .copilot-tracking/research/2026-09-11/delete-knowledge-estate-research.md

## User Decisions and Requirements

* A user must be able to delete a knowledge estate.
* Existing Microsoft Copilot Studio-like visual conventions remain authoritative.

## Goals

* Make estate deletion discoverable and intentional.
* Preserve existing authorization, purge, and tombstone guarantees.

## Scope and Non-Goals

* In scope: estate-page action, exact-name confirmation dialog, purge request, portfolio refresh, tests, and deployment.
* Non-goals: bulk deletion, restore, retention-policy redesign, or new backend deletion semantics.

## Functional Requirements

* FR-01: The estate heading exposes Delete estate.
* FR-02: Submission remains disabled until the entered estate name exactly matches.
* FR-03: Confirmation calls the existing purge endpoint and removes the estate from the visible portfolio.
* FR-04: API authorization and errors remain visible to the user.

## Non-Functional Requirements

* NFR-01: The dialog is keyboard-operable, named, and focus-safe.
* NFR-02: The action is visually destructive without disrupting existing Fluent styling.
* NFR-03: No deletion occurs on cancel, mismatch, or request failure.

## Acceptance Criteria

* AC-01: Delete estate opens a warning dialog naming the active estate.
* AC-02: The destructive submit is disabled until exact-name confirmation.
* AC-03: Success invokes `POST /v1/estates/{id}/purge`, closes the dialog, announces success, and returns to the refreshed portfolio.
* AC-04: Cancel and failed requests preserve the estate.
* AC-05: Targeted tests, JavaScript syntax, responsive browser checks, and live deployment health pass.

## Phase Checklist

<!-- rpi:phase id=P01 -->
### [ ] P01: Implement Safe Estate Deletion

<!-- rpi:task id=P01-T01 -->
#### [ ] P01-T01: Add the Confirmed Delete Interaction

* Reuse the existing administrator-only purge contract.

<!-- rpi:task id=P01-T02 -->
#### [ ] P01-T02: Validate and Deploy

* Prove interaction states, regression safety, and live revision health.

## Critique Disposition

* The bounded plan reuses an already tested destructive backend contract. No independent critique was dispatched because the complete review scope is small enough to inspect directly; exact confirmation, failure preservation, accessibility, and server authorization are locked as implementation gates.

## Follow-Up Items

* None.

## Handoff

* Planning Readiness: Ready.
* Changes record: .copilot-tracking/changes/2026-09-11/delete-knowledge-estate-changes.md
