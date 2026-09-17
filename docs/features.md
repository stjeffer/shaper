---
title: Shaper feature guide
description: Wiki-style guide to Knowledge Estates, assessment Findings, governed transformations, and lifecycle controls
ms.date: 2026-09-12
ms.topic: overview
---

## Product model

Shaper organizes related enterprise content into a **Knowledge Estate**. An estate
holds source registrations, immutable document versions, assessment evidence,
recommendations, approval decisions, transformed artifacts, and workflow history.

The product reshapes content for retrieval and agent use. It is not an
accountability or task-assignment system. Ownership can remain part of broader
estate governance, but it does not affect Findings or transformation actions.

## Feature status

| Capability | Current state | Product boundary |
|---|---|---|
| Knowledge Estates | Implemented | Durable, collection-scoped workspaces |
| URL and SharePoint registration | Implemented | Registration only until a connector synchronizes content |
| File and ZIP upload | Implemented | Bounded uploads with scanning and inventory controls |
| Individual document removal | Implemented | Excludes a document from future workflows while retaining source provenance |
| Document assessment | Implemented | 31 deterministic, read-only checks per document |
| Evidence-grounded Findings | Implemented | Content-quality findings with agent impact and quoted evidence |
| Full-document review | Implemented | Exact original-file download plus an authorized, version-pinned extracted-text viewer |
| Transformation recommendations | Implemented | Generated only for selected documents |
| Human approval | Implemented | Required before transformation and publication |
| Semantic HTML output | Implemented | Escaped, versioned, estate-owned artifacts |
| Workflow progress | Implemented | Polls durable run state until a terminal status |
| MCP workflow access | Implemented | Findings, proposals, decisions, one-document transformations, artifact approval, exact HTML, and evaluation questions |
| Archive and purge | Implemented | Archive is read-only; purge is permanent and confirmed |
| SharePoint synchronization | Planned | Requires Microsoft Graph consent and connector configuration |
| Quantitative readiness calibration | Planned | Requires representative, human-reviewed evaluation data and is not shown in the Assess experience |

## Knowledge Estate workflow

The authenticated workspace at `/concept/` presents four task-oriented stages.
The URL records the active estate and stage, so a user can return to the same
workspace context.

The authenticated MCP endpoint at `/mcp/` exposes the same application
services for agent and automation clients. Binary uploads remain on the
authenticated REST endpoint so file-size, malware-scanning, ZIP-expansion, and
source-retention controls are not duplicated in tool arguments. See
[Use Shaper through MCP](mcp.md) for setup, tool contracts, examples, and
testing.

### Estate overview and assessment catalogue

The start screen reports each estate's current, non-deleted document count and
current-version assessment coverage:

* **No documents** means the estate has no current documents to assess.
* **Not assessed** means no current document version has a matching report.
* **Assessed** with a partial coverage count means some, but not all, current
  document versions have matching reports.
* **Assessed** means every current document version has a matching report.

Uploading or synchronizing a new source version therefore reduces the displayed
assessment coverage, or returns the estate to **Not assessed**, until discovery
evaluates that version. Historical reports do not make changed content appear
current.

Each estate row has an accessible **Actions** ellipsis menu. **Edit** updates the
estate name, description, output naming convention, and evaluation preference
using optimistic concurrency. Archived estates remain read-only. **Delete**
opens the same name-confirmed, archive-then-purge safeguard used inside the
estate workspace.

The **Assessment checks** screen groups all 31 deterministic checks into
keyboard-operable category tabs so reviewers can inspect one focused group at a
time. Each entry explains what the check looks for and its likely impact on
retrieval or agent answers. The browser loads this catalogue from the
authenticated `GET /v1/assessment-checks` contract, keeping the explanation
aligned with the implemented check set.

### Sources

Users can:

* Create a named estate with a description and output naming convention
* Switch between accessible **URL or SharePoint** and **File upload** tabs
* Register URL or SharePoint sources
* Upload individual files or bounded ZIP bundles
* Review the current document inventory
* Remove an individual document from future assessment and improvement planning
* Choose whether the current transformation run tries one automatic repair from
  preservation findings

