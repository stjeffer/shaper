<!-- markdownlint-disable-file -->
# RPI Plan: Shaper Knowledge Transformation Platform

## Task Metadata

* Task ID: shaper-knowledge-transformation-platform
* Task slug: shaper-knowledge-transformation-platform
* Planning status: Ready
* Plan date: 2026-09-10
* Phase details: .copilot-tracking/details/2026-09-10/shaper-knowledge-transformation-platform-phase-details.md
* Plan critique: .copilot-tracking/reviews/plans/2026-09-10/shaper-knowledge-transformation-platform-plan-critique.md

## Executive Summary

This plan turns the new Shaper vision into a working vertical slice rather than
only changing product copy. It adds an immutable estate assessment, explainable
Agent Readiness scoring, topic and overlap analysis, prioritized interventions,
and an authenticated REST endpoint. It also replaces the narrow compile dialog
with a four-phase Discover, Understand, Recommend, and Transform experience.

The existing answer-shaping, human review, immutable release, query, MCP, and
Azure deployment paths remain intact. They become the first execution capability
behind Transform rather than the definition of the product.

### User Decisions and Requirements Highlights

* Shaper is a Knowledge Transformation Platform that creates trusted knowledge
  for agents.
* Discover is read-only, and transformation requires human approval.
* SharePoint is a delivery surface rather than the product boundary.
* The product must assess content, understand knowledge, recommend interventions,
  and support Safe, Guided rewrite, and Knowledge consolidation modes.

### What You May Not Know

* The first Agent Readiness percentage will be a transparent deterministic
  heuristic. It will show component metrics, evidence counts, and limitations.
  It will not be described as measured enterprise accuracy until calibrated
  against a representative reviewed corpus.
* Azure AI Search remains an optional retrieval and enrichment projection. Shaper
  owns canonical decisions, review state, and knowledge assets.

### Unresolved Decisions or Blockers

* None.

