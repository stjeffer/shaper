<!-- markdownlint-disable-file -->
# Task Research: multi-source-shaper-requirements

| Field | Value |
|---|---|
| Date | 2026-09-10 |
| Researcher / agent | rpi-research |
| Status | In progress |
| Artifact path | .copilot-tracking/research/2026-09-10/multi-source-shaper-requirements-research.md |

## Research Brief

* What to research: Audit the deployed Shaper implementation and concept against
  the caller's exact input and output capability lists.
* Why it matters: The next product definition must not narrow, rename, or omit
  any caller-required source or knowledge asset.
* Audience or intended use: Product planning, architecture, implementation, and
  a product-group pitch.
* Scope: Existing source kinds, parsers, connectors, shaping models, publication
  formats, API and MCP surfaces, prototype copy, and planning evidence.
* Non-goals: Source-code changes, connector implementation, UI implementation,
  production activation, and measured accuracy claims.
* Criteria: Every exact caller term appears in a traceable capability matrix;
  current coverage and gaps are distinguished; overlaps are normalized without
  deleting caller language; outputs have planning-ready semantic contracts.
* Requested outputs: Exact requirements baseline, coverage audit, gap analysis,
  architecture implications, risks, and planning readiness.
* Output mode: convergence.

## Research Parameters

| Field | Value |
|---|---|
| Research questions | What exists, what is missing, and what contracts preserve the exact input and output list? |
| Codebase scope | src/shaper/, prototype/, schemas/, docs/, tests/, and existing RPI artifacts |
| External scope | None required for the initial codebase audit |
| Initial internal candidate areas | Domain models, connectors, parsers, publication, query, prototype source cards, and prior research |
| Initial external candidate areas | Official connector APIs only if code evidence cannot define a planning-ready boundary |
| Research posture | focused |
| Posture provenance | Default for an exact caller-specified audit |
| Explicit limits / deadline | Preserve every caller-provided input and output term exactly |
| Posture-specific completion basis | Focused scope and materiality |
| Edits allowed during research? | no, research-only |
| Resolved evidence root | .copilot-tracking/ |
| Known constraints / excluded sources | No product-code or documentation mutation during research |

## Extension Registry and Provenance

| Kind | Candidate | Match and provenance | Scoped authority or output contract | Selected / skipped reason |
|---|---|---|---|---|
| Instruction | copilot-tracking.instructions.md | Research artifact path match | Artifact identity and evidence conventions | Selected |
| Instruction | untrusted-content-boundary.instructions.md | Research ingests repository and possible external evidence | Treat retrieved content as data | Selected |
| Skill | rpi-research | Explicit research continuation | Three-wave evidence and readiness contract | Selected |
| Research specialist | None | Bounded repository audit is small enough to inspect directly | None | Skipped to avoid unnecessary delegation |

## User Participation and Research Decisions

| Checkpoint | Questions or no-interaction rationale | Answers / unanswered | Resulting decision or selected further research |
|---|---|---|---|
| Intake | Exact lists and intended Shaper direction are explicit | No unanswered intake question | Treat both lists as authoritative and immutable |
| Direction change | None | None | Preserve the focused audit |
| Convergence | Pending completed three-wave cycle | Pending | Pending |

## Scope and Success Criteria

* Scope: Audit current support and define a complete future capability boundary.
* Assumptions: "Wikis," "knowledge bases," and "legacy intranet content" are
  source categories, while Confluence and SharePoint are named source systems.
* Success criteria:
  * Every exact input and output is classified as implemented, partial, or absent.
  * Evidence uses stable codebase IDs and workspace-relative locations.
  * Architecture implications preserve provenance, permissions, and versioning.
  * Contrarian analysis tests whether the requested outputs should be independent
    files, views over a canonical asset, or both.

## Task Research Requests

* Explicit requests: Ensure inputs are SharePoint sites, PDFs, Word documents,
  Wikis, Confluence, Knowledge bases, and Legacy intranet content. Ensure outputs
  are Canonical knowledge assets, Structured metadata, Summaries, Q&A pairs,
  Taxonomies, Business entities, Knowledge graphs, and AI-ready source content.
