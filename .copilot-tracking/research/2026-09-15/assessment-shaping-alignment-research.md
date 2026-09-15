<!-- markdownlint-disable-file -->

# Task Research: assessment-shaping-alignment

| Field | Value |
|---|---|
| Date | 2026-09-15 |
| Researcher / agent | rpi-research |
| Status | Complete |
| Artifact path | `.copilot-tracking/research/2026-09-15/assessment-shaping-alignment-research.md` |

## Research Brief

* What to research: Whether document assessment findings, approved transformation requirements, shaping instructions, deterministic preservation validation, retry behavior, and deployed runtime versions form one coherent contract.
* Why it matters: Assessment must not approve transformations that shaping cannot faithfully produce or validation will systematically reject.
* Audience or intended use: HVE Builder authoring and validation of the Shaper transformation contract.
* Scope: `document_findings.py`, `assessment.py`, `orchestration.py`, `shaping.md`, `shaping.py`, `validation.py`, token estimation, progress errors, tests, and runtime version/deployment evidence.
* Non-goals: Changing source documents, weakening material-fact preservation, or resolving missing policy details without evidence.
* Criteria: Every assessment finding has a compatible transformation action; actions are source-supported or flag-only; validation measures preservation rather than wording identity; failures expose current actionable evidence; runtime provenance identifies stale deployments.
* Requested outputs: Converged correction recommendation with code evidence and explicit risks.
* Output mode: convergence.

## Research Parameters

| Field | Value |
|---|---|
| Research question(s) | Where do assessment, shaping, and validation conflict, and what correction makes them mutually consistent? |
| Codebase scope | Shaper assessment-to-artifact pipeline and directly related tests/docs |
| External scope | None |
| Initial internal candidate areas | Finding catalog; recommendation mapping; shaping prompt; preservation validator; deployed error strings |
| Initial external candidate areas | None |
| Research posture | focused |
| Posture provenance | default for bounded internal task with supplied failure evidence |
| Explicit limits / deadline | None |
| Posture-specific completion basis | Focused scope and materiality |
| Edits allowed during research? | No, research-only |
| Resolved evidence root | `.copilot-tracking/` |
| Known constraints / excluded sources | Preserve strict grounding and anti-invention controls; research phase is read-only |

## Extension Registry and Provenance

| Kind | Candidate | Match and provenance | Scoped authority or output contract | Selected / skipped reason |
|---|---|---|---|---|
| Instruction | HVE Builder and prompt-authoring instructions | Targets include a runtime system prompt | Prompt lifecycle and evidence gates | Selected |
| Skill | python-foundational | Python pipeline is in scope | Python correctness and type-safety criteria | Selected |
| Skill | hve-builder | User requests alignment of runtime prompt and supporting code | Improve-mode lifecycle owner | Selected as parent |
| Research specialist | None | The pipeline is bounded and tightly coupled | No independent lane needed | Skipped; inline research avoids duplicated context |

## User Participation and Research Decisions

| Checkpoint | Questions or no-interaction rationale | Answers / unanswered | Resulting decision or selected further research |
|---|---|---|---|
| Intake | Supplied error and alignment objective are sufficient | No question needed | Audit the full contract and stale-runtime evidence |
| Direction change | No material direction change yet | Not applicable | Continue focused cycle |
| Convergence | Evidence distinguishes stale deployment from remaining local contract gaps | No question needed | Select evidence-carrying, capability-safe alignment correction |

## Scope and Success Criteria

* Scope: One end-to-end contract from deterministic finding to approved action, model output, validator result, and user-visible failure.
* Assumptions: The reported four-attempt error came from a deployed revision older than the current local two-call implementation; current mappings may still contain semantic conflicts.
* Success criteria:
  * Every research question is answered or has the smallest missing evidence named.
  * Code evidence uses stable `C#` IDs and workspace-relative `path:line` locations.
  * Wider, deeper, and contrarian waves complete in order.
  * Alternatives and risks are explicit.
  * Planning readiness and self-check are recorded.

## Task Research Requests

