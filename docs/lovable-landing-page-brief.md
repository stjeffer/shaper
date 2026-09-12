# Lovable build brief: Shaper public landing page

Paste this brief into Lovable as the build instruction. Build a **single public landing / advertisement page** for Shaper. This is **not** the authenticated product workspace. Treat every repository fact below as authoritative, and do not invent unsupported capability.

## Overview

Build a premium, modern enterprise landing page for **Shaper**: a governed platform that helps teams assess and reshape source content so it is more reliable for retrieval and agent answers.

Shaper is **not** an autonomous agent and **not** a source-rewriting bot. Present it as a **governed platform coordinating bounded specialist roles** across assessment, recommendation, transformation, and approval. Human governance must stay central throughout the page:

- assessment signals are **review candidates**
- transformation outputs are **proposals**
- publication requires **human review and approval**

Use confident, plain-language, evidence-led copy. Preserve the canonical product and check labels used in this brief. Avoid hype, fear, pseudo-precision, and vague "AI magic" language.

## Author-only repository grounding

Use these references to verify the generated page. Do not render these repository-relative links on the public page:

- [README](../README.md)
- [Feature guide](features.md)
- [Document readiness checklist](document-readiness-checklist.md)
- [Deployment guidance](deployment.md)

## Goal, audience, positioning, success criteria

### Goal

Convince a serious enterprise visitor that Shaper solves a specific problem: **documents that work for humans often fail the extraction, chunking, retrieval, and grounding path that agents rely on**. The page should explain how Shaper exposes those failure modes, turns them into evidence-backed findings, proposes governed improvements, and keeps humans in control.

### Audience

Primary audiences:

1. knowledge management and content governance leads
2. Microsoft 365 / SharePoint / intranet owners
3. internal AI platform and Copilot owners
4. enterprise architecture and digital workplace leaders
5. documentation, policy, and operations teams responsible for high-stakes guidance

Secondary audiences:

- security and compliance-adjacent reviewers who care about governed publication
- delivery teams evaluating content readiness before rolling material into assistant experiences

### Product positioning

Position Shaper as:

- a **source-quality and governance layer** for enterprise knowledge used by agents
- a **Knowledge Estate** platform for organising registrations, uploads, findings, decisions, and outputs
- a **human-governed shaping workflow**, not a black-box automation product
- a way to improve what downstream retrieval and assistants can reliably use, **before** publishing approved outputs

Do **not** position it as:

- a general autonomous agent
- a crawler that roams the estate freely
- a legal or compliance authority
- a guaranteed accuracy engine
- a quantified readiness scoring product

### Landing-page success criteria

The finished page should make a first-time visitor able to say, without guesswork:

1. what Shaper is
2. who it is for
3. why source quality affects agent answers
4. what the 29 deterministic checks do
5. how the governed workflow works end to end
6. what is available now versus planned
7. where a CTA would send them next

## Non-negotiable facts and claim boundaries

Keep these statements explicit in copy and visuals:

- Shaper organises content into **Knowledge Estates**.
- Current inputs include **URL and SharePoint registration**, **individual file upload**, and **bounded malware-scanned ZIP upload**.
- Registered sources and uploaded documents appear in the current document inventory.
- Source versions are **immutable**.
- Findings include **evidence and source locations**.
- Users can open a **full-document review** of the exact source version.
- Recommendations are generated for **selected documents**, not automatically for everything.
- Recommendation review includes an **accessible stacked input / output / repair-and-safety token-budget infographic** with an enforced maximum before model use.
- Approval is **exact and version-pinned**.
- Only **approved** proposals can enter transformation.
- Current transformation output is **approved-only semantic HTML**.
- Review includes **before / after panels**.
- Publication approval is **separate** from proposal approval.
- Estates can include **evaluation reports**.
- The platform supports **archive and purge** with governance controls.
- The current deployed shape is an **authenticated Azure deployment**.
- SharePoint is **registration only today**.
- Microsoft Graph crawling and synchronization are **planned**, not current.
- Registered URL, wiki, Confluence, or intranet locations must **not** imply arbitrary crawling or automatic synchronization.
- Findings are **not** a score out of 100.

