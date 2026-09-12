<!-- markdownlint-disable-file -->
# RPI Phase Details: Knowledge Estate Workflow Redesign

## Metadata

* Task ID: knowledge-estate-workflow-redesign
* Task slug: knowledge-estate-workflow-redesign
* Related plan: .copilot-tracking/plans/2026-09-10/knowledge-estate-workflow-redesign-plan.md
* Evidence sources: .copilot-tracking/research/2026-09-10/knowledge-estate-workflow-redesign-research.md
* Planning status: Ready

## Phase Index

| Phase ID | Name | Status | Detail sections |
|---|---|---|---|
| P01 | Establish Estate Contracts and Multi-Agent Boundaries | Ready | P01, P01-T01, P01-T02 |
| P02 | Register Sources and Build the Document Inventory | Ready | P02, P02-T01, P02-T02, P02-T03 |
| P03 | Run Multi-Agent Discovery | Ready | P03, P03-T01, P03-T02 |
| P04 | Recommend, Estimate, and Decide | Ready | P04, P04-T01, P04-T02, P04-T03 |
| P05 | Transform Approved Content and Publish Artifacts | Ready | P05, P05-T01, P05-T02, P05-T03 |
| P06 | Expose Durable APIs and the Live Product Experience | Ready | P06, P06-T01, P06-T02, P06-T03, P06-T04 |
| P07 | Deploy and Prove the Azure Workflow | Ready | P07, P07-T01, P07-T02, P07-T03 |

<!-- rpi:phase id=P01 -->
## P01: Establish Estate Contracts and Multi-Agent Boundaries

### Context

The current `Collection` is a one-source, one-output authorization boundary. A user-managed Knowledge Estate needs many sources and lifecycle records without weakening that boundary. Current source versions, review decisions, and content-addressed identities provide reusable patterns.

### Intent

Create immutable workflow contracts and application ports that preserve deterministic platform authority and distinct specialist-agent evidence.

### Boundaries

* Included: Estate aggregate, lifecycle records, repository ports, concurrency, identity, and role ownership
* Excluded: Infrastructure adapters, API routes, and UI

### Likely Targets

* src/shaper/domain/estate.py: New estate workflow contracts
* src/shaper/domain/__init__.py: Public domain exports
* src/shaper/application/estates.py: Estate workflow service, internal collection grants, and repository protocols
* src/shaper/application/ports.py: Shared source and persistence boundaries where appropriate
* tests/test_estate_domain.py: Domain invariants
* tests/test_estates.py: Application behavior

### Dependencies

* Research C1-C25

### Validation Expectations

* Verify strict immutable models, stable IDs, safe naming policy, legal state transitions, optimistic revisions, and package layering.

### Completion Evidence

* Targeted estate domain and service tests pass.
* Existing domain and architecture tests remain green.

### Unresolved Items

* None

<!-- rpi:task id=P01-T01 -->
### P01-T01: Define the Knowledge Estate Domain

#### Context

The requested workflow needs first-class entities that are absent from the current domain.

#### Intent

Define `KnowledgeEstate`, `EstateSource`, `EstateDocument`, `WorkflowRun`, `DiscoveryRun`, `DocumentReadinessReport`, `RecommendationRun`, `DocumentRecommendation`, `TokenEstimate`, `TransformationDecision`, `TransformationRun`, `TokenUsage`, `KnowledgeArtifact`, `ArtifactNamingPolicy`, `CollectionGrant`, and a non-content purge tombstone.

#### Boundaries

* Included: Stable identity, tenant and collection ownership, source version pinning, timestamps, revisions, status enums, immutable value objects, and validation
* Excluded: Persistence and orchestration behavior

#### Likely Targets

* src/shaper/domain/estate.py: Domain definitions
* src/shaper/domain/__init__.py: Exports
* tests/test_estate_domain.py: Creation, validation, hashing, naming, and transition fixtures

#### Dependencies

* Existing `DomainModel`, `Identifier`, `canonical_hash`, `SourceDocument`, and review patterns

#### Validation Expectations

* Reject mismatched tenant or collection boundaries, duplicate source or document IDs, unsafe naming templates, invalid token ranges, maximums below upper estimates, and inconsistent source versions.

#### Completion Evidence

* Repeated construction from equivalent inputs produces stable identities.
* Pydantic strict-mode and immutability tests pass.

#### Unresolved Items

* None. Naming grammar is intentionally restricted to `{source_stem}` in this increment.

<!-- rpi:task id=P01-T02 -->
### P01-T02: Define Repository and Orchestration Ports

#### Context

The application needs persistence without importing SQLite or PostgreSQL, and agents need bounded outputs without workflow authority.

#### Intent

Define repository contracts for estates and workflow records, plus service boundaries that separate evidence generation from state transitions.

#### Boundaries

