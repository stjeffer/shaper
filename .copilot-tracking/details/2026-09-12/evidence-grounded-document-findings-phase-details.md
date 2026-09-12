<!-- markdownlint-disable-file -->
# Phase Details: Evidence-grounded document findings

## P01: Preserve and model evidence

Status: Complete

Add backward-compatible evidence models to the readiness report. Preserve real
parser heading text in normalized content for future uploads. Keep table, row,
page, and block locations in structured evidence when available, but do not
inject synthetic location markers into text consumed by transformation.

Completion evidence:

* Older report JSON validates without new fields.
* New reports contain completed checks and bounded evidence objects.
* New uploads retain useful structure in stored normalized content.

## P02: Implement the complete detector catalog

Status: Complete

Build one deterministic assessment pipeline that returns structured findings.
Checks cover external and circular references, absent appendices and definitions,
version ambiguity, amendments, vague language, discretion, undefined terms,
unclear responsibility, numeric and authority conflicts, terminology drift,
missing enumerations, dangling programs, verbal policy, restricted companions,
heading hierarchy, inaccessible embedded content, repeated variation, and
noncanonical duplication.

Completion evidence:

* One parameterized test maps representative text to every code in the exact
  22-code catalog and asserts catalog equality.
* Multi-evidence findings quote both sides of a conflict.
* Discovery first collects all readable profiles, then generates reports with the
  complete peer set; unreadable documents retain partial-run behavior.
* Generic reasons and recommendation actions derive from structured findings.

## P03: Expose evidence to content owners

Status: Complete

Add an authorized endpoint for exact-version normalized document content. Reject
missing, cross-estate, deleted, and source-version-mismatched requests. Render
each finding with location, quote, explanation, and review-required wording. Add
a full-document dialog and keep selection-based recommendation approval
unchanged.

Completion evidence:

* The endpoint validates estate membership and current source version.
* Results expose evidence through semantic HTML.
* Full document content loads only after user action.
* Keyboard focus returns correctly when the dialog closes.

## P04: Validate, document, and deploy

Status: In progress. Tests, static validation, and documentation are complete.
Review, commit, deployment, and live verification remain.

Update the feature guide, run the repository-native validation suite, perform a
rendered browser pass, commit the result, build an immutable ACR image, update
the existing development Container App, and verify health and the live site.

Completion evidence:

* At most four new test functions cover detector, peer, endpoint, and ingestion
  semantics.
* Full repository validation passes.
* The deployed revision is healthy and receives 100 percent traffic.
