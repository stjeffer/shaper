<!-- markdownlint-disable-file -->

# Task Research: post-shaping-validation-strictness

| Field              | Value |
|--------------------|-------|
| Date               | 2026-09-16 |
| Researcher / agent | rpi-research |
| Status             | Complete |
| Artifact path      | .copilot-tracking/research/2026-09-16/post-shaping-validation-strictness-research.md |

## Research Brief

* What to research: Why post-shaping validation continues to reject candidates with review-note, material-fact, clause, modality, and qualifier findings, and whether the gate should be removed, optional, or calibrated.
* Why it matters: Repeated false positives prevent approved transformations from completing even when the user perceives no meaningful policy difference.
* Audience or intended use: Engineering implementation of a production-safe correction.
* Scope: src/shaper/application/validation.py, src/shaper/application/shaping.py, src/shaper/prompts/shaping.md, related tests, and the supplied failure.
* Non-goals: Disabling invention detection, weakening approval binding, or redesigning assessment.
* Criteria: Reduce false positives while retaining fail-closed rejection of invented values, changed duties, and unapproved omissions.
* Requested outputs: Root cause, alternatives, and one implementation recommendation.
* Output mode: convergence.

## Research Parameters

| Field | Value |
|-------|-------|
| Research question(s) | Which validation rules are producing false positives, and what is the narrowest safe calibration? |
| Codebase scope | Shaping prompt, candidate validation, repair flow, and focused tests |
| External scope | none |
| Initial internal candidate areas | src/shaper/application/validation.py; src/shaper/application/shaping.py; src/shaper/prompts/shaping.md; tests/test_validation_review.py; tests/test_shaping.py |
| Initial external candidate areas | none |
| Research posture | focused |
| Posture provenance | default for bounded internal task with named failure evidence |
| Explicit limits / deadline | none |
| Posture-specific completion basis | focused scope and materiality |
| Edits allowed during research? | no, research-only |
| Resolved evidence root | .copilot-tracking/ |
| Known constraints / excluded sources | Code-only research; do not make the validation gate optional or remove it without evidence that safety remains enforced elsewhere |

## Extension Registry and Provenance

| Kind | Candidate | Match and provenance | Scoped authority or output contract | Selected / skipped reason |
|------|-----------|----------------------|-------------------------------------|---------------------------|
| Instruction | copilot-tracking.instructions.md | Applies to research artifact path | Tracking artifact structure and path rules | Selected |
| Skill | rpi-research | Explicitly activated for decision-critical internal research | Read-only three-wave evidence synthesis | Selected |
| Skill | hve-builder | Shaping prompt may require a follow-on behavior-bearing mutation | Prompt lifecycle and behavior gate | Deferred until research selects a change |
| Research specialist | none | Focused continuous validation chain is small enough to trace inline | Not applicable | Skipped to avoid duplicated investigation |

## User Participation and Research Decisions

| Checkpoint | Questions or no-interaction rationale | Answers / unanswered | Resulting decision or selected further research |
|------------|-----------------------------------------|----------------------|--------------------------------------------------|
| Intake | The user supplied the failure and three alternatives; autopilot permits selecting the safest evidence-backed option | No unanswered intake question | Compare removal, optional mode, and calibration; prefer calibration if evidence supports it |
| Direction change | None yet | None | Preserve current brief |
| Convergence | Evidence supports calibration rather than removal or optional bypass | No unanswered question | Select a required gate with semantic blockers and advisory representation findings |

## Scope and Success Criteria

* Scope: Post-shaping deterministic validation and its repair feedback.
* Assumptions: At least some listed findings are caused by representation-sensitive heuristics rather than true policy changes.
* Success criteria:
  * Every research question is answered or marked with the missing evidence.
  * Code findings use stable evidence IDs and workspace-relative locations.
  * Removal, optional validation, and targeted calibration are compared.
  * The recommendation preserves invention and approval safeguards.

## Task Research Requests

* Explicit requests: Investigate continually blocking post-shaping assessment and choose removal, optional behavior, or less strict behavior.
* Inferred research questions: Determine why values such as `0` and `701` are extracted; why valid sections after review notes appear; whether source-authored AI directives are still treated as mandatory policy; and whether repair feedback is actionable.
* Caller constraints and non-goals: Fix repeated blocking without allowing hallucinated policy or silent policy loss.

## Direction Controls

| Control type | Direction or boundary | Source / checkpoint | Effect on active brief, evidence, or revalidation |
|--------------|-----------------------|---------------------|---------------------------------------------------|
| add | Compare remove, optional, and less strict | User | Alternatives must be explicitly assessed |
| exclude | Do not retain a gate that continually blocks valid shaping without calibration | User | False-positive sources must be identified and addressed |
| narrow | Focus on post-shaping validation | User | Assessment changes are considered only where shared classification directly causes the failure |

