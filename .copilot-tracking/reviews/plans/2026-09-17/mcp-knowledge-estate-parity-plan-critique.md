<!-- markdownlint-disable-file -->
# RPI Plan Critique: MCP Knowledge Estate Workflow Parity

## Metadata

* Task ID: MCP-KNOWLEDGE-ESTATE-PARITY-2026-09-17
* Critique date: 2026-09-17
* Plan: .copilot-tracking/plans/2026-09-17/mcp-knowledge-estate-parity-plan.md
* Phase details: .copilot-tracking/details/2026-09-17/mcp-knowledge-estate-parity-phase-details.md
* Critique execution status: Complete

## Inputs and Criterion Boundary

* Task context and caller requirements: Determine what it takes to expose the
  complete findings-led Knowledge Estate workflow through MCP while preserving
  human governance, authorization, source integrity, review acknowledgments,
  and score-free product behavior, within the caller's locked candidate
  boundaries (closed test-ownership set, zero removals, a two-module and
  one-doc-page addition cap, canonical-service authority, no generated
  targets, and specific semantic/regression/validation coverage).
* Research and evidence considered: src/shaper/interfaces/mcp_server.py,
  src/shaper/interfaces/http.py, src/shaper/interfaces/auth.py,
  src/shaper/application/estates.py, src/shaper/application/decisions.py,
  src/shaper/application/artifacts.py, src/shaper/application/evaluation.py,
  tests/test_interfaces.py, tests/test_estate_interfaces.py,
  tests/test_artifacts.py, tests/test_architecture.py,
  tests/evaluation-suggestions.test.mjs,
  prototype/copilot-studio-knowledge-compiler/evaluation-suggestions.mjs,
  docs/planning/brds/shaper-business-requirements.md, and the pinned
  dependency `mcp==1.13.1` in pyproject.toml.
* Decisions, dependencies, and acceptance criteria considered: FR-01 through
  FR-13, NFR-01 through NFR-08, AC-01 through AC-13, the Phase Index (P01
  through P05) and every listed task's Boundaries, Likely Targets,
  Dependencies, and Validation Expectations, and the caller's locked candidate
  boundaries verbatim.
* Assessment boundary: This critique evaluates plan and phase-detail
  credibility against the supplied source code, tests, and BRD. It does not
  execute code, install the pinned `mcp` package, or perform external research
  beyond fetching text already present in the repository; conclusions about
  FastMCP resource byte-return support are therefore based on the plan's own
  stated uncertainty, not independent verification.

## Coverage Assessment

| Requirement, research, phase, or task ID | Coverage | Evidence or concern |
|---|---|---|
| Locked boundary: Test ownership (closed 5-file set) | Partial | P01-T02 phase details (line 181) assign new tests to `tests/test_evaluation_sets.py`, a file outside the enumerated ownership set. |
| Locked boundary: Exact removals: none | Partial | P01-T02 moves browser evaluation-set generation server-side but does not state the disposition of the existing `prototype/copilot-studio-knowledge-compiler/evaluation-suggestions.mjs` module or `tests/evaluation-suggestions.test.mjs`. |
| NFR-03 / AC-04 (idempotency and concurrency) | Partial | `estates.py` and `artifacts.py` have optimistic revision checks for updates/decisions/approvals but no idempotency-key mechanism for `create`, `register`, `discovery.start`, `recommendation.start`, or `transformation.start`; plan does not scope this gap explicitly. |
| NFR-06 (bounded, observable long-running calls) | Partial | Discovery (≤500 docs) and transformation (≤100 docs) run synchronously inside one MCP call; NFR-003's 90-second per-model-request cap makes worst-case duration far exceed typical client/ingress timeouts; mitigation is deferred to a reactive Follow-Up Item rather than a present validation expectation. |
| NFR-08 / AC-11 (original tool and resource compatibility) | Partial | `tests/test_interfaces.py` currently tests only the four original tools; none of the three original resource families (`knowledge://units`, `knowledge://sources`, `knowledge://releases`) have any existing regression test, so "preserving" them is actually a net-new obligation the plan does not explicitly task. |
| FR-11 / NFR-04 (evaluation-set tool, score-free) | Partial | `src/shaper/application/evaluation.py` already implements a different, pre-existing "evaluation" concept (`QualityScores`/`EvaluationEvidence`, advisory quality scoring). The plan's new `evaluation_sets.py` module name is adjacent enough to risk field or scope confusion against the score-free mandate; the plan states the right exclusion but not the disambiguation. |
| P01 domain-model scope (`src/shaper/domain/`) | Partial | "Add request or response models only where shared domain contracts are justified" does not say whether these land in existing domain files or new domain modules; the locked "Maximum additions" boundary only counts application modules, leaving domain-file scope open to drift. |
| P02-T03 FastMCP resource byte capability | Partial | Correctly flagged as an Unresolved Item, but the dependency is pinned exactly (`mcp==1.13.1`), so this is resolvable now rather than deferred to implementation for a requirement (NFR-05/FR-10) with an exact-byte contract. |
| FR-01–FR-10, FR-12, FR-13, most of NFR-01/02/05/07, AC-01/02/05/06/07/08/09/10/12/13 | Covered | Contracts map cleanly to existing `EstateService`, `EstateSourceService`, `DiscoveryService`, `EstateRecommendationService`, `TransformationDecisionService`, and `EstateTransformationService` authorization and revision logic already read in `estates.py`, `decisions.py`, and `artifacts.py`. |

