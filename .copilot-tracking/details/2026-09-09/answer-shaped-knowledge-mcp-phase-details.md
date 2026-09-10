<!-- markdownlint-disable-file -->
# RPI Phase Details: Agentic Answer-Shaped Knowledge Compiler

## Metadata

* Task ID: answer-shaped-knowledge-mcp
* Task slug: answer-shaped-knowledge-mcp
* Planning status: Ready
* Related plan: .copilot-tracking/plans/2026-09-09/answer-shaped-knowledge-mcp-plan.md
* Evidence sources: .copilot-tracking/research/2026-09-09/answer-shaped-knowledge-mcp-research.md

## Phase Index

| Phase ID | Name | Status | Detail sections |
|---|---|---|---|
| P01 | Establish foundation and contracts | Complete | P01, P01-T01 through P01-T03 |
| P02 | Implement secure source ingestion | Complete | P02, P02-T01 through P02-T03 |
| P03 | Implement bounded agentic shaping | Complete | P03, P03-T01 through P03-T03 |
| P04 | Implement validation and review | Complete | P04, P04-T01 through P04-T03 |
| P05 | Implement release publication and retrieval | Complete | P05, P05-T01 through P05-T03 |
| P06 | Expose jobs, review, query, and MCP interfaces | Complete | P06, P06-T01 through P06-T03 |
| P07 | Deploy and prove production operability | Blocked | P07, P07-T01 through P07-T04 |

<!-- rpi:phase id=P01 -->
## P01: Establish foundation and contracts

### Current Execution State

* Declared scope: Full plan.
* Active task: Implementation complete; ready for explicit Review.
* Approved write boundary: Planned production, test, schema, prompt, rubric,
  evaluation, documentation, and implementation-tracking targets.
* Validation intent: Targeted checks per task, phase completion checks, and the
  final local matrix; credential-dependent live suites remain opt-in.
* Blockers: None for implementation. Live checks require external credentials,
  an Azure subscription, tenant resources, and a representative corpus.
* Completed evidence: P01 format, lint, strict typing, 13 tests, 80.74 percent
  branch-aware coverage, schema drift, transaction, and architecture checks pass.
  P01 created 23 tracked files against its 24-file allowance.
* Completed evidence: P02 strict typing, lint, and 27 local tests pass.
  Upload rejection, scanner failure, expiry, SharePoint pagination and
  tombstones, content hashing, and PDF, DOCX, Markdown, and text parsing are covered.
* Completed evidence: P03 strict typing, lint, and 34 tests pass. Static
  capability checks prove the agent has four read-only tools; success, repair,
  abstention, unauthorized access, and independent model-call budget behavior are covered.
* Completed evidence: P04 strict typing, lint, and 39 tests pass. Deterministic
  grounding failures block publication, evaluator identity and input are pinned,
  review approval is role-authorized, and stale revisions fail explicitly.
* Completed evidence: P05 strict typing, lint, and 45 tests pass. Complete
  snapshots carry valid prior units, artifacts verify independently, manifest
  precedes current-pointer updates, stale pointer races fail, and query
  authorization is checked before hybrid ranking.

### Context

The repository is empty. Research selects a protocol-independent compiler and
query service, one bounded shaping agent, deterministic control and publication,
and adapters for SharePoint, uploads, models, indexes, and MCP.

### Intent

Create the executable Python baseline and stable contracts that every later
phase can implement independently.

### Boundaries

* Included: Toolchain, package structure, configuration, typed domain models,
  JSON Schemas, tenant/collection/principal authorization, ports, SQLite state,
  errors, and architecture rules.
* Excluded: External connector, model, agent, publication, query, and interface behavior.

### Likely Targets

* pyproject.toml and uv.lock: Python 3.11 project, dependencies, and validation tools.
* .gitignore: Credentials, `.venv`, caches, databases, uploads, indexes, and releases.
* src/shaper/domain/: Provider-neutral entities, values, states, and invariants.
* src/shaper/application/: Use cases and external-service protocols.
* src/shaper/infrastructure/: Adapter boundary.
* src/shaper/interfaces/: HTTP, CLI, and MCP boundary.
* tests/: Unit, contract, integration, security, evaluation, and architecture layout.

### Dependencies

* Completed research artifact.

### Validation Expectations

* `uv sync` creates `.venv` and installs from the lockfile.
* Ruff, mypy, and pytest run through `uv run`.
* Import tests prove dependency direction.
* The package imports without cloud credentials.

### Completion Evidence

* Toolchain and architecture tests pass.
* Exported schemas match committed canonical snapshots.
* SQLite migrations apply to an empty database and upgrade idempotently.
* P01 adds no more than 24 tracked files.

### Unresolved Items

* None. Runtime and initial adapter decisions are recorded in the plan baseline.

<!-- rpi:task id=P01-T01 -->
### P01-T01: Scaffold the project and quality gates

#### Context

The implementation needs a reproducible environment and one validation command
before behavior is added.

#### Intent

Create the Python package, dependency groups, typed configuration, logging
bootstrap, test hierarchy, and local validation commands.

#### Boundaries

* Included: Python 3.11, `uv`, Pydantic settings, structured logging, Ruff,
  mypy, pytest, coverage, and package markers.
* Excluded: Domain behavior and production credentials.

#### Likely Targets

* pyproject.toml, uv.lock, .python-version, .gitignore, README.md
* src/shaper/__init__.py, src/shaper/config.py, src/shaper/logging.py
* tests/conftest.py, tests/architecture/test_import_boundaries.py

