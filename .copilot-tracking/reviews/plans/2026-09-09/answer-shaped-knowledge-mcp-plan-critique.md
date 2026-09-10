<!-- markdownlint-disable-file -->
# RPI Plan Critique: Agentic Answer-Shaped Knowledge Compiler

## Metadata

* Task ID: answer-shaped-knowledge-mcp
* Critique date: 2026-09-09
* Plan: .copilot-tracking/plans/2026-09-09/answer-shaped-knowledge-mcp-plan.md
* Phase details: .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md
* Critique execution status: Complete

## Inputs and Criterion Boundary

* Task context and caller requirements: Compile unstructured policies, FAQs, and similar material into versioned answer-ready evidence units; implement answer shaping as agentic AI; accept SharePoint document-library URLs or secured direct uploads; accept caller-selected output paths with SharePoint preferred; preserve source grounding, provenance, and versioning; expose appropriate operations through MCP.
* Research and evidence considered: .copilot-tracking/research/2026-09-09/answer-shaped-knowledge-mcp-research.md (W1-W32, Q1-Q10, Current Decisions, Unresolved Decisions, Alternatives, Open Questions and Residual Uncertainty).
* Decisions, dependencies, and acceptance criteria considered: Plan User Decisions and Requirements, Goals, Scope and Non-Goals, FR-01 through FR-14, NFR-01 through NFR-09, AC-01 through AC-14, Implementation Baseline and Change Budget, Test Ownership and Validation Strategy, Phase Checklist P01 through P07 with all 21 tasks, Dependencies, Critique Disposition, Follow-Up Items, and all phase-detail Context, Intent, Boundaries, Likely Targets, Dependencies, Validation Expectations, Completion Evidence, and Unresolved Items sections.
* Assessment boundary: This is the single final-candidate critique and assesses the whole supplied boundary once. It can conclude whether the plan is internally consistent, faithful to the caller's confirmed direction, traceable to research evidence, and executable as sequenced. It cannot verify repository state beyond the plan's own "empty repository" assertion, cannot verify live SharePoint, model, or evaluator behavior, and did not conduct new research. File-count analysis is derived only from the Likely Targets enumerated in the supplied phase details.

## Coverage Assessment

