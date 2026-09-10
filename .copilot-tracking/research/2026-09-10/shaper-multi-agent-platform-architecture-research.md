<!-- markdownlint-disable-file -->
# Research: Shaper Multi-Agent Platform Architecture

## Research Brief

* Topic: Reframe and develop Shaper as a platform that orchestrates five
  specialized knowledge agents.
* Purpose: Translate the caller's authoritative architecture guidance into an
  executable application boundary and durable C4 architecture.
* Audience and use: Product engineering, Azure architecture, API consumers, and
  subsequent implementation.
* Scope: Platform and agent boundaries, deterministic orchestration, API and
  schemas, current versus target architecture, product positioning, and tests.
* Non-goals: SPFx implementation, production connector provisioning,
  distributed worker provisioning, autonomous source overwrite, or replacing
  the current transformation kernel.
* Output mode: Convergence.
* Research posture: Balanced because the caller supplied the target model, but
  the current monolithic assessment boundary needs architectural decomposition.
* Interaction: Skipped because the brief explicitly resolves the product,
  system, surface, agent, and workflow decisions needed for this increment.

## Extensions and Participation

* C4 architecture: selected for System Context, Container, and Orchestrator
  Component views using Mermaid flowcharts.
* RPI research: selected for current-to-target evidence and readiness.
* Python guidance: selected for typed contracts and dependency direction.
* Accessibility: retained for any product-surface changes.
* Deployment diagram: not included in this increment. Infrastructure evidence
  exists, but the caller requested architectural steering rather than a
  deployment diagram and the current and target topologies already coexist.
  Current versus planned deployment remains explicit in prose.
* External research: skipped. The caller's brief is authoritative and the
  implementation question is repository-internal.
* Delegation: skipped because this is one continuous architecture chain over a
  small application boundary.

## Questions

* Q1: Which current capabilities map to each specialized agent?
* Q2: What must remain deterministic platform responsibility?
* Q3: What is the smallest executable increment that establishes the architecture?
* Q4: How should current and planned elements be represented without overstating deployment?

## Cycle 1

### Wider wave

The current service already contains most capability kernels but presents them
as unrelated services:

* EstateAssessmentService calculates content quality, knowledge quality, and
  agent readiness in one method.
* CompilationService runs the bounded model-assisted shaping loop and enforces
  independent review before publication.
* ReviewService and deterministic validation provide governance controls.
* HTTP, MCP, CLI composition, and job dispatch form a platform shell.
* SourceConnector, ModelGateway, Validator, storage, index, identity, and
  transaction protocols already preserve ports-and-adapters boundaries.

The missing architecture is an explicit platform orchestrator and typed
specialized-agent outputs. Without them, the code and API can still be read as
one assessment service plus one shaping agent rather than a platform coordinating
separate responsibilities.

### Deeper wave

* C1: src/shaper/interfaces/cli.py:113 composes HTTP, MCP, assessment, compilation,
  identity, storage, and workers in one hosted Azure service. This is the current
  platform composition root.
* C2: src/shaper/application/assessment.py:41 currently owns audit metrics,
  knowledge topics, contradiction candidates, readiness, and recommendations.
  It provides reusable evidence but does not expose agent responsibility boundaries.
* C3: src/shaper/application/compiler.py:88 is the current Transformation Agent
  kernel: it uses a bounded model loop, validates output, submits independent
  review, and publishes only after approval.
* C4: src/shaper/application/review.py and
  src/shaper/application/validation.py provide current Governance Agent
  mechanisms for candidate validation, review, and approval.
* C5: src/shaper/application/ports.py:54 defines provider-neutral boundaries for
  sources, models, validation, evaluation, storage, indexes, identity, and
  transactions. The orchestrator can depend inward on typed application
  services without coupling to Azure adapters.
* C6: src/shaper/domain/assessment.py:211 already provides immutable,
  content-addressed assessment evidence with coverage, findings, topics,
  recommendations, and human-approval semantics.
* C7: prototype/copilot-studio-knowledge-compiler/index.html currently presents
  Discover, Understand, Recommend, and Transform and explicitly stops at approval.
* C8: docs/deployment.md distinguishes the current single-container development
  topology from the planned worker, Service Bus, PostgreSQL, and connector
  topology.

### Contrarian wave

* Reject making the platform orchestrator an LLM agent. Workflow control,
  authorization, budgets, evidence lineage, approval, retries, and publication
  must remain deterministic application responsibilities.
* Reject five independent model deployments in the first increment. Specialized
  responsibility boundaries are required now; deployment isolation can follow
  when workload and scaling evidence justify it.
* Reject splitting the existing assessment algorithm immediately. It is
  deterministic, tested evidence generation. Specialized agents can initially
  produce typed responsibility-specific views over one immutable assessment,
  avoiding duplicated calculations and inconsistent scores.
* Reject representing SharePoint as the system boundary. It is an external
  source and delivery surface; the Azure service remains the product.
* Reject claiming Governance Agent continuity is already scheduled. Current
  governance output can identify monitoring candidates, while recurring scans
  and managed scheduling remain planned capabilities.
* Reject a current-state deployment diagram that includes Service Bus and
  PostgreSQL. Those resources are target architecture only.

## Synthesis

### Selected architecture

Create a deterministic `KnowledgeTransformationOrchestrator` inside the
application layer. It generates one immutable assessment and coordinates five
specialized agents:

* Assessment Agent returns content-health dimensions and audit findings.
* Knowledge Agent returns topics, overlap, contradiction, duplicate, and
  authority evidence.
* Transformation Agent returns human-approval-required transformation proposals.
* Governance Agent returns current monitoring controls and unresolved governance
  findings without claiming a recurring scheduler.
* Agent Readiness Agent returns the readiness score, readiness dimension,
  coverage, limitations, and prioritized interventions.

The orchestrator returns one typed `KnowledgeTransformationAnalysis`, exposed
through authenticated REST and the generated domain schema. The existing
assessment and compilation APIs remain compatible.

### C4 model decision

Produce planned-platform System Context and Container views plus an Orchestrator
Component view. Mark target-only containers and integrations as planned. Do not
produce a deployment diagram in this increment. The architecture document must
also state the current implementation mapping so readers cannot mistake all
planned containers for deployed resources.

### Alternatives

* Keep only documentation: rejected because the code would continue to obscure
  the platform and agent boundaries.
* Refactor every capability into separate processes now: rejected because
  current workloads, state, and deployment evidence do not justify that
  operational complexity.
* Make each phase a separate agent: rejected because Recommend is a workflow
  phase, while agent responsibilities cut across phases.

## Risks

* Agent outputs can become duplicated projections if they copy rather than
  reference immutable assessment evidence.
* Naming every deterministic specialist an agent may imply autonomous LLM
  behavior. Contracts and documentation must state that an agent is a bounded
  capability role and may be deterministic or model-assisted.
* Governance output must not imply continuous scheduling until managed workers
  exist.
* Target diagrams must visibly distinguish planned elements from the deployed MVP.

## Research Disposition

* Research disposition: Executed one balanced wider, deeper, and contrarian cycle.
* Planning Readiness: Ready.
* Re-entry decision: No additional cycle. The brief resolves architectural intent,
  current kernels are mapped, and the selected increment has bounded code,
  documentation, API, schema, and validation surfaces.
* Blockers: None.
