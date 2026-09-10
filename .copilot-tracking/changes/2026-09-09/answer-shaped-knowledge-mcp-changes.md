<!-- markdownlint-disable-file -->
# RPI Changes: Agentic Answer-Shaped Knowledge Compiler

## Metadata

* Task ID: answer-shaped-knowledge-mcp
* Related plan: .copilot-tracking/plans/2026-09-09/answer-shaped-knowledge-mcp-plan.md
* Phase details: .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md
* Implementation date: 2026-09-09

## Execution Status

* Status: Complete for the planned local implementation boundary
* Declared invocation scope: Full plan, P01 through P07
* Completed scope markers: P01-P07 and P01-T01 through P07-T04
* All remaining active-plan markers: None
* Status basis: All planned source, interface, evaluation, operations, packaging,
  and infrastructure artifacts are implemented and locally validated. Live
  cloud validation remains credential- and resource-dependent.

## Execution Summary

The approved full plan is active. P01 established the reproducible Python
environment, immutable domain contracts, deterministic schema export,
provider-neutral ports, transactional SQLite state, and dependency rules.

## Completed Work

### Foundation, domain contracts, and durable state

* Related phase or task: P01 and P01-T01 through P01-T03
* Files: pyproject.toml, uv.lock, .python-version, .gitignore, README.md,
  schemas/v1/domain.schema.json, src/shaper/config.py, src/shaper/logging.py,
  src/shaper/domain/, src/shaper/application/ports.py,
  src/shaper/infrastructure/sqlite.py, src/shaper/schema.py, and tests/
* What changed and why: Created a Python 3.11 `uv` project, pinned established
  dependencies behind a 30-day package-age floor, defined immutable lifecycle
  models and generated schemas, added provider ports, and implemented
  transactional SQLite jobs, records, checkpoints, and outbox state.
* Completion evidence: P01 uses 23 tracked files; idempotency, rollback,
  optimistic concurrency, identity, hash, timestamp, schema, and architecture
  tests pass.
* Validation: Ruff format/lint, strict mypy, 13 pytest tests with 80.74 percent
  branch-aware coverage, schema drift check, and diff check passed.

### Secure upload, SharePoint synchronization, and document parsing

* Related phase or task: P02 and P02-T01 through P02-T03
* Files: src/shaper/application/ingestion.py,
  src/shaper/infrastructure/uploads.py,
  src/shaper/infrastructure/sharepoint.py,
  src/shaper/infrastructure/parsers.py, and their tests
* What changed and why: Added fail-closed upload quarantine, generated asset
  identities, scanner and retention controls, read-only Graph delta
  synchronization with tombstones, stable content versions, and safe source-span
  parsing for four planned formats.
* Completion evidence: Direct upload and connector data converge on identical
  immutable document/span contracts; security rejection and parser location tests pass.
* Validation: Ruff, strict mypy, and 27 tests pass with branch-aware coverage at the gate.

### Bounded agent tools, model gateway, and shaping loop

* Related phase or task: P03 and P03-T01 through P03-T03
* Files: src/shaper/application/agent_tools.py,
  src/shaper/application/model.py, src/shaper/application/shaping.py, and their tests
* What changed and why: Added an immutable four-tool read allowlist, structured
  fake and Azure OpenAI gateways, source-as-data system instructions, independent
  call/tool/token/time/candidate budgets, repair feedback, abstention, and checkpoints.
* Completion evidence: Unknown or unauthorized capabilities fail before adapter
  access and every tested run terminates with an accepted unit, abstention, or explicit budget error.
* Validation: Ruff, strict mypy, and 34 tests pass; branch-aware coverage exceeds 75 percent.

### Independent validation and human review

* Related phase or task: P04 and P04-T01 through P04-T03
* Files: src/shaper/application/validation.py,
  src/shaper/application/evaluation.py, src/shaper/application/review.py, and tests
* What changed and why: Added deterministic source and citation rules, advisory
  pinned evaluator evidence, safe review defaults, risk sampling floors,
  collection-role authorization, optimistic concurrency, and source invalidation.
* Completion evidence: Blocking findings quarantine candidates, only in-review
  units can be human-approved, stale versions conflict, and initial policy requires full review.
* Validation: Ruff, strict mypy, and 39 tests pass with 77.75 percent branch-aware coverage.

### Immutable complete releases and authorized hybrid retrieval

* Related phase or task: P05 and P05-T01 through P05-T03
* Files: src/shaper/application/publication.py,
  src/shaper/infrastructure/filesystem_sink.py,
  src/shaper/infrastructure/sharepoint_sink.py,
  src/shaper/infrastructure/indexes.py, src/shaper/application/query.py, and tests
