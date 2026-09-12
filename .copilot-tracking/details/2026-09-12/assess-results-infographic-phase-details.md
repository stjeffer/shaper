<!-- markdownlint-disable-file -->
# RPI Phase Details: Assess Results infographic

## Metadata

* Task ID: assess-results-infographic
* Task slug: assess-results-infographic
* Related plan: .copilot-tracking/plans/2026-09-12/assess-results-infographic-plan.md
* Evidence sources: .copilot-tracking/research/2026-09-12/assess-results-infographic-research.md and caller requirements

## Phase Index

| Phase ID | Name | Status | Detail sections |
|---|---|---|---|
| P01 | Align reshaping evidence with content quality | Complete | P01, P01-T01, P01-T02 |
| P02 | Render accessible infographic Results | Complete | P02, P02-T01, P02-T02 |
| P03 | Lock behavior and validate the rendered outcome | Complete | P03, P03-T01, P03-T02 |

<!-- rpi:phase id=P01 -->
## P01: Align reshaping evidence with content quality

### Context

`DocumentAssessmentService` currently adds `missing_owner` to `finding_codes`, adds ten effort points for it, and maps it to "Add an accountable owner." Shared metadata scoring also awards 40 readiness points for ownership. `TransformationAgent.recommend()` independently maps the same code to an ownership metadata action.

### Intent

Keep per-document discovery and reshaping focused on content characteristics that affect AI use.

### Boundaries

* Included: Per-document report generation and transformation action mapping.
* Excluded: Estate-wide `MISSING_OWNER` governance findings and persisted schema changes.

### Likely Targets

* src/shaper/application/assessment.py: Remove owner-only code and imperative reason from document reporting and make metadata completeness content-only.
* src/shaper/application/orchestration.py: Remove owner-only transformation mapping.
* tests/test_assessment.py and tests/test_orchestration.py: Prove intentional semantics.

### Dependencies

* Existing content finding detectors remain unchanged.

### Validation Expectations

* Ownerless and owned equivalent profiles produce the same document report.
* Long paragraph and cross-policy findings still emit and affect effort.

### Completion Evidence

* Targeted assessment and orchestration tests pass.

### Unresolved Items

* None.

<!-- rpi:task id=P01-T01 -->
### P01-T01: Remove ownership from per-document discovery findings

#### Context

The report's effort formula counts every finding equally, and metadata completeness currently includes ownership, so merely hiding the owner label would leave distorted readiness and reshaping effort.

#### Intent

Remove `missing_owner` at its per-document report source.

#### Boundaries

* Included: `_finding_codes()`, `_reasons()`, and content-only `_metadata_score()` behavior used by assessment.
* Excluded: `AssessmentFindingKind` removal because estate-level assessment still uses it.

#### Likely Targets

* src/shaper/application/assessment.py: Delete owner emission and reason mapping.

#### Dependencies

* None.

#### Validation Expectations

* Missing owner does not change codes, reasons, readiness score, effort points, or effort band.

#### Completion Evidence

* A deterministic owner-invariance test passes.

#### Unresolved Items

* None.

<!-- rpi:task id=P01-T02 -->
### P01-T02: Remove ownership from per-document transformation actions

#### Context

The transformation agent would otherwise convert legacy `missing_owner` reports into the same unwanted action.

#### Intent

Ensure reshaping proposals remain content-focused even for historical reports.

#### Boundaries

* Included: Per-report transformation action mapping.
* Excluded: Estate-level intervention recommendations.

#### Likely Targets

* src/shaper/application/orchestration.py: Remove the `missing_owner` mapping.
* tests/test_orchestration.py: Confirm content mappings remain and ownership is ignored.

#### Dependencies

* None.

#### Validation Expectations

* A legacy report containing only `missing_owner` falls back to canonical agent-ready content rather than ownership metadata.

#### Completion Evidence

* Targeted orchestration tests pass.

#### Unresolved Items

* None.

<!-- rpi:phase id=P02 -->
## P02: Render accessible infographic Results

### Context

The table currently flattens `report.reasons` into prose. `report.finding_codes` already contains stable categories suitable for a visual result vocabulary.

### Intent

Render each supported AI-readiness problem as a compact, explanatory result item.

### Boundaries

* Included: Results heading, code-to-presentation metadata, DOM rendering, CSS, positive empty state, accountability-code filtering, and generic unknown-code state.
* Excluded: New API fields, interactive charts, tooltips that hide required meaning, and navigation redesign.

### Likely Targets

* prototype/copilot-studio-knowledge-compiler/index.html: Rename the table heading.
* prototype/copilot-studio-knowledge-compiler/app.js: Add centralized result metadata and semantic rendering.
* prototype/copilot-studio-knowledge-compiler/styles.css: Add responsive visual result styles.

### Dependencies

* `finding_codes` remains present in discovery responses.

### Validation Expectations

* Each issue is visible as an individual item with icon plus text.
* Icons are decorative and hidden from assistive technology.
* The list remains meaningful with CSS disabled.
* Accountability-only codes are ignored; unknown codes produce one generic unresolved indicator rather than an all-clear.

### Completion Evidence

* Static UI contract test and browser inspection pass.

### Unresolved Items

* None.

