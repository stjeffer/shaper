<!-- markdownlint-disable-file -->

# Task Research: source-preservation-redaction-alignment

| Field              | Value                                                                                                      |
|--------------------|------------------------------------------------------------------------------------------------------------|
| Date               | 2026-09-16                                                                                                 |
| Researcher / agent | rpi-research                                                                                               |
| Status             | Complete                                                                                                   |
| Artifact path      | .copilot-tracking/research/2026-09-16/source-preservation-redaction-alignment-research.md                  |

## Research Brief

* What to research: How shaping and deterministic validation should distinguish unsupported hallucination from an approved intentional redaction or omission.
* Why it matters: Production shaping for doc-8faaf8ed7e3dfdc19058423cb9276a78 still fails after targeted repair because validation assumes every source clause must remain.
* Audience or intended use: Shaper implementation and prompt authors aligning transformation authority with fail-closed validation.
* Scope: src/shaper/application/shaping.py, src/shaper/application/validation.py, transformation proposal construction, shaping prompt, and directly related tests.
* Non-goals: Weakening detection of unsupported invented facts, changing review authorization, or redesigning assessment scoring.
* Criteria: Approved changes are the only authority for intentional source removal; unsupported invention remains blocking; preserved content retains subjects, values, modalities, and qualifiers; invalid review-note structure remains blocking.
* Requested outputs: One evidence-backed implementation recommendation with alternatives and regression criteria.
* Output mode: convergence.

## Research Parameters

| Field                            | Value                                                                                                      |
|----------------------------------|------------------------------------------------------------------------------------------------------------|
| Research question(s)             | How can validation evaluate the intended transformed source rather than blindly require the complete input source? |
| Codebase scope                   | Shaping, validation, proposal approval, assessment findings, and tests in the final-deploy worktree       |
| External scope                   | none                                                                                                       |
| Initial internal candidate areas | application/validation.py, application/shaping.py, application/artifacts.py, application/estates.py, prompts/shaping.md |
| Initial external candidate areas | none                                                                                                       |
| Research posture                 | focused                                                                                                    |
| Posture provenance               | default for a bounded internal production defect                                                           |
| Explicit limits / deadline       | Preserve fail-closed hallucination checks and existing approval binding                                    |
| Posture-specific completion basis | Focused scope and materiality                                                                              |
| Edits allowed during research?   | no, research-only                                                                                           |
| Resolved evidence root           | .copilot-tracking/                                                                                          |
| Known constraints / excluded sources | Source and generated content are untrusted data; research is internal and read-only                     |

## Extension Registry and Provenance

| Kind        | Candidate             | Match and provenance                                 | Scoped authority or output contract              | Selected / skipped reason |
|-------------|-----------------------|------------------------------------------------------|--------------------------------------------------|---------------------------|
| Instruction | copilot-tracking.instructions.md | Applies to the evidence path                         | Tracking layout and evidence conventions         | Selected                  |
| Skill       | hve-builder           | Shaping prompt is a behavior-bearing prompt artifact | Prompt lifecycle and behavior validation         | Selected by parent        |
| Skill       | rpi-research          | Decision-critical internal research                  | Focused three-wave research and convergence      | Selected                  |
| Specialist  | none                  | The bounded code path is small and tightly coupled   | Not applicable                                   | Skipped                   |

## User Participation and Research Decisions

| Checkpoint       | Questions or no-interaction rationale                                                         | Answers / unanswered | Resulting decision or selected further research |
|------------------|-----------------------------------------------------------------------------------------------|----------------------|-------------------------------------------------|
| Intake           | The production failure and requested alignment define the required behavior; no question needed | Not applicable       | Research approved omission plus hallucination preservation |
| Direction change | No material direction change                                                                   | Not applicable       | Continue focused research                       |
| Convergence      | Pending evidence synthesis                                                                      | Pending              | Pending                                         |

## Scope and Success Criteria