| Requirement, research, phase, or task ID | Coverage | Evidence or concern |
|------------------------------------------|----------|---------------------|
| User decisions (agentic shaping, dual inputs, caller output path, derivative units, MCP boundary) | Covered | Each confirmed decision in the research Direction Controls and Current Decisions tables maps to a plan requirement and at least one task. |
| Goals | Partial | Goal "make every source, unit, job, agent run, ... auditable and versioned" is not fully realized: no lifecycle exists for units whose source version changes or is deleted (PC-002). |
| Scope and Non-Goals | Covered | In-scope list matches FR/NFR set; non-goals match research rejections for GraphRAG, long-context routing, multi-agent, raw MCP transfer, and automatic publication. |
| FR-01 | Covered | P02-T01, P02-T02, P02-T03; AC-01 asserts the shared contract. |
| FR-02 | Covered | P02-T01 boundaries and validation expectations track W23 controls item by item. |
| FR-03 | Partial | Source-side delta, tombstones, and overlap exclusion are planned in P02-T02, but no task consumes a change or deletion to invalidate derived published units (PC-002) or to define the resulting release content (PC-001). |
| FR-04 | Covered | P02-T03 golden fixtures cover order, heading path, location, tables, Unicode, malformed input, and limits. |
| FR-05 | Covered | P03-T01 and P03-T03 with static allowlist, budget, and cancellation tests. |
| FR-06 | Covered | P03-T02 schema-constrained output plus P01-T02 versioned schemas. |
| FR-07 | Partial | P04-T01 and P04-T02 are strong, but P03-T03 requires validator feedback before P04-T01 exists (PC-007). |
| FR-08 | Partial | State set omits any superseded, withdrawn, or retired terminal state for published units (PC-002). |
| FR-09 | Partial | Manifest-last and eTag pointer protocol are complete for one run; release completeness across incremental runs is undefined (PC-001), and non-current or orphan releases have no lifecycle (PC-012). |
| FR-10 | Partial | Lexical path is concrete; the vector path has no embedding provider, port, or credential-free strategy (PC-005). Authorization filtering is asserted without a defined model (PC-003). |
| FR-11 | Partial | Tool and resource surface matches research; model-invoked `knowledge.compile` has no server-side quota or cost cap and relies on advisory host confirmation (PC-009). |
| FR-12 | Partial | Idempotency, checkpoints, and resume are well specified; the interaction between idempotent replay and incremental release content is unspecified (PC-001). |
| FR-13 | Partial | HTTP and CLI use cases are defined, but the reviewer and operator identity model is deferred to "verified actor headers or tokens" (PC-003). |
| FR-14 | Covered | P01-T02, P03-T03, P05-T01, and P07-T03 record derivation, run, validator, review, index, and release provenance consistent with W12. |
| NFR-01 | Covered | Deterministic validators plus release-integrity tests; AC "deliberately broken reference blocks publication" is objectively testable. |
| NFR-02 | Covered | Allowlist, budget, adversarial, and forced-exhaustion tests align with W26, W31, and W32. |
| NFR-03 | Covered | P01-T03 transactions, P03-T03 resume, P05-T01 rollback, P06-T01 restart, and P07-T02 fault injection. |
| NFR-04 | Partial | The 10,000-unit p95 target is measurable, but it is meaningless for the semantic route until the embedding strategy exists (PC-005); the "documented development profile" is not yet defined. |
| NFR-05 | Partial | Per-run budgets are enforced; there is no aggregate per-principal or per-collection cost ceiling for externally triggered compiles (PC-009). |
| NFR-06 | Partial | Gate intent is sound, but the regression gate has no defined baseline artifact, tolerance band, storage location, or approval owner (PC-008). |
| NFR-07 | Partial | Conflicts with FR-10 and AC-06 semantic-paraphrase coverage unless a credential-free embedding strategy is named (PC-005). |
| NFR-08 | Covered | Import-boundary tests, Ruff, mypy strict, and one documented validation command. |
| NFR-09 | Covered | Redaction tests, secret scan, structured-log assertions, and source-text logging off by default. |
| AC-01 | Covered | Directly exercised by P02 completion evidence. |
| AC-02 | Covered | P03-T01 and P03-T03 tests, including abstention and write-tool absence. |
| AC-03 | Covered | P04-T01 and P04-T02 explicitly forbid silent fallback and automatic pass. |
| AC-04 | Partial | Review is required by default with no volume, sampling, or risk-tiering policy, so first-corpus publication throughput is unbounded (PC-010). |
| AC-05 | Covered | P05-T01 and P05-T02 ordering, concurrency, and rollback tests. |
| AC-06 | Partial | "Authorized evidence" has no defined authorization model (PC-003); paraphrase coverage depends on PC-005. |
| AC-07 | Partial | Surface exclusions are correct; compile invocation control is advisory only (PC-009). |
| AC-08 | Covered | P06-T01 duplicate submission, interruption, and cancellation tests. |
| AC-09 | Partial | "Complete lineage" holds within one release; corpus-level completeness is undefined for incremental runs (PC-001). |
| AC-10 | Covered | P07-T01 requires at least 30 synthetic cases across all five categories with explicit subject-matter-review markers. |
| AC-11 | Partial | Compares agent against fixed chain only; it does not test the answer-unit-versus-contextual-chunk value hypothesis that research names as the primary residual uncertainty (PC-006). |
| AC-12 | Covered | P07-T02 covers injection, budget, malformed, cross-tenant, partial publication, stale eTag, and restart. |
| AC-13 | Partial | Depends on resolving PC-005 for the credential-free path to remain honest. |
| AC-14 | Covered | P07-T03 documentation set matches the operational surface. |
| P01 and P01-T01 through P01-T03 | Partial | Contracts are thorough, but `Collection` and `Tenant` are load-bearing scope concepts used in P03-T01 and P06-T02 that never appear in the domain model (PC-003), and no embedding port is listed (PC-005). |
| P02 and P02-T01 through P02-T03 | Covered | Strongest phase; security, identity, delta, and parser boundaries are concrete and evidence-linked. |
| P03 and P03-T01 through P03-T03 | Partial | Trust boundary is excellent; P03-T03 has an unresolved backward dependency on P04-T01 validators (PC-007). |
| P04 and P04-T01 through P04-T03 | Partial | Validation authority is correct; review operability and reviewer identity are underspecified (PC-010, PC-003). |
| P05 and P05-T01 through P05-T03 | Partial | Single-run publication protocol is credible; cross-run release semantics, retention, and the embedding path are not (PC-001, PC-005, PC-012). |
| P06 and P06-T01 through P06-T03 | Partial | Adapter-over-use-case structure is correct; compile exposure control is incomplete (PC-009). |
| P07 and P07-T01 through P07-T03 | Partial | Broad and honest evidence plan; missing the chunk baseline (PC-006) and the regression baseline definition (PC-008); the file-budget check arrives too late (PC-004). |
| Dependencies | Partial | Five external dependencies are named; an embedding model or deployment and an identity provider are absent (PC-005, PC-003). |
| Risks and assumptions | Covered | "What You May Not Know" states nondeterminism, review-by-default, and deferred complexity honestly and matches W30, W27, and W28. |
| Test ownership | Covered | Tests land with behavior; connector suites are shared across fakes and live adapters; live suites skip with explicit reasons. |
| Exact removals: none | Covered | Correct for a repository with no production files. |
| Maximum 75 tracked additions | Missing | Enumerated Likely Targets exceed the cap well before P04 begins (PC-004). |
| Canonical and generated targets | Partial | JSON Schemas are listed as both canonical targets and generated exports, and P01 commits them as canonical snapshots (PC-011). |
| Semantic versus regression coverage | Partial | Definitions are sound, but with a deterministic fake model both categories exercise plumbing only until a live baseline exists (PC-008). |
| Validation evidence | Covered | One final validation command plus named additional performance and live-cloud commands, with completion evidence per phase. |

