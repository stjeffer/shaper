<!-- markdownlint-disable-file -->
# Plan Critique: Evidence-grounded document findings

## Inputs

* Plan: .copilot-tracking/plans/2026-09-12/evidence-grounded-document-findings-plan.md
* Phase details: .copilot-tracking/details/2026-09-12/evidence-grounded-document-findings-phase-details.md
* Research: .copilot-tracking/research/2026-09-12/evidence-grounded-document-findings-research.md
* Caller requirements: Complete supplied issue taxonomy, exact document content,
  reviewable findings, and approval of changes.

## Criterion Boundary

The critique assessed requirements coverage, report compatibility, ingestion
evidence, peer-aware execution, authorization, UI evidence, tests, deployment,
and false-positive controls.

## Execution

* Execution status: Complete
* Verdict: Revise

## Coverage Assessment

The candidate addresses the correct architecture and preserves the approval
boundary. Four planner-owned gaps need explicit acceptance criteria or task
detail before implementation.

## Findings

### PC-001: Peer-aware report execution order is unspecified

* Severity: High
* Related IDs: FR04, P02-T03
* Evidence: C1 and C11 show reports are currently persisted while profiles are
  still being collected.
* Impact: Early documents cannot reliably compare against later estate peers.
* Smallest useful change: Require a two-pass discovery loop that builds every
  readable profile before generating any report.
* Action owner: Planner
* Resolving evidence: Plan and details explicitly require two-pass execution and
  preserve partial-run handling for unreadable documents.
* Decision type: Direct correction

### PC-002: The complete detector contract is not enumerated

* Severity: High
* Related IDs: FR03, P02-T01, P02-T02, AC01
* Evidence: The user supplied 22 distinct conditions, while the plan summarizes
  groups without stable codes.
* Impact: Implementation or tests could omit a required condition without
  violating a named contract.
* Smallest useful change: Add the exact stable code list to the plan and bind
  the parameterized test to it.
* Action owner: Planner
* Resolving evidence: Plan lists every code and requires catalog equality.
* Decision type: Direct correction

### PC-003: Content retrieval is not version-pinned

* Severity: Medium
* Related IDs: FR06, NFR03, AC06
* Evidence: Reports are source-version pinned, while the planned endpoint says
  only "current normalized document content."
* Impact: A content owner could open text that differs from the evidence used by
  the displayed report after a new version arrives.
* Smallest useful change: Require `source_version` on retrieval and reject a
  version mismatch.
* Action owner: Planner
* Resolving evidence: Endpoint task and acceptance criteria specify exact-version
  retrieval and mismatch rejection.
* Decision type: Direct correction

### PC-004: Structural preservation may silently change transformation input

* Severity: Medium
* Related IDs: P01-T02, NFR04
* Evidence: C7 identifies flattened normalized text as current transformation
  input.
* Impact: Adding headings and location markers could leak synthetic markers into
  generated content or change source semantics.
* Smallest useful change: Preserve real heading text only, keep parser locations
  in structured evidence where available, and never inject synthetic table or
  page labels into transformation text.
* Action owner: Planner
* Resolving evidence: Phase details constrain normalization and tests prove
  headings are preserved without synthetic location text.
* Decision type: Direct correction

## Severity Summary

* High: 2
* Medium: 2
* Low: 0

## Closeout

* Highest-impact finding: PC-001
* Action owner: Planner
* Smallest next action: Apply all four direct corrections in one plan revision.
* User response required: No