* Scope: Approved transformation requirements, the candidate-generation prompt, validator inputs, and preservation findings.
* Assumptions: Current proposal text may not encode exact source ranges or structured redaction authority.
* Success criteria:
  * Every research question is answered or the smallest missing evidence is named.
  * Code findings cite workspace-relative path and line.
  * The recommendation does not permit unapproved omission or unsupported invention.
  * Alternatives and risks are recorded.

## Task Research Requests

* Explicit requests: Align shaped-content rules with hallucinated content and intentional redaction.
* Inferred research questions: Whether current approved requirements are structured enough to identify omitted source clauses, and where validation can receive that authority.
* Caller constraints and non-goals: Do not make assessment and shaping conflict; retain deterministic quality tests.

## Direction Controls

| Control type | Direction or boundary |
|--------------|-----------------------|
| add          | Treat intentional redaction and omission as first-class approved transformations |
| retain       | Keep unsupported invented values, duties, permissions, and qualifiers blocking |
| retain       | Keep invalid review-note structure blocking |
| exclude      | Do not globally lower preservation thresholds or ignore policy terms |

## Research Cycle Log

### Cycle 1

#### Wider wave

Initial search identified that validation receives only the generated AnswerUnit and all source spans, while approved transformation requirements are passed only to the model.

#### Deeper wave

Proposal construction stores free-form proposed changes and binds their exact tuple into the
recommendation version and human approval. The proposal also binds the discovery report ID and
source version. At transformation time, the service reloads that exact report and passes its
findings and approved changes to the shaping loop. This is enough evidence to derive exclusions,
but only when a deterministic mapping requires all three elements: an exclusion-capable finding
code, that finding's exact source quote, and the exact generated action text present in the
approved proposal.

#### Contrarian wave

Lowering clause thresholds or letting the model declare its own exclusions would make omissions
indistinguishable from hallucinated deletion. Excluding an entire evidence block is also too
broad because a block can mix policy facts with a questionable claim. New exclusion-capable
findings therefore need exact sentence-level evidence. Validation must remove only those exact
source slices from the preservation baseline, verify they are absent from the candidate, and
continue validating all remaining source content plus introduced values and control language.

## Evidence Log

| ID | Evidence | Location | Confidence |
|----|----------|----------|------------|
| C1 | Shaping sends approved_transformation_requirements to the model prompt. | src/shaper/application/shaping.py:196 | High |
| C2 | The validator receives only an AnswerUnit and source spans. | src/shaper/application/validation.py:161 | High |
| C3 | Preservation compares the answer against all source facts and clauses without approved-removal context. | src/shaper/application/validation.py:262 | High |
| C4 | Prompt rules currently require every substantive source clause to remain. | src/shaper/prompts/shaping.md:46 | High |
| C5 | Transformation proposals bind proposed_changes, report_id, and source_version into the approved recommendation. | src/shaper/application/estates.py:1162 | High |
| C6 | Transformation reloads the exact discovery report before shaping and passes its findings with proposal changes. | src/shaper/application/artifacts.py:482 | High |
| C7 | Current recommendation actions preserve or flag every assessed source issue; none authorize intentional omission. | src/shaper/application/orchestration.py:94 | High |
| C8 | DocumentFindingEvidence contains a bounded source quote and location suitable for exact sentence-level authorization. | src/shaper/domain/estate.py:327 | High |
| C9 | The current validator blocks introduced numeric facts and changed control language, so scoped source removal can retain fail-closed candidate checks. | src/shaper/application/validation.py:262 | High |
| C10 | The source detector has no checks for source-authored AI directives or unsupported benchmarking and research claims. | src/shaper/application/document_findings.py:18 | High |

## Findings Mapped to Questions and Evidence