Document rows show only a concise format label such as **PDF**, **DOCX**,
**Markdown**, or **Text**. Raw MIME types and modification timestamps remain
available as source metadata but do not clutter the inventory.

Each active document row includes a named **Remove** action with a confirmation
dialog. Removal clears current browser selections and assessment evidence so
stale findings cannot be reused. The document is excluded from future
assessment and improvement planning, while its immutable source provenance and
existing generated artifacts remain available for governance. Archived estates
are read-only. Permanent content deletion remains an estate-level purge.

Assessed document rows keep only the finding count, highest urgency, and review
action visible. On wide screens, **Review findings** opens a dedicated inline
detail panel beside the document list. On narrow screens, the same complete
finding explanations, agent impact, evidence, and review requirements open in a
modal detail view rather than expanding the table row vertically.

SharePoint registrations record whether synchronization should use the signed-in
user's delegated access or an organization-managed application connection.
Application credentials are configured by an administrator outside the browser;
Shaper never asks a content owner to paste a client secret into the source form.

On wider screens, source input occupies the left half of the Sources workspace
and the registered-source list occupies the right half. The columns stack on
narrow screens. Registered web locations display their user-facing URL.
Uploaded files display a readable source type without exposing their internal
opaque asset or blob-storage identifier.

The left navigation rail uses labelled, consistent line icons for creating a
knowledge estate and opening the assessment-check catalogue. Internal
environment indicators and opaque identity fragments are not shown because
they do not help people complete either task.

The workspace uses native semantic HTML controls styled by local design tokens.
The fixed dark theme uses a near-black canvas, layered charcoal surfaces, a
cyan accent, and lime completion highlights with Segoe UI and system-font
fallbacks. Local CSS defines control density, radii, interaction states, visible
focus, and responsive behavior. No runtime web-component bootstrap or public
CDN is required.

Action controls use native buttons, links, fields, selects, checkboxes, tabs,
dialogs, and disclosure elements with explicit accessible names and states.
Interface symbols are locally packaged Microsoft Fluent System Icons under the
upstream MIT license; text glyphs and emoji are not used as control icons.

The shell uses comfortable spacing for navigation and forms, with compact rows
for estate and findings data. Charcoal layers define panels, inputs, and data
surfaces. Cyan marks interactive focus and primary actions, while lime indicates
successful or completed states. Ordinary cards remain flat; elevation is limited
to menus and modal dialogs. Tabs use a borderless treatment and accent selection
indicator instead of outlining every tab.

Uploaded content enters the scanning and inventory boundary before assessment.
SharePoint entries are truthful registrations. They do not imply that Graph
synchronization has occurred.

### Discover and assess

Discovery creates a durable workflow run and a readiness report for each current
document version. The browser follows the run until it reaches `completed`,
`partial`, `failed`, or `cancelled`, then retrieves the matching reports.
Discovery runs for estates containing one document as well as larger estates.
Document checkboxes remain available before discovery; they select which
assessed documents proceed to recommendations rather than limiting discovery.

Each report contains:

* Evidence coverage
* The complete list of checks that ran
* Typed content findings with plain-language agent impact, bounded quotes, and
  locations
* The source version and assessment time

Internal deterministic metrics support compatibility and bounded processing,
but the Assess experience does not present readiness or reshaping effort as a
score.

Discovery uses two passes. It first collects every readable document profile,
then assesses each document against the complete peer set. This allows
cross-document checks to identify unresolved references, conflicting numeric
statements, and substantially duplicated content without changing partial-run
behavior for unreadable files.

## Content-focused Findings

The Assess table presents each document as a compact native-control review surface.
Findings summarize the count and high-priority count before the user expands
them. Each finding includes a label, a plain-language description, an explicit
explanation of the impact on agent responses, severity, and content-owner review
status. Expanding its evidence reveals the exact source quote and normalized
section or line location. The responsive layout becomes document cards on narrow
screens while retaining the semantic table and finding lists for assistive
technology.

