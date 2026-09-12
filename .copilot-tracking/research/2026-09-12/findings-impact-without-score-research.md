<!-- markdownlint-disable-file -->

# Task Research: findings-impact-without-score

| Field              | Value                                                                 |
|--------------------|-----------------------------------------------------------------------|
| Date               | 2026-09-12                                                            |
| Researcher / agent | rpi-research                                                          |
| Status             | Complete                                                              |
| Artifact path      | .copilot-tracking/research/2026-09-12/findings-impact-without-score-research.md |

## Research Brief

* What to research: Identify the prompt-engineering artifacts that calculate or present a score out of 100 and determine how findings can instead explain their effect on agent performance.
* Why it matters: The requested output should communicate actionable findings and their performance consequences without reducing the assessment to a numeric score.
* Audience or intended use: HVE Builder authoring, static review, behavior-gate classification, and validation.
* Scope: Repository-local prompt, agent, skill, instruction, template, test, and documentation surfaces that define the affected assessment output.
* Non-goals: External research, unrelated scoring systems, implementation outside the identified assessment workflow, and changes during this research phase.
* Criteria: Locate every authoritative output contract and directly coupled validation surface; identify the smallest consistent change set; preserve unrelated workflow behavior.
* Requested outputs: A convergence recommendation with exact target paths, evidence locations, acceptance criteria, and risks.
* Output mode: convergence

## Research Parameters

| Field                            | Value                                                                 |
|----------------------------------|-----------------------------------------------------------------------|
| Research question(s)             | Which artifacts own the score and findings output, and what contract should replace the score while explaining performance impact? |
| Codebase scope                   | Current repository                                                    |
| External scope                   | none                                                                  |
| Initial internal candidate areas | .github agents, prompts, skills, instructions, tests, and repository documentation |
| Initial external candidate areas | none                                                                  |
| Research posture                 | focused                                                               |
| Posture provenance               | default for a bounded internal change                                 |
| Explicit limits / deadline       | none                                                                  |
| Posture-specific completion basis | Focused scope coverage and materiality                               |
| Edits allowed during research?   | no, research-only                                                     |
| Resolved evidence root           | .copilot-tracking                                                     |
| Known constraints / excluded sources | Code-only research; no external sources; research-only during this phase |

## Extension Registry and Provenance

* Precedence: platform and host safety; caller scope and criteria; matching repository instructions and enforced schemas; rpi-research contract; domain skills and specialists; examples and preferences.

| Kind                | Candidate                                      | Match and provenance                    | Scoped authority or output contract                     | Selected / skipped reason |
|---------------------|------------------------------------------------|-----------------------------------------|---------------------------------------------------------|---------------------------|
| Instruction         | copilot-tracking.instructions.md               | Applies to the evidence path            | Tracking artifact placement and content conventions     | Selected                  |
| Instruction         | hve-builder.instructions.md                    | Applies to prompt-engineering artifacts | Authoring quality criteria                              | Selected                  |
| Instruction         | markdown.instructions.md and writing-style.instructions.md | Apply to Markdown targets | Markdown structure and clear language                   | Selected                  |
| Skill               | hve-builder                                    | Explicitly matched to artifact changes  | Owns lifecycle routing after research                   | Selected                  |
| Research specialist | none                                           | Bounded, low-volume internal search      | No independent lane improves evidence quality           | Skipped                   |

## User Participation and Research Decisions

| Checkpoint       | Questions or no-interaction rationale | Answers / unanswered | Resulting decision or selected further research |
|------------------|----------------------------------------|----------------------|--------------------------------------------------|
| Intake           | The request provides a clear desired outcome and the branch context narrows the intent. | No questions needed | Research the current score and finding-impact contract. |
| Direction change | No material direction change.          | Not applicable       | Keep the focused code-only scope.                |
| Convergence      | Evidence supports a bounded presentation change with an additive finding field. | No question needed | Remove score presentation, add explicit agent-impact explanations, and preserve internal scoring contracts. |

## Scope and Success Criteria

* Scope: Identify the authoritative score and finding-output definitions plus directly coupled tests and documentation.
* Assumptions: The affected workflow is represented by current repository artifacts and branch changes; verify both rather than trusting the branch name.
* Success criteria:
  * Every research question is answered or marked unanswerable with the missing evidence named.
  * Evidence uses stable IDs and workspace-relative `path:line` locations.
  * The recommendation removes the score consistently and defines clear performance-impact language.
  * Risks and directly coupled validation surfaces are identified.

## Task Research Requests