Never claim:

- autonomous source rewriting
- estate-wide modification
- recurring governance schedules
- distributed workers as a current feature
- guaranteed accuracy
- legal or compliance correctness
- quantified ROI or performance uplift
- quantitative readiness scoring

## Information architecture and anchored navigation

Build the page as one long, scrollable document with sticky anchored navigation.

Use this nav order exactly:

1. `Overview` → `#overview`
2. `Why source quality matters` → `#why-source-quality-matters`
3. `How defects become agent failures` → `#defect-to-agent-impact`
4. `29 deterministic checks` → `#checks`
5. `How Shaper works` → `#workflow`
6. `Platform features` → `#features`
7. `Before and after` → `#before-after`
8. `Architecture and trust` → `#architecture-trust`
9. `Current and planned` → `#current-planned`
10. `Next step` → `#cta`

On mobile, convert sticky navigation into a compact anchor menu or section jump list with no horizontal overflow.

---

## Section-by-section build direction

## `#overview` Hero

### Purpose

Make the visitor understand the product in one screen: Shaper improves the quality and governance of source content before agents rely on it.

### Layout

Two-column desktop hero; stacked on mobile.

Left side:

- eyebrow
- H1
- subhead
- two CTAs
- short proof bullets

Right side:

- editorial-style visual showing an **estate-to-agent pipeline motif**
- visual layers: source repositories → evidence-backed findings → governed proposal → approved semantic output → downstream agent use
- use a refined UI-inspired diagram, not a cartoon robot

### Copy direction

Use this message shape:

- Documents written for people often break when they pass through extraction, chunking, metadata, retrieval, and grounding.
- Shaper helps teams assess those source issues, understand likely agent impact, and govern approved reshaping.
- Humans stay in control at every approval boundary.

### Hero proof bullets

Use 3 to 4 concise bullets such as:

- 29 deterministic checks with evidence and likely agent impact
- version-pinned recommendations and approvals
- approved-only semantic HTML transformation
- separate output review before publication

### CTA labels

Use placeholders only, for example:

- `Request a walkthrough`
- `See the workflow`

Do not invent real URLs.

## `#why-source-quality-matters` Problem space

### Purpose

Explain the problem in practical terms. Do not say "AI is only as good as your data" and move on. Show the concrete content problem.

### Required narrative

Explain that agents do not consume a document the way a person does. A pipeline typically:

1. extracts text and structure
2. divides content into chunks
3. enriches chunks with metadata
4. retrieves a small subset for a question
5. grounds the answer in that retrieved evidence

A weak source can therefore create failure long before answer generation:

- poor structure weakens chunk boundaries
- missing metadata weakens filtering and ranking
- unresolved references strip away context
- contradictions surface incompatible answers
- ambiguous rules encourage unsupported specificity
- poor provenance makes old and current guidance look equally valid
- content trapped in images or objects can disappear during extraction

### Visual direction

Create an editorial diagram or progressive scrollytelling strip with these stages:

`source quality` → `extraction` → `chunking` → `metadata` → `retrieval` → `grounding` → `answer`

Each stage should show how a source defect can propagate.

### Tone

Practical and evidence-led, not alarmist.

## `#defect-to-agent-impact` Source-defect-to-agent-impact chain

### Purpose

Show why Shaper focuses on findings instead of a single score.

### Required message

State plainly that a single readiness score cannot explain **which failure mode is present**, **why it matters**, or **what a content owner should inspect next**. Shaper therefore presents **reviewable findings** that connect:

- what was detected
- why it can affect retrieval or answers
- where the evidence appears in the source
- what a human should review

### Required content blocks

Create four linked cards or steps:

1. **Detect the condition** — identify a structural, metadata, ambiguity, contradiction, or provenance issue
2. **Explain likely agent impact** — show the retrieval or answer risk in plain language
3. **Show evidence and location** — point to the exact quoted source or bounded location
4. **Keep the human decision** — content owner corrects, clarifies, accepts, or defers

### Governance note

Repeat that findings are **review candidates**, not autonomous verdicts.

## `#checks` 29 deterministic checks catalog

