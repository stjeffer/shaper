<!-- markdownlint-disable-file -->
# RPI Plan: MCP Knowledge Estate Workflow Parity

## Task Metadata

* Task ID: MCP-KNOWLEDGE-ESTATE-PARITY-2026-09-17
* Task slug: mcp-knowledge-estate-parity
* Planning status: Ready
* Plan date: 2026-09-17
* Phase details: .copilot-tracking/details/2026-09-17/mcp-knowledge-estate-parity-phase-details.md
* Plan critique: .copilot-tracking/reviews/plans/2026-09-17/mcp-knowledge-estate-parity-plan-critique.md

## Executive Summary

Shaper already exposes an authenticated Streamable HTTP MCP server, but that
server covers only grounded query, evidence explanation, legacy compilation,
and compile-job status. The implemented Knowledge Estate workflow is available
through the browser and REST API only.

This plan adds MCP coverage by adapting the existing application services
rather than calling REST internally or duplicating business rules. MCP clients
will be able to inspect estates, documents, findings, proposals, decisions,
runs, artifacts, and evaluation suggestions; start bounded workflow runs; and
submit governed decisions using the same authorization, revision, source
identity, acknowledgment, and publication checks already enforced by the
application.

Binary file transfer remains on the authenticated REST upload endpoint. MCP
will expose source registration and the resulting inventory but will not accept
base64 file bodies. This avoids excessive MCP context use, preserves current
size and malware-scanning controls, and gives clients a clear upload-then-use
workflow.

The expected implementation is medium-sized: approximately 6 to 9 engineering
days, including contract design, implementation, tests, documentation, and
deployment verification. The estimate assumes no new OAuth application,
connector, or asynchronous job platform is required.

### User Decisions and Requirements Highlights

* Extend the implemented Shaper capabilities into MCP.
* Provide usable instructions for MCP consumers.
* Preserve the findings-led, score-free workflow and explain agent impact.
* Keep approved changes, finding acknowledgment, and publication governed.

### What You May Not Know

* Most required behavior already exists in application services behind REST, so
  the MCP layer should remain thin.
* The evaluation set is currently assembled in the browser from proposal and
  source data. It needs an application service before REST and MCP can share it.
* MCP has no standard multipart file-upload primitive. Sending file bytes as
  JSON base64 would increase memory and token costs and duplicate existing
  upload controls.
* MCP tool annotations communicate risk to clients but cannot prove that a
  person confirmed an action. Server-side roles, revisions, rationales, and
  exact finding acknowledgments remain the enforcement boundary.

### Unresolved Decisions or Blockers

* None. The plan adopts REST staging for binary uploads, treats MCP elicitation
  as an optional client enhancement rather than a security dependency, and
  exposes current non-idempotent workflow starts with explicit annotations and
  retry guidance.

