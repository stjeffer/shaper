<!-- markdownlint-disable-file -->

# Task Research: knowledge-estate-workflow-redesign

| Field | Value |
|---|---|
| Date | 2026-09-10 |
| Researcher / agent | rpi-research |
| Status | Complete |
| Artifact path | .copilot-tracking/research/2026-09-10/knowledge-estate-workflow-redesign-research.md |

## Research Brief

* What to research: Map the requested Knowledge Estates, per-file Discover scoring, file-level recommendations, approval decisions, and named artifact transformation flow onto the existing Shaper platform.
* Why it matters: The current concept demonstrates an estate-wide sample assessment but does not yet represent the user-owned lifecycle that defines the product.
* Audience or intended use: Product and engineering planning for the next implementation increment.
* Scope: Current domain contracts, application services, HTTP routes, persistence, upload and SharePoint boundaries, hosted concept, tests, and directly related architecture documentation.
* Non-goals: Source changes, implementation, deployment, production connector authorization design, and visual redesign outside the requested workflow.
* Criteria: Every requested stage maps to explicit entities, state transitions, API surfaces, persistence needs, UI screens, approval boundaries, and testable outcomes.
* Requested outputs: Evidence-backed convergence recommendation and planning-readiness determination.
* Output mode: convergence.

## Research Parameters

| Field | Value |
|---|---|
| Research question(s) | What platform changes are required to implement the four-stage knowledge-estate lifecycle safely and coherently? |
| Codebase scope | src/shaper, prototype/copilot-studio-knowledge-compiler, tests, docs/architecture.md, docs/deployment.md |
| External scope | none |
| Initial internal candidate areas | Estate assessment contracts and service; platform orchestration; upload and SharePoint adapters; HTTP composition; hosted concept; persistence |
| Initial external candidate areas | none |
| Research posture | balanced |
| Posture provenance | default for a bounded internal architecture and product-flow change |
| Explicit limits / deadline | none |
| Posture-specific completion basis | Balanced scope coverage and adequate evidence for a planning handoff |
| Edits allowed during research? | no, research-only |
| Resolved evidence root | .copilot-tracking/ |
| Known constraints / excluded sources | Research-only phase; preserve human approval and immutable derived artifacts; no claims that unavailable connectors are live |

## Extension Registry and Provenance

| Kind | Candidate | Match and provenance | Scoped authority or output contract | Selected / skipped reason |
|---|---|---|---|---|
| Instruction | copilot-tracking.instructions.md | Applies to the research evidence path | Tracking path, identity, and evidence conventions | Selected |
| Instruction | markdown.instructions.md and writing-style.instructions.md | Applies to the Markdown research artifact | Markdown structure and writing clarity | Selected, with tracking-file markdownlint exception |
| Skill | rpi-research | Explicit active phase | Three-wave read-only research and planning-readiness handoff | Selected |
| Skill | ux-artifacts | Requested multi-screen product workflow and engineering handoff | UX structure and evidence-labelled handoff assets | Deferred to planning or implementation because this phase is research-only |
| Skill | accessibility | Interactive selection, approval, upload, and status surfaces | WCAG, keyboard, focus, and announcement criteria | Selected as downstream acceptance criteria; no separate planner run required during code research |
| Skill | python-foundational | Python domain and API changes are likely | Python typing and quality conventions | Deferred to implementation |
| Research specialist | none | The repository scope is small and tightly coupled | No independent lane would improve evidence quality | Skipped; research remains inline |

## User Participation and Research Decisions

| Checkpoint | Questions or no-interaction rationale | Answers / unanswered | Resulting decision or selected further research |
|---|---|---|---|
| Intake | The four requested stages, source types, naming example, and approval rule provide sufficient direction. | No intake question needed. | Research the supplied lifecycle as authoritative product direction. |
| Direction change | The caller added token estimates for every transformation after Cycle 1. | No clarification needed; the requirement is precise. | Re-entered research for Cycle 2 and added estimate, budget, and actual-usage contracts. |
| Convergence | Evidence supports one first-class Knowledge Estate workflow rather than extending the aggregate demo in place. | No further question required during research. | Select the durable estate aggregate and per-document workflow with per-transformation token estimates for planning. |