#### Dependencies

* None.

#### Validation Expectations

* A fresh `uv sync` succeeds.
* Missing required production configuration raises a specific startup error only
  when the dependent adapter is selected.
* Logs are structured and source text is excluded by default.

#### Completion Evidence

* Format, lint, typing, import, and minimal test commands pass.

#### Unresolved Items

* None.

<!-- rpi:task id=P01-T02 -->
### P01-T02: Define domain schemas and invariants

#### Context

Evidence units are rebuildable derivatives linked to exact source versions.
Identity and state semantics must not depend on Graph, a model provider, or MCP.

#### Intent

Define immutable typed contracts and versioned JSON Schemas for the complete
source-to-release lifecycle.

#### Boundaries

* Included: `SourceRef`, `OutputRef`, `SourceDocument`, `SourceSpan`,
  `AnswerUnit`, `Claim`, `Applicability`, `AgentRun`, `ValidationFinding`,
  `ReviewDecision`, `CompileJob`, `ReleaseManifest`, `Tenant`, `Collection`,
  `Principal`, collection roles, source-permission snapshots, and state enums
  including `superseded` and `withdrawn`.
* Excluded: Persistence and adapter serialization details.

#### Likely Targets

* src/shaper/domain/sources.py
* src/shaper/domain/evidence.py
* src/shaper/domain/jobs.py
* src/shaper/domain/reviews.py
* src/shaper/domain/releases.py
* schemas/: Generated, committed versioned JSON Schema snapshots
* tests/unit/domain/

#### Dependencies

* P01-T01.

#### Validation Expectations

* Domain models reject invalid IDs, missing source spans, naive timestamps,
  unsupported transitions, unsafe paths, and inconsistent hashes.
* `unit_id` uses a stable derivation key; `unit_version` hashes canonical unit content.
* Schema version is explicit and unknown major versions fail closed.
* Pydantic models are canonical; a documented regeneration command updates
  schema snapshots and validation fails on uncommitted drift.

#### Completion Evidence

* Boundary-value and serialization round-trip tests pass.
* JSON Schema exports are deterministic.

#### Unresolved Items

* None.

<!-- rpi:task id=P01-T03 -->
### P01-T03: Define ports, state store, and dependency rules

#### Context

Research requires replaceable connectors and model/index implementations while
keeping workflow semantics stable.

#### Intent

Define application protocols and implement transactional SQLite repositories for
jobs, checkpoints, sources, candidates, review state, and release metadata.

#### Boundaries

* Included: `SourceConnector`, `UploadStore`, `DocumentParser`, `ModelGateway`,
  `AgentTool`, `Validator`, `Evaluator`, `ReviewRepository`, `ReleaseSink`,
  `EmbeddingProvider`, `LexicalIndex`, `VectorIndex`, identity, clock, ID, and
  transaction ports.
* Excluded: Real external adapters.

#### Likely Targets

* src/shaper/application/ports.py
* src/shaper/application/transactions.py
* src/shaper/infrastructure/sqlite.py
* src/shaper/infrastructure/migrations/
* tests/contract/test_repositories.py
* tests/architecture/test_import_boundaries.py

#### Dependencies

* P01-T02.

#### Validation Expectations

* Repository contract tests run against in-memory and file-backed SQLite.
* State writes, checkpoints, idempotency claims, and outbox records share explicit transactions.
* Application and domain packages do not import infrastructure or interface packages.

#### Completion Evidence

* Migration, concurrency, rollback, and restart tests pass.

#### Unresolved Items

* None.

<!-- rpi:phase id=P02 -->
## P02: Implement secure source ingestion

### Context

The compiler must accept SharePoint libraries or direct uploads without exposing
raw bytes through MCP. Both routes converge on one immutable source contract.

### Intent

Resolve, authorize, validate, parse, version, and checkpoint source content
before any text reaches the shaping agent.

### Boundaries

* Included: Upload quarantine, scanner port, SharePoint read connector, delta
  checkpoints, safe parsers, source hashing, and span generation.
* Excluded: AI shaping and output publication.

### Likely Targets

* src/shaper/infrastructure/uploads.py
* src/shaper/infrastructure/sharepoint_source.py
* src/shaper/infrastructure/parsers.py
* src/shaper/application/ingestion.py
* src/shaper/interfaces/http/uploads.py
* tests/contract/source_connectors/
* tests/integration/ingestion/

### Dependencies

* P01.

### Validation Expectations

* The same connector contract suite covers fakes and live adapters.
* Unsupported or unsafe content stops before parsing or agent invocation.
* Source/output overlap is rejected.

### Completion Evidence

* Direct-upload and SharePoint fixtures yield equivalent source and span contracts.
* Initial and resumed delta sync tests pass.
* P02 adds no more than 24 tracked files.

### Unresolved Items

* Live SharePoint validation requires a configured test tenant.

<!-- rpi:task id=P02-T01 -->
### P02-T01: Implement quarantined direct uploads

#### Context

Direct upload is a separate data plane. It must return an opaque asset ID only
after bounded staging and security checks.

#### Intent

Implement streaming upload, quarantine lifecycle, metadata validation, scanner
integration, content hashing, expiration, and authorized asset retrieval.

#### Boundaries

* Included: Configured root, generated names, size limit, extension/media/signature
  checks, archive rejection, scanner protocol, retention metadata, and cleanup.
* Excluded: Browser UI and raw MCP upload.

#### Likely Targets