### Purpose

Present Shaper's assessment model clearly and accurately. This section must feel substantial and trustworthy.

### Presentation rules

- Present **29 deterministic checks** as **7 baseline checks + 22 content-integrity checks**.
- Group the 22 content-integrity checks under clear risk families.
- Do **not** collapse them into a numeric score.
- For every check, show:
  - plain-English label
  - what it looks for
  - likely agent impact

### Baseline checks

| Check | What it looks for | Likely agent impact |
|---|---|---|
| Limited metadata (`poor_metadata`) | Too little document metadata for strong filtering and context | Retrieval has less context for ranking the right passage. |
| Weak structure (`structure_gap`) | Missing or weak headings and focused sections | Poor chunk boundaries make the right passage harder to isolate. |
| Freshness risk (`stale`) | Older guidance that may no longer be current | Agents may return obsolete rules as if they are current. |
| Long paragraph (`long_paragraph`) | Oversized passages mixing several ideas | Chunking and retrieval precision can fall. |
| Document reference (`cross_policy_reference`) | Opaque references to another document without enough local context | The retrieved passage may be incomplete on its own. |
| No question coverage (`faq_gap`) | Missing FAQ or question-shaped language | Common user queries may match less directly. |
| Implicit procedure (`procedure_gap`) | Procedural content without clear numbered steps | Agents may struggle to present a reliable sequence. |

### Content-integrity checks

#### Structural and referential integrity

| Check | What it looks for | Likely agent impact |
|---|---|---|
| External dependency (`external_dependency`) | A rule depends on material outside the available source set | The agent may retrieve an incomplete rule when the dependency is missing. |
| Circular reference (`circular_reference`) | Two sections or documents depend on each other to explain the rule | The agent cannot resolve one complete answer cleanly. |
| Missing referenced content (`missing_referenced_content`) | A referenced appendix, section, or item is absent | The agent may omit key detail or invent a filler answer. |
| Version ambiguity (`version_ambiguity`) | Multiple versions exist but the current one is unclear | The agent may surface outdated guidance. |
| Orphaned amendment (`orphaned_amendment`) | A later change exists without clear connection to the base text | The agent may answer from the old rule and miss the amendment. |

#### Ambiguity and decision clarity

| Check | What it looks for | Likely agent impact |
|---|---|---|
| Vague quantifier (`vague_quantifier`) | Terms such as "regularly", "promptly", or "as needed" without usable bounds | The agent must either repeat unhelpful vagueness or infer unsupported specifics. |
| Discretion clause (`discretion_clause`) | Decision language that depends on human judgement without framing the judgement | The agent may overgeneralise a case-specific decision. |
| Undefined term (`undefined_term`) | Important term used without definition | The same term may be interpreted inconsistently across answers. |
| Unclear responsibility (`unclear_responsibility`) | An action exists but the responsible person or approver is unclear | The agent may describe a task without saying who must do it. |

#### Contradiction and consistency

| Check | What it looks for | Likely agent impact |
|---|---|---|
| Conflicting numeric value (`conflicting_numeric_value`) | Different numbers or thresholds for the same rule | Retrieval may surface inconsistent values. |
| Conflicting authority (`conflicting_authority`) | Competing governing instructions with unclear precedence | The agent may choose the wrong rule source. |
| Terminology drift (`terminology_drift`) | Different terms used for the same concept, or one term used inconsistently | Retrieval matches weaken and concepts may be conflated. |

#### Incompleteness

| Check | What it looks for | Likely agent impact |
|---|---|---|
| Missing definitions (`missing_definitions`) | Terms are used as if already defined, but definitions are absent | The agent may guess the meaning instead of grounding it. |
| Missing enumeration (`missing_enumeration`) | A promised list or breakdown is incomplete or missing | The agent cannot give a complete location-specific answer. |
| Dangling program (`dangling_program`) | An expired, inactive, or unanchored program is described as current | The agent may present inactive options as still available. |

#### Provenance and authority