## Verdict

* Verdict: Revise
* Rationale: The plan is directionally sound and well-grounded in the existing
  application-service authorization model, but it contains one direct
  conflict with a locked boundary (a sixth test file outside the closed
  ownership set), one under-scoped governance/cost risk (idempotency-free
  workflow-start operations exposed to MCP retry patterns), and several
  smaller but concrete gaps (resource regression coverage that does not yet
  exist, a resolvable-now FastMCP capability question, and naming/scope
  ambiguity around evaluation-set generation and domain models). These are
  correctable without new user decisions in most cases and do not require
  re-scoping the overall approach.

## Findings

<!-- rpi:critique id=PC-001 -->
### PC-001 [Critical]: New test file breaks the locked closed test-ownership set

* Related IDs: P01-T02, locked boundary "Test ownership"
* Evidence: .copilot-tracking/details/2026-09-17/mcp-knowledge-estate-parity-phase-details.md:181 lists `tests/test_evaluation_sets.py: Add deterministic generation tests.` The caller's locked boundaries state test ownership is closed to exactly `tests/test_interfaces.py`, `tests/test_estate_interfaces.py`, `tests/test_artifacts.py`, `tests/test_shaping.py`, and `tests/test_architecture.py`, with "existing files may be extended" as the only growth mechanism.
* Concern: The phase details name a sixth test file that is not in the locked ownership list and is not created anywhere else in the plan's "Maximum additions" accounting (which only allows two application modules and one documentation page "plus focused tests" inside the owned files).
* Impact: If implemented as written, this is a direct, avoidable violation of a caller-locked boundary, which would force a rework pass during or after implementation and could mask which file is authoritative for evaluation-set regression evidence.
* Smallest useful change: Move the deterministic evaluation-set generation tests into an already-owned file — `tests/test_estate_interfaces.py` (REST behavior preservation, since the shared service backs both REST and MCP) or `tests/test_interfaces.py` (MCP contract and parity coverage) — and delete the `tests/test_evaluation_sets.py` reference from P01-T02.
* Action owner: Planning parent.
* Exact resolving evidence: Revised P01-T02 Likely Targets list only the five locked test files, and no new test file path appears anywhere in the plan or phase details.
* Decision route: Direct planner correction; the locked boundary already permits extending existing owned files, so no user decision is required.

<!-- rpi:critique id=PC-002 -->
### PC-002 [High]: Idempotency claim is unachievable for workflow-start mutations, and MCP retry risk is unscoped

