<!-- markdownlint-disable-file -->
# RPI Plan Critique: Knowledge Estate Workflow Redesign

## Metadata

* Task ID: knowledge-estate-workflow-redesign
* Critique date: 2026-09-10
* Plan: .copilot-tracking/plans/2026-09-10/knowledge-estate-workflow-redesign-plan.md
* Phase details: .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md
* Critique execution status: Complete

## Inputs and Criterion Boundary

* Task context and caller requirements: Shaper remains a multi-agent Knowledge Transformation Platform with Assessment, Knowledge, Transformation, Governance, and Agent Readiness specialists under deterministic orchestration. Users define named estates from multiple SharePoint locations, ZIP bundles, individual documents, and supported URLs. Discovery scores each document and estimates reshaping effort. Recommendations are generated for selected documents only. Every transformation proposal carries a token estimate before approval. Users approve or decline per document, and only an approved current source version may be transformed. Outputs are new named artifacts using an estate policy such as `shaper_{source_stem}.html`, and sources are never overwritten. The workflow must be live, testable, and deployed to Azure without fabricated connected or success states.
* Research and evidence considered: .copilot-tracking/research/2026-09-10/knowledge-estate-workflow-redesign-research.md (C1-C25), docs/architecture.md, docs/deployment.md, and the plan and phase-details artifacts named above. Repository structure was inspected read-only, without reading application logic, solely to test the plan's factual claims about existing files, existing tests, and existing validation tooling: tests/, src/shaper/, bicep/, prototype/copilot-studio-knowledge-compiler/, scripts/, and the pytest, coverage, and mypy configuration in pyproject.toml.
* Decisions, dependencies, and acceptance criteria considered: FR-01-FR-16, NFR-01-NFR-10, AC-01-AC-16, P01-P07 and all 20 tasks, the Dependencies list, the User Decisions and Requirements list, the Locked Implementation Boundaries (test ownership, no source or test file removals, at most seven new production modules and seven focused tests, no new frontend or accessibility framework, PostgreSQL canonical production workflow state with SQLite local state, separate token estimates and actuals, separate pre-transform and output decisions, HTML artifacts plus retained JSONL projection, semantic and regression coverage, and listed validation evidence), the Follow-Up Items, and the research Current Decisions and Unresolved Decisions tables.
* Assessment boundary: The critique can conclude whether the plan's requirements, tasks, acceptance criteria, and locked boundaries are internally consistent, traceable to C1-C25 and the supplied documentation, and sufficient to make the requested workflow demonstrably live. It cannot verify runtime behavior, Azure tenant state, Microsoft Graph consent, Container Apps authentication behavior, or whether any implementation would in fact pass the named checks, because no code was executed and no external research was performed. Findings that name missing evidence are stated as missing rather than inferred as defects in the implementation.

## Coverage Assessment