* Explicit requests: Remove the score out of 100; produce findings in clear language; let users see why findings impact agent performance.
* Inferred research questions: Find all affected output contracts, determine the clearest replacement schema, and identify tests or docs that enforce it.
* Caller constraints and non-goals: No broader redesign was requested.

## Direction Controls

| Control type (add / change / narrow / exclude / discard) | Direction or boundary | Source | Effect on remaining work |
|----------------------------------------------------------|-----------------------|--------|--------------------------|
| change                                                   | Replace numeric scoring with explanatory findings | user | Search for score ownership and impact fields. |
| narrow                                                   | Preserve the surrounding review workflow | inferred from request | Avoid unrelated architecture changes. |

## Research Questions

|  # | Sub-question | Type (depth / breadth / straightforward) | Priority | Status |
|---:|--------------|------------------------------------------|----------|--------|
| Q1 | Which artifacts calculate, require, or display a score out of 100? | breadth | H | answered |
| Q2 | Which artifacts define findings and their explanation of agent-performance impact? | depth | H | answered |
| Q3 | Which tests, fixtures, schemas, or docs must change to keep the contract consistent? | breadth | H | answered |
| Q4 | What is the smallest coherent replacement contract, and what counter-risks must it address? | depth | H | answered |

## Prior Knowledge Gate

* Existing artifacts reviewed: The current source, tests, documentation, and the completed Assess Results and evidence-grounded findings research and plans.
* Reused (verified) findings: The per-document Assess table is a bounded content-quality surface; estate-wide governance assessment and artifact evaluation are separate score-bearing contracts.
* Superseded / stale: The earlier decision that no finding schema expansion was needed is superseded by the new requirement to expose a distinct agent-performance impact explanation.

## Research Cycle Log

### Cycle 1

* Active direction controls: Replace score; preserve surrounding workflow.
* Active research posture and completion basis: focused; cover all material score and impact surfaces.
* Explicit limits or deadline effect: none

#### Wave 1: Wider

* Plan and independent lanes: Search repository text and current branch diff for numeric score, findings, impact, and performance terminology.
* Worker evidence relationships or inline fallback: Inline because this is a bounded, tightly coupled search.
* Reflection: The per-document score is rendered in each Assess row and averaged in the summary. A score is also embedded in transformation rationale, while separate estate-wide and artifact-evaluation scores serve different workflows.

#### Wave 2: Deeper

* Parent-prioritized material from Wave 1: The per-document readiness report, result renderer, recommendation rationale, documentation, and static UI/API tests.
* Plan and independent lanes: Read authoritative target sections and directly coupled validation surfaces.
* Worker evidence relationships or inline fallback: Inline review of C1-C10.
* Reflection: Findings already carry a label, explanation, severity, and evidence, but no separate field explains agent-performance consequences. The UI renders the generic explanation without an impact label.

#### Wave 3: Contrarian

* In-scope challenge targets and boundaries: Test whether removing the score would leave ordering, severity, summary, or validation ambiguous.
* Plan and independent lanes: Inspect alternative qualitative contracts already present in the repository and look for dependencies on numeric scoring.
* Worker evidence relationships or inline fallback: Existing API compatibility and adjacent score workflows were inspected inline.
* Reflection: Removing every numeric metric would conflate per-document content discovery with estate governance and transformed-artifact evaluation. Removing only the visible per-document readiness score, while retaining internal metrics for effort and adding an optional backward-compatible impact field, satisfies the request without breaking historical report deserialization.

#### Parent Synthesis and Disposition

| Material / claim | Evidence IDs or worker pointers | Parent disposition (accepted / rejected / deferred) | Evidence-based rationale | Primary-artifact treatment |
|------------------|---------------------------------|-----------------------------------------------------|--------------------------|----------------------------|
| Remove per-document score presentation | C1, C2, C3, C4 | accepted | The score is presented as a headline judgment even though the actionable unit is the evidence-grounded finding. | Selected recommendation |
| Add explicit agent-impact language to findings | C5, C6, C7 | accepted | Existing explanations identify conditions but do not consistently state the consequence for agent behavior. | Selected recommendation |
| Remove all score-bearing contracts | C8, C9, C10 | rejected | Estate governance and artifact evaluation are separate workflows; broad removal would exceed the current Assess-surface request. | Scope boundary |

#### Cycle Re-entry Evaluation

* Another complete three-wave cycle needed: no.
* Trigger or stop basis: The focused target set, dependencies, compatibility risk, and alternative were covered; another search is unlikely to change the recommendation.
* Revised brief or revalidation required: none.
* Readiness effect: Ready.

## Evidence Log

* Delegation: inline because the bounded, tightly coupled search does not justify a worker.

### Codebase Evidence

