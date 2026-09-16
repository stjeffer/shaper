<!-- markdownlint-disable-file -->

# Task Research: evaluation-question-count

| Field | Value |
|-------|-------|
| Date | 2026-09-15 |
| Researcher / agent | rpi-research |
| Status | Complete |
| Artifact path | .copilot-tracking/research/2026-09-15/evaluation-question-count-research.md |

## Research Brief

* What to research: Where the evaluation common-question count is generated,
  bounded, persisted, displayed, and tested, and what must change to raise it from
  five to 20.
* Why it matters: Five questions do not exercise enough of an estate's knowledge
  to provide useful evaluation coverage.
* Audience or intended use: Shaper maintainers implementing and validating the
  evaluation-generation change.
* Scope: Evaluation prompt, runtime schema and orchestration, token budgeting,
  API/UI presentation, tests, and directly related documentation.
* Non-goals: Changing assessment findings, transformation behavior, or evaluation
  grading semantics.
* Criteria: The runtime requests 20 distinct common questions when knowledge can
  support them, degrades honestly for smaller knowledge sets, and preserves
  grounding and schema validation.
* Requested outputs: One implementation recommendation with affected surfaces and
  validation needs.
* Output mode: convergence

## Research Parameters

| Field | Value |
|-------|-------|
| Research questions | Which surfaces enforce five questions, and how should a target of 20 behave for limited knowledge? |
| Codebase scope | Current Shaper checkout, evaluation-related source, prompt, tests, UI, and docs |
| External scope | None |
| Initial internal candidate areas | src/shaper/prompts, application evaluation services, domain models, API/UI, tests |
| Initial external candidate areas | None |
| Research posture | focused |
| Posture provenance | Default for a bounded internal change with a supplied target |
| Explicit limits / deadline | User requested approximately 20 questions |
| Posture-specific completion basis | Focused scope and materiality |
| Edits allowed during research? | no, research-only |
| Resolved evidence root | .copilot-tracking/research |
| Known constraints / excluded sources | Code-only research; user-staged assets remain untouched |

## Extension Registry and Provenance

| Kind | Candidate | Match and provenance | Scoped authority or output contract | Selected / skipped reason |
|------|-----------|----------------------|-------------------------------------|---------------------------|
| Instruction | copilot-tracking.instructions.md | Applies to research evidence path | Tracking path and evidence conventions | Selected |
| Instruction | markdown.instructions.md and writing-style.instructions.md | Applies to Markdown artifacts | Markdown structure and prose conventions | Selected |
| Skill | hve-builder | Evaluation prompt is behavior-bearing | Prompt lifecycle, static review, and behavior gate | Selected by parent |
| Skill | rpi-research | HVE Builder codebase exploration bridge | Read-only three-wave evidence artifact | Selected |
| Research specialist | None | Bounded, low-volume continuous code path | No independent lane needed | Skipped |

## User Participation and Research Decisions

| Checkpoint | Questions or no-interaction rationale | Answers / unanswered | Resulting decision or selected further research |
|------------|---------------------------------------|----------------------|--------------------------------------------------|
| Intake | The user supplied the current and desired count; no question would materially change research. | Target is approximately 20. | Research 20 as the default target and verify limited-knowledge behavior. |
| Direction change | Evidence showed the cap is client-side and per document. | No user interaction needed. | Prefer an estate-wide balanced target to avoid unbounded growth. |
| Convergence | Code evidence resolves the design choice. | No unanswered question. | Select up to 20 distinct, source-grounded questions per estate. |

## Scope and Success Criteria

* Scope: Trace the complete common-question generation path and identify all
  aligned changes required for a default target of 20.
* Assumptions: The current count of five may be encoded in more than one runtime,
  prompt, schema, or UI surface.
* Success criteria:
  * Every question is answered or marked with the smallest missing evidence.
  * Every finding cites a stable code evidence ID and workspace-relative location.
  * Alternatives and limited-knowledge behavior are compared.
  * Planning readiness and residual risks are explicit.

## Task Research Requests

* Explicit request: Generate a high number of common evaluation questions; five
  is insufficient and approximately 20 are needed.
* Inferred questions: Whether 20 should be exact or a maximum, and whether question
  diversity, grounding, deduplication, and budgets need adjustment.
* Caller constraints and non-goals: Preserve current evaluation semantics outside
  question coverage.

## Direction Controls

| Control type | Direction or boundary | Source / checkpoint | Effect on active brief, evidence, or revalidation |
|--------------|-----------------------|---------------------|---------------------------------------------------|
| Change | Raise common evaluation questions from five to approximately 20. | User | Trace and align every enforcing surface. |
| Narrow | Do not alter assessment or shaping behavior. | Research brief | Keep investigation on evaluation generation. |

## Research Questions

| # | Sub-question | Type | Priority | Status |
|---:|--------------|------|----------|--------|
| Q1 | Where is the current count of five enforced? | Straightforward | H | Answered |
| Q2 | What output and persistence contracts constrain a count of 20? | Depth | H | Answered |
| Q3 | How should limited knowledge and duplicate questions be handled? | Depth | H | Answered |
| Q4 | What tests, UI, docs, and budgets must change? | Breadth | H | Answered |