| Finding | Detection basis | Why it matters for AI use |
|---|---|---|
| Limited metadata | Fewer than two content metadata fields | Weakens filtering and retrieval context |
| Weak structure | Missing or insufficient headings and focused sections | Makes passages harder to isolate |
| Freshness risk | Source is older than the three-year review threshold | Increases the risk of outdated answers |
| Long paragraph | A paragraph exceeds 150 words | Can reduce chunk and retrieval precision |
| Document reference | Opaque references to another policy, procedure, or standard | Hides context outside the retrieved passage |
| No question coverage | No FAQ or question-shaped content is detected | Reduces direct answer coverage |
| Implicit procedure | Procedural language lacks explicit numbered steps | Makes actions harder to extract and follow |

Seven baseline checks produce these established Findings. Twenty-four additional
checks cover the document-quality risks below.

| Risk group | Checks |
|---|---|
| Structural and referential | External dependency, circular reference, missing referenced content, version ambiguity, orphaned amendment |
| Ambiguity | Vague quantifier, discretion clause, undefined term, unclear responsibility |
| Contradiction | Conflicting numeric value, conflicting authority, terminology drift |
| Incompleteness | Missing definitions, missing enumeration, dangling program |
| Provenance and authority | Unclear source of truth, undocumented verbal policy, restricted companion |
| Formatting and retrieval | Inconsistent heading hierarchy, inaccessible embedded content, repeated variation, noncanonical duplicate |
| Unsafe source instruction | Source-authored AI directive, unsupported comparative claim |

These checks identify review candidates. They do not prove legal meaning,
authority, or semantic contradiction. A content owner must inspect the quoted
evidence and source context before approving a proposed change.

### Review the source content

Select **View document** from an assessment row to open the complete normalized
source used by the check. The request includes the report's exact source version.
Shaper rejects a stale version, a deleted or missing document, and a document
outside the authorized estate. Content loads only after the user requests it and
is not copied into every assessment report.

The viewer preserves real headings for newly uploaded documents. Synthetic PDF
page, block, table, and row labels are not inserted into transformation input.

The interface also handles compatibility cases:

* A report with no supported content issues shows **No content issues detected**
* Legacy `missing_owner` findings are ignored because they are accountability
  signals, not content-shaping results
* One or more unknown future codes produce one **Additional issue detected**
  card per document
* The estate-level **Findings found** total uses the same classification as each
  row, preventing the summary from disagreeing with visible Findings

## Recommend

Recommendations are separate from assessment Findings. Findings describe what
makes the current content less suitable for AI. Recommendations describe
proposed content transformations for documents the user selects.

The recommendation stage:

* Uses the selected document IDs and the active discovery run
* Produces version-pinned proposals
* Leads with a per-document summary of all 31 deterministic checks, including
  which checks need attention and which passed
* Shows failed-check explanations and likely agent impact before the proposed
  changes
* Lists every passed check in an on-demand review section
* Presents the assessment-backed improvement actions and review constraint as
  the primary decision information
* Merges estimated input, output, and repair-and-safety contingency into one stacked bar
* Defines tokens as pieces of text the model reads and writes
* Uses the enforced maximum as the shared chart scale and processing guardrail
* States the estimate confidence and planned output filename
* Derives overhead from the active shaping prompt and response schema, then reserves
  an initial candidate and one targeted repair rather than allowing an unapproved
  overrun
* Loads shaping and model-assisted evaluation instructions from separate,
  version-controlled Markdown resources packaged with the application
* Binds approval to the shaping prompt hash and estimator version
* Requires a fresh recommendation and approval when either contract changes
* Enforces the configured maximum before model use
* Records an append-only approve or decline decision