* src/shaper/application/uploads.py
* src/shaper/infrastructure/uploads.py
* src/shaper/interfaces/http/uploads.py
* tests/unit/test_upload_policy.py
* tests/integration/test_upload_lifecycle.py

#### Dependencies

* P01-T02 and P01-T03.

#### Validation Expectations

* Path traversal, double extensions, MIME mismatch, oversized streams, unscanned
  assets, expired assets, and cross-tenant access fail explicitly.
* Scanner unavailability fails closed in the production profile.

#### Completion Evidence

* Security and lifecycle tests pass without persisting supplied filenames.

#### Unresolved Items

* Production scanner product and retention period remain deployment configuration.

<!-- rpi:task id=P02-T02 -->
### P02-T02: Implement SharePoint source synchronization

#### Context

SharePoint paths are locators. Stable site, drive, and item IDs plus content
hashes define durable identity, while delta links drive incremental refresh.

#### Intent

Implement tenant-scoped URL resolution, document enumeration, content download,
permission-homogeneous root validation, delta resume, tombstones, descendant
invalidation events, and source/output overlap exclusion.

#### Boundaries

* Included: Selected-permission validation, URL normalization, library/folder
  root resolution, pagination, retryable Graph failures, eTags, version IDs,
  content hashes, source-permission snapshots, delta tokens, source-change
  events, and deletion events.
* Excluded: SharePoint write operations.

#### Likely Targets

* src/shaper/infrastructure/graph_client.py
* src/shaper/infrastructure/sharepoint_source.py
* src/shaper/application/synchronization.py
* tests/contract/test_sharepoint_source.py
* tests/integration/test_sharepoint_source_live.py

#### Dependencies

* P01-T03.

#### Validation Expectations

* Fakes cover pagination, throttling, moved items, renamed items, deletions,
  expired delta tokens, folder filtering, changed-version supersession, and
  moved-out/deleted-source withdrawal.
* Live tests assert the configured app cannot enumerate an ungranted site.
* Sources with unsupported unique permissions are refused rather than ingested
  into a collection-scoped authorization boundary.

#### Completion Evidence

* Initial and incremental sync produce deterministic change sets and checkpoints.

#### Unresolved Items

* App-only versus delegated read is deployment configuration; Selected scope is required.

<!-- rpi:task id=P02-T03 -->
### P02-T03: Parse and normalize supported documents

#### Context

The agent needs ordered, addressable source spans rather than mutable parser output.

#### Intent

Safely parse supported formats, preserve useful structure and location, normalize
text, emit diagnostics, and calculate immutable source/span hashes.

#### Boundaries

* Included: Digitally readable PDF, DOCX, Markdown, plain text, headings,
  paragraphs, basic tables, page/block coordinates, and parser limits.
* Excluded: OCR, images, embedded executables, macros, and arbitrary archive expansion.

#### Likely Targets

* src/shaper/application/parsing.py
* src/shaper/infrastructure/parsers.py
* tests/fixtures/documents/
* tests/contract/test_parsers.py

#### Dependencies

* P01-T02 and a validated asset or SharePoint content stream.

#### Validation Expectations

* Golden fixtures verify text order, heading path, page or block location,
  table diagnostics, Unicode normalization, empty files, malformed files, and limits.
* Parser exceptions identify document, format, expected condition, and recovery action.

#### Completion Evidence

* All parser contract fixtures produce versioned spans or explicit diagnostics.

#### Unresolved Items

* OCR and advanced table extraction remain follow-up items.

<!-- rpi:phase id=P03 -->
## P03: Implement bounded agentic shaping

### Context

The user requires agentic AI answer shaping. Research confines autonomy to
semantic decomposition and repair inside a deterministic task envelope.

### Intent

Implement one observable agent that can acquire permitted context and produce or
abstain from source-grounded candidate units within hard budgets.

### Boundaries

* Included: Read-only tools, agent envelope, model gateway, structured output,
  bounded loop, retries, abstention, cancellation, and checkpoints.
* Excluded: Multi-agent coordination, web browsing, shell access, publication,
  permission changes, and persistent free-form memory.

### Likely Targets

* src/shaper/application/agent_tools.py
* src/shaper/application/shaping.py
* src/shaper/infrastructure/model_gateway.py
* tests/unit/agent/
* tests/contract/test_model_gateway.py

### Dependencies

* P01 and P02.

### Validation Expectations

* Adversarial source text cannot alter the tool allowlist or system envelope.
* Every run terminates and has reconstructable inputs, outputs, calls, and decisions.

### Completion Evidence

* Fake-model scenario suite covers success, repair, abstention, invalid output,
  timeout, cancellation, budget exhaustion, and transient provider failure.
* P03 adds no more than 18 tracked files.

### Unresolved Items

* Live-model quality is evaluated in P07 and does not alter the trust boundary.

<!-- rpi:task id=P03-T01 -->
### P03-T01: Implement read-only agent tools and task envelope

#### Context

Tools are the agent's main capability and risk boundary.

#### Intent

Expose tenant- and source-scoped span lookup, neighboring context, approved
taxonomy lookup, and candidate-conflict search through typed read-only tools.

#### Boundaries

* Included: Input/output schemas, authorization context, result caps, token
  accounting, tracing, and immutable tool registry.
* Excluded: Filesystem, arbitrary HTTP, Graph write, publication, email, shell,
  permission, prompt, schema, and configuration tools.

#### Likely Targets

* src/shaper/application/agent_tools.py
* src/shaper/application/agent_policy.py
* tests/unit/agent/test_tools.py
* tests/security/test_agent_capabilities.py