* Related IDs: NFR-03, AC-03, AC-04, FR-03, FR-04, FR-05, FR-07, P03-T01, P03-T02, P03-T03
* Evidence: `src/shaper/application/estates.py` (`EstateService.create`, `EstateSourceService.register`, `DiscoveryService.start`) and `src/shaper/application/artifacts.py` (`EstateTransformationService.start`) each mint a new record or run id (`f"discover-{self._id_factory()}"`, `f"transform-{self._id_factory()}"`, etc.) with no idempotency-key parameter or lookup; only optimistic `expected_revision` checks exist, and only for updates, decisions, and approvals. `grep -n "idempotenc"` across `estates.py`, `artifacts.py`, `decisions.py` finds nothing; the only idempotency key in the codebase is the legacy `knowledge.compile` job path in `http.py`/`mcp_server.py`.
* Concern: NFR-03 states "Mutations preserve optimistic concurrency and idempotency where the underlying workflow supports them" and requires tests for "repeated idempotency keys," but the underlying services do not support idempotency for `create`, `register`, `discovery.start`, `recommendation.start`, or `transformation.start`. The phase details do not say which mutations are exempt, so P05-T01 could satisfy the letter of NFR-03 by testing only the two operations that already have revision checks (decide, approve) while silently leaving the four workflow-start operations without any test proving repeat-call behavior is safe or at least visible.
* Impact: MCP clients (autonomous agents) are more likely than a human browser user to retry a call after a timeout or transport error. A retried `discovery.start`, `recommendation.start`, or `transformation.start` call creates a wholly new run, which for transformation means duplicate LLM spend and duplicate generated artifacts entering the review queue — a governance-relevant and cost-relevant side effect, not just a cosmetic one.
* Smallest useful change: Add an explicit statement to NFR-03 (or a new Non-Goal) that `create`, `register`, and the three `*.start` operations are not idempotent and that repeated calls create additional records/runs by design; require FR-12 tool annotations to mark these `idempotentHint=false`; and add one test per such operation proving a repeated call is visible (creates a second, distinct, auditable run/record) rather than silently colliding or corrupting state.
* Action owner: Planning parent, with product/governance awareness that true idempotency-key support for workflow-start operations is out of the current locked scope.
* Exact resolving evidence: Revised NFR-03 wording distinguishes idempotent-capable operations (decide, approve, update) from non-idempotent workflow-start operations, and P03/P05 phase details add explicit repeat-call test tasks for the latter.
* Decision route: Direct planner correction to scope and test the existing behavior. Adding real idempotency-key deduplication to the workflow-start services would be a divergent, larger change requiring a separate user decision, and is not required to close this finding.

<!-- rpi:critique id=PC-003 -->
### PC-003 [Medium]: Synchronous batch discovery/transformation calls risk exceeding MCP client and ingress timeouts

* Related IDs: NFR-06, FR-04, FR-07, BRD NFR-003, Follow-Up Items
* Evidence: `DiscoveryService.start` in `estates.py` accepts up to 500 documents and executes them inline in one call; `EstateTransformationService.start` in `artifacts.py` accepts up to 100 recommendation ids and executes each with at least one model request (and up to one repair request) inline. `docs/planning/brds/shaper-business-requirements.md` NFR-003 fixes a 90-second request timeout per model call. The plan's NFR-06 defers any bound on this to "a future job split... triggered only if measured client or ingress timeouts require it," and the Follow-Up Items section repeats the same reactive posture.
* Concern: A single MCP `estate.transformation.start` call over a realistic batch (tens of documents) can foreseeably run well past common MCP client and reverse-proxy/ingress default timeouts (commonly 30–120 seconds) even without waiting for a production incident to "measure" it, since the 90-second per-model-request cap is already a known, fixed constant.
* Impact: Without an explicit, tested upper bound or client guidance now, the first production MCP transformation call over a modest batch risks a client-perceived hang or a terminated connection whose underlying run keeps executing server-side, which the plan's own AC-set does not verify.
* Smallest useful change: Add a validation expectation (not just a Follow-Up Item) that documents the worst-case duration for MCP `discovery.start`/`recommendation.start`/`transformation.start` given current batch limits and the 90-second-per-request cap, and either (a) document a recommended smaller MCP-side batch ceiling in `docs/mcp.md`, or (b) add a test proving the run remains resumable/inspectable via `run.get`/`discovery.recover_expired` if the client disconnects mid-call.
* Action owner: Planning parent.
* Exact resolving evidence: P03/P05 phase details include an explicit MCP timeout/duration validation expectation and, if a client-side batch ceiling is chosen, a corresponding test and `docs/mcp.md` note.
* Decision route: Direct planner correction to document and test the already-known constant risk. This is already a partially accepted residual risk per the Follow-Up Items section, so if the planning parent judges the existing reactive posture sufficient, that is an acceptable explicit acceptance rather than a mandatory blocking change.