The action is labelled **Create improvement plan** rather than implying that
token estimation is the recommendation. Token usage is supporting information
in a collapsed section beneath the assessment results and recommended changes.
Activating the action moves to the review step immediately and exposes a live,
inline progress state. Completion reports how many plans are ready; stale or
missing discovery evidence produces an actionable error instead of an empty
approval screen.

Completed improvement plans collectively offer up to 20 distinct,
content-grounded evaluation questions before output evaluation is enabled. Shaper
samples substantive passages across the estate and balances the selection across
documents. It returns fewer questions when the available knowledge cannot support
20 without duplication. Short labels and fragments below the substantive-passage threshold do not become
filler questions. Reviewers can include or exclude individual cases and
prepare either Microsoft Foundry JSONL using the standard `query`,
`ground_truth`, and `context` columns, or a Copilot Studio single-response CSV
using `question` and `expectedResponse`. Suggested keywords remain visible in
Shaper so reviewers can configure keyword-match evaluation after import.
Expected answers are derived from version-pinned source passages and remain
marked for subject-matter review. The UI names suitable Foundry evaluator
dimensions or Copilot Studio test methods without claiming that a generated case
has already been validated.

The approval workspace separates **Assessment results** and **Evaluation set**
into keyboard-operable tabs. Assessment findings and proposed transformations
remain the default view; evaluation drafts have a dedicated view instead of
adding length above every assessment result.

Transformation controls appear above both review tabs so reviewers receive
immediate feedback after activation. While approved content is transformed, a
live progress surface names the complete-content, source-preservation,
grounding, and optional repair stages and reports their actual
results as the service completes each stage.

After approval, the proposal card changes to an explicit **Transformation
approved** state, shows that the document is ready to transform, and disables
duplicate approval. The transformation action becomes available immediately.

No recommendation grants authority to modify a source document. Approval applies
to the exact proposal and source version that the user reviewed.