| Requirement, research, phase, or task ID | Coverage | Evidence or concern |
|------------------------------------------|----------|---------------------|
| FR-01 | Partial | P01-T01 and P02-T01 define create, inspect, and revision behavior; AC-01 proves persistence; rename, archive, and deletion semantics have no acceptance coverage (PC-012, PC-015) |
| FR-02 | Covered | P02-T01 typed multi-source registration with stable IDs; AC-02 |
| FR-03 | Covered | P02-T01 and P02-T03 explicit lifecycle states; AC-04 forbids sample substitution |
| FR-04 | Covered | P02-T02 bounded expansion matrix; NFR-05; AC-03; numeric limits deferred but explicitly bounded and configurable |
| FR-05 | Partial | P03-T01 and P03-T02 define report content and relational evidence; no execution model or scale bound for a discovery run (PC-002) |
| FR-06 | Covered | P01-T02 and P03-T02 assert role distinction and no agent authority; AC-12 |
| FR-07 | Partial | P04-T01 pins selection, discovery, and source versions; the cost boundary of proposal generation itself is undefined (PC-004) |
| FR-08 | Covered | P04-T02 deterministic estimator with no `ModelGateway` call; C20-C25 |
| FR-09 | Partial | P04-T03 actor, reason, revision, and source-version pinning; invalidation set omits estimator and model-deployment change (PC-013) |
| FR-10 | Covered | P05-T01 fail-closed dispatch with zero-gateway-call evidence; AC-08, AC-09 |
| FR-11 | Partial | P05-T02 retains provider counts and variance for transformation runs only; earlier-stage spend unaccounted (PC-004) |
| FR-12 | Covered | P05-T03 naming policy, traversal rejection, deterministic collision suffix; C11, C19 |
| FR-13 | Partial | P05-T03 keeps two distinct records, but "independent" review is undefined against AC-14 (PC-006) |
| FR-14 | Partial | P06-T02 defines resources and boundaries; interactive role source and principal trust are undefined (PC-001, PC-010) |
| FR-15 | Partial | P06-T03 enumerates truthful states; progress and polling have no server run contract (PC-002); hosted asset path boundary unowned (PC-009) |
| FR-16 | Partial | P06-T02 and P07-T01 establish a session; authorization claims for that session are unspecified (PC-001) |
| NFR-01 | Covered | P01-T02 port isolation plus existing tests/test_architecture.py |
| NFR-02 | Covered | P01-T02, P02-T01, P04-T03 compare-and-save semantics |
| NFR-03 | Covered | P01-T01 stable identity, P04-T02 estimator determinism, P05-T03 byte-identical rendering |
| NFR-04 | Partial | Cap derivation and fail-closed exhaustion defined; no post-exhaustion user path (PC-007) |
| NFR-05 | Covered | P02-T02 traversal, encryption, ratio, extension, signature, and per-entry scanning matrix |
| NFR-06 | Partial | P06-T01 and P07-T01 add PostgreSQL; the set of record families that become PostgreSQL-canonical is undefined (PC-005) |
| NFR-07 | Partial | Secret handling and managed identity covered; principal-header trust (PC-010) and customer-data retention (PC-012) are not |
| NFR-08 | Partial | P06-T04 method adequacy is sound; no repeatable harness exists inside the locked boundary (PC-008) |
| NFR-09 | Covered | Explicit non-success states across P02, P05, P06; the assertion method for "no broad catch" is unstated but low risk |
| NFR-10 | Partial | Compatibility asserted; public concept and demo path boundary is ambiguous (PC-009); coverage gate risk (PC-011) |
| AC-01-AC-03 | Covered | Estate persistence, mixed-source inventory, and unsafe-archive rejection map to P02 tasks |
| AC-04 | Covered | Authorization-required state is explicit; live Graph proof is an accepted external dependency |
| AC-05 | Partial | Content defined; run execution and scale undefined (PC-002) |
| AC-06-AC-10 | Covered | Selection scope, estimate presentation, decisions, stale-version invalidation, and actual accounting map to P04 and P05 |
| AC-11 | Partial | Publication path defined; independence semantics undefined (PC-006) |
| AC-12 | Covered | P03-T02 agent-ownership and no-authority assertions |
| AC-13 | Partial | Bearer-path boundaries defined; interactive-principal role source and header trust undefined (PC-001, PC-010) |
| AC-14 | Partial | Revision persistence claimed; scope of durable records undefined (PC-005) and journey depends on PC-001 |
| AC-15 | Partial | Methods adequate; evidence is one-time and unguarded (PC-008) |
| AC-16 | Partial | Test ownership names two files that do not exist and saturates the locked cap (PC-003); coverage gate and JavaScript check claims are unverified (PC-008, PC-011) |
| P01 | Covered | Contracts precede behavior; targets and validation expectations are specific and testable |
| P02 | Covered | Ingestion boundaries are strong; test ownership needs correction (PC-003) |
| P03 | Partial | Evidence content is well specified; execution model and model-spend boundary are not (PC-002, PC-004) |
| P04 | Partial | Estimation and decision invariants are strong; cap recovery and revalidation set are incomplete (PC-007, PC-013) |
| P05 | Partial | Fail-closed dispatch and artifact safety are strong; review independence is undefined (PC-006) |
| P06 | Partial | Persistence, API, UI, and accessibility tasks exist; PC-001, PC-005, PC-008, PC-009, PC-010, PC-011 apply |
| P07 | Partial | Deployment proof is concrete; PC-005, PC-012, and PC-014 apply |
| Research C1-C25 | Covered | Every plan requirement traces to cited evidence; C25 tokenizer absence is handled by labeled approximation, and the three research Unresolved Decisions (generic URL scope, collision behavior, mandatory output review) are each resolved in the plan |

## Verdict

* Verdict: Revise
* Rationale: The plan is architecturally credible, traceable to C1-C25, and faithful to every confirmed user requirement, including the multi-agent boundary, per-document decisions, pre-approval token estimates, immutable named artifacts, and truthful connector states. Five High findings nonetheless block a confident implementation start: interactive browser users have no defined source of collection-scoped authorization (PC-001), long-running discovery and recommendation runs have no execution model (PC-002), the locked test-ownership map names two test modules that do not exist and would push new test modules past the locked cap of seven (PC-003), model spend before the approval gate is unbounded and unaccounted (PC-004), and the set of records that actually become PostgreSQL-canonical is undefined so the durability claim in NFR-06 and AC-14 is only partly provable (PC-005). Each is resolvable by planner-owned plan text changes without contradicting current user direction.

