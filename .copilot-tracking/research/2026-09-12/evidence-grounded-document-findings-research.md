<!-- markdownlint-disable-file -->
# RPI Research: Evidence-grounded document findings

## Research Brief

* Topic: Expand document suitability assessment from summary reasons to evidence-grounded findings.
* Purpose: Let a content owner see what is wrong, where it occurs, the exact source text, and the proposed content correction before approval.
* Audience or use: Knowledge Estate content owners assessing newly uploaded documents.
* Scope: Existing ingestion, deterministic assessment, report persistence/API, Assess UI, recommendation approval, tests, documentation, and deployment.
* Non-goals: Autonomous policy interpretation, legal conclusions, accountability assignment, or unsupported claims that a heuristic proves a contradiction.
* Criteria: Cover every user-listed problem category; quote actual source evidence; identify a stable location; expose uncertainty; preserve human approval; avoid false all-clear states.
* Output mode: Convergence toward an implementation-ready design.
* Initial questions:
  * What source text and structure survive ingestion?
  * What report schema can carry evidence without losing compatibility?
  * Which checks can be deterministic within one document?
  * Which checks require cross-document comparison or human confirmation?
  * How should evidence appear in the current Assess and approval workflow?
* Research posture: Focused, selected from the bounded repository task and supplied failure evidence.
* Interaction: Skipped because the caller supplied the required detection catalog and target workflow.

## Extension Resolution

* Selected: Repository coding, testing, markdown, accessibility, and RPI instructions.
* Selected: Accessibility guidance for semantic evidence presentation.
* Selected: Existing assessment, estate, API, and UI contracts as primary implementation evidence.
* Skipped: External research because the requested behavior is repository-specific and the caller supplied the taxonomy.
* Skipped: Delegation because the relevant code path is a tightly coupled assessment-to-UI chain.

## Cycle 1

### Wider Wave

* C1: `src/shaper/application/estates.py:721` executes discovery synchronously in
  the request and persists a durable run, so a small deterministic document can
  complete almost instantly even though the browser supports polling.
* C2: `src/shaper/application/assessment.py:113` emits only seven per-document
  finding codes. It does not cover most of the caller's structural, ambiguity,
  contradiction, incompleteness, provenance, or retrieval taxonomy.
* C3: `src/shaper/domain/estate.py:314` stores only reasons and finding codes in a
  document report. There is no evidence quote, location, confidence, or completed
  check inventory.
* C4: `prototype/copilot-studio-knowledge-compiler/app.js:527` renders result
  labels from code-only presentation metadata. It cannot show source evidence.
* C5: `src/shaper/interfaces/http.py:494` lists document metadata but exposes no
  authorized endpoint for viewing normalized source content.

### Deeper Wave

* C6: `src/shaper/infrastructure/parsers.py:56` already creates ordered source
  spans with heading paths and PDF, block, table, and row locations.
* C7: `src/shaper/application/estates.py:683` flattens those spans into plain text
  and discards headings and locations before persistence. New uploads therefore
  lose useful structural evidence before assessment.
* C8: `src/shaper/infrastructure/sqlite.py:484` serializes readiness reports as
  complete Pydantic JSON records. PostgreSQL reuses this repository contract, so
  additive report fields with defaults do not require a relational migration.
* C9: `src/shaper/application/orchestration.py:94` maps finding codes to proposed
  transformations. New evidence-grounded codes can extend the existing
  selection, recommendation, approval, and transformation boundary.
* C10: `src/shaper/domain/assessment.py:102` bounds normalized document text at
  100,000 characters. Full-content viewing can reuse this existing limit.
* C11: `src/shaper/application/assessment.py:185` already performs estate-wide
  duplicate and contradiction analysis, but uploaded profiles contain no
  extracted assertions. Per-document evidence therefore needs bounded text
  heuristics and peer-document context rather than claiming semantic certainty.

### Contrarian Wave

* C12: Several requested conditions, including undefined terms, terminology
  drift, authority conflicts, and subtle contradiction, cannot be proven by
  regex alone. Automated output must be labelled as a review candidate and quote
  the evidence that triggered it.
* C13: Reporting an absent section or missing version marker has no literal
  offending quote. These findings need an explicit document-level location and a
  bounded opening excerpt rather than fabricated evidence.
* C14: Returning complete document text inside every discovery report would
  duplicate protected content, inflate persistence, and expose more data than
  needed. An authenticated on-demand content endpoint is safer.
* C15: Artificially delaying deterministic analysis would make progress appear
  realistic without improving assessment quality. The UI should instead state
  that bounded deterministic checks may complete quickly and show which checks
  ran.

## Findings

* The root cause of the weak experience is a code-only report contract, not only
  the visual presentation.
* The report should add structured findings containing code, label, explanation,
  review-required state, and one or more exact evidence excerpts with locations.
* Every report should record the complete check catalog so a no-finding result
  means the checks ran rather than that analysis was skipped.
* New uploads should preserve heading and table context in normalized text.
* The assessment service should accept peer profiles so external references,
  duplicate content, and numeric conflicts can consider the estate rather than
  one document in isolation.
* The UI should render evidence quotes inline and provide an authenticated,
  on-demand full-document viewer.
* Existing `finding_codes` and `reasons` should remain for compatibility and
  recommendation mapping.

## Decisions

* Treat every automated issue as a reviewable finding with evidence, not a definitive policy judgment.
* Preserve deterministic execution unless repository evidence shows an existing bounded model-analysis path is required.
* Implement the caller's complete taxonomy as bounded candidate detectors.
* Keep assessment synchronous for this task and explain that deterministic checks
  may complete quickly. Do not add fake latency.
* Use additive domain fields with defaults to preserve older persisted reports.
* Fetch complete normalized content only when the user requests it.

## Risks

* False positives from linguistic heuristics. Mitigation: candidate wording,
  exact quotes, locations, and human approval.
* False negatives for semantic contradictions. Mitigation: completed-check
  inventory and explicit limitations rather than an unsupported all-clear claim.
* Structural loss during ingestion. Mitigation: preserve heading and table
  markers for new uploads without rewriting historical source versions.
* Large UI payloads. Mitigation: bounded excerpts in reports and on-demand full
  content retrieval.

## Planning Readiness

Ready. The assessment-to-UI chain, compatibility strategy, detector boundary,
and acceptance evidence are identified.

## Research Disposition

Executed and complete after one focused wider, deeper, and contrarian cycle. A
second cycle is unnecessary because remaining uncertainty is implementation and
validation work, not missing architectural evidence.