## Scope and Success Criteria

* Scope: Evidence-only analysis of the current implementation against the four requested stages.
* Assumptions: An estate is a durable named aggregate; uploaded ZIP contents become individual source documents; transformation outputs are new artifacts; source documents remain unchanged.
* Success criteria:
  * Every research question is answered or marked with the missing evidence.
  * Findings cite workspace-relative code locations.
  * Alternatives and approval-state risks are compared.
  * Planning readiness and unresolved decisions are explicit.

## Task Research Requests

* Explicit requests: Define named estates from SharePoint sites, ZIP files, individual uploads, and URLs; discover and score each file; select files for detailed recommendations with token estimates for every transformation; approve or decline per document; transform only approved documents; apply estate-level output naming.
* Inferred research questions: What durable aggregate and source model is needed? Which current APIs and stores can be reused? Where must estate-wide assessment be decomposed to document-level results? How should estimates, budgets, and actual token use be represented? What approval and publication state machine prevents accidental transformation? What UI information architecture best fits the flow?
* Caller constraints and non-goals: Preserve exact lifecycle intent; do not retain mock connection or completion claims.

## Direction Controls

| Control type | Direction or boundary | Source / checkpoint | Effect on active brief, evidence, or revalidation |
|---|---|---|---|
| change | Knowledge Estates becomes a real definition and source-management screen. | User request, 2026-09-10 | Replaces the current navigation placeholder and sample-source framing. |
| add | Discover reports readiness and reshaping effort for every individual source file. | User request, 2026-09-10 | Requires document-level analysis and selection contracts. |
| add | Every proposed transformation reports an estimated token range before approval. | User request, 2026-09-10 | Requires deterministic estimate, budget, and actual-usage contracts. |
| change | Recommend is initiated for user-selected files and produces per-file detailed reports. | User request, 2026-09-10 | Requires selection-scoped recommendation generation rather than aggregate proposals alone. |
| narrow | Transform only approved documents and create new artifacts using an estate-level naming convention. | User request, 2026-09-10 | Requires durable per-document decisions and immutable output identity. |
| exclude | Do not imply a connector or source is active without live evidence. | Prior user correction, 2026-09-10 | UI and APIs must expose truthful source lifecycle states. |

## Research Questions

| # | Sub-question | Type | Priority | Status |
|---:|---|---|---|---|
| Q1 | What durable Knowledge Estate aggregate, source types, and naming policy are required? | depth | H | answered |
| Q2 | How does current assessment logic need to change for per-file readiness and effort scoring? | depth | H | answered |
| Q3 | What selection-scoped recommendation and per-file report contracts are needed? | depth | H | answered |
| Q4 | What approval and transformation state machine guarantees that only approved files produce new named artifacts? | depth | H | answered |
| Q5 | Which current implementation components are reusable, missing, or misleading for this workflow? | breadth | H | answered |
| Q6 | What credible alternative workflow should be rejected or retained? | straightforward | M | answered |
| Q7 | How should token estimates, enforceable budgets, and actual usage be represented for each transformation? | depth | H | answered |

## Prior Knowledge Gate

* Existing artifacts reviewed: Current domain, application, interface, infrastructure, UI, architecture, deployment, and live-source evidence.
* Reused (verified) findings: Shaper is a platform; immutable source versions, human review decisions, optimistic concurrency, SharePoint delta enumeration, safe parsing, and immutable release assembly are reusable foundations.
* Superseded / stale: The current aggregate-only concept, single-source collection shape, post-transformation-only review flow, and fixed sample are insufficient as the primary product workflow.

## Research Cycle Log

### Cycle 1

* Active direction controls: All controls above.
* Active research posture and completion basis: balanced; scope coverage and adequate evidence.
* Explicit limits or deadline effect: none.

#### Wave 1: Wider