#### Dependencies

* P01-T03 and P02-T03.

#### Validation Expectations

* Tool calls cannot cross collection, tenant, source, or configured result limits.
* Unknown tools and malformed arguments fail before adapter invocation.

#### Completion Evidence

* Static allowlist and runtime authorization tests pass.

#### Unresolved Items

* None.

<!-- rpi:task id=P03-T02 -->
### P03-T02: Implement model gateway and structured candidate generation

#### Context

Provider output is probabilistic and provider schemas differ. Domain code must
consume one stable, validated candidate contract.

#### Intent

Implement the model protocol, deterministic fake, Azure OpenAI adapter, versioned
prompt set, schema-constrained response, usage capture, and explicit provider errors.

#### Boundaries

* Included: Model/deployment identity, parameters, structured output, refusal,
  usage, response IDs, timeout, rate-limit classification, and redacted traces.
* Excluded: Provider fallback that silently changes quality or cost.

#### Likely Targets

* src/shaper/application/model.py
* src/shaper/infrastructure/azure_openai.py
* src/shaper/prompts/
* tests/contract/test_model_gateway.py
* tests/integration/test_model_live.py

#### Dependencies

* P01-T02 and P03-T01.

#### Validation Expectations

* The fake deterministically drives every control path.
* Malformed, refused, truncated, or semantically invalid outputs remain distinct.
* Secrets and source bodies are absent from default logs.

#### Completion Evidence

* Contract tests pass for fake and configured live adapter.

#### Unresolved Items

* Deployment name, region, and model version are configuration supplied by the operator.

<!-- rpi:task id=P03-T03 -->
### P03-T03: Implement checkpointed shaping loop

#### Context

Agentic behavior must support adaptive context requests and repair without
allowing unbounded loops or success-shaped failure.

#### Intent

Coordinate tool calls, candidate generation, preliminary validation feedback,
repair attempts, abstention, cancellation, budgets, and durable checkpoints.

#### Boundaries

* Included: Explicit loop states, configurable hard limits, retry taxonomy,
  idempotent checkpoint resume, append-only run events, and the P01 `Validator`
  port backed in this phase only by schema and source-span-existence checks.
* Excluded: Self-approval and publication.

#### Likely Targets

* src/shaper/application/shaping.py
* src/shaper/application/checkpoints.py
* tests/unit/agent/test_shaping_loop.py
* tests/integration/test_shaping_resume.py

#### Dependencies

* P03-T01 and P03-T02.

#### Validation Expectations

* Maximum attempts, tool calls, tokens, elapsed time, and candidate count are
  enforced independently.
* Restart from every checkpoint yields one coherent run and no duplicate candidate.
* An architecture test prevents validation rules from being duplicated between
  the shaping loop and the P04 validator implementations.

#### Completion Evidence

* State-machine, property-based boundary, cancellation, and resume tests pass.

#### Unresolved Items

* Default numeric budgets are configuration and are tuned by P07 evidence.

<!-- rpi:phase id=P04 -->
## P04: Implement validation and review

### Context

Structured output proves syntax, not source support, completeness, policy
correctness, or safe publication. The agent cannot be its own acceptance authority.

### Intent

Apply independent validation and a durable review state machine before any unit
becomes publishable.

### Boundaries

* Included: Deterministic validators, model-assisted evaluators, findings,
  policy aggregation, review queue, evidence view, and state transitions.
* Excluded: Source correction and automatic publication threshold approval.

### Likely Targets

* src/shaper/application/validation.py
* src/shaper/application/evaluation.py
* src/shaper/application/review.py
* src/shaper/interfaces/http/reviews.py
* tests/unit/validation/
* tests/integration/test_review_flow.py

### Dependencies

* P01 and P03.

### Validation Expectations

* Deterministic failures cannot be overridden by model scores.
* Every transition records actor, reason, prior version, and timestamp.
* Initial policy requires human approval.

### Completion Evidence

* Full candidate lifecycle tests pass with optimistic-concurrency conflicts.
* P04 adds no more than 16 tracked files.

### Unresolved Items

* Automatic-publication thresholds require P07 and external governance approval.

<!-- rpi:task id=P04-T01 -->
### P04-T01: Implement deterministic validation

#### Context

Mechanical invariants should never depend on another model call.

#### Intent

Validate schema, source/span existence, source version, authorization scope,
taxonomy values, dates, required qualifiers, duplicate identity, conflicts, and release policy.

#### Boundaries

* Included: Typed findings with rule ID, severity, subject, evidence, and remedy,
  implemented behind the P01 `Validator` port. This phase extends, rather than
  duplicates, P03's schema and source-span-existence checks.
* Excluded: Probabilistic entailment or completeness scoring.

#### Likely Targets

* src/shaper/application/validation.py
* src/shaper/domain/findings.py
* tests/unit/validation/test_deterministic.py

#### Dependencies

* P01-T02 and candidate output from P03.

#### Validation Expectations

* Published-state eligibility requires zero blocking deterministic findings.
* Rule order does not alter aggregate result.
* An architecture test proves each rule ID has one implementation owner.

#### Completion Evidence

* Mutation and boundary tests show every invariant fails closed.

#### Unresolved Items

* None.

<!-- rpi:task id=P04-T02 -->
### P04-T02: Implement model-assisted quality evaluation

#### Context

Groundedness, completeness, preserved qualifiers, and appropriate abstention
need semantic evaluation, but evaluator output is advisory evidence rather than authority.

