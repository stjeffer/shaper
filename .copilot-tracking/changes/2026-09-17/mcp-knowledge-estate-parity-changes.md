<!-- markdownlint-disable-file -->
# RPI Changes: MCP Knowledge Estate Workflow Parity

## Metadata

* Task ID: MCP-KNOWLEDGE-ESTATE-PARITY-2026-09-17
* Related plan: .copilot-tracking/plans/2026-09-17/mcp-knowledge-estate-parity-plan.md
* Phase details: .copilot-tracking/details/2026-09-17/mcp-knowledge-estate-parity-phase-details.md
* Implementation date: 2026-09-17

## Execution Status

* Status: Implementation complete; production release pending
* Declared invocation scope: Full plan
* Completed scope markers: P01 through P04, P05-T01, and P05-T02
* All remaining active-plan markers: P05 and P05-T03
* Status basis: MCP parity, documentation, tests, and deployment smoke automation
  are complete and review-ready. No production deployment was performed.

## Execution Summary

The existing Streamable HTTP MCP server now exposes the governed Knowledge
Estate workflow through the same application services used by REST. Binary
upload remains an authenticated REST staging operation, while MCP handles
discovery, findings, recommendations, decisions, transformations, artifact
review and approval, exact approved HTML retrieval, and evaluation questions.

## Completed Work

### Shared contracts and evaluation generation

* Added an application-owned deterministic evaluation-set service.
* Added an authenticated REST evaluation endpoint and moved the browser from a
  duplicate local generator to that shared service.
* Removed the retired JavaScript reference generator and its disconnected test.

### MCP read and workflow surfaces

* Expanded the existing four MCP tools with the complete Knowledge Estate tool
  set while preserving all original tool and resource identifiers.
* Added estate, source, document, run, report, proposal, decision, artifact,
  assessment-check, and evaluation reads.
* Added governed estate creation and update, URL and SharePoint source
  registration, discovery, recommendation, proposal decision, transformation,
  artifact review, and artifact approval operations.
* Kept raw file and ZIP upload on the authenticated REST endpoint so existing
  size, malware scanning, archive, and retention controls remain authoritative.
* Removed readiness scores from MCP discovery reports while retaining clear
  findings, evidence, severity, and agent-impact language.

### Governed resources and publication

* Added versioned source text and artifact preview resources.
* Added an approved-content resource that returns exact hash-verified bytes.
* Preserved review-role authorization, optimistic revisions, rationale,
  complete finding acknowledgment, and publication integrity checks.

### Documentation and operations

* Added a complete MCP setup, authentication, workflow, testing, deployment,
  and troubleshooting guide.
* Updated README, architecture, feature, deployment, and operations guidance.
* Expanded deployment smoke automation to verify tool discovery, an authorized
  estate read, and a collection authorization denial.

### Tests and independent review

* Added real MCP SDK workflow coverage from estate creation through exact-byte
  approved HTML retrieval.
* Added regression coverage for all original MCP resource families.
* Added evaluation, REST parity, authorization, score-removal, and browser
  architecture tests.
* Independent code review found and resolved two documentation/test issues:
  discovery field names now match the live contract, and the unused browser-side
  evaluation implementation was removed.

## Implementation-Time Plan and Detail Updates

### Resolve final critique findings before source edits

* Affected plan area or markers: NFR-03, NFR-06, AC-14, AC-15, P01, P02-T03,
  P03, and P05
* What changed: Clarified non-idempotent workflow starts, one-document MCP
  transformation calls, retry guidance, first-time legacy resource tests,
  evaluation-score isolation, domain-file scope, and raw-byte resource support.
* Why: The final critique identified retry, timeout, compatibility, naming, and
  scope ambiguities.
* Triggering evidence: PC-001 through PC-007 and direct inspection of pinned
  FastMCP 1.13.1.
* User answer or decision: The user requested implementation of the complete MCP
  layer with setup and testing documentation.
* Reconciliation performed: Plan requirements, acceptance criteria, critique
  disposition, phase details, dependencies, and follow-up items were updated.
* Planning and critique state: Ready; all critique findings are resolved or
  explicitly accepted with bounded residual risk.

## Validation Record

| Check | Scope | Status | Evidence or reason |
|---|---|---|---|
| FastMCP capability inspection | P01 | Passed | Pinned FastMCP accepts tool annotations and raw byte resources |
| Ruff | P01-P05 | Passed | All changed Python files pass |
| Strict mypy | P01-P05 | Passed | No issues in 89 source files |
| Targeted Python tests | P01-P05 | Passed | 68 tests pass |
| Tracked full Python suite | P01-P05 | Passed | 383 tests pass |
| Coverage gate | P05-T01 | Passed | 80.87%, above the 75% threshold |
| Bash syntax | P05-T03 preparation | Passed | `scripts/deploy.sh` parses successfully |
| Diff hygiene | Full change set | Passed | `git diff --check` reports no errors |
| Independent code review | Full change set | Passed | Two findings resolved; no remaining high-confidence findings |

## Pre-Review Reconciliation

* Plan markers and phase details: Reconciled
* Completed-work evidence and handoff prose: Reconciled
* Validation, blockers, remaining work, and follow-up items: Reconciled
* Review readiness: Ready; production release remains a separate action

## Blockers

* None.

## Remaining Work

* P05-T03: Deploy to production and run the authenticated post-deployment smoke
  workflow.

## Follow-Up Items

* Canonical plan list: .copilot-tracking/plans/2026-09-17/mcp-knowledge-estate-parity-plan.md, `## Follow-Up Items`
* MCP-native binary upload remains outside scope pending a standardized bounded
  transport.
* Durable idempotency for workflow starts remains a telemetry-triggered
  follow-up.
* Asynchronous transformation jobs remain a telemetry-triggered follow-up.

## Return-to-Caller State

* Implementation execution status: Complete and review-ready; release pending
* Declared scope and markers: Full plan; P01 through P04 and P05-T01/T02 complete
* Validation coverage: Ruff, mypy, 68 targeted tests, 383 tracked full-suite
  tests, 80.87% coverage, Bash syntax, and diff checks passed
* Blockers: None
* Current plan and detail updates: Completion markers and production-release
  boundary reconciled
* Planning and critique state: Ready
* Follow-up items: Native binary upload, durable workflow idempotency, and
  asynchronous transformation
* Review readiness or no-handoff reason: Ready for release; P05-T03 remains
  pending because no production deployment was requested
* Continuation owner: Release operator