## Findings

<!-- rpi:critique id=PC-001 -->
### PC-001 [High]: Interactive browser principals have no defined source of collection-scoped roles

* Related IDs: FR-14, FR-16, NFR-07, AC-01, AC-13, AC-14, P06-T02, P07-T01, Dependencies
* Evidence: .copilot-tracking/plans/2026-09-10/knowledge-estate-workflow-redesign-plan.md (FR-14, FR-16, AC-13, Dependencies); .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md (P06-T02 Intent and Validation Expectations, P07-T01); docs/deployment.md Prerequisites, which states the existing model uses "Collection-scoped app roles such as `shaper:{collection}:query`"
* Concern: The plan establishes a same-origin Container Apps session for browser users and asserts collection and role enforcement, but never states how an interactively signed-in human acquires `shaper:{collection}:*` authorization. The existing role claims are described in docs/deployment.md as app roles carried in bearer tokens obtained through client credentials for smoke testing. No task, dependency, or acceptance criterion establishes user or group app-role assignment, a claim-mapping rule from the ingress principal to collection roles, or the behavior for an authenticated user with no role.
* Impact: AC-01 requires a signed-in user to create an estate while AC-13 requires insufficient-role rejection. Without a defined role source, implementation must improvise, and the most likely improvisation is a permissive default that grants any authenticated tenant user full estate authority, silently defeating AC-13 and NFR-07 on the live deployment that AC-14 requires. The dependency also has tenant-administration lead time that is currently invisible in the Dependencies list.
* Smallest useful change: State in FR-16 and P06-T02 the exact mapping from an ingress-authenticated principal to tenant, collection, and role, add "Entra app-role assignment for interactive users or groups" to the Dependencies list, and add one acceptance condition for an authenticated user who holds no collection role.
* Action owner: Planning parent for the plan text and dependency entry; tenant administrator for the assignment itself during P07
* Exact resolving evidence: FR-16 and P06-T02 name the claim source and mapping rule; the Dependencies list includes interactive role assignment; an AC or P06-T02 validation expectation asserts that an authenticated principal without a collection role receives an authorization failure rather than estate access
* Decision route: Direct planner correction; the tenant assignment is a deployment dependency of the same class the plan already records for Graph and PostgreSQL, not a divergent user decision

<!-- rpi:critique id=PC-002 -->
### PC-002 [High]: Discovery and recommendation runs have no execution model, scale bound, or run contract

* Related IDs: FR-05, FR-07, FR-15, NFR-09, AC-05, AC-14, P03, P03-T02, P04, P06-T03
* Evidence: .copilot-tracking/research/2026-09-10/knowledge-estate-workflow-redesign-research.md C8, C15, C16 (current compilation handles exactly one staged upload and current platform analysis is synchronous and stateless); docs/architecture.md "Current implementation boundary" and the Containers diagram, which mark specialist workers and asynchronous dispatch as planned; .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md P06-T03, which lists "polling" and progress states with no corresponding server-side run contract in P03 or P04
* Concern: FR-05 requires discovery of every document in an estate that may contain whole SharePoint libraries, and FR-15 promises transformation progress and retryable failures, but no requirement, task, or non-functional threshold defines how a discovery or recommendation run executes: synchronous request, durable queued run, resumable checkpointing, timeout, cancellation, partial-source failure semantics, or a maximum document count per estate or per run. The existing job coordination is described only in the transformation path (P05-T01).
* Impact: A live estate of realistic size can exceed HTTP request and ingress timeouts, producing exactly the class of untruthful or stuck state the user prohibited. The UI states in P06-T03 cannot be implemented against an undefined server contract, and AC-05 and AC-14 become unprovable at any size beyond the four-document fixture in AC-02.
* Smallest useful change: Add one requirement, or an explicit boundary statement in P03 and P04, that discovery and recommendation execute as durable, pollable runs with status, partial-failure, and cancellation semantics reusing the existing job coordination, and state one documented per-run document bound with the behavior when it is exceeded.
* Action owner: Planning parent
* Exact resolving evidence: P03 and P04 boundaries name the run execution mechanism and its status contract; a requirement or NFR states the per-run document bound and over-bound behavior; P06-T03 polling states reference that contract
* Decision route: Direct planner correction, provided the mechanism reuses existing job coordination and stays inside the locked seven-module cap

<!-- rpi:critique id=PC-003 -->
### PC-003 [High]: The locked test-ownership map names two nonexistent test modules and already saturates the seven-test cap