## Prior Knowledge Gate

* Existing artifacts reviewed: Prior session context established separate
  evaluation and shaping prompts, but did not identify the question count.
* Reused findings: Evaluation has an externalized system prompt and structured
  output, subject to HVE Builder lifecycle checks.
* Superseded / stale: None.

## Research Cycle Log

### Cycle 1

* Active direction controls: Raise coverage to approximately 20 without changing
  assessment or shaping.
* Active research posture and completion basis: Focused; the bounded client-side
  generation path and its direct consumers are covered.
* Explicit limits or deadline effect: The user supplied 20 as the desired scale.

#### Wave 1: Wider

* Plan and independent lanes: Search prompt, backend, domain, frontend, test, and
  documentation surfaces for question generation and the number five.
* Worker evidence relationships or inline fallback: Inline because the path is
  small and continuous.
* Reflection: The evaluation prompt's five refers to rubric criteria, not common
  questions. The actual question cap is in browser code.

#### Wave 2: Deeper

* Parent-prioritized material from Wave 1: Passage extraction, question wording,
  per-document accumulation, selection state, exports, and test coverage.
* Plan and independent lanes: Trace the pure browser functions through loading,
  rendering, selection, and dataset export.
* Worker evidence relationships or inline fallback: C1-C6.
* Reflection: Raising only the slice would bias early source passages and permit
  20 questions per document with no estate-level bound.

#### Wave 3: Contrarian

* In-scope challenge targets and boundaries: Exact 20 per document, exact 20 even
  for sparse sources, model-backed generation, and a simple first-20 slice.
* Plan and independent lanes: Test each alternative against grounding, diversity,
  predictable list size, and implementation scope.
* Worker evidence relationships or inline fallback: C1-C6.
* Reflection: An exact count would require duplicate or unsupported questions for
  sparse knowledge. A model-backed path adds cost and a new service contract
  without being necessary to raise deterministic draft coverage.

#### Parent Synthesis and Disposition

| Material / claim | Evidence IDs | Parent disposition | Evidence-based rationale | Treatment |
|------------------|--------------|--------------------|--------------------------|-----------|
| Use an estate-wide target of 20 | C1, C2, C4 | Accepted | It raises one-document coverage while bounding multi-document estates. | Recommendation |
| Return fewer than 20 for sparse knowledge | C3 | Accepted | Grounding is more important than filling a quota. | Requirement |
| Select the first 20 passages | C3 | Rejected | It overrepresents early sections. | Alternative |
| Change the AI evaluation prompt | C1, C5 | Rejected | That prompt scores answer units and does not generate draft questions. | Non-goal |

#### Cycle Re-entry Evaluation

* Another complete three-wave cycle needed: No.
* Trigger or stop basis: All questions are answered by direct code evidence; the
  next likely searches are redundant.
* Revised brief or revalidation required: None.
* Readiness effect: Ready.

## Evidence Log

* Delegation: Inline; the relevant path is low-volume and continuous.

### Codebase Evidence

| ID | Claim / finding | Location | Tool | Confidence | Notes |
|----|-----------------|----------|------|------------|-------|
| C1 | Draft generation truncates each document to five passages. | prototype/copilot-studio-knowledge-compiler/app.js:309 | Read | High | `.slice(0, 5)` is the direct cap. |
| C2 | Suggestions from every proposal are appended into one estate-level list. | prototype/copilot-studio-knowledge-compiler/app.js:332 | Read | High | There is no final estate cap or balancing. |
| C3 | Passage extraction often keeps an entire block together and splits only content over 1,200 characters. | prototype/copilot-studio-knowledge-compiler/app.js:255 | Read | High | Many documents cannot yield 20 passages today. |
| C4 | Every generated suggestion is selected and rendered by default. | prototype/copilot-studio-knowledge-compiler/app.js:363 | Read | High | Per-document growth directly expands the review list. |
| C5 | The model evaluation prompt defines five scoring criteria, not question generation. | src/shaper/prompts/evaluation.md:3 | Read | High | Prompt changes are out of scope. |
| C6 | Existing tests check export wiring but not question count, diversity, or balancing. | tests/test_architecture.py:259 | Read | High | New assertions or executable browser validation are needed. |

### External Evidence

None.

### Contradictions / Conflicts

* The user asked for approximately 20, while sparse knowledge may not support 20
  distinct grounded questions. Resolve this by treating 20 as a target maximum
  and reporting the actual count.

## Findings Mapped to Questions and Evidence