| Check | What it looks for | Likely agent impact |
|---|---|---|
| Unclear source of truth (`unclear_source_of_truth`) | It is not obvious which source is authoritative | The agent may rely on stale or non-authoritative guidance. |
| Undocumented verbal policy (`undocumented_verbal_policy`) | Important clarification exists only in verbal or informal form | The governing clarification is unavailable to ground the answer. |
| Restricted companion (`restricted_companion`) | A required companion source exists but may not be accessible | The agent may answer without required context. |

#### Formatting and retrieval hygiene

| Check | What it looks for | Likely agent impact |
|---|---|---|
| Inconsistent heading hierarchy (`inconsistent_heading_hierarchy`) | Broken or misleading heading nesting | Related rules can be split incorrectly, or unrelated content merged. |
| Inaccessible embedded content (`inaccessible_embedded_content`) | Important information is trapped inside images or embedded objects | Extraction may miss the content entirely. |
| Repeated variation (`repeated_variation`) | Slightly different repeats of the same rule | Retrieval may surface different versions and produce inconsistent answers. |
| Noncanonical duplicate (`noncanonical_duplicate`) | Duplicate content exists with no clearly identified canonical source | The agent may retrieve an outdated duplicate. |

### Section close

End this section with one short statement:

> These checks surface deterministic review candidates. They do not prove legal meaning, semantic correctness, or policy validity on their own.

## `#workflow` How Shaper works

### Purpose

Show the governed journey from source intake to approved output.

### Required workflow sequence

Use a horizontal desktop journey and stacked mobile cards.

1. **Create a Knowledge Estate**
   - named estate
   - description
   - output naming convention
2. **Register or upload sources**
   - URL registration
   - SharePoint registration only
   - individual file upload
   - bounded ZIP upload scanned for malware before inventory
   - current document inventory
3. **Discover and assess**
   - durable workflow run
   - per-document findings
   - evidence coverage
   - exact source version and assessment time
4. **Review full source**
   - open the exact normalized source version
5. **Recommend for selected documents**
   - selected-document scope only
   - version-pinned proposal
   - token-budget infographic with input, output, repair-and-safety, total, and enforced maximum
6. **Human approval**
   - append-only approve or decline decision
   - approval pinned to exact source version, proposal, estimator, and model deployment
7. **Transform approved proposals**
   - approved-only semantic HTML output
8. **Review before publication**
   - before / after panels
   - separate publication approval boundary
9. **Archive or purge when needed**
   - archive is read-only
   - purge is permanent and governed

### Important workflow language

Say that Shaper coordinates **bounded specialist roles** inside one governed platform. Do not describe it as self-directing automation.

## `#features` Platform features

### Purpose

Show concrete features using product-style cards, not vague benefits.

### Recommended card groups

#### Estate and source controls

- Knowledge Estates
- URL registration
- SharePoint registration
- individual file upload
- bounded malware-scanned ZIP upload
- immutable source versions
- source inventory and listing

#### Assessment and evidence

- 29 deterministic checks
- evidence and source locations
- full-document review
- score-free findings view
- likely agent impact explanations

#### Recommendation and approval

- selected-document recommendations
- accessible stacked token-budget infographic
- exact version-pinned approval
- append-only decision history

#### Transformation and publication governance

- approved-only semantic HTML transformation
- before / after review panels
- separate publication approval
- evaluation reports

#### Lifecycle and deployment

- workflow progress and durable state
- archive and purge
- authenticated Azure deployment

### Copy direction

Each card should describe the concrete control or output, then the practical reason it matters.

Example pattern:

- **Immutable source versions** — every finding, proposal, and approval stays tied to the exact source revision under review.

## `#before-after` Before and after story

### Purpose

Make the outcome tangible without claiming autonomous rewriting.

### Required story shape

Use one realistic example story based on policy or operational content:

- **Before reshaping**: a dense, cross-referenced, ambiguous document with weak headings and hidden dependencies
- **After reshaping**: an approved semantic HTML proposal with clearer structure, explicit labels, better chunk boundaries, and preserved governance context

### Non-negotiable caveat

State in the section itself:

- the transformed output is a **proposal derived from an approved recommendation**
- it does **not** rewrite the original estate automatically
- publication still requires **human review**

### Visual direction

