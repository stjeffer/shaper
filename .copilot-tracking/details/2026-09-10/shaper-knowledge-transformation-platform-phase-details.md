<!-- markdownlint-disable-file -->
# RPI Phase Details: Shaper Knowledge Transformation Platform

## Metadata

* Task ID: shaper-knowledge-transformation-platform
* Task slug: shaper-knowledge-transformation-platform
* Related plan: .copilot-tracking/plans/2026-09-10/shaper-knowledge-transformation-platform-plan.md
* Evidence sources: .copilot-tracking/research/2026-09-10/shaper-knowledge-transformation-platform-research.md

## Phase Index

| Phase ID | Name | Status | Detail sections |
|---|---|---|---|
| P01 | Establish the estate assessment domain | Ready candidate | P01, P01-T01, P01-T02, P01-T03 |
| P02 | Expose the assessment service | Ready candidate | P02, P02-T01, P02-T02 |
| P03 | Reframe the hosted product experience | Ready candidate | P03, P03-T01, P03-T02 |
| P04 | Align product and Azure documentation | Ready candidate | P04, P04-T01 |
| P05 | Verify the complete increment | Ready candidate | P05, P05-T01 |

<!-- rpi:phase id=P01 -->
## P01: Establish the estate assessment domain

### Context

Existing contracts protect source identity and trusted answer publication, but
there is no estate aggregate. New contracts should follow the repository's
immutable strict Pydantic pattern and keep analysis upstream of compilation.

### Intent

Represent and analyze the four-phase workflow without mutating source content.

### Boundaries

* Included: Profiles, scores, assessment coverage, unavailable metrics, findings,
  topics, recommendations, modes, identity, limitations, deterministic analysis,
  tests, and generated schema.
* Excluded: Persistence, autonomous authority decisions, model evaluation,
  connector execution, and source mutation.

### Likely Targets

* src/shaper/domain/assessment.py: New immutable assessment contracts.
* src/shaper/application/assessment.py: Side-effect-free analysis service.
* src/shaper/domain/__init__.py: Public exports.
* src/shaper/schema.py: Canonical schema registration.
* tests/test_assessment.py: Semantic coverage.
* schemas/v1/domain.schema.json: Generated canonical artifact.

### Dependencies

* Existing DomainModel and canonical_hash patterns.

### Validation Expectations

* Stable identity, numeric bounds, input bounds, score aggregation, coverage,
  unavailable evidence, finding provenance, recommendation ranking, and
  limitations are tested.

### Completion Evidence

* Focused assessment tests and schema generation pass.

### Unresolved Items

* Calibration is intentionally deferred and must remain visible as a limitation.

<!-- rpi:task id=P01-T01 -->
### P01-T01: Add canonical assessment contracts

#### Context

The brief's terms must become explicit API-safe vocabulary rather than UI-only strings.

#### Intent

Define strict models for document profiles, metrics, dimensions, assessment
coverage, findings, topic clusters, recommendations, transformation modes, and
estate assessments.

#### Boundaries

* Included: Immutable fields, enums, bounds, validators, canonical version identity.
* Excluded: Storage adapters and provider-specific payloads.

#### Likely Targets

* src/shaper/domain/assessment.py: Canonical definitions.
* src/shaper/domain/__init__.py: Stable imports.

#### Dependencies

* DomainModel, Identifier, Sha256, and canonical_hash.

#### Validation Expectations

* Invalid ranges and inconsistent aggregate scores fail explicitly.

#### Completion Evidence

* Model construction and validation tests pass.

#### Unresolved Items

* None.

<!-- rpi:task id=P01-T02 -->
### P01-T02: Implement deterministic estate analysis

#### Context

The first score must be explainable and must not be confused with model confidence.

#### Intent

Compute transparent signals from profiles, build candidate findings and clusters,
and rank interventions without side effects.

#### Boundaries

* Included: Token normalization, bounded similarity, freshness, metadata, owner,
  authority, normalized business-term assertion comparisons with provenance,
  procedures, FAQs, chunks, topics, and unavailable-signal handling.
* Excluded: Claims that similarity proves duplication or that recency proves authority.

#### Likely Targets

* src/shaper/application/assessment.py: Analysis rules.

#### Dependencies

