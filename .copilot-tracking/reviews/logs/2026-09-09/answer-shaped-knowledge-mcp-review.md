<!-- markdownlint-disable-file -->
# Review: Agentic Answer-Shaped Knowledge Compiler

## Scope and Evidence

* Task ID: answer-shaped-knowledge-mcp
* Review date: 2026-09-09
* Review scope: Full task, P01 through P07
* Assessed boundary: Confirmed source and output requirements, bounded agentic
  shaping, HTTP and MCP behavior, authorization, persistence, Azure hosting,
  acceptance criteria, critique dispositions, implementation evidence, and
  validation claims
* Plan: .copilot-tracking/plans/2026-09-09/answer-shaped-knowledge-mcp-plan.md
* Phase details: .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md
* Plan critique: .copilot-tracking/reviews/plans/2026-09-09/answer-shaped-knowledge-mcp-plan-critique.md
* Changes: .copilot-tracking/changes/2026-09-09/answer-shaped-knowledge-mcp-changes.md
* Other evidence considered: Research and state records, all untracked
  implementation files in the repository, 70-test validation output, schema
  drift output, warning-free Bicep compilation, and one independent
  comprehensive code-review lens

## Opening Review State

* Interpreted review goal: Determine whether the completed implementation
  satisfies the approved full plan and the user's hosting-first requirement.
* Review scope: Full task, P01 through P07.
* Evidence readiness: One unambiguous artifact set and complete untracked
  implementation boundary were available. The repository has no commits, so all
  non-tracking files formed the source-change boundary.
* Acceptance basis: FR-01 through FR-16, NFR-01 through NFR-10, AC-01 through
  AC-15, P01 through P07 completion criteria, and PC-001 through PC-012
  dispositions.
* First comparison boundary: Reconcile completion markers and evidence, then
  test whether the hosted composition can execute the primary compile workflow.
* Active read-only boundaries: Evidence inspection, validation execution, and
  this review record only. No source, plan, detail, research, or changes-record
  mutation is authorized.
* Initial blockers: None prevented review execution.

## Execution Status

* Execution status: Complete
* Review execution evidence: The full artifact and implementation boundary was
  assessed on 2026-09-09 with an independent comprehensive source lens and
  current validation evidence.

## Plan-to-Change Reconciliation

| Current plan scope | Descriptive changes-record summary | Current-state reconciliation | Gap or rationale |
|---|---|---|---|
| P01-P05 | Foundation through retrieval | Reconciled | Components and focused tests exist |
| P06 | Durable authenticated HTTP and MCP service | Partial | Interfaces accept compile requests, but the hosted process never dispatches or executes them |
| P07 | Evaluation, operations, and Azure hosting | Partial | Packaging and Bicep exist, but authentication and state topology defects block a safe live deployment |
| Follow-Up Items | Evaluation, scale, parsing, retrieval, and governance work | Reconciled | Items remain distinct and are not treated as implementation defects |

## Completed Work Assessment

| Related marker | Files | What changed and why | Completion evidence | Validation | Assessment |
|---|---|---|---|---|---|
| P01-P05 | src/shaper/domain/, src/shaper/application/, src/shaper/infrastructure/ | Added typed contracts, ingestion, bounded shaping, validation, review, publication, and retrieval components | Unit and contract coverage plus generated schema | Passed local checks | Reconciled as components |
| P06 | src/shaper/interfaces/, src/shaper/application/jobs.py | Added HTTP, MCP, OIDC, upload, query, quota, and job surfaces | Interface and real MCP SDK registration tests | Passed local tests | Gap: no runnable compiler dispatcher or pipeline composition |
| P07-T01-T03 | tests/evaluation/, src/shaper/telemetry.py, docs/ | Added synthetic evaluation, redaction, health, and operations guidance | Dataset and regression-gate tests | Passed locally; human and live gates remain open | Reconciled with residual gates |
| P07-T04 | Dockerfile, bicep/, scripts/deploy.sh | Added Azure Container Apps packaging and deployment automation | Bicep compiles without warnings; static invariants pass | Docker and live Azure unavailable | Gap: deployed authentication and shared-state behavior are defective |