## Verdict

* Verdict: Revise
* Rationale: The plan is architecturally credible, faithful to every confirmed user decision, and unusually well traced from W1-W32 into requirements, tasks, and validation evidence. Its trust boundary, publication protocol, and honest treatment of nondeterminism are implementation-ready. However, three load-bearing behaviors that the caller's requirements depend on are undefined rather than deferred: what a release contains when only some sources changed, what happens to published units when their source version changes or disappears, and how retrieval-time authorization and reviewer identity are established. A fourth issue, the 75-file change budget, is demonstrably unachievable as written and is only checked in the final task. These are correctable inside the plan without new research.

## Findings

<!-- rpi:critique id=PC-001 -->
### PC-001 [Critical]: Release content under incremental compilation is undefined

* Related IDs: FR-03, FR-09, FR-12, AC-05, AC-09, P02-T02, P05-T01, P05-T03, P06-T01
* Evidence: .copilot-tracking/plans/2026-09-09/answer-shaped-knowledge-mcp-plan.md FR-03, FR-09, FR-12; .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md P02-T02 "delta resume", P05-T01 "Manifest is the final release artifact", P05-T03 "release-scoped FTS5 and vector projections"; .copilot-tracking/research/2026-09-09/answer-shaped-knowledge-mcp-research.md SharePoint snapshot layout showing `releases/<run-id>/documents/<source-document-id>/<source-version>/units.jsonl` and a single `current.json`. The strings "incremental" and "carry" appear nowhere in the plan in a release-content sense.
* Concern: Delta synchronization implies a run may process only changed documents, while `current.json` points to exactly one immutable release manifest and indexes are release-scoped. Nothing states whether a release is a full corpus snapshot with unchanged units carried forward, or a delta. Both readings are load-bearing and neither is chosen.
* Impact: If a release is a delta, the current release and every index built from it silently lose all unchanged content, which breaks FR-10, AC-06, and AC-09 corpus completeness. If a release is a full snapshot, every run republishes previously approved units, which collides with the default human-review gate in AC-04 unless approvals are carried forward by `unit_version`, and it multiplies SharePoint storage per run. Implementation would have to invent this contract mid-build, after P01 schemas and P05 sinks are frozen.
* Smallest useful change: State one release-composition rule in the plan and in P05-T01: a release is a complete corpus snapshot, assembled from newly shaped units plus carried-forward units whose `unit_version` and source version are unchanged and whose prior approval is still valid. Add the carry-forward rule to FR-09 and FR-12, add a matching acceptance criterion, and add "carry-forward set" to the P05-T01 manifest contract and the P05-T03 index build.
* Action owner: planning parent
* Exact resolving evidence: FR-09 and P05-T01 state the composition rule; the release manifest contract lists carried-forward units with their originating run ID; P05-T01 validation expectations include a test in which a second run over one changed document produces a current release that still resolves every unchanged unit; P05-T03 index build consumes that full release.
* Decision route: direct planner correction

<!-- rpi:critique id=PC-002 -->
### PC-002 [High]: No invalidation or supersession lifecycle for published units

* Related IDs: FR-03, FR-08, FR-14, NFR-01, AC-09, P01-T02, P04-T03, P05-T01
* Evidence: .copilot-tracking/plans/2026-09-09/answer-shaped-knowledge-mcp-plan.md FR-08 state list (`drafted`, `validated`, `quarantined`, `human-approved`, `rejected`, `published`) and line 67 "Preserve source grounding, provenance, freshness, and version history"; .copilot-tracking/research/2026-09-09/answer-shaped-knowledge-mcp-research.md Key Discoveries "Freshness is a lineage problem. Every derived unit must identify the exact source version and transformation so changed or deleted sources can invalidate descendants" and Q6 implication "Preserve routing, lineage, invalidation, and least-privilege boundaries". The words "supersede", "invalidate", and "stale unit" appear nowhere in the plan or phase details; "freshness" appears once, only as a restatement of user direction.
* Concern: FR-03 propagates renames, moves, changes, and deletions at the source-connector level only. No requirement, state, acceptance criterion, or task defines what happens to already-published units whose source version was replaced or whose source document was deleted or moved out of the configured root.
* Impact: The system can publish evidence that cites a source version that no longer exists, which directly contradicts NFR-01's "existing source spans from the manifest's exact source versions" once a second run occurs, and defeats the caller's freshness requirement. It also leaves no withdrawal path for content that must be removed for privacy or governance reasons, which is expensive to retrofit after immutable release semantics are frozen in P01 and P05.
* Smallest useful change: Add `superseded` and `withdrawn` to the FR-08 state set and to the P01-T02 state enums, add a requirement that a source-version change or deletion event marks descendant units in the affected state with the triggering source event recorded in provenance, and add the corresponding transition and exclusion rules to P04-T03 and P05-T01.
* Action owner: planning parent
* Exact resolving evidence: FR-08 lists the two additional states; P01-T02 domain state enums include them; P04-T03 validation expectations include a test where a changed and a deleted source version drive descendant units to `superseded` and `withdrawn`; P05-T01 excludes those units from the next current release while retaining them in prior immutable releases with the reason recorded.
* Decision route: direct planner correction

