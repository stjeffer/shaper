# Shaper Multi-Agent Platform Architecture Plan

**Task ID:** `shaper-multi-agent-platform-architecture`

## Executive Summary

Establish Shaper in code and documentation as a deterministic Azure-native
platform orchestrating five bounded specialist agents. Add immutable typed agent
outputs, a platform analysis aggregate, an application orchestrator, and an
authenticated REST endpoint while preserving the existing assessment and
compilation contracts. Document planned C4 System Context, Container, and
Orchestrator Component views, clearly separating deployed MVP capabilities from
planned distributed containers. Update the hosted concept to show Shaper as the
platform and governance as a continuous loop. Do not build SPFx, deploy new
Azure resources, or allow autonomous source mutation.

## Sources

* Caller-provided Shaper Architecture Guidance, 2026-09-10
* `.copilot-tracking/research/2026-09-10/shaper-multi-agent-platform-architecture-research.md`
* `src/shaper/application/assessment.py`
* `src/shaper/application/compiler.py`
* `src/shaper/application/ports.py`
* `src/shaper/interfaces/cli.py`
* `docs/deployment.md`

## User Decisions and Requirements

* Shaper is not an agent; it is an Azure-native Knowledge Transformation Platform.
* Shaper orchestrates Assessment, Knowledge, Transformation, Governance, and
  Agent Readiness agents.
* The Knowledge Agent is the heart of knowledge understanding.
* Transformations are proposals and never overwrite source content automatically.
* The platform workflow is Discover, Understand, Recommend, Transform, with
  continuous governance.
* SharePoint is a dashboard and integration surface, not the product boundary.
* Surface priority is Azure platform, REST API, Copilot Agent, SharePoint, Teams,
  then Foundry.
* Preserve existing capabilities and develop against the new architecture.

## Goals

* Make the platform-versus-agent boundary executable and testable.
* Provide typed, immutable outputs for all five specialized agents.
* Keep orchestration, authorization, evidence lineage, and approval deterministic.
* Preserve the current assessment, compilation, review, query, and MCP behavior.
* Publish evidence-backed C4 architecture with current/planned distinctions.

## Scope and Non-Goals

In scope:

* Domain contracts for agent roles and coordinated platform analysis.
* Bounded specialist application services and deterministic orchestration.
* Authenticated REST exposure and generated JSON Schema.
* Product concept and architecture documentation.
* Unit, interface, architecture, schema, and accessibility-safe regression checks.

Out of scope:

* Separate runtime deployments for each agent.
* SPFx, Teams, Copilot, or Foundry client implementation.
* Production connectors, Service Bus, PostgreSQL, or recurring schedules.
* Autonomous source modification or publication.
* Azure deployment of this increment.

## Functional Requirements

* FR1: One synchronous, stateless platform analysis coordinates all five named
  specialist roles. Durable multi-phase workflow state remains follow-up work.
* FR2: Every agent output references the same immutable assessment identity.
* FR3: Assessment output exposes content-health evidence.
* FR4: Knowledge output exposes topic, overlap, duplicate, contradiction, and
  authority evidence.
* FR5: Transformation output contains proposals whose approval requirement is
  invariant and explicitly reports proposal-only and execution-availability state.
* FR6: Governance output identifies monitored conditions and explicitly reports
  that recurring monitoring is not configured.
* FR7: Agent Readiness output exposes score, coverage, readiness metrics,
  limitations, and prioritized interventions.
* FR8: Existing `POST /v1/assessments` behavior remains compatible.
* FR9: A new authenticated platform-analysis endpoint returns the aggregate
  without implying a persisted workflow run.

## Non-Functional Requirements

* NFR1: Domain models remain strict, frozen, content-addressed, and provider-neutral.
* NFR2: Application and domain layers do not import infrastructure or interfaces.
* NFR3: The orchestrator has no model, cloud, or persistence dependency.
* NFR4: No output claims continuous scheduling, accuracy, or autonomous authority.
* NFR5: Documentation and UI distinguish deployed MVP from planned architecture.
* NFR6: UI changes retain existing keyboard, focus, reduced-motion, and reflow behavior.