#### Intent

Implement evaluator protocols, a deterministic fake, configured model adapter,
versioned rubrics, evidence capture, and release-policy integration.

#### Boundaries

* Included: Groundedness, source-context coverage, qualifier/exception coverage,
  conflict handling, abstention, and task adherence.
* Excluded: Hidden chain-of-thought storage and unreviewed threshold changes.

#### Likely Targets

* src/shaper/application/evaluation.py
* src/shaper/infrastructure/model_evaluator.py
* src/shaper/evaluation/rubrics/
* tests/contract/test_evaluator.py

#### Dependencies

* P04-T01 and P03-T02.

#### Validation Expectations

* Scores include evaluator identity, rubric version, input hash, output, and rationale summary.
* Missing evaluator service routes to review or diagnosed failure, never automatic pass.

#### Completion Evidence

* Synthetic cases cover supported, unsupported, incomplete, conflicted, and abstaining candidates.

#### Unresolved Items

* Current managed evaluator names and preview status must be checked at implementation time.

<!-- rpi:task id=P04-T03 -->
### P04-T03: Implement review and state transitions

#### Context

Generated units need explicit ownership and review evidence before publication.

#### Intent

Implement the candidate state machine, queue, evidence projection, approve/reject
commands, source-driven supersede/withdraw transitions, concurrency guard,
OIDC-derived actor identity, and configurable collection publication policy.

#### Boundaries

* Included: Validated principal identity, comments, immutable prior versions,
  full review for initial releases, permanent full review for policy-rule,
  low-confidence, and conflicted units, configurable sampling for eligible
  standard-risk units at no less than 20 percent, low-risk FAQ units at no less
  than 10 percent after approval, and batch review only when evidence and policy match.
* Excluded: A full graphical review portal.

#### Likely Targets

* src/shaper/application/review.py
* src/shaper/interfaces/http/reviews.py
* src/shaper/interfaces/cli/reviews.py
* tests/unit/test_review_state.py
* tests/integration/test_review_flow.py

#### Dependencies

* P04-T01 and P04-T02.

#### Validation Expectations

* Invalid or stale transitions return explicit conflicts.
* A reviewer sees candidate, supporting spans, findings, conflicts, and run provenance.
* Queue and batch operations support an assumed 20 to 100 units per document
  and at least 5,000 pending units per collection without loading all records.
* A changed source drives descendants to `superseded`; deletion or movement out
  of scope drives them to `withdrawn`, with the source event recorded.

#### Completion Evidence

* Lifecycle and concurrency tests prove only eligible units can become approved.

#### Unresolved Items

* The initial identity mechanism is a validated OIDC token. Caller-supplied
  actor headers are never authoritative.

<!-- rpi:phase id=P05 -->
## P05: Implement release publication and retrieval

### Context

Accepted units must form one immutable, integrity-checkable release. SharePoint
does not provide a transaction across multiple files.

### Intent

Serialize and publish a complete release atomically at the application level,
then build bounded retrieval projections.

### Boundaries

* Included: Release assembly, integrity hashes, filesystem and SharePoint sinks,
  current pointer, lexical/vector indexes, fusion, filters, and source expansion.
* Excluded: GraphRAG, production-scale vector service, and source mutation.

### Likely Targets

* src/shaper/application/publication.py
* src/shaper/infrastructure/filesystem_sink.py
* src/shaper/infrastructure/sharepoint_sink.py
* src/shaper/application/query.py
* src/shaper/infrastructure/indexes.py
* tests/integration/publication/
* tests/unit/query/

### Dependencies

* P01, P02, and P04.

### Validation Expectations

* Manifest integrity validates independently.
* A release becomes current only after every required artifact exists.
* Query authorization is applied before ranking.

### Completion Evidence

* Fault-injected publication and 10,000-unit retrieval benchmark pass.
* P05 adds no more than 20 tracked files.

### Unresolved Items

* Production vector backend selection is deferred until evidence exceeds the local envelope.

<!-- rpi:task id=P05-T01 -->
### P05-T01: Build release manifests and filesystem publication

#### Context

The filesystem sink is the local reference implementation of the publication contract.

#### Intent

Create deterministic JSONL artifacts, diagnostics, manifest, integrity verifier,
complete active-corpus assembly, carry-forward provenance, manifest-last commit,
retention handling, and eTag-equivalent current-pointer update.

#### Boundaries

* Included: Configured root ID, validated relative path, temp staging,
  conflict-fail release directory, newly approved units, unchanged carried units,
  originating run and approval metadata, superseded/withdrawn exclusion, atomic
  local pointer replacement, retention, orphan cleanup, and rollback.
* Excluded: Arbitrary absolute paths and mutable release content.

#### Likely Targets

* src/shaper/application/publication.py
* src/shaper/infrastructure/filesystem_sink.py
* tests/integration/publication/test_filesystem.py

#### Dependencies

* P04-T03.

#### Validation Expectations

* Manifest is the final release artifact.
* Failed serialization, write, hash, or pointer update leaves prior current release unchanged.
* A second run changing one document produces a full current snapshot containing
  new approved units and every still-valid unchanged unit.
* Carry-forward requires identical `unit_version`, source version, permission
  snapshot, and approval policy; otherwise the unit re-enters validation/review.
* Current plus 10 prior successful releases and at least 90 days are retained.
  A pointer-race loser ends `completed_not_current`; its unpinned orphan release
  is deleted after 24 hours by an administrative cleanup operation.