* Related IDs: AC-16, Locked Implementation Boundaries (Test Ownership, Maximum Additions), P02-T02, P06-T02
* Evidence: .copilot-tracking/plans/2026-09-10/knowledge-estate-workflow-redesign-plan.md Test Ownership lists "tests/test_archive.py and existing tests/test_uploads.py" and "existing tests/test_interfaces.py and tests/test_auth.py"; .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md P02, P02-T02, and P06-T02 repeat those targets. The tests directory contains no test_uploads.py and no test_auth.py; upload behavior currently lives in tests/test_ingestion.py, tests/test_compilation.py, and tests/test_interfaces.py, and authentication cases live in tests/test_interfaces.py. The seven declared new modules (test_estate_domain, test_estates, test_archive, test_token_estimation, test_decisions, test_artifacts, test_estate_repository) already consume the locked cap of at most seven new test modules exactly.
* Impact: Implementation must either create two more test modules and break a locked boundary the user confirmed, or quietly relocate upload and authentication coverage, which breaks the AC-16 traceability the plan depends on for evidence. Either outcome produces an unplanned deviation at the point where the plan claims to be most precise.
* Smallest useful change: Remap the two entries to the existing files that actually own that coverage, for example "tests/test_archive.py and existing tests/test_ingestion.py and tests/test_compilation.py" and "existing tests/test_interfaces.py", and mirror the correction in the P02, P02-T02, and P06-T02 likely targets.
* Action owner: Planning parent
* Exact resolving evidence: Test Ownership and the P02, P02-T02, and P06-T02 targets reference only files that exist or are among the seven declared new modules, and the new-module count remains at seven
* Decision route: Direct planner correction. Raising the locked cap from seven would instead be a divergent user decision, so the remap is the change that preserves current user direction

<!-- rpi:critique id=PC-004 -->
### PC-004 [High]: Model spend during discovery and recommendation is unbounded, unestimated, and unaccounted

* Related IDs: FR-07, FR-08, FR-11, NFR-04, AC-07, AC-10, P03-T02, P04-T01, P04-T02, research C20-C25
* Evidence: .copilot-tracking/plans/2026-09-10/knowledge-estate-workflow-redesign-plan.md FR-08 and FR-11 scope estimates and actual accounting to transformations only; .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md P04-T01 has the Transformation Agent "build document proposals grounded in the selected discovery evidence" without stating whether that path calls a model, while P04-T02 forbids a model call only during estimation; docs/architecture.md states a role "can use deterministic analysis, model-assisted reasoning, or both"
* Concern: The user requirement is that a transformation proposal shows a token estimate before approval. The plan satisfies that for the transformation itself but leaves the cost class of proposal generation and estate-level agent composition undefined. If either path is model-assisted, users incur uncapped, unestimated, and unrecorded token consumption before any approval gate exists, and NFR-04's fail-closed ceiling does not apply to it.
* Impact: The workflow can spend model budget on documents the user later declines, with no record in the accounting contracts (FR-11 covers completed transformations only). That undermines the resource-visibility intent behind the user's token requirement and leaves a live deployment with an uncontrolled cost surface.
* Smallest useful change: State explicitly in P03 and P04 boundaries that discovery and recommendation generation are deterministic and invoke no `ModelGateway`; if any model-assisted path is intended, attach a per-run cap and a usage record to it under FR-11.
* Action owner: Planning parent
* Exact resolving evidence: P03 and P04 boundaries contain an explicit deterministic-only statement with a matching validation expectation asserting zero gateway calls, or FR-11 and P04-T01 extend accounting and capping to the recommendation run
* Decision route: Direct planner correction when the intent is deterministic. A deliberate model-assisted proposal path with pre-Recommend cost consent would be a significant user decision

<!-- rpi:critique id=PC-005 -->
### PC-005 [High]: The set of records that become PostgreSQL-canonical is undefined, so the durability claim is only partly provable