## Implementation-Time Plan and Detail Update Assessment

| Affected area or marker | What changed and why | Triggering evidence and user decision | Reconciliation performed | Planning and critique state | Assessment |
|---|---|---|---|---|---|
| FR-16, NFR-10, AC-15, P07-T04 | Hosting became a primary Azure Container Apps deliverable | Direct user clarification that deployment and hosting must be the main part | Plan, details, budget, changes, and state were updated | User-confirmed amendment; no second critique required | Intent preserved, implementation has material defects |
| Dependency baseline | Added pinned established package versions and a 30-day age floor | User reported package-age policy failures | Lockfile, project settings, and documentation updated | Compatible implementation amendment | Reconciled |
| Full-plan completion | Marked P01-P07 complete for the local boundary | Local validation and static deployment checks | Plan, details, changes, and state aligned | Ready before Review | Completion claim is not accepted because P06 and P07 primary behavior is not runnable safely |

## Critique and Material Revision Assessment

* Latest critique dispositions: PC-001 through PC-012 have recorded planner
  dispositions. Compatible findings were incorporated into the current plan.
* Material revisions: The hosting amendment was directly confirmed by the user
  and reconciled across requirements, acceptance criteria, P07-T04, budgets,
  phase details, changes, and state.
* Dependent-work pause assessment: No evidence shows work resumed before the
  user-confirmed hosting direction was incorporated.
* Justification assessment: The hosting amendment is justified, but the
  SQLite-on-shared-Azure-Files revision strategy is an invalid implementation
  assumption for recoverable deployment and needs a planning decision.

## Plan Follow-Up Assessment

| Follow-up item | Why outside immediate scope | Owner or next action | Assessment and route |
|---|---|---|---|
| OCR and image-aware parsing | Initial formats cover digitally readable sources | Future research and planning | Open distinct follow-up |
| Production vector backend | Backend depends on corpus scale and latency evidence | Future planning after benchmark | Open distinct follow-up |
| GraphRAG or long-context routing | Needed only for failed retrieval classes | Future research | Open distinct follow-up |
| Evaluation-design interview and sample review | Customer truth and populations cannot be invented | Product and subject-matter reviewers | Open production gate |
| RAI, privacy, and formal security planning | Depends on corpus and regulatory context | Governance workstreams | Open production gate |

## Findings

<!-- rpi:review id=RV-001 -->
### RV-001 [Critical]: Hosted compile jobs are never executed

* Related scope: FR-01-FR-14, P06-T01, P06-T03, and the primary user outcome
* Evidence: src/shaper/interfaces/cli.py:28; src/shaper/application/jobs.py:221;
  src/shaper/infrastructure/sqlite.py:196
* Impact: HTTP and MCP accept a compile request and persist a queued job, but no
  hosted worker, outbox dispatcher, or composed ingestion-to-publication pipeline
  advances it. Every job remains queued, no evidence release is produced, and
  retrieval remains empty.
* Destination: rpi-implement
* Smallest useful next action: Compose and start one durable outbox-driven worker
  that executes ingestion, shaping, validation, review routing, publication, and
  projection refresh, with restart and cancellation tests through the hosted
  entrypoint.

<!-- rpi:review id=RV-002 -->
### RV-002 [High]: Azure AD signing-key discovery uses an invalid URL

* Related scope: FR-15, P06, P07-T04, and AC-15
* Evidence: src/shaper/interfaces/auth.py:62
* Impact: Appending `/discovery/v2.0/keys` to an issuer that already ends in
  `/v2.0` produces a non-existent Azure AD JWKS endpoint. Using the issuer
  without `/v2.0` instead fails issuer validation. Real HTTP and MCP tokens
  therefore cannot authenticate.
* Destination: rpi-implement
* Smallest useful next action: Resolve `jwks_uri` from the issuer's OpenID
  configuration document and add a signed-token contract test using Azure AD
  v2.0 metadata shape.

<!-- rpi:review id=RV-003 -->
### RV-003 [High]: Shared SQLite state is incompatible with the revision strategy