For current user input, see [User Decisions and Requirements](#user-decisions-and-requirements).
The planner keeps the synthesized sections below current as evidence and user
direction evolve.

## User Decisions and Requirements

* Add the currently missing Knowledge Estate, findings, reshaping, approval,
  export, and evaluation capabilities to MCP.
* Reuse the deployed authenticated MCP endpoint and existing collection-scoped
  authorization model.
* Do not weaken the product's human-governance and source-integrity controls.
* Keep the interface findings-led and do not reintroduce a readiness score out
  of 100.
* Provide clear usage and deployment instructions for MCP clients.

## Goals

* Give authorized MCP clients functional parity with the governed Knowledge
  Estate workflow, except for raw binary upload transport.
* Keep REST, browser, and MCP behavior consistent by sharing application
  services and response contracts.
* Make all consequential actions explicit, concurrency-safe, auditable, and
  discoverable through MCP metadata and tool descriptions.
* Preserve exact approved artifact bytes and source-backed finding evidence.
* Provide tested client setup and end-to-end usage documentation.

## Scope and Non-Goals

### In Scope

* Extend the MCP service dependency container with existing estate, source,
  inventory, discovery, recommendation, decision, transformation, review, and
  repository services.
* Add read-only MCP tools and resources for estates, sources, documents,
  assessment checks, runs, findings, proposals, decisions, artifacts, token
  usage, evaluation suggestions, and approved HTML.
* Add MCP mutation tools for estate creation and update, source registration,
  discovery, recommendation, proposal decisions, transformation, and artifact
  approval.
* Preserve optimistic concurrency and exact finding acknowledgment inputs.
* Add a shared server-side evaluation-set service so browser, REST, and MCP use
  one deterministic implementation.
* Add MCP tool annotations and structured, sanitized error responses.
* Add interface, authorization, parity, exact-byte, and deployment smoke tests.
* Update architecture, feature, deployment, operations, README, and MCP usage
  documentation.

### Non-Goals

* Raw file or ZIP bytes transported as base64 through MCP tool arguments.
* SharePoint synchronization before connector consent and synchronization are
  implemented.
* New content transformations, assessment checks, or scoring models.
* Replacing REST or the browser workspace.
* Making MCP elicitation support mandatory for all clients.
* Exposing filesystem paths, database identifiers, credentials, source content
  in logs, or unapproved artifact bytes.
* Estate purge in the first MCP parity release. Purge remains browser or REST
  only because it is irreversible and has no demonstrated agent use case.

## Functional Requirements

* FR-01: MCP clients can list and inspect authorized Knowledge Estates with
  assessment summaries and revision metadata.
  * Observable acceptance criteria: Results match REST semantics and exclude
    unauthorized tenant or collection records.
* FR-02: MCP clients can create and update an estate using the existing
  collection role and optimistic revision checks.
  * Observable acceptance criteria: Conflicting revisions fail without
    mutation.
* FR-03: MCP clients can register URL or SharePoint sources and inspect sources,
  documents, source-retention state, and document content where authorized.
  * Observable acceptance criteria: Registration does not claim synchronization
    and raw binary upload remains a documented REST staging step.
* FR-04: MCP clients can start discovery and retrieve per-document findings,
  evidence, completed checks, and plain-language agent impact.
  * Observable acceptance criteria: The response contains no readiness score
    out of 100 and matches stored report data.
* FR-05: MCP clients can start recommendations and inspect exact proposals,
  source versions, token estimates, and current decisions.
  * Observable acceptance criteria: Cross-estate and stale references fail.
* FR-06: Review-authorized MCP clients can approve or decline an exact proposal
  with a rationale and expected current decision identity.
  * Observable acceptance criteria: The existing review role, stale-source, and
    decision-conflict checks remain authoritative.
* FR-07: MCP clients can start a bounded transformation with optional one-pass
  preservation repair and inspect run status, usage, generated artifacts, and
  validation findings.
  * Observable acceptance criteria: Only currently approved proposals can be
    transformed, and non-bypassable integrity failures still prevent artifacts.
* FR-08: Review-authorized MCP clients can inspect artifact metadata and preview
  hash-verified generated HTML.
  * Observable acceptance criteria: Preview remains unavailable to query-only
    callers.
* FR-09: Review-authorized MCP clients can approve the current artifact revision
  with rationale, expected review revision, expected artifact revision, and the
  exact set of current finding rule identifiers.
  * Observable acceptance criteria: Missing, additional, stale, or mismatched
    acknowledgments prevent approval.
* FR-10: Query-authorized MCP clients can retrieve exact hash-verified bytes for
  approved HTML artifacts.
  * Observable acceptance criteria: Generated but unapproved content is denied,
    and returned bytes hash to the stored content hash.
* FR-11: MCP clients can generate and retrieve up to 20 distinct,
  source-grounded evaluation questions through a shared application service.
  * Observable acceptance criteria: Sparse estates return fewer questions
    without duplicates or filler.
* FR-12: MCP discovery accurately describes each tool's read-only, mutating,
  idempotent, and destructive characteristics.
  * Observable acceptance criteria: Client tool listing includes annotations
    and no tool description implies authority the server does not grant.
* FR-13: MCP callers receive stable structured errors for authentication,
  authorization, validation, conflict, not-found, rate-limit, and provider
  failures.
  * Observable acceptance criteria: Errors contain safe actionable categories
    without secrets, source text, or internal storage paths.

## Non-Functional Requirements

* NFR-01: MCP and REST operations use the same application service methods and
  domain models.
  * Objective threshold or evaluation condition: No MCP adapter duplicates
    assessment, transformation, decision, review, or publication business
    rules.
  * Observable acceptance criteria: Parity tests produce equivalent normalized
    results for representative REST and MCP calls.
* NFR-02: All MCP operations fail closed under existing tenant and
  collection-role authorization.
  * Objective threshold or evaluation condition: Every tool has positive,
    missing-role, and cross-tenant tests.
  * Observable acceptance criteria: Unauthorized requests return no protected
    record data.
* NFR-03: Updates, decisions, and approvals preserve existing optimistic
  concurrency; compile jobs preserve existing idempotency; estate creation,
  source registration, discovery start, recommendation start, and
  transformation start are explicitly non-idempotent in this release.
  * Objective threshold or evaluation condition: Revision conflicts and compile
    idempotency remain tested; each non-idempotent tool is marked
    `idempotentHint=false`, returns a unique persisted identity, and has a
    repeat-call visibility test.
  * Observable acceptance criteria: Retries cannot silently overwrite current
    state, and operators are told to inspect current runs before retrying a
    timed-out workflow start.
* NFR-04: MCP does not expose a user-facing readiness score out of 100.
  * Objective threshold or evaluation condition: Contract snapshots and tests
    contain findings and agent impact, not aggregate readiness scores.
  * Observable acceptance criteria: MCP responses match the findings-led UI and
    REST policy.
* NFR-05: Approved artifact export preserves exact stored bytes.
  * Objective threshold or evaluation condition: SHA-256 and byte-equality tests
    pass for MCP resource reads.
  * Observable acceptance criteria: MCP and REST downloads are byte-identical.
* NFR-06: Long-running transformation calls remain bounded and observable.
  * Objective threshold or evaluation condition: MCP transformation accepts one
    recommendation per call, has a documented client timeout of at least 210
    seconds for the initial request plus one optional 90-second repair, and
    returns a persisted run identity that can be inspected after a client-side
    timeout.
  * Observable acceptance criteria: Timeout and provider failures remain
    inspectable through run reads and produce terminal run records or explicit
    recovery guidance rather than a fabricated success.
* NFR-07: MCP responses and logs do not disclose access tokens, filesystem
  paths, database connection data, or unrelated source content.
  * Objective threshold or evaluation condition: Security-focused response and
    logging tests pass.
  * Observable acceptance criteria: Errors and resources contain only
    authorized bounded data.
* NFR-08: Existing MCP clients remain compatible.
  * Objective threshold or evaluation condition: The original four tools and
    three resource URI families retain names and behavior.
  * Observable acceptance criteria: Existing interface tests pass unchanged,
    except for assertions that intentionally expand the complete tool set.

## Acceptance Criteria

* AC-01: Given a query-only principal, when the MCP client lists and reads an
  estate, reports, findings, proposals, runs, and approved artifacts, then only
  records in authorized collections are returned.
* AC-02: Given a principal without the required role or from another tenant,
  when any new MCP tool or resource is called, then access fails without leaking
  whether the protected record exists.
* AC-03: Given an active estate and staged REST upload, when the client invokes
  the MCP workflow, then it can discover, review findings, generate proposals,
  record decisions, transform, inspect artifacts, approve, and retrieve approved
  HTML.
* AC-04: Given a stale estate, proposal decision, review, or artifact revision,
  when a mutation is attempted, then the operation reports a conflict and makes
  no change.
* AC-05: Given artifact validation findings, when approval omits or alters the
  exact acknowledgment set, then approval fails.
* AC-06: Given an unapproved artifact, when a query-role caller requests export,
  then access fails; after governed approval, the MCP bytes equal REST download
  bytes and the stored hash.
* AC-07: Given preservation repair is disabled, when an integrity-valid
  transformation has reviewable preservation findings, then the artifact is
  retained with those findings rather than blocked.
* AC-08: Given preservation repair is enabled, when reviewable findings exist,
  then at most one repair is attempted and remaining findings are persisted.
* AC-09: Given a sparse estate, when evaluation questions are requested, then
  fewer than 20 distinct grounded questions are returned instead of duplicates.
* AC-10: Given any MCP list-tools response, when clients inspect annotations,
  then read and mutation characteristics are accurate and irreversible purge is
  absent.
* AC-11: Given the current MCP query and compile consumers, when the expanded
  server is deployed, then all four existing tools and all three existing
  resources remain usable.
* AC-12: Given deployment smoke credentials, when the MCP smoke test runs, then
  it initializes, lists the expected tool set, calls one authorized read tool,
  and verifies one authorization denial.
* AC-13: Given a documented MCP client configuration, when an operator follows
  the instructions with a valid token, then the client can initialize, list
  tools, and complete the staged end-to-end workflow.
* AC-14: Given any non-idempotent MCP mutation, when the same arguments are
  submitted twice, then two distinct persisted identities are visible and the
  tool metadata and documentation warn the caller to inspect current state
  before retrying.
* AC-15: Given the original MCP resource families, when a real SDK client reads
  a unit, source, and release resource, then their names and behavior remain
  compatible.

## Implementation Context Record

| Context item | Current artifact or record |
|---|---|
| Plan | .copilot-tracking/plans/2026-09-17/mcp-knowledge-estate-parity-plan.md |
| Phase details | .copilot-tracking/details/2026-09-17/mcp-knowledge-estate-parity-phase-details.md |
| Latest critique | .copilot-tracking/reviews/plans/2026-09-17/mcp-knowledge-estate-parity-plan-critique.md with all findings resolved in this plan |
| Relevant research | Existing code, tests, BRD, architecture, deployment, operations, and prior MCP research are sufficient |
| Changes-record role | .copilot-tracking/changes/2026-09-17/mcp-knowledge-estate-parity-changes.md is created or continued by implementation |
| Planning execution and readiness | Planning and critique complete; ready for implementation |
| Continuation context | Standalone implementation-ready plan |

## Sources

* src/shaper/interfaces/mcp_server.py: Existing MCP tools, resources, auth, and
  FastMCP configuration.
* src/shaper/interfaces/http.py: Current Knowledge Estate REST contracts and
  orchestration.
* src/shaper/interfaces/auth.py: OIDC validation and collection-role mapping.
* src/shaper/application/estates.py: Estate, source, inventory, discovery, and
  recommendation services.
* src/shaper/application/decisions.py: Proposal decision authorization and
  optimistic intent.
* src/shaper/application/artifacts.py: Transformation, review, exact
  acknowledgment, and approved-content controls.
* src/shaper/domain/estate.py: Knowledge Estate, finding, artifact, and revision
  models.
* tests/test_interfaces.py: Existing MCP contract and shared-host tests.
* tests/test_estate_interfaces.py: REST workflow and authorization evidence.
* tests/test_artifacts.py: Artifact review, acknowledgment, and exact-byte
  evidence.
* prototype/copilot-studio-knowledge-compiler/app.js: Browser integration with
  shared evaluation-set generation.
* docs/planning/brds/shaper-business-requirements.md: Business requirements and
  governance boundaries.
* docs/architecture.md: Current application and validation architecture.
* docs/deployment.md: Deployed MCP transport, identity, and smoke test.
* docs/operations.md: Security, upgrade, and operational requirements.

## Phase Checklist

<!-- rpi:phase id=P01 -->
### [x] P01: Define MCP contracts and shared boundaries

* Intent: Establish the tool taxonomy, input and output schemas, error model,
  annotations, compatibility constraints, and binary-upload boundary.
* Dependencies: Existing domain models and FastMCP SDK capabilities.

<!-- rpi:task id=P01-T01 -->
#### [x] P01-T01: Define tool and resource contracts

* Requirement and evidence: FR-01 through FR-13 and current REST operations.
* Expected result: A reviewed contract table for names, roles, inputs, outputs,
  annotations, retry semantics, errors, and application service owners.
* Detail section: P01-T01 in .copilot-tracking/details/2026-09-17/mcp-knowledge-estate-parity-phase-details.md

<!-- rpi:task id=P01-T02 -->
#### [x] P01-T02: Extract shared response and evaluation services

* Requirement and evidence: NFR-01 and browser-only evaluation generation.
* Expected result: REST, browser, and MCP can consume shared application-owned
  summaries and evaluation suggestions without adapter-to-adapter calls.
* Detail section: P01-T02 in .copilot-tracking/details/2026-09-17/mcp-knowledge-estate-parity-phase-details.md

<!-- rpi:phase id=P02 -->
### [x] P02: Add read and evidence surfaces

* Intent: Let MCP clients inspect every governed workflow object before any
  mutation.
* Dependencies: P01.

<!-- rpi:task id=P02-T01 -->
#### [x] P02-T01: Add estate, source, document, run, and report tools

* Requirement and evidence: FR-01, FR-03, FR-04, and AC-01.
* Expected result: Authorized structured reads match REST behavior and retain
  finding evidence and agent-impact language.
* Detail section: P02-T01 in .copilot-tracking/details/2026-09-17/mcp-knowledge-estate-parity-phase-details.md

<!-- rpi:task id=P02-T02 -->
#### [x] P02-T02: Add proposal, decision, artifact, usage, and evaluation tools

* Requirement and evidence: FR-05, FR-08, FR-11, and AC-01.
* Expected result: Clients can obtain all state required to make explicit,
  revision-aware decisions.
* Detail section: P02-T02 in .copilot-tracking/details/2026-09-17/mcp-knowledge-estate-parity-phase-details.md

<!-- rpi:task id=P02-T03 -->
#### [x] P02-T03: Add bounded content resources

* Requirement and evidence: FR-03, FR-08, FR-10, NFR-05, and NFR-07.
* Expected result: Authorized source text, review preview, and approved HTML are
  available through typed resources with correct media types and hash checks.
* Detail section: P02-T03 in .copilot-tracking/details/2026-09-17/mcp-knowledge-estate-parity-phase-details.md

<!-- rpi:phase id=P03 -->
### [x] P03: Add governed workflow mutations

* Intent: Expose lifecycle and shaping operations without bypassing application
  controls.
* Dependencies: P01 and P02.

<!-- rpi:task id=P03-T01 -->
#### [x] P03-T01: Add estate and source mutations

* Requirement and evidence: FR-02, FR-03, and AC-04.
* Expected result: Create, update, and source registration reuse existing
  authorization and revision checks; upload staging remains REST.
* Detail section: P03-T01 in .copilot-tracking/details/2026-09-17/mcp-knowledge-estate-parity-phase-details.md

<!-- rpi:task id=P03-T02 -->
#### [x] P03-T02: Add discovery and recommendation mutations

* Requirement and evidence: FR-04, FR-05, and AC-03.
* Expected result: MCP can start bounded runs and return stored reports and
  proposals from the same application services as REST.
* Detail section: P03-T02 in .copilot-tracking/details/2026-09-17/mcp-knowledge-estate-parity-phase-details.md

<!-- rpi:task id=P03-T03 -->
#### [x] P03-T03: Add proposal decision and transformation mutations

* Requirement and evidence: FR-06, FR-07, AC-04, AC-07, and AC-08.
* Expected result: Review-role decisions and compile-role transformations
  preserve stale-source, current-decision, approval, integrity, and repair
  limits.
* Detail section: P03-T03 in .copilot-tracking/details/2026-09-17/mcp-knowledge-estate-parity-phase-details.md

<!-- rpi:phase id=P04 -->
### [x] P04: Add artifact governance and exact export

* Intent: Complete review, acknowledgment, approval, and publication parity.
* Dependencies: P02 and P03.

<!-- rpi:task id=P04-T01 -->
#### [x] P04-T01: Add artifact approval

* Requirement and evidence: FR-09, AC-04, and AC-05.
* Expected result: MCP approval requires the exact current revisions, rationale,
  review role, and complete current finding acknowledgment set.
* Detail section: P04-T01 in .copilot-tracking/details/2026-09-17/mcp-knowledge-estate-parity-phase-details.md

<!-- rpi:task id=P04-T02 -->
#### [x] P04-T02: Add approved HTML retrieval

* Requirement and evidence: FR-10, NFR-05, and AC-06.
* Expected result: MCP returns only approved, hash-verified HTML and proves byte
  equality with REST export.
* Detail section: P04-T02 in .copilot-tracking/details/2026-09-17/mcp-knowledge-estate-parity-phase-details.md

<!-- rpi:phase id=P05 -->
### [ ] P05: Validate, document, and deploy

* Intent: Prove parity, compatibility, security, usability, and production
  readiness.
* Dependencies: P01 through P04.

<!-- rpi:task id=P05-T01 -->
#### [x] P05-T01: Add contract, parity, and security tests

* Requirement and evidence: NFR-01 through NFR-08 and AC-01 through AC-12.
* Expected result: Targeted tests cover every tool, resource, role, conflict,
  repeat-call behavior, byte-preservation path, and the previously untested
  legacy resource families.
* Detail section: P05-T01 in .copilot-tracking/details/2026-09-17/mcp-knowledge-estate-parity-phase-details.md

<!-- rpi:task id=P05-T02 -->
#### [x] P05-T02: Publish MCP usage and operations guidance

* Requirement and evidence: AC-13 and current documentation set.
* Expected result: Documentation provides client configuration, token
  acquisition guidance, REST upload staging, complete workflow examples, role
  mapping, troubleshooting, and limitations.
* Detail section: P05-T02 in .copilot-tracking/details/2026-09-17/mcp-knowledge-estate-parity-phase-details.md

<!-- rpi:task id=P05-T03 -->
#### [ ] P05-T03: Deploy and smoke test MCP parity

* Requirement and evidence: AC-12 and existing Container Apps deployment.
* Expected result: A healthy revision initializes MCP, lists the expected tools,
  exercises an authorized read, proves an authorization denial, and completes a
  staged end-to-end workflow.
* Detail section: P05-T03 in .copilot-tracking/details/2026-09-17/mcp-knowledge-estate-parity-phase-details.md

## Dependencies

* Existing FastMCP version: Must support structured tools, resources, tool
  annotations, and Streamable HTTP without replacing the current transport.
* Existing application services: Remain the only authority for workflow and
  governance rules.
* Entra app roles: Query, compile, review, and admin claims must be assigned to
  MCP callers for their intended collections.
* Authenticated REST upload: Remains available for staging file and ZIP bytes
  before MCP workflow orchestration.
* ClamAV and PostgreSQL readiness: Required for upload and durable workflow
  behavior.
* Azure OpenAI capacity: Required for recommendation and transformation calls.

## Critique Disposition

| Critique run and finding | Disposition | Plan response or residual risk |
|---|---|---|
| PC-001 | Resolved | Evaluation-set Python tests are assigned to tests/test_estate_interfaces.py and tests/test_interfaces.py; no new test file is planned |
| PC-002 | Resolved with explicit residual risk | NFR-03, AC-14, P03, and P05 now document and test non-idempotent workflow starts; durable idempotency is a follow-up |
| PC-003 | Resolved | MCP transformation is limited to one recommendation per call, client timeout guidance is explicit, and run inspection after timeout is tested |
| PC-004 | Resolved | P05-T01 now requires first-time SDK regression coverage for all three original MCP resource families |
| PC-005 | Resolved | The grounded evaluation-set service is explicitly isolated from the legacy quality-score evaluator, and MCP schema tests forbid score fields |
| PC-006 | Resolved | Shared contracts may extend only the existing src/shaper/domain/estate.py; no new domain module is planned |
| PC-007 | Resolved | Inspection of pinned mcp 1.13.1 confirmed FastMCP resources accept raw bytes, so approved HTML uses a binary resource without base64 |

## Follow-Up Items

* Consider a future MCP-native binary transfer capability only if the protocol
  and target clients standardize a bounded upload mechanism. Owner: Product and
  security architecture.
* Consider asynchronous transformation jobs if measured MCP client or ingress
  timeouts make the existing synchronous service unsuitable. Owner: Platform
  engineering after telemetry review.
* Add durable idempotency keys to estate creation, source registration, and
  workflow-start application services if MCP retry telemetry shows duplicate
  records or material model spend. Owner: Product and platform engineering.

## Handoff

* Implementation artifact: .copilot-tracking/changes/2026-09-17/mcp-knowledge-estate-parity-changes.md
* Ready phase or task: P05-T03
* Remaining provisional question or blocker: Production deployment requires a
  separate release action and smoke credentials.
