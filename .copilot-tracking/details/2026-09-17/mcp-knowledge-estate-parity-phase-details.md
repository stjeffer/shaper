<!-- markdownlint-disable-file -->
# RPI Phase Details: MCP Knowledge Estate Workflow Parity

## Metadata

* Task ID: MCP-KNOWLEDGE-ESTATE-PARITY-2026-09-17
* Task slug: mcp-knowledge-estate-parity
* Related plan: .copilot-tracking/plans/2026-09-17/mcp-knowledge-estate-parity-plan.md
* Evidence sources: Current application services, HTTP and MCP adapters, domain
  models, interface tests, deployment guidance, operations guidance, and BRD

## Task-Level Context

The codebase already has a thin MCP adapter and a much broader REST adapter.
Both run in one ASGI process and resolve the same principal model. The work
therefore centers on defining safe MCP contracts, injecting existing services,
and proving behavioral parity. Business logic must not move into or be copied
into the MCP interface.

The browser previously generated evaluation suggestions locally. That behavior
was the only listed capability without an application-owned service contract
and has moved into a deterministic application service for REST and MCP use.

MCP tool annotations improve client presentation but do not enforce human
approval. Authorization, exact object identity, optimistic concurrency, reason
text, stale-source checks, and complete finding acknowledgment remain
server-side requirements.

The pinned `mcp==1.13.1` implementation has been inspected. FastMCP function
resources accept raw `bytes`, and tool registration accepts `ToolAnnotations`
with read-only, destructive, idempotent, and open-world hints. Approved HTML
will therefore use a binary resource directly rather than base64.

## Phase Index

| Phase ID | Name | Status | Detail sections |
|---|---|---|---|
| P01 | Define MCP contracts and shared boundaries | Complete | P01, P01-T01, P01-T02 |
| P02 | Add read and evidence surfaces | Complete | P02, P02-T01, P02-T02, P02-T03 |
| P03 | Add governed workflow mutations | Complete | P03, P03-T01, P03-T02, P03-T03 |
| P04 | Add artifact governance and exact export | Complete | P04, P04-T01, P04-T02 |
| P05 | Validate, document, and deploy | In progress: P05-T01 and P05-T02 complete; P05-T03 pending | P05, P05-T01, P05-T02, P05-T03 |

<!-- rpi:phase id=P01 -->
## P01: Define MCP contracts and shared boundaries

### Context

The current MCP interface declares four tools inline and returns application
model dumps. The REST adapter also contains some response assembly and the
browser owns evaluation suggestion generation. Adding many more inline closures
without contracts would make parity difficult to test and maintain.

### Intent

Define stable tool names, schemas, annotations, error categories, and shared
presenters before exposing new operations.

### Boundaries

* Included: Contract inventory, MCP service dependencies, error mapping,
  annotations, shared response assembly, and evaluation generation.
* Excluded: New assessment logic, transformation rules, and raw file transport.

### Likely Targets

* src/shaper/interfaces/mcp_server.py: Expand the MCP adapter.
* src/shaper/interfaces/http.py: Reuse extracted presenters and evaluation
  service without changing HTTP behavior.
* src/shaper/application/estate_views.py: Candidate shared read-model and
  response assembly service.
* src/shaper/application/evaluation_sets.py: Candidate deterministic evaluation
  suggestion service.
* src/shaper/interfaces/cli.py: Inject the additional application services.
* src/shaper/domain/estate.py: Add request or response models only where shared
  domain contracts are justified; do not add a new domain module.

### Dependencies

* Confirm the installed FastMCP annotation and binary resource APIs from the
  locked dependency version during implementation.

### Validation Expectations

* Every planned tool maps to one existing or newly extracted application
  service method.
* Every mutation lists its required role, concurrency input, idempotency
  behavior, and annotation.
* Existing tool names and resource URIs remain unchanged.
* Every non-idempotent mutation is marked `idempotentHint=false`.

### Completion Evidence

* Contract tests enumerate the complete tool and resource set with schemas and
  annotations.
* No interface adapter calls another interface adapter.

### Unresolved Items

* None.

<!-- rpi:task id=P01-T01 -->
### P01-T01: Define tool and resource contracts

#### Context

Recommended names should use one consistent namespace, such as
`estate.list`, `estate.get`, `estate.create`, `estate.update`,
`estate.source.register`, `estate.document.list`, `estate.discovery.start`,
`estate.report.list`, `estate.recommendation.start`, `estate.proposal.list`,
`estate.proposal.decide`, `estate.transformation.start`,
`estate.artifact.list`, `estate.artifact.approve`, and
`estate.evaluation.list`. Exact names are finalized in a contract test before
implementation.