## Research Questions

| # | Sub-question | Type | Priority | Status |
|---:|--------------|------|----------|--------|
| Q1 | Which exact validation heuristics explain the supplied findings? | depth | H | answered |
| Q2 | Does the repair loop receive enough structured guidance to correct those findings? | depth | H | answered |
| Q3 | What safety controls would be lost by removing or making validation optional? | straightforward | H | answered |
| Q4 | What calibrated design reduces false positives without accepting inventions or unauthorized omissions? | depth | H | answered |

## Prior Knowledge Gate

* Existing artifacts reviewed: Prior source-preservation research and prompt 2.1 behavior evidence from the current release.
* Reused (verified) findings: Approval-bound exclusions and review-note separation are current as of commit 07820a2; fresh code evidence is still required for this failure.
* Superseded / stale: The conclusion that all current preservation checks are appropriately calibrated is challenged by the new production failure.

## Research Cycle Log

### Cycle 1

* Active direction controls: compare all three alternatives; preserve anti-invention and approval boundaries.
* Active research posture and completion basis: focused; stop after the continuous validation chain and focused regressions explain the material failure.
* Explicit limits or deadline effect: none.

#### Wave 1: Wider

* Plan and independent lanes: Map each reported rule ID to its extractor and matching algorithm, then trace repair feedback and prompt layout constraints.
* Worker evidence relationships or inline fallback: Inline because this is one tightly coupled validation chain.
* Reflection: C1-C4 show three distinct causes: malformed review-note structure expands the semantic scan to the complete answer; generic material-clause matching treats every three-word source clause as policy; and qualifier matching treats words such as `once` as restrictions without first establishing policy context.

#### Wave 2: Deeper

* Parent-prioritized material from Wave 1: C1-C4, plus the bounded repair behavior in C5 and warning acceptance in C6.
* Plan and independent lanes: Inspect token/value extraction, review-note splitting, clause alignment, qualifier matching, exclusion classification, and bounded repair.
* Worker evidence relationships or inline fallback: Inline.
* Reflection: C5 shows the model receives structured findings but has only one repair candidate. Repeating broad lexical blockers is therefore terminal. C6 confirms warnings remain visible to review while only blocking findings prevent transformation, enabling safe separation of advisory representation checks from semantic invariants.

#### Wave 3: Contrarian

* In-scope challenge targets and boundaries: Test whether removal or optional validation is safer or simpler, and whether prompt-only changes could solve the issue.
* Plan and independent lanes: Compare enforcement coverage and existing regression expectations for all three alternatives.
* Worker evidence relationships or inline fallback: Inline; C6-C8 compare enforcement coverage.
* Reflection: Removing or bypassing validation would also remove exact invention, identifier, modality, and approved-exclusion enforcement. Prompt-only repair cannot prevent deterministic false positives. A required calibrated gate is the only alternative that addresses the root cause without creating an unsafe bypass.

#### Parent Synthesis and Disposition

| Material / claim | Evidence IDs or worker pointers | Parent disposition | Evidence-based rationale | Primary-artifact treatment |
|------------------|---------------------------------|--------------------|--------------------------|----------------------------|
| Review-note structure and policy diagnostics should remain visible but not independently block | C1, C5, C6 | accepted | They describe output organization, while substantive omission and invention checks still run on the policy region | Recommendation |
| Semantic checks must always exclude the review-note region | C1, C3 | accepted | A formatting defect must not manufacture facts or controls from non-policy notes | Recommendation |
| Generic lexical material-clause coverage should be advisory | C2, C6 | accepted | It cannot reliably distinguish paraphrase from omission; specific facts, identifiers, modalities, and qualifiers remain blocking | Recommendation |
| Qualifier preservation should require policy context | C4 | accepted | Bare lexical matches such as rhetorical `once` are not policy restrictions | Recommendation |
| Remove or make validation optional | C3, C6 | rejected | Both alternatives remove independent anti-invention and policy-preservation enforcement | Rejected alternative |
| Expand unsafe-source discovery for coordinated AI directives and unsupported promotional comparisons | C7 | accepted | Current patterns do not cover the supplied `frame ... recommended default` and `sets the standard` language consistently | Recommendation |

#### Cycle Re-entry Evaluation

* Another complete three-wave cycle needed: no.
* Trigger or stop basis: Focused code paths explain every reported finding category; likely additional sources are redundant.
* Revised brief or revalidation required: none.
* Readiness effect: Ready for a targeted implementation and regression pass.

## Evidence Log

