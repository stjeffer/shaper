<!-- markdownlint-disable-file -->
# RPI Plan Critique: Shaper Knowledge Transformation Platform

## Metadata

* Task ID: shaper-knowledge-transformation-platform
* Critique date: 2026-09-10
* Plan: .copilot-tracking/plans/2026-09-10/shaper-knowledge-transformation-platform-plan.md
* Phase details: .copilot-tracking/details/2026-09-10/shaper-knowledge-transformation-platform-phase-details.md
* Critique execution status: Complete

## Inputs and Criterion Boundary

* Task context and caller requirements: The authoritative Knowledge
  Transformation Platform brief, including four phases, readiness dimensions,
  intervention types, transformation modes, Azure-native surfaces, human
  approval, and explicit exclusions.
* Research and evidence considered:
  .copilot-tracking/research/2026-09-10/shaper-knowledge-transformation-platform-research.md
  plus the plan and phase details.
* Decisions, dependencies, and acceptance criteria considered: The deterministic
  estate-assessment vertical slice, preservation of the compiler, zero new
  dependencies, explicit validation matrix, no source mutation, and deferred
  production calibration.
* Assessment boundary: This critique evaluates implementation credibility for the
  selected vertical slice. It cannot establish production metric validity or
  connector completeness because the plan explicitly defers representative
  corpus calibration and connector expansion.

## Coverage Assessment

| Requirement, research, phase, or task ID | Coverage | Evidence or concern |
|---|---|---|
| Discover | Covered | P01 and P02 define read-only assessment over bounded profiles |
| Understand | Covered | P01-T02 defines topics, overlap, contradictions, and score dimensions |
| Recommend | Covered | P01-T02 defines ranked interventions and supported modes |
| Transform | Partial by design | P03 reaches approval readiness while existing answer shaping remains the only execution path |
| Agent Readiness score | Partial | Metrics and explanations are planned, but assessment coverage and unavailable evidence are not represented |
| Human approval and no mutation | Covered | Scope, functional requirements, and acceptance criteria agree |
| REST and dashboard surfaces | Covered | P02 and P03 provide executable REST plus a hosted concept |
| Azure-native target | Covered as documentation | P04 distinguishes current from target resources |
| Test and validation ownership | Covered | Change budget names semantic, interface, schema, full-suite, Bicep, and browser evidence |

## Verdict

* Verdict: Revise.
* Rationale: The plan is close to implementation-ready, but two direct planner
  corrections are needed to prevent a readiness percentage from hiding missing
  evidence and to avoid overstating deterministic contradiction detection.

## Findings

<!-- rpi:critique id=PC-001 -->
### PC-001 High: Readiness coverage is not part of the score contract

* Related IDs: Q3, P01-T01, P01-T02, Agent Readiness non-functional requirement.
* Evidence: .copilot-tracking/plans/2026-09-10/shaper-knowledge-transformation-platform-plan.md
* Concern: The plan requires component metrics and limitations but does not
  represent how much of the estate or rubric was assessable. A 75 score over four
  observed signals can look equivalent to 75 over complete evidence.
* Impact: Users could interpret missing evidence as measured quality, undermining
  the product's trusted-knowledge positioning.
* Smallest useful change: Add assessment coverage to the domain, API, UI, tests,
  and acceptance criteria. Require assessed and unavailable metric counts and a
  visible coverage percentage alongside the readiness score.
* Action owner: Planning parent.
* Exact resolving evidence: Plan and phase details require coverage fields,
  unknown handling, UI disclosure, and tests proving unavailable evidence does
  not silently become a positive score.
* Decision route: Direct planner correction.

<!-- rpi:critique id=PC-002 -->
### PC-002 Medium: Contradiction detection scope can be misread as open-text inference

* Related IDs: Q2, P01-T02, contradiction functional requirement.
* Evidence: .copilot-tracking/details/2026-09-10/shaper-knowledge-transformation-platform-phase-details.md
* Concern: The selected deterministic service can compare normalized declared
  business terms, but the plan's top-level behavior says it detects
  contradictions without naming that boundary.
* Impact: The delivered endpoint and concept could imply semantic contradiction
  detection across arbitrary prose, which this increment cannot validate.
* Smallest useful change: State that the MVP detects contradiction candidates
  from normalized business-term assertions supplied or extracted upstream, and
  includes provenance and a review-required label.
* Action owner: Planning parent.
* Exact resolving evidence: Functional requirements, details, acceptance
  criteria, API contract, and UI language consistently use candidate
  contradiction terminology and identify assertion provenance.
* Decision route: Direct planner correction.

## Strengths and Residual Risk

* The plan preserves the validated compiler and avoids an unreviewable platform rewrite.
* Test ownership, no-dependency scope, and current-versus-target Azure boundaries are clear.
* Production score calibration and broader transformation execution remain
  explicit follow-ups rather than hidden incompleteness.

## Questions or Blocking Evidence Gaps

* None. Both findings are planner-owned corrections supported by the existing brief.

## Limitations

* No representative enterprise corpus is available, so the critique cannot
  validate thresholds, weights, or measured business value.

## Recommended Next Action

* Highest-impact finding: PC-001.
* Action owner: Planning parent.
* Smallest next action: Add explicit assessment coverage and unavailable-evidence
  handling, then apply PC-002 terminology and provenance corrections.
* User response required: no.