Read tools receive read-only annotations. Creation and workflow-start tools
receive mutating, non-destructive annotations. Proposal decisions and artifact
approval receive mutating annotations and explicit confirmation-oriented
descriptions. Purge is not exposed.

#### Intent

Create a compact, predictable MCP API that an agent can discover without
guessing REST routes.

#### Boundaries

* Included: Names, descriptions, JSON schemas, result envelopes, roles, error
  categories, and annotations.
* Excluded: Tool implementation.

#### Likely Targets

* src/shaper/interfaces/mcp_server.py: Tool registration and contract helpers.
* tests/test_interfaces.py: Tool-set, schema, annotation, and compatibility
  assertions.

#### Dependencies

* Existing Pydantic domain and request constraints.

#### Validation Expectations

* Inputs forbid unknown fields where practical.
* List results use stable `items` envelopes.
* Versioned records always include revision metadata.
* Mutation results expose resulting identities and current revisions.

#### Completion Evidence

* A test-owned contract snapshot covers all tools and resources.

#### Unresolved Items

* None.

<!-- rpi:task id=P01-T02 -->
### P01-T02: Extract shared response and evaluation services

#### Context

The REST adapter assembles estate summaries and workflow result envelopes.
Evaluation questions are generated in prototype JavaScript. MCP parity requires
one application-owned implementation, not a second translation of browser
logic.

#### Intent

Move reusable presentation and deterministic evaluation behavior behind typed
application boundaries while keeping existing REST output stable.

#### Boundaries

* Included: Estate summary presenter, workflow read model, deterministic
  evaluation-set generator, and browser integration with the shared endpoint.
* Excluded: Model-generated questions and quantitative artifact scoring.

#### Likely Targets

* src/shaper/application/estate_views.py: Shared authorized read projections.
* src/shaper/application/evaluation_sets.py: Shared grounded-question
  generation.
* src/shaper/interfaces/http.py: Delegate existing response assembly.
* prototype/copilot-studio-knowledge-compiler/app.js: Consume shared evaluation
  results.
* tests/test_estate_interfaces.py: Preserve REST contracts.
* tests/test_estate_interfaces.py: Add deterministic generation and preserved
  REST behavior tests.
* tests/test_interfaces.py: Add MCP evaluation contract and parity tests.

#### Dependencies

* Current source-retention and proposal models.

#### Validation Expectations

* Up to 20 distinct questions remain balanced across documents.
* Sparse estates return fewer questions.
* Source identifiers and evidence remain attached.
* The grounded evaluation-set service does not import, wrap, or expose
  `application/evaluation.py` quality-score models.
* MCP evaluation schemas contain no `score` or `scores` field.

#### Completion Evidence

* Browser, REST, and MCP receive equivalent evaluation data from one service.

#### Unresolved Items

* None.

<!-- rpi:phase id=P02 -->
## P02: Add read and evidence surfaces

### Context

Agents need current state before they can safely propose or invoke actions. Read
parity should land before mutations so the decision context and revisions are
available.

### Intent

Expose authorized, structured, findings-led views of all Knowledge Estate
workflow state.

### Boundaries

* Included: Metadata, findings, evidence, agent impact, decisions, usage, and
  bounded content resources.
* Excluded: Mutations and unrestricted content dumps.

### Likely Targets

* src/shaper/interfaces/mcp_server.py: Read tools and resources.
* src/shaper/application/estate_views.py: Authorized projections.
* src/shaper/interfaces/cli.py: Service wiring.
* tests/test_interfaces.py: MCP behavior and authorization.

### Dependencies

* P01 contracts and shared projections.

### Validation Expectations

* Query-role and cross-tenant boundaries are tested for every resource family.
* Findings include rule, severity, evidence, remedy, and agent impact where
  present in the stored report.
* No aggregate readiness score is added.

### Completion Evidence

* An MCP SDK client lists and calls every read tool and resource in tests.

### Unresolved Items

* None.

<!-- rpi:task id=P02-T01 -->
### P02-T01: Add estate, source, document, run, and report tools

#### Context

EstateService and related services already enforce query authorization. Some
repository reads currently rely on a preceding estate authorization in the REST
adapter; the shared application read service must preserve that order.

#### Intent

Provide complete discovery context without leaking records across estates,
collections, or tenants.

#### Boundaries

* Included: Assessment-check catalog, estate list and get, source list, document
  list, run list and get, and discovery report list.
* Excluded: Source registration and run creation.

#### Likely Targets

* src/shaper/application/estate_views.py
* src/shaper/interfaces/mcp_server.py
* tests/test_interfaces.py

