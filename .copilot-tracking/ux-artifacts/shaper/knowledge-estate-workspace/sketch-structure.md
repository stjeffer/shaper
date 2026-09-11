<!-- markdownlint-disable-file -->
# UX Artifact: Knowledge Estate Workspace

## Artifact Context

* Project: shaper
* Subject: Knowledge Estate Workspace
* Mode: sketch-structure
* Status: partial
* Sources: Current Shaper HTML, CSS, browser rendering, live workflow behavior, and user feedback in this conversation

## Observed

* The current surface gives equal visual weight to global navigation, explanatory copy, forms, workflow steps, and data, which weakens task hierarchy.
* The global navigation presents unavailable destinations and consumes desktop space without helping users complete the active workflow.
* The estate list does not summarize estate volume, status, or evaluation configuration before users open an estate.
* The estate workflow is functionally ordered as Define, Discover, Recommend, and Transform.
* The application already exposes loading, no-access, empty, partial, failure, approval, transformation, evaluation, and publication states.

## Reported

* The product owner described the current interface as awful and requested a radical improvement.
* The product owner rejected the bespoke dark/lime redesign and requested Microsoft branding.
* Earlier direction requires a substantial live workflow rather than a demo-first interface.

## Assumed

* The primary user needs a task-focused operational workspace rather than a broad product navigation shell. Validate through direct workflow observation.
* Microsoft Fluent 2 conventions, including Segoe UI, Microsoft blue, neutral surfaces, compact controls, restrained elevation, and a 4px spacing rhythm, are the intended visual direction. Validate through product-owner review.
* Estate-level summary counts will help users choose where to work next. Validate with usage analytics and task testing.

## Unresolved

* The preferred information density for large estates has not been tested with representative production volumes.
* No supplied research establishes whether users prefer a horizontal workflow rail or persistent vertical process navigation.
* Use of any protected Microsoft corporate logo or product mark remains outside this design; Shaper retains its own product tile.

## Surface Scope

| Surface | Intended user outcome | Entry context | Source boundary |
|---|---|---|---|
| Estate portfolio | Identify an estate and understand its current configuration before opening it | Successful authenticated session with collection access | Does not cover cross-collection navigation or administration |
| Estate workspace | Move one estate through source definition, discovery, recommendation approval, transformation, evaluation, and publication review | User opens an estate from the portfolio | Does not change workflow rules, API contracts, or authorization |

## Surface Composition

| Surface | Region | Order | Content purpose | Control or content element | Visible label or affordance | Applies in state | Basis and source |
|---|---|---|---|---|---|---|---|
| All | Banner | 1 | Establish product and session context | Brand, product descriptor, environment, identity | Shaper, Knowledge operations, Live service | All | Observed in current interface |
| All | Navigation | 2 | Return to estates and explain the governed process | Portfolio link and compact process model | Knowledge estates; Define, Discover, Recommend, Transform | All | Assumed simplification of observed navigation |
| Estate portfolio | Main | 3 | Orient users around the product outcome | Outcome-led heading and primary action | Shape source content into governed knowledge; New estate | Loaded | Assumed from product purpose and current creation task |
| Estate portfolio | Main | 4 | Summarize portfolio state | Three summary measures | Total estates, Active, With evaluations | Loaded | Assumed from available estate records |
| Estate portfolio | Main | 5 | Choose an estate | Scannable estate cards with status, description, evaluation mode, revision, and update time | Open estate | Populated | Observed available record fields |
| Estate workspace | Main | 3 | Preserve context and expose current estate status | Back control, estate title, description, lifecycle badge | Back to estates; estate name; status | Loaded | Observed current behavior |
| Estate workspace | Main | 4 | Show workflow sequence and current/completed stages | Four-step workflow control | Define, Discover, Recommend, Transform | Loaded | Observed workflow and assumed completion treatment |
| Estate workspace | Main | 5 | Complete the current stage | Stage-specific panel, evidence, actions, and recovery states | Existing stage labels and controls | Stage selected | Observed current functionality |

## Interaction States

| Surface | State | Entry condition | Available controls | Information conveyed | Exit condition | Basis and source |
|---|---|---|---|---|---|---|
| Estate portfolio | Loading | Session or estate list is pending | None | Identity and access are being checked | Request succeeds or fails | Observed current behavior |
| Estate portfolio | Empty | Collection has no estates | New estate | What an estate is and how to begin | Estate created | Observed current behavior |
| Estate portfolio | Populated | One or more estates exist | New estate; open estate | Portfolio status and estate summaries | Estate opened or created | Observed data plus assumed summary |
| Estate workspace | Stage active | User opens estate or selects a stage | Stage controls and available actions | Current stage, evidence, prerequisites, and next action | User changes stage or completes action | Observed current behavior |
| Estate workspace | Stage complete | Durable evidence exists for the stage | Reopen stage | Completed progress without blocking review | Evidence changes or another stage opens | Assumed from available workflow records |
| Estate workspace | Busy | A stage mutation or load is pending | None within affected panel | Operation in progress | Request succeeds or fails | Observed current behavior |

## State Transitions

| Surface | From state | User action or event | To state | Surface change or feedback | Unresolved behavior | Basis and source |
|---|---|---|---|---|---|---|
| Estate portfolio | Empty or populated | Create estate | Estate workspace, Define | New estate becomes current and source actions appear | None | Observed current behavior |
| Estate portfolio | Populated | Open estate | Estate workspace, last requested or Define stage | Estate context and workflow evidence load | Remembering the last visited stage is undecided | Observed current behavior |
| Estate workspace | Define | Add source or upload | Define with inventory | Source count and registered-source list update | None | Observed current behavior |
| Estate workspace | Define | Select Discover | Discover | Readiness action and document evidence appear | Whether incomplete prerequisites should disable navigation is unresolved | Observed current behavior |
| Estate workspace | Discover | Request recommendations | Recommend | Proposal and token-estimate review appears | None | Observed current behavior |
| Estate workspace | Recommend | Transform approved documents | Transform | Artifact, evaluation, and review controls appear | None | Observed current behavior |

## Existing Design Intent References

| Surface | Existing record or intent identifier | Relationship to this structure |
|---|---|---|
| Estate portfolio | None | No supplied record |
| Estate workspace | None | No supplied record |

## Human Review

> [!CAUTION]
> **Disclaimer:** This agent is an assistive coaching tool only. It does not conduct user research, observe stakeholders, or speak for the people whose problems you are designing for, and it does not replace primary research, direct stakeholder contact, design review, or product and strategy decision authority. Personas, problem statements, journey maps, empathy maps, concept tests, and other Design Thinking artifacts produced with this tool are scaffolding for your own research and synthesis — not substitutes for real stakeholder voice or observed behavior. Validate all AI-generated assumptions, personas, themes, and insights against actual stakeholders before treating any Design Thinking artifact as a basis for product, design, or strategy commitments. Outputs from this tool do not constitute validated research findings or design approval.

- [ ] Reviewed and validated by a qualified human reviewer