* Plan and independent lanes: Inventory current domain, application, API, persistence, connector, UI, and test capabilities against Q1-Q6.
* Worker evidence relationships or inline fallback: Inline because the code paths are tightly coupled and small enough to inspect directly.
* Reflection: The codebase contains useful low-level source, parsing, assessment, review, and publication primitives, but no persisted Knowledge Estate aggregate or estate lifecycle. The current `Collection` owns exactly one source and one output, while the UI's Knowledge Estates navigation is a placeholder. C1-C7, C12-C16.

#### Wave 2: Deeper

* Parent-prioritized material from Wave 1: Estate identity and multiplicity, per-document scoring, selection-scoped reports, decision timing, output naming, and persistence.
* Plan and independent lanes: Trace assessment granularity, source ingestion identity, approval transitions, publication naming, and UI navigation behavior.
* Worker evidence relationships or inline fallback: Inline trace from source references through compilation, review, and release assembly.
* Reflection: Existing scoring helpers operate on individual profiles but are averaged into three estate dimensions. Findings retain document IDs, which provides a migration path to per-document reports. Existing review decisions are version-pinned and optimistic, but they occur only after shaping has already created a candidate. Release output is one `units.jsonl`, not per-document HTML with an estate naming rule. C3-C4, C8-C11, C17-C19.

#### Wave 3: Contrarian

* In-scope challenge targets and boundaries: Challenge whether one aggregate workflow, immediate ZIP expansion, and per-file approval are the safest boundaries.
* Plan and independent lanes: Compare aggregate batch recommendations, lazy source expansion, and overwrite-oriented transformation against the requested model.
* Worker evidence relationships or inline fallback: Inline comparison against current authorization, archive, publication, and review contracts.
* Reflection: Reusing `Collection` as the estate would preserve authorization compatibility but retain its one-source invariant and confuse an authorization boundary with a user-managed aggregate. Approving only generated candidates would violate the requirement that only approved documents are transformed. Arbitrary URL fetching would introduce an SSRF boundary; URLs should initially resolve through registered connectors, starting with SharePoint. ZIP expansion must be bounded and produce individually scanned document records rather than treating the archive as one document. C1, C5-C10, C17.

#### Parent Synthesis and Disposition

| Material / claim | Evidence IDs or worker pointers | Parent disposition | Evidence-based rationale | Primary-artifact treatment |
|---|---|---|---|---|
| First-class `KnowledgeEstate` aggregate with many child sources | C1, C5, C6, C12-C16 | accepted | The current collection and demo cannot model named, editable, many-source estates. | Selected recommendation |
| Per-document readiness plus estate-level relational findings | C3, C4, C17, C18 | accepted | Existing helper scores and evidence IDs can be decomposed without losing duplicate, contradiction, or topic analysis. | Finding and plan boundary |
| Pre-transformation document decisions | C8-C10, C18 | accepted | Current review protects publication but occurs after transformation; a separate authorization gate is required before work begins. | Safety invariant |
| Estate naming template producing per-document HTML | C11, C19 | accepted | Current release output has no caller-visible filenames; a validated naming contract and artifact record are required. | Output contract |
| Arbitrary URL retrieval in the first increment | C5-C7 | rejected | The existing safe connector resolves SharePoint HTTPS locations; unconstrained web fetching adds an unplanned SSRF and content-trust boundary. | Deferred risk |
| Preserve post-output review as a second optional or policy-driven gate | C9-C11 | accepted | Pre-transform approval does not prove generated output quality; current immutable review evidence remains useful before publication. | Two-gate workflow |

#### Cycle Re-entry Evaluation

* Another complete three-wave cycle needed: no.
* Trigger or stop basis: All questions are answered with code evidence; remaining decisions are planning-level contract details rather than missing research.
* Revised brief or revalidation required: none.
* Readiness effect: Ready.

### Cycle 2

#### Wave 1: Wider