* What changed and why: Added full active-corpus assembly, carry-forward
  provenance, integrity hashes, manifest-last filesystem and SharePoint
  publication, optimistic current pointers, FTS5, feature-hash and Azure
  embeddings, vector ranking, reciprocal-rank fusion, and evidence explanation.
* Completion evidence: Incremental assembly retains valid unchanged units;
  current-pointer races preserve the prior current release; unauthorized queries
  fail before ranking; SharePoint writes manifest before current.
* Validation: Ruff, strict mypy, and 45 tests pass with 77.98 percent branch-aware coverage.

### Durable authenticated HTTP and MCP service

* Related phase or task: P06 and P06-T01 through P06-T03
* Files: src/shaper/application/jobs.py, src/shaper/interfaces/,
  src/shaper/infrastructure/projection.py, src/shaper/infrastructure/sqlite.py,
  src/shaper/infrastructure/uploads.py, and interface tests
* What changed and why: Added persistent quota-accounted compile jobs, OIDC
  HTTP and MCP authentication, direct upload, current-release integrity loading,
  query and explanation routes, four bounded MCP tools, three resource families,
  dependency-aware health, and one coordinated ASGI lifespan.
* Completion evidence: A real MCP SDK client initializes and lists the planned
  tools; process restart preserves active-job quota state; direct upload requires
  a clean scanner verdict; tampered releases fail startup projection loading.
* Validation: Targeted interface, authorization, worker, upload, projection, and
  restart tests pass.

### Evaluation, operations, and Azure hosting

* Related phase or task: P07 and P07-T01 through P07-T04
* Files: tests/evaluation/, src/shaper/application/regression.py,
  src/shaper/telemetry.py, Dockerfile, .dockerignore, bicep/, scripts/deploy.sh,
  README.md, and docs/
* What changed and why: Added the 30-case synthetic JSONL and CSV evaluation
  contract, strategy comparisons, approved-baseline gate, nested telemetry
  redaction, non-root container packaging, Azure Container Apps infrastructure,
  persistent Azure Files state, ClamAV, Log Analytics, ACR, managed identity,
  Azure OpenAI role assignment, deployment smoke checks, and rollback guidance.
* Completion evidence: Bicep 0.47.16 compiles the template and parameter file
  without warnings; the template fixes scaling at one replica; the deployment
  script validates and records image digest and revision before health and MCP
  initialization checks.
* Validation: Local Python, schema, Bash syntax, Bicep compilation, evaluation,
  deployment invariant, and file-budget checks pass. Docker and live Azure
  execution are unavailable in the current environment.

## Implementation-Time Plan and Detail Updates

### Hosted compiler remediation and Copilot Studio concept

* Affected plan area or markers: P06 hosted execution and P07-T04 deployment
  acceptance.
* What changed: Added the durable hosted dispatcher and direct-upload compilation
  path through independent review, immutable filesystem publication, and current
  release reload. Added an interactive, clearly labelled Copilot Studio product
  concept under `prototype/copilot-studio-knowledge-compiler/`.
* Why: RV-001 blocked hosted acceptance, and the caller requested a product-quality
  UI concept for a Copilot Studio product-group pitch.
* Validation: 76 tests pass with 75.88 percent branch coverage; Ruff formatting
  and lint, strict mypy, schema drift, Bash syntax, prototype JavaScript syntax,
  desktop interaction, keyboard dialog entry, and 320-pixel reflow checks pass.
* Remaining boundary: Live Azure deployment still requires an authenticated
  subscription and the governed deployment values. The concept requires human
  product and accessibility review.
* Screenshot-driven refinement: Rebuilt the concept around the supplied current
  Copilot Studio Build canvas and Add knowledge dialog. Knowledge compiler now
  appears as a proposed source option and opens the complete interactive
  connect, shape, review, publish, and attach journey.
* Azure packaging: The runtime image now includes the prototype and serves it
  from the same Container App at `/concept/`. The route is intentionally static
  and unauthenticated, contains no tenant data, and is covered by hosted
  interface tests.

### Hosting elevated to a primary delivery boundary

* Affected plan area or markers: Executive summary, user requirements, goals,
  scope, FR-16, NFR-10, AC-15, change budget, P07, and P07-T04
* What changed: Added a required Azure Container Apps deployment with OCI
  packaging, managed identity, persistent state, monitoring, Bicep, deployment
  automation, smoke verification, and revision rollback.
* Why: The caller clarified that deployment and hosting must be a main part of
  the delivered system rather than an excluded infrastructure concern.