<!-- rpi:critique id=PC-003 -->
### PC-003 [High]: Authorization and actor identity are asserted throughout but never specified

* Related IDs: FR-10, FR-11, FR-13, NFR-02, AC-04, AC-06, AC-07, AC-12, P01-T02, P03-T01, P04-T03, P05-T03, P06-T02, P06-T03
* Evidence: .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md P03-T01 "Tool calls cannot cross collection, tenant, source", P05-T03 "Queries cannot retrieve unauthorized units", P06-T02 "unauthorized collection", P04-T03 unresolved item "Identity provider integration can be deployment-specific behind verified actor headers or tokens"; P01-T02 domain contract list contains no `Collection`, `Tenant`, or `Principal` type; .copilot-tracking/research/2026-09-09/answer-shaped-knowledge-mcp-research.md Open Questions lists "access-control model" as an important unknown, and W13 requires access control applied at retrieval time.
* Concern: Tenant, collection, and authorized-unit filtering are referenced as security invariants in at least six tasks and four acceptance criteria, yet no requirement defines how a principal is authenticated, how a unit's authorization labels are derived from the source item's SharePoint permissions, or whether query results are permission-trimmed per user or only scoped per collection. The reviewer approval gate, which is the primary control preventing unsafe publication, is left behind "verified actor headers".
* Impact: If the service reads sources with app-only Selected permissions and does not trim results, any caller with query access sees evidence derived from documents they cannot open in SharePoint, which is a confidentiality regression relative to the source system and a plausible blocker for a governed corpus. AC-06, AC-07, and AC-12 cannot be objectively verified against an undefined model, and the plan's claim that "no blocker prevents implementation" is therefore overstated.
* Smallest useful change: Add one requirement that fixes the authorization model for this build, most simply collection-scoped authorization with a recorded source-permission snapshot and an explicit non-goal for per-user SharePoint permission trimming, plus a named authenticated-actor mechanism for review and administrative operations. Add `Collection`, `Tenant`, and `Principal` to P01-T02 and a dependency for the identity provider.
* Action owner: user, then planning parent
* Exact resolving evidence: A new functional requirement states the authorization unit of isolation and whether permission trimming is in scope; P01-T02 domain contracts include the scope and principal types; P04-T03 names the authenticated actor mechanism rather than headers; Dependencies lists the identity provider; AC-06 and AC-12 reference the chosen model.
* Decision route: significant or divergent user decision, because per-user permission trimming versus collection-scoped access materially changes the connector permission model, the unit schema, and the query path, and current user direction does not resolve it

<!-- rpi:critique id=PC-004 -->
### PC-004 [High]: The 75-file change budget is not achievable and is verified too late

* Related IDs: Implementation Baseline and Change Budget, P07-T03, all phase Likely Targets
* Evidence: .copilot-tracking/plans/2026-09-09/answer-shaped-knowledge-mcp-plan.md "Maximum additions: 75 tracked files including configuration, lockfile, source, tests, fixtures, schemas, and documentation"; .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md P07-T03 validation expectation "Total tracked additions remain within the 75-file budget or the plan is amended"; enumerated Likely Targets across P01 through P03 alone name roughly 45 explicit files plus five directory targets (`schemas/`, `tests/unit/domain/`, `migrations/`, `prompts/`, `tests/fixtures/documents/`) that each expand to several tracked files, and P07-T01 requires "At least 30 synthetic cases".
* Concern: P01 through P03 plausibly consume the entire budget before validation, review, publication, retrieval, three interface surfaces, telemetry, four documentation files, evaluation rubrics, and the evaluation case set are written. P04 through P07 name approximately 19 further source modules, 15 further test modules, and the case corpus.
* Impact: A budget that is exceeded by roughly a factor of two is not a control; it either forces an unplanned amendment at the last task or pressures implementation to bundle unrelated concerns into fewer files, which conflicts with NFR-08 maintainability. Discovering this in P07-T03 is the least useful moment.
* Smallest useful change: Recompute the budget from the enumerated Likely Targets, restate it as a per-phase allowance with directory targets expanded, and treat the evaluation case corpus as one or two data files rather than 30 tracked files. Move the budget check to the end of each phase.
* Action owner: planning parent
* Exact resolving evidence: The Implementation Baseline states a recomputed total with a per-phase breakdown consistent with the Likely Targets; each phase's completion evidence includes its allowance check; P07-T01 states the case corpus file layout. If the 75-file cap is an externally imposed constraint rather than a planner estimate, the plan instead records the scope reduction the user selects.
* Decision route: direct planner correction, unless the cap is a user constraint, in which case it becomes a scope decision