<!-- rpi:critique id=PC-004 -->
### PC-004 [Medium]: Original MCP resource-family regression coverage does not exist yet and is not explicitly tasked

* Related IDs: AC-11, NFR-08, P01, P05-T01
* Evidence: `tests/test_interfaces.py` (586 lines, fully read) tests the four original tools (`test_given_mcp_server_when_listed_then_only_planned_tools_are_exposed`, `test_given_mcp_server_when_initialized_then_real_sdk_client_lists_tools`) but contains zero references to `resource`, `list_resources`, or `knowledge://` — the three original resource families (`knowledge://units/{unit_id}`, `knowledge://sources/{source_id}`, `knowledge://releases/{release_id}`) in `src/shaper/interfaces/mcp_server.py` have no existing test at all.
* Concern: AC-11 and NFR-08 claim the three original resources "remain compatible" / "retain names and behavior," implying preservation of existing coverage, but no such coverage exists to preserve — it must be created net-new. P05-T01's Likely Targets and Validation Expectations do not call this out separately from the four-tools baseline, so it could be silently skipped if reviewers assume it is a preservation-only task.
* Impact: A real regression in one of the three original resources could ship undetected, undermining the explicit compatibility guarantee the plan and BRD both make for existing MCP clients.
* Smallest useful change: Add an explicit P01 or P05-T01 validation expectation and task line requiring one new SDK-client test per original resource family (`knowledge://units/*`, `knowledge://sources/*`, `knowledge://releases/*`) alongside the new resource tests, clearly distinguished as "first-time regression coverage," not merely "unchanged."
* Action owner: Planning parent.
* Exact resolving evidence: `tests/test_interfaces.py` contains passing SDK-client tests exercising all three original resource URIs by name.
* Decision route: Direct planner correction.

<!-- rpi:critique id=PC-005 -->
### PC-005 [Low-Medium]: Naming collision risk between the existing quality-score evaluator and the proposed evaluation-set generator

* Related IDs: FR-11, NFR-04, P01-T02, P02-T02, BR-002/DD-001
* Evidence: `src/shaper/application/evaluation.py` already exists and implements `QualityScores`/`EvaluationEvidence` — an advisory, model-assisted *quality-score* evaluator for answer units, unrelated to the browser's grounded question-set generation in `prototype/copilot-studio-knowledge-compiler/evaluation-suggestions.mjs`. The plan proposes a new, adjacently named `src/shaper/application/evaluation_sets.py` for the latter, distinct concept.
* Concern: The BRD is emphatic that findings shall replace user-facing scores (BR-002, DD-001, NFR-04), and the plan's own P02-T02 Validation Expectations correctly says "Legacy artifact evaluation scores remain excluded," but neither the plan nor phase details state explicitly that `evaluation_sets.py` must not import, wrap, or expose any field from `evaluation.py`'s `QualityScores`/`EvaluationEvidence` models.
* Impact: Two similarly named modules under the same package increase the chance an implementer conflates them, accidentally surfacing a quality score (or a field derived from one) through the new `estate.evaluation.list` MCP tool, which would violate the product's score-free mandate.
* Smallest useful change: Add one sentence to P01-T02 or P02-T02 stating that `evaluation_sets.py` is unrelated to and must not reference `evaluation.py`'s scoring models, and add a contract-test assertion that the evaluation-set tool's output schema contains no numeric score field.
* Action owner: Planning parent.
* Exact resolving evidence: P01-T02/P02-T02 phase details contain the disambiguation sentence, and a `tests/test_interfaces.py` assertion confirms the evaluation-set tool schema excludes any `score`/`scores` field.
* Decision route: Direct planner correction.