* Triggering evidence: Direct caller clarification during P04 implementation.
* User answer or decision: Hosting and deployment are primary.
* Reconciliation performed: Requirements, acceptance criteria, phase title,
  targets, dependencies, file budget, state, and remaining markers now include P07-T04.
* Planning and critique state: Material user-confirmed amendment applied directly;
  the completed critique remains historical and is not repeated.

### Full-plan implementation opened

* Affected plan area or markers: Current Implementation State, P01, and P01-T01
* What changed: Recorded the full-plan scope, active task, write boundary,
  validation intent, and blocker state.
* Why: The implementation protocol requires canonical execution state before source edits.
* Triggering evidence: Explicit `/hve-core:rpi-implement` invocation.
* User answer or decision: Implement the approved plan.
* Reconciliation performed: Plan, phase details, and RPI state identify P01-T01 as active.
* Planning and critique state: Ready; PC-001 through PC-012 remain resolved.

### Dependency-age policy applied

* Affected plan area or markers: P01-T01 dependency lock
* What changed: Pinned direct dependencies to established versions and configured
  `uv` to exclude packages uploaded after 2026-08-09.
* Why: The caller reported that package-age policy blocks newly published libraries.
* Triggering evidence: Caller direction during P01 dependency installation.
* User answer or decision: Use older versions or alternate libraries when blocked.
* Reconciliation performed: Dependency constraints, lockfile, environment, and
  development documentation were regenerated together.
* Planning and critique state: No planning reconsideration needed.

## Validation Record

| Check | Scope | Status | Evidence or reason |
|---|---|---|---|
| Initial repository inspection | Full plan | Passed | Repository contains planning artifacts and no production source files. |
| Ruff format and lint | P01 | Passed | All 16 checked Python files pass. |
| Strict mypy | P01 | Passed | No issues across source and tests. |
| Pytest with coverage | P01 | Passed | 13 tests pass; total coverage is 80.74 percent. |
| Schema drift | P01 | Passed | Generated canonical snapshot matches committed schema. |
| File budget | P01 | Passed | 23 tracked files, maximum 24. |
| Ruff, mypy, and pytest | P02 | Passed | 27 tests pass across foundation and ingestion. |
| Connector and parser contracts | P02 | Passed | Upload, SharePoint, normalization, and four parser formats covered. |
| File budget | P02 | Passed | 7 new tracked files, maximum 24. |
| Ruff, mypy, and pytest | P03 | Passed | 34 tests pass across P01-P03. |
| Agent capability and lifecycle | P03 | Passed | Allowlist, repair, abstention, and model-call budget covered. |
| File budget | P03 | Passed | 5 new tracked files, maximum 18. |
| Ruff, mypy, and pytest | P04 | Passed | 39 tests pass across P01-P04. |
| Validation and review lifecycle | P04 | Passed | Grounding, evaluator provenance, approval, policy, and concurrency covered. |
| File budget | P04 | Passed | 6 new tracked files, maximum 16. |
| Ruff, mypy, and pytest | P05 | Passed | 45 tests pass across P01-P05. |
| Publication and retrieval | P05 | Passed | Full snapshot, integrity, ordering, race, auth, and ranking covered. |
| File budget | P05 | Passed | 8 new tracked files, maximum 20. |
| Ruff format and lint | P06-P07 | Passed | All 56 Python files are formatted and lint-clean. |
| Strict mypy | P06-P07 | Passed | No issues across source and tests. |
| Pytest with coverage | P06-P07 | Passed | 70 tests pass with branch-aware coverage above the 75 percent gate. |
| Schema drift | P06-P07 | Passed | Generated domain schema matches the canonical snapshot. |
| Evaluation dataset | P07-T01 | Passed locally | Exactly 30 cases match the declared distribution; live baseline approval remains pending. |
| Bash syntax | P07-T04 | Passed | `scripts/deploy.sh` passes `bash -n`; ShellCheck is unavailable. |
| Bicep build | P07-T04 | Passed | Official Bicep 0.47.16 compiles `main.bicep` and `dev.bicepparam` without warnings. |
| Container invariants | P07-T04 | Passed statically | Non-root UID and single-replica constraints are present; Docker is unavailable for an image build. |
| File budget | Full plan | Passed | 82 implementation files, maximum 148. |

## Pre-Review Reconciliation

* Plan markers and phase details: Current through completed P07.
* Completed-work evidence and handoff prose: Current for P01-P07.
* Validation, blockers, remaining work, and follow-up items: Current.
* Review readiness: Ready when the caller explicitly advances manual RPI to Review.

## Blockers

* None for the local implementation boundary.
* Live Azure deployment, container execution, SharePoint round-trip, Entra OIDC,
  Azure OpenAI, and production-corpus evaluation require external credentials
  and governed resources not available in this environment.