<!-- rpi:critique id=PC-005 -->
### PC-005 [High]: No embedding provider, port, or credential-free strategy for the vector route

* Related IDs: FR-10, NFR-04, NFR-07, AC-06, AC-13, P01-T03, P05-T03, Dependencies
* Evidence: .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md P01-T03 port list (`SourceConnector`, `UploadStore`, `DocumentParser`, `ModelGateway`, `AgentTool`, `Validator`, `Evaluator`, `ReviewRepository`, `ReleaseSink`, `LexicalIndex`, `VectorIndex`, clock, ID, transaction) with no embedding port, and P05-T03's only reference, an unresolved item stating "Embedding model is configured through the model/index adapter and recorded in the release"; .copilot-tracking/plans/2026-09-09/answer-shaped-knowledge-mcp-plan.md NFR-07 "`uv run pytest` completes locally with no cloud sign-in" and FR-10 acceptance requiring coverage of "semantic paraphrases"; Dependencies names an Azure OpenAI deployment for shaping and evaluation only.
* Concern: The hybrid retrieval decision from W4 and W13 requires embeddings, but no port owns their production, no dependency names an embedding deployment, and no strategy explains how vector representations exist during credential-free local runs.
* Impact: Either NFR-07 and AC-13 break because local tests need a cloud embedding call, or FR-10, NFR-04, and AC-06 become vacuous locally because a deterministic stub cannot demonstrate paraphrase retrieval. Both outcomes are discovered in P05-T03 after the ports are frozen in P01-T03.
* Smallest useful change: Add an `EmbeddingProvider` port to P01-T03 with a deterministic local implementation, state in P05-T03 and the Test Ownership section that local paraphrase tests assert contract and ranking behavior only while semantic quality is an opt-in live-model suite, and add the embedding deployment to Dependencies.
* Action owner: planning parent
* Exact resolving evidence: P01-T03 lists the embedding port; P05-T03 names the local and live implementations and which assertions each supports; NFR-07 and AC-13 explicitly acknowledge the split; Dependencies lists the embedding deployment.
* Decision route: direct planner correction

<!-- rpi:critique id=PC-006 -->
### PC-006 [High]: The core value hypothesis is never tested

* Related IDs: AC-11, NFR-06, P07-T01, research Q1, Q4, W4, W5, W10
* Evidence: .copilot-tracking/research/2026-09-09/answer-shaped-knowledge-mcp-research.md Residual uncertainty "The expected benefit of an agent over a fixed structured generation workflow, and of answer units over contextual source chunks, is corpus-specific", and Potential Next Research priority H "Benchmark answer units versus contextual source chunks on a representative corpus - Tests the core value hypothesis"; .copilot-tracking/plans/2026-09-09/answer-shaped-knowledge-mcp-plan.md AC-11 compares only "Agent-versus-fixed-chain"; the word "chunk" appears nowhere in the plan or phase details.
* Concern: Research names two independent uncertainties. The plan operationalizes one of them, the agent versus fixed chain comparison, and silently drops the other, whether shaped answer units retrieve better than contextualized source chunks. The Follow-Up Items list defers OCR, vector backends, and GraphRAG but not this benchmark.
* Impact: The project builds seven phases of shaping, validation, review, and publication machinery on a premise it never measures, and the P07 evidence set cannot answer the first question a stakeholder will ask about whether the compiler earned its cost. A contextual-chunk baseline is cheap to add inside the existing harness and expensive to add later.
* Smallest useful change: Extend P07-T01 and AC-11 to include a contextualized source-chunk retrieval baseline over the same synthetic corpus and the same retrieval metrics, reported alongside the fixed-chain comparison and with the same "the unit path need not win for the implementation to be accepted" framing.
* Action owner: planning parent
* Exact resolving evidence: AC-11 names the chunk baseline; P07-T01 boundaries and likely targets include the baseline builder and its report; the runner emits comparable retrieval metrics for units and chunks.
* Decision route: direct planner correction