Use side-by-side panels on desktop and stacked labelled panels on mobile:

- `Before reshaping`
- `After reshaping`

Make them feel like real UI review surfaces.

## `#architecture-trust` Architecture and trust

### Purpose

Show credible delivery and governance boundaries.

### Required content

Summarise the current deployment truthfully:

- authenticated HTTP and MCP service on Azure Container Apps
- ClamAV sidecar inside the same replica for upload scanning
- Azure Database for PostgreSQL for durable estate, workflow, decision, and review state
- Azure Files mounted state for uploads and legacy release files
- authenticated Knowledge Estates workspace served by the same application

### Required governance message

Explain that:

- Shaper preserves evidence lineage between source, findings, proposals, and outputs
- uploads pass a scanning boundary before inventory
- the platform does not have arbitrary shell, filesystem, publication, or review authority over enterprise content
- output publication remains a human decision

### Visual direction

Use a clean enterprise architecture strip or diagram with clearly separated layers:

- inputs and registrations
- Shaper governed platform
- durable state and scanning boundary
- approved outputs for downstream agent use

Do not draw futuristic distributed-agent swarms.

## `#current-planned` Current vs planned boundaries

### Purpose

Build trust by being explicit.

### Layout

Use a two-column comparison or labelled tabs:

- `Current today`
- `Planned next`

### Current today

Must include:

- Knowledge Estates
- URL registration
- SharePoint registration only
- individual file upload
- bounded ZIP upload with scanning
- 29 deterministic checks
- evidence-backed findings
- full-document review
- selected-document recommendations
- version-pinned approvals
- approved-only semantic HTML transformation
- before / after review
- separate publication approval
- evaluation reports
- archive and purge
- authenticated Azure deployment

### Planned next

May include, clearly labelled planned:

- Microsoft Graph-based SharePoint and OneDrive crawling / synchronization
- more managed asynchronous processing and connectors in production topology
- optional retrieval projection surfaces after approval

### Explicit boundary text

Include one short paragraph that says:

> SharePoint entries are truthful registrations today. They do not mean content has been crawled or synchronized. References to URL, wiki, Confluence, or intranet locations must not be read as arbitrary crawling capability.

## `#cta` Final CTA

### Purpose

Close with a serious enterprise action, not hype.

### Content

Use a tight summary:

- Shaper helps teams inspect whether enterprise content is fit for retrieval and agent use
- it turns source issues into evidence-backed findings
- it proposes governed reshaping, keeps approvals version-pinned, and requires human publication review

### CTA labels

Use placeholder destinations only, such as:

- `Book a product walkthrough`
- `Talk about your knowledge estate`
- `Review deployment approach`

Add a short note that destinations are placeholders until the page owner supplies them.

---

## Visual and brand direction

Use a **premium enterprise aesthetic** with **editorial data storytelling**.

### Must-have visual characteristics

- crisp layout with generous spacing
- dark-on-light or carefully controlled low-glare palette
- restrained accent colour for state and emphasis
- elegant typography with strong heading rhythm
- estate-to-agent pipeline motif across hero and supporting diagrams
- diagram-led explanation instead of decorative illustrations
- UI-inspired cards, findings rows, evidence callouts, before/after review panels, and token visualisation blocks
- restrained motion only where it clarifies progression or state

### Must avoid

- stock-photo meeting scenes
- glowing robot heads
- generic chatbot bubbles as the main visual language
- fake customer logos
- fake testimonials
- fake usage numbers or business metrics
- noisy gradient overload
- parallax or motion that risks readability

## Responsive requirements

Design responsively from the start.

### Required breakpoints and behaviour

- no horizontal overflow at any width
- full 320px reflow support
- stacked layout for comparisons and diagrams on small screens
- desktop side-by-side panels may stack on tablet and mobile
- long tables should convert into cards or stacked definition blocks on narrow screens without losing content

### Mobile section order

Keep this order on mobile:

1. Hero
2. Why source quality matters
3. Source-defect-to-agent-impact chain
4. 29 deterministic checks
5. Workflow
6. Features
7. Before / after
8. Architecture and trust
9. Current vs planned
10. Final CTA

