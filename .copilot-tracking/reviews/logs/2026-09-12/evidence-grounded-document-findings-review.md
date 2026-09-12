<!-- markdownlint-disable-file -->
# Review: Evidence-grounded document findings

## Scope and Evidence

* Task ID: evidence-grounded-document-findings
* Review date: 2026-09-12
* Review scope: Implemented P01 through P03 and P04-T01 through P04-T02
* Assessed boundary: Evidence contracts, 22 new checks, peer-aware discovery,
  source retrieval, Assess UI, tests, documentation, and local validation
* Plan: .copilot-tracking/plans/2026-09-12/evidence-grounded-document-findings-plan.md
* Phase details: .copilot-tracking/details/2026-09-12/evidence-grounded-document-findings-phase-details.md
* Plan critique: .copilot-tracking/reviews/plans/2026-09-12/evidence-grounded-document-findings-plan-critique.md
* Changes: .copilot-tracking/changes/2026-09-12/evidence-grounded-document-findings-changes.md
* Other evidence considered:
  .copilot-tracking/research/2026-09-12/evidence-grounded-document-findings-research.md,
  source diff, 175-test run, Ruff, mypy, schema, JavaScript syntax, and diff checks

## Opening Review State

* Interpreted review goal: Assess whether the implemented evidence-grounded
  document assessment is complete, usable, and safe to deploy.
* Review scope: Implemented P01 through P03 and P04-T01 through P04-T02.
* Evidence readiness: Plan, details, critique, changes, research, source, tests,
  and local validation evidence are available.
* Acceptance basis: FR01 through FR09, NFR01 through NFR06, AC01 through AC08,
  and applied critique findings PC-001 through PC-004.
* First comparison boundary: Reconcile plan markers and validation, then inspect
  the complete changed runtime boundary.
* Active read-only boundaries: Review may update only this review record.
* Initial blockers: None.

## Execution Status

* Execution status: Partial
* Review execution evidence: The implemented boundary received one complete
  review. P04-T03 remains unexecuted and two defects require later implementation.

## Plan-to-Change Reconciliation

| Current plan scope | Descriptive changes-record summary | Current-state reconciliation | Gap or rationale |
|---|---|---|---|
| P01 | Evidence contracts and heading preservation | Reconciled | Additive defaults preserve report compatibility |
| P02 | Complete detector catalog and peer-aware discovery | Reconciled | All 22 codes have representative executable coverage |
| P03 | Evidence UI and version-pinned source viewer | Partial | The viewer handler is not callable from the click listener |
| P04-T01 | Bounded tests | Partial | Endpoint denial branches and exact catalog equality are not asserted |
| P04-T02 | Documentation and local validation | Reconciled | All recorded local commands passed |
| P04-T03 | Commit, deploy, and live verification | Missing | Correctly recorded as remaining work |

## Completed Work Assessment

| Related marker | Files | What changed and why | Completion evidence | Validation | Assessment |
|---|---|---|---|---|---|
| P01 | src/shaper/domain/estate.py; src/shaper/application/estates.py | Added findings and preserved real headings | Additive models and workflow test | Tests, mypy, schema passed | Reconciled |
| P02 | src/shaper/application/document_findings.py; src/shaper/application/assessment.py; src/shaper/application/orchestration.py | Added 22 deterministic review-candidate checks | Parameterized detector test | Tests and Ruff passed | Reconciled |
| P03 | src/shaper/interfaces/http.py; prototype/copilot-studio-knowledge-compiler/ | Added source endpoint and evidence UI | Static contract and workflow tests | Syntax and Python tests passed | Gap, RV-001 |
| P04-T01 | tests/ | Added detector, workflow, and UI coverage | 175 tests passed | Passed with coverage gaps | Gap, RV-002 |
| P04-T02 | docs/features.md | Documented checks, evidence, and limitations | Current feature guide | Factual comparison completed | Reconciled |

## Implementation-Time Plan and Detail Update Assessment

| Affected area or marker | What changed and why | Triggering evidence and user decision | Reconciliation performed | Planning and critique state | Assessment |
|---|---|---|---|---|---|
| P02-T03 | Discovery became two-pass | Peer-aware checks require all readable profiles | Plan, details, and changes agree | PC-001 applied | Reconciled |
| FR09 | Exact 22-code catalog was enumerated | User supplied mandatory taxonomy | Plan and detector constant agree | PC-002 applied | Reconciled |
| P03-T01 | Retrieval requires current source version | Findings must remain tied to reviewed content | Plan, endpoint, and test agree | PC-003 applied | Reconciled |
| P01-T02 | Only real headings enter normalized text | Synthetic parser labels could affect output | Plan, details, and implementation agree | PC-004 applied | Reconciled |