* Included: Load, list, create, compare-and-save, append-only decision and usage operations, durable run leases, and unit-of-work semantics required by a transition
* Excluded: Database-specific SQL

#### Likely Targets

* src/shaper/application/estates.py: Estate service and repository contracts
* src/shaper/application/ports.py: Shared protocols
* src/shaper/application/orchestration.py: Estate-scoped orchestration boundary
* tests/test_estates.py: In-memory contract fake and behavior tests
* tests/test_orchestration.py: Multi-agent ownership assertions

#### Dependencies

* P01-T01

#### Validation Expectations

* A stale expected revision fails.
* Agent results cannot directly create decisions, jobs, or publications.
* Existing stateless analysis remains compatible.

#### Completion Evidence

* Application tests exercise all transitions through ports without infrastructure imports.

#### Unresolved Items

* None

<!-- rpi:phase id=P02 -->
## P02: Register Sources and Build the Document Inventory

### Context

SharePoint delta enumeration and individual upload validation exist, but neither is composed into a many-source estate. ZIP bundles are unsupported.

### Intent

Create truthful source registrations and convert supported source content into individual immutable estate documents.

### Boundaries

* Included: SharePoint site or library URLs, individual files, ZIP bundles, checkpoints, source status, and inventory
* Excluded: Unrestricted web URLs and additional enterprise connectors

### Likely Targets

* src/shaper/application/estates.py: Source commands and inventory transitions
* src/shaper/infrastructure/uploads.py: Estate association and individual asset handling
* src/shaper/infrastructure/archive.py: Bounded ZIP expansion
* src/shaper/infrastructure/sharepoint.py: Source state and delta integration
* src/shaper/application/ingestion.py: Multi-document ingestion entry points
* tests/test_archive.py, tests/test_sharepoint.py, tests/test_ingestion.py, tests/test_compilation.py, and tests/test_interfaces.py

### Dependencies

* P01
* Existing ClamAV availability for uploaded content
* Microsoft Graph authorization for successful SharePoint synchronization

### Validation Expectations

* Test successful and failed connector states, stable IDs, checkpoint reuse, file withdrawal, duplicate content versions, and the full malicious ZIP matrix.

### Completion Evidence

* A mixed estate produces one inventory row per accepted file.
* Unavailable authorization remains explicit and creates no sample inventory.

### Unresolved Items

* Graph tenant administration is an external deployment dependency, not an implementation ambiguity.

<!-- rpi:task id=P02-T01 -->
### P02-T01: Implement Estate and Source Registration

#### Context

Users need to create named estates and attach multiple independently managed source definitions.

#### Intent

Add authorized commands to create, update, archive, and inspect estates and register or remove typed sources.

#### Boundaries

* Included: Names, descriptions, naming policy, source kind, safe locator, status, diagnostic, timestamps, and revision
* Excluded: Retrieving arbitrary HTTPS content

#### Likely Targets

* src/shaper/application/estates.py: Commands, queries, grants, archive, and purge
* src/shaper/domain/estate.py: Source status and locator contracts
* tests/test_estates.py: Authorization and concurrency cases

#### Dependencies

* P01

#### Validation Expectations

* Enforce collection roles, tenant matching, locator type, uniqueness, optimistic revision, and explicit purge confirmation.
* An archived estate remains readable and rejects sync, discovery, recommendation, decision, and transformation operations.
* Purge removes content-bearing records and bytes while retaining only a minimal non-content audit tombstone.

#### Completion Evidence

* One estate can retain multiple source registrations with independent state and diagnostics.
* Archive and purge behavior satisfy AC-18 and AC-19.

#### Unresolved Items

* None

<!-- rpi:task id=P02-T02 -->
### P02-T02: Implement Bounded Upload and ZIP Expansion

#### Context

The current upload store accepts one supported file. ZIP bundles must become multiple files without weakening quarantine.

#### Intent

Associate uploads with an estate and expand ZIP entries through a dedicated bounded adapter before document creation.

#### Boundaries

* Included: Path normalization, entry count, per-entry and aggregate expanded sizes, compression ratio, encryption rejection, supported extension and signature checks, per-entry malware scan, and archive provenance
* Excluded: Nested archives and unsupported entry types

#### Likely Targets

* src/shaper/infrastructure/archive.py: ZIP boundary
* src/shaper/infrastructure/uploads.py: Estate-aware upload staging
* src/shaper/application/ingestion.py: Individual document creation
* tests/test_archive.py: Archive attack and success matrix
* tests/test_ingestion.py, tests/test_compilation.py, and tests/test_interfaces.py: Upload regression and estate association

#### Dependencies

* P02-T01
* Existing upload size and malware policies

#### Validation Expectations

* Reject traversal, absolute paths, symlinks, encrypted entries, nested archives, extension/signature mismatch, executable suffixes, excessive expansion, and infected content.

