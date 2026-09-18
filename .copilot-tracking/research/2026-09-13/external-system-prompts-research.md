<!-- markdownlint-disable-file -->

# Task Research: external-system-prompts

| Field | Value |
|---|---|
| Date | 2026-09-13 |
| Researcher / agent | rpi-research |
| Status | Complete |
| Artifact path | .copilot-tracking/research/2026-09-13/external-system-prompts-research.md |

## Research Brief

* What to research: Locate every runtime system prompt and determine a maintainable Markdown resource and loading contract.
* Why it matters: The caller updated the shaping prompt and wants all system prompts reviewable outside Python source.
* Audience or intended use: Maintainers reviewing and versioning model instructions.
* Scope: src, tests, packaging metadata, and deployment/runtime loading.
* Non-goals: Rewriting the caller's updated prompt or changing its behavior.
* Criteria: Complete prompt inventory, preserved text, deterministic loading, packaged resources, explicit startup failure, and tests that reject inline runtime system prompts.
* Requested outputs: Converged implementation recommendation.
* Output mode: convergence.

## Research Parameters

| Field | Value |
|---|---|
| Research question(s) | Which runtime system prompts exist, and how should Markdown resources be loaded and packaged? |
| Codebase scope | src, tests, pyproject.toml, Dockerfile |
| External scope | None; Python standard-library resource loading is sufficient unless packaging evidence disproves it |
| Initial internal candidate areas | src/shaper/application/model.py, model gateway call sites, package metadata |
| Initial external candidate areas | None |
| Research posture | focused |
| Posture provenance | default for a bounded internal task with a named target |
| Explicit limits / deadline | Preserve the caller's updated prompt exactly |
| Posture-specific completion basis | Focused scope and materiality |
| Edits allowed during research? | no, research-only |
| Resolved evidence root | .copilot-tracking/ |
| Known constraints / excluded sources | Source changes deferred until research closes |

## Extension Registry and Provenance

| Kind | Candidate | Match and provenance | Scoped authority or output contract | Selected / skipped reason |
|---|---|---|---|---|
| Instruction | hve-builder.instructions.md | System-prompt artifact authoring | Prompt quality and lifecycle gates | Selected |
| Skill | hve-builder | Caller requested maintainable prompt artifacts | Parent authoring workflow | Selected |
| Skill | rpi-research | HVE Builder requires open-ended workspace exploration through this bridge | Research-only evidence | Selected |
| Research specialist | None | Bounded repository is small enough for one focused pass | None | Skipped |

## User Participation and Research Decisions

| Checkpoint | Questions or no-interaction rationale | Answers / unanswered | Resulting decision or selected further research |
|---|---|---|---|
| Intake | Caller explicitly requested Markdown externalization for every system prompt | Supplied | Preserve content and externalize all runtime system prompts |
| Direction change | None | None | No change |
| Convergence | No interaction needed for a deterministic resource-loading refactor | None | Select package resources with fail-fast loading |

## Scope and Success Criteria

* Scope: Runtime prompts, resource loader, packaging, and tests.
* Assumptions: The shaping prompt may be the only runtime system prompt; verify rather than trust.
* Success criteria:
  * Every model system-message call resolves content from a Markdown resource.
  * The caller's updated text is byte-for-byte preserved apart from the Python string delimiter/newline boundary.
  * Missing or blank prompt files fail explicitly.
  * Package and container builds include prompt resources.
  * Tests reject new inline system-prompt literals.

## Task Research Requests

* Explicit requests: Confirm the updated prompt is visible; move it and all other system prompts to Markdown.
* Inferred research questions: Find every model call, prompt constant, token estimator dependency, and packaging path.
* Caller constraints and non-goals: Do not revise the updated prompt.

## Direction Controls

| Control type | Direction or boundary | Source | Effect |
|---|---|---|---|
| add | Externalize every system prompt | Caller | Inventory all runtime model-message construction |
| narrow | Preserve updated shaping text | Caller | Refactor only; no prompt-content editing |

## Research Questions

| ID | Question | Decision impact | Status |
|---|---|---|---|
| Q1 | How many runtime system prompts exist? | Determines resource inventory | Answered |
| Q2 | Where is each prompt consumed? | Determines loader integration and tests | Answered |
| Q3 | How are package resources included at runtime? | Determines deployment-safe loading | Answered |
| Q4 | What alternative loading approaches exist? | Determines maintainability and failure behavior | Answered |

## Prior Knowledge Gate

The known shaping prompt is in src/shaper/application/model.py and is used both as the Azure OpenAI system message and inside the shaping user payload. This is verified baseline evidence, not a complete inventory. Package-resource behavior and other possible model call sites require repository evidence.

## Research Cycle Log

### Cycle 1

#### Wider wave

The runtime has one Azure OpenAI chat-completion gateway and two semantic model operations:
shaping and model-assisted evaluation. Only shaping currently has named system-prompt text.
The gateway injects that shaping prompt into both operations, so the evaluator receives an
instruction to rewrite content rather than to assess it.

#### Deeper wave

The shaping prompt is consumed three ways: as the actual system message, duplicated inside the
shaping user payload, and included in token-estimation overhead. The user-payload duplication is
unnecessary and can create prompt drift. `uv_build` includes the complete Python module tree and
its data files in wheels by default, so Markdown files under `src/shaper/prompts/` are packaged.
The Dockerfile also copies `src` into both build and runtime images.