#### Completion Evidence

* Ordering, integrity, concurrency, rollback, and cleanup tests pass.

#### Unresolved Items

* None.

<!-- rpi:task id=P05-T02 -->
### P05-T02: Implement SharePoint release publication

#### Context

SharePoint supplies governed storage and native history but only per-item
concurrency. Immutable release folders and `current.json` supply snapshot semantics.

#### Intent

Implement bounded Graph uploads, conflict behavior, manifest-last ordering,
eTag current-pointer updates, and publication diagnostics.

#### Boundaries

* Included: Stable destination resolution, small/resumable upload choice,
  deferred commit where supported, retries, check-in where required, and label errors.
* Excluded: Replacing sensitivity-labelled source files and broad write permission.

#### Likely Targets

* src/shaper/infrastructure/sharepoint_sink.py
* tests/contract/test_release_sink.py
* tests/integration/test_sharepoint_sink_live.py

#### Dependencies

* P02-T02 Graph client and P05-T01 publication contract.

#### Validation Expectations

* Concurrent current-pointer updates produce one winner and one diagnosed conflict.
* Missing grants, protected-file restrictions, throttling, and interrupted upload are explicit.
* The race loser records `completed_not_current` and an orphan reference for the
  same retention cleanup used by the filesystem sink.

#### Completion Evidence

* Fake fault suite passes; configured live test publishes and verifies one release.

#### Unresolved Items

* Delegated publication remains a deployment option for tenant policies that reject app-only writes.

<!-- rpi:task id=P05-T03 -->
### P05-T03: Build indexes and query service

#### Context

Answer-ready units improve context efficiency only if exact terms, paraphrases,
filters, conflicts, and source context remain retrievable.

#### Intent

Build full-release FTS5 and vector projections, embedding generation,
deterministic fusion/reranking, collection-role filters, conflict reporting,
coverage warnings, and source expansion.

#### Boundaries

* Included: Lexical index, `EmbeddingProvider`, vector port, deterministic local
  feature-hashing adapter, Azure OpenAI embedding adapter, result cap, token
  budget, release pinning, and explain metadata.
* Excluded: Graph and long-context routes.

#### Likely Targets

* src/shaper/application/query.py
* src/shaper/infrastructure/indexes.py
* tests/unit/query/
* tests/performance/test_query_benchmark.py

#### Dependencies

* P05-T01 and accepted units from P04.

#### Validation Expectations

* Queries cannot retrieve unauthorized units.
* Exact identifiers, synonyms, paraphrases, filters, conflict sets, and empty
  results produce expected bounded responses.
* The documented 10,000-unit p95 target is measured.
* Local tests assert embedding/index contracts, filtering, fusion, and ranking
  mechanics. Only the configured live embedding suite asserts paraphrase quality.
* Index construction consumes the complete release, including eligible
  carried-forward units, rather than only the changed-source set.

#### Completion Evidence

* Semantic fixture and performance reports pass their plan thresholds.

#### Unresolved Items

* The live embedding deployment is configured and recorded in the release;
  credential-free local runs use the deterministic feature-hashing adapter.

<!-- rpi:phase id=P06 -->
## P06: Expose jobs, review, query, and MCP interfaces

### Context

The same application use cases must serve operators, upload clients, and agent
hosts without exposing unsafe operations through MCP.

### Intent

Provide idempotent job execution, minimal HTTP and CLI surfaces, and the planned
MCP tools and resources.

### Boundaries

* Included: Compile, status, cancellation, upload, review, query, explanation,
  MCP tools/resources, authorization, and structured errors.
* Excluded: Raw MCP upload, delete, permission grant, forced publish, and arbitrary paths.

### Likely Targets

* src/shaper/application/jobs.py
* src/shaper/interfaces/http/
* src/shaper/interfaces/cli/
* src/shaper/interfaces/mcp/
* tests/contract/interfaces/
* tests/integration/test_compile_job.py

### Dependencies

* P02-P05.

### Validation Expectations

* All adapters call shared use cases and enforce consistent authorization.
* MCP results are bounded and contain structured evidence rather than hidden state.
* P06 adds no more than 18 tracked files.

### Completion Evidence

* End-to-end compile, review, publish, query, and explain flow passes through each interface.

### Unresolved Items

* MCP resource subscriptions are implemented only if supported by the selected SDK version.

<!-- rpi:task id=P06-T01 -->
### P06-T01: Implement compile-job orchestration and HTTP/CLI interfaces

#### Context

Compilation is externally visible and long-running. It needs idempotency,
checkpoint resume, explicit terminal states, and operator control.

#### Intent

Implement compile submission, worker execution, status, cancellation, retry,
upload/review routes, maintenance commands, and structured diagnostics.

#### Boundaries

* Included: Source/output refs, idempotency key, authorization context, outbox
  dispatch, full-snapshot assembly, graceful shutdown, and explicit retryability.
* Excluded: Distributed queue infrastructure until load requires it.

#### Likely Targets

* src/shaper/application/jobs.py
* src/shaper/interfaces/http/app.py
* src/shaper/interfaces/http/jobs.py
* src/shaper/interfaces/cli/main.py
* tests/integration/test_compile_job.py

#### Dependencies

* P02-P05.

#### Validation Expectations

* Duplicate submission returns the original job.
* Process interruption resumes from the last committed checkpoint.
* Cancellation cannot mark partial output successful.
* Resume preserves the same changed set and carry-forward basis, preventing a
  duplicate release or omission of unchanged units.