* Delegation: inline; the scope is one continuous validation chain.

### Codebase Evidence

| ID | Claim / finding | Location (`path:line`) | Tool | Confidence | Notes |
|----|-----------------|------------------------|------|------------|-------|
| C1 | A malformed review-note section causes every semantic check to scan the entire answer, so note metadata and later headings become candidate policy. | src/shaper/application/validation.py:294 | read | high | `answer_text` switches to the full answer whenever the structure check reports any issue. |
| C2 | Generic material-clause preservation blocks any source clause with at least three meaningful words when lexical coverage falls below 60%, regardless of whether the clause is operative policy, promotional prose, or a faithful paraphrase. | src/shaper/application/validation.py:433 | read | high | This is representation-sensitive and duplicates more specific controls. |
| C3 | Material facts remain a necessary semantic invariant, but they currently consume the expanded full-answer region after a review-note structure defect. | src/shaper/application/validation.py:342 | read | high | This explains unrelated introduced values in the same failure cluster. |
| C4 | Qualifier checks apply `only`, `after`/`once`, `within`, and `during` to every source clause; `_is_policy_clause` excludes only questions and colon-terminated lines. | src/shaper/application/validation.py:574 | read | high | Rhetorical `once you explore` is therefore treated as a policy restriction. |
| C5 | The shaping loop permits two candidates by default and treats every blocking validator finding as mandatory repair input; failure after the second candidate is terminal. | src/shaper/application/shaping.py:81 | read | high | Broad false positives cannot be recovered through further attempts. |
| C6 | Publication evaluation passes when blocking findings are zero while retaining warning counts, so representation diagnostics can remain visible without preventing transformation. | src/shaper/application/artifacts.py:164 | read | high | Existing severity semantics support calibration without an optional bypass. |
| C7 | Unsafe-source discovery recognizes explicit AI context and a narrow comparative vocabulary, then narrows evidence to matching coordinated fragments. It does not cover imperative `frame` continuations or `sets the standard` promotional comparisons. | src/shaper/application/document_findings.py:438 | read | high | Supplied source language can remain in the preservation baseline even when it is unsafe guidance or promotional assertion. |
| C8 | Prompt 2.1 requires review notes to be final and treats every validator finding as blocking repair work. | src/shaper/prompts/shaping.md:92 | read | high | Prompt-only refinement cannot correct a deterministic classification error. |

### External Evidence

No external evidence.

### Contradictions / Conflicts

* The user reports no meaningful difference, while the validator reports several policy changes. C1-C4 resolve the contradiction as cascading and context-free classification rather than evidence that all listed policy changes occurred.

## Findings Mapped to Questions and Evidence

| Question | Finding | Evidence IDs | Confidence | Decision or readiness implication |
|----------|---------|--------------|------------|----------------------------------|
| Q1 | The structure defect cascades into facts and controls; generic clause and qualifier checks are context-free. | C1-C4, C7 | high | Calibrate scope and severity rather than adding retries. |
| Q2 | Repair receives structured findings but only one bounded repair and must treat all blockers as defects. | C5, C8 | high | False blockers must be removed at the validator. |
| Q3 | Removal or optional bypass loses independent invention, identifier, modality, and exclusion checks. | C3, C6 | high | Keep the gate required. |
| Q4 | Separate semantic blockers from representation warnings, always isolate substantive policy, require policy context for qualifiers, and improve unsafe-source discovery. | C1-C8 | high | Ready for implementation. |

## Key Discoveries

* One review-note layout defect currently amplifies into unrelated value and modality failures.
* Generic lexical similarity is being used as a blocking semantic judgment even though specific deterministic invariants already exist.
* Rhetorical temporal words are treated as policy qualifiers without a policy-context predicate.
* The existing warning path provides a safe way to retain diagnostics without blocking publication.
* Source-authored AI directives and promotional comparisons need broader but still bounded deterministic classification.

## Alternatives and Decision State

### Selected Recommendation

* Approach: Keep post-shaping validation mandatory, always isolate the substantive answer from review notes, downgrade representation-only review-note and generic clause diagnostics to warnings, restrict qualifier checks to policy-bearing clauses, and expand deterministic unsafe-source classification for coordinated directive continuations and explicit promotional comparisons.
* Rationale: This removes cascading and context-free false blockers while preserving exact values, identifiers, duties, permissions, prohibitions, approved exclusions, and grounded claims as blocking invariants.
* Evidence refs: C1-C8.
* Implementation impact: validation.py, document_findings.py, prompt version and contract wording if needed, plus focused regressions and behavior evidence.
* Confidence: high; candidate-specific text could refine classification but is not required to address the demonstrated algorithmic causes.