### Mobile interaction notes

- anchor navigation becomes a jump list, drawer, or compact sticky bar
- diagrams turn into vertical step cards
- before / after panels stack with clear labels
- token infographic remains readable without sideways scroll

## Accessibility requirements

Meet these requirements in the generated page:

- semantic landmarks: `header`, `nav`, `main`, `section`, `footer`
- correct heading hierarchy with one `h1`
- keyboard support for navigation, menus, tabs, accordions, and any carousel-like behaviour
- visible focus indicators with strong contrast
- text and UI contrast that meets accessibility expectations
- reduced-motion support for any animation
- status or meaning never conveyed by colour alone
- charts and diagrams include text equivalents or adjacent summaries
- no autoplay video or animation
- descriptive labels for CTAs, toggles, and navigation controls
- link purpose remains clear out of context
- comparison panels and token visuals remain understandable to screen-reader users

Prefer semantic HTML, real lists, real buttons, real tables where appropriate, and accessible SVG with text alternatives for diagrams.

## Interaction requirements and graceful states

### Interactions to include

- anchored navigation scroll to section
- subtle reveal or fade-in motion only if reduced-motion is respected
- expandable detail for the checks catalogue on smaller screens
- hover and focus states that mirror each other where relevant
- CTA hover/focus treatments that feel premium but restrained

### Graceful states

If Lovable needs placeholder data or imagery, handle it explicitly:

- placeholder CTA URLs are allowed and should be visibly labelled as placeholders
- if a diagram cannot render richly, fall back to clear stacked cards with text labels
- if before / after imagery is unavailable, render styled text panels based on realistic UI framing
- if charts simplify on mobile, preserve the text summary beside or beneath them

Do not invent backend behaviour, live syncing, dashboards, or authenticated flows beyond the public marketing page.

## Lovable implementation instructions

### Component approach

Use reusable components with consistent spacing and state handling:

- `StickyAnchorNav`
- `HeroPipeline`
- `EditorialSectionHeader`
- `ImpactChainDiagram`
- `CheckGroupTable` or `CheckGroupCards`
- `WorkflowSteps`
- `FeatureCardGrid`
- `BeforeAfterPanels`
- `ArchitectureTrustDiagram`
- `CurrentVsPlanned`
- `FinalCTA`

### Suggested content data structures

Model content in structured arrays / objects so sections stay reusable and editable.

Suggested shapes:

```ts
navItems: { label: string; href: string }[]
workflowSteps: {
  title: string
  summary: string
  bullets: string[]
}[]
checkGroups: {
  group: string
  checks: {
    label: string
    code: string
    purpose: string
    impact: string
  }[]
}[]
featureGroups: {
  title: string
  items: {
    name: string
    description: string
  }[]
}[]
currentPlanned: {
  current: string[]
  planned: string[]
}
ctaLinks: {
  label: string
  href: string
  placeholder: boolean
}[]
```

### Diagram rendering approach

- Prefer semantic HTML + CSS layouts for simple pipelines and comparison blocks.
- Use accessible SVG for diagrams that need connectors or richer flow.
- Do not rely on canvas-only diagrams.
- Every diagram must have a nearby text summary.
- Every visual stage label must remain readable at 320px.

### Performance and SEO

- keep the page lightweight
- avoid heavy animation libraries unless Lovable needs one already
- lazy-load only below-the-fold decorative visuals
- set meaningful title and meta description
- include Open Graph placeholders
- use descriptive section headings for SEO and accessibility
- optimise images and avoid giant background media

Suggested metadata:

- title: `Shaper | Governed content shaping for agent-ready knowledge`
- description: `Assess source documents, expose evidence-backed findings, and govern approved reshaping before agents rely on enterprise knowledge.`

### Layout hygiene

- no horizontal overflow
- no clipped focus rings
- no text on low-contrast imagery
- no sticky elements that cover anchored headings
- preserve comfortable reading width for body copy

### Quality checks for the generated build

Before considering the page done, ensure:

- every nav anchor resolves
- every section appears in the required order
- 29 checks are present as 7 baseline + 22 grouped content-integrity checks
- no score out of 100 appears anywhere
- SharePoint is described as registration only today
- Graph crawling / synchronization is labelled planned only
- every CTA destination is clearly placeholder content unless real URLs are supplied
- there is no horizontal scroll at 320px
- keyboard focus remains visible throughout

## Concise copy deck

Use or adapt this copy. Keep the substance intact.

### Hero

- Eyebrow: `Governed knowledge shaping for enterprise content`
- Headline: `Make source content more reliable before agents rely on it.`
- Subhead: `Shaper helps teams assess document quality, expose likely agent impact, and govern approved reshaping across a Knowledge Estate — with evidence, version-pinned approvals, and human review at every boundary.`
- Primary CTA: `Request a walkthrough`
- Secondary CTA: `See the workflow`

### Section headlines

- `Why source quality matters to agent answers`
- `How source defects become retrieval and grounding failures`
- `29 deterministic checks, shown as findings rather than a score`
- `A governed workflow from intake to approved output`
- `Concrete platform features for Knowledge Estates`
- `Review the change before anything is published`
- `Architecture and trust boundaries`
- `What is available now, and what is planned next`
- `Start with the content your agents depend on`

### CTA labels

- `Book a product walkthrough`
- `Talk about your knowledge estate`
- `Review deployment approach`

## Testable acceptance criteria

The generated page is acceptable only if all of these are true:

1. It is a single responsive landing page with anchored navigation.
2. It presents Shaper as a **governed platform coordinating bounded specialist roles**, not an autonomous agent.
3. It explains the source-quality chain across extraction, chunking, metadata, retrieval, grounding, and answers.
4. It presents **29 deterministic checks** accurately as **7 baseline + 22 content-integrity checks**.
5. Every check group includes purpose and likely agent impact.
6. It states that findings are **review candidates** and not a score out of 100.
7. It states that recommendations are selection-scoped and approvals are exact and version-pinned.
8. It states that only approved proposals enter semantic HTML transformation.
9. It states that publication approval is separate and human-controlled.
10. It includes current features: Knowledge Estates; URL and SharePoint registration; individual file upload; bounded malware-scanned ZIP upload; current document inventory; immutable source versions; evidence and source locations; full-document review; selected-document recommendations; accessible stacked input/output/repair-and-safety token-budget infographic; exact version-pinned approval; approved-only semantic HTML transformation; before/after review panels; separate publication approval; evaluation reports; archive and purge; authenticated Azure deployment.
11. It states explicitly that SharePoint is registration only today and Graph crawling / synchronization is planned.
12. It makes clear that registered URL, wiki, Confluence, or intranet locations do not imply arbitrary crawling.
13. It makes no claim of autonomous rewriting, estate-wide modification, recurring governance schedules, distributed workers, guaranteed accuracy, legal/compliance correctness, quantified ROI/performance uplift, or quantitative readiness scoring.
14. It uses premium enterprise visual direction without stock-photo AI clichés or fabricated proof.
15. It supports keyboard use, visible focus, reduced motion, contrast, semantic landmarks, text alternatives for charts, and 320px reflow.
16. It uses placeholder CTA destinations unless real destinations are supplied.
17. It does not render author-only repository references as public-page links.

## Explicit do-not-claim checklist

Do **not** claim any of the following in the build:

- `Shaper autonomously fixes your content`
- `Shaper crawls your entire estate today`
- `Shaper continuously governs content on a schedule`
- `Shaper rewrites source documents in place`
- `Shaper guarantees accurate answers`
- `Shaper proves legal, policy, or compliance correctness`
- `Shaper delivers quantified ROI, accuracy uplift, or performance improvement`
- `Shaper produces a readiness score out of 100`
- `SharePoint sync is live today`
- `Registered sources are automatically crawled just because they are listed`
- fake testimonials, fake customer logos, or fake adoption metrics

## Final note to Lovable

Build this page to feel like a serious enterprise product launch: elegant, restrained, diagram-led, and factually grounded. The most important outcome is clarity and trust. If a design choice makes the product sound more autonomous, more quantified, or more general than the facts support, choose the more truthful option.