#### Dependencies

* P01-T02.

#### Validation Expectations

* Cross-estate run and document identifiers are rejected.
* Document source-retention availability is explicit.
* Reports are returned only after estate authorization.

#### Completion Evidence

* Positive and negative MCP SDK tests pass for every read family.

#### Unresolved Items

* None.

<!-- rpi:task id=P02-T02 -->
### P02-T02: Add proposal, decision, artifact, usage, and evaluation tools

#### Context

These records supply the evidence and exact identities required by later
mutations.

#### Intent

Allow clients to build a complete review context before invoking a decision or
approval.

#### Boundaries

* Included: Proposal lists, current decisions, transformation runs, token
  usage, artifact metadata and findings, review revisions, and evaluations.
* Excluded: Proposal decisions and artifact approval.

#### Likely Targets

* src/shaper/application/estate_views.py
* src/shaper/application/evaluation_sets.py
* src/shaper/interfaces/mcp_server.py
* tests/test_interfaces.py

#### Dependencies

* P01-T02 and P02-T01.

#### Validation Expectations

* Proposal output includes source version and token estimate.
* Artifact output includes current revision, review revision, status, content
  hash, and finding identities.
* Legacy artifact evaluation scores remain excluded.

#### Completion Evidence

* Read results contain every input needed by P03 and P04 mutations.

#### Unresolved Items

* None.

<!-- rpi:task id=P02-T03 -->
### P02-T03: Add bounded content resources

#### Context

MCP resources fit retrievable content better than large tool responses.
Artifact content is already hash-verified and role-gated by the transformation
service.

#### Intent

Expose current document text, reviewer preview, and approved HTML without
weakening content authorization.

#### Boundaries

* Included: Current normalized document text, review preview, and approved HTML.
* Excluded: Original binary source downloads and unbounded collection exports.

#### Likely Targets

* src/shaper/interfaces/mcp_server.py
* src/shaper/application/artifacts.py
* tests/test_interfaces.py
* tests/test_artifacts.py

#### Dependencies

* P02-T01 and P02-T02.

#### Validation Expectations

* Reviewer preview requires review role.
* Approved HTML requires query role and approved status.
* HTML resource bytes match stored bytes and REST download.
* Resource metadata includes media type, filename, and content hash.

#### Completion Evidence

* Exact-byte, status, and role tests pass through a real MCP SDK client.

#### Unresolved Items

* Confirm whether the locked FastMCP resource API accepts raw bytes. If it does
  not, return base64 with explicit encoding and verify decoded byte equality.

<!-- rpi:phase id=P03 -->
## P03: Add governed workflow mutations

### Context

The existing services enforce collection roles, estate lifecycle, stale-source
checks, proposal identity, and transformation limits. MCP must call those
services directly and add no alternate authority.

### Intent

Enable safe orchestration from MCP while making consequential operations clear
to clients.

### Boundaries

* Included: Estate create and update, source registration, discovery,
  recommendation, proposal decision, and transformation.
* Excluded: Estate purge, document deletion, raw upload, and new workflow
  semantics.

### Likely Targets

* src/shaper/interfaces/mcp_server.py
* src/shaper/interfaces/cli.py
* tests/test_interfaces.py
* tests/test_estate_interfaces.py

### Dependencies

* P01 and P02.

### Validation Expectations

* Every mutation is role-tested and uses existing service validation.
* Responses return current persisted state, not success-shaped placeholders.
* Tool annotations reflect mutation risk.

### Completion Evidence

* End-to-end MCP tests progress a staged document through artifact generation.

### Unresolved Items

* None.

<!-- rpi:task id=P03-T01 -->
### P03-T01: Add estate and source mutations

#### Context

Estate creation and update are straightforward service adapters. Source
registration records a location but does not synchronize it. Binary upload is
multipart REST with bounded reads, malware scanning, ZIP expansion, and
inventory ingestion.

#### Intent

Expose safe metadata mutations while retaining the proven upload boundary.

#### Boundaries

* Included: Estate create and update and URL or SharePoint source registration.
* Excluded: Base64 uploads, archive and purge, and unsupported synchronization.

#### Likely Targets

* src/shaper/interfaces/mcp_server.py
* docs/mcp.md
* tests/test_interfaces.py

#### Dependencies

* Authenticated REST upload remains operational.

#### Validation Expectations

* The MCP result explains that registered URL and SharePoint sources remain
  pending until connector synchronization.
* Upload instructions return the REST staging route and expected next MCP call.

#### Completion Evidence

* MCP can create an estate and register a source; a REST-staged upload appears
  in MCP document inventory.