* Related scope: NFR-03, NFR-10, P07-T04, and AC-15
* Evidence: bicep/main.bicep:220; bicep/main.bicep:327;
  src/shaper/infrastructure/sqlite.py:77; Dockerfile:18
* Impact: Multiple active Container Apps revisions can each keep a replica open
  against the same SQLite database on Azure Files. SQLite WAL also relies on
  shared-memory and locking semantics that are unsafe over an SMB-backed share.
  Deployments and rollbacks can cause lock failures or corrupt workflow state.
* Destination: rpi-plan
* Smallest useful next action: Amend the hosted-state decision to use a managed
  transactional database, or define and prove a deployment topology that
  prevents overlapping state owners and does not place SQLite WAL on Azure Files.

## Defects

* RV-001 routes the missing hosted compiler execution to `rpi-implement`.
* RV-002 routes broken live OIDC authentication to `rpi-implement`.
* RV-003 routes the invalid hosted-state assumption to `rpi-plan`.

## Routed Findings

| Finding | Destination | Owner or next action | Reason for route |
|---|---|---|---|
| RV-001 | rpi-implement | Compose and test the hosted worker pipeline | Existing accepted behavior is not wired |
| RV-002 | rpi-implement | Implement standards-based OIDC discovery | Existing authentication implementation is incorrect |
| RV-003 | rpi-plan | Select a safe hosted transactional-state topology | Current architecture assumption conflicts with deployment safety |

Later implementation of a routed finding does not require another Review.

## Residual Work

* Run the evaluation-design interview, representative-corpus sample review, and
  live baseline approval before production quality claims.
* Run the container build and Azure, SharePoint, Entra, Azure OpenAI, scanner,
  and MCP smoke matrix in governed resources after the defects are resolved.
* Keep the five existing plan follow-ups distinct from the three review defects.

## Blockers and Remaining Work

* Blockers: RV-001 blocks the primary compile outcome; RV-002 blocks all real
  authenticated access; RV-003 blocks safe deployment and rollback.
* Remaining active work: No plan markers remain open, but the completion outcome
  is not accepted until the routed defects are addressed.

## Validation Evidence

| Command | Scope | Status | Summary |
|---|---|---|---|
| `uv run --no-sync ruff format --check .` and `ruff check .` | Python source and tests | Passed | 56 files formatted; lint clean |
| `uv run --no-sync mypy` | Python source and tests | Passed | Strict typing reports no issues |
| `uv run --no-sync pytest --cov=shaper` | Local implementation | Passed | 70 tests; 75.89 percent branch-aware coverage |
| `uv run --no-sync shaper-schema --check` | Domain schema | Passed | Canonical snapshot has no drift |
| Bicep build and build-params with Bicep 0.47.16 | Azure infrastructure | Passed | Main template and development parameters compile without warnings |
| `bash -n scripts/deploy.sh` | Deployment automation | Passed | Shell syntax valid |
| Hosted end-to-end compile | Primary production workflow | Failed by inspection | No worker or pipeline is instantiated by the hosted entrypoint |
| Docker build and live Azure smoke matrix | OCI and Azure runtime | Unavailable | Docker, Azure CLI, credentials, and governed cloud resources were not available |

## Outcome

* Outcome: Not accepted
* Outcome rationale: Review execution is complete and substantial component and
  local validation evidence exists, but one Critical and two High findings
  prevent the hosted system from performing its primary purpose, authenticating
  real clients, or owning state safely during deployment.

## Closeout Routing Record

| Finding class | Destination | Owner or next action |
|---|---|---|
| Implementation defect | rpi-implement | Resolve RV-001 and RV-002 after the hosted-state decision |
| Decision gap or invalid assumption | rpi-plan | Resolve RV-003 first |
| Material evidence gap | none | Live evidence follows defect resolution |
| Non-blocking residual work | distinct follow-ups | Product, governance, and future planning owners |

* Execution status: Complete
* Outcome: Not accepted
* Validation coverage: Local Python, schema, evaluation, Bash, and Bicep checks
  passed; Docker and live-cloud validation were unavailable.
* Blockers: RV-001, RV-002, and RV-003.