* P01-T01.

#### Validation Expectations

* Representative estates produce expected score directions, explicit coverage,
  and review-required candidate findings.

#### Completion Evidence

* Determinism and behavioral tests pass.

#### Unresolved Items

* Threshold calibration remains follow-up work.

<!-- rpi:task id=P01-T03 -->
### P01-T03: Register canonical schemas and domain tests

#### Context

The repository checks a generated schema bundle for drift.

#### Intent

Include new public contracts in schema generation and protect them with tests.

#### Boundaries

* Included: Schema generator registration and generated artifact.
* Excluded: A separate public OpenAPI package.

#### Likely Targets

* src/shaper/schema.py: Register models.
* schemas/v1/domain.schema.json: Regenerate.
* tests/test_assessment.py: Contract tests.

#### Dependencies

* P01-T01 and P01-T02.

#### Validation Expectations

* `uv run shaper-schema --check` passes after regeneration.

#### Completion Evidence

* Generated schema matches source.

#### Unresolved Items

* None.

<!-- rpi:phase id=P02 -->
## P02: Expose the assessment service

### Context

HTTP composition already injects optional services and enforces collection roles.

### Intent

Expose assessment as an authenticated first-class service without coupling it to storage.

### Boundaries

* Included: Request validation, compile-role authorization, service injection, JSON response.
* Excluded: New auth roles, asynchronous jobs, persisted assessment history.

### Likely Targets

* src/shaper/interfaces/http.py: Endpoint and service dependency.
* src/shaper/interfaces/cli.py: Hosted service composition.
* tests/test_interfaces.py: Interface behavior.

### Dependencies

* P01.

### Validation Expectations

* Success, unauthorized role, invalid bounds, and unavailable service return explicit results.

### Completion Evidence

* Targeted interface tests pass and OpenAPI includes the endpoint.

### Unresolved Items

* None.

<!-- rpi:task id=P02-T01 -->
### P02-T01: Add the authenticated assessment endpoint

#### Context

Assessment is a write-like compute operation over governed collection content, so
the existing compile role is the least-surprising authorization boundary.

#### Intent

Add `POST /v1/assessments`.

#### Boundaries

* Included: Collection role check, strict request model, assessment response.
* Excluded: Anonymous sample endpoint.

#### Likely Targets

* src/shaper/interfaces/http.py: Request and route.

#### Dependencies

* P01.

#### Validation Expectations

* Permission and validation failures map to appropriate HTTP status codes.

#### Completion Evidence

* Endpoint contract tests pass.

#### Unresolved Items

* None.

<!-- rpi:task id=P02-T02 -->
### P02-T02: Wire hosted composition and interface tests

#### Context

The hosted CLI is the current production composition root.

#### Intent

Supply a stateless `EstateAssessmentService` and preserve all existing services.

#### Boundaries

* Included: Service construction and readiness-neutral injection.
* Excluded: New Azure resources.

#### Likely Targets

* src/shaper/interfaces/cli.py: Composition.
* tests/test_interfaces.py: HTTP behavior.

#### Dependencies

* P02-T01.

#### Validation Expectations

* Combined HTTP and MCP lifespan test remains green.

#### Completion Evidence

* Interface tests pass.

#### Unresolved Items

* None.

<!-- rpi:phase id=P03 -->
## P03: Reframe the hosted product experience

### Context

The current concept only connects one source, compiles answer units, reviews, and publishes.

### Intent

Show estate-level value before transformation and align the UI with the product brief.

### Boundaries

* Included: Static sample estate, assessment animation, score dimensions,
  coverage, findings, topics, recommendations, mode choice, approval boundary,
  and responsive UI.
* Excluded: Calling the authenticated API from the unauthenticated static concept.

### Likely Targets

* prototype/copilot-studio-knowledge-compiler/index.html: Semantic experience.
* prototype/copilot-studio-knowledge-compiler/styles.css: Visual system and responsiveness.
* prototype/copilot-studio-knowledge-compiler/app.js: Four-phase state flow.

### Dependencies

* P01 vocabulary.

### Validation Expectations

* Desktop and 320-pixel flows complete with keyboard-accessible controls and no errors.

### Completion Evidence

* Browser snapshots and interaction checks.

### Unresolved Items