| ID | Claim / finding | Location (`path:line`) | Tool | Confidence | Notes |
|----|-----------------|------------------------|------|------------|-------|
| C1 | The Assess table visibly labels and renders a per-document Readiness column. | prototype/copilot-studio-knowledge-compiler/index.html:230 | read | high | This is the primary user-facing score surface. |
| C2 | Each document row renders `readiness_score` as a value out of 100 and a progress bar. | prototype/copilot-studio-knowledge-compiler/app.js:635 | read | high | Removing the column also removes score-specific ARIA and styling. |
| C3 | The discovery summary averages `readiness_score` and renders `Estate readiness` out of 100. | prototype/copilot-studio-knowledge-compiler/app.js:688 | read | high | The summary is the second visible per-document score aggregation. |
| C4 | Transformation rationale repeats the document score out of 100. | src/shaper/application/estates.py:1078 | read | high | User-facing downstream prose must not reintroduce the score. |
| C5 | `DocumentFinding` carries label, explanation, severity, review state, and evidence, but no distinct agent-impact explanation. | src/shaper/domain/estate.py:321 | read | high | An additive optional field preserves old persisted reports. |
| C6 | The browser maps each structured finding into visible detail and expandable evidence. | prototype/copilot-studio-knowledge-compiler/app.js:247 | read | high | The existing result component can expose agent impact without a new interaction pattern. |
| C7 | Finding explanations describe detected conditions, and only some state an agent consequence. | src/shaper/application/document_findings.py:158 | read | high | A code-keyed impact catalog avoids duplicating impact prose at every detector call site. |
| C8 | `readiness_score` is part of persisted report identity and effort calculation. | src/shaper/domain/estate.py:332 | read | high | Removing it from the API model would break persisted report compatibility and deterministic IDs. |
| C9 | Estate-wide assessment scores are returned by a separate `/v1/assessments` endpoint. | src/shaper/interfaces/http.py:782 | read | high | This distinct governance assessment is outside the Assess table change. |
| C10 | Artifact evaluation scores are a separate post-transformation quality gate. | tests/test_estate_interfaces.py:285 | read | high | Removing them would weaken an unrelated validation workflow. |

### External Evidence

No external evidence.

### Contradictions / Conflicts

* The explicit request to remove the score conflicts with preserving the existing score in the API. Resolve this by removing score presentation and score-based rationale while retaining the persisted internal field for compatibility and effort calculation (C1-C4, C8).

## Findings Mapped to Questions and Evidence

| Question | Finding | Evidence IDs | Confidence | Decision or readiness implication |
|----------|---------|--------------|------------|-----------------------------------|
| Q1 | The relevant score appears in the Assess table, its summary, and recommendation rationale; the API field also participates in report identity. | C1, C2, C3, C4, C8 | high | Remove user-facing uses, not the compatibility field. |
| Q2 | Findings are structured and evidence-linked, but lack a distinct agent-impact field and label. | C5, C6, C7 | high | Add `agent_impact` and render it explicitly. |
| Q3 | The UI architecture test, report/API tests, documentation, and generated schema are directly coupled. | C1-C8 | high | Update targeted assertions and regenerate the schema snapshot. |
| Q4 | A bounded presentation change plus an additive optional field avoids breaking persisted reports or unrelated score workflows. | C8, C9, C10 | high | Proceed with this compatibility-preserving implementation. |

## Key Discoveries

* The visible score occupies both a table column and an estate summary card, so removing only `/100` text would leave the same unsupported ranking signal (C1-C3).
* The existing evidence disclosure already provides an accessible interaction pattern; agent impact should be visible text, not icon- or color-only content (C6).
* Numeric metrics can remain internal to effort calculation and report identity while the user-facing assessment becomes findings-led (C4, C8).

## Alternatives and Decision State

### Selected Recommendation

* Approach: Remove the per-document Readiness column, readiness progress indicator, estate readiness summary, and score-based recommendation rationale. Add a backward-compatible `agent_impact` field to structured findings, populate it from one code-keyed catalog, and render it with an explicit "Agent impact" label beside evidence.
* Rationale: This replaces an uncalibrated headline score with actionable, evidence-linked language while preserving persisted reports, internal effort calculation, estate governance assessment, and transformed-artifact evaluation.
* Evidence refs: C1-C10.
* Implementation impact: Domain finding model, finding construction, recommendation rationale, Assess UI markup/script/styles, targeted tests, schema snapshot, README, and feature documentation.
* Confidence: high.

### Alternative: Retain a non-prominent numeric score

* Approach: Keep the score but emphasize prose findings.
* Trade-offs: Preserves the current presentation but continues to foreground an uncalibrated ranking.
* Evidence refs: C1-C3.
* Rejection rationale: Conflicts with the explicit request and does not make findings the primary assessment output.