#### Completion Evidence

* Each safe entry has its own source ID, version, title, media type, archive locator, and scan result.
* Failure does not create partial inventory records.

#### Unresolved Items

* Initial numeric archive limits follow or tighten the existing upload limit and remain configurable.

<!-- rpi:task id=P02-T03 -->
### P02-T03: Integrate SharePoint Synchronization

#### Context

The existing connector resolves one SharePoint location and emits changed or withdrawn files using Graph delta.

#### Intent

Drive that connector from estate source registrations and persist checkpoints, versions, withdrawals, and diagnostics.

#### Boundaries

* Included: SharePoint `sites` and `teams` URLs supported by the current resolver
* Excluded: OneDrive personal locations, arbitrary web URLs, and delegated interactive Graph access

#### Likely Targets

* src/shaper/infrastructure/sharepoint.py: Connector diagnostics and hosted transport integration
* src/shaper/application/estates.py: Sync command and inventory updates
* tests/test_sharepoint.py: Delta, permission, failure, and status cases

#### Dependencies

* P02-T01
* Graph application authorization

#### Validation Expectations

* Preserve source IDs and versions, continue from delta checkpoints, withdraw deleted files, and fail without success-shaped fallback.

#### Completion Evidence

* Authorized sync creates inventory from live Graph responses.
* Unauthorized sync persists `authorization_required` with corrective guidance.

#### Unresolved Items

* None

<!-- rpi:phase id=P03 -->
## P03: Run Multi-Agent Discovery

### Context

Current scoring helpers operate on individual profiles but collapse their results into one estate score. Duplicate, contradiction, topic, and authority analysis is relational.

### Intent

Persist per-document reports while preserving estate-level multi-document evidence and the five specialist roles.

### Boundaries

* Included: Read-only deterministic analysis and evidence through a durable, pollable run
* Excluded: Recommendation decisions and transformation

### Likely Targets

* src/shaper/application/assessment.py: Document-level report builder and new detectors
* src/shaper/domain/assessment.py: Compatible finding extensions
* src/shaper/application/orchestration.py: Estate-scoped agent composition
* src/shaper/application/estates.py: Discovery lifecycle persistence
* tests/test_assessment.py and tests/test_orchestration.py

### Dependencies

* P01-P02

### Validation Expectations

* Verify deterministic scoring, zero model calls, explicit unavailable metrics, coverage, document relationships, agent ownership, durable statuses, cancellation, partial failure, lease recovery, and no source mutation.

### Completion Evidence

* Every current document version in a run of at most 500 documents has one report or an explicit document failure.
* The estate summary references the same document IDs and versions.
* Larger snapshots fail before dispatch with guidance to narrow the source set.

### Unresolved Items

* Scores remain explicitly uncalibrated heuristics.

<!-- rpi:task id=P03-T01 -->
### P03-T01: Produce Per-Document Readiness and Effort Reports

#### Context

Structure, readability, metadata, freshness, retrieval, FAQ, procedure, and chunking helpers already exist.

#### Intent

Expose those signals per document and add long-paragraph and cross-policy-reference evidence plus a transparent effort model.

#### Boundaries

* Included: Deterministic rules, evidence excerpts or locations, coverage, severity, effort points, effort band, and rationale
* Excluded: Model-authored scores and claims of answer accuracy

#### Likely Targets

* src/shaper/application/assessment.py: Reusable scorers and document report assembly
* src/shaper/domain/assessment.py and src/shaper/domain/estate.py: Findings and report contracts
* tests/test_assessment.py: Threshold, coverage, and regression cases

#### Dependencies

* P01-T01
* Inventory profiles from P02

#### Validation Expectations

* Long paragraphs and unresolved or opaque cross-policy references generate document-scoped findings.
* Effort points map deterministically to named bands and list contributing interventions.
* Aggregating document-scoped metric scores reproduces existing estate dimensions where semantics are unchanged.

#### Completion Evidence

* Fixture reports are stable and explain every score and effort result.

#### Unresolved Items

* Calibrated effort prediction remains a follow-up after observed transformation data exists.

<!-- rpi:task id=P03-T02 -->
### P03-T02: Compose Estate-Level Specialist-Agent Results

#### Context

Document reports do not replace duplicate, contradiction, topic, authority, governance, or aggregate readiness analysis.

#### Intent

Run all five agents deterministically over a discovery snapshot and persist distinct role outputs and one orchestrated summary through a durable run.

#### Boundaries

* Included: Queued, running, partial, completed, cancelling, cancelled, and failed states; leases; checkpoints; Assessment evidence; knowledge relationships; transformation opportunity categories; governance conditions; and readiness prioritization
* Excluded: Model calls, transformation proposals for unselected documents, and all approval authority

#### Likely Targets

