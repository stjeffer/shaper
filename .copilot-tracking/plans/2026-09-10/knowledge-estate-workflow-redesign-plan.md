<!-- markdownlint-disable-file -->
# RPI Plan: Knowledge Estate Workflow Redesign

## Task Metadata

* Task ID: knowledge-estate-workflow-redesign
* Task slug: knowledge-estate-workflow-redesign
* Planning status: Ready
* Plan date: 2026-09-10
* Phase details: .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md
* Plan critique: .copilot-tracking/reviews/plans/2026-09-10/knowledge-estate-workflow-redesign-plan-critique.md

## Executive Summary

Shaper will gain a durable Knowledge Estate workflow while remaining a multi-agent Knowledge Transformation Platform. A user will create an estate, add one or more sources, discover every document, select documents for detailed proposals, inspect transformation effort and token estimates, approve or decline each proposal, and transform only approved document versions into new named HTML artifacts.

The deterministic platform orchestrator will continue to own identity, authorization, source-version checks, workflow state, token budgets, human decisions, job dispatch, and publication. The Assessment Agent will produce document health evidence. The Knowledge Agent will analyze topics, overlap, contradictions, and cross-policy relationships. The Transformation Agent will propose and execute bounded transformations. The Governance Agent will identify drift and stale decisions. The Agent Readiness Agent will score document and estate usability. No agent may approve its own proposal, overwrite source content, or bypass publication review.

Implementation proceeds from immutable domain contracts through safe source ingestion, durable pollable analysis runs, multi-agent discovery, recommendation and decision gates, transformation and artifact creation, durable persistence, authenticated APIs, the hosted user experience, and Azure deployment. Discover and Recommend use deterministic agent logic in this increment and make no model calls. Existing compile, review, source-version, parser, and release-integrity primitives remain in place where their contracts are still valid.

### User Decisions and Requirements Highlights

* Shaper remains a platform coordinating five specialist agents, not a single agent.
* Knowledge Estates are named, durable, multi-source aggregates inside the existing collection authorization boundary.
* Every document receives readiness, effort, recommendation, token-estimate, decision, and transformation evidence.
* Only an explicitly approved source version may consume model tokens or produce a derivative.
* Transformations create immutable named HTML artifacts and never overwrite source content.

### What You May Not Know

* The existing review gate occurs after candidate generation. The new workflow needs a separate pre-transformation authorization while retaining review of generated output before publication.
* User-created estates need durable Azure state. The current deployed SQLite database is local to a Container Apps revision, so the production profile will use Azure Database for PostgreSQL while local development retains SQLite.
* The current hosted concept uses a public fixed sample. Live user-owned estates also require same-origin interactive Entra authentication. Azure Container Apps built-in authentication will identify the browser user, while PostgreSQL-backed collection grants will authorize that principal. Existing bearer-token API and MCP clients remain supported.
* SharePoint synchronization cannot truthfully report success until Microsoft Graph application permissions are granted. The source will remain in `authorization_required` state until that external dependency is satisfied.
* A first-generation token estimate can be exhausted. Retry requires a new estimate and a new approval so execution never exceeds the budget a user approved.

### Unresolved Decisions or Blockers

* No design decision blocks implementation planning.
* Live SharePoint synchronization, interactive app-role assignment, and passwordless PostgreSQL startup depend on tenant and database administrator configuration during deployment. The product must surface those states explicitly rather than substitute sample data.