<!-- rpi:critique id=PC-006 -->
### PC-006 [Low]: Domain-model addition scope is unstated and not covered by the locked "Maximum additions" cap

* Related IDs: P01, locked boundary "Maximum additions"
* Evidence: P01 Likely Targets state "src/shaper/domain/: Add request or response models only where shared domain contracts are justified," without naming a target file. The locked boundary "Maximum additions: two production application modules (shared estate views and evaluation sets)... existing files may be extended" caps only application modules, not domain files.
* Concern: Because the domain-file scope is unstated, an implementer could create one or more new domain modules (e.g., a new `domain/estate_views.py` or `domain/evaluation_sets.py`) without technically violating the letter of the locked cap, which only names application modules — but this would exceed the evident spirit of a tightly bounded addition set and could fragment the "domain models remain authoritative" canonical-target boundary across more files than reviewers expect.
* Impact: Ambiguity here risks scope creep in the implementation phase and inconsistent review expectations, though it does not currently contradict any explicit rule.
* Smallest useful change: State explicitly in P01 that any new request/response models are added to the existing `src/shaper/domain/estate.py` (or another explicitly named existing domain file), with no new domain module files.
* Action owner: Planning parent.
* Exact resolving evidence: P01 Likely Targets name a specific existing domain file rather than the `src/shaper/domain/` directory.
* Decision route: Direct planner correction.

<!-- rpi:critique id=PC-007 -->
### PC-007 [Low]: A resolvable FastMCP capability question is deferred despite an exact pinned dependency version