* src/shaper/application/orchestration.py: Estate discovery entry point
* src/shaper/domain/platform.py: Compatible estate result references where required
* src/shaper/application/estates.py: Discovery state and persistence
* tests/test_orchestration.py: Agent responsibility and no-authority assertions

#### Dependencies

* P03-T01

#### Validation Expectations

* All five roles execute or return explicit unavailable evidence.
* No `ModelGateway` call occurs during discovery.
* Relationship findings preserve every affected document.
* The orchestrator controls order and persistence without allowing an agent to mutate workflow state directly.
* Expired leases resume from the latest safe checkpoint and retain prior attempt evidence.

#### Completion Evidence

* One discovery run can be reconstructed from stored agent results and document versions.

#### Unresolved Items

* None

<!-- rpi:phase id=P04 -->
## P04: Recommend, Estimate, and Decide

### Context

Current recommendations group document IDs at estate level. The requested workflow starts from user selection and needs detailed proposed changes and token estimates before approval.

### Intent

Create immutable, selection-scoped proposals and version-pinned human decisions through durable, pollable runs.

### Boundaries

* Included: Proposed changes, outputs, rationale, risk, effort, token estimate, approval, decline, run status, cancellation, and partial failure
* Excluded: All model execution before approval

### Likely Targets

* src/shaper/application/orchestration.py: Selection-scoped Transformation Agent path
* src/shaper/application/token_estimation.py: Deterministic estimator
* src/shaper/application/decisions.py: Decision state machine
* src/shaper/application/estates.py: Recommendation lifecycle
* tests/test_token_estimation.py, tests/test_decisions.py, tests/test_orchestration.py

### Dependencies

* P01 and P03

### Validation Expectations

* Verify the 100-document run bound, selection boundaries, estimate invariants, zero model calls across recommendation and estimation, role authorization, stale-version rejection, and optimistic concurrency.

### Completion Evidence

* Every selected current document has a reviewable proposal and estimate.
* Every decision is attributable and immutable.

### Unresolved Items

* None

<!-- rpi:task id=P04-T01 -->
### P04-T01: Generate Selection-Scoped Recommendations

#### Context

Recommendations must explain proposed changes for each selected file rather than present only aggregate interventions.

#### Intent

Have the Transformation Agent deterministically build document proposals grounded in the selected discovery evidence.

#### Boundaries

* Included: A durable run of at most 100 selected document IDs, discovery ID, source versions, proposed interventions, expected artifact, evidence IDs, rationale, risk, and effort
* Excluded: Model calls, unselected documents, and transformation output generation

#### Likely Targets

* src/shaper/application/orchestration.py: Transformation Agent proposal entry point
* src/shaper/application/estates.py: Selection validation and run persistence
* src/shaper/domain/estate.py: Recommendation contracts
* tests/test_orchestration.py and tests/test_estates.py

#### Dependencies

* P03

#### Validation Expectations

* Reject unknown, duplicate, withdrawn, or stale document selections.
* Reject more than 100 selections before dispatch.
* Assert zero `ModelGateway` calls.
* Preserve traceability to findings and agent evidence.

#### Completion Evidence

* Proposal count and document IDs exactly equal the valid selected set.

#### Unresolved Items

* None

<!-- rpi:task id=P04-T02 -->
### P04-T02: Estimate and Cap Transformation Tokens

#### Context

The runtime already counts actual provider tokens and enforces a cap, but callers currently choose that cap without an estimate.

#### Intent

Create a deterministic estimator that gives users a transparent range and supplies the enforced job maximum.

#### Boundaries

* Included: Source token approximation, fixed prompt and schema overhead, transformation-kind output factors, repair allowance, estimator and model version, confidence, and assumptions
* Excluded: A model call for estimation and an exact-cost promise

#### Likely Targets

* src/shaper/application/token_estimation.py: Estimation algorithm
* src/shaper/domain/estate.py: `TokenEstimate`
* tests/test_token_estimation.py: Pure-function and boundary tests

#### Dependencies

* P04-T01
* Model deployment configuration

#### Validation Expectations

* Lower estimates do not exceed upper estimates.
* Maximum is at least the upper total and respects platform quota.
* Equivalent source version, transformation kind, model, and estimator version yield equivalent estimates.
* Estimation invokes no `ModelGateway`.

#### Completion Evidence

* Every proposed transformation displays an input range, output range, expected total, maximum, assumptions, and confidence.

#### Unresolved Items

* Initial approximation is labeled and later calibrated from actual usage.

<!-- rpi:task id=P04-T03 -->
### P04-T03: Record Pre-Transformation Decisions

#### Context

Existing output review cannot satisfy approval-before-transformation.

#### Intent

Add a distinct decision service for approve and decline outcomes before job creation.

#### Boundaries