* Explicit requests: Ensure assessment and reshaping are aligned and not working against one another.
* Inferred research questions: Which recommended actions can cause unsupported invention or validator rejection? Does the validator distinguish faithful restructuring from material loss? Does the runtime expose prompt/estimator provenance?
* Caller constraints and non-goals: Do not trade reliability for silent acceptance of lossy output.

## Direction Controls

| Control type | Direction or boundary | Provenance | Effect |
|---|---|---|---|
| add | Include deployed four-attempt error provenance | Caller error | Verify stale runtime separately from local contract |
| exclude | Do not invent missing policy facts | Existing product requirement | Flag gaps for human review |
| narrow | Assessment-to-reshaping compatibility | Caller | Avoid unrelated UI and persistence changes |

## Candidate Research Areas

| Area | Why it may matter | Initial status |
|---|---|---|
| Finding-to-action mapping | Can request semantic changes unsupported by source | Active |
| Prompt contract | Governs model interpretation of approved actions | Active |
| Preservation validator | May reject legitimate restructuring or miss semantic loss | Active |
| Retry and progress contract | Must repair exact failures rather than regenerate blindly | Active |
| Runtime provenance | Old deployment can mask corrected local behavior | Active |

## Research Questions

| ID | Question |
|---|---|
| Q1 | Do all assessment findings map to transformations that preserve source authority? |
| Q2 | Can the current validator reject changes that assessment explicitly recommends? |
| Q3 | Does repair feedback tell the model exactly what to preserve without undoing approved structure changes? |
| Q4 | How should stale runtime behavior be distinguished from current-contract failure? |

## Research Cycle Log

### Cycle 1

| Wave | Scope | Status | Reflection |
|---|---|---|---|
| Wider | Enumerate contracts and finding/action categories | Complete | The 29 checks retain bounded evidence, but transformation receives only derived action strings. |
| Deeper | Trace risky actions through prompt and validation | Complete | Three actions exceed available evidence or output capability; validation also omits common advisory, permission, and exception language covered by the prompt. |
| Contrarian | Challenge strict-preservation and action-gating alternatives | Complete | Deploy-only leaves semantic gaps; disabling validation hides loss; a new typed requirement schema is stronger but unnecessarily migratory for the immediate fix. |

## Evidence Log

| ID | Source | Evidence | Supports |
|---|---|---|---|
| C1 | `src/shaper/application/document_findings.py:18` | The assessment catalog defines seven baseline and 22 detailed checks. | Q1 |
| C2 | `src/shaper/domain/estate.py:327` | Each detailed finding retains a code, explanation, agent impact, and up to four bounded evidence quotes. | Q1, Q3 |
| C3 | `src/shaper/application/orchestration.py:94` | The transformation agent reduces findings to plain action strings. | Q1, Q3 |
| C4 | `src/shaper/application/orchestration.py:97` | Metadata generation, embedded-content conversion, and subtle-rule consolidation exceed available evidence or output capability. | Q1, Q2 |
| C5 | `src/shaper/application/shaping.py:45` | Candidate output has no metadata field. | Q1 |
| C6 | `src/shaper/domain/estate.py:423` | A proposal already pins the discovery run and report ID, so assessment evidence can be resolved without schema migration. | Q3 |
| C7 | `src/shaper/application/artifacts.py:593` | Shaping currently receives only `proposal.proposed_changes`, not the pinned report findings. | Q1, Q3 |
| C8 | `src/shaper/prompts/shaping.md:41` | The prompt requires source preservation, gap separation, no invention, and narrow repair. | Q1, Q3 |
| C9 | `src/shaper/application/validation.py:16` | Blocking operative-clause detection omits common advisory, permission, and exception markers. | Q2 |
| C10 | `src/shaper/application/shaping.py:64` | The local shaping budget is two model calls and two candidates. | Q4 |
| C11 | Repository search, 2026-09-15 | The reported four-attempt message and four-call defaults do not exist in the current checkout. | Q4 |
| C12 | `src/shaper/application/shaping.py:298` | A rejected candidate receives structured validator details and its rejected payload for targeted repair. | Q3 |

## Findings Mapped to Questions and Evidence