* Related IDs: P02-T03, FR-08, FR-10, NFR-05
* Evidence: `pyproject.toml` pins `mcp==1.13.1` exactly (not a range). P02-T03's Unresolved Items state: "Confirm whether the locked FastMCP resource API accepts raw bytes. If it does not, return base64 with explicit encoding and verify decoded byte equality."
* Concern: This is a reasonable fallback, and correctly flagged as unresolved rather than ignored — but because the exact version is already pinned in the repository, the underlying capability question is answerable now (by inspecting the installed `mcp` package's resource-registration code) rather than left open into implementation for a requirement (byte-exact export, NFR-05) that is central to the plan's credibility.
* Impact: Leaving this open is low risk because a documented fallback (base64) exists, but resolving it now would let P02-T03 and P04-T02 be written with one concrete design instead of two conditional branches, reducing implementation-time rework.
* Smallest useful change: Before implementation begins, inspect the pinned `mcp==1.13.1` FastMCP resource API (or its release notes) and update P02-T03/P04-T02 to state definitively which of the two designs (raw bytes vs. base64-with-hash-check) will be used.
* Action owner: Planning parent.
* Exact resolving evidence: P02-T03's Unresolved Items section is empty or replaced with a confirmed design statement, and the corresponding task's Likely Targets describe one concrete return-type approach.
* Decision route: Direct planner correction; no user decision needed since the fallback design is already specified.

## Strengths and Residual Risk

* The contract-to-service mapping is credible and thoroughly evidenced: every
  new tool traces to an existing, already-role-checked application method
  (`EstateService`, `EstateSourceService`, `DiscoveryService`,
  `EstateRecommendationService`, `TransformationDecisionService`,
  `EstateTransformationService`), confirmed by direct reading of
  `estates.py`, `decisions.py`, and `artifacts.py`.
* The score-free, findings-led, and human-governance constraints are
  consistently reflected in FR-04, FR-09, NFR-04, and the BRD's BR-002/DD-001,
  and the plan correctly keeps purge and raw binary upload out of MCP scope.
* The Follow-Up Items section already explicitly and visibly defers
  asynchronous-job and native-upload scope, which is an accepted residual risk
  rather than a silent gap — PC-003 asks only that the same posture be backed
  by a present validation expectation, not that the deferral itself be
  reversed.
* P01-T02's Unresolved Items handling for the FastMCP resource-byte question
  (PC-007) demonstrates good practice in flagging design uncertainty rather
  than assuming it away; the finding only asks that an already-answerable
  question be resolved earlier given the exact pinned dependency version.

## Questions or Blocking Evidence Gaps

* None. All findings above are correctable directly by the planning parent
  from evidence already in this repository; none require a new, divergent
  product decision to proceed with a revision pass.

## Limitations

* This critique did not execute any code, install the pinned `mcp` package,
  or run the existing test suite; PC-007's conclusion that the FastMCP
  capability question is "resolvable now" is based on the exact-pin evidence
  in `pyproject.toml`, not on having inspected the installed library's source.
* `src/shaper/domain/estate.py` and `docs/architecture.md` were consulted only
  indirectly through the plan/phase-details text and `estates.py`/`artifacts.py`
  imports, not read in full, because they were outside the caller's supplied
  artifact list.

## Related Artifacts

| Artifact | Description |
|---|---|
| [.copilot-tracking/plans/2026-09-17/mcp-knowledge-estate-parity-plan.md](.copilot-tracking/plans/2026-09-17/mcp-knowledge-estate-parity-plan.md) | Candidate plan under critique |
| [.copilot-tracking/details/2026-09-17/mcp-knowledge-estate-parity-phase-details.md](.copilot-tracking/details/2026-09-17/mcp-knowledge-estate-parity-phase-details.md) | Phase details under critique |
| [src/shaper/interfaces/mcp_server.py](src/shaper/interfaces/mcp_server.py) | Current four-tool, three-resource MCP adapter |
| [src/shaper/interfaces/auth.py](src/shaper/interfaces/auth.py) | OIDC/ingress principal resolution reused by MCP |
| [src/shaper/application/estates.py](src/shaper/application/estates.py) | Estate, source, discovery, recommendation services and role checks |
| [src/shaper/application/decisions.py](src/shaper/application/decisions.py) | Proposal decision optimistic-intent enforcement |
| [src/shaper/application/artifacts.py](src/shaper/application/artifacts.py) | Transformation, approval, and content-retrieval services |
| [src/shaper/application/evaluation.py](src/shaper/application/evaluation.py) | Existing quality-score evaluator (naming-collision risk in PC-005) |
| [tests/test_interfaces.py](tests/test_interfaces.py) | Existing MCP/HTTP contract tests; no original-resource coverage today (PC-004) |
| [tests/test_estate_interfaces.py](tests/test_estate_interfaces.py) | REST workflow and authorization regression evidence |
| [tests/test_artifacts.py](tests/test_artifacts.py) | Artifact review, acknowledgment, and byte-equality evidence |
| [tests/evaluation-suggestions.test.mjs](tests/evaluation-suggestions.test.mjs) | Existing JS test for browser-local evaluation-set generation (PC-001/PC-002 disposition gap) |
| [prototype/copilot-studio-knowledge-compiler/evaluation-suggestions.mjs](prototype/copilot-studio-knowledge-compiler/evaluation-suggestions.mjs) | Existing browser-local evaluation-set generator (PC-001/PC-002 disposition gap) |
| [docs/planning/brds/shaper-business-requirements.md](docs/planning/brds/shaper-business-requirements.md) | BRD governance, score-free, and NFR-003 timeout evidence |

## Next Steps

* Highest-impact finding: PC-001 (Critical) — resolve the locked
  test-ownership conflict before implementation starts.
* Action owner: Planning parent (`/rpi-plan`) to revise P01-T02 and any other
  affected phase-detail sections directly; no user decision is required for
  any finding in this critique.
* No user action is required. The planning parent may proceed with a revision
  pass and finalize without a second independent critique, per this critique's
  Pass/Revise/Blocked disposition of Revise with no unresolved Critical-severity
  ambiguity requiring user input.