* Included: Actor, reason, outcome, recommendation version, source version, expected revision, time, and invalidation
* Excluded: Post-output review decisions

#### Likely Targets

* src/shaper/application/decisions.py: State transitions and authorization
* src/shaper/application/estates.py: Decision commands and queries
* tests/test_decisions.py: Outcome, concurrency, and invalidation matrix

#### Dependencies

* P04-T01-P04-T02

#### Validation Expectations

* Only authorized users decide.
* Source, recommendation, estimator-version, or model-deployment changes invalidate approval.
* Decline creates no runnable authorization.
* Every mutation requires the current revision.

#### Completion Evidence

* Approved and declined proposals remain separately queryable with complete provenance.

#### Unresolved Items

* None

<!-- rpi:phase id=P05 -->
## P05: Transform Approved Content and Publish Artifacts

### Context

The existing compiler shapes one upload, returns combined token usage, submits output to review, and publishes approved units into JSONL.

### Intent

Enforce the new pre-transform gate, retain actual accounting, and add named HTML derivatives without removing the current output-review and JSONL path.

### Boundaries

* Included: Authorized job dispatch, token cap, usage, HTML rendering, naming, collision handling, review, and immutable publication
* Excluded: Source changes

### Likely Targets

* src/shaper/application/jobs.py and src/shaper/application/compiler.py: Authorization and execution
* src/shaper/application/shaping.py and src/shaper/domain/models.py: Split actual accounting where required
* src/shaper/application/artifacts.py: HTML and names
* src/shaper/application/publication.py and src/shaper/infrastructure/compilation.py: Artifact publication
* tests/test_jobs_auth.py, tests/test_compilation.py, tests/test_artifacts.py, tests/test_publication.py

### Dependencies

* P01 and P04

### Validation Expectations

* Test fail-closed dispatch, source-version race, budget exhaustion, usage persistence, safe output, collision, post-output review, and release integrity.

### Completion Evidence

* One approved document produces one reviewed artifact and accounting record.
* Declined and stale documents produce neither model calls nor artifacts.

### Unresolved Items

* None

<!-- rpi:task id=P05-T01 -->
### P05-T01: Enforce Approved-Only Transformation

#### Context

Job submission currently accepts any authorized `SourceRef` and caller-supplied budget.

#### Intent

Require a current approval record and derive the job cap from the retained token estimate.

#### Boundaries

* Included: Recommendation, decision, source version, estimator version, model deployment, role, quota, idempotency, and cancellation checks
* Excluded: Automatic approval

#### Likely Targets

* src/shaper/application/jobs.py: Submission precondition
* src/shaper/application/compiler.py: Dispatch-time revalidation
* tests/test_jobs_auth.py and tests/test_compilation.py

#### Dependencies

* P04-T03

#### Validation Expectations

* Reject missing, declined, withdrawn, superseded, stale, cross-tenant, or over-quota authorization before `ModelGateway.generate`.
* Recheck source version, estimator version, and model deployment immediately before execution.
* A budget-exhausted terminal run cannot retry directly. The system creates a new estimate and requires a new approval while retaining the prior estimate and usage.

#### Completion Evidence

* Mock gateway call count remains zero for every rejected case.

#### Unresolved Items

* None

<!-- rpi:task id=P05-T02 -->
### P05-T02: Persist Actual Token Usage

#### Context

Provider input/output usage is available, but the shaping outcome collapses it and the compiler discards it.

#### Intent

Retain actual input and output tokens, calls, timing, model provenance, cap, and estimate variance for every terminal run.

#### Boundaries

* Included: Successful, abstained, budget-exhausted, cancelled, and failed terminal accounting
* Excluded: Retroactive reconstruction of historical runs

#### Likely Targets

* src/shaper/application/shaping.py: Separate token counters in outcome
* src/shaper/application/compiler.py: `AgentRun` and `TokenUsage` persistence
* src/shaper/domain/models.py and src/shaper/domain/estate.py: Accounting contracts
* tests/test_compilation.py: Terminal accounting cases

#### Dependencies

* P05-T01

#### Validation Expectations

* Persist provider counts without replacing the original estimate.
* Calculate signed and percentage variance safely, including zero estimates.
* Keep sensitive prompt content out of accounting.

#### Completion Evidence

* Run status APIs can return estimate and actual usage as distinct records.

#### Unresolved Items

* Monetary cost remains optional and must use deployment-owned pricing configuration if later enabled.

<!-- rpi:task id=P05-T03 -->
### P05-T03: Render, Review, and Publish Named HTML

#### Context

Current publication creates only `units.jsonl`; the requested output is a new artifact named at estate level.

#### Intent

Render deterministic safe HTML, route it through the separate output-review service and role check, and add it to an immutable artifact manifest. The same actor may hold pre-transform and output-review roles in this development increment; no separation-of-duties claim is made.