## Acceptance Criteria

* AC1: Tests prove the aggregate contains exactly five unique agent roles.
* AC2: Tests prove every output shares the aggregate assessment ID.
* AC3: Tests prove transformation proposals always require approval.
* AC4: Tests prove governance scheduling is reported as unconfigured.
* AC5: Existing assessment and HTTP tests pass unchanged.
* AC6: New endpoint rejects unauthenticated access and returns deterministic output.
* AC7: Generated schema contains the platform aggregate.
* AC8: A compatibility test proves the assessment and analysis endpoints produce
  the same assessment identity from the same inputs.
* AC9: C4 source passes renderer rule review and Mermaid parse validation when a
  repository-available validator supports the syntax.
* AC10: Ruff, strict mypy, targeted tests, full tests, schema check, JavaScript
  parsing, and Bicep build pass.

## Phase Checklist

<!-- phase:P01 -->
## P01 - Define Platform Contracts and Orchestration

* [x] `P01-T01` Add immutable agent-role and platform-analysis contracts.
* [x] `P01-T02` Add five bounded specialist services and the deterministic
  Knowledge Transformation Orchestrator.
* [x] `P01-T03` Add focused orchestration tests.

<!-- phase:P02 -->
## P02 - Expose the Platform Boundary

* [x] `P02-T01` Add the authenticated platform-analysis HTTP endpoint.
* [x] `P02-T02` Compose the orchestrator in the hosted service.
* [x] `P02-T03` Register and regenerate the public schema.
* [x] `P02-T04` Add interface and compatibility tests.

<!-- phase:P03 -->
## P03 - Align Architecture and Product Surfaces

* [x] `P03-T01` Add C4 System Context, Container, and Orchestrator Component
  diagrams using Mermaid flowchart syntax.
* [x] `P03-T02` Update README and deployment guidance with agent boundaries,
  current/planned distinctions, surface priority, and governance loop.
* [x] `P03-T03` Update the hosted concept to present the platform and five agents.

<!-- phase:P04 -->
## P04 - Validate the Increment

* [x] `P04-T01` Run formatting, lint, strict typing, targeted and full tests,
  schema checks, JavaScript parsing, Bicep build, and Mermaid validation.
* [x] `P04-T02` Reconcile documentation, generated artifacts, changed files,
  and the implementation record.

## Test Ownership and Change Limits

* Semantic behavior: `tests/test_orchestration.py` and focused HTTP tests.
* Regression behavior: existing assessment, interface, architecture, and schema tests.
* Exact removals: none.
* Maximum new production modules: two (`domain/platform.py`,
  `application/orchestration.py`).
* Canonical schema source: Python domain models.
* Generated target: `schemas/v1/domain.schema.json`.

## Risks and Mitigations

* Agent projections could diverge from assessment evidence: derive all outputs in
  one call from one immutable assessment.
* Agent naming could imply all roles are LLMs: document agents as bounded
  capability roles that may be deterministic or model-assisted.
* Governance could overstate current behavior: include explicit scheduling state.
* C4 diagrams could mix implementation states: label every target-only element planned.

## Critique Disposition

* Critique execution: Complete.
* Verdict: Revise, resolved by direct planner corrections.
* PC-001: Applied. Analysis terminology and the synchronous, stateless current
  boundary are explicit.
* PC-002: Applied. Transformation output must expose proposal-only and execution
  availability state.
* PC-003: Applied. Both API surfaces use one assessment service implementation,
  and compatibility testing compares their assessment identity.
* Final readiness: Implementation ready; no user decision or second critique required.

## Follow-Up Items

* Deploy each agent as an independent worker only after scaling and isolation
  evidence supports that operational boundary.
* Add recurring governance schedules with managed state and durable checkpoints.
* Build Copilot, SharePoint, Teams, and Foundry clients in the confirmed surface order.
* Deploy this increment after explicit approval for the externally visible action.

## Handoff

Implementation is complete and validated. Review the full increment using
`.copilot-tracking/changes/2026-09-10/shaper-multi-agent-platform-architecture-changes.md`
as the evidence record.