* Plan and independent lanes: Inventory token budgets, provider usage accounting, run records, and regression metrics after the caller added per-transformation token estimates.
* Worker evidence relationships or inline fallback: Inline because the token lifecycle spans four small, directly connected modules.
* Reflection: Shaper accepts a caller-supplied job budget, enforces a hard shaping token cap, and receives actual provider input and output token counts. It does not calculate a pre-run estimate. C20-C22.

#### Wave 2: Deeper

* Parent-prioritized material from Wave 1: Estimate identity, source-version pinning, input/output split, uncertainty, budget enforcement, and actual-versus-estimated reconciliation.
* Plan and independent lanes: Trace whether token accounting is persisted and whether historical token evidence can calibrate estimates.
* Worker evidence relationships or inline fallback: Inline trace from the model gateway through the shaping outcome, compiler, and regression summaries.
* Reflection: The shaping outcome returns combined actual tokens, but the compiler discards that accounting. An `AgentRun` contract contains input tokens, output tokens, and estimated cost but is not instantiated in the current workflow. Regression summaries already compare mean token use, providing a future calibration signal. C21-C24.

#### Wave 3: Contrarian

* In-scope challenge targets and boundaries: Challenge a single exact token number, model-generated self-estimates, and using an estimate without a hard budget.
* Plan and independent lanes: Compare point estimates, bounded ranges, maximum budgets, and historical calibration.
* Worker evidence relationships or inline fallback: Inline comparison against the existing provider and budget contracts.
* Reflection: A single exact number would imply unsupported precision because repairs and tool calls vary. Letting the model estimate its own future use is circular. The estimate should be deterministic, versioned, source-version pinned, presented as an expected range plus enforced maximum, then reconciled with provider-reported actual input and output usage. C20-C25.

#### Parent Synthesis

| Material | Evidence | Disposition | Rationale | Decision impact |
|---|---|---|---|---|
| Per-transformation `TokenEstimate` | C20-C25 | accepted | Users need resource visibility before approval, while the runtime needs an enforceable ceiling. | Required recommendation field |
| Exact single-number prediction | C21-C25 | rejected | Repair loops, tool calls, output size, and tokenizer availability make exact prediction misleading. | Use expected range and cap |
| Provider-reported actual usage | C21-C24 | accepted | Actual input/output counts are available but currently discarded. | Persist and reconcile after execution |
| Model-authored token estimate | C21-C22 | rejected | It adds token cost and cannot enforce its own future consumption. | Use a deterministic estimator |

* Another complete three-wave cycle needed: no.
* Trigger or stop basis: The added requirement is answered across proposal, execution, and reconciliation stages.
* Revised brief or revalidation required: The selected workflow now includes token estimates on every proposed transformation.
* Readiness effect: Remains Ready.

## Evidence Log

* Delegation: inline; tightly coupled internal code research does not justify a separate worker.

### Codebase Evidence