#### Contrarian wave

Keeping one shared system prompt would minimize signature changes, but it leaves evaluation
semantically coupled to reshaping and becomes actively contradictory after the caller's update.
Reading a repository-relative file at every request would permit hot editing, but creates repeated
I/O and mid-process prompt drift. An importlib-resources loader cached per process gives deterministic
behavior in source trees and wheels and can fail explicitly for missing or blank resources.

## Evidence Log

| ID | Source | Evidence | Supports |
|---|---|---|---|
| C1 | src/shaper/application/model.py:15 | The caller-updated SHAPING_PROMPT remains inline in Python. | Q1, Q2 |
| C2 | src/shaper/application/model.py:179 | AzureOpenAIModelGateway is the located runtime chat-completion call site. | Q1, Q2 |
| C3 | src/shaper/application/shaping.py:158 | SHAPING_PROMPT is duplicated into the serialized user payload. | Q2 |
| C4 | src/shaper/application/token_estimation.py:10 | Token estimation imports the same prompt constant. | Q2 |
| C5 | src/shaper/application/evaluation.py:69 | Model-assisted evaluation calls the shared gateway without a task-specific system prompt. | Q1, Q2 |
| C6 | src/shaper/application/ports.py:90 | ModelGateway exposes only user prompt and schema, preventing operation-specific system prompts. | Q2 |
| C7 | pyproject.toml:29 | The project uses uv_build with the package rooted under src/shaper. | Q3 |
| C8 | Dockerfile:11 | The complete src tree is copied into the builder and runtime image. | Q3 |
| W1 | https://docs.astral.sh/uv/concepts/build-backend/ retrieved 2026-09-13 | uv_build wheel files include the top-level module, and package data should live under the module root. | Q3 |

## Findings Mapped to Questions and Evidence

| Question | Finding | Evidence |
|---|---|---|
| Q1 | One named system prompt exists, but two distinct runtime operations need separate system instructions. | C1, C2, C5 |
| Q2 | The prompt enters the gateway as a fixed global, is duplicated into shaping input, and cannot vary by operation through the current protocol. | C2, C3, C4, C6 |
| Q3 | `src/shaper/prompts/*.md` is a deployment-safe resource location for both wheels and the current container image. | C7, C8, W1 |
| Q4 | A cached `importlib.resources` loader with explicit errors is safer than per-call path reads or retaining inline constants. | C7, W1 |

## Key Discoveries

* The caller's prompt update is visible and currently limited to src/shaper/application/model.py.
  No source edit should normalize or rewrite it.
* Evaluation currently inherits the shaping system prompt accidentally.
* The shaping prompt is sent twice: once as the system message and again under `instructions` in
  the user JSON.
* Package-local Markdown resources are compatible with the existing uv and Docker build paths.

## Alternatives and Decision State

| Alternative | Benefits | Costs / risks | State |
|---|---|---|---|
| importlib.resources package loader | Works from wheels and source trees; explicit package ownership | Requires package-data verification | Selected |
| Path relative to __file__ | Simple | Less explicit packaging contract and harder to test as a resource API | Rejected |
| Read at each model call | Hot-editable | Repeated I/O and allows mid-process prompt drift | Rejected unless caller requests hot reload |
| Keep shaping prompt for evaluation | Smallest diff | Contradicts evaluation purpose and the updated rewriting behavior | Rejected |

## Open Questions, Risks, and Residual Uncertainty

* Adding a required `system_prompt` argument changes all test doubles; failing to update one will
  be caught by strict typing and tests.
* Markdown heading and example text become model-visible content by design.

## Current Decisions

* Preserve the caller-updated shaping prompt exactly.
* Use one cached `importlib.resources` loader rather than independent file reads.
* Add `shaping.md` and `evaluation.md` as the complete runtime system-prompt inventory.
* Make the system prompt an explicit required argument to every model-gateway call.
* Remove the duplicate shaping instructions from the user payload.

## Unresolved Decisions

None.

## Potential Next Research

No further research is needed before implementation.

## Planning Readiness

Ready. All material questions are answered and the selected architecture is supported by C1-C8
and W1.

## Closeout Record

Research disposition: executed. One focused wider/deeper/contrarian cycle completed. The selected
approach is package-local Markdown resources loaded through a cached, fail-fast resource loader.

## Advisory Next Step

Return this evidence to HVE Builder authoring. No user action is required.

## Sources

| Artifact | Description |
|---|---|
| src/shaper/application/model.py | Prompt definition and Azure OpenAI model gateway |
| src/shaper/application/shaping.py | Prompt payload assembly |
| src/shaper/application/token_estimation.py | Prompt-size dependency |
| src/shaper/application/evaluation.py | Model-assisted evaluation call site |
| src/shaper/application/ports.py | Model gateway protocol |
| pyproject.toml | uv_build package configuration |
| Dockerfile | Container source-copy contract |

## Artifact Self-Check

* Opening state is persisted.
* Wider, deeper, and contrarian waves are complete.
* Caller direction and non-goals are explicit.
* Every question is answered with evidence.
* Evidence IDs use workspace-relative paths or a dated official URL.
* The selected recommendation is explicit and alternatives are dispositioned.