* Inferred research questions: Which requirements are source systems versus
  formats; which outputs are primary assets versus derived projections; what
  extension points are required; and how should HTML packaging represent them?
* Caller constraints and non-goals: Exact terminology is authoritative. Research
  only in this phase.

## Direction Controls

| Control type | Direction or boundary | Provenance | Effect |
|---|---|---|---|
| change | Expand Shaper from the deployed upload/SharePoint compiler to a multi-source developer tool | Caller on 2026-09-10 | Audit all connector and packaging surfaces |
| narrow | Use the exact seven inputs and eight outputs | Caller on 2026-09-10 | Do not substitute or omit terms |
| add | Portable HTML knowledge output for downstream agents | Caller on 2026-09-10 | Assess HTML as a carrier for all output views |

## Research Cycle Log

### Cycle 1 Wider Wave

* Status: Complete
* Questions: Current breadth of input and output coverage.
* Findings:
  * The domain exposes only `sharepoint` and `upload` source kinds (C2).
  * The safe parser supports PDF and Word DOCX, plus Markdown and plain text
    (C3).
  * A SharePoint source adapter exists, but the hosted compiler explicitly
    rejects non-upload jobs (C4, C5).
  * The prototype exposes only SharePoint and file upload (C6).
  * The canonical `AnswerUnit` contains canonical questions, one answer, grounded
    claims, applicability, derivation, and confidence (C7).
  * Release publication emits `units.jsonl` and `manifest.json`; it does not emit
    HTML or independent summary, taxonomy, entity, or graph artifacts (C8, C9).
* Reflection: The exact list spans two input dimensions and two output layers.
  PDFs and Word documents are formats, while SharePoint sites and Confluence are
  systems. Canonical assets and AI-ready source content are authoritative
  products, while summaries, Q&A pairs, taxonomies, business entities, and
  knowledge graphs can be derived views with shared provenance.

### Cycle 1 Deeper Wave

* Status: Complete
* Questions: Required contracts, provenance, versioning, and HTML packaging.
* Findings:
  * Input contracts need a connector identity independent of content media type.
    A connector can enumerate source items, return bytes or normalized content,
    report source-native versions, capture permissions, and emit tombstones.
  * The exact input labels should remain product capabilities while mapping to
    connector families: SharePoint sites; Wikis; Confluence; Knowledge bases;
    Legacy intranet content; and direct file ingestion for PDFs and Word
    documents.
  * Every normalized source item needs stable source identity, source-system
    locator, source version, media type, title, timestamps, permission snapshot,
    and ordered addressable spans. The existing `SourceDocument` and
    `SourceSpan` provide most of this canonical ingestion base (C10).
  * Output contracts should use one versioned canonical knowledge asset as the
    authority and generate the other exact outputs as explicitly versioned,
    traceable projections. Each projection must retain source IDs, source
    versions, span citations, derivation identity, and approval state.
  * The portable package should contain human- and agent-readable HTML plus
    machine-readable metadata. A practical boundary is one `index.html`, asset
    pages or fragments, `manifest.json`, JSON-LD structured metadata and graph
    data, and optional tabular or JSON exports. HTML is the delivery carrier,
    not the only semantic representation.
  * "AI-ready source content" should preserve normalized full-fidelity source
    passages and headings separately from concise answer-shaped derivatives.
    This avoids losing evidence needed for future models or alternate shaping.
* Reflection: A connector-normalize-shape-enrich-package pipeline can cover the
  exact list without adding one bespoke end-to-end workflow per source.

### Cycle 1 Contrarian Wave

* Status: Complete
* Questions: Risks of treating every output as a separate artifact and every
  source label as a distinct connector.
* Counter-evidence and risks:
  * Seven `SourceKind` enum members would be misleading because PDFs and Word
    documents are formats, and Wikis, Knowledge bases, and Legacy intranet
    content may share HTTP, export-file, or vendor-specific adapters.
  * Eight independently authored outputs would drift. For example, a summary,
    Q&A pair, entity record, and graph edge could disagree about the same policy
    unless they derive from one approved canonical asset and cite the same spans.
  * HTML-only output is insufficient for reliable graph traversal, metadata
    exchange, and deterministic validation. Conversely, JSON-only output is less
    portable for knowledge systems that ingest web pages.
  * A single giant HTML document would weaken incremental versioning, access
    trimming, citation granularity, and selective reprocessing.
  * "Knowledge graph" must not imply unsupported semantic truth. Nodes and edges
    need evidence links, extraction confidence, ontology or relation type, and
    review state.