<!-- rpi:task id=P02-T01 -->
### P02-T01: Rename and render the Results surface

#### Context

The current supported examples map to `long_paragraph` (paragraphs over 150 words) and `cross_policy_reference`, while related codes cover structure, metadata, freshness, FAQ, and procedure gaps. A true heading-bounded section-size detector is outside current evidence.

#### Intent

Create one centralized mapping from supported finding code to concise label, explanatory detail, icon, and category.

#### Boundaries

* Included: Supported content-quality codes and positive no-issue output.
* Excluded: Owner/accountability and raw code display.

#### Likely Targets

* prototype/copilot-studio-knowledge-compiler/app.js: Render a semantic list in each Results cell.
* prototype/copilot-studio-knowledge-compiler/index.html: Change Findings to Results.

#### Dependencies

* P01 establishes authoritative content-only semantics for new reports.

#### Validation Expectations

* Long sections and document references render as distinct items.
* Historical `missing_owner` is ignored and unknown codes render as an "Additional issue detected" fallback.

#### Completion Evidence

* Static assertions cover heading, code-driven mapping, and owner exclusion.

#### Unresolved Items

* None.

<!-- rpi:task id=P02-T02 -->
### P02-T02: Style responsive and accessible result indicators

#### Context

The existing style system uses compact cards, badges, blue/amber/red accents, and responsive table scrolling.

#### Intent

Extend the visual language with a mini-card/list treatment that conveys category through icon, label, detail, and color together.

#### Boundaries

* Included: Layout, typography, icons, category accents, wrapping, and positive state.
* Excluded: Animation and interactive disclosure.

#### Likely Targets

* prototype/copilot-studio-knowledge-compiler/styles.css: Result-grid, result-item, icon, text, severity/category, and narrow-layout rules.

#### Dependencies

* Semantic DOM from P02-T01.

#### Validation Expectations

* Text and semantic grouping decide meaning; visual cues only reinforce it.
* Indicators wrap without overlap at desktop and narrow viewport widths.

#### Completion Evidence

* Browser screenshots and accessibility-tree/source inspection demonstrate the intended presentation.

#### Unresolved Items

* None.

<!-- rpi:phase id=P03 -->
## P03: Lock behavior and validate the rendered outcome

### Context

Backend semantics are covered by pytest. The repository does not have a JavaScript unit runner, so the bounded UI contract will use an existing Python static-asset test pattern plus direct browser validation.

### Intent

Use the smallest existing validation surfaces that can decide each behavior.

### Boundaries

* Included: At most two new test cases, targeted existing tests, repository lint/format checks, and browser rendering.
* Excluded: Adding new test dependencies or claiming browser reflow from static tests alone.

### Likely Targets

* tests/test_assessment.py: Owner-invariance report test.
* tests/test_architecture.py: Static prototype Results contract test.
* Existing project commands from pyproject.toml.

### Dependencies

* P01 and P02 implementation complete.

### Validation Expectations

* Backend test decides semantic behavior.
* Static test decides required source contract.
* Browser pass at 1280px, 320px, and 200% zoom decides the intended layout states. Accessibility-tree inspection verifies list semantics, row association, visible names, and decorative-icon exclusion without claiming full screen-reader conformance.

### Completion Evidence

* Commands and browser observations are recorded in the changes artifact.

### Unresolved Items

* None.

<!-- rpi:task id=P03-T01 -->
### P03-T01: Add targeted regression tests

#### Context

Existing tests already cover long paragraph and reference detection.

#### Intent

Add only missing coverage for ownership invariance and the new UI contract.

#### Boundaries

* Included: Maximum two new tests, plus extending the existing transformation-agent proposal test with the legacy owner-code assertion.
* Excluded: Duplicating existing finding-detector tests.

#### Likely Targets

* tests/test_assessment.py
* tests/test_architecture.py

#### Dependencies

* Final implementation shape.

#### Validation Expectations

* Tests fail against the old behavior and pass against the new behavior.

#### Completion Evidence

* Targeted pytest selectors pass.

#### Unresolved Items

* None.

<!-- rpi:task id=P03-T02 -->
### P03-T02: Run targeted and visual validation

#### Context

Adaptive layout, visual comprehension, semantic association, and preserved controls require a rendered check.

#### Intent

Validate code, semantics, and the actual UI at representative viewports.

#### Boundaries

* Included: Existing pytest, lint/format commands, local app serving, checks at 1280px and 320px, a 200% zoom/reflow check, and issue/empty/accountability-only/unknown result states.
* Excluded: New accessibility harness installation unless an existing command requires it.

#### Likely Targets

* pyproject.toml: Discover repository-native commands.
* Hosted prototype route: Render current assets against real or controlled data.

#### Dependencies

* Implementation and tests complete.

#### Validation Expectations

* No targeted regression.
* Results are legible, wrap correctly, and remain associated with their document row.
* Accessibility-tree inspection exposes each Results collection as a labelled list and excludes decorative icons.
* Selecting an assessed document still enables Get recommendations and the action still advances to the proposal workflow.

#### Completion Evidence

* Passing command output, screenshots for 1280px/320px/200% states, accessibility-tree observations for named result states, and successful selection/recommendation interaction are recorded.

#### Unresolved Items

* None.