* Related IDs: NFR-06, NFR-10, AC-14, P06-T01, P07-T01, Locked Canonical and Generated Targets, research C12, C13
* Evidence: .copilot-tracking/research/2026-09-10/knowledge-estate-workflow-redesign-research.md C12 (SQLite today stores jobs, generic records, checkpoints, and outbox entries) and C13; docs/deployment.md IMPORTANT block, which states that in-flight jobs and review state do not survive replica replacement and that `minReplicas` and `maxReplicas` are fixed at one because of SQLite locking; .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md P06-T01, whose targets describe SQLite as "Local tables and repositories" and PostgreSQL as "Production adapter" without enumerating record families
* Concern: The locked boundary says "PostgreSQL is canonical for production workflow records" but neither the plan nor the details state whether existing job, review, delta-checkpoint, and outbox records move with the estate records. The plan also does not state whether the single-replica constraint and its documented rationale change, even though P07-T02 supersedes the deployment statement that container-local SQLite is the active workflow store.
* Impact: NFR-06 and AC-14 can pass on a narrow reading (the estate row survives a revision) while an in-flight transformation, its approval, or a Graph delta checkpoint is still lost, which is the failure the user's "live and testable" requirement targets. The ambiguity also hides scope: migrating job and outbox storage is materially larger work than migrating estate records, and it interacts with the locked seven-module cap.
* Smallest useful change: Enumerate in the Canonical and Generated Targets section exactly which record families are PostgreSQL-canonical in production and which explicitly remain out of scope, and add one smoke step or acceptance condition covering an in-flight transformation across a revision change or an explicit statement that in-flight job durability is deferred.
* Action owner: Planning parent
* Exact resolving evidence: The Canonical and Generated Targets list names each record family and its production store; P06-T01 targets match that list; P07-T03 or AC-14 states the in-flight durability expectation and its result
* Decision route: Direct planner correction; deferring in-flight job durability should be recorded as an accepted residual risk rather than left implicit

<!-- rpi:critique id=PC-006 -->
### PC-006 [Medium]: "Independent" output review is undefined and may conflict with the single-user end-to-end journey

* Related IDs: FR-13, AC-11, AC-14, P05-T03, research C10
* Evidence: .copilot-tracking/plans/2026-09-10/knowledge-estate-workflow-redesign-plan.md FR-13 and AC-11 require artifacts to pass "the existing independent output-review gate" while AC-14 requires one signed-in user to complete the hosted journey end to end; research C10 records that current review decisions are immutable, version-targeted, role-authorized, and concurrency protected, but says nothing about actor separation
* Concern: The plan never defines whether independence means a distinct decision record and role check, or a different human actor from the pre-transform approver. The two readings produce different implementations and different acceptance outcomes.
* Impact: If actor separation is required, AC-14 cannot pass in a development deployment operated by one person, and implementation will discover the conflict late. If it is not required, P07-T02 documentation risks describing a separation-of-duties control that does not exist.
* Smallest useful change: Define independence in FR-13 as a distinct record, service, and role check, and state explicitly whether the same actor may hold both decisions in this increment.
* Action owner: Planning parent
* Exact resolving evidence: FR-13 states the independence definition and the same-actor rule; AC-11 and AC-14 are consistent with it; P07-T02 documentation scope reflects the same wording
* Decision route: Direct planner correction if independence means separate records; requiring distinct human actors would be a significant user decision because it changes AC-14

<!-- rpi:critique id=PC-007 -->
### PC-007 [Medium]: No defined recovery path when an approved transformation exhausts the estimate-derived cap

* Related IDs: FR-08, FR-10, FR-11, NFR-04, AC-08, AC-10, P04-T02, P05-T01, P05-T02, research C25
* Evidence: .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md P05-T01 derives the job cap from the retained estimate and P05-T02 records budget-exhausted terminal accounting; P04-T02 records that the initial approximation is labeled and later calibrated; research C25 confirms no tokenizer package exists, so the estimate is an approximation
* Concern: The plan defines fail-closed behavior at the cap but no state transition afterwards. Because the approval is pinned to a specific estimate and source version, it is unclear whether a budget-exhausted run may be re-estimated and retried, whether it requires a fresh approval, or whether the document is simply stuck.
* Impact: With an unvalidated first-generation estimator, cap exhaustion is a likely early failure mode. Users would see a terminal failure with no next action, contradicting NFR-09's requirement that failures remain recoverable with a corrective action.
* Smallest useful change: Add one state transition and matching acceptance condition: a budget-exhausted run produces a new estimate and requires a fresh explicit approval before retry, with the original estimate and usage record retained immutably.
* Action owner: Planning parent
* Exact resolving evidence: P05-T01 or P04-T03 documents the re-estimate and re-approval transition; an acceptance criterion asserts that a budget-exhausted document cannot retry without a new decision and that both records persist
* Decision route: Direct planner correction

<!-- rpi:critique id=PC-008 -->
### PC-008 [Medium]: Accessibility and JavaScript verification have no repeatable harness, and the named "existing JavaScript parse check" does not exist in the repository

