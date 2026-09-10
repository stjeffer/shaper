# Shaper Multi-Agent Platform Architecture Phase Details

**Task ID:** `shaper-multi-agent-platform-architecture`

<!-- phase:P01 -->
## P01 - Define Platform Contracts and Orchestration

### P01-T01 - Add immutable contracts

Create strict frozen domain models for agent identity, each responsibility-specific
output, and one content-addressed aggregate. Reuse assessment-domain types rather
than copying evidence. Validate exactly one output for each required role and a
single shared assessment ID.

### P01-T02 - Add specialist services and orchestrator

The synchronous, stateless orchestrator uses one injected
`EstateAssessmentService` to create an `EstateAssessment`, then coordinates five
deterministic specialist services that project responsibility-specific views.
The orchestrator, not any specialist, controls execution order and aggregation.
The Transformation Agent reports that outputs are proposal-only and whether
execution is currently available; publication stays in the existing
human-approved compilation workflow.

### P01-T03 - Test orchestration

Cover role completeness, evidence identity, deterministic content addressing,
finding classification, approval invariants, governance scheduling posture, and
invalid aggregate rejection.

<!-- phase:P02 -->
## P02 - Expose the Platform Boundary

### P02-T01 - Add HTTP endpoint

Add an authenticated request using the existing bounded profile input and return
the aggregate. Reuse the existing strict JSON validation pattern and error
translation. Keep `POST /v1/assessments` unchanged.

### P02-T02 - Compose hosted service

Add an optional orchestrator dependency to `HttpServices` and wire the production
composition root with deterministic specialists. No Azure adapter is needed.

### P02-T03 - Register schema

Register the aggregate and any public request-relevant models in `schema.py`,
regenerate the canonical JSON Schema, and preserve schema drift checks.

### P02-T04 - Test interface compatibility

Verify authentication, success output, deterministic repeated calls, invalid
input translation, continued assessment endpoint behavior, and equal assessment
identity across the assessment and analysis endpoints for identical input.

<!-- phase:P03 -->
## P03 - Align Architecture and Product Surfaces

### P03-T01 - Add C4 diagrams

Use Mermaid `flowchart` C4 conventions. The System Context view shows enterprise
knowledge practitioners and agent builders using Shaper, with content systems as
sources and consuming agent/search platforms as delivery dependencies. The
Container view separates the current API/orchestrator from planned workers,
managed workflow state, durable knowledge assets, source connectors, and search
projection. The Component view details deterministic orchestration and the five
specialist roles. Do not create a deployment diagram.

### P03-T02 - Update platform documentation

State “Shaper is not an agent” prominently. Document role boundaries, current
implementation mapping, target operational decomposition, surface priority,
human approval, and continuous governance limitations.

### P03-T03 - Update hosted concept

Retain the four transformation phases but present Shaper as the platform
coordinating five specialist agents. Add the governance loop without claiming
scheduled monitoring. Preserve all accessibility behavior.

<!-- phase:P04 -->
## P04 - Validate the Increment

### P04-T01 - Run repository validation

Run existing Ruff, mypy, pytest, schema, JavaScript syntax, and Bicep commands.
Use Mermaid CLI only if already available or executable without adding a project
dependency. Otherwise perform renderer rule-by-rule source validation and report
the renderer limitation.

### P04-T02 - Reconcile evidence

Confirm all acceptance criteria against actual outputs, update plan checkboxes,
record divergence and validation evidence, and prepare the one post-implementation
review boundary.
