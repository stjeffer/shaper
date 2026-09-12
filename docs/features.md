---
title: Shaper feature guide
description: Wiki-style guide to Knowledge Estates, assessment Results, governed transformations, and lifecycle controls
ms.date: 2026-09-12
ms.topic: overview
---

## Product model

Shaper organizes related enterprise content into a **Knowledge Estate**. An estate
holds source registrations, immutable document versions, assessment evidence,
recommendations, approval decisions, transformed artifacts, and workflow history.

The product reshapes content for retrieval and agent use. It is not an
accountability or task-assignment system. Ownership can remain part of broader
estate governance, but it does not affect a document's content-readiness score,
reshaping effort, Results, or transformation actions.

## Feature status

| Capability | Current state | Product boundary |
|---|---|---|
| Knowledge Estates | Implemented | Durable, collection-scoped workspaces |
| URL and SharePoint registration | Implemented | Registration only until a connector synchronizes content |
| File and ZIP upload | Implemented | Bounded uploads with scanning and inventory controls |
| Document assessment | Implemented | 29 deterministic, read-only checks per document |
| Evidence-grounded Results | Implemented | Quoted content-quality findings that require human review |
| Full-document review | Implemented | Authorized, version-pinned normalized source viewer |
| Transformation recommendations | Implemented | Generated only for selected documents |
| Human approval | Implemented | Required before transformation and publication |
| Semantic HTML output | Implemented | Escaped, versioned, estate-owned artifacts |
| Workflow progress | Implemented | Polls durable run state until a terminal status |
| Archive and purge | Implemented | Archive is read-only; purge is permanent and confirmed |
| SharePoint synchronization | Planned | Requires Microsoft Graph consent and connector configuration |
| Score calibration | Planned | Requires representative, human-reviewed evaluation data |

## Knowledge Estate workflow

The authenticated workspace at `/concept/` presents four task-oriented stages.
The URL records the active estate and stage, so a user can return to the same
workspace context.

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

* A readiness score from 0 to 100
* Evidence coverage
* Reshaping effort in low, medium, or high bands
* The complete list of checks that ran
* Typed content findings with bounded quotes and locations
* The source version and assessment time

The score is an uncalibrated deterministic heuristic. It is not an accuracy
percentage, model confidence, or publication decision.

Discovery uses two passes. It first collects every readable document profile,
then assesses each document against the complete peer set. This allows
cross-document checks to identify unresolved references, conflicting numeric
statements, and substantially duplicated content without changing partial-run
behavior for unreadable files.

## Content-focused Results

The Assess table presents each document as a compact Fluent-style review surface.
Readiness uses a labelled progress indicator, and Results summarize the finding
count and high-priority count before the user expands them. Each finding includes
a label, explanation, severity, and content-owner review status. Expanding its
evidence reveals the exact source quote and normalized section or line location.
The responsive layout becomes document cards on narrow screens while retaining
the semantic table, labelled progress indicators, and finding lists for assistive
technology.

| Result | Detection basis | Why it matters for AI use |
|---|---|---|
| Limited metadata | Fewer than two content metadata fields | Weakens filtering and retrieval context |
| Weak structure | Missing or insufficient headings and focused sections | Makes passages harder to isolate |
| Freshness risk | Source is older than the three-year review threshold | Increases the risk of outdated answers |
| Long paragraph | A paragraph exceeds 150 words | Can reduce chunk and retrieval precision |
| Document reference | Opaque references to another policy, procedure, or standard | Hides context outside the retrieved passage |
| No question coverage | No FAQ or question-shaped content is detected | Reduces direct answer coverage |
| Implicit procedure | Procedural language lacks explicit numbered steps | Makes actions harder to extract and follow |

Seven baseline checks produce these established Results. Twenty-two additional
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
* The estate-level **Results found** total uses the same classification as each
  row, preventing the summary from disagreeing with visible Results

## Recommend

Recommendations are separate from assessment Results. Results describe what
makes the current content less suitable for AI. Recommendations describe
proposed content transformations for documents the user selects.

The recommendation stage:

* Uses the selected document IDs and the active discovery run
* Produces version-pinned proposals
* Estimates input and output token ranges
* Enforces the configured maximum before model use
* Records an append-only approve or decline decision

No recommendation grants authority to modify a source document. Approval applies
to the exact proposal and source version that the user reviewed.

## Transform and review

Only approved proposals enter transformation. The current output is escaped
semantic HTML with an estate-owned name such as
`shaper_{source_stem}.html`.

When estate evaluations are enabled, each artifact receives versioned checks for
citation coverage, structure, and validation. A second human review is required
before artifact content can be retrieved.

This two-boundary model separates:

1. Approval of the proposed content change
2. Approval of the generated output

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
