# Plan Critique: Shaper Multi-Agent Platform Architecture

## Execution

* Status: Complete
* Verdict: Revise
* Boundary: Caller architecture guidance, completed research, implementation
  plan, phase details, stated requirements, acceptance criteria, dependencies,
  test ownership, and change limits.
* Limitations: No external research was performed; deployment is outside this
  implementation increment.

## Coverage Assessment

The plan credibly establishes Shaper as a platform rather than an agent,
preserves compatibility, and separates current from planned topology. It covers
all five agent roles, deterministic orchestration, approval boundaries, API,
schema, documentation, concept, and validation. Two execution-state ambiguities
could cause the implementation or documentation to overstate current capability.

## Findings

### PC-001 - Distinguish analysis orchestration from durable workflow orchestration

* Severity: Medium
* Related IDs: FR1, FR9, P01-T02, P02-T01
* Evidence: The planned endpoint coordinates five roles synchronously over one
  assessment, while durable multi-phase workflow state and managed scheduling
  are explicitly out of scope.
* Impact: Calling the result a platform run could imply persisted Discover to
  Govern lifecycle state that the increment does not implement.
* Smallest useful change: Name the contract and endpoint an analysis, state that
  the orchestrator is synchronous and stateless in this increment, and retain
  durable phase workflow as follow-up.
* Action owner: Planning parent and implementation.
* Resolving evidence: Plan requirements and API tests use analysis terminology;
  architecture documentation states the current lifecycle limitation.
* Disposition type: Direct planner correction.

### PC-002 - Make transformation execution availability explicit

* Severity: Medium
* Related IDs: FR5, NFR4, P01-T02, P03-T02
* Evidence: The planned Transformation Agent output projects recommendations,
  but the current CompilationService supports only single-upload shaping and is
  not invoked by the analysis orchestrator.
* Impact: Consumers could mistake recommendations for executable estate-wide
  transformations or assume Knowledge Consolidation is implemented.
* Smallest useful change: Add explicit proposal-only and execution-availability
  state to the Transformation Agent output and test it. Document the existing
  compilation kernel as a separate, human-approved execution path.
* Action owner: Planning parent and implementation.
* Resolving evidence: Typed contract, invariant tests, and current-capability
  mapping in architecture documentation.
* Disposition type: Direct planner correction.

### PC-003 - Preserve assessment compatibility with a single source of truth

* Severity: Low
* Related IDs: FR8, NFR1, P01-T02, P02-T04
* Evidence: Both the legacy assessment endpoint and the new analysis endpoint
  will construct assessment evidence.
* Impact: Separate construction paths could drift in validation, limits, or IDs.
* Smallest useful change: Inject one `EstateAssessmentService` instance into the
  orchestrator and use the same service implementation for both endpoints.
* Action owner: Implementation.
* Resolving evidence: Composition code and a test comparing assessment identity
  across both API surfaces.
* Disposition type: Direct planner correction.

## Closeout

* Highest-impact finding: PC-001.
* User response required: No.
* Smallest next action: Apply all three direct corrections to the plan and phase
  details, then proceed to implementation without another critique.