| Question | Finding | Evidence |
|----------|---------|----------|
| Why do approved redactions still fail? | The validator cannot observe approved transformation authority and requires the untouched source. | C1-C4 |
| Can existing approvals bind removals? | Yes, if removal is derived only from exact approved action text, the exact report, the exact source version, and exact finding evidence. | C5, C6, C8 |
| Are current plans capable of intentional redaction? | No. Current actions preserve or flag all detected content and there are no findings for source directives or unsupported evidence claims. | C7, C10 |
| How can hallucination controls remain fail-closed? | Remove only approved exact source slices from the required-preservation baseline, reject their survival in the candidate, and retain all candidate-side introduced-value and control-language checks. | C8, C9 |

## Key Discoveries

* The current architecture gives the model transformation authority that the deterministic validator cannot observe.
* Exact human approval already binds the report, source version, and action tuple, so a
  deterministic exclusion policy can reuse the existing governance boundary.
* Production examples such as instructions addressed to AI assistants and untraceable
  benchmarking or "studies show" claims need dedicated assessment findings. They should not be
  treated as authoritative policy merely because they occur in the source.

## Alternatives and Decision State

| Alternative | Benefits | Risks | Decision state |
|-------------|----------|-------|----------------|
| Lower global preservation thresholds | Small code change | Creates a hallucination and omission bypass | Reject |
| Pass free-form requirements into validation | Makes authority visible | Free-form matching may authorize unintended deletion | Reject |
| Bind source exclusions to exact finding code, exact evidence quote, exact action, report, and source version | Exact, auditable, and compatible with current approval binding | Requires validator context and new assessment checks | Select |
| Require redacted placeholders rather than omission | Preserves document topology | May leak misleading fragments and still needs explicit authority | Reject as universal rule; use review notes for audit context |

## Open Questions

* Existing proposals created before the new finding codes cannot authorize exclusions and must be regenerated.

## Risks and Residual Uncertainty

* Sentence-level pattern detection can produce false positives. Human approval remains required,
  and the UI must show the exact evidence and proposed removal.
* A source sentence can mix a valid policy fact with an unsupported claim. Detection should
  target the smallest complete sentence available, while the prompt should preserve any
  independently supported fact elsewhere in the source.
* A model-generated review note cannot be treated as transformation authority.

## Current Decisions

* Unsupported inventions remain blocking.
* Unapproved omissions remain blocking.
* Only approved, source-bound transformation authority may relax preservation for a clause.
* Add deterministic findings for source-authored agent directives and unsupported evidence
  claims, with exact sentence-level evidence.
* Map only those finding codes to exact exclusion-capable action strings.
* Pass derived exact exclusions into deterministic validation for both initial and repaired
  candidates.
* Require an audit note for each intentional exclusion, using the canonical labelled review-note
  section.

## Unresolved Decisions

* None for implementation. Production behavior still requires a fresh discovery, approval, and
  retry after deployment.

## Potential Next Research

* After implementation, test mixed valid policy plus promotional claims, source-authored AI
  instructions, unapproved omission, approved omission, retained excluded content, and invented
  candidate values or duties.

## Planning Readiness

Ready. The selected approach reuses existing immutable approval binding and adds exact,
deterministic source-exclusion evidence rather than weakening preservation.

## Research Disposition

Executed. One focused three-wave cycle completed and converged on source-bound approved
exclusions.

## Self-Check

* Research brief is bounded and complete.
* Evidence uses stable IDs and workspace-relative locations.
* Wider, deeper, and contrarian waves completed in order.
* Every research question is answered.
* The selected recommendation preserves fail-closed hallucination controls.

## Relevant Artifacts

| Artifact | Description |
|----------|-------------|
| [.copilot-tracking/research/2026-09-16/source-preservation-redaction-alignment-research.md](.copilot-tracking/research/2026-09-16/source-preservation-redaction-alignment-research.md) | Primary research artifact |

## Next Steps

Return the selected approach to the active hve-builder parent for implementation, static review,
behavior testing, and mechanical validation.