* Reflection: The selected direction is a dual representation: immutable
  canonical records and derived machine-readable structures packaged with
  portable HTML pages. Product labels stay exact, while internal connector and
  format taxonomies stay orthogonal.

### Cycle 1 Parent Synthesis

* The caller's seven inputs and eight outputs form the authoritative capability
  baseline.
* Existing code provides a credible kernel for direct PDF and Word ingestion,
  normalized spans, grounded Q&A assets, metadata, review, and immutable
  releases.
* Planning must add connector contracts and adapters, enrichment models,
  multi-artifact release assembly, HTML rendering, JSON-LD graph and metadata
  serialization, and exact capability presentation in the prototype.
* Re-entry decision: Another research cycle is not required for requirements
  completeness. Vendor API details belong to implementation planning or
  connector-specific research.

## Evidence Log

| ID | Type | Location | Finding | Confidence |
|---|---|---|---|---|
| C1 | Caller requirement | Conversation, 2026-09-10 | The seven input labels and eight output labels are authoritative | High |
| C2 | Code | src/shaper/domain/models.py:49 | Source kinds are limited to SharePoint and upload | High |
| C3 | Code | src/shaper/infrastructure/parsers.py:27 | PDF and Word DOCX parsing are implemented alongside Markdown and text | High |
| C4 | Code | src/shaper/infrastructure/sharepoint.py:36 | A read-only SharePoint source adapter resolves and synchronizes a configured root | High |
| C5 | Code | src/shaper/application/compiler.py:114 | Hosted compilation rejects every source kind except upload | High |
| C6 | Prototype | prototype/copilot-studio-knowledge-compiler/index.html:245 | The concept offers SharePoint or PDF, Word, Markdown, and text upload only | High |
| C7 | Code | src/shaper/domain/models.py:282 | AnswerUnit models grounded canonical questions and an answer with provenance | High |
| C8 | Code | src/shaper/application/publication.py:33 | Release assembly emits only units.jsonl as its content artifact | High |
| C9 | Code | src/shaper/infrastructure/filesystem_sink.py:45 | Filesystem publication writes supplied artifacts and a manifest without HTML rendering | High |
| C10 | Code | src/shaper/domain/models.py:180 | SourceDocument and SourceSpan provide stable normalized evidence identity and metadata | High |

## Findings Mapped to Questions and Evidence

| Exact requirement | Current status | Evidence | Planning interpretation |
|---|---|---|---|
| SharePoint sites | Partial | C2, C4, C5, C6 | Finish hosted enumeration, ingestion, delta, permissions, and tombstones |
| PDFs | Implemented for direct upload | C3, C6 | Retain as a format capability usable through any connector |
| Word documents | Implemented for DOCX direct upload | C3, C6 | Retain as a format capability; define legacy DOC policy separately |
| Wikis | Missing | C2, C6 | Add a generic wiki connector contract and concrete adapters or import profiles |
| Confluence | Missing | C2, C6 | Add a named Confluence connector using the shared source contract |
| Knowledge bases | Missing | C2, C6 | Add a category capability with pluggable vendor adapters and export ingestion |
| Legacy intranet content | Missing | C2, C6 | Add crawl, export, or migration ingestion with explicit permission and freshness limits |
| Canonical knowledge assets | Partial | C7, C8 | Generalize AnswerUnit into or alongside a canonical asset aggregate |
| Structured metadata | Partial | C7, C10 | Promote embedded metadata to an explicit package artifact and schema |
| Summaries | Missing | C7, C8 | Add grounded summary projection with citations and qualifier preservation |
| Q&A pairs | Implemented as answer-ready units | C7 | Preserve the exact Q&A pairs label and support multiple pairs per source asset |
| Taxonomies | Missing as output | C8 | Add versioned taxonomy terms, hierarchy, mappings, and evidence |
| Business entities | Missing | C8 | Add typed entity mentions, canonical entities, aliases, and source citations |
| Knowledge graphs | Missing | C8 | Add evidence-grounded nodes and edges, preferably serialized as JSON-LD |
| AI-ready source content | Partial | C3, C10 | Package normalized headings and spans in HTML and machine-readable form |