## Critique and Material Revision Assessment

* Latest critique dispositions: PC-001 through PC-004 were applied.
* Material revisions: Two-pass discovery, exact catalog ownership,
  version-pinned retrieval, and real-heading-only normalization are reflected in
  the current plan and implementation.
* Dependent-work pause assessment: No evidence of work continuing before the
  critique dispositions were recorded.
* Justification assessment: Supported by research and preserved user intent.

## Plan Follow-Up Assessment

| Follow-up item | Why outside immediate scope | Owner or next action | Assessment and route |
|---|---|---|---|
| None | Not applicable | Not applicable | No plan follow-up items |

## Findings

<!-- rpi:review id=RV-001 -->
### RV-001 [High]: The full-document action calls an out-of-scope function

* Related scope: P03-T02
* Evidence: prototype/copilot-studio-knowledge-compiler/app.js defines
  `openDocument` inside `approveArtifact`, while the document click handler calls
  it from module scope.
* Impact: Selecting **View document** raises a `ReferenceError`, so content owners
  cannot inspect the complete normalized source before approving changes.
* Destination: rpi-implement
* Smallest useful next action: Move `openDocument` to module scope and add a
  browser or callable-scope regression assertion.

<!-- rpi:review id=RV-002 -->
### RV-002 [Medium]: Required endpoint and catalog contract branches lack assertions

* Related scope: P04-T01
* Evidence: The workflow test covers authorized retrieval and stale-version
  rejection, but not missing, deleted, or cross-estate documents. The detector
  test verifies 22 rows and each expected result, but not exact equality with
  `DOCUMENT_CHECK_CODES`.
* Impact: AC06 and the exact FR09 contract can regress without failing the suite.
* Destination: rpi-implement
* Smallest useful next action: Extend the existing tests with missing,
  cross-estate, deleted, and exact-catalog assertions without adding new test
  functions.

## Defects

* RV-001 routes the broken document-view action to `rpi-implement`.
* RV-002 routes missing acceptance-contract assertions to `rpi-implement`.

## Routed Findings

| Finding | Destination | Owner or next action | Reason for route |
|---|---|---|---|
| RV-001 | rpi-implement | Restore callable document-view behavior | Implementation defect |
| RV-002 | rpi-implement | Complete existing acceptance tests | Validation defect |

Later implementation of a routed finding does not require another Review.

## Residual Work

* P04-T03 remains distinct residual work: commit, deploy, and live verification
  after the routed defects are corrected.

## Blockers and Remaining Work

* Blockers: RV-001 prevents deployment because a requested workflow is broken.
* Remaining active work: P04-T03 remains pending until RV-001 and RV-002 are
  implemented and validated.

## Validation Evidence

| Command | Scope | Status | Summary |
|---|---|---|---|
| `PYTHONPATH=src uv run pytest` | Repository | Passed | 175 tests passed |
| `uv run ruff check .` | Repository | Passed | No lint findings |
| `uv run ruff format --check .` | Repository | Passed | 84 files formatted |
| `PYTHONPATH=src uv run mypy` | Repository | Passed | 84 source files checked |
| `PYTHONPATH=src uv run shaper-schema --check` | Contracts | Passed | Schema current |
| `node --check prototype/copilot-studio-knowledge-compiler/app.js` | Prototype | Passed | Syntax valid |
| `git diff --check` | Change set | Passed | No whitespace errors |
| Rendered browser workflow | Assess source viewer | Failed | RV-001 prevents the action |
| Azure health and workflow | Deployment | Skipped | Deployment blocked by RV-001 |

## Outcome

* Outcome: Defects found
* Outcome rationale: The assessment model and detector catalog are implemented
  and locally validated, but the requested source viewer is broken and acceptance
  coverage is incomplete. The change is not ready to deploy.

## Closeout Routing Record

| Finding class | Destination | Owner or next action |
|---|---|---|
| Implementation defect | rpi-implement | Correct RV-001 and RV-002 |
| Decision gap or invalid assumption | None | None |
| Material evidence gap | None | None |
| Non-blocking residual work | Follow-up | Complete P04-T03 after corrections |

* Execution status: Partial
* Outcome: Defects found
* Validation coverage: Local automated checks passed; browser workflow failed;
  deployment was skipped.
* Blockers: RV-001 blocks deployment.