#### Completion Evidence

* Worker lifecycle, signal, retry, idempotency, and restart tests pass.

#### Unresolved Items

* A distributed queue is a follow-up if measured concurrency exceeds the local worker.

<!-- rpi:task id=P06-T02 -->
### P06-T02: Implement query and explanation interfaces

#### Context

Agents and operators need the same bounded retrieval and provenance view.

#### Intent

Expose authorized query and explanation use cases through HTTP and CLI with
stable response contracts and source links.

#### Boundaries

* Included: Collection/release selection, filters, top-k, token budget, source
  expansion, conflict/coverage warnings, why-matched metadata, validated OIDC
  principal, and collection-role enforcement.
* Excluded: Final natural-language answer generation.

#### Likely Targets

* src/shaper/interfaces/http/query.py
* src/shaper/interfaces/cli/query.py
* tests/contract/interfaces/test_query.py

#### Dependencies

* P05-T03.

#### Validation Expectations

* Invalid filters, unknown release, unauthorized collection, and excessive
  budgets return typed errors.
* Responses are identical in meaning across HTTP and CLI.

#### Completion Evidence

* Interface contract and authorization tests pass.

#### Unresolved Items

* None.

<!-- rpi:task id=P06-T03 -->
### P06-T03: Implement MCP tools and resources

#### Context

MCP provides reusable agent-host integration but should not own the data plane or administration.

#### Intent

Expose the four planned tools and versioned evidence resources through a thin
adapter over application use cases.

#### Boundaries

* Included: `knowledge.query`, `knowledge.explain`, `knowledge.compile`,
  `knowledge.job_status`, unit/source/release resources, structured content,
  OIDC authentication, collection roles, result caps, server-enforced compile
  quotas, aggregate model-token budgets, and compile confirmation metadata.
* Excluded: Raw upload, deletion, permission changes, arbitrary file access,
  forced publication, and direct agent-workflow tools.

#### Likely Targets

* src/shaper/interfaces/mcp/server.py
* src/shaper/interfaces/mcp/tools.py
* src/shaper/interfaces/mcp/resources.py
* tests/contract/interfaces/test_mcp.py

#### Dependencies

* P06-T01 and P06-T02.

#### Validation Expectations

* Tool and resource schemas match canonical contracts.
* Compile accepts references only and exposes that confirmation is required.
* Resource URIs are stable, bounded, and authorization-checked.
* Repeated compile requests are rejected with a structured quota error after
  one active job per collection, two active jobs per principal, 10 submissions
  per rolling 24 hours, or the configured aggregate token budget.

#### Completion Evidence

* MCP protocol and snapshot tests pass with a real SDK client.

#### Unresolved Items

* Optional resource subscriptions depend on SDK support and do not block the core surface.

<!-- rpi:phase id=P07 -->
## P07: Deploy and prove production operability

### Context

The system is not delivered until it has a repeatable Azure-hosted deployment.
It is not ready for automatic publication or production operation until hosting,
quality, security, fault behavior, telemetry, and operator procedures are evidenced.

### Intent

Package and deploy the service, then complete the synthetic evaluation baseline,
adversarial and fault tests, configured live tests, observability,
documentation, and final release gate.

### Boundaries

* Included: OCI image, Azure Container Apps, Bicep, managed identity, persistent
  state, deployment and rollback automation, synthetic evaluation contract,
  fixed-chain comparison, system/process metrics, red-team fixtures, live
  connectors, telemetry, health, runbooks, and docs.
* Excluded: Invented customer expected answers and unchecked human-review approval.

### Likely Targets

* tests/evaluation/
* tests/security/
* tests/integration/live/
* src/shaper/telemetry.py
* docs/
* README.md
* Dockerfile and .dockerignore
* bicep/
* scripts/deploy.sh

### Dependencies

* P01-P06.

### Validation Expectations

* Local required suites pass without credentials.
* Configured live suites report exact prerequisites and results.
* Automatic publication remains off until separately approved.

### Completion Evidence

* Final validation, evaluation, security, fault, performance, and live-test
  reports are referenced in the implementation changes record.
* P07 adds no more than 28 tracked files and the whole implementation remains
  within the 148-file cap.

### Unresolved Items

* Production evaluation thresholds and governance approvals remain explicit follow-ups.

<!-- rpi:task id=P07-T01 -->
### P07-T01: Build the evaluation and regression harness

#### Context

The value of agentic shaping and answer units is corpus-specific. Evaluation must
measure output quality and agent process without inventing source truth.

#### Intent

Create a machine-readable synthetic evaluation contract, fixed structured-chain
baseline, contextualized-source-chunk retrieval baseline, programmatic runner,
metric adapters, approved live baseline, reports, and upgrade regression gate.

#### Boundaries

* Included: Easy, grounding, hard, negative/error, and safety categories;
  groundedness, completeness, qualifier coverage, abstention, task adherence,
  tool accuracy, retrieval recall/rank, latency, token use, and estimated cost.
* Excluded: Production expected answers before the evaluation-design interview,
  user-population confirmation, sample review, and subject-matter approval.

#### Likely Targets

* tests/evaluation/cases.jsonl
* tests/evaluation/metadata.json
* tests/evaluation/baselines/live-approved.json
* tests/evaluation/test_runner.py
* tests/evaluation/test_agent_vs_fixed.py
* tests/evaluation/test_units_vs_chunks.py
* src/shaper/evaluation/reporting.py

#### Dependencies

* P03-P06.