* Related IDs: NFR-08, AC-15, AC-16, P06-T04, Locked Test Ownership, Locked Validation Evidence, Semantic and Regression Coverage
* Evidence: .copilot-tracking/plans/2026-09-10/knowledge-estate-workflow-redesign-plan.md Test Ownership cites an "existing JavaScript parse check plus browser-based static, interaction, accessibility-tree, and adaptive-rendering verification", and Validation Evidence lists "JavaScript parse validation" and browser checks. The repository contains no package.json, no Node or browser tooling configuration, no committed JavaScript parse step in tests or scripts/deploy.sh, and no browser automation dependency, while the locked boundary forbids adding a new accessibility framework.
* Concern: The verification the plan relies on for NFR-08 and AC-15 exists only as ad-hoc operator or agent activity recorded in the changes artifact. The Semantic and Regression Coverage section nonetheless claims that browser verification covers the real user journey, which reads as a repeatable guarantee.
* Impact: Accessibility and front-end behavior are verified once and are then unguarded against regression, and AC-16 names a check that cannot be run as written. This is the largest gap between what the plan promises as evidence and what the repository can produce.
* Smallest useful change: State plainly that browser accessibility and JavaScript validation are one-time manual or agent-executed evidence for this increment, recorded in the changes artifact and accepted as a residual regression risk, and either name the exact command used for JavaScript parse validation or remove the "existing" qualifier.
* Action owner: Planning parent
* Exact resolving evidence: Validation Evidence and Semantic and Regression Coverage distinguish repeatable suite checks from one-time recorded evidence; AC-16 names only checks that can be executed as written
* Decision route: Direct planner correction. Adding an automated browser or accessibility harness would be a divergent user decision because the locked boundary forbids a new accessibility framework

<!-- rpi:critique id=PC-009 -->
### PC-009 [Medium]: The public concept surface and the authenticated live product UI share one asset path, and the module that serves it is unowned

* Related IDs: FR-15, FR-16, NFR-07, NFR-10, AC-14, P06-T02, P06-T03, P07-T01
* Evidence: docs/deployment.md states that the `/concept/` prototype is "intentionally unauthenticated, accepts no caller-provided content" and instructs "Do not add customer or tenant data to the prototype assets or demo service"; the plan makes prototype/copilot-studio-knowledge-compiler/index.html, app.js, and styles.css the live estate product surface serving authenticated customer content while keeping `GET /v1/demo/analysis` public; src/shaper/interfaces/hosted.py, which serves those assets, appears in no task's likely targets
* Concern: The plan changes the trust class of a surface that existing documentation defines as public, without stating which paths remain anonymous under Container Apps authentication and which require a session, and without assigning ownership of the module that serves the assets.
* Impact: Either the authenticated workflow is served from a path documented as public, or the documented public concept breaks silently. The unowned serving module also means the routing and authentication wiring for FR-15 and FR-16 has no planned home.
* Smallest useful change: Add src/shaper/interfaces/hosted.py to the P06-T02 or P06-T03 targets, and state the exact anonymous path set (health, fixed demo, static assets) versus session-required paths, with one interface test asserting that boundary.
* Action owner: Planning parent
* Exact resolving evidence: P06-T02 or P06-T03 lists hosted.py and the anonymous path set; a validation expectation asserts that estate screens and data require a session while health and the fixed demo remain public; P07-T02 documentation supersedes the deployment.md public-concept description
* Decision route: Direct planner correction

<!-- rpi:critique id=PC-010 -->
### PC-010 [Medium]: No invariant prevents forged ingress principal headers when trusted-ingress mode is not in force

* Related IDs: FR-14, FR-16, NFR-07, AC-13, P06-T02, P07-T01
* Evidence: .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md P06-T02 accepts "either the existing validated bearer principal or a trusted Container Apps authenticated principal in the production ingress path" and adds "auth mode and trusted-ingress configuration" to config, with a validation expectation for "trusted-ingress gating"; no requirement states what happens to client-supplied principal headers when that mode is disabled, in local development, or when the container is reached directly
* Concern: Accepting an ingress-injected principal introduces a header-trust boundary. The plan gates it by configuration but never states the fail-safe: headers ignored unless trusted-ingress mode is explicitly enabled, and never merged with bearer-derived claims.
* Impact: A permissive default would let a crafted header impersonate any tenant, collection, and role, defeating AC-13 and NFR-07 on the very deployment AC-14 requires.
* Smallest useful change: Add an explicit invariant to FR-14 or NFR-07 and a matching test expectation in P06-T02: ingress principal headers are honored only in configured trusted-ingress mode, are otherwise ignored entirely, and never augment a bearer principal.
* Action owner: Planning parent
* Exact resolving evidence: A requirement states the header-trust invariant; P06-T02 validation expectations include a spoofed-header rejection case in the default configuration
* Decision route: Direct planner correction

<!-- rpi:critique id=PC-011 -->
### PC-011 [Medium]: The coverage gate interacts badly with a PostgreSQL adapter whose integration tests may be unavailable