<!-- rpi:critique id=PC-007 -->
### PC-007 [Medium]: P03-T03 depends on validation feedback that P04-T01 delivers later

* Related IDs: FR-05, FR-07, P03, P03-T03, P04, P04-T01
* Evidence: .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md P03-T03 intent "Coordinate tool calls, candidate generation, preliminary validation feedback, repair attempts" with dependencies "P03-T01 and P03-T02"; P04-T01 dependencies "P01-T02 and candidate output from P03"; .copilot-tracking/plans/2026-09-09/answer-shaped-knowledge-mcp-plan.md P03 depends on "P01 and P02" and P04 depends on "P01 and P03".
* Concern: The repair loop is defined as consuming validator feedback, but the validators are built one phase later and are themselves declared to depend on P03 output. Nothing states which minimal checks exist inside P03.
* Impact: Implementation either stalls at P03-T03, builds a throwaway validator, or quietly implements P04-T01 rules inside P03 and duplicates them, which weakens the deterministic-validation authority that NFR-01 and AC-03 rely on.
* Smallest useful change: State in P03-T03 that the loop consumes a `Validator` feedback port defined in P01-T03, backed in P03 only by schema and source-span-existence checks, and that all remaining deterministic rules land in P04-T01 behind the same port with no duplication.
* Action owner: planning parent
* Exact resolving evidence: P03-T03 boundaries name the port and the two in-phase checks; P04-T01 states that it extends the same port; an architecture or unit test asserts that no validation rule is implemented in both modules.
* Decision route: direct planner correction

<!-- rpi:critique id=PC-008 -->
### PC-008 [Medium]: The regression and upgrade gate has no baseline artifact, tolerance, or owner

* Related IDs: NFR-06, AC-11, P07-T01, Test Ownership and Validation Strategy
* Evidence: .copilot-tracking/plans/2026-09-09/answer-shaped-knowledge-mcp-plan.md NFR-06 acceptance "A model, prompt, schema, or validator change cannot update the current release when its required evaluation gate fails" and "Regression coverage compares normalized units, evaluator scores, retrieval results, state transitions, latency, and cost"; .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md P07-T01 intent includes an "upgrade regression gate" but its Likely Targets and Validation Expectations name no baseline artifact. The only "baseline" defined elsewhere is the fixed-chain comparison.
* Concern: A regression gate requires a stored, versioned, approved baseline and a tolerance band for scores that are nondeterministic by W30. None of the baseline's provenance, storage location, refresh procedure, approval owner, or comparison tolerance is specified, and against the deterministic fake model the comparison exercises plumbing only.
* Impact: The gate that NFR-06 promises as the control over model, prompt, and schema upgrades cannot be enforced as described, so the strongest safety claim in the plan is unimplementable as written.
* Smallest useful change: Specify in P07-T01 the baseline artifact and where it is stored, that it is produced by a configured live-model run, its approval owner, and the numeric tolerance for score drift; state in the Test Ownership section that the fake-model regression suite verifies gate mechanics while threshold enforcement requires the live baseline.
* Action owner: planning parent
* Exact resolving evidence: P07-T01 names the baseline artifact, producer, owner, and tolerance; NFR-06's verification approach distinguishes mechanics from threshold enforcement; a test proves that a degraded score below tolerance blocks the current-pointer update.
* Decision route: direct planner correction

<!-- rpi:critique id=PC-009 -->
### PC-009 [Medium]: Model-invoked compilation is bounded only by advisory host confirmation

* Related IDs: FR-11, NFR-05, AC-07, P06-T03, W2, W26, W32
* Evidence: .copilot-tracking/plans/2026-09-09/answer-shaped-knowledge-mcp-plan.md FR-11 acceptance "confirmation metadata for compilation" and NFR-05 which caps "each run"; .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md P06-T03 "Compile accepts references only and exposes that confirmation is required"; the words "quota" and "rate limit" appear nowhere; .copilot-tracking/research/2026-09-09/answer-shaped-knowledge-mcp-research.md W26 requires explicit authorization for sensitive operations and W32 requires limited autonomous scope for high-impact actions.
* Concern: `knowledge.compile` is a model-controlled, mutating, cost-incurring operation whose only invocation control is metadata that the host may or may not honour. Per-run budgets do not bound how many runs a caller can start.
* Impact: A prompt-injected or misbehaving host agent can start repeated expensive compile jobs, exhausting model spend and worker capacity, which is the excessive-agency pattern the plan otherwise defends against well.
* Smallest useful change: Add a server-enforced compile authorization and quota rule to FR-11 and NFR-05, covering concurrent jobs and aggregate cost per principal and collection, independent of host confirmation, and add the corresponding test to P06-T03.
* Action owner: planning parent
* Exact resolving evidence: FR-11 and NFR-05 state the server-side limits; P06-T03 validation expectations include a test where repeated compile invocations are rejected at the quota with a structured error; AC-07 references the enforced limit rather than confirmation metadata alone.
* Decision route: direct planner correction