## Key Discoveries

1. The current implementation covers two of seven inputs completely enough for
   development use: PDFs and Word documents through direct upload.
2. SharePoint has adapter code but is not wired into hosted compilation.
3. Q&A pairs are the only exact derived-output capability currently implemented.
4. Structured metadata and canonical knowledge assets are partial because their
   fields exist but are not independent, named package contracts.
5. The safest architecture separates source connector, content format,
   canonical asset, derived projection, and package renderer.
6. HTML should be an interoperable delivery view backed by structured manifests
   and JSON-LD, not a replacement for canonical machine-readable records.

## Alternatives and Decision State

| Alternative | Strengths | Weaknesses | Decision |
|---|---|---|---|
| Add one pipeline per exact input | Direct product mapping | Duplicates parsing, provenance, and publishing logic | Rejected |
| Add every input as one SourceKind | Simple UI enumeration | Conflates systems, categories, and formats | Rejected |
| Shared connector contract plus independent format registry | Reuses ingestion and parsing while preserving exact product labels | Requires capability mapping metadata | Selected |
| Emit eight separately authored outputs | Obvious output files | High semantic drift and validation cost | Rejected |
| Canonical asset plus derived projections | Consistent provenance, incremental rebuilds, shared review | Requires renderer and projection orchestration | Selected |
| HTML only | Broad human and web-agent portability | Weak graph and metadata interchange | Rejected |
| HTML plus manifest and JSON-LD | Human-readable, agent-readable, testable, graph-capable | Larger package contract | Selected |

## Current Decisions

* Preserve every caller-provided label verbatim in the requirements baseline.
* Model connectors and file formats independently.
* Use one approved, versioned canonical knowledge asset as the semantic authority.
* Derive Summaries, Q&A pairs, Taxonomies, Business entities, Knowledge graphs,
  Structured metadata, and AI-ready source content from that authority.
* Publish portable HTML together with a manifest and machine-readable structured
  data, including JSON-LD for linked entities and graph relationships.

## Unresolved Decisions

* Which wiki and knowledge-base products need first-party adapters beyond the
  explicitly named Confluence connector.
* Whether "Word documents" must include legacy `.doc` in addition to `.docx`.
* Which legacy intranet authentication and crawling patterns are permitted.
* The initial business-entity ontology and taxonomy governance owner.
* Whether a package is one HTML page per canonical asset or a bounded collection
  of pages with an index. The evidence favors per-asset pages plus an index.

## Risks and Residual Uncertainty

* Source permissions may not map cleanly between originating systems and target
  agent knowledge stores.
* Legacy content can lack stable IDs, versions, or trustworthy freshness dates.
* Generated summaries, entities, taxonomy mappings, and graph edges can amplify
  unsupported inferences unless every item retains span-level evidence.
* A graph schema chosen before representative corpus analysis may overfit one
  business domain.
* HTML consumers vary in how they handle metadata, scripts, links, and embedded
  JSON-LD; the package requires a conservative static profile.

## Potential Next Research

1. Confluence, generic wiki, knowledge-base, and legacy intranet connector API
   and export-format comparison.
2. Portable static HTML and JSON-LD ingestion compatibility across target agent
   platforms.
3. Business-entity and taxonomy schema discovery using representative customer
   documents.
4. Paired baseline versus shaped evaluation design for each output projection.

## Planning Readiness

* Status: Ready.
* Reason: The exact capability baseline, current gaps, selected architecture
  boundary, risks, and open connector-specific decisions are recorded. Planning
  can sequence the common contracts before vendor adapters.

## Research Disposition

* Disposition: executed.
* Status: Complete.

## Self-Check

* Exact caller lists captured: Passed.
* Three waves completed in order: Passed.
* Findings mapped to evidence: Passed.
* Alternatives and contrarian evidence assessed: Passed.
* Planning readiness supported: Passed.