* None.

<!-- rpi:task id=P03-T01 -->
### P03-T01: Build the four-phase concept flow

#### Context

The UI must show visibility and recommendations before any content changes.

#### Intent

Create a coherent demo from source estate to approval-ready intervention.

#### Boundaries

* Included: Sample data, deterministic display values, visible coverage, and
  review-required candidate language clearly presented as a concept.
* Excluded: Fabricated production measurement claims.

#### Likely Targets

* prototype/copilot-studio-knowledge-compiler/index.html
* prototype/copilot-studio-knowledge-compiler/styles.css
* prototype/copilot-studio-knowledge-compiler/app.js

#### Dependencies

* P01 terminology.

#### Validation Expectations

* All four phases are reachable and understandable.

#### Completion Evidence

* Browser interaction succeeds.

#### Unresolved Items

* None.

<!-- rpi:task id=P03-T02 -->
### P03-T02: Validate accessibility and responsive behavior

#### Context

The concept must support keyboard and narrow viewport use.

#### Intent

Apply semantic controls, focus management, live status, reduced motion, contrast,
and reflow expectations.

#### Boundaries

* Included: WCAG-oriented inspection appropriate to the static concept.
* Excluded: Formal certification.

#### Likely Targets

* prototype/copilot-studio-knowledge-compiler/

#### Dependencies

* P03-T01.

#### Validation Expectations

* Keyboard flow, visible focus, live announcements, reduced motion, and 320-pixel reflow.

#### Completion Evidence

* Browser inspection records no blocking issue.

#### Unresolved Items

* None.

<!-- rpi:phase id=P04 -->
## P04: Align product and Azure documentation

### Context

README currently defines Shaper as an answer-ready evidence compiler, and the
deployment guide documents only the bounded development topology.

### Intent

Explain the product, current vertical slice, scoring caveat, and production target.

### Boundaries

* Included: Positioning, workflow, current capabilities, target components, and deferred scale work.
* Excluded: Claiming unprovisioned services are deployed.

### Likely Targets

* README.md: Product and local usage.
* docs/deployment.md: Current versus target Azure topology.

### Dependencies

* P01-P03.

### Validation Expectations

* Documentation clearly distinguishes current implementation from target architecture.

### Completion Evidence

* Manual documentation review.

### Unresolved Items

* None.

<!-- rpi:task id=P04-T01 -->
### P04-T01: Update product positioning and architecture guidance

#### Context

Repository documentation must stop presenting answer units as the entire product.

#### Intent

Describe Knowledge Transformation Platform semantics and Azure evolution.

#### Boundaries

* Included: README and deployment updates.
* Excluded: New architecture decision record.

#### Likely Targets

* README.md
* docs/deployment.md

#### Dependencies

* Implemented behavior.

#### Validation Expectations

* Claims match the implementation and deployed-resource reality.

#### Completion Evidence

* Documentation is internally consistent.

#### Unresolved Items

* None.

<!-- rpi:phase id=P05 -->
## P05: Verify the complete increment

### Context

The change spans domain, API, schemas, UI, and documentation.

### Intent

Verify the exact acceptance criteria and prevent regressions.

### Boundaries

* Included: Existing repository commands and browser tools.
* Excluded: New test frameworks or production deployment.

### Likely Targets

* Full changed surface.

### Dependencies

* P01-P04.

### Validation Expectations

* Targeted tests, Ruff, strict mypy, full pytest with coverage, schema check,
  Bicep compile, and browser interaction all pass.

### Completion Evidence

* Command results and browser snapshots are recorded in the changes artifact.

### Unresolved Items

* None.

<!-- rpi:task id=P05-T01 -->
### P05-T01: Run targeted and repository validation

#### Context

Validation must cover semantics, regression, generation, infrastructure, and UI.

#### Intent

Produce executable completion evidence.

#### Boundaries

* Included: Existing commands only.
* Excluded: Live Azure deployment unless a defect requires it.

#### Likely Targets

* tests/, schemas/v1/domain.schema.json, bicep/main.bicep, and hosted concept.

#### Dependencies

* All implementation tasks.

#### Validation Expectations

* No failing validation attributable to the change.

#### Completion Evidence

* Recorded pass results.

#### Unresolved Items

* None.