### Alternative: Remove post-shaping validation

* Approach: Publish model output without deterministic source-preservation validation.
* Trade-offs: Eliminates blocking but also removes the independent invention and policy-loss boundary.
* Evidence refs: C3, C6.
* Rejection rationale: It removes independent checks for invented facts, changed controls, source identity, and approved exclusions.

### Alternative: Make post-shaping validation optional

* Approach: Permit deployments or transformations to bypass the gate.
* Trade-offs: Reduces blocking selectively but creates inconsistent trust guarantees and an unsafe configuration path.
* Evidence refs: C3, C6.
* Rejection rationale: It creates inconsistent trust guarantees and an operator-controlled path around safety validation.

### Alternative: Calibrate representation-sensitive rules

* Approach: Retain deterministic validation while narrowing heuristics and separating blocking semantic invariants from advisory structural diagnostics.
* Trade-offs: Requires targeted code and regression work but retains independent safety controls.
* Evidence refs: C1-C8.
* Rejection rationale: Selected, not rejected.

## Open Questions, Risks, and Residual Uncertainty

* Blocking: none.
* Important: Production source and candidate bodies are unavailable, so conclusions must be grounded in the supplied snippets and local regressions.
* Follow-up: Retry with fresh governance state after deployment.
* Residual uncertainty: The complete production candidate is unavailable; focused regressions must represent the reported snippets and cascading structure case.

## Current Decisions

| Decision | Status | Owner / source | Rationale | Evidence IDs | Implications |
|----------|--------|----------------|-----------|--------------|--------------|
| Preserve an independent anti-invention boundary | confirmed | User concern plus C3 and C6 | Less blocking does not require accepting hallucinated policy | C3, C6 | Keep semantic invariants blocking |
| Calibrate rather than remove or bypass validation | proposed | C1-C8 | Addresses the root causes while retaining independent enforcement | C1-C8 | Implement focused severity, scope, context, and classification changes |

## Unresolved Decisions

| Decision | Smallest evidence or answer needed | Owner | Impact | Blocker status |
|----------|------------------------------------|-------|--------|----------------|
| Production retry result | Fresh discovery, approval, and transformation after deployment | downstream owner | Confirms document-specific behavior | follow-up |

## Potential Next Research

| Priority | Research item | Expected value | Trigger | Selected? | Related questions / evidence |
|----------|---------------|----------------|---------|-----------|------------------------------|
| H | Add regressions for cascading review-note structure, rhetorical qualifiers, directive continuations, and promotional comparisons | Verifies the selected calibration | Implementation | yes | Q1-Q4; C1-C8 |

## Planning Readiness

* Status: Ready.
* Decision state: Required calibrated gate selected.
* Evidence basis: C1-C8.
* Preconditions met: Root causes, alternatives, retained safeguards, and test targets are identified.
* Blockers: none.
* Smallest action to change readiness: none.

## Closeout Record

| Field | Record |
|-------|--------|
| Research execution status | Complete |
| Completed waves | Wider, Deeper, and Contrarian |
| Lane evidence or inline fallback | Inline continuous-chain investigation selected |
| Research disposition | executed |
| Planning Readiness | Ready, supported by C1-C8 |
| Blockers | none |
| Continuation owner and state | Active parent may begin implementation |

## Advisory Next Step

| Field | Record |
|-------|--------|
| Research disposition | executed |
| Planning Readiness | Ready, supported by C1-C8 |
| Output mode and planning support | convergence; yes |
| Acting owner | active parent |
| Required gates or confirmations | Focused implementation tests and prompt behavior gate pending |
| Continuation result | Active parent implementation |
| Primary evidence file | .copilot-tracking/research/2026-09-16/post-shaping-validation-strictness-research.md |
| Notes for planning or re-entry | Preserve semantic blockers and add production-failure regressions |

* Advisory only: rpi-research does not invoke a follow-on skill.
* Completion or limit-blocked basis: All reported rule families are explained and further code search is unlikely to change the selected calibration.

## Sources

No external sources used.

## Artifact Self-Check

* [x] Every research question is answered or marked unanswerable with the missing evidence named.
* [x] Every executed cycle includes Wider, Deeper, and Contrarian waves.
* [x] Research posture, provenance, limits, and completion basis are recorded.
* [x] Every codebase finding carries a stable ID and location.
* [x] Sources states that no external sources were used.
* [x] Findings, alternatives, decisions, and readiness cite evidence IDs.
* [x] Extension provenance is recorded.
* [x] User participation and no-interaction rationale are recorded.
* [x] Direction controls are recorded.
* [x] Parent synthesis records dispositions.
* [x] No placeholders or stale pending states remain.