| ID | Claim / finding | Location (`path:line`) | Tool | Confidence | Notes |
|---|---|---|---|---|---|
| C1 | `Collection` is an authorization boundary with exactly one `SourceRef` and one `OutputRef`; it cannot represent a named estate with many independently managed sources. | src/shaper/domain/models.py:114 | read | high | `Collection.validate_boundary` also couples source and collection identity. |
| C2 | The HTTP assessment contract accepts caller-built profile dictionaries and has no Knowledge Estate CRUD or source-management resource. | src/shaper/interfaces/http.py:79 | read and grep | high | Existing endpoints are capability-oriented rather than estate-oriented. |
| C3 | `EstateAssessmentService` computes three aggregate dimensions by averaging profile-level helper scores and returns one overall assessment. | src/shaper/application/assessment.py:51 | read | high | Document-level results are not preserved as first-class records. |
| C4 | Current scoring covers headings, sentence length, metadata, freshness, procedures, FAQs, and paragraph chunking, but it has no cross-policy-reference detector or reshaping-effort model. | src/shaper/application/assessment.py:280 | read and grep | Existing helpers are reusable inputs to a richer document report. |
| C5 | `SharePointSource` already resolves one HTTPS SharePoint library and enumerates individual files through Graph delta with stable IDs and source versions. | src/shaper/infrastructure/sharepoint.py:36 | read | Reusable connector primitive, not yet composed into a hosted estate workflow. |
| C6 | The upload route stages one file at a time, and the upload store rejects extensions outside its allow-list; general ZIP estate uploads are not implemented. | src/shaper/interfaces/http.py:258 | read | DOCX package ZIP validation is not bulk archive ingestion. |
| C7 | The parser safely supports PDF, DOCX, Markdown, and plain text as individual source documents. | src/shaper/infrastructure/parsers.py:21 | read | Reusable after source enumeration or archive expansion. |
| C8 | Hosted compilation processes exactly one staged upload and explicitly reports hosted SharePoint compilation and publication as unconfigured. | src/shaper/application/compiler.py:114 | read | Current kernel is document-scoped but not estate-orchestrated. |
| C9 | The current compilation flow shapes content and creates a review candidate before the human approval method is called. | src/shaper/application/compiler.py:147 | read | This protects publication, not the requested pre-transformation consent boundary. |
| C10 | Review decisions are immutable, version-targeted, role-authorized, and optimistic-concurrency protected. | src/shaper/application/review.py:132 | read | Reusable pattern for recommendation decisions and stale-source protection. |
| C11 | Release assembly publishes approved units into one `units.jsonl` artifact and does not create per-document named HTML assets. | src/shaper/application/publication.py:56 | read | A new knowledge-artifact manifest and renderer are required. |
| C12 | SQLite persistence stores jobs, generic records, checkpoints, and outbox entries, but defines no estate, source, document, discovery, recommendation, decision, or artifact repository. | src/shaper/infrastructure/sqlite.py:15 | read | Generic records can support a dev adapter, but first-class repositories are still needed. |
| C13 | The deployed development profile stores SQLite on local container storage, so workflow state does not survive replica replacement. | docs/deployment.md:23 | read | User-created estates require durable managed state before the workflow can be considered persistent. |
| C14 | Knowledge Estates is currently a dead navigation link, while Discover renders the fixed sample inside one four-phase page. | prototype/copilot-studio-knowledge-compiler/index.html:33 | read and grep | The information architecture must become route or screen based. |
| C15 | The README explicitly describes current platform analysis as synchronous, stateless, and profile-input based. | README.md:99 | read | Confirms the requested lifecycle is new platform work, not UI wiring. |
| C16 | The public demo constructs three fixed profiles at process startup and returns them with a fixed analysis. | src/shaper/application/demo.py:38 | read | Useful demo fixture only; not a user-defined estate. |
| C17 | `SourceDocument` already provides immutable source version, content hash, permission snapshot, and observed time. | src/shaper/domain/models.py:196 | read | These fields should pin discovery, recommendation, approval, and transformation inputs. |
| C18 | Existing intervention recommendations carry document IDs, supported modes, and an approval-required invariant. | src/shaper/domain/assessment.py:199 | read | Reusable semantics, but the current grouping is not a per-document detailed report. |
| C19 | `OutputRef` already rejects absolute paths, traversal, and backslashes. | src/shaper/domain/models.py:123 | read | Reusable validation principle for estate naming templates and artifact paths. |
| C20 | `CompileJob` stores a positive `requested_token_budget`, but the value is supplied by the caller rather than estimated by Shaper. | src/shaper/domain/models.py:400 | read | Current budget is a cap, not a forecast. |
| C21 | `ShapingLoop` enforces maximum token use and returns observed token use with model and tool call counts. | src/shaper/application/shaping.py:59 | read | Provides reusable enforcement and runtime accounting. |
| C22 | The Azure OpenAI gateway returns provider-reported prompt and completion token counts separately. | src/shaper/application/model.py:112 | read | Persist these as actual usage per transformation. |
| C23 | `AgentRun` defines input tokens, output tokens, and estimated cost, but current compilation does not construct or persist it and discards shaping usage. | src/shaper/domain/models.py:358 | read and grep | Accounting exists as an unused contract. |
| C24 | Regression summaries aggregate model tokens and reject increases over a baseline tolerance. | src/shaper/application/regression.py:285 | read | Historical actuals can calibrate estimates by transformation type and model. |
| C25 | The dependency manifest includes the OpenAI client but no explicit tokenizer package. | pyproject.toml:15 | read and grep | Planning must choose a model-compatible tokenizer or clearly label approximation. |