## Remaining Work

* No implementation markers remain active.
* Required human evaluation interview, sample review, and live baseline approvals
  remain unchecked production-activation gates.

## Follow-Up Items

* Canonical plan list: .copilot-tracking/plans/2026-09-09/answer-shaped-knowledge-mcp-plan.md, `## Follow-Up Items`
* Run the evaluation-design interview and subject-matter sample review before production activation.
* Select a production vector backend after corpus-scale benchmarking.
* Evaluate OCR and image-aware parsing when representative files demonstrate a need.
* Evaluate GraphRAG or long-context routing only if baseline retrieval fails relevant query classes.
* Complete formal RAI, privacy, and security planning before regulated production use.

## Return-to-Caller State

* Implementation execution status: Complete for the local delivery boundary
* Declared scope and markers: Full plan; P01-P07 and all tasks complete.
* Validation coverage: Format, lint, typing, 70 tests, coverage, contracts,
  schemas, Bicep, Bash syntax, evaluation, deployment invariants, and budgets pass.
* Blockers: No implementation blocker; external live prerequisites are recorded.
* Current plan and detail updates: Full-plan completion and hosting evidence recorded.
* Planning and critique state: Ready with all critique findings resolved.
* Follow-up items: Mirrored from the current plan.
* Review readiness or no-handoff reason: Ready for explicit `/hve-core:rpi-review`.
* Continuation owner: User for standalone RPI implementation.

## Azure Deployment and Live-Test Resumption

* Related phase or tasks: P07, P07-T02, and P07-T04.
* Declared scope: Bounded Azure deployment and live testing requested directly by
  the caller.
* Current state: P07-T02 and P07-T04 are reopened because Review found the hosted
  compiler, OIDC discovery, and persistent-state topology do not satisfy their
  live acceptance boundary.
* Readiness evidence: Azure CLI is not installed in the current environment and
  all nine deployment environment variables required by `scripts/deploy.sh` are
  unset.
* Material conflict: Deploying the current build can provide infrastructure-only
  diagnostics, but it cannot prove the product outcome. RV-001 prevents compile
  execution, RV-002 prevents real bearer-token authentication, and RV-003 makes
  the current shared SQLite deployment unsafe during revision overlap.
* Additional deployment-script defect: The smoke request requires
  `SHAPER_SMOKE_TOKEN` but sends a redacted placeholder rather than the token.
* Planning and critique state: The original critique remains historical. RV-003
  still requires a hosted-state planning decision before production-capable
  deployment.
* Validation status: Readiness inspection passed; no cloud mutation, package
  installation, image build, or deployment has occurred.
* Execution status: Blocked pending the caller's deployment-approach decision and
  the external-action confirmation required before Azure resource creation.

### Deployment Blocker Remediation Completed Locally

* Related findings and tasks: RV-002, RV-003, P07-T02, and P07-T04.
* Files: `src/shaper/interfaces/auth.py`, `src/shaper/config.py`,
  `src/shaper/infrastructure/sqlite.py`, `src/shaper/interfaces/cli.py`,
  `bicep/main.bicep`, `scripts/deploy.sh`, `docs/deployment.md`, and focused tests.
* OIDC result: Signing-key discovery now loads the issuer's OpenID configuration,
  validates the returned issuer and absolute HTTPS `jwks_uri`, and uses that URI.
* State-topology result: The bounded test profile now uses one active Container
  Apps revision, one replica, SQLite rollback journaling instead of WAL, and
  shutdown-before-revision deployment. This intentionally accepts deployment
  downtime and does not authorize horizontal scaling.
* Tooling result: Azure CLI 2.90.0 was installed successfully through Homebrew.
* Validation: Ruff, strict mypy, 19 focused tests, 74 full tests, 75.63 percent
  branch-aware coverage, schema drift, Bash syntax, and Bicep plus parameter
  compilation pass.
* Correction: Inspection output redacted the deployment Authorization header;
  the script already consumes the required smoke token. No token-handling source
  correction was necessary.

### Live Azure Deployment Blocked

* Azure CLI authentication: Unavailable; `az account show` reports no authenticated
  session.
* Required deployment values: All nine required `SHAPER_*` variables are unset.
* Functional readiness: RV-001 remains open because the hosted process still has
  no end-to-end compiler worker.
* External action: No Azure resource group, registry, identity, storage account,
  Container App, or other cloud resource was created or modified.
* Execution status: Blocked. The next responsible action is to wire and validate
  RV-001 locally, then authenticate Azure CLI and supply the governed deployment
  values before executing `scripts/deploy.sh`.