See the
[governed transformation diagram](architecture.md#governed-transformation-and-token-budget)
for the estimate, approval, preflight, shaping, and artifact boundaries.

## Transform and review

Only approved proposals enter transformation. The current output is escaped
semantic HTML with an estate-owned name such as
`shaper_{source_stem}.html`.

Transformation reshapes the complete source document; it does not replace the
source with a summary. The approved recommendations are included in the shaping
request together with the exact proposal-pinned assessment findings. Findings
explain the detected condition, likely agent impact, and supporting source
evidence. They are diagnostic context, not permission to edit. Only the approved
recommendations authorize transformations. For the two unsafe-source findings,
an approved recommendation can authorize omission only of the exact
fragment-level finding evidence from the exact report and current source version.
The candidate must add the canonical intentional-exclusion review note, and may
not retain that text as substantive policy. Any other omission remains a
preservation finding for human review.

Actions that require unavailable authority remain flag-only. Shaper preserves
the source instead of inventing missing metadata or definitions, deciding that
different terms are equivalent, recreating inaccessible embedded content, or
consolidating subtly different repeated rules. Safe approved actions can
restructure headings, sections, grounded questions and answers, and
source-supported procedures.

When unresolved gaps must remain visible, the generated document appends one
final **Missing information and review notes** section. Source identifiers,
evidence scores, confidence scores, validation scores, and machine status
annotations do not appear in the human-facing answer. Preservation checks treat
that final section as review context rather than policy even when its formatting
is imperfect. Review-note structure and policy wording remain visible as diagnostic warnings
without cascading into unrelated policy findings. Invented values, identifiers,
duties, permissions, prohibitions, and policy-bearing temporal restrictions in
the substantive document become clear preservation findings with source evidence.

The shaping contract requires preservation of rules, duties, advisory language,
permissions, prohibitions, exceptions, qualifiers, thresholds, dates,
definitions, procedure steps, escalation paths, and material examples.
Deterministic analysis detects outputs with missing values or durations and checks
each operative category independently. Structural list, step, and question
numbers are not treated as policy facts. Clause matching follows source-specific
identity words, values, controls, and qualifiers instead of relying on original
clause position. This permits faithful Q&A, list, and procedure restructuring
while reporting values, modal strength, polarity, or qualifiers moved between
subjects. Low source-word coverage remains visible as review evidence and
does not reject a faithful clearer rewrite by itself. Generic lexical
material-clause similarity is also advisory. Qualifier preservation requires
policy context, so rhetorical uses of
words such as "once" or "within" do not create false temporal findings.

The default run retains an integrity-valid artifact for review even when
preservation findings remain. Selecting **Try one automatic repair from
preservation findings** makes one bounded repair attempt for that run. Source
identity, source version, cited evidence, candidate schema, exclusion authority,
and retained intentionally excluded content remain non-bypassable. A missing
exclusion audit note remains a review finding instead of blocking artifact
generation. Publication requires acknowledgment of every finding stored on the
current artifact.

The Azure OpenAI request is bounded by a 90-second timeout and an output-token
limit from the approved estimate. The common path therefore uses one model call;
a second call occurs only for a targeted preservation repair.

The output card presents findings in clear language beside the before-and-after
comparison. It does not present a score out of 100. Human review remains required
before publication approval.

The Outputs view places the complete extracted text from the exact retained
source version and the generated agent-ready HTML in labelled **Before
reshaping** and **After reshaping** panels.
The panels appear side by side when space permits and stack on narrow screens.
The generated preview is sandboxed, and each panel reports loading failures
independently so reviewers can still inspect the available side of the
comparison.

After publication approval, the Outputs view exposes **Export approved HTML**.
The authenticated download returns the exact stored artifact bytes with the
estate-governed filename rather than serializing the styled browser preview.
Unapproved candidates remain unavailable for export.

This two-boundary model separates:

1. Approval of the proposed content change
2. Approval of the generated output

The [assessment evidence diagram](architecture.md#assessment-evidence-architecture)
shows how source evidence becomes findings before this transformation workflow
begins.

## Workflow progress and recovery

Discovery, recommendation, and transformation are represented as durable runs.
The workspace polls `/v1/estates/{estate_id}/runs` and announces state changes.
Busy regions expose `aria-busy`, while terminal failures remain visible rather
than appearing successful.

Refreshing an estate reloads:

* Current sources and document versions
* The latest completed or partial discovery reports
* The latest recommendation proposals
* Current decisions and transformed artifacts
* Workflow completion indicators

## Estate lifecycle

An active estate accepts source, assessment, recommendation, and transformation
changes. Archiving makes the estate read-only and enables permanent purge.

Purge requires:

* An archived estate
* The exact confirmation phrase `PURGE {estate name}`
* A recorded reason

The lifecycle panel supports an explicit archive-then-purge flow. The
name-confirmed **Delete estate** action performs the same archive-first sequence
as a single user operation. Purge removes estate content and retains the
repository's audit tombstone.

> [!CAUTION]
> Purge cannot be undone. Apply organizational retention, privacy, and records
> requirements before using it.

## Security and governance boundaries

* HTTP and MCP access require configured identity and collection-scoped roles
* Source versions, proposals, decisions, and artifacts retain evidence lineage
* Uploaded files must pass the configured scanning boundary
* The shaping capability has no arbitrary shell, filesystem, permission, review,
  or publication authority
* Output publication remains a human decision

See [platform architecture](architecture.md), [deployment guidance](deployment.md),
[operations guidance](operations.md), and
[improvement reporting](improvement-reporting.md) for deeper technical detail.

## Current limitations

* Assessment thresholds are deterministic defaults, not calibrated quality claims
* Every evidence-grounded finding is a deterministic review candidate, not a
  proven semantic or legal conclusion
* Historical versions do not gain preserved heading context unless they are
  uploaded again
* Scanned PDFs without extractable text can fail ingestion before embedded-content
  checks can run
* SharePoint content synchronization is not complete without Graph integration
* Confluence, ServiceNow, arbitrary wiki crawling, and distributed specialist
  workers remain planned work

---

This documentation was materially shaped with AI assistance and requires human
review before external publication.