* Related IDs: AC-16, NFR-10, P06-T01, Locked Validation Evidence
* Evidence: pyproject.toml sets `fail_under = 75` with branch coverage over the whole `shaper` package, omitting only application/ports.py and interfaces/cli.py; .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md P06-T01 records the unresolved item that "PostgreSQL integration tests may require CI or local service availability"; the plan lists "Full existing test suite and coverage threshold" as validation evidence
* Concern: A new production adapter whose branches are exercised only when a database service is present counts against a package-wide coverage gate, and the plan states no intended handling.
* Impact: The named validation evidence may fail for environmental reasons, and the likely improvised remedy during implementation is to loosen the coverage configuration or add shallow tests, either of which weakens AC-16 without a recorded decision.
* Smallest useful change: State the intended handling in P06-T01: run the shared repository contract suite against a disposable PostgreSQL when available, and decide now whether the adapter is added to the coverage omit list with a recorded justification or must meet the gate through adapter-level tests.
* Action owner: Planning parent
* Exact resolving evidence: P06-T01 records the coverage handling decision, and Validation Evidence states the threshold expectation for the PostgreSQL adapter explicitly
* Decision route: Direct planner correction

<!-- rpi:critique id=PC-012 -->
### PC-012 [Medium]: No retention, deletion, or data-classification requirement for the customer content this increment introduces

* Related IDs: FR-01, FR-02, FR-04, FR-12, NFR-07, AC-14, P07-T01, P07-T02
* Evidence: .copilot-tracking/plans/2026-09-10/knowledge-estate-workflow-redesign-plan.md FR-01 offers rename and archive but no delete or purge, and the Canonical and Generated Targets section makes sources and artifacts immutable; docs/deployment.md warns "Do not add customer or tenant data to the prototype assets or demo service" and describes a development profile with Azure Files uploads and immutable releases
* Concern: The increment converts a fixed-sample development deployment into a durable store of real user-uploaded documents, derived artifacts, and workflow records, with no requirement covering deletion of an estate and its content, retention limits, or the data classification acceptable in the development environment.
* Impact: Users who upload the wrong document have no defined removal path, immutability guarantees can conflict with a deletion request, and the deployment documentation's data-handling guidance becomes stale in a way that affects real content rather than sample data.
* Smallest useful change: Add one requirement covering estate, source, and document deletion or an explicit non-goal with its rationale and mitigation, and require P07-T02 to state the data-classification limit for the development deployment.
* Action owner: Planning parent for the plan text; user for a deliberate deferral of deletion
* Exact resolving evidence: A requirement or Non-Goal entry states the deletion position and its rationale; P07-T02 scope includes the development-environment data-handling statement
* Decision route: Direct planner correction to record the position; deferring deletion entirely is a user decision worth confirming because it affects real customer content

<!-- rpi:critique id=PC-013 -->
### PC-013 [Low]: Approval invalidation ignores estimator-version and model-deployment changes

* Related IDs: FR-09, FR-10, NFR-03, NFR-04, P04-T02, P04-T03, P05-T01
* Evidence: .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md P04-T03 invalidates approval on source or recommendation change only, while P04-T02 pins the estimate to estimator version and model deployment and P05-T01 derives the job cap from that estimate
* Concern: A configuration change between approval and dispatch alters the basis of the approved cost and cap while leaving the approval valid.
* Impact: A user can approve one cost basis and receive execution against another, weakening the meaning of the pre-transform consent the user required.
* Smallest useful change: Include estimator version and model deployment in the dispatch-time revalidation set in P05-T01 and in the invalidation conditions in P04-T03.
* Action owner: Planning parent
* Exact resolving evidence: P04-T03 and P05-T01 list estimator version and model deployment among the conditions that invalidate or block dispatch
* Decision route: Direct planner correction

<!-- rpi:critique id=PC-014 -->
### PC-014 [Low]: The Bicep parameter target names a file that does not exist

* Related IDs: P07, P07-T01
* Evidence: .copilot-tracking/details/2026-09-10/knowledge-estate-workflow-redesign-phase-details.md P07 and P07-T01 target "bicep/dev.parameters.json"; the repository contains bicep/dev.bicepparam and docs/deployment.md validates with `--parameters bicep/dev.bicepparam`
* Concern: The named target does not exist, so implementation may create a redundant parameter file or edit the wrong artifact.
* Impact: Minor wasted work and a possible divergence between the deployment script, documentation, and the parameter file actually used.
* Smallest useful change: Replace the target path with bicep/dev.bicepparam in P07 and P07-T01.
* Action owner: Planning parent
* Exact resolving evidence: P07 and P07-T01 reference bicep/dev.bicepparam
* Decision route: Direct planner correction