#### Unresolved Items

* None.

<!-- rpi:task id=P03-T02 -->
### P03-T02: Add discovery and recommendation mutations

#### Context

Both operations are synchronous and bounded by current document selection
limits. Their services return persisted run records and reports or proposals.

#### Intent

Expose assessment and recommendation generation with complete stored outcomes.

#### Boundaries

* Included: Discovery start and recommendation start.
* Excluded: New background execution model.

#### Likely Targets

* src/shaper/interfaces/mcp_server.py
* tests/test_interfaces.py

#### Dependencies

* P02 read surfaces.

#### Validation Expectations

* Recommendation input requires a discovery run from the same estate.
* Selected document identifiers remain bounded and unique.
* Provider failures are reported without fabricated results.

#### Completion Evidence

* MCP responses match normalized REST results for the same service fixtures.

#### Unresolved Items

* None.

<!-- rpi:task id=P03-T03 -->
### P03-T03: Add proposal decision and transformation mutations

#### Context

Proposal decisions require review role, reason, and expected current decision
identity. Transformations require approved proposals and can request one
optional preservation repair.

#### Intent

Expose the central governed transformation path without bypassing decisions or
validation.

#### Boundaries

* Included: Approve or decline proposal and start transformation.
* Excluded: Automatic proposal approval, repeated repair loops, and mutation of
  generated artifacts.

#### Likely Targets

* src/shaper/interfaces/mcp_server.py
* tests/test_interfaces.py
* tests/test_shaping.py

#### Dependencies

* P02-T02.

#### Validation Expectations

* Decision conflicts and stale proposals fail.
* Transformations reject unapproved proposals and cross-estate selections.
* `enforce_preservation_checks` retains its current meaning: request at most one
  repair, not make diagnostics universally blocking.

#### Completion Evidence

* Tests cover review mode, optional repair, persisted findings, provider
  failure, and integrity blocking through MCP.

#### Unresolved Items

* None.

<!-- rpi:phase id=P04 -->
## P04: Add artifact governance and exact export

### Context

Artifact approval has the strongest governance requirements. The application
already requires review role, current review and artifact revisions, rationale,
and the exact set of validation finding rule identifiers.

### Intent

Expose review and publication without making MCP an alternate approval path.

### Boundaries

* Included: Review context, artifact approval, and approved HTML retrieval.
* Excluded: Approval without rationale, blanket acknowledgment, and unapproved
  publication.

### Likely Targets

* src/shaper/interfaces/mcp_server.py
* src/shaper/application/artifacts.py
* tests/test_interfaces.py
* tests/test_artifacts.py

### Dependencies

* P02 and P03.

### Validation Expectations

* Approval inputs are explicit and cannot default current revisions or finding
  acknowledgments.
* Exact stored bytes remain the publication output.

### Completion Evidence

* MCP end-to-end tests prove current-state approval and byte-identical export.

### Unresolved Items

* None.

<!-- rpi:task id=P04-T01 -->
### P04-T01: Add artifact approval

#### Context

Tool metadata can advise clients to request confirmation, but the server must
continue to rely on identity, role, exact revisions, rationale, and
acknowledgments.

#### Intent

Make approval explicit, reviewable, concurrency-safe, and auditable.

#### Boundaries

* Included: Current artifact and review identity, finding acknowledgments, and
  reason.
* Excluded: Inferred acknowledgment and automatic retries after conflict.

#### Likely Targets

* src/shaper/interfaces/mcp_server.py
* tests/test_interfaces.py
* tests/test_artifacts.py

#### Dependencies

* P02-T02.

#### Validation Expectations

* Every current finding identity must be acknowledged exactly once.
* Stale review or artifact revisions fail.
* The persisted decision records the authenticated principal.

#### Completion Evidence

* Positive approval and all rejection-path tests pass.

#### Unresolved Items

* None.

<!-- rpi:task id=P04-T02 -->
### P04-T02: Add approved HTML retrieval

#### Context

The existing content method requires query role, approved status, and a valid
content hash. MCP should expose that method directly as a content resource.

#### Intent

Allow downstream agents and ingestion workflows to retrieve exactly what a
reviewer approved.

#### Boundaries

* Included: Approved HTML content and metadata.
* Excluded: Unapproved preview for query-only principals.

#### Likely Targets

* src/shaper/interfaces/mcp_server.py
* tests/test_interfaces.py
* tests/test_artifacts.py

#### Dependencies

* P04-T01.

#### Validation Expectations

* Byte equality is tested against repository content and REST download.
* Incorrect stored hash fails instead of returning content.