#### Boundaries

* Included: Semantic HTML, source and derivation metadata, naming policy, safe normalization, collision suffix, content hash, approval ID, and artifact retrieval
* Excluded: Source overwrite and arbitrary active content

#### Likely Targets

* src/shaper/application/artifacts.py: Renderer and resolver
* src/shaper/application/publication.py: Artifact bundle assembly
* src/shaper/infrastructure/compilation.py and src/shaper/infrastructure/filesystem_sink.py: Storage
* tests/test_artifacts.py and tests/test_publication.py

#### Dependencies

* P05-T01-P05-T02
* Existing output review service

#### Validation Expectations

* Escape untrusted content.
* Reject traversal and reserved names.
* Resolve collisions with a deterministic source-ID suffix.
* Verify artifact and manifest hashes.
* Require a current output approval before publication.
* Keep output review separate by record, service, and role even when one development actor holds both roles.

#### Completion Evidence

* Repeated rendering from equivalent approved content is byte-identical.
* The source content remains unchanged.

#### Unresolved Items

* None

<!-- rpi:phase id=P06 -->
## P06: Expose Durable APIs and the Live Product Experience

### Context

The current platform analysis is synchronous and stateless, the browser experience uses a public fixed sample, and deployed SQLite state is revision-local.

### Intent

Provide persistent adapters, complete authenticated REST resources, and an accessible live interface.

### Boundaries

* Included: Local and Azure persistence, API, interactive browser session, UI, and changed-surface verification
* Excluded: A new frontend framework

### Likely Targets

* src/shaper/infrastructure/sqlite.py and src/shaper/infrastructure/postgres.py
* src/shaper/interfaces/http.py, src/shaper/interfaces/auth.py, src/shaper/interfaces/hosted.py, src/shaper/interfaces/cli.py, src/shaper/config.py
* prototype/copilot-studio-knowledge-compiler/index.html, app.js, and styles.css
* tests/test_estate_repository.py, tests/test_sqlite.py, and tests/test_interfaces.py

### Dependencies

* P01-P05

### Validation Expectations

* Use repository contract tests, API boundary tests, auth tests, browser interaction, accessibility tree, and adaptive-rendering checks.

### Completion Evidence

* The local and Azure profiles serve the same domain workflow.
* The UI completes the journey against live endpoints.

### Unresolved Items

* None

<!-- rpi:task id=P06-T01 -->
### P06-T01: Implement Local and Production Persistence

#### Context

Generic SQLite records are reusable locally, but production state must survive Container Apps revisions.

#### Intent

Implement the repository contracts with SQLite for development and PostgreSQL for Azure. Production PostgreSQL owns internal collection grants, estates, sources, documents, connector checkpoints, discovery and recommendation runs, reports, recommendations, pre-transform decisions, compile jobs, candidates, review records, shaping checkpoints, outbox events, agent runs, token usage, artifact manifests, and current release pointers. Azure Files retains source and artifact bytes.

#### Boundaries

* Included: Schema migrations, indexes, JSON payloads where appropriate, transactions, revisions, idempotency, and repository contract parity
* Excluded: Cross-region disaster recovery

#### Likely Targets

* src/shaper/infrastructure/sqlite.py: Local tables and repositories
* src/shaper/infrastructure/postgres.py: Production adapter
* src/shaper/config.py and src/shaper/interfaces/cli.py: Adapter selection
* pyproject.toml and uv.lock: PostgreSQL driver
* tests/test_estate_repository.py and tests/test_sqlite.py

#### Dependencies

* P01-T02

#### Validation Expectations

* Run identical repository contract cases against SQLite and a disposable PostgreSQL test instance when available.
* Keep the PostgreSQL adapter inside the package coverage threshold. Use adapter-level fake connections to cover branches when a live service is unavailable; do not add a coverage omission.
* Verify transaction rollback and stale revisions.

#### Completion Evidence

* The production profile refuses to start without durable-store configuration.
* Local development continues without PostgreSQL.
* Expired run and job leases recover queued work after a process or revision change.

#### Unresolved Items

* A live PostgreSQL contract run remains environment-dependent, but adapter-level tests must satisfy the normal coverage gate.

<!-- rpi:task id=P06-T02 -->
### P06-T02: Add Authenticated Estate REST Resources

#### Context

Existing authenticated APIs use bearer tokens, while a same-origin browser needs interactive sign-in.

#### Intent

Expose workflow resources and accept either the existing validated bearer principal or a trusted Container Apps authenticated principal in the production ingress path. Browser tenant and object claims resolve through PostgreSQL collection grants; an Entra bootstrap-administrator role authorizes grant administration.

#### Boundaries

* Included: Estate, source, upload, discovery, recommendation, decision, transformation, usage, artifact, collection-grant, archive, purge, paging, status, and browser-session endpoints
* Excluded: Client credentials in browser code and weakening MCP authentication