| Finding | Questions | Evidence | State |
|---|---|---|---|
| F1. The reported four-attempt failure is stale-runtime behavior, not current local behavior. | Q4 | C10, C11 | Evidence-backed |
| F2. Evidence-rich findings are reduced to action strings before the model call. | Q1, Q3 | C2, C3, C6, C7 | Evidence-backed |
| F3. Three current actions can require unsupported invention or semantic resolution. | Q1, Q2 | C4, C5, C8 | Evidence-backed |
| F4. The prompt promises broader preservation of permissions, exceptions, and qualifiers than blocking validation enforces. | Q2 | C8, C9 | Evidence-backed |
| F5. Targeted repair mechanics are aligned once a candidate reaches validation. | Q3 | C12 | Evidence-backed |

## Key Discoveries

* The report ID already stored in each proposal can retrieve and verify the exact assessment findings; no persistence schema change is needed.
* The primary conflict is loss of evidence and transformation-capability semantics between assessment and shaping, not strict preservation itself.
* Existing local retry corrections are valid but have not reached the Azure revision producing the caller's error.

## Alternatives and Decision State

| Alternative | Benefits | Costs / risks | Decision |
|---|---|---|---|
| Deploy current local changes only | Removes four-call loop and improves repair feedback | Leaves unsafe actions and missing assessment evidence | Rejected |
| Rewrite action strings only | Prevents the clearest invention requests | Model still lacks finding explanations and quotes; validator remains narrower than prompt | Rejected |
| Pass pinned findings, make unsafe actions flag-only, and align operative validation | Uses existing provenance, gives exact context, and preserves anti-invention controls | Adds request payload and targeted tests; prompt version advances | Selected |
| Introduce typed transformation requirement objects | Strongest long-term capability model | Requires proposal migration and wider UI/API changes | Deferred |
| Relax preservation validation | Fewer rejected candidates | Can publish lossy policy output | Rejected |

## Open Questions, Risks, and Residual Uncertainty

* Azure has not executed the selected final contract; native provider behavior and latency remain deployment-time evidence.
* Word overlap remains a deterministic proxy rather than proof of semantic equivalence.
* Embedded assets cannot be reconstructed unless extraction supplies their actual content.

## Current Decisions

* Preserve the two-call targeted repair design.
* Resolve and verify the proposal's exact discovery report before shaping.
* Include structured assessment findings in initial and repair requests.
* Convert unrepresentable or authority-changing actions to preserve-and-flag requirements.
* Expand blocking operative markers to advisory, permission, and exception language.
* Advance prompt and estimator versions together because request overhead and approved behavior change.

## Unresolved Decisions

* Typed transformation requirement capability classes are deferred; the immediate correction uses existing pinned report provenance.

## Potential Next Research

* After implementation and contained behavior validation, deploy an immutable Azure revision and verify attempt 1 of 2.
* Consider typed requirement objects if future UI needs explicit automatic-versus-human routing.

## Planning Readiness

Ready for implementation. The selected correction is bounded, uses existing proposal provenance, and has clear mechanical and behavior acceptance criteria.

## Research Disposition

Executed. Focused internal research completed one full wider/deeper/contrarian cycle and selected a converged correction.

## Artifact Self-Check

* Questions answered: Pass.
* Internal evidence has stable IDs and path/line provenance: Pass.
* Wider, deeper, and contrarian waves completed in order: Pass.
* Alternatives and rejection rationale recorded: Pass.
* Remaining uncertainty and deployment boundary recorded: Pass.

## Relevant Artifacts

| Artifact | Description |
|---|---|
| [src/shaper/application/orchestration.py](src/shaper/application/orchestration.py) | Maps assessment findings to approved transformation requirements |
| [src/shaper/prompts/shaping.md](src/shaper/prompts/shaping.md) | Runtime shaping instructions |
| [src/shaper/application/validation.py](src/shaper/application/validation.py) | Deterministic preservation gate |
| [src/shaper/application/artifacts.py](src/shaper/application/artifacts.py) | Resolves approved proposals and starts shaping |
| [src/shaper/application/document_findings.py](src/shaper/application/document_findings.py) | Evidence-rich deterministic findings |

## Next Steps

Return C1-C12 and the selected correction to the active HVE Builder parent for improve-mode authoring, static review, behavior testing, and host validation.