For current user input, see [User Decisions and Requirements](#user-decisions-and-requirements). The planner keeps the synthesized sections below current as evidence and user direction evolve.

## User Decisions and Requirements

* Shaper must remain a Knowledge Transformation Platform that coordinates multiple specialized agents.
* The specialist roles remain Assessment Agent, Knowledge Agent, Transformation Agent, Governance Agent, and Agent Readiness Agent.
* Users must be able to define and name a Knowledge Estate containing one or more SharePoint locations, ZIP bundles, individual uploads, or supported connector URLs.
* Users must be able to review estate sources, upload content, and add URLs without fabricated connection states.
* Discovery must assess every individual document for current agent readiness and potential reshaping effort, including structural and cross-policy-reference problems.
* Users must select documents before requesting detailed recommendations.
* Every proposed transformation must include an estimated token range and enforced maximum before approval.
* Users must approve or decline each document proposal. Only the approved source version may be transformed.
* Transformations must create new artifacts and never overwrite source content.
* The estate owns the output naming rule. The default is `shaper_{source_stem}.html`.
* The resulting workflow must be live, testable, and deployed to Azure rather than represented by static connected states.
* The hosted interface must use a compact Microsoft Copilot Studio-like application shell and Fluent web typography, navigation, tabs, controls, and work surfaces rather than a bespoke dashboard treatment.

## Goals

* Deliver a live estate-to-artifact workflow through authenticated REST APIs and the hosted product experience.
* Preserve explicit multi-agent responsibilities behind deterministic orchestration and human approval.
* Make per-document quality, effort, proposed work, token demand, decisions, execution, and provenance inspectable.
* Persist user-created workflow state across process and Azure Container Apps revision replacement.
* Retain secure, accessible, and truthful behavior when a connector, model, database, or authorization dependency is unavailable.
* Provide explicit archive and purge behavior for real user content stored by the development deployment.

## Scope and Non-Goals

### In Scope

* Durable estate, source, document, discovery, recommendation, decision, transformation, token-usage, and artifact contracts
* Multi-agent orchestration across Discover, Recommend, Transform, and Govern
* SharePoint source registration, synchronization through the existing Graph connector, and truthful authorization state
* Safe individual upload and bounded ZIP expansion into individual estate documents
* Per-document discovery and estate-level relational analysis
* Selection-scoped recommendations, deterministic token estimates, and approval decisions
* Approved-only transformation and immutable HTML artifact publication
* Local SQLite and production PostgreSQL repository adapters
* Authenticated REST resources and same-origin browser authentication
* A live multi-screen Knowledge Estates experience
* Azure infrastructure, deployment automation, smoke tests, and architecture documentation
* WCAG 2.2 AA-oriented keyboard, focus, announcement, reflow, contrast, text-spacing, target-size, and reduced-motion verification
* Estate archive and administrator-authorized purge of content-bearing records and bytes

### Non-Goals

* Overwriting or editing source documents
* Unrestricted arbitrary web crawling or fetching
* Production support for Confluence, ServiceNow, wikis, file shares, or legacy intranet connectors in this increment
* Calibrated claims that the readiness score equals answer accuracy
* Replacing the specialist-agent architecture with one general-purpose agent
* Autonomous approval or publication by any agent
* Removing the existing JSONL release and query path
* Retrofitting every historical job into the new estate workflow
* A committed automated browser accessibility regression harness in this increment

## Functional Requirements

* FR-01: Authenticated users can create, list, inspect, rename, and archive Knowledge Estates within an authorized collection.
  * Observable acceptance criteria: The estate retains its name, description, naming policy, revision, and status after an application restart.
* FR-02: An estate can own multiple typed source registrations without changing the existing collection authorization boundary.
  * Observable acceptance criteria: One estate can contain multiple SharePoint registrations, uploaded files, and ZIP bundles with stable source IDs.
* FR-03: Source status is factual and explicit.
  * Observable acceptance criteria: Sources report states such as `pending`, `syncing`, `ready`, `authorization_required`, or `failed`; the UI never renders `connected` without successful connector evidence.
* FR-04: ZIP bundles expand into individually identifiable documents through bounded archive validation.
  * Observable acceptance criteria: Traversal, encrypted entries, unsupported formats, excessive entry counts, expanded-size limits, compression-ratio limits, and malware findings stop ingestion with actionable errors.
* FR-05: Discovery produces one immutable report per document version and one estate summary through a durable pollable run.
  * Observable acceptance criteria: Every current document has a 0-100 readiness score, evidence coverage, explainable effort band, findings, and provenance; duplicates, contradictions, topics, authority, and cross-policy relationships retain all affected document IDs. Runs expose queued, running, partial, completed, cancelling, cancelled, and failed states, process at most 500 documents, and reject larger snapshots with guidance to narrow the source set.
* FR-06: The five specialist agents retain distinct responsibilities in estate-scoped orchestration.
  * Observable acceptance criteria: Tests demonstrate Assessment, Knowledge, Transformation, Governance, and Agent Readiness results are composed by the orchestrator while approval and publication remain outside agent authority.
* FR-07: Recommendations are generated only for the document IDs selected by the user and are pinned to the discovery and source versions.
  * Observable acceptance criteria: A durable pollable run processes at most 100 selected documents, unselected documents receive no proposal, and exceeding the bound fails before work begins.
* FR-08: Every proposed transformation includes a deterministic token estimate.
  * Observable acceptance criteria: The proposal reports model deployment, estimator version, input and output ranges, expected total, enforced maximum, assumptions, and confidence without making a model call.
* FR-09: Users can approve or decline each proposed document transformation with an actor, reason, timestamp, expected revision, and source version.
  * Observable acceptance criteria: Conflicting revisions and changed source versions reject the decision rather than silently applying it.
* FR-10: Transformation job creation requires an approved current proposal.
  * Observable acceptance criteria: A declined, undecided, withdrawn, or stale proposal causes a typed conflict before any model call or artifact write.
* FR-11: Completed transformations retain actual token accounting separately from estimates.
  * Observable acceptance criteria: Input tokens, output tokens, model calls, tool calls, enforced maximum, estimate variance, model, and prompt version are queryable for each run.
* FR-12: Approved transformations create safe immutable HTML artifacts using the estate naming policy.
  * Observable acceptance criteria: The default resolves to `shaper_{source_stem}.html`; unsafe paths are rejected and collisions receive a deterministic source-ID suffix.
* FR-13: Generated artifacts pass the existing output-review gate before becoming published.
  * Observable acceptance criteria: Pre-transform authorization and post-output review use distinct records, services, and role checks. The same actor may perform both decisions in this development increment when assigned both roles; the platform makes no separation-of-duties claim.
* FR-14: REST resources expose the complete estate workflow with collection-scoped authorization.
  * Observable acceptance criteria: Estate, source, discovery, recommendation, decision, transformation, usage, and artifact operations enforce tenant and role boundaries. Browser principals resolve tenant and object IDs from Container Apps claims and load collection grants from PostgreSQL; existing bearer principals retain current role parsing.
* FR-15: The hosted experience supports estate list, estate definition, source management, discovery results, recommendation review, decisions, transformation progress, and artifact review.
  * Observable acceptance criteria: Every screen loads live server state, polls durable run resources, exposes partial results and retryable failures, and contains no fixed completion or connection claims.
* FR-16: Browser users authenticate interactively without access to client credentials.
  * Observable acceptance criteria: Azure Container Apps authentication establishes a same-origin identity from tenant and object claims; an Entra-assigned bootstrap administrator manages internal collection grants; a user or group with no grant receives 403; API and MCP bearer-token behavior remains compatible.
* FR-17: Administrators can archive or purge an estate.
  * Observable acceptance criteria: Archived estates remain readable but reject new sync, discovery, recommendation, decision, and transformation operations. Purge requires an administrator, current revision, and explicit confirmation; it deletes uploaded source bytes, derived artifacts, and content-bearing workflow records while retaining only a minimal non-content audit tombstone.

## Non-Functional Requirements

* NFR-01: Domain and application layers remain independent of infrastructure and interface packages.
  * Objective threshold or evaluation condition: Existing architecture dependency tests and new multi-agent boundary tests pass.
  * Observable acceptance criteria: No import from `shaper.infrastructure` or `shaper.interfaces` appears in domain or application modules.
* NFR-02: All mutable workflow resources use optimistic concurrency.
  * Objective threshold or evaluation condition: A stale expected revision fails every update and decision test.
  * Observable acceptance criteria: No last-write-wins update occurs for estates, recommendations, decisions, or review records.
* NFR-03: Workflow identity and outputs are reproducible.
  * Objective threshold or evaluation condition: Stable inputs, source versions, estimator version, model parameters, and naming policy yield stable IDs and artifact names.
  * Observable acceptance criteria: Determinism tests pass across repeated executions.
* NFR-04: Token estimates communicate uncertainty and enforce a hard ceiling.
  * Objective threshold or evaluation condition: Every expected range is ordered, the maximum is not below the upper estimate, and runtime usage cannot proceed past the cap.
  * Observable acceptance criteria: Budget-exhaustion tests fail closed with persisted diagnostic state. Retry creates a new estimate and requires a fresh approval while retaining prior estimates and usage.
* NFR-05: Untrusted files and archive contents remain isolated until validation and malware scanning complete.
  * Objective threshold or evaluation condition: Existing file limits remain active and ZIP expansion adds bounded entry, size, ratio, extension, encryption, traversal, and per-entry scanning checks.
  * Observable acceptance criteria: The complete malicious-archive test matrix passes.
* NFR-06: Estates and active workflow state survive service restart and Container Apps revision replacement.
  * Objective threshold or evaluation condition: Production uses PostgreSQL rather than container-local SQLite for workflow records.
  * Observable acceptance criteria: A deployment smoke test creates an estate and queued run, moves traffic to a new revision, and reads or resumes both records from PostgreSQL.
* NFR-07: Secrets and tokens remain outside browser storage, source code, logs, and workflow artifacts.
  * Objective threshold or evaluation condition: Browser authentication uses platform-managed sessions; database and model access use managed identity or existing Key Vault references.
  * Observable acceptance criteria: Security-sensitive logs and client assets contain no credentials or bearer tokens. Ingress principal headers are ignored unless trusted-ingress mode is explicitly enabled, are never merged with bearer claims, and a request presenting both identity modes is rejected.
* NFR-08: The hosted workflow receives standard-tier accessibility verification for changed surfaces.
  * Objective threshold or evaluation condition: Static checks block on decidable failures; keyboard, accessibility-tree/live-region, 200% zoom, 320-pixel reflow, text-spacing, target-size, contrast, and reduced-motion methods decide their applicable classes.
  * Observable acceptance criteria: No serious or critical static finding remains, all journeys complete by keyboard, focus is visible and not obscured, status changes are announced once, and adaptive-rendering checks pass. Browser and accessibility evidence is a one-time implementation gate recorded in the changes artifact; lack of a committed regression harness is accepted residual risk.
* NFR-09: Failures remain explicit and recoverable.
  * Objective threshold or evaluation condition: Connector, database, model, parsing, and publication failures produce non-success states with a retry or corrective action.
  * Observable acceptance criteria: No broad catch or success-shaped fallback appears in the new workflow.
* NFR-10: The current authenticated compile, review, query, MCP, health, and fixed-demo contracts remain compatible unless explicitly superseded.
  * Objective threshold or evaluation condition: Existing tests pass alongside new workflow tests.
  * Observable acceptance criteria: No pre-existing public contract is removed by this increment.
* NFR-11: Real content has an explicit lifecycle and development-environment classification.
  * Objective threshold or evaluation condition: Archive blocks new processing; purge removes content-bearing bytes and records; documentation permits only non-sensitive, tenant-approved test content until a formal privacy and production-readiness review.
  * Observable acceptance criteria: Archive and purge tests pass, and deployment documentation states retention, deletion, and acceptable-data limits.

## Acceptance Criteria

* AC-01: A signed-in user creates an estate named "HR Policies", sets `shaper_{source_stem}.html`, reloads the application, and sees the same estate and revision.
* AC-02: The user adds two individual files and one ZIP containing two supported files; the estate inventory shows four individual documents with stable source versions and scan evidence.
* AC-03: Unsafe ZIP fixtures are rejected before document creation and expose a specific failure reason.
* AC-04: A SharePoint URL resolves and synchronizes when Graph authorization is present; otherwise it displays `authorization_required` and no sample documents.
* AC-05: Discovery displays readiness, evidence coverage, effort, findings, and source provenance for every document, plus estate-level duplicate, contradiction, topic, authority, and cross-reference evidence.
* AC-06: Selecting two of four documents generates detailed proposals only for those two documents.
* AC-07: Each proposal displays estimated input and output ranges, expected total, hard cap, confidence, estimator version, and assumptions.
* AC-08: Approving one proposal and declining another creates a job only for the approved current source version.
* AC-09: Changing the approved source version before dispatch invalidates the authorization and creates no model call or artifact.
* AC-10: The completed run stores actual input and output tokens and variance from the retained estimate.
* AC-11: The approved output passes the separate output-review service and role check and publishes a hash-verified HTML artifact with the resolved safe name; the source remains unchanged.
* AC-12: The five specialist-agent outputs remain separately inspectable and the deterministic orchestrator retains all approval, budget, and publication authority.
* AC-13: Estate CRUD and all workflow operations reject cross-tenant and insufficient-role access.
* AC-14: The end-to-end hosted journey runs against live APIs, preserves an estate and queued run across a new Azure revision, and never substitutes the fixed demo for unavailable customer data.
* AC-15: The changed screens pass the one-time accessibility methods defined in NFR-08, including keyboard-only completion and announced asynchronous status.
* AC-16: Existing tests plus targeted domain, archive, assessment, token, decision, artifact, repository, API, architecture, `node --check prototype/copilot-studio-knowledge-compiler/app.js`, Bicep, shell, and deployment smoke checks pass.
* AC-17: An authenticated user with no collection grant receives 403 for estate operations, while a granted user receives only the configured collection roles.
* AC-18: An archived estate remains readable and rejects every new processing or decision operation.
* AC-19: An administrator-confirmed purge removes content-bearing estate records and stored bytes and leaves a non-content audit tombstone.
* AC-20: A budget-exhausted run cannot retry until a new estimate is generated and explicitly approved; both attempts remain auditable.

## Implementation Context Record

| Context item | Current artifact or record |
|---|---|
| Plan | .copilot-tracking/plans/2026-09-10/knowledge-estate-workflow-redesign-plan.md |
| Phase details | .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md |
| Latest critique | .copilot-tracking/reviews/plans/2026-09-10/knowledge-estate-workflow-redesign-plan-critique.md, Complete with Revise verdict; PC-001-PC-015 resolved in plan |
| Relevant research | .copilot-tracking/research/2026-09-10/knowledge-estate-workflow-redesign-research.md |
| Changes-record role | .copilot-tracking/changes/2026-09-10/knowledge-estate-workflow-redesign-changes.md is created by implementation |
| Planning execution and readiness | Complete and implementation-ready after direct critique corrections |
| Continuation context | Standalone manual RPI plan |

## Sources

* .copilot-tracking/research/2026-09-10/knowledge-estate-workflow-redesign-research.md: C1-C25 define gaps, reusable primitives, token accounting, alternatives, and the selected boundary.
* docs/architecture.md: Current C4 multi-agent responsibilities and deterministic platform controls.
* docs/deployment.md: Current Container Apps topology and non-durable SQLite limitation.
* User direction on 2026-09-10: Preserves the multi-agent architecture and requires per-transformation token estimates.
* Accessibility skill: Supplies method-adequacy requirements for interaction, announcement, and adaptive-rendering evidence.

## Phase Checklist

<!-- rpi:phase id=P01 -->
### [x] P01: Establish Estate Contracts and Multi-Agent Boundaries

* Intent: Define immutable workflow contracts and deterministic ownership before adding behavior.
* Dependencies: Completed research C1-C25

<!-- rpi:task id=P01-T01 -->
#### [x] P01-T01: Define the Knowledge Estate Domain

* Requirement and evidence: FR-01, FR-02, FR-05, FR-07-FR-13; research C1, C17-C20
* Expected result: Versioned domain contracts represent estates, sources, documents, reports, proposals, estimates, decisions, runs, usage, naming policies, and artifacts.
* Detail section: P01-T01 in .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md

<!-- rpi:task id=P01-T02 -->
#### [x] P01-T02: Define Repository and Orchestration Ports

* Requirement and evidence: FR-06, NFR-01-NFR-03; research C10, C12, C17
* Expected result: Application ports isolate persistence and make agent evidence ownership distinct from deterministic workflow authority.
* Detail section: P01-T02 in .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md

<!-- rpi:phase id=P02 -->
### [x] P02: Register Sources and Build the Document Inventory

* Intent: Populate estates from truthful, bounded source definitions.
* Dependencies: P01

<!-- rpi:task id=P02-T01 -->
#### [x] P02-T01: Implement Estate and Source Registration

* Requirement and evidence: FR-01-FR-03, FR-14; research C1, C2, C5
* Expected result: Estate services manage many typed sources, collection grants, archive and purge behavior, and explicit connector lifecycle states.
* Detail section: P02-T01 in .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md

<!-- rpi:task id=P02-T02 -->
#### [x] P02-T02: Implement Bounded Upload and ZIP Expansion

* Requirement and evidence: FR-04, NFR-05; research C6, C7
* Expected result: Uploaded files and safe ZIP entries become individually scanned, versioned estate documents.
* Detail section: P02-T02 in .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md

<!-- rpi:task id=P02-T03 -->
#### [x] P02-T03: Integrate SharePoint Synchronization

* Requirement and evidence: FR-03, AC-04; research C5, C17
* Expected result: Registered SharePoint sources use stable Graph IDs and delta checkpoints when authorized and report `authorization_required` otherwise.
* Detail section: P02-T03 in .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md

<!-- rpi:phase id=P03 -->
### [x] P03: Run Multi-Agent Discovery

* Intent: Produce per-document evidence and estate-level knowledge analysis without modifying content.
* Dependencies: P01-P02

<!-- rpi:task id=P03-T01 -->
#### [x] P03-T01: Produce Per-Document Readiness and Effort Reports

* Requirement and evidence: FR-05, NFR-03; research C3, C4, C17
* Expected result: Existing scoring signals are decomposed into immutable document reports with new long-paragraph, cross-reference, and explainable effort evidence.
* Detail section: P03-T01 in .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md

<!-- rpi:task id=P03-T02 -->
#### [x] P03-T02: Compose Estate-Level Specialist-Agent Results

* Requirement and evidence: FR-06, AC-05, AC-12; research C3, C18
* Expected result: A durable, pollable, deterministic run composes distinct results from all five agents while duplicate, contradiction, topic, authority, and governance relationships remain intact.
* Detail section: P03-T02 in .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md

<!-- rpi:phase id=P04 -->
### [x] P04: Recommend, Estimate, and Decide

* Intent: Turn selected discovery evidence into versioned proposals that users can approve before transformation.
* Dependencies: P01, P03

<!-- rpi:task id=P04-T01 -->
#### [x] P04-T01: Generate Selection-Scoped Recommendations

* Requirement and evidence: FR-07, research C18
* Expected result: A durable, pollable, deterministic Transformation Agent run proposes detailed changes only for selected current document versions without model calls.
* Detail section: P04-T01 in .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md

<!-- rpi:task id=P04-T02 -->
#### [x] P04-T02: Estimate and Cap Transformation Tokens

* Requirement and evidence: FR-08, NFR-04; research C20-C25
* Expected result: A deterministic estimator attaches transparent input/output ranges and a hard maximum to each proposal without model inference.
* Detail section: P04-T02 in .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md

<!-- rpi:task id=P04-T03 -->
#### [x] P04-T03: Record Pre-Transformation Decisions

* Requirement and evidence: FR-09, FR-10; research C9, C10
* Expected result: Version-pinned approve and decline decisions use role authorization and optimistic concurrency and invalidate on source, recommendation, estimator, or model-deployment change.
* Detail section: P04-T03 in .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md

<!-- rpi:phase id=P05 -->
### [x] P05: Transform Approved Content and Publish Artifacts

* Intent: Consume model resources only for approved current versions and publish reviewed derivatives.
* Dependencies: P01, P04

<!-- rpi:task id=P05-T01 -->
#### [x] P05-T01: Enforce Approved-Only Transformation

* Requirement and evidence: FR-10, NFR-04; research C8-C10, C20-C21
* Expected result: Job submission and dispatch fail before a model call when authorization is missing, declined, withdrawn, stale, or over budget; budget exhaustion requires a new estimate and approval.
* Detail section: P05-T01 in .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md

<!-- rpi:task id=P05-T02 -->
#### [x] P05-T02: Persist Actual Token Usage

* Requirement and evidence: FR-11; research C21-C24
* Expected result: Completed and failed runs retain provider-reported input/output usage, calls, cap, model provenance, and estimate variance.
* Detail section: P05-T02 in .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md

<!-- rpi:task id=P05-T03 -->
#### [x] P05-T03: Render, Review, and Publish Named HTML

* Requirement and evidence: FR-12, FR-13; research C11, C19
* Expected result: Safe deterministic names, immutable HTML bytes, hashes, provenance, and distinct output-review records and role checks extend the existing release; one actor may hold both roles in development.
* Detail section: P05-T03 in .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md

<!-- rpi:phase id=P06 -->
### [x] P06: Expose Durable APIs and the Live Product Experience

* Intent: Make the workflow persistent, authenticated, operable, and accessible.
* Dependencies: P01-P05

<!-- rpi:task id=P06-T01 -->
#### [x] P06-T01: Implement Local and Production Persistence

* Requirement and evidence: NFR-02, NFR-06; research C12, C13
* Expected result: SQLite supports local development and PostgreSQL supports durable Azure workflow state through the same repository contracts.
* Detail section: P06-T01 in .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md

<!-- rpi:task id=P06-T02 -->
#### [x] P06-T02: Add Authenticated Estate REST Resources

* Requirement and evidence: FR-14, NFR-07, NFR-10; research C2
* Expected result: Complete collection-scoped workflow APIs support bearer clients and same-origin Container Apps browser sessions backed by internal principal grants and fail-closed header trust.
* Detail section: P06-T02 in .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md

<!-- rpi:task id=P06-T03 -->
#### [x] P06-T03: Replace the Demo-First UI with Live Estate Screens

* Requirement and evidence: FR-15, FR-16; research C14-C16
* Expected result: Public static assets host a signed-out shell while all estate data and actions require a session; the authenticated workspace uses a compact Copilot Studio-like application shell with task-named tabs and durable deep links; durable run polling shows truthful loading, authorization, empty, partial, failure, retry, and completion states.
* Detail section: P06-T03 in .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md

<!-- rpi:task id=P06-T04 -->
#### [x] P06-T04: Verify Accessible Interaction Behavior

* Requirement and evidence: NFR-08, AC-15
* Expected result: One-time static and rendered methods adequately decide keyboard, focus, announcement, adaptive-rendering, contrast, target-size, and reduced-motion criteria for changed screens and record the accepted regression risk.
* Detail section: P06-T04 in .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md

<!-- rpi:phase id=P07 -->
### [ ] P07: Deploy and Prove the Azure Workflow

* Intent: Provision durable dependencies, deploy the feature, and verify persistence and end-to-end behavior.
* Dependencies: P01-P06

<!-- rpi:task id=P07-T01 -->
#### [ ] P07-T01: Provision PostgreSQL and Interactive Entra Authentication

* Requirement and evidence: NFR-06, NFR-07, FR-16
* Expected result: Bicep and deployment automation configure passwordless application data access, bootstrap-admin app-role assignment, internal collection grants, browser sessions, explicit anonymous paths, and existing API/MCP authentication compatibility.
* Detail section: P07-T01 in .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md

<!-- rpi:task id=P07-T02 -->
#### [x] P07-T02: Update Architecture and Operations Documentation

* Requirement and evidence: Multi-agent user decision, NFR-10
* Expected result: C4 diagrams, README, and deployment guidance describe durable estates, agent roles, run bounds, two approval gates, token accounting, content lifecycle, acceptable development data, public and protected paths, and truthful connector states.
* Detail section: P07-T02 in .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md

<!-- rpi:task id=P07-T03 -->
#### [ ] P07-T03: Run End-to-End Deployment Validation

* Requirement and evidence: AC-01-AC-20
* Expected result: Targeted tests, full regression, build checks, deployment smoke, estate and queued-run persistence across revision, and the hosted browser journey all pass.
* Detail section: P07-T03 in .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md

## Dependencies

* Microsoft Graph application permissions: Required for live SharePoint enumeration; until granted, source status remains `authorization_required`.
* Azure Database for PostgreSQL Flexible Server: Required for durable production workflow state.
* PostgreSQL Entra administrator and managed-identity principal bootstrap: Required for passwordless application access.
* Azure Container Apps authentication configuration: Required for same-origin browser sessions while preserving API/MCP bearer access.
* Entra bootstrap-administrator app-role assignment: Required for an interactive tenant administrator to create internal principal or group collection grants.
* Existing Azure OpenAI deployment: Required only after a current approved proposal passes the pre-transform gate.
* Existing ClamAV service: Required for every uploaded file and expanded ZIP entry.

## Locked Implementation Boundaries

### Test Ownership

* New domain invariants: tests/test_estate_domain.py
* Estate services and multi-agent workflow: tests/test_estates.py and existing tests/test_orchestration.py
* ZIP boundaries: tests/test_archive.py plus existing tests/test_ingestion.py, tests/test_compilation.py, and tests/test_interfaces.py
* Document scoring: existing tests/test_assessment.py
* Token estimator: tests/test_token_estimation.py
* Pre-transform decisions: tests/test_decisions.py and existing tests/test_jobs_auth.py
* Artifact rendering and naming: tests/test_artifacts.py and existing tests/test_publication.py
* Actual token usage: existing tests/test_compilation.py
* Repository contract and PostgreSQL adapter: tests/test_estate_repository.py and existing tests/test_sqlite.py
* HTTP and authentication: existing tests/test_interfaces.py
* Architecture and documentation invariants: existing tests/test_architecture.py
* Hosted UI JavaScript and accessibility: `node --check prototype/copilot-studio-knowledge-compiler/app.js` plus one-time browser-based static, interaction, accessibility-tree, and adaptive-rendering verification recorded in the changes artifact
* Azure resources and deployment: existing Bicep compilation, shell syntax check, and scripts/deploy.sh smoke flow

### Exact Removals

* No source or test file is removed.
* The dead `href="#"` Knowledge Estates navigation behavior is replaced with a working screen transition.
* The hosted product experience stops treating `GET /v1/demo/analysis` as its primary workflow. The endpoint remains for fixed-sample smoke and compatibility use.
* The deployment documentation statement that container-local SQLite is the active workflow store is superseded after PostgreSQL deployment.

### Maximum Additions

* At most seven new production modules: src/shaper/domain/estate.py, src/shaper/application/estates.py, src/shaper/application/token_estimation.py, src/shaper/application/decisions.py, src/shaper/application/artifacts.py, src/shaper/infrastructure/archive.py, and src/shaper/infrastructure/postgres.py.
* At most seven focused new test modules corresponding to the new concerns listed under Test Ownership.
* No new frontend framework. The current HTML, CSS, and JavaScript application remains the product surface.
* No new accessibility framework is added. Existing browser tooling and the accessibility method-adequacy contract provide verification.

### Canonical and Generated Targets

* PostgreSQL is canonical in production for internal collection grants, estates, sources, documents, connector checkpoints, discovery and recommendation runs, document reports, recommendations, pre-transform decisions, compile jobs, candidates, review records, shaping checkpoints, outbox events, agent runs, token usage, artifact manifests, and current release pointers. SQLite implements the same record families for local development.
* Uploaded source bytes, quarantine assets, immutable release bytes, and HTML artifact bytes remain in the configured Azure Files asset store; PostgreSQL stores their metadata, hashes, and locators.
* Source documents and versions remain immutable evidence.
* Recommendation decisions and output-review decisions are separate canonical records.
* Token estimates and actual usage are separate immutable records.
* HTML artifacts and their manifest entries are generated, hash-verified derivatives.
* The current JSONL release remains a compatible generated projection.

### Semantic and Regression Coverage

* Semantic tests cover aggregate invariants, version pinning, role boundaries, state transitions, estimate mathematics, archive safety, naming, and agent ownership.
* Regression tests retain current compile, review, query, MCP, health, assessment, demo, architecture, and deployment behavior.
* One-time browser verification covers the real user journey and cannot be replaced by static HTML inspection for keyboard, focus, announcements, or reflow. A repeatable committed browser harness remains follow-up work.

### Validation Evidence

* Targeted pytest selections for every changed Python concern
* Full existing test suite and coverage threshold
* Ruff and strict mypy
* `node --check prototype/copilot-studio-knowledge-compiler/app.js`
* Bicep compilation and shell syntax
* Browser checks at keyboard-only, accessibility tree, 200% zoom, 320-pixel reflow, text-spacing, reduced-motion, and representative viewport sizes
* Authenticated REST and MCP smoke tests
* Estate and queued-run persistence plus expired-lease recovery across an Azure revision change
* Live hosted workflow from estate creation through artifact retrieval

## Critique Disposition

| Critique run and finding | Disposition | Plan response or residual risk |
|---|---|---|
| PC-001 | Resolved | Browser tenant and object claims map through PostgreSQL collection grants; bootstrap administration and no-grant 403 behavior are explicit. |
| PC-002 | Resolved | Discovery and recommendation are durable pollable runs bounded to 500 and 100 documents respectively. |
| PC-003 | Resolved | Test ownership now uses existing ingestion, compilation, and interface tests without exceeding the seven-test cap. |
| PC-004 | Resolved | Discover and Recommend are deterministic and assert zero model calls in this increment. |
| PC-005 | Resolved | Every PostgreSQL-canonical record family and Azure Files byte family is enumerated; queued-run recovery is acceptance evidence. |
| PC-006 | Resolved | Output-review independence means a separate record, service, and role check; the same development actor may hold both roles. |
| PC-007 | Resolved | Budget exhaustion creates a new estimate and requires fresh approval before retry. |
| PC-008 | Resolved with accepted residual risk | JavaScript uses an exact `node --check` command; browser accessibility evidence is a one-time implementation gate without a committed regression harness. |
| PC-009 | Resolved | Public static, health, and fixed-demo paths are separated from protected estate data and actions; hosted.py is assigned in phase details. |
| PC-010 | Resolved | Ingress identity headers are ignored outside trusted mode, never merged, and conflict with bearer identity fails closed. |
| PC-011 | Resolved | PostgreSQL adapter branches remain inside coverage and use adapter-level fakes plus a disposable integration service when available. |
| PC-012 | Resolved | Archive and administrator-confirmed purge are in scope; development accepts only non-sensitive tenant-approved test content pending formal privacy review. |
| PC-013 | Resolved | Estimator-version and model-deployment changes invalidate approval and block dispatch. |
| PC-014 | Resolved | Phase details target the existing bicep/dev.bicepparam file. |
| PC-015 | Resolved | Archived estates are read-only and reject all new processing and decisions. |

## Follow-Up Items

* Add authenticated general web, Confluence, ServiceNow, wiki, file-share, and legacy intranet connectors after separate connector threat models and contracts.
* Calibrate readiness and effort scores against representative human-reviewed estates before using them in outcome claims.
* Calibrate token-estimate ranges by model and transformation kind after sufficient actual usage exists.
* Evaluate PostgreSQL scaling, retention, backup, and disaster-recovery objectives before production launch.
* Add a committed browser and accessibility regression harness after the initial live workflow is stable.

## Handoff

* Implementation artifact: .copilot-tracking/changes/2026-09-10/knowledge-estate-workflow-redesign-changes.md
* Ready phase or task: P01
* Remaining provisional question or blocker: None