#### Likely Targets

* src/shaper/interfaces/http.py: Routes and response contracts
* src/shaper/interfaces/auth.py: Strict principal resolution
* src/shaper/interfaces/hosted.py: Public static-shell and protected-data path boundary
* src/shaper/interfaces/cli.py: Service composition
* src/shaper/config.py: Auth mode and trusted-ingress configuration
* tests/test_interfaces.py

#### Dependencies

* P02-P06-T01

#### Validation Expectations

* Test tenant and collection boundaries, internal grants, no-grant 403 behavior, roles, malformed payloads, stale revisions, paging, idempotency, unsupported auth headers, and trusted-ingress gating.
* Ignore ingress principal headers unless trusted-ingress mode is explicitly enabled, never merge them with bearer claims, and reject requests that present both identity modes.
* Keep health, `GET /v1/demo/analysis`, `/concept/`, and static assets explicitly public. Require authentication for every estate data and action endpoint.

#### Completion Evidence

* OpenAPI exposes the full workflow.
* Existing bearer clients and MCP initialization remain green.
* Browser users receive only roles present in current internal collection grants.

#### Unresolved Items

* None

<!-- rpi:task id=P06-T03 -->
### P06-T03: Replace the Demo-First UI with Live Estate Screens

#### Context

Knowledge Estates is a dead link and the current flow renders server-owned fixed sample data.

#### Intent

Implement screens for estate list, definition, sources, inventory and discovery, selection and recommendations, decisions, transformation progress, artifacts, archive, and purge. Use a compact Copilot Studio-like Fluent application shell with task-named tabs and durable deep links. Poll server-owned durable run resources rather than simulating progress.

#### Boundaries

* Included: Public signed-out shell; existing static HTML, CSS, and JavaScript surface; same-origin protected API; Copilot Studio-like Fluent web typography, navigation, tabs, command surfaces, and loading treatment; truthful status; durable run polling; partial results; retry; responsive state
* Excluded: New frontend framework and simulated success

#### Likely Targets

* prototype/copilot-studio-knowledge-compiler/index.html: Semantic screen structure and dialogs where needed
* prototype/copilot-studio-knowledge-compiler/app.js: Routing, authentication, API state, commands, polling, and errors
* prototype/copilot-studio-knowledge-compiler/styles.css: Responsive, focus, status, and table/card layouts

#### Dependencies

* P06-T02

#### Validation Expectations

* Verify signed-out, no-grant, loading, empty, unauthorized, authorization-required, partial-source failure, validation failure, conflict, progress, budget-exhausted, re-estimate, archive, purge, success, and retry states.
* Ensure selected-document count, token totals, and decision states come from live data.
* Compare the rendered estate list and workspace hierarchy against current Copilot Studio and Fluent web patterns, and verify a direct estate-stage URL remains on that estate and stage after initialization.

#### Completion Evidence

* A signed-in and granted user completes AC-01 through AC-20 without developer tools or mock state.

#### Unresolved Items

* None

<!-- rpi:task id=P06-T04 -->
### P06-T04: Verify Accessible Interaction Behavior

#### Context

Static scans cannot decide keyboard, focus, announcements, or adaptive rendering.

#### Intent

Apply adequate one-time verification methods to each changed interactive state and record evidence in the changes artifact.

#### Boundaries

* Included: Semantic structure, labels and errors, keyboard order, dialogs, focus placement and return, live status, busy state, 200% zoom, 320-pixel reflow, text spacing, target size, contrast, forced colors where available, and reduced motion
* Excluded: A claim of full organizational accessibility conformance

#### Likely Targets

* The three prototype files changed in P06-T03
* Browser validation evidence recorded in the implementation changes artifact

#### Dependencies

* P06-T03

#### Validation Expectations

* Static methods decide structure and basic name/role.
* Browser keyboard probes decide interaction.
* Accessibility-tree or manual AT checks decide computed name, role, and live announcements.
* Rendered states decide zoom, reflow, text spacing, and focus visibility.

#### Completion Evidence

* Every changed screen and asynchronous state has adequate evidence or an explicit unresolved accessibility blocker.
* `node --check prototype/copilot-studio-knowledge-compiler/app.js` passes.

#### Unresolved Items

* A qualified-human production review and committed browser accessibility regression harness remain outside this implementation claim and are accepted residual risks.

<!-- rpi:phase id=P07 -->
## P07: Deploy and Prove the Azure Workflow

### Context

The current Azure deployment has Container Apps, Entra API authentication, Azure OpenAI, Azure Files, and ClamAV, but not durable relational workflow storage or browser sessions.

### Intent

Provision the missing Azure controls, update documentation, deploy, and prove the complete journey.

### Boundaries