<!-- rpi:critique id=PC-015 -->
### PC-015 [Low]: Rename and archive behavior in FR-01 has no acceptance coverage

* Related IDs: FR-01, AC-01, P02-T01
* Evidence: .copilot-tracking/plans/2026-09-10/knowledge-estate-workflow-redesign-plan.md FR-01 includes rename and archive; AC-01 covers creation, naming policy, and persistence only; P02-T01 mentions archive in its intent with no validation expectation for it
* Concern: The plan does not state what archiving means operationally, in particular whether an archived estate still accepts sync, discovery, recommendation, decision, or transformation operations.
* Impact: An ambiguous archive state can leave a "closed" estate silently able to consume model tokens and produce artifacts.
* Smallest useful change: Extend AC-01 or add one acceptance condition stating that an archived estate rejects new runs and decisions while remaining readable, and add the matching validation expectation to P02-T01.
* Action owner: Planning parent
* Exact resolving evidence: An acceptance criterion and a P02-T01 validation expectation define archived-estate behavior
* Decision route: Direct planner correction

## Strengths and Residual Risk

* Requirement-to-evidence traceability is strong. Every functional requirement, task, and locked boundary cites specific research evidence IDs from C1-C25, and the critique found no requirement that contradicts its cited evidence.
* All confirmed user requirements are represented without dilution: the five specialist roles under deterministic orchestration (FR-06, AC-12), named multi-source estates (FR-01, FR-02), per-document scoring with explainable effort (FR-05), selection-scoped recommendations (FR-07), a pre-approval token estimate on every proposal (FR-08), per-document approve or decline with source-version pinning (FR-09, FR-10), non-destructive named artifacts (FR-12), and a live Azure deployment with truthful states (FR-03, FR-15, AC-14).
* The safety invariants are unusually concrete for a plan of this size: zero-gateway-call evidence for rejected dispatch (P05-T01), a full malicious-archive matrix (P02-T02), deterministic byte-identical rendering (P05-T03), and immutable estimate-versus-actual separation (P05-T02).
* The plan resolves all three research Unresolved Decisions rather than inheriting them: generic URL scope is deferred to a Non-Goal with a threat-model rationale, collision behavior uses a deterministic source-ID suffix, and output review is made mandatory for every artifact.
* The seven-module production cap appears achievable on inspection: every other change lands in modules that already exist (orchestration, assessment, uploads, ingestion, sharepoint, jobs, compiler, shaping, publication, sqlite, http, auth, cli, config), and the prototype surface adds no files.
* Residual risk explicitly accepted by the plan and not disputed here: readiness and effort scores remain uncalibrated heuristics; token estimates are labeled approximations until actuals accumulate; live SharePoint sync may remain externally blocked; a qualified-human accessibility review remains outside the implementation claim.
* Residual risk worth recording: the Maximum Additions section governs modules and tests but not dependency additions, while P06-T01 adds a PostgreSQL driver to pyproject.toml and uv.lock. This is a reasonable and necessary change; it is simply not covered by the stated boundary.

## Questions or Blocking Evidence Gaps

* None blocking. All findings are answerable from the plan, the phase details, C1-C25, docs/architecture.md, docs/deployment.md, and the repository structure already inspected. No additional research is required to resolve any PC finding.
* One optional user confirmation, not a blocker: PC-012 asks whether deferring estate and document deletion in this increment is intended, given that the increment stores real customer content for the first time.

## Limitations

* No code was read or executed. Claims about existing behavior are taken from research evidence C1-C25 and the supplied documentation; only file existence, test-module names, and the pytest, coverage, and mypy configuration were checked directly to test the plan's factual assertions about its own boundary.
* Azure, Entra, Microsoft Graph, and Container Apps authentication behavior could not be verified. PC-001, PC-009, and PC-010 identify undefined plan positions, not confirmed platform defects.
* Effort, duration, and sequencing feasibility were not assessed beyond internal consistency of phase dependencies, which are coherent as written.
* The critique does not grade formatting or template adherence; every finding names a substantive planning risk.

## Recommended Next Action

* Highest-impact finding: PC-001
* Action owner: planning parent
* Smallest next action: Revise FR-16, P06-T02, P07-T01, and the Dependencies list to define the interactive principal-to-collection-role mapping and its tenant assignment dependency, then apply the remaining direct corrections (PC-002 through PC-015) in the same revision pass without a further critique.
* User response required: no. Every recommended change is a planner-owned correction consistent with current user direction; only a deliberate deferral of estate deletion (PC-012) or a decision to raise the locked seven-test cap instead of remapping ownership (PC-003) would need user confirmation.
