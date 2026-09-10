<!-- markdownlint-disable-file -->
# UX Artifact: Copilot Studio Knowledge Compiler Concept

## Artifact Context

* Project: answer-shaped-knowledge
* Subject: Copilot Studio knowledge compiler concept
* Mode: sketch-structure
* Status: complete
* Sources: In-context product concept supplied by the user on 2026-09-09, the
  repository's knowledge-compiler workflow, and Microsoft Learn's current
  "Add knowledge to an existing agent" product documentation, supplemented by
  caller-supplied screenshots of the current Build canvas and Add knowledge dialog

## Observed

* The repository models SharePoint and direct-upload sources, bounded AI shaping,
  deterministic validation, human review, immutable releases, and HTTP and MCP
  retrieval.
* The current implementation and review artifacts identify provenance, review,
  versioning, and deployment as material parts of the capability.
* Microsoft Learn shows the current agent Knowledge surface with a Knowledge
  heading, explanatory text, an Add knowledge action, source rows with Ready
  status, and an Add knowledge dialog containing upload and source choices.
* Caller-supplied screenshots show the current Build canvas with persistent left
  navigation, centered Build/Preview/Evaluate/Monitor modes, a right-side
  configuration card, and Knowledge as an expandable configuration row.
* The supplied Add knowledge dialog uses a search field, upload drop zone,
  Featured and Advanced filters, a two-column source list, and a footer-level
  Cancel action.

## Reported

* The user wants to pitch this capability to the Microsoft Copilot Studio product
  group as a potential addition to the Copilot Studio UI.
* The user wants a mock UI that demonstrates how a maker could use the capability.

## Assumed

* A maker would expect the capability near an agent's existing knowledge
  configuration. Validate this placement with the Copilot Studio product group.
* A guided four-step flow is appropriate for a pitch prototype because it makes
  compilation, review, and release governance visible. Validate the terminology
  and sequence through concept testing.
* SharePoint and file upload are appropriate primary entry choices based on the
  confirmed technical scope, not observed Copilot Studio usage data.

## Unresolved

* Whether the product surface should call the capability "Knowledge compiler,"
  "Optimize knowledge," or another product-approved term
* Whether compilation belongs inside an agent, at environment level, or within a
  reusable knowledge-source asset
* Which review roles, licensing tier, capacity model, and administrative controls
  the product group would require
* Whether versioned releases should be visible to makers or represented as
  background implementation detail

## Surface Scope

| Surface | Intended user outcome | Entry context | Source boundary |
|---|---|---|---|
| Agent knowledge workspace | Turn selected documents into governed answer-ready knowledge and attach the published release to an agent | Maker opens an agent and selects Knowledge | Concept only; does not assert current Copilot Studio information architecture |
| Evidence-unit review | Inspect generated answers, questions, qualifiers, confidence, and source evidence before approval | Compilation reaches review | Does not define enterprise approval policy |
| Publish confirmation | Understand what version is attached and what changed | All required units are approved | Does not define production licensing or capacity |

## Surface Composition