### External Evidence

No external evidence used.

### Contradictions / Conflicts

* The current documentation calls the analysis proposal-only, but the only executable compiler generates a candidate before approval. Resolve by distinguishing pre-transformation authorization from post-generation publication review. C9-C10.

## Findings Mapped to Questions and Evidence

| Question | Finding | Evidence IDs | Confidence | Decision or readiness implication |
|---|---|---|---|---|
| Q1 | Introduce a durable named `KnowledgeEstate` with many `EstateSource` children and a validated `ArtifactNamingPolicy`, rather than widening `Collection`. | C1, C5-C7, C12-C16, C19 | high | Plan new aggregate, repositories, and CRUD APIs while retaining collection-scoped authorization. |
| Q2 | Add immutable `DocumentReadinessReport` records per source version; retain a separate estate summary for relational findings such as duplication and contradictions. | C3-C4, C17 | high | Decompose current helper scoring and add long-paragraph, cross-reference, and effort evidence. |
| Q3 | Create a version-pinned `RecommendationRun` for selected document IDs with one detailed proposed-change report per document. | C2, C17-C18 | high | Selection and report generation become server-side workflow resources. |
| Q4 | Add pre-transform approve or decline decisions, enforce them in job creation, recheck source versions, and retain post-output review before publication. | C8-C11, C17-C19 | high | Two explicit gates prevent unauthorized work and unreviewed publication. |
| Q5 | Reuse SharePoint enumeration, parsers, immutable source identity, optimistic review, and release integrity; replace the demo-only UI and add durable estate workflow storage. | C5-C17 | high | Implementation can build on existing primitives but is a multi-layer increment. |
| Q6 | Reject aggregate-only, post-transform-only approval, unconstrained URL fetch, and source overwrite approaches. | C1, C5-C11, C14-C18 | high | The selected workflow is more work but matches safety and product intent. |
| Q7 | Attach a deterministic, versioned token estimate to each transformation proposal, expose an expected range and enforceable cap before approval, then persist actual input/output tokens and variance after execution. | C20-C25 | high | Token visibility becomes part of recommendation, authorization, quota, and run evidence. |

## Key Discoveries

* The Knowledge Estate is not the same thing as the current collection contract. It is a user-managed aggregate inside the collection authorization boundary. C1.
* Readiness must be dual-level: per-document scores and effort for selection, plus estate-level relational analysis for duplication, contradiction, topic, and authority. C3-C4.
* Approval timing must change. A document-level recommendation decision authorizes transformation; generated artifacts can then retain the existing review-before-publication control. C9-C10.
* ZIP upload requires safe bounded expansion, path normalization, supported-entry filtering, per-entry malware scanning, and individual source records. C6-C7.
* Artifact naming must be validated and collision-safe. The recommended default is `shaper_{source_stem}.html`, with the template stored on the estate and the resolved name stored on each artifact. C11, C19.
* Each proposed transformation needs an immutable `TokenEstimate`: source version, transformation kind, model deployment, estimator version, estimated input and output ranges, expected total, enforced maximum, assumptions, and confidence. Actual usage must be stored separately and must never overwrite the estimate. C20-C25.

## Alternatives and Decision State

### Selected Recommendation

* Approach: Build a persistent Knowledge Estate workflow with many registered sources, versioned documents, per-document discovery reports, selection-scoped recommendation runs with token estimates, pre-transform decisions, and immutable named HTML artifacts.
* Rationale: This is the only approach that satisfies all four requested stages while reusing existing source-version, connector, scoring, review, authorization, and publication primitives.
* Evidence refs: C1-C25.
* Implementation impact: New estate domain module and repositories; source registration and archive ingestion; document-level assessment and effort model; recommendation, token-estimation, and decision services; transformation authorization; actual-usage accounting; HTML artifact renderer and naming policy; estate REST resources; multi-screen UI; persistence and deployment updates.
* Confidence: high for the architecture boundary; medium for final naming-template grammar and generic URL scope, which planning can safely constrain.

