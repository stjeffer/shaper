# Changes: Shaper Multi-Agent Platform Architecture

## Scope

Implemented the full approved plan for task
`shaper-multi-agent-platform-architecture`. The increment establishes an
executable platform-versus-agent boundary without deploying new Azure resources.

## Platform Contracts and Orchestration

Completed `P01-T01`, `P01-T02`, and `P01-T03`.

* Added strict, frozen, content-addressed domain contracts for the five
  specialist roles and their coordinated analysis.
* Added role-specific dimension invariants and a shared assessment-identity invariant.
* Added the synchronous, stateless `KnowledgeTransformationOrchestrator`.
* Added deterministic Assessment, Knowledge, Transformation, Governance, and
  Agent Readiness services over one immutable assessment.
* Kept transformation output proposal-only and reported estate-wide execution
  as unavailable.
* Reported recurring governance scheduling as unconfigured.
* Added orchestration tests for role completeness, evidence identity,
  determinism, approvals, governance posture, and tamper detection.

## REST and Schema Boundary

Completed `P02-T01`, `P02-T02`, `P02-T03`, and `P02-T04`.

* Added authenticated `POST /v1/platform/analyses`.
* Reused one `EstateAssessmentService` implementation across the assessment and
  platform-analysis surfaces.
* Composed the orchestrator in the hosted CLI service.
* Registered the platform aggregate and regenerated the canonical JSON Schema.
* Added interface tests for authentication rejection, all five roles, and equal
  assessment identity across both endpoints.
* Preserved `POST /v1/assessments` and all existing API behavior.

## Architecture and Product Surfaces

Completed `P03-T01`, `P03-T02`, and `P03-T03`.

* Added C4 System Context, Container, and Shaper API and Orchestrator Component
  diagrams using the required Mermaid flowchart conventions.
* Distinguished the current single-container MVP from planned specialist
  workers, PostgreSQL, Blob Storage, Azure AI Search, and product clients.
* Documented that Shaper is not an agent, the Knowledge Agent is the central
  understanding role, and SharePoint is a surface rather than the platform boundary.
* Documented agent responsibility boundaries, product-surface priority, and
  continuous-governance limitations.
* Updated the hosted concept with five specialist cards, a governance navigation
  surface, platform positioning, and agent-specific progress announcements.
* Preserved 320-pixel reflow, reduced-motion behavior, live status, and heading focus.

## Validation

Completed `P04-T01` and `P04-T02`.

* Ruff format check passed for 67 files.
* Ruff lint passed.
* Strict mypy passed for 67 source files.
* Full pytest passed: 105 tests.
* Coverage passed at 79.07% against the required 75%.
* Both schema check entry points passed.
* JavaScript syntax passed.
* Bicep compilation passed.
* Git diff hygiene passed.
* Focused platform, interface, and architecture tests passed: 25 tests.
* Browser validation confirmed five agent cards and no horizontal overflow at
  320 pixels (`scrollWidth` 305, `clientWidth` 305).
* Reduced-motion interaction reached Understand, moved focus to its heading, and
  announced phase 2 of 4.
* C4 source validation passed through renderer-convention architecture tests and
  rule-by-rule inspection.
* Mermaid CLI render validation was not run because `mmdc` is unavailable and no
  new validation dependency was added.

## Plan Reconciliation

All full-plan tasks have implementation and validation evidence. No plan
divergence, source removal, Azure deployment, source overwrite, or recurring
governance claim was introduced.

## Follow-Up Work

* Add durable Discover-to-Govern workflow state and managed scheduling.
* Deploy specialist roles independently only when workload evidence justifies it.
* Build Copilot, SharePoint, Teams, and Foundry clients in the confirmed order.

## Azure Deployment

The user explicitly requested deployment after the implementation Review.

* Deployed image
  `crshaperdevi5e45vhjjbud6.azurecr.io/shaper:20260910100733`
* Deployed revision `ca-shaper-dev--0000013`
* Routed 100% of traffic to the healthy revision
* Preserved the service URL and `/concept/` product experience
* Verified liveness, readiness, MCP initialization, OpenAPI, the legacy
  assessment API, and authenticated `POST /v1/platform/analyses`
* Verified all five specialist roles, shared assessment identity,
  proposal-only transformation, unavailable estate-wide execution, and
  unconfigured recurring governance
* Corrected the deployment collection to `faqifier`, matching the Entra
  collection-scoped roles
* Deleted every temporary smoke-client credential after use

## Live Testable Concept

Completed the requested hosted UI follow-up.

* Added public, read-only `GET /v1/demo/analysis` over fixed server-owned sample
  profiles
* Reused the production `KnowledgeTransformationOrchestrator` without exposing
  caller-supplied content or weakening the authenticated analysis endpoint
* Replaced the timed UI simulation with live API rendering for readiness,
  evidence coverage, dimensions, findings, topics, and transformation proposals
* Added visible, announced failure handling and a retryable assessment action
* Preserved the proposal-only transformation and human approval boundary
* Added endpoint coverage for configured, unavailable, and deterministic
  responses
* Passed Ruff, strict mypy, schema validation, JavaScript parsing, Bicep
  compilation, diff hygiene, and all 106 tests with 79.16% coverage
* Verified live rendering, keyboard focus movement, live-region announcements,
  retry behavior, reduced-motion behavior, and 320-pixel reflow without
  horizontal overflow
* Deployed image
  `crshaperdevi5e45vhjjbud6.azurecr.io/shaper:20260910103126`
* Deployed healthy revision `ca-shaper-dev--0000014` with 100% traffic
* Verified live readiness, the public sample endpoint, the full concept journey,
  MCP initialization, and temporary credential removal

The standalone axe CLI could not run because no system Chrome binary is
installed. The integrated browser accessibility-tree and interaction checks
passed, and an earlier static concept scan reported zero axe violations.

## Live Source Evidence Correction

Removed the remaining mocked connector state after live testing identified that
the Discover source cards still claimed static SharePoint and OneDrive
connections.

* Changed the public sample response to pair its analysis with the exact three
  fixed source records used as orchestrator input
* Replaced hard-coded Connected labels, Connect buttons, and the 396-document
  count with API-backed titles, owners, modification dates, authority states,
  and source count
* Added honest loading and unavailable states with `aria-busy`, live-region
  announcements, and retry behavior
* Preserved the full assessment, recommendation, and approval journey
* Passed all 106 tests with 79.24% coverage, Ruff, mypy, JavaScript parsing,
  shell syntax, diff hygiene, and local browser validation
* Confirmed zero Connected labels and zero Connect buttons in the rendered
  local and Azure experiences
* Corrected the deployed Entra JWT audience from the identifier URI to the API
  application UUID after reproducing the client-credential token mismatch
* Hardened deployment smoke authentication by passing the bearer header through
  a protected temporary file
* Deployed healthy revision `ca-shaper-dev--0000016` with 100% traffic
* Verified the public source response, authenticated platform analysis, MCP
  initialization, liveness, readiness, and temporary credential removal