| Surface | Region | Order | Content purpose | Control or content element | Visible label or affordance | Applies in state | Basis and source |
|---|---|---|---|---|---|---|---|
| Agent knowledge workspace | Banner | 1 | Identify agent and concept status | Product title and concept badge | Copilot Studio; Product concept | All | Assumed from pitch need |
| Agent knowledge workspace | Navigation | 2 | Preserve product context | Primary agent navigation | Overview, Topics, Knowledge, Actions, Settings | All | Assumed placement |
| Agent knowledge workspace | Main | 3 | Orient the maker | Heading and four-step progress | Knowledge compiler; Connect, Shape, Review, Publish | All | Reported concept and observed workflow |
| Agent knowledge workspace | Main | 4 | Select governed input | Source-choice cards | Connect SharePoint; Upload files | Connect | Reported source requirements |
| Agent knowledge workspace | Main | 5 | Configure shaping | Instruction and control summary | Answer shaping; Guardrails on | Connect and Shape | Observed bounded-agent design |
| Agent knowledge workspace | Complementary | 6 | Explain expected value | Outcome summary | What this creates | Connect | Reported pitch purpose |
| Evidence-unit review | Main | 1 | Select a generated unit | Unit list with review status | Suggested question and status | Review | Observed answer-unit model |
| Evidence-unit review | Main | 2 | Assess answer quality | Answer, qualifiers, confidence, source spans | Answer preview; Evidence | Review | Observed validation and provenance model |
| Evidence-unit review | Main | 3 | Record human disposition | Review controls | Request changes; Approve unit; Approve all | Review | Observed human-review requirement |
| Publish confirmation | Main | 1 | Confirm immutable output | Release summary and publish control | Publish release | Publish | Observed release model |
| Publish confirmation | Status | 2 | Confirm attachment | Success message and version | Release v1 published and attached | Published | Assumed product presentation |

## Interaction States

| Surface | State | Entry condition | Available controls | Information conveyed | Exit condition | Basis and source |
|---|---|---|---|---|---|---|
| Agent knowledge workspace | Empty | No source connected | Connect SharePoint; Upload files | Supported inputs and governed output | Source selected | Reported inputs |
| Agent knowledge workspace | Ready | At least one source connected | Configure shaping; Start compilation | Source count, file count, and safety controls | Start compilation | Observed workflow |
| Agent knowledge workspace | Compiling | Compilation started | View activity | Current stage and progress | Candidate units created or failure | Observed job model |
| Evidence-unit review | Review required | Candidate units pass deterministic validation | Select unit; inspect evidence; approve or request changes | Answer, canonical questions, qualifiers, confidence, and citations | Required decisions recorded | Observed review model |
| Publish confirmation | Ready to publish | Required units approved | Publish release | Version and unit summary | Publication succeeds or fails | Observed publication model |
| Publish confirmation | Published | Immutable release and current pointer created | Open agent test panel | Release identity and attachment status | Maker leaves or tests agent | Assumed product integration |

## State Transitions

| Surface | From state | User action or event | To state | Surface change or feedback | Unresolved behavior | Basis and source |
|---|---|---|---|---|---|---|
| Agent knowledge workspace | Empty | Connect SharePoint or upload files | Ready | Source inventory and Start compilation appear | SharePoint consent UX | Reported source requirements |
| Agent knowledge workspace | Ready | Start compilation | Compiling | Progress and bounded-agent activity appear | Cancellation and retry placement | Observed hosted job design |
| Agent knowledge workspace | Compiling | Candidates pass validation | Review required | Unit list and evidence detail replace setup panel | Partial-failure presentation | Observed validation workflow |
| Evidence-unit review | Review required | Approve all required units | Ready to publish | Publish control becomes available | Delegated reviewer workflow | Observed human-review control |
| Publish confirmation | Ready to publish | Publish release | Published | Immutable version and agent attachment confirmation appear | Rollback presentation | Observed versioning; assumed UI |

## Existing Design Intent References

| Surface | Existing record or intent identifier | Relationship to this structure |
|---|---|---|
| All concept surfaces | None | No caller-supplied Design Intent Record exists |

## Human Review

> [!CAUTION]
> **Disclaimer:** This agent is an assistive coaching tool only. It does not conduct user research, observe stakeholders, or speak for the people whose problems you are designing for, and it does not replace primary research, direct stakeholder contact, design review, or product and strategy decision authority. Personas, problem statements, journey maps, empathy maps, concept tests, and other Design Thinking artifacts produced with this tool are scaffolding for your own research and synthesis — not substitutes for real stakeholder voice or observed behavior. Validate all AI-generated assumptions, personas, themes, and insights against actual stakeholders before treating any Design Thinking artifact as a basis for product, design, or strategy commitments. Outputs from this tool do not constitute validated research findings or design approval.

- [ ] Reviewed and validated by a qualified human reviewer
