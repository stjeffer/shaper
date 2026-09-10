<!-- markdownlint-disable-file -->
# RPI Plan: Agentic Answer-Shaped Knowledge Compiler

## Task Metadata

* Task ID: answer-shaped-knowledge-mcp
* Task slug: answer-shaped-knowledge-mcp
* Planning status: Ready
* Plan date: 2026-09-09
* Phase details: .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md
* Plan critique: .copilot-tracking/reviews/plans/2026-09-09/answer-shaped-knowledge-mcp-plan-critique.md

## Executive Summary

This plan builds a new Python service that compiles policy documents, FAQs, and
similar source material into versioned, answer-ready evidence units. It accepts
a SharePoint document-library URL or a secured direct upload, preserves exact
source spans, uses one bounded AI agent for semantic shaping, validates every
candidate, publishes immutable releases to SharePoint or a configured
filesystem root, and exposes compile, query, explanation, status, and evidence
operations through MCP. The primary delivery includes a container image,
Azure Container Apps hosting, managed identity, persistent state, monitoring,
infrastructure-as-code, and a repeatable deployment and smoke-test workflow.

The architecture is deliberately hybrid. AI decides how to decompose a source,
identify claims, preserve qualifiers, follow cross-references, and repair
rejected drafts. Deterministic code owns source identity, tool permissions,
budgets, workflow state, validation, approval, indexing, and publication. The
agent never receives source mutation or publication credentials.

### User Decisions and Requirements Highlights

* Answer shaping is an agentic AI capability, not a deterministic text transform.
* Inputs include SharePoint document-library URLs and direct uploads.
* Callers choose the output location, with SharePoint preferred for governed access and native history.
* Evidence units remain derivatives. Authoritative source spans and complete provenance are retained.
* MCP is the agent-facing orchestration and query boundary, not the binary upload or storage layer.
* Hosting and deployment are a primary deliverable, not a later operational add-on.

### What You May Not Know

* Exact regeneration is not guaranteed because model output is probabilistic.
  Reproducibility is provided through immutable inputs and outputs, pinned
  configuration, complete run traces, and regression comparison.
* The first production policy defaults generated units to human review until a
  representative, subject-matter-reviewed evaluation set establishes safe
  automatic-publish thresholds.
* The initial implementation uses one agent and a transparent bounded loop.
  Multi-agent orchestration, OCR, GraphRAG, and a production vector backend are
  deferred until measured need justifies their complexity.

### Unresolved Decisions or Blockers

* No blocker prevents implementation.
* The initial authorization model is collection-scoped. OIDC-authenticated
  principals receive explicit collection roles, and each collection must map to
  a permission-homogeneous SharePoint root. Per-user SharePoint permission
  trimming is a later capability rather than an implicit promise.
* Live SharePoint, model, and evaluator checks require a test tenant, app
  registration, and configured deployments. Tests are authored with fakes and
  skip explicitly when these external prerequisites are absent.
* Quality thresholds for automatic publication remain disabled until the
  evaluation-design interview, representative corpus, and subject-matter review
  are complete.