### Alternative: Preserve the current aggregate-only four-phase experience

* Approach: Keep one estate-wide score and aggregate recommendations.
* Trade-offs: Lower implementation cost and maximum reuse of the current API.
* Evidence refs: C2-C4, C14-C16.
* Rejection rationale: It cannot support document selection, effort estimates, per-file reports, or per-document decisions.

### Alternative: Reuse current candidate review as the only approval

* Approach: Transform selected files immediately, then let users approve or reject generated candidates.
* Trade-offs: Reuses current compilation and review with fewer new states.
* Evidence refs: C8-C10.
* Rejection rationale: It transforms declined documents before the user has authorized transformation.

### Alternative: Treat ZIP and SharePoint inputs as single opaque sources

* Approach: Score and transform an archive or site as one item.
* Trade-offs: Simpler ingestion and fewer records.
* Evidence refs: C5-C7, C17.
* Rejection rationale: It breaks the user's individual-file scoring, selection, recommendation, and approval model.

### Alternative: Allow arbitrary URLs at estate creation

* Approach: Fetch any HTTPS URL supplied by a user.
* Trade-offs: Broad source support with a simple-looking UI.
* Evidence refs: C5-C7.
* Rejection rationale: The current platform has a SharePoint-specific resolver, not a safe general web connector; unrestricted fetching creates SSRF, authentication, crawl-scope, and provenance risks.

### Alternative: Show one exact token estimate

* Approach: Display one predicted total for each transformation.
* Trade-offs: Simple to scan and aggregate.
* Evidence refs: C20-C25.
* Rejection rationale: It hides uncertainty from repair loops, tools, schema overhead, and output variation. Display an expected range and a separately enforced maximum instead.

## Open Questions, Risks, and Residual Uncertainty

* Blocking: None for planning.
* Important: Interpret "add URLs" as registered connector URLs in the first increment, starting with SharePoint site or library URLs. Generic web URLs require a separate connector and threat model.
* Follow-up: Plan archive limits, connector credentials, durable Azure state, artifact collision handling, and the second publication-review gate.
* Residual uncertainty: The user supplied one naming example but not a full template grammar. Planning can use a restricted `{source_stem}` token and default `shaper_{source_stem}.html` without blocking progress.
* Residual uncertainty: Token ranges require a model-compatible tokenizer and initial multipliers before historical calibration exists. Label estimate confidence and estimator version rather than presenting false precision.

## Current Decisions

| Decision | Status | Owner / source | Rationale | Evidence IDs | Implications |
|---|---|---|---|---|---|
| Knowledge Estates is a durable named aggregate within the collection authorization boundary. | confirmed | user and evidence | Explicit requested workflow; current collection cannot represent many sources. | C1-C2, C12-C16 | Requires first-class domain, API, persistence, and UI support. |
| Discovery produces per-document readiness and effort while retaining estate-level relational findings. | confirmed | user and evidence | Individual selection requires document-level reports; duplicates and contradictions remain relational. | C3-C4, C17-C18 | Requires dual-level assessment contracts. |
| Only approved documents transform into new artifacts. | confirmed | user | Explicit safety rule; current approval occurs too late. | C8-C10 | Approval must be durable, version-pinned, and enforced before job creation. |
| Outputs are new immutable HTML artifacts named from an estate-level policy. | proposed | user and evidence | Matches the example and existing immutable release posture. | C11, C19 | Default to `shaper_{source_stem}.html`; never overwrite source documents. |
| First-increment URLs are registered connector URLs, initially SharePoint. | proposed | evidence constraint | Current safe URL resolver is SharePoint-specific. | C5-C7 | Generic web URLs remain a separate connector task. |
| Every transformation proposal includes an immutable token estimate, and every completed transformation records actual usage. | confirmed | user and evidence | Explicit caller requirement; current runtime already exposes budget and usage primitives. | C20-C25 | Approval UI shows range and cap; execution enforces the cap and stores variance. |