<!-- rpi:critique id=PC-010 -->
### PC-010 [Medium]: Human-review-by-default has no volume, sampling, or risk-tiering policy

* Related IDs: AC-04, NFR-06, FR-08, P04-T03, Dependencies
* Evidence: .copilot-tracking/plans/2026-09-09/answer-shaped-knowledge-mcp-plan.md AC-04 "the default policy requires this approval before publication" and "Automatic publication remains disabled until a subject-matter-reviewed dataset defines and meets live thresholds"; .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md P04-T03 excludes "A full graphical review portal" and permits "batch review only when evidence and policy match"; no requirement states an expected unit volume per document or per corpus.
* Concern: The one gate that must clear before anything is ever published is manual, has no per-collection or risk-tiered scoping, is served by minimal HTTP and CLI surfaces, and faces an unbounded number of generated units.
* Impact: The first realistic corpus can produce more units than reviewers can process, so the system reaches P07 fully built but unable to publish anything, and the automatic-publication threshold work that depends on reviewed data never starts.
* Smallest useful change: Add a review-policy requirement that supports per-collection risk tiers and a defined initial mode, such as full review for policy-rule units and sampled review for low-risk units, with the sampling rate and tiering owned by the already-listed subject-matter-reviewer dependency; state an expected units-per-document order of magnitude in P04-T03 so the queue and batch design is sized deliberately.
* Action owner: planning parent, with thresholds owned by the named subject-matter reviewers
* Exact resolving evidence: A requirement or acceptance criterion states the configurable review-policy tiers and the initial mode; P04-T03 records the assumed unit volume and the batch-review contract that satisfies it; Dependencies restates who owns the tier thresholds.
* Decision route: direct planner correction, with threshold values already routed to the recorded governance dependency

<!-- rpi:critique id=PC-011 -->
### PC-011 [Low]: JSON Schemas are listed as both canonical and generated targets

* Related IDs: Implementation Baseline and Change Budget, P01, P01-T02, NFR-08
* Evidence: .copilot-tracking/plans/2026-09-09/answer-shaped-knowledge-mcp-plan.md "Canonical targets: Pydantic domain models, workflow state machine, answer-unit schema, release-manifest schema, ..." and "Generated targets: `uv.lock`, exported JSON Schemas, ..."; .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md P01-T02 likely target "schemas/: Exported versioned JSON Schemas" and P01 completion evidence "Exported schemas match committed canonical snapshots".
* Concern: The answer-unit and release-manifest schemas are named canonical while the exported JSON Schemas are named generated, and P01 commits the exports as canonical snapshots. Which artifact an implementer edits when the contract changes is ambiguous.
* Impact: Ambiguity between a hand-authored schema and a Pydantic-derived export invites duplicate maintenance and silent contract drift for the artifacts that external release consumers depend on.
* Smallest useful change: State that the Pydantic models are the single canonical source and that `schemas/` holds generated snapshots committed only for change detection and consumer distribution, never hand-edited.
* Action owner: planning parent
* Exact resolving evidence: The Canonical and Generated target lists name the models as canonical and the schema files as committed generated snapshots; P01-T02 states the regeneration command and that drift fails the build.
* Decision route: direct planner correction

<!-- rpi:critique id=PC-012 -->
### PC-012 [Low]: Release retention, pruning, and non-current releases have no lifecycle

* Related IDs: FR-09, AC-05, AC-14, P05-T01, P05-T02, P07-T03
* Evidence: .copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md P05-T02 "Concurrent current-pointer updates produce one winner and one diagnosed conflict"; retention appears only for direct uploads in FR-02 and P02-T01 and as a documentation topic in P07-T03; the word "prune" appears nowhere.
* Concern: Every run writes a full immutable release folder to SharePoint or the filesystem, and a loser in a current-pointer race leaves a complete, permanently unreferenced release. Nothing defines how long releases are kept, whether orphans are cleaned up, or what the losing job's terminal state is.
* Impact: Storage in a governed SharePoint library grows without bound, orphaned releases are indistinguishable from valid rollback targets, and AC-14's rollback documentation has no retention contract to describe.
* Smallest useful change: Add a release retention and orphan-handling rule to FR-09 and P05-T01, covering the minimum retained release count, the terminal state of a race loser, and whether orphan releases are marked or removed.
* Action owner: planning parent
* Exact resolving evidence: FR-09 states the retention and orphan rule; P05-T01 and P05-T02 validation expectations include the race loser's terminal state and orphan marking; P07-T03 documents the retention and rollback procedure against that rule.
* Decision route: direct planner correction

## Strengths and Residual Risk

