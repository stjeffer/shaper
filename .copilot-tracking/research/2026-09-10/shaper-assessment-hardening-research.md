<!-- markdownlint-disable-file -->
# Research: Shaper Assessment Hardening

## Research Brief

* Topic: Resolve RV-001 through RV-004 from the completed platform Review.
* Purpose: Establish the smallest correct implementation boundary for accepted
  input handling, schema publication, and approval focus.
* Audience and use: Automatic RPI planning and implementation.
* Scope: Timezone validation, unavailable readability, canonical schema
  generation, keyboard focus, and regression coverage.
* Non-goals: New product behavior, scoring calibration, production connectors,
  or broader transformation execution.
* Output mode: Convergence.
* Research posture: Focused, selected because the Review supplies reproducible
  failures and exact source boundaries.
* Interaction: Skipped because autopilot selected the highest-ranked bounded
  defect follow-up and no product decision is required.

## Extensions and Participation

* Platform, repository, Python, accessibility, and RPI instructions: selected
  for safety, code quality, interaction adequacy, and evidence handling.
* Python foundational guidance: applicable to validation and optional metric design.
* Accessibility guidance: applicable to focus continuity and dynamic-state evidence.
* External research: skipped because all four defects are internal contract and
  interaction failures with direct executable evidence.
* Delegation: skipped because the lanes are small, tightly coupled to the same
  bounded increment, and already have an independent Review.

## Questions

* Q1: Where should timezone awareness be enforced so all callers fail safely?
* Q2: How should unassessable text preserve the unavailable-metric contract?
* Q3: Why did the recorded module schema check pass while the canonical snapshot is stale?
* Q4: What is the correct focus target after approval preparation?

## Cycle 1

### Wider wave

The Review identified four symptoms across three boundaries: API and service
input validation, generated schema publication, and dynamic UI focus. Existing
tests cover aware document times, normal readability, initial schema registration,
static accessibility, and the successful journey, but not the failing states.

### Deeper wave

* C1: src/shaper/interfaces/http.py:77 accepts any parsed `datetime`; the service
  reaches freshness arithmetic before the result model validates
  `assessed_at`.
* C2: src/shaper/application/assessment.py:51 is also a public application
  boundary, so service-level timezone validation protects HTTP and non-HTTP callers.
* C3: src/shaper/application/assessment.py:111 assumes every accepted profile has
  a readability value, while src/shaper/application/assessment.py:285 raises
  through `_mean` when text contains no word-bearing sentence.
* C4: src/shaper/schema.py:30 registers the new models, but
  schemas/v1/domain.schema.json:4 omits them.
* C5: src/shaper/schema.py has no module entrypoint guard. Therefore
  `python -m shaper.schema --check` executes no check, while the console entrypoint
  calls `main` and correctly exposes drift.
* C6: prototype/copilot-studio-knowledge-compiler/app.js:160 reveals the approval
  state and hides the focused trigger without assigning focus to the new state.
* C7: tests/test_assessment.py:170 covers naive profile modification time but not
  naive assessment time or text without assessable sentences.

### Contrarian wave

* Reject HTTP-only timestamp validation. It would fix the observed response but
  leave direct application callers exposed to the same arithmetic failure.
* Reject broad rejection of punctuation-only text. The domain deliberately
  accepts bounded non-empty source text, and the assessment contract already
  defines unavailable metrics and reduced coverage.
* Reject treating the live-region announcement as sufficient focus handling.
  Announcement and keyboard position are separate interaction requirements.
* Reject changing validation documentation to the no-op module command. The
  generator should be executable both as a module and console entrypoint, and
  the snapshot must contain the public contracts.

## Findings and Recommendation

* Q1: Add service-boundary aware-time validation and map its `ValueError` through
  the existing HTTP validation response path. Cover direct service and HTTP calls.
* Q2: Make readability optional for unassessable text, aggregate only available
  document values, and emit the existing unavailable metric shape when none are
  available. This preserves coverage semantics.
* Q3: Add the missing `__main__` guard, regenerate the schema, and validate both
  invocation forms.
* Q4: Give the revealed approval confirmation `tabindex="-1"` and move focus to
  it before hiding the trigger. Assert the active element and announcement.

## Alternatives

* HTTP-only timestamp validation: rejected because it leaves the application
  service unsafe.
* Reject non-word content at the domain boundary: rejected because unavailable
  evidence is a defined assessment result.
* Keep only the console schema command: rejected because the documented module
  invocation should not silently succeed without running.
* Move focus to the phase heading: viable, but the revealed approval confirmation
  is more specific to the user action and resulting state.

## Risks

* Optional readability aggregation must not change scores for currently
  assessable profiles.
* API error mapping must remain explicit and must not introduce a broad catch.
* Generated schema output may be large but should change only by adding the two
  registered public models.

## Research Disposition

* Research disposition: Reused Review evidence and completed one focused wider,
  deeper, and contrarian cycle.
* Planning Readiness: Ready.
* Re-entry decision: No additional cycle. Each defect has a confirmed root cause,
  a bounded correction, and an executable regression target.
* Blockers: None.