For current user input, see [User Decisions and Requirements](#user-decisions-and-requirements). The planner keeps the synthesized sections below current as evidence and user direction evolve.

## User Decisions and Requirements

* Compile unstructured policies, FAQs, and similar documents into versioned, answer-ready evidence units.
* Implement answer shaping as an agentic AI component.
* Accept either a SharePoint document-library URL or a secured direct upload.
* Accept a caller-selected output path, preferably SharePoint.
* Preserve source grounding, provenance, freshness, and version history.
* Expose the capability through MCP where MCP is an appropriate agent-facing boundary.
* Make hosting and deployment a main part of the delivered system.

## Goals

* Deliver a working compiler and query service that turns supported documents
  into source-grounded evidence units suitable for efficient agent retrieval.
* Isolate probabilistic agent reasoning from authorization, source mutation,
  validation authority, and publication.
* Make every source, unit, job, agent run, validation result, review decision,
  release, and current pointer auditable and versioned.
* Support local development without cloud credentials while preserving
  contract-equivalent SharePoint and model adapters.
* Establish measurable quality, security, reliability, performance, and cost
  gates before automatic publication is enabled.
* Deliver a repeatable Azure-hosted deployment with explicit identity, state,
  networking, monitoring, upgrade, and rollback behavior.

## Scope and Non-Goals

### In Scope

* Python 3.11 service scaffold managed with `uv`.
* Typed domain contracts for source references, source documents, source spans,
  answer units, jobs, agent runs, validation, review, releases, and manifests.
* Direct-upload HTTP staging with quarantine and pluggable malware scanning.
* SharePoint URL resolution, enumeration, content download, delta
  synchronization, deletion handling, and Selected-permission configuration.
* PDF, DOCX, Markdown, and plain-text parsing for digitally readable content.
* One bounded answer-shaping agent with read-only tools, structured output,
  budgets, checkpoints, retries, abstention, and complete provenance.
* Deterministic and model-assisted validation with review and quarantine states.
* Immutable filesystem and SharePoint release publication with manifest-last
  commit and eTag-protected current pointer.
* SQLite-backed job/checkpoint state, source metadata, review state, and FTS5
  lexical retrieval.
* Provider-neutral vector-index port with an in-memory reference adapter for
  bounded local evaluation.
* Provider-neutral embedding port with a deterministic local hashing adapter and
  an Azure OpenAI embedding adapter for live semantic evaluation.
* HTTP, CLI, and MCP interfaces for compile, status, query, explanation, review,
  and evidence access.
* OIDC authentication with tenant, collection, principal, and role-based
  authorization contracts for query, review, compile, and administration.
* OCI container packaging and Azure Container Apps hosting with managed identity,
  Log Analytics, persistent Azure Files state, revision-based rollback, and Bicep.
* A deployment script that provisions infrastructure, builds and publishes the
  image, deploys one state-owning service replica, and runs health and MCP smoke checks.
* Unit, contract, integration, fault-injection, security, evaluation, and
  end-to-end tests plus operator and architecture documentation.

### Non-Goals

* Editing, replacing, or correcting authoritative source documents.
* Treating generated summaries or claims as canonical truth.
* Raw file transfer through MCP arguments.
* Arbitrary filesystem paths, broad tenant permissions, or write-capable agent tools.
* Per-user SharePoint permission trimming in the initial build. Each collection
  uses a permission-homogeneous SharePoint root and collection-scoped access roles.
* Scanned-document OCR, image understanding, audio/video ingestion, or website crawling.
* Multi-agent orchestration, GraphRAG, long-context routing, or automatic taxonomy generation.
* A production-scale vector store before corpus scale and latency evidence select one.
* Fully automatic publication before human-labelled evaluation and governance approval.
* A user-facing document management portal beyond the minimal upload and review APIs.
* Multi-replica execution while SQLite owns workflow state. The initial hosted
  profile is deliberately constrained to one replica; horizontal scaling
  requires a transactional managed-database adapter.

## Functional Requirements

* FR-01: Normalize SharePoint-library and upload-asset inputs into one
  `SourceDocument` stream with stable identity and content-hash versions.
  * Observable acceptance criteria: Identical content received through either
    connector yields the same content hash and parser input contract.
* FR-02: Stage direct uploads outside the publish root with size, extension,
  media-type, signature, archive, filename, authorization, malware-scan, and
  retention controls.
  * Observable acceptance criteria: Invalid or unscanned assets cannot become
    source documents or enter an agent context.
* FR-03: Resolve SharePoint URLs to stable site, drive, and item identifiers,
  enumerate only the configured root, checkpoint delta synchronization, and
  propagate renames, moves, changes, and deletions into descendant-unit
  supersession or withdrawal.
  * Observable acceptance criteria: Contract tests cover initial enumeration,
    delta resume, deletion tombstones, source/output overlap exclusion, and
    invalidation of units derived from changed or removed source versions.
* FR-04: Parse supported files into ordered, immutable source spans that retain
  heading path, page or block location, source version, text, and parser diagnostics.
  * Observable acceptance criteria: Parser fixtures reconstruct the expected
    text order and location metadata without losing qualifiers or tables marked
    as unsupported.
* FR-05: Run one AI shaping agent inside a deterministic task envelope using
  only source-span, taxonomy, and candidate-conflict read tools.
  * Observable acceptance criteria: Tool allowlist and budget tests prove that
    the agent cannot mutate state, access unrelated sources, or run indefinitely.
* FR-06: Emit schema-constrained candidate units containing claims,
  qualifiers, applicability, canonical questions, source-span references,
  confidence, ambiguity, conflict signals, and derivation metadata.
  * Observable acceptance criteria: Every candidate validates against the
    versioned answer-unit schema or enters an explicit rejected state.
* FR-07: Validate candidate units through deterministic schema, reference,
  authorization, duplication, temporal, taxonomy, and policy checks plus
  model-assisted groundedness and completeness checks.
  * Observable acceptance criteria: No unit reaches `published` with a missing
    source span, invalid source version, unresolved mandatory conflict, or failed
    release policy.
* FR-08: Route candidates through `drafted`, `validated`, `quarantined`,
  `human-approved`, `rejected`, `published`, `superseded`, and `withdrawn`
  states with actor, reason, triggering source event, timestamp, and
  optimistic-concurrency metadata. Review policy is collection-scoped and
  risk-tiered: initial releases require full review; after separately approved
  thresholds, policy-rule and conflicted units remain fully reviewed while
  standard-risk units require at least a 20 percent sample and low-risk FAQ
  units require at least a 10 percent sample. Subject-matter reviewers own any
  stricter collection tier or sampling policy.
  * Observable acceptance criteria: Invalid transitions fail explicitly and
    every accepted transition is recoverable from the audit record; changed
    and deleted sources remove superseded or withdrawn descendants from the
    next current release without rewriting prior releases.
* FR-09: Publish immutable per-run releases to a configured filesystem root or
  SharePoint folder. Every successful release is a complete active-corpus
  snapshot assembled from newly approved units plus prior units carried forward
  only when `unit_version`, source version, permission snapshot, and approval
  remain unchanged. The manifest records each carried unit's originating run.
  Write the manifest last and update `current.json` with an eTag precondition.
  Retain at least the current and previous 10 successful releases and at least
  90 days of history. Mark a pointer-race loser `completed_not_current` and
  remove its unpinned orphan release after 24 hours.
  * Observable acceptance criteria: Interrupted or concurrent publication
    never exposes a partial release as current; an incremental run over one
    changed source still resolves all unchanged active units from the new
    current release.
* FR-10: Build lexical and vector retrieval representations from accepted units
  and return ranked units, source excerpts, conflicts, coverage warnings, and
  retrieval metadata.
  * Observable acceptance criteria: Query contract tests cover exact terms,
    semantic paraphrases, filters, conflicts, empty results, and source expansion.
* FR-11: Expose `knowledge.query`, `knowledge.explain`,
  `knowledge.compile`, and `knowledge.job_status` MCP tools plus versioned unit,
  source, and release-manifest resources. `knowledge.compile` requires a
  server-authorized principal and enforces per-principal and per-collection quotas:
  one active compile per collection, two active compiles per principal, 10
  submissions per principal per rolling 24 hours, and a configurable aggregate
  model-token budget that has no unlimited production setting.
  * Observable acceptance criteria: MCP contract tests verify schemas,
    authorization, server-side quota rejection, bounded result sizes,
    confirmation metadata for compilation, and the absence of raw-upload or
    administrative tools.
* FR-12: Provide idempotent compile jobs with persisted checkpoints, cancellation,
  bounded retries, terminal diagnostics, safe resume after process failure, and
  deterministic full-snapshot assembly from changed and carried-forward units.
  * Observable acceptance criteria: Replaying one idempotency key neither
    duplicates work nor creates two current releases or omits unchanged units.
* FR-13: Provide minimal HTTP and CLI operations for upload, compile, status,
  review, publish approval, and maintenance outside the model-controlled surface.
  * Observable acceptance criteria: Interface tests enforce the same
    authorization and application use cases without duplicating domain logic.
* FR-14: Record complete provenance for sources, agent runs, prompts, schemas,
  model configuration, embedding configuration, source-permission snapshots,
  tool calls, validators, human decisions, carry-forward origins, indexes, and releases.
  * Observable acceptance criteria: One release manifest traces every published
    unit to an exact source version and derivation run without consulting logs.
* FR-15: Authenticate callers with validated OIDC tokens and authorize against
  explicit `Tenant`, `Collection`, `Principal`, and role assignments. The
  initial build grants collection-scoped `query`, `compile`, `review`, and
  `admin` roles and accepts only permission-homogeneous SharePoint roots.
  * Observable acceptance criteria: Queries and actions are denied when the
    principal lacks the collection role; ingestion refuses a configured source
    with unsupported unique-permission scope; reviewer identity is derived from
    the validated token, never a caller-supplied actor header.
* FR-16: Package and deploy the authenticated HTTP and MCP service to Azure
  Container Apps through versioned Bicep and a repeatable deployment command.
  The hosted profile uses managed identity for Azure access, an encrypted
  persistent state mount, immutable container revisions, centralized logs, and
  a single replica while SQLite is the state owner.
  * Observable acceptance criteria: Infrastructure validates, the image builds,
    deployment outputs an HTTPS endpoint, readiness and MCP initialization smoke
    checks pass, secrets are supplied through protected deployment inputs, and
    a previous healthy revision can be restored without rebuilding.

## Non-Functional Requirements

* NFR-01: Published evidence has complete provenance.
  * Objective threshold or evaluation condition: 100 percent of published units
    reference existing source spans from the manifest's exact source versions.
  * Operating condition or verification approach: Enforced in deterministic
    validators and release-integrity tests.
  * Observable acceptance criteria: A deliberately broken reference blocks publication.
* NFR-02: Agent autonomy is bounded and least-privileged.
  * Objective threshold or evaluation condition: Zero write-capable,
    network-general, shell, permission, or publication tools are present in the
    agent allowlist; every run terminates at configured call, token, time, and retry limits.
  * Operating condition or verification approach: Static allowlist tests,
    adversarial fixtures, and forced-budget-exhaustion tests.
  * Observable acceptance criteria: A source-embedded instruction cannot cause
    a write, cross-tenant read, budget extension, or validation bypass.
* NFR-03: Workflow and publication are recoverable.
  * Objective threshold or evaluation condition: Every durable transition is
    transactional; fault injection at each checkpoint resumes without duplicate
    units or a partial current release.
  * Operating condition or verification approach: SQLite transaction tests and
    filesystem/SharePoint sink fault simulation.
  * Observable acceptance criteria: The same job completes once after restart.
* NFR-04: Initial retrieval performance is bounded.
  * Objective threshold or evaluation condition: Warm local top-10 queries over
    10,000 synthetic units achieve p95 latency below 500 ms on the documented
    development profile. Local hashing embeddings verify vector contract,
    filtering, fusion, and ranking mechanics; semantic paraphrase quality is
    asserted only by the opt-in live embedding suite.
  * Operating condition or verification approach: Repeatable benchmark command
    records corpus size, hardware, index version, and percentile distribution.
  * Observable acceptance criteria: CI or an explicit performance job reports the threshold.
* NFR-05: Compilation cost and latency are observable and capped.
  * Objective threshold or evaluation condition: Each run records model calls,
    tokens, tool calls, retries, elapsed time, and estimated cost; configured
    budgets stop further model work rather than silently exceeding limits.
    Server-side concurrent-job, rolling submission, and aggregate model-token
    quotas are enforced per principal and collection independently of MCP host confirmation.
  * Operating condition or verification approach: Fake-model budget tests and
    live-model opt-in tests.
  * Observable acceptance criteria: Budget exhaustion produces a diagnosed
    quarantine or failed job, never a success-shaped result.
* NFR-06: Quality gates are evidence-based.
  * Objective threshold or evaluation condition: All synthetic mandatory cases
    pass deterministic grounding, qualifier, exception, conflict, abstention,
    and state-transition checks. Automatic publication remains disabled until a
    subject-matter-reviewed dataset defines and meets live thresholds.
  * Operating condition or verification approach: Programmatic evaluation is
    the system of record; manual sample review is required before threshold
    changes. A configured live run produces
    tests/evaluation/baselines/live-approved.json, approved by the evaluation
    owner and a domain reviewer. Upgrades fail when deterministic pass rates
    fall at all, model-assisted pass rates fall by more than 5 percentage
    points, or p95 latency or model-token use rises by more than 20 percent,
    unless those owners approve a new baseline through review.
  * Observable acceptance criteria: A model, prompt, schema, or validator change
    cannot update the current release when its required evaluation gate fails.
* NFR-07: External systems are optional for local development.
  * Objective threshold or evaluation condition: Unit, contract, security, and
    synthetic end-to-end tests pass without SharePoint or model credentials.
  * Operating condition or verification approach: Deterministic fakes implement
    connector, model, evaluator, and embedding contracts. The local hashing
    embedding adapter tests mechanics only; live semantic quality tests skip
    with a stated reason when no embedding deployment is configured.
  * Observable acceptance criteria: `uv run pytest` completes locally with no cloud sign-in.
* NFR-08: The implementation remains maintainable and portable.
  * Objective threshold or evaluation condition: Domain and application packages
    do not import infrastructure or interface packages; public APIs are typed;
    formatter, linter, type checker, and tests pass.
  * Operating condition or verification approach: Architecture import tests,
    Ruff, mypy, and pytest.
  * Observable acceptance criteria: One documented validation command passes.
* NFR-09: Sensitive data and secrets do not leak.
  * Objective threshold or evaluation condition: Credentials never enter prompts,
    release artifacts, diagnostics, or logs; source text logging is off by default.
  * Operating condition or verification approach: Redaction tests, secret scan,
    and structured-log assertions.
  * Observable acceptance criteria: Test credentials and marked sensitive spans
    are absent from captured logs and manifests.
* NFR-10: Hosting is repeatable, observable, and recoverable.
  * Objective threshold or evaluation condition: A clean Azure resource group
    reaches a healthy service revision from one documented deployment command;
    declared infrastructure is idempotent and deployment is pinned to an image digest.
  * Operating condition or verification approach: Container build, Bicep build,
    what-if/deployment validation, health smoke checks, and revision rollback drill.
  * Observable acceptance criteria: Deployment evidence records the revision,
    endpoint, image digest, health result, and rollback command without recording secrets.

## Acceptance Criteria

* AC-01: A direct upload and a SharePoint fixture compile through the same
  source-document and source-span contracts.
* AC-02: The bounded agent produces versioned candidate units with exact source
  references, abstains on insufficient evidence, and cannot access a write tool.
* AC-03: Deterministic and model-assisted validation route success, retry,
  quarantine, review, and rejection without silent fallback.
* AC-04: A reviewer can inspect source evidence and approve or reject a candidate;
  initial releases require full review. Later collection policies may sample
  lower-risk units only after approved thresholds, while policy-rule,
  low-confidence, and conflicted units remain fully reviewed.
* AC-05: Filesystem and SharePoint sinks publish immutable releases using
  manifest-last ordering. Each current release is a complete active-corpus
  snapshot with traceable carry-forward; current-pointer races fail safely and
  orphan retention follows the configured lifecycle.
* AC-06: Query and explanation return bounded, authorized evidence with source
  excerpts, conflicts, and coverage warnings using collection-scoped roles.
* AC-07: MCP exposes the four planned tools and three resource families with no
  binary upload, arbitrary path, permission, delete, or forced-publish surface;
  compile authorization and quotas are enforced by the server.
* AC-08: Compile jobs are idempotent, resumable, cancellable, and diagnosable.
* AC-09: A release manifest provides complete source-to-unit-to-agent-to-review
  lineage, carried-forward origin, permission snapshot, and full active-corpus
  completeness and validates independently.
* AC-10: Synthetic evaluation includes easy, grounding, hard, negative/error,
  and safety cases; expected domain answers that lack authoritative sources are
  marked for subject-matter review rather than invented.
* AC-11: Agent-versus-fixed-chain evaluation reports quality, groundedness,
  completeness, abstention, tool accuracy, latency, and cost. The same harness
  compares answer-unit retrieval against contextualized source chunks. Neither
  the agent nor unit path must win for implementation acceptance, but the
  evidence must be reported before production activation.
* AC-12: Prompt-injection, budget-exhaustion, malformed-file, cross-tenant,
  unauthorized-role, forged-actor, partial-publication, stale-eTag, and restart tests pass.
* AC-13: Local validation passes without cloud credentials; live SharePoint and
  model suites run when explicitly configured.
* AC-14: Operator documentation covers configuration, permissions, data flow,
  review policy, retention, recovery, release rollback, and model/prompt upgrades.
* AC-15: The shipped OCI image runs as a non-root process with health probes;
  Bicep provisions the Azure Container Apps environment, managed identity,
  persistent state, monitoring, and service revision; the deployment script
  builds, deploys, and smoke-tests the authenticated endpoint.

## Implementation Baseline and Change Budget

* Runtime: Python 3.11.
* Environment and dependency management: `uv` with `.venv` and committed `uv.lock`.
* Service interfaces: FastAPI for HTTP, Typer for CLI, and the official Python
  MCP SDK for the MCP server.
* Data contracts and configuration: Pydantic v2 and JSON Schema.
* Durable local state and lexical index: SQLite in WAL mode with FTS5.
* AI integration: provider-neutral `ModelGateway` protocol with a first Azure
  OpenAI structured-output adapter and a deterministic fake for tests.
* Embeddings: provider-neutral `EmbeddingProvider` protocol with a deterministic
  local feature-hashing adapter for credential-free mechanics tests and an
  Azure OpenAI embedding adapter for live semantic evaluation.
* SharePoint integration: a narrow Microsoft Graph adapter using Azure Identity;
  Graph types do not cross the infrastructure boundary.
* Caller identity: OIDC JWT validation at HTTP and MCP boundaries. Application
  authorization uses explicit tenant, collection, principal, and role values.
* Document parsing: PyMuPDF for digitally readable PDF, python-docx for DOCX,
  and built-in text handling for Markdown and plain text.
* Validation: Ruff format/lint, mypy strict mode for application packages, pytest,
  pytest-cov, contract tests, and architecture import tests.
* Agent implementation: a transparent bounded loop in application code. Do not
  add a multi-agent framework unless evaluation produces a plan amendment.
* Exact removals: none. The repository has no production files.
* Maximum additions: 148 tracked files, checked after every phase, with these
  phase allowances: P01 24, P02 24, P03 18, P04 16, P05 20, P06 18, and P07 20.
  P07 has an additional 8-file deployment allowance confirmed during implementation.
  The evaluation corpus uses one JSONL data file plus one metadata file rather
  than one file per case. Generated caches, local databases, uploaded assets,
  evaluation reports, and release snapshots remain ignored.
* Canonical targets: Pydantic domain models, workflow state machine, prompt and
  rubric sources, MCP tool/resource definitions, and hand-authored evaluation
  case metadata. Pydantic models are the single source of truth for data contracts.
* Generated targets: `uv.lock`, committed JSON Schema snapshots generated from
  Pydantic models, OpenAPI output, local indexes, test reports, and release
  artifacts. Schema snapshots are never hand-edited; regeneration drift fails validation.

## Test Ownership and Validation Strategy

* Every `Pxx-Txx` task owns its unit and contract tests. Tests land with behavior,
  not in a later cleanup phase.
* Connector contract suites run unchanged against fakes and live adapters.
* Semantic coverage validates claims, qualifiers, exceptions, applicability,
  conflicts, citations, abstention, and review routing.
* Regression coverage compares normalized units, evaluator scores, retrieval
  results, state transitions, latency, and cost. It does not require byte-identical AI output.
* Fake-model regression proves gate mechanics. Threshold enforcement compares a
  configured live run with tests/evaluation/baselines/live-approved.json, whose
  update requires approval from the evaluation owner and a domain reviewer.
* Local feature-hashing embeddings validate vector contract, filtering, fusion,
  and ranking mechanics. Only the live embedding suite makes semantic-quality claims.
* Live SharePoint and model tests are opt-in and fail with actionable diagnostics
  when configured incorrectly. They skip with an explicit reason when not configured.
* The final validation command runs formatting checks, linting, strict typing,
  unit/contract/integration/security tests, schema export comparison, and the
  synthetic end-to-end suite. Performance and live-cloud suites run as named
  additional commands.

## Implementation Context Record

| Context item | Current artifact or record |
|---|---|
| Plan | .copilot-tracking/plans/2026-09-09/answer-shaped-knowledge-mcp-plan.md |
| Phase details | .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md |
| Latest critique | .copilot-tracking/reviews/plans/2026-09-09/answer-shaped-knowledge-mcp-plan-critique.md with Revise verdict and all findings resolved by the planning parent |
| Relevant research | .copilot-tracking/research/2026-09-09/answer-shaped-knowledge-mcp-research.md |
| Changes-record role | .copilot-tracking/changes/2026-09-09/answer-shaped-knowledge-mcp-changes.md is created or continued by implementation as its evidence record |
| Planning execution and readiness | Complete and Ready after one critique and planner-owned revision |
| Continuation context | Manual RPI Agent remains in Plan until explicit advancement |

## Current Implementation State

* Declared invocation scope: Full plan, P01 through P07.
* Active phase: P07 complete; implementation is ready for explicit Review.
* First execution boundary: Completed.
* Approved write boundary: The planned production, test, schema, prompt, rubric,
  evaluation, documentation, and implementation-tracking targets within the
  148-file budget.
* Validation intent: Run each task's targeted checks, each phase's completion
  checks, and the final local validation matrix. Live checks remain opt-in when
  their documented external prerequisites are unavailable.
* Active blockers: None. Live Azure, SharePoint, Entra, Azure OpenAI, and
  production-corpus validation await external credentials and governed resources.

## Sources

* .copilot-tracking/research/2026-09-09/answer-shaped-knowledge-mcp-research.md: architecture, evidence W1-W32, decisions, alternatives, risks, and planning readiness
* Caller conversation on 2026-09-09: confirmed inputs, outputs, versioning, MCP interest, and agentic AI answer shaping
* Python foundational skill: typed APIs, explicit errors, small responsibilities, dependency fit, and maintainability
* Evaluation-design skill: evaluation categories, system and process metrics, synthetic-data boundaries, review ownership, and programmatic evaluation guidance

## Phase Checklist

<!-- rpi:phase id=P01 -->
### [x] P01: Establish foundation and contracts

* Intent: Create the Python service baseline and freeze provider-neutral domain,
  state, schema, and port contracts.
* Dependencies: Completed research.
* Implementation state: Complete; all P01 validation and file-budget checks pass.

<!-- rpi:task id=P01-T01 -->
#### [x] P01-T01: Scaffold the project and quality gates

* Requirement and evidence: Empty repository; Python and `uv` baseline selected above.
* Expected result: Installable package, typed configuration, package boundaries,
  validation commands, CI-ready tests, and ignored runtime artifacts.
* Detail section: P01-T01 in .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md
* Implementation state: Complete.

<!-- rpi:task id=P01-T02 -->
#### [x] P01-T02: Define domain schemas and invariants

* Requirement and evidence: FR-01, FR-06, FR-08, FR-09, FR-12, FR-14.
* Expected result: Versioned typed models and JSON Schemas for sources, spans,
  units, jobs, runs, validation, review, releases, tenants, collections,
  principals, roles, and source-permission snapshots.
* Detail section: P01-T02 in .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md

<!-- rpi:task id=P01-T03 -->
#### [x] P01-T03: Define ports, state store, and dependency rules

* Requirement and evidence: Research requires connector, model, index, evaluator,
  and output adapters behind stable application contracts.
* Expected result: Typed protocols, SQLite migrations, transaction boundaries,
  explicit errors, `EmbeddingProvider`, and architecture tests.
* Detail section: P01-T03 in .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md

<!-- rpi:phase id=P02 -->
### [x] P02: Implement secure source ingestion

* Intent: Convert SharePoint and direct-upload inputs into validated, versioned source spans.
* Dependencies: P01.
* Implementation state: Complete; upload, SharePoint, parser, and normalization checks pass.

<!-- rpi:task id=P02-T01 -->
#### [x] P02-T01: Implement quarantined direct uploads

* Requirement and evidence: FR-02 and W19, W20, W23.
* Expected result: Streaming upload endpoint, asset lifecycle, scanner port,
  hash calculation, retention metadata, and explicit rejection diagnostics.
* Detail section: P02-T01 in .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md

<!-- rpi:task id=P02-T02 -->
#### [x] P02-T02: Implement SharePoint source synchronization

* Requirement and evidence: FR-03 and W14-W18, W22.
* Expected result: URL resolution, stable identifiers, recursive enumeration,
  content download, permission-homogeneous root validation, delta checkpoints,
  tombstones, descendant invalidation events, and output-root exclusion.
* Detail section: P02-T02 in .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md

<!-- rpi:task id=P02-T03 -->
#### [x] P02-T03: Parse and normalize supported documents

* Requirement and evidence: FR-01 and FR-04.
* Expected result: Safe PDF, DOCX, Markdown, and text parsers producing ordered,
  immutable source spans and diagnostics.
* Detail section: P02-T03 in .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md

<!-- rpi:phase id=P03 -->
### [x] P03: Implement bounded agentic shaping

* Intent: Produce source-grounded candidate units through one observable,
  least-privileged, budgeted AI agent.
* Dependencies: P01 and P02.
* Implementation state: Complete; capability, repair, abstention, and budget checks pass.

<!-- rpi:task id=P03-T01 -->
#### [x] P03-T01: Implement read-only agent tools and task envelope

* Requirement and evidence: FR-05, NFR-02, W24, W26-W28, W31, W32.
* Expected result: Tenant-scoped span, taxonomy, and conflict tools plus immutable
  run instructions and enforced budgets.
* Detail section: P03-T01 in .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md

<!-- rpi:task id=P03-T02 -->
#### [x] P03-T02: Implement model gateway and structured candidate generation

* Requirement and evidence: FR-06, W25, W30.
* Expected result: Provider-neutral model port, deterministic fake, Azure OpenAI
  adapter, pinned configuration, and schema-constrained candidate output.
* Detail section: P03-T02 in .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md

<!-- rpi:task id=P03-T03 -->
#### [x] P03-T03: Implement checkpointed shaping loop

* Requirement and evidence: FR-05, FR-12, FR-14.
* Expected result: Bounded context acquisition, candidate repair, abstention,
  cancellation, retry classification, checkpoints, and run provenance. Repair
  consumes the P01 `Validator` port using only schema and source-span-existence
  checks until P04 extends that same port.
* Detail section: P03-T03 in .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md

<!-- rpi:phase id=P04 -->
### [x] P04: Implement validation and review

* Intent: Prevent unsupported, unsafe, incomplete, or conflicted units from publication.
* Dependencies: P01 and P03.
* Implementation state: Complete; deterministic, evaluator, policy, and lifecycle checks pass.

<!-- rpi:task id=P04-T01 -->
#### [x] P04-T01: Implement deterministic validation

* Requirement and evidence: FR-07, NFR-01, NFR-06.
* Expected result: Schema, source, authorization, taxonomy, temporal,
  duplicate/conflict, and release-policy validators with typed findings,
  extending the P01 port without duplicating P03 checks.
* Detail section: P04-T01 in .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md

<!-- rpi:task id=P04-T02 -->
#### [x] P04-T02: Implement model-assisted quality evaluation

* Requirement and evidence: FR-07, W9, W29.
* Expected result: Groundedness, completeness, qualifier, abstention, and task
  adherence evaluators isolated behind a port with recorded prompts and scores.
* Detail section: P04-T02 in .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md

<!-- rpi:task id=P04-T03 -->
#### [x] P04-T03: Implement review and state transitions

* Requirement and evidence: FR-08 and default human-review policy.
* Expected result: Optimistic-concurrency state machine, review queue, evidence
  view, approve/reject/supersede/withdraw operations, OIDC-derived reviewer
  identity, risk tiers, batch and sampling policy, audit records, and publish eligibility.
* Detail section: P04-T03 in .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md

<!-- rpi:phase id=P05 -->
### [x] P05: Implement release publication and retrieval

* Intent: Publish accepted evidence atomically and make it efficiently retrievable.
* Dependencies: P01, P02, and P04.
* Implementation state: Complete; full-snapshot, sink, integrity, and retrieval checks pass.

<!-- rpi:task id=P05-T01 -->
#### [x] P05-T01: Build release manifests and filesystem publication

* Requirement and evidence: FR-09, FR-14.
* Expected result: Deterministic artifact serialization, integrity hashes,
  full active-corpus assembly, approval-preserving carry-forward with origin
  run IDs, superseded/withdrawn exclusion, manifest-last commit, current
  pointer, retention/orphan handling, and rollback-capable local sink.
* Detail section: P05-T01 in .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md

<!-- rpi:task id=P05-T02 -->
#### [x] P05-T02: Implement SharePoint release publication

* Requirement and evidence: W18-W22 and immutable snapshot decision.
* Expected result: Conflict-fail upload strategy, resumable transfer selection,
  manifest-last ordering, eTag current-pointer update, and label diagnostics.
* Detail section: P05-T02 in .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md

<!-- rpi:task id=P05-T03 -->
#### [x] P05-T03: Build indexes and query service

* Requirement and evidence: FR-10, W4, W5, W13.
* Expected result: Full-release FTS5 lexical index, embedding and vector-index
  ports, local feature-hashing adapters, Azure OpenAI embedding adapter,
  fusion/reranking, filters, source expansion, conflicts, and coverage warnings.
* Detail section: P05-T03 in .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md

<!-- rpi:phase id=P06 -->
### [x] P06: Expose jobs, review, query, and MCP interfaces

* Intent: Provide bounded interfaces without duplicating application logic or
  exposing binary transfer and administration to model-controlled tools.
* Dependencies: P02-P05.
* Implementation state: Complete; authenticated HTTP/MCP, persistent jobs and
  quotas, uploads, retrieval, health, and real SDK initialization checks pass.

<!-- rpi:task id=P06-T01 -->
#### [x] P06-T01: Implement compile-job orchestration and HTTP/CLI interfaces

* Requirement and evidence: FR-11-FR-13.
* Expected result: Idempotent compile use case, worker execution, upload and
  review HTTP routes, operator CLI, status, cancellation, and diagnostics.
* Detail section: P06-T01 in .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md

<!-- rpi:task id=P06-T02 -->
#### [x] P06-T02: Implement query and explanation interfaces

* Requirement and evidence: FR-10, FR-13.
* Expected result: Authorized, bounded query and explanation responses shared by
  HTTP, CLI, and MCP adapters.
* Detail section: P06-T02 in .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md

<!-- rpi:task id=P06-T03 -->
#### [x] P06-T03: Implement MCP tools and resources

* Requirement and evidence: FR-11, W1-W3.
* Expected result: Four MCP tools, three resource families, structured errors,
  OIDC and collection-role enforcement, server-side compile quotas,
  confirmation metadata, authorization filtering, and subscriptions if supported.
* Detail section: P06-T03 in .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md

<!-- rpi:phase id=P07 -->
### [ ] P07: Deploy and prove production operability

* Intent: Ship the hosted Azure service and establish release evidence,
  operational controls, and documentation across local and live environments.
* Dependencies: P01-P06.
* Implementation state: Complete for the local delivery boundary; Bicep compiles
  without warnings. Live deployment remains an external credentialed check.

<!-- rpi:task id=P07-T01 -->
#### [x] P07-T01: Build the evaluation and regression harness

* Requirement and evidence: NFR-04-NFR-06, AC-10, AC-11.
* Expected result: Synthetic evaluation contract, fixed-chain baseline,
  contextualized-chunk retrieval baseline, approved live regression baseline,
  tolerance gate, system/process metrics, benchmark reporting, and explicit
  subject-matter-review markers.
* Detail section: P07-T01 in .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md

<!-- rpi:task id=P07-T02 -->
#### [ ] P07-T02: Complete adversarial, fault, and live integration tests

* Requirement and evidence: NFR-02, NFR-03, NFR-07, NFR-09, AC-12, AC-13.
* Expected result: Injection, permission, budget, malformed-input, restart,
  publication-race, SharePoint, and model test evidence.
* Detail section: P07-T02 in .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md

<!-- rpi:task id=P07-T03 -->
#### [x] P07-T03: Finalize observability, operations, and documentation

* Requirement and evidence: FR-14, NFR-05, NFR-08, NFR-09, AC-14.
* Expected result: Structured telemetry, health checks, runbooks, permissions
  guide, retention and recovery procedures, upgrade process, and final validation.
* Detail section: P07-T03 in .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md

<!-- rpi:task id=P07-T04 -->
#### [ ] P07-T04: Package and deploy the Azure-hosted service

* Requirement and evidence: Confirmed hosting priority, FR-16, NFR-10, and AC-15.
* Expected result: Non-root OCI image, Azure Container Apps Bicep, managed
  identity, persistent single-replica state, Log Analytics, protected
  configuration, deployment automation, health/MCP smoke checks, and rollback guidance.
* Detail section: P07-T04 in .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md

## Dependencies

* Representative corpus and subject-matter reviewers: required to create and
  approve live expected behaviors, review tiers, sampling rates, and
  automatic-publication thresholds.
* SharePoint test tenant, source/output libraries, app registration, and Selected
  grants: required for live connector and publisher tests.
* Azure OpenAI deployment and optional separate evaluator deployment: required
  for live shaping and quality-evaluator tests.
* Azure OpenAI embedding deployment: required for live semantic retrieval tests;
  local mechanics use deterministic feature hashing.
* OIDC identity provider registration, issuer, audience, role-mapping
  administration, and test principals: required for live authorization tests.
* Malware scanner integration: required before direct uploads are enabled in a
  production profile; local tests use an explicit deterministic scanner fake.
* SharePoint retention, sensitivity-label, and version settings: required to
  finalize delegated versus app-only publication policy.

## Critique Disposition

| Critique run and finding | Disposition | Plan response or residual risk |
|---|---|---|
| PC-001: Incremental release composition | resolved | FR-09 and P05 define a complete current snapshot with unchanged approved units carried forward by exact unit/source/permission version |
| PC-002: Published-unit invalidation | resolved | FR-03 and FR-08 add superseded and withdrawn lifecycle events; current releases exclude affected units while prior releases remain immutable |
| PC-003: Authorization and actor identity | resolved by planner assumption | FR-15 selects OIDC-authenticated collection roles and permission-homogeneous SharePoint roots; per-user permission trimming is an explicit non-goal |
| PC-004: Unachievable file budget | resolved | Budget increased to 140 with per-phase allowances, compact evaluation data files, and phase-end checks |
| PC-005: Missing embedding strategy | resolved | Added `EmbeddingProvider`, local feature hashing for mechanics, Azure OpenAI for live semantic quality, and explicit dependencies |
| PC-006: Missing core value benchmark | resolved | AC-11 and P07-T01 compare answer units with contextualized source chunks |
| PC-007: Backward validator dependency | resolved | P03 uses the P01 validator port with two minimal checks; P04 extends the port without duplication |
| PC-008: Undefined regression baseline | resolved | NFR-06 and P07-T01 define the approved live baseline, owners, tolerances, and gate mechanics |
| PC-009: Advisory-only compile control | resolved | FR-11, NFR-05, and P06-T03 add server authorization and per-principal/collection quotas |
| PC-010: Unbounded review policy | resolved | FR-08 and P04-T03 define initial full review, later risk tiers and sampling, volume assumptions, and threshold owners |
| PC-011: Schema source ambiguity | resolved | Pydantic models are canonical; committed JSON Schemas are generated snapshots and drift evidence |
| PC-012: Missing release lifecycle | resolved | FR-09 and P05 define retention, race-loser state, orphan cleanup, and rollback documentation |

## Follow-Up Items

* Evaluate OCR and image-aware parsing after representative files demonstrate a need; owner: future research and planning.
* Select and implement a production vector backend after corpus scale and p95 query evidence exceed the local adapter's envelope; owner: future planning.
* Evaluate GraphRAG or long-context routes only for query classes that the baseline retrieval evaluation fails; owner: future research.
* Run the evaluation-design interview and sample review before creating a customer or production evaluation dataset; owner: product and subject-matter reviewers.
* Complete RAI, privacy, and formal security planning before a production launch if the corpus contains regulated, personal, legal, health, or financial content; owner: governance workstreams.

## Handoff

* Implementation artifact: .copilot-tracking/changes/2026-09-09/answer-shaped-knowledge-mcp-changes.md
* Ready phase or task: P01
* Remaining provisional question or blocker: None