* The agent trust boundary is the strongest part of the plan and is fully evidence-backed. NFR-02, P03-T01, and P03-T03 implement W26, W31, and W32 concretely: a static read-only allowlist, tenant and source scoping, independently enforced call, token, time, and retry budgets, no publication credential, and no persistent cross-source memory. AC-02 and AC-12 make this objectively testable rather than aspirational.
* Requirement-to-task traceability is complete. Every one of FR-01 through FR-14, NFR-01 through NFR-09, and AC-01 through AC-14 maps to at least one `Pxx-Txx` task, and every task cites requirements or W-IDs. Nothing in the plan is unattributed, and nothing in the research recommendation is silently dropped except the value benchmark in PC-006.
* The plan is honest about probabilistic behavior. "Exact regeneration is not guaranteed" matches W30 exactly, and the substitution of immutable inputs, pinned configuration, full run traces, and regression comparison for byte-identical replay is the correct engineering response rather than an overpromise.
* The manifest-last plus eTag-guarded current-pointer protocol is correctly identified as an application invariant rather than a SharePoint guarantee, which matches the research contrarian finding that Graph offers per-item but not cross-file transactions.
* Deferrals are disciplined and each has a named trigger: OCR, production vector backend, GraphRAG, long-context routing, multi-agent orchestration, and distributed queueing are all excluded with the evidence that would reopen them.
* "Exact removals: none" is correct and consistent with an empty repository, and the local-first validation posture in NFR-07 keeps the whole build testable without cloud dependencies, subject to PC-005.
* Residual risk explicitly accepted by the plan and not challenged here: probabilistic output is not exactly reproducible; automatic publication stays disabled until governance approves thresholds; live SharePoint, model, and evaluator behavior is unverifiable until a tenant and deployments exist; and formal RAI, privacy, and security approvals are separate production-governance workstreams. The NFR-04 "documented development profile" is also still undefined, which is acceptable for a first benchmark but should be recorded when the benchmark is written.

## Questions or Blocking Evidence Gaps

* One decision-critical question requires a user answer, from PC-003: is query-time authorization collection-scoped with a recorded source-permission snapshot, or must results be permission-trimmed per user against the originating SharePoint item permissions? The choice changes the connector permission model, the answer-unit schema, and the query path, so it should be settled before P01-T02 freezes the domain contracts.
* No other finding is blocked on missing evidence. PC-001, PC-002, and PC-004 through PC-012 are resolvable from the supplied research and the plan's own baseline without new research.

## Limitations

* Assessment used only the three supplied artifacts. Repository state, tooling availability, and the accuracy of "the repository has no production files" were not independently verified.
* No new research was performed. External claims were accepted as recorded in W1-W32 with their stated retrieval dates and confidence, and no source was refetched or revalidated.
* The PC-004 file-count analysis is an estimate derived from the enumerated Likely Targets and the directory targets they imply. It establishes that the budget is materially wrong, not the exact final count.
* Live behavior of SharePoint delta and version semantics, Azure OpenAI structured output, managed evaluator availability, and MCP SDK subscription support cannot be confirmed from planning artifacts; the plan already routes each to configured live tests or implementation-time checks.

## Recommended Next Action

* Highest-impact finding: PC-001
* Action owner: planning parent
* Smallest next action: Revise the plan directly for PC-001, PC-002, and PC-004 through PC-012 in one pass, folding the release-composition rule into FR-09, FR-12, and P05-T01 first because PC-002, PC-010, and PC-012 all depend on it, and obtain the PC-003 authorization decision from the user before freezing P01-T02 domain contracts. No further critique is required.
* User response required: yes, for PC-003 only

## Related Artifacts

| Artifact | Description |
|---|---|
| [.copilot-tracking/plans/2026-09-09/answer-shaped-knowledge-mcp-plan.md](.copilot-tracking/plans/2026-09-09/answer-shaped-knowledge-mcp-plan.md) | Final-candidate plan under critique |
| [.copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md](.copilot-tracking/details/2026-09-09/answer-shaped-knowledge-mcp-phase-details.md) | Phase and task detail sections for P01 through P07 |
| [.copilot-tracking/research/2026-09-09/answer-shaped-knowledge-mcp-research.md](.copilot-tracking/research/2026-09-09/answer-shaped-knowledge-mcp-research.md) | Supporting research, evidence W1-W32, decisions, and alternatives |
| [.copilot-tracking/reviews/plans/2026-09-09/answer-shaped-knowledge-mcp-plan-critique.md](.copilot-tracking/reviews/plans/2026-09-09/answer-shaped-knowledge-mcp-plan-critique.md) | This critique |

## Next Steps

* Run `/rpi-plan` to apply the PC-001, PC-002, and PC-004 through PC-012 revisions and to put the PC-003 authorization question to the user. This critique is the single final-candidate pass; the planning parent finalizes without another critique.