#### Completion Evidence

* MCP consumers can save the retrieved content without transformation.

#### Unresolved Items

* None.

<!-- rpi:phase id=P05 -->
## P05: Validate, document, and deploy

### Context

The expanded public interface needs full contract, role, compatibility, and
operator coverage before deployment.

### Intent

Prove the MCP extension is safe, usable, compatible, and supportable.

### Boundaries

* Included: Existing test tools, documentation, smoke tests, deployment, and
  post-deployment verification.
* Excluded: New test frameworks and unrelated application changes.

### Likely Targets

* tests/test_interfaces.py
* tests/test_estate_interfaces.py
* tests/test_artifacts.py
* tests/test_architecture.py
* scripts/deploy.sh
* README.md
* docs/mcp.md
* docs/architecture.md
* docs/features.md
* docs/deployment.md
* docs/operations.md

### Dependencies

* P01 through P04.

### Validation Expectations

* Run targeted MCP, estate interface, artifact, shaping, and architecture tests.
* Run repository formatting, linting, strict typing, and full tests if targeted
  validation passes.
* Production smoke covers more than initialization.

### Completion Evidence

* All relevant checks pass and a healthy Container Apps revision serves the
  expanded MCP contract.

### Unresolved Items

* Production deployment and post-deployment smoke testing require a separate
  release action and short-lived smoke credentials.

<!-- rpi:task id=P05-T01 -->
### P05-T01: Add contract, parity, and security tests

#### Context

Existing MCP tests list exactly four tools and establish a real SDK connection.
They provide a base for expanded contract tests.

#### Intent

Test observable behavior and governance, not implementation details.

#### Boundaries

* Included: Tool listing, schemas, annotations, role matrix, cross-tenant
  denial, conflicts, findings, repair behavior, and exact bytes.
* Excluded: Redundant tests of unchanged domain internals.

#### Likely Targets

* tests/test_interfaces.py
* tests/test_estate_interfaces.py
* tests/test_artifacts.py
* tests/test_shaping.py
* tests/test_architecture.py

#### Dependencies

* P01 through P04.

#### Validation Expectations

* Each new tool has success and denied-access coverage.
* Consequential mutations include stale-state coverage.
* Existing query and compile semantics remain covered.

#### Completion Evidence

* Targeted and full repository validation passes at current coverage thresholds.

#### Unresolved Items

* None.

<!-- rpi:task id=P05-T02 -->
### P05-T02: Publish MCP usage and operations guidance

#### Context

Current documentation identifies the endpoint and authentication model but does
not describe the complete MCP tool workflow.

#### Intent

Give developers and operators a tested path from identity setup through
approved HTML retrieval.

#### Boundaries

* Included: Client configuration, token acquisition, role mapping, REST upload
  staging, tool examples, resources, errors, and troubleshooting.
* Excluded: Client-specific instructions that cannot be validated.

#### Likely Targets

* docs/mcp.md
* README.md
* docs/architecture.md
* docs/features.md
* docs/deployment.md
* docs/operations.md

#### Dependencies

* Final tool contracts and production URL conventions.

#### Validation Expectations

* Examples use placeholders and no secrets.
* Every documented tool name and argument is contract-tested.
* Limitations distinguish registration from synchronization and REST upload
  from MCP orchestration.

#### Completion Evidence

* A clean client can initialize, list tools, and follow the documented workflow.

#### Unresolved Items

* None.

<!-- rpi:task id=P05-T03 -->
### P05-T03: Deploy and smoke test MCP parity

#### Context

The deployment script currently validates health and MCP initialization only.
Expanded public behavior needs a bounded authenticated read and authorization
check.

#### Intent

Verify the deployed revision serves the expected contract and enforces access.

#### Boundaries

* Included: Tool-list verification, authorized read, denied read, health,
  readiness, logs, and one staged end-to-end workflow.
* Excluded: Destructive production purge and broad load testing.

#### Likely Targets

* scripts/deploy.sh
* docs/deployment.md
* docs/operations.md

#### Dependencies

* Short-lived smoke identities with known allowed and denied collections.
* Approved Azure OpenAI and ClamAV capacity.

#### Validation Expectations

* Smoke output never prints bearer tokens.
* Failed MCP checks prevent declaring deployment success.
* One generated artifact can be reviewed, approved, and retrieved with exact
  bytes in a controlled smoke estate.

#### Completion Evidence

* Healthy revision, expected tool set, authorization evidence, workflow result,
  and no unexpected production errors.

#### Unresolved Items

* Production deployment and post-deployment smoke testing require a separate
  release action and short-lived smoke credentials.