## Unresolved Decisions

| Decision | Smallest evidence or answer needed | Owner | Impact | Blocker status |
|---|---|---|---|---|
| Exact generic URL connector scope | A future user decision plus SSRF and crawl-boundary design. | downstream planning | Source creation beyond SharePoint | follow-up |
| Naming collision behavior | Choose deterministic disambiguation, recommended source-ID suffix on collision. | downstream planning | Stable artifact paths | important |
| Whether post-output review is mandatory for every artifact | Apply current risk policy or require universal review for the first increment. | downstream planning | Publication timing | important |

## Potential Next Research

| Priority | Research item | Expected value | Trigger | Selected? | Related questions / evidence |
|---|---|---|---|---|---|
| M | General authenticated web connector threat model | Safely expand beyond SharePoint URLs | User requests generic web URLs | deferred | Q1, Q6; C5-C7 |
| M | Calibrated effort model | Replace heuristic effort bands with measured delivery effort | Representative completed transformations exist | deferred | Q2; C3-C4 |
| M | Calibrated token estimator | Replace initial assumptions with per-model, per-transformation historical distributions | Sufficient actual transformation runs exist | deferred | Q7; C22-C25 |

## Planning Readiness

* Status: Ready.
* Decision state: Convergence recommendation selected.
* Evidence basis: C1-C25.
* Preconditions met: Lifecycle, aggregate boundary, source types, per-document analysis, recommendation scope, token estimation and accounting, approval timing, artifact behavior, reusable primitives, gaps, and alternatives are defined.
* Blockers: None for planning.
* Smallest action to change readiness: None.

## Closeout Record

| Field | Record |
|---|---|
| Research execution status | Complete |
| Completed waves | Cycles 1 and 2 Wider, Deeper, and Contrarian |
| Lane evidence or inline fallback | Inline fallback selected |
| Research disposition | executed |
| Planning Readiness | Ready, supported by C1-C25 |
| Blockers | none |
| Continuation owner and state | manual RPI Agent, active Research |

## Advisory Next Step

| Field | Record |
|---|---|
| Research disposition | executed |
| Planning Readiness | Ready, supported by C1-C25 |
| Output mode and planning support | convergence; yes when evidence gates pass |
| Acting owner | manual RPI Agent |
| Required gates or confirmations | Research gates passed; manual phase advancement remains pending |
| Continuation result | advisory `/rpi-plan` |
| Primary evidence file | .copilot-tracking/research/2026-09-10/knowledge-estate-workflow-redesign-research.md |
| Notes for planning or re-entry | Plan the new aggregate and APIs before replacing the demo UI. Preserve collection authorization, source-version pinning, per-transformation token estimates and actual usage, pre-transform decisions, and immutable output review. |

* Advisory only: rpi-research does not invoke a follow-on skill.
* Completion or limit-blocked basis: All scoped questions are answered, alternatives were tested, and another cycle would be redundant.

## Sources

No external sources used.

## Artifact Self-Check

* [x] Every research question is answered.
* [x] Wider, Deeper, and Contrarian waves are complete.
* [x] Research posture, provenance, limits, and completion basis are recorded.
* [x] Every codebase finding carries a stable evidence ID and location.
* [x] Findings, alternatives, decisions, and readiness cite evidence.
* [x] Extension registry records applicable instructions and skills.
* [x] User participation and direction controls are recorded.
* [x] Parent synthesis and re-entry evaluation are complete.
* [x] Planning readiness and advisory next step are final.
* [x] External content is treated as data and no secrets are recorded.
* Checked sections: All required research sections.
* Missing or limited sections: No external evidence was needed; generic URL scope, naming collision behavior, and initial token-calibration factors remain planning decisions.