#### Validation Expectations

* At least 30 synthetic cases exercise every category without real customer data.
* Cases needing domain truth are marked for subject-matter review.
* Reports identify model, prompt, schema, evaluator, corpus, hardware, and configuration.
* Answer units and contextualized chunks are compared over the same cases and
  retrieval metrics.
* A configured live run creates the baseline. The evaluation owner and domain
  reviewer approve changes to it. The gate allows no deterministic pass-rate
  drop, at most a 5 percentage-point model-assisted pass-rate drop, and at most
  a 20 percent p95 latency or model-token increase.
* Fake-model tests prove comparison and blocking mechanics but make no live
  quality claim.

#### Completion Evidence

* The runner compares agent and fixed-chain shaping plus answer-unit and
  contextual-chunk retrieval and produces actionable pass/fail evidence.

#### Unresolved Items

* Live distribution, user populations, expected answers, and thresholds require the formal interview and review.

<!-- rpi:task id=P07-T02 -->
### P07-T02: Complete adversarial, fault, and live integration tests

#### Context

Documents are untrusted inputs and agents amplify permission or workflow errors.

#### Intent

Test indirect injection, capability abuse, tenant isolation, malformed files,
budget exhaustion, evaluator failure, database restart, publication races, and live adapters.

#### Boundaries

* Included: Benign conformance stimuli, synthetic secrets, fake Graph/model fault
  matrices, test tenant operations, and explicit cleanup.
* Excluded: Harmful-elicitation payload authoring and production data.

#### Likely Targets

* tests/security/
* tests/integration/test_fault_recovery.py
* tests/integration/live/test_sharepoint_round_trip.py
* tests/integration/live/test_model_round_trip.py

#### Dependencies

* P01-P06 and optional live credentials.

#### Validation Expectations

* No adversarial document can change instructions, access a write tool, cross a
  tenant boundary, bypass a collection role or quota, forge reviewer identity,
  leak a secret, or make a failed release current.
* Live tests use dedicated resources and verify cleanup.

#### Completion Evidence

* Required local security/fault suites pass; configured live suites pass or
  report an explicit external blocker.

#### Unresolved Items

* Formal security, privacy, and RAI approvals are separate production-governance work.

<!-- rpi:task id=P07-T03 -->
### P07-T03: Finalize observability, operations, and documentation

#### Context

Long-running agentic jobs need operator-visible state, cost, failure, review,
publication, and recovery behavior.

#### Intent

Add structured telemetry and health checks, document configuration and security,
write runbooks, reconcile schemas and commands, and execute the final validation matrix.

#### Boundaries

* Included: Traces, metrics, redacted events, readiness/liveness, permissions,
  deployment profiles, retention, recovery, rollback, review, and upgrade guides.
* Excluded: Multi-region and multi-replica topology while SQLite owns workflow state.

#### Likely Targets

* src/shaper/telemetry.py
* src/shaper/interfaces/http/health.py
* README.md
* docs/architecture.md
* docs/configuration.md
* docs/operations.md
* docs/security.md

#### Dependencies

* P01-P07-T02.

#### Validation Expectations

* Telemetry correlates job, source, agent run, candidate, release, and request IDs
  without logging secrets or source bodies.
* Documentation commands and examples execute against the local profile.
* P07 remains within its 28-file allowance and total tracked additions remain
  within the 148-file budget or the plan is amended before completion.

#### Completion Evidence

* Final command matrix passes and the implementation changes record contains
  validation evidence, known external prerequisites, and remaining follow-ups.

#### Unresolved Items

* None for implementation handoff; production activation remains governed separately.

<!-- rpi:task id=P07-T04 -->
### P07-T04: Package and deploy the Azure-hosted service

#### Context

Hosting and deployment are a primary user requirement. The service must be
operable outside a developer checkout without weakening its identity, state, or
secret boundaries.

#### Intent

Build a non-root OCI image and deploy it to Azure Container Apps with managed
identity, persistent state, monitoring, protected configuration, health probes,
revision rollback, and automated smoke verification.

#### Boundaries

* Included: Multi-stage container build, Azure Container Registry, Container
  Apps environment and service, Log Analytics, Azure Files state, Bicep,
  deployment automation, health/MCP smoke tests, and rollback instructions.
* Excluded: Multi-replica state ownership until a managed transactional database
  adapter replaces SQLite, multi-region failover, and tenant permission grants.

#### Likely Targets

* Dockerfile
* .dockerignore
* bicep/main.bicep
* bicep/main.bicepparam
* scripts/deploy.sh
* docs/deployment.md

#### Dependencies

* P06 interfaces and P07-T03 health, telemetry, and operations behavior.

#### Validation Expectations

* The image runs as a non-root user and starts the HTTP/MCP service.
* `az bicep build` succeeds and deployment inputs expose no plain-text secrets.
* Container Apps uses one active revision and one replica while SQLite owns
  state, disables WAL on Azure Files, and deactivates the current revision before
  starting a replacement.
* The deployment command records image digest and revision, waits for readiness,
  executes health and MCP initialization smoke checks, and documents rollback.

#### Completion Evidence

* Local container configuration checks pass. Azure validation and deployment
  either pass in a configured subscription or report the exact external
  credential/subscription prerequisite without weakening the local gate.

#### Unresolved Items

* Horizontal scaling and zero-downtime revision replacement require a separately
  planned managed-database adapter.
* Live deployment requires an authenticated Azure CLI session and the governed
  identity, model, scanner, collection, and smoke-token values.