* Included: Development environment deployment and evidence
* Excluded: Production launch approval and multi-region resilience

### Likely Targets

* bicep/main.bicep and bicep/dev.bicepparam
* scripts/deploy.sh
* Dockerfile where runtime dependencies change
* docs/architecture.md, docs/deployment.md, and README.md
* tests/test_architecture.py

### Dependencies

* P01-P06
* Azure and Entra permissions

### Validation Expectations

* Compile infrastructure, deploy, inspect revision health, authenticate browser and API clients, test estate and queued-run persistence plus expired-lease recovery across revision, and complete the user workflow.

### Completion Evidence

* The live URL serves the new workflow and all AC-01-AC-20 evidence is recorded.

### Unresolved Items

* SharePoint live sync remains externally blocked if Graph consent is unavailable; the rest of the workflow must still deploy and the UI must show the true blocker.

<!-- rpi:task id=P07-T01 -->
### P07-T01: Provision PostgreSQL and Interactive Entra Authentication

#### Context

The production profile needs a durable database and the browser cannot use the existing client-credential smoke identity.

#### Intent

Add PostgreSQL Flexible Server, passwordless managed-identity access, Container Apps built-in Entra authentication for same-origin browser sessions, a bootstrap-administrator app role, and internal collection grants.

#### Boundaries

* Included: Least-privilege network and data-plane access, application settings, auth callback, explicit anonymous paths, bootstrap administrator assignment, internal grant bootstrap, public fixed demo, and existing bearer flow
* Excluded: Passwords in parameters, outputs, logs, or source

#### Likely Targets

* bicep/main.bicep: Database, identity access, Container Apps auth configuration, and settings
* bicep/dev.bicepparam: Non-secret development values
* scripts/deploy.sh: Entra callback or principal bootstrap and smoke flow
* src/shaper/config.py: Required settings
* Dockerfile and dependency locks: PostgreSQL runtime

#### Dependencies

* P06-T01-P06-T02
* Entra and PostgreSQL administrator capability

#### Validation Expectations

* Bicep compiles.
* Deployment logs contain no secrets.
* Health remains reachable.
* Browser session, bearer API, and MCP bearer flows each authenticate as designed.
* An authenticated but ungranted browser principal receives 403.

#### Completion Evidence

* The deployed application writes and reads PostgreSQL with managed identity and serves an authenticated browser estate session.

#### Unresolved Items

* None

<!-- rpi:task id=P07-T02 -->
### P07-T02: Update Architecture and Operations Documentation

#### Context

Current documentation describes stateless analysis and local SQLite state.

#### Intent

Document the implemented estate lifecycle and preserve the explicit multi-agent platform positioning.

#### Boundaries

* Included: C4 components, data flow, durable run bounds, agent responsibilities, two decision gates, token estimates and actuals, PostgreSQL record ownership, auth and internal grants, public and protected paths, archive, purge, non-sensitive development-data classification, source states, deployment, and limitations
* Excluded: Unsupported connector claims

#### Likely Targets

* docs/architecture.md: Updated C4 and component responsibilities
* docs/deployment.md: Resources, auth, database, Graph dependency, and operations
* README.md: Current MVP and live workflow
* tests/test_architecture.py: Current enforced architecture assertions

#### Dependencies

* Implemented P01-P07-T01 behavior

#### Validation Expectations

* Documentation matches deployed behavior.
* "Shaper is not an agent" and all five agent-role names remain explicit.

#### Completion Evidence

* Architecture tests and documentation-specific checks pass.

#### Unresolved Items

* None

<!-- rpi:task id=P07-T03 -->
### P07-T03: Run End-to-End Deployment Validation

#### Context

The outcome is not complete until it is observable at the Azure URL and persists across revisions.

#### Intent

Run the smallest targeted checks during implementation, then the complete regression and deployment proof.

#### Boundaries

* Included: Python, JavaScript, infrastructure, shell, REST, MCP, database, browser, accessibility, and deployment evidence
* Excluded: Unsupported production SLA claims

#### Likely Targets

* Existing test suite and validation commands
* scripts/deploy.sh: Smoke tests
* Live Container Apps revision and hosted concept
* .copilot-tracking/changes/2026-09-10/knowledge-estate-workflow-redesign-changes.md: Implementation evidence

#### Dependencies

* P01-P07-T02

#### Validation Expectations

* Run targeted pytest selections, full pytest with current coverage requirement, Ruff, strict mypy, `node --check prototype/copilot-studio-knowledge-compiler/app.js`, Bicep compilation, shell syntax, authenticated REST and MCP smoke, estate and queued-run revision persistence, expired-lease recovery, and browser methods from P06-T04.

#### Completion Evidence

* All AC-01-AC-20 pass or the task stops with the exact unresolved blocker.
* Temporary credentials and test data are removed.

#### Unresolved Items

* None