| Question | Finding | Evidence IDs | Confidence | Decision or readiness implication |
|----------|---------|--------------|------------|-----------------------------------|
| Q1 | The only common-question cap is `.slice(0, 5)` in client-side draft generation. | C1, C5 | High | No AI prompt or backend migration is needed. |
| Q2 | Drafts are transient browser objects exported as JSONL or CSV. | C2, C4 | High | No persistence schema or token budget changes are needed. |
| Q3 | Generate only from substantive unique passages and allow fewer than 20. | C3 | High | Avoid invented or repetitive questions. |
| Q4 | Update passage selection, review copy, documentation, and frontend validation. | C4, C6 | High | Implementation is bounded and ready. |

## Key Discoveries

* The current five-question behavior is deterministic frontend logic, not AI
  generation.
* A per-document limit of 20 could create an unbounded review set across an
  estate.
* Balanced estate-level selection can provide up to 20 questions while preserving
  representation across documents and source order.

## Alternatives and Decision State

### Selected Recommendation

* Approach: Generate a richer pool of distinct passage-grounded questions per
  document, then select up to 20 across the estate with round-robin document
  balancing.
* Rationale: This meets the desired coverage, bounds review and export size, and
  avoids early-document bias or unsupported filler.
* Evidence refs: C1-C4.
* Implementation impact: Browser generation and selection helpers, review copy,
  feature documentation, and frontend contract validation.
* Confidence: High; native browser validation will confirm rendering and export.

### Alternative: 20 per document

* Approach: Replace `.slice(0, 5)` with `.slice(0, 20)`.
* Trade-offs: Minimal code, but large estates can produce hundreds of selected
  drafts and early passages dominate.
* Evidence refs: C1, C2, C4.
* Rejection rationale: It does not provide a predictable estate evaluation set.

### Alternative: AI-generated questions

* Approach: Add a backend model call and structured question schema.
* Trade-offs: Potentially more natural wording, but introduces cost, latency,
  approval, failure handling, token budgets, and a new prompt lifecycle.
* Evidence refs: C5.
* Rejection rationale: The requested coverage increase does not require a new
  model workflow.

## Open Questions, Risks, and Residual Uncertainty

* Blocking: None.
* Important: None.
* Follow-up: A future model-backed generator could improve question naturalness if
  deterministic drafts prove insufficient after user testing.
* Residual uncertainty: Actual source structure varies, so sparse documents may
  still produce fewer than 20 grounded questions.

## Current Decisions

| Decision | Status | Owner / source | Rationale | Evidence IDs | Implications |
|----------|--------|----------------|-----------|--------------|--------------|
| Target up to 20 questions per estate | Confirmed | User plus evidence | Meets requested scale with bounded review size. | C1-C4 | Add an explicit constant and balanced selector. |
| Never pad to 20 with duplicates or unsupported questions | Confirmed | Evidence | Evaluation cases must remain grounded. | C3 | Show the actual available count. |
| Leave model evaluation prompt unchanged | Confirmed | Evidence | It governs scoring, not question creation. | C5 | HVE prompt behavior gate is not applicable. |

## Unresolved Decisions

None.

## Potential Next Research

| Priority | Research item | Expected value | Trigger | Selected? | Related questions / evidence |
|----------|---------------|----------------|---------|-----------|------------------------------|
| Low | Model-backed natural-language question generation | Improve wording quality | Deterministic question feedback is poor | Deferred | C5 |

## Planning Readiness

* Status: Ready.
* Decision state: Select up to 20 distinct, balanced, passage-grounded questions
  per estate.
* Evidence basis: C1-C6.
* Preconditions met: Runtime path, alternatives, constraints, and validation
  surfaces are identified.
* Blockers: None.
* Smallest action to change readiness: None.

## Closeout Record

| Field | Record |
|-------|--------|
| Research execution status | Complete |
| Completed waves | Wider, Deeper, and Contrarian |
| Lane evidence or inline fallback | Inline due to one small continuous browser path |
| Research disposition | Executed |
| Planning Readiness | Ready, C1-C6 |
| Blockers | None |
| Continuation owner and state | HVE Builder parent, automatic return to authoring |

## Advisory Next Step

| Field | Record |
|-------|--------|
| Research disposition | Executed |
| Planning Readiness | Ready |
| Output mode and planning support | Convergence; implementation-ready |
| Acting owner | HVE Builder parent |
| Required gates or confirmations | Frontend behavior and host validation pending |
| Continuation result | Return evidence to active HVE Builder authoring |
| Primary evidence file | .copilot-tracking/research/2026-09-15/evaluation-question-count-research.md |
| Notes for planning or re-entry | Implement balanced up-to-20 generation without changing evaluation prompt |

* Advisory only: rpi-research does not invoke a follow-on skill.
* Completion basis: All code-path questions are answered and further searches are
  unlikely to change the recommendation.

## Sources

No external sources used.

## Artifact Self-Check

* [x] Every research question is answered.
* [x] The cycle includes Wider, Deeper, and Contrarian waves in order.
* [x] Research posture, provenance, and completion basis are recorded.
* [x] Every codebase finding has a stable C-ID and workspace-relative location.
* [x] Findings, alternatives, decisions, and readiness cite evidence IDs.
* [x] Extension and participation records are complete.
* [x] Untrusted content remained inert and no secrets were recorded.
