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
| Document assessment | Implemented | 29 deterministic, read-only checks per document |
| Evidence-grounded Findings | Implemented | Content-quality findings with agent impact and quoted evidence |
| Full-document review | Implemented | Authorized, version-pinned normalized source viewer |
| Transformation recommendations | Implemented | Generated only for selected documents |
| Human approval | Implemented | Required before transformation and publication |
| Semantic HTML output | Implemented | Escaped, versioned, estate-owned artifacts |
| Workflow progress | Implemented | Polls durable run state until a terminal status |
| Archive and purge | Implemented | Archive is read-only; purge is permanent and confirmed |
| SharePoint synchronization | Planned | Requires Microsoft Graph consent and connector configuration |
| Quantitative readiness calibration | Planned | Requires representative, human-reviewed evaluation data and is not shown in the Assess experience |

## Knowledge Estate workflow

The authenticated workspace at `/concept/` presents four task-oriented stages.
The URL records the active estate and stage, so a user can return to the same
workspace context.

### Estate overview and assessment catalogue

The start screen reports each estate's current, non-deleted document count and
current-version assessment coverage:

* **No documents** means the estate has no current documents to assess.
* **Not assessed** means no current document version has a matching report.
* **Partially assessed** means some, but not all, current document versions have
  matching reports.
* **Assessed** means every current document version has a matching report.

Uploading or synchronizing a new source version therefore returns the affected
estate to a partially assessed or not assessed state until discovery evaluates
that version. Historical reports do not make changed content appear current.

Each estate row has an accessible **Actions** ellipsis menu. **Edit** updates the
estate name, description, output naming convention, and evaluation preference
using optimistic concurrency. Archived estates remain read-only. **Delete**
opens the same name-confirmed, archive-then-purge safeguard used inside the
estate workspace.

The **Assessment checks** screen lists all 29 deterministic checks by category.
Each entry explains what the check looks for and its likely impact on retrieval
or agent answers. The browser loads this catalogue from the authenticated
`GET /v1/assessment-checks` contract, keeping the explanation aligned with the
implemented check set.

### Sources

Users can:

* Create a named estate with a description and output naming convention
* Register URL or SharePoint sources
* Upload individual files or bounded ZIP bundles
* Review the current document inventory
* Choose whether transformed artifacts include evaluation reports

Uploaded content enters the scanning and inventory boundary before assessment.
SharePoint entries are truthful registrations. They do not imply that Graph
synchronization has occurred.

### Discover and assess

Discovery creates a durable workflow run and a readiness report for each current
document version. The browser follows the run until it reaches `completed`,
`partial`, `failed`, or `cancelled`, then retrieves the matching reports.

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

The Assess table presents each document as a compact Fluent-style review surface.
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

Seven baseline checks produce these established Findings. Twenty-two additional
checks cover the document-quality risks below.

| Risk group | Checks |
|---|---|
| Structural and referential | External dependency, circular reference, missing referenced content, version ambiguity, orphaned amendment |
| Ambiguity | Vague quantifier, discretion clause, undefined term, unclear responsibility |
| Contradiction | Conflicting numeric value, conflicting authority, terminology drift |
| Incompleteness | Missing definitions, missing enumeration, dangling program |
| Provenance and authority | Unclear source of truth, undocumented verbal policy, restricted companion |
| Formatting and retrieval | Inconsistent heading hierarchy, inaccessible embedded content, repeated variation, noncanonical duplicate |

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
* Merges estimated input, output, and repair-and-safety contingency into one stacked bar
* Defines tokens as pieces of text the model reads and writes
* Uses the enforced maximum as the shared chart scale and processing guardrail
* States the estimate confidence and planned output filename
* Derives overhead from the active shaping prompt and response schema, then reserves
  one bounded repair attempt rather than allowing an unapproved overrun
* Requires a fresh recommendation and approval when the estimator version changes
* Enforces the configured maximum before model use
* Records an append-only approve or decline decision

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
request, while the shaping contract requires preservation of rules, duties,
permissions, prohibitions, exceptions, qualifiers, thresholds, dates,
definitions, procedure steps, escalation paths, and material examples.
Deterministic gates reject outputs with insufficient source-word coverage,
missing values or durations, or omitted operative clauses. A rejected candidate
gets at most one bounded repair attempt. If preservation still fails, the run
fails visibly and no artifact is saved.

When estate evaluations are enabled, each artifact receives versioned checks for
citation coverage, structure, and validation. A second human review is required
before publication approval.

The Outputs view places the exact normalized source version and the generated
agent-ready HTML in labelled **Before reshaping** and **After reshaping** panels.
The panels appear side by side when space permits and stack on narrow screens.
The generated preview is sandboxed, and each panel reports loading failures
independently so reviewers can still inspect the available side of the
comparison.

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