For current user input, see [User Decisions and Requirements](#user-decisions-and-requirements).

## User Decisions and Requirements

* Use the supplied 2026-09-10 vision and positioning as the authoritative product brief.
* Build Shaper as an AI-powered Knowledge Transformation Platform, not a document
  editor, SharePoint web part, RAG pipeline, metadata utility, or grammar tool.
* Support a four-phase workflow: Discover, Understand, Recommend, and Transform.
* Discover must analyze an estate without modifying source content.
* Report a 0-100 Agent Readiness Score with prioritized remediation recommendations.
* Score Content Quality, Knowledge Quality, and Agent Readiness dimensions.
* Identify duplicates, stale content, missing ownership, contradictions,
  authority gaps, overlap, and business topics.
* Recommend consolidation, authority selection, archival, structure modernization,
  metadata, summaries, FAQs, procedures, knowledge packs, and canonical guidance.
* Expose Safe, Guided rewrite, and Knowledge consolidation transformation modes.
* Require human approval before publication or source-affecting actions.
* Preserve Azure-native service boundaries and support SharePoint, Copilot,
  Foundry, REST, and administrative dashboard surfaces over time.
* Treat the trusted curated canonical knowledge estate as the product outcome.

## Goals

* Establish a testable estate-level product domain above the existing compiler.
* Deliver explainable readiness analysis and actionable interventions.
* Make all four phases visible and coherent in the hosted product concept.
* Preserve existing trusted transformation and retrieval behavior.
* Document the validated MVP boundary and production Azure target.

## Scope and Non-Goals

### In Scope

* Immutable assessment domain contracts and deterministic assessment service
* Content, knowledge, and agent-readiness component metrics
* Duplicate, stale, ownership, authority, contradiction, topic, and overlap findings
* Ranked intervention recommendations and transformation modes
* Authenticated REST assessment endpoint and hosted composition
* Canonical JSON Schema generation for the new contracts
* Four-phase concept UI with sample assessment, recommendations, and mode selection
* README and deployment documentation aligned to the new product and scale-out target
* Focused unit, interface, schema, and UI validation

### Non-Goals

* Modifying or deleting source content
* Automatically declaring an authoritative source
* Production calibration of the readiness score
* New production connectors beyond existing upload and SharePoint foundations
* Provisioning Service Bus, PostgreSQL, Blob Storage, or Azure AI Search in this increment
* Replacing the compiler, review workflow, immutable release format, query, or MCP
* Claiming measured accuracy improvement

## Functional Requirements

* Accept a bounded list of normalized document profiles for estate assessment.
  * Observable acceptance criteria: authenticated callers receive one immutable
    assessment with stable identity for the same input.
* Calculate named metrics for all three readiness dimensions and disclose
  assessment coverage.
  * Observable acceptance criteria: each dimension and overall score are 0-100
    and each metric includes an explanation and evidence document IDs; the
    assessment reports available and unavailable metric counts and coverage.
* Detect candidate duplicates, stale documents, missing owners, metadata gaps,
  contradictory normalized business-term assertions, and authority gaps.
  * Observable acceptance criteria: representative inputs produce typed findings
    without silently selecting authority or changing sources; contradiction
    candidates retain assertion provenance and require review.
* Group documents into business topics and report pairwise overlap.
  * Observable acceptance criteria: topic clusters include source IDs, overlap,
    and a concise recommendation.
* Rank remediation interventions and associate supported transformation modes.
  * Observable acceptance criteria: response recommendations use the brief's
    intervention vocabulary and expose Safe, Guided rewrite, or Knowledge consolidation.
* Expose the assessment through authenticated REST.
  * Observable acceptance criteria: `/v1/assessments` requires compile access,
    validates bounded input, and returns the canonical assessment schema.
* Present the four-phase product journey in the hosted concept.
  * Observable acceptance criteria: the user can run a sample assessment, inspect
    dimensions and findings, review ranked interventions, choose a transformation
    mode, and reach an approval-ready state.

## Non-Functional Requirements

* Assessment is deterministic and side-effect free.
  * Objective threshold or evaluation condition: identical canonical inputs and
    assessment time produce identical assessment IDs and results.
  * Observable acceptance criteria: unit tests compare repeated results.
* Scores disclose their heuristic status.
  * Objective threshold or evaluation condition: every assessment contains a
    limitations statement, metric-level explanations, assessment coverage, and
    unavailable-evidence handling.
  * Observable acceptance criteria: API and UI never label readiness as accuracy
    or model confidence, and unavailable evidence never silently becomes a
    positive metric value.
* Existing behavior remains compatible.
  * Objective threshold or evaluation condition: all existing tests and schema
    checks pass without removals.
  * Observable acceptance criteria: compile, review, publish, query, MCP, health,
    and hosted concept tests remain green.
* Input is bounded.
  * Objective threshold or evaluation condition: at most 500 profiles per request,
    profile text at most 100,000 characters, and metadata at most 50 fields.
  * Observable acceptance criteria: Pydantic rejects over-limit requests.
* The UI remains keyboard operable and responsive.
  * Objective threshold or evaluation condition: semantic controls, visible focus,
    live progress, no horizontal overflow at 320 CSS pixels, and reduced-motion support.
  * Observable acceptance criteria: browser review covers desktop and narrow viewport flows.

## Acceptance Criteria

* One request demonstrates all four phases without modifying source content.
* The sample estate produces an Agent Readiness Score, three dimension scores,
  assessment coverage, explainable metrics, prioritized findings, topic clusters,
  and interventions.
* Duplicate and contradiction findings are labeled candidates for review, and
  contradiction candidates retain normalized assertion provenance.
* No algorithm treats recency alone as authority.
* Transform mode selection ends at an approval boundary and does not mutate sources.
* The new models appear in the canonical generated schema.
* Existing and new targeted tests, Ruff, strict mypy, full pytest with coverage,
  schema check, and Bicep compilation pass.
* The hosted concept is visually inspected at desktop and 320-pixel widths.
* Documentation states the product positioning, MVP limitations, and Azure scale-out path.

## Implementation Context Record

| Context item | Current artifact or record |
|---|---|
| Plan | .copilot-tracking/plans/2026-09-10/shaper-knowledge-transformation-platform-plan.md |
| Phase details | .copilot-tracking/details/2026-09-10/shaper-knowledge-transformation-platform-phase-details.md |
| Latest critique | .copilot-tracking/reviews/plans/2026-09-10/shaper-knowledge-transformation-platform-plan-critique.md, Revise findings resolved |
| Relevant research | .copilot-tracking/research/2026-09-10/shaper-knowledge-transformation-platform-research.md |
| Changes-record role | .copilot-tracking/changes/2026-09-10/shaper-knowledge-transformation-platform-changes.md is created by implementation |
| Planning execution and readiness | Complete and implementation-ready |
| Continuation context | Confirmed automatic RPI Agent continues to implementation |

## Sources

* .copilot-tracking/research/2026-09-10/shaper-knowledge-transformation-platform-research.md: selected vertical slice and evidence
* src/shaper/domain/models.py: existing canonical identity and lifecycle patterns
* src/shaper/application/ports.py: existing dependency-direction and adapter boundaries
* src/shaper/interfaces/http.py: authenticated REST composition pattern
* prototype/copilot-studio-knowledge-compiler/: hosted concept implementation
* README.md and docs/deployment.md: current product and Azure topology

## Phase Checklist

<!-- rpi:phase id=P01 -->
### [x] P01: Establish the estate assessment domain

* Intent: Add immutable, strict contracts for all four phases and a deterministic
  assessment service.
* Dependencies: Completed research artifact.

<!-- rpi:task id=P01-T01 -->
#### [x] P01-T01: Add canonical assessment contracts

* Requirement and evidence: The brief requires readiness dimensions, findings,
  topics, recommendations, and modes.
* Expected result: New strict domain models expose stable identity, bounded data,
  evidence references, score explanations, coverage, unavailable evidence, and
  limitations.
* Detail section: P01-T01 in .copilot-tracking/details/2026-09-10/shaper-knowledge-transformation-platform-phase-details.md

<!-- rpi:task id=P01-T02 -->
#### [x] P01-T02: Implement deterministic estate analysis

* Requirement and evidence: Research selected a transparent heuristic MVP.
* Expected result: One side-effect-free service calculates metrics and coverage,
  detects review-required candidates with provenance, clusters topics, and ranks
  interventions.
* Detail section: P01-T02 in .copilot-tracking/details/2026-09-10/shaper-knowledge-transformation-platform-phase-details.md

<!-- rpi:task id=P01-T03 -->
#### [x] P01-T03: Register canonical schemas and domain tests

* Requirement and evidence: New contracts must be portable and regression-safe.
* Expected result: Generated schema includes assessment models and focused tests
  cover identity, bounds, scoring, findings, recommendations, and limitations.
* Detail section: P01-T03 in .copilot-tracking/details/2026-09-10/shaper-knowledge-transformation-platform-phase-details.md

<!-- rpi:phase id=P02 -->
### [x] P02: Expose the assessment service

* Intent: Add authenticated REST access and compose the service in the hosted app.
* Dependencies: P01.

<!-- rpi:task id=P02-T01 -->
#### [x] P02-T01: Add the authenticated assessment endpoint

* Requirement and evidence: REST is an explicit product surface.
* Expected result: Compile-authorized callers can submit profiles and receive a
  canonical assessment; invalid and unauthorized input fails explicitly.
* Detail section: P02-T01 in .copilot-tracking/details/2026-09-10/shaper-knowledge-transformation-platform-phase-details.md

<!-- rpi:task id=P02-T02 -->
#### [x] P02-T02: Wire hosted composition and interface tests

* Requirement and evidence: The deployed app must expose the new service without
  regressing existing interfaces.
* Expected result: CLI composition supplies the assessment service, and focused
  HTTP tests cover success, authorization, and unavailable-service behavior.
* Detail section: P02-T02 in .copilot-tracking/details/2026-09-10/shaper-knowledge-transformation-platform-phase-details.md

<!-- rpi:phase id=P03 -->
### [x] P03: Reframe the hosted product experience

* Intent: Replace the narrow compile dialog with the four-phase platform journey.
* Dependencies: P01 semantics.

<!-- rpi:task id=P03-T01 -->
#### [x] P03-T01: Build the four-phase concept flow

* Requirement and evidence: The user supplied the complete product workflow and positioning.
* Expected result: The concept presents estate connection, assessment results,
  topic analysis, recommendations, transformation modes, and approval boundary.
* Detail section: P03-T01 in .copilot-tracking/details/2026-09-10/shaper-knowledge-transformation-platform-phase-details.md

<!-- rpi:task id=P03-T02 -->
#### [x] P03-T02: Validate accessibility and responsive behavior

* Requirement and evidence: The existing hosted concept is a user-facing product surface.
* Expected result: Keyboard, focus, live-region, reduced-motion, and 320-pixel
  viewport checks pass through browser inspection.
* Detail section: P03-T02 in .copilot-tracking/details/2026-09-10/shaper-knowledge-transformation-platform-phase-details.md

<!-- rpi:phase id=P04 -->
### [x] P04: Align product and Azure documentation

* Intent: Make the repository describe the new product boundary and scale-out target.
* Dependencies: P01-P03.

<!-- rpi:task id=P04-T01 -->
#### [x] P04-T01: Update product positioning and architecture guidance

* Requirement and evidence: Current documentation describes only an answer-unit compiler.
* Expected result: README and deployment guidance describe the four phases,
  scoring limitations, existing MVP topology, and production target services.
* Detail section: P04-T01 in .copilot-tracking/details/2026-09-10/shaper-knowledge-transformation-platform-phase-details.md

<!-- rpi:phase id=P05 -->
### [x] P05: Verify the complete increment

* Intent: Prove correctness, compatibility, generated-artifact consistency, and UI behavior.
* Dependencies: P01-P04.

<!-- rpi:task id=P05-T01 -->
#### [x] P05-T01: Run targeted and repository validation

* Requirement and evidence: Completion requires executable evidence.
* Expected result: Targeted tests, Ruff, mypy, full pytest with coverage, schema
  check, Bicep build, and browser checks pass.
* Detail section: P05-T01 in .copilot-tracking/details/2026-09-10/shaper-knowledge-transformation-platform-phase-details.md

## Dependencies

* Existing Pydantic and FastAPI stack: supplies strict contracts and REST validation.
* Existing authentication roles: the assessment endpoint reuses compile authorization.
* Existing prototype hosting: static files remain served at `/concept/`.
* Existing schema generator: new models become canonical generated artifacts.
* No new package dependencies are required.

## Test Ownership and Change Budget

* Semantic test owner: tests/test_assessment.py, new, maximum 12 focused tests.
* Interface regression owner: tests/test_interfaces.py, maximum 4 added tests.
* Schema regression owner: existing schema generation/check command and generated
  schemas/v1/domain.schema.json.
* Architecture documentation owner: README.md and docs/deployment.md.
* UI validation owner: browser inspection of the hosted static concept.
* Exact test removals: none.
* Maximum production Python additions: two new modules plus exports and composition edits.
* Maximum new dependencies: zero.

## Critique Disposition

| Critique run and finding | Disposition | Plan response or residual risk |
|---|---|---|
| PC-001 readiness coverage | resolved | Domain, API, UI, tests, and acceptance now require available and unavailable metric counts plus visible coverage |
| PC-002 contradiction scope | resolved | Requirements now limit MVP detection to normalized assertions with provenance and review-required language |

## Follow-Up Items

* Calibrate scores and thresholds against representative, human-reviewed estates;
  this requires customer evidence and an evaluation owner.
* Add production connectors and managed asynchronous processing after the shared
  assessment contract and workload shape are validated.
* Implement transformation execution for Guided rewrite and Knowledge consolidation
  after approval, provenance, and publication contracts are reviewed.

## Handoff

* Implementation artifact: .copilot-tracking/changes/2026-09-10/shaper-knowledge-transformation-platform-changes.md
* Ready phase or task: Review.
* Remaining provisional question or blocker: None.