### Alternative: Remove all numeric scoring models

* Approach: Delete per-document, estate-wide, and artifact-evaluation score fields and calculations.
* Trade-offs: Eliminates scores comprehensively but breaks persisted report identity, public contracts, orchestration, and unrelated quality gates.
* Evidence refs: C8-C10.
* Rejection rationale: Exceeds the bounded Assess workflow need and introduces unnecessary compatibility risk.

## Open Questions, Risks, and Residual Uncertainty

* Blocking: none.
* Important: Historical reports will not contain `agent_impact`; the UI needs a clear fallback rather than failing or hiding the field.
* Follow-up: Calibration could later justify a quantitative signal, but it is not required for this change.
* Residual uncertainty: Rendered visual balance requires browser inspection after implementation.

## Current Decisions

| Decision | Status (proposed / confirmed / deferred / superseded) | Owner / source (user / evidence / constraint) | Rationale | Evidence IDs | Implications |
|----------|-------------------------------------------------------|-----------------------------------------------|-----------|--------------|--------------|
| Remove the score out of 100 | confirmed | user | Explicit requirement | User request | Numeric score must disappear from output contracts and dependent surfaces. |
| Explain each finding's agent-performance impact | confirmed | user | Explicit requirement | User request | Findings need plain-language causal explanation. |
| Preserve internal score-bearing compatibility contracts | confirmed | evidence | Prevent breaking persisted reports and separate workflows. | C8-C10 | User-facing output changes without broad domain removal. |

## Unresolved Decisions

| Decision | Smallest evidence or answer needed | Owner | Impact | Blocker status |
|----------|------------------------------------|-------|--------|----------------|
| None | No additional evidence required. | research | No remaining implementation decision. | follow-up |

## Potential Next Research

| Priority | Research item | Expected value | Trigger | Selected? | Related questions / evidence |
|----------|---------------|----------------|---------|-----------|------------------------------|
| L | Revisit quantitative readiness after calibration evidence exists | Could support a future validated measure | Representative human-reviewed evaluation data | deferred | C1-C3 |

## Planning Readiness

* Status: Ready.
* Decision state: Convergence recommendation selected.
* Evidence basis: C1-C10.
* Preconditions met: Target surfaces, compatibility boundary, replacement schema, accessibility pattern, tests, and documentation are identified.
* Blockers: none.
* Smallest action to change readiness: none.

## Closeout Record

| Field                            | Record |
|----------------------------------|--------|
| Research execution status        | Complete |
| Completed waves                  | Cycle 1 Wider, Deeper, and Contrarian |
| Lane evidence or inline fallback | Inline fallback selected for bounded, tightly coupled research |
| Research disposition             | executed |
| Planning Readiness               | Ready (C1-C10) |
| Blockers                         | none |
| Continuation owner and state     | hve-builder parent, ready for implementation |

## Advisory Next Step

| Field                            | Record |
|----------------------------------|--------|
| Research disposition             | executed |
| Planning Readiness               | Ready (C1-C10) |
| Output mode and planning support | convergence; supports direct HVE Builder lifecycle routing |
| Acting owner                     | hve-builder parent |
| Required gates or confirmations  | Implementation and targeted validation pending |
| Continuation result              | Return evidence to active hve-builder parent |
| Primary evidence file            | .copilot-tracking/research/2026-09-12/findings-impact-without-score-research.md |
| Notes for planning or re-entry   | Apply the selected bounded implementation and verify UI, API, schema, and tests. |

* Advisory only: rpi-research does not invoke a follow-on skill.
* Completion or limit-blocked basis: All material questions are answered and another cycle is unlikely to change the recommendation.

## Sources

No external sources used.

## Artifact Self-Check

* [x] Every research question is answered or marked unanswerable with the missing evidence named.
* [x] Every executed cycle includes Wider, Deeper, and Contrarian waves in that order.
* [x] Research posture, provenance, explicit limits, and completion basis are recorded.
* [x] Every codebase finding carries a stable evidence ID and `path:line`.
* [x] Sources states that no external sources were used.
* [x] Findings, alternatives, decisions, and readiness claims cite evidence IDs.
* [x] Extension selection and provenance are recorded.
* [x] User participation and no-interaction rationale are recorded.
* [x] Direction controls record the caller's requested change and narrowed scope.
* [x] Parent synthesis records accepted, rejected, and deferred material.
* [x] Cycle re-entry evaluation records the completion decision.
* [x] The convergence recommendation cites evidence and rejects alternatives.
* [x] Planning Readiness follows from the evidence.
