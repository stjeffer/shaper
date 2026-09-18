<!-- markdownlint-disable-file -->

# Task Research: compact-review-findings

| Field | Value |
|---|---|
| Date | 2026-09-12 |
| Researcher / agent | rpi-research |
| Status | Complete |
| Artifact path | .copilot-tracking/research/2026-09-12/compact-review-findings-research.md |

## Research Brief

* What to research: A more space-efficient way to show document review findings than the current expanding dropdown.
* Why it matters: Expanded findings create excessive vertical scrolling and reduce comparison across documents.
* Audience or intended use: Shaper product and implementation decision.
* Scope: Current Assess document rows, finding summaries and details, Fluent UI patterns, and accessible disclosure alternatives.
* Non-goals: Source code changes, backend contract changes, and changes to finding meaning.
* Criteria: Compact default state, clear finding count and severity, rapid scanning, keyboard and screen-reader usability, and full evidence access on demand.
* Requested outputs: Evidence-backed comparison and one recommended presentation.
* Output mode: convergence.

## Research Parameters

| Field | Value |
|---|---|
| Research question(s) | Which compact interaction best preserves scanability and access to finding evidence? |
| Codebase scope | prototype/copilot-studio-knowledge-compiler/app.js, index.html, styles.css |
| External scope | Official Microsoft Fluent guidance, WAI-ARIA Authoring Practices, and relevant public-sector design guidance |
| Initial internal candidate areas | documentFindings rendering, Assess table, responsive styles |
| Initial external candidate areas | Fluent accordion/table patterns, ARIA disclosure/dialog patterns, progressive disclosure |
| Research posture | focused |
| Posture provenance | default |
| Explicit limits / deadline | none |
| Posture-specific completion basis | focused scope and materiality |
| Edits allowed during research? | no, research-only |
| Resolved evidence root | .copilot-tracking/research |
| Known constraints / excluded sources | Preserve findings, agent impact, evidence, and source-review access; no implementation in this phase |

## Extension Registry and Provenance

* Precedence: platform safety; caller scope; repository instructions; rpi-research; accessibility skill; examples.

| Kind | Candidate | Match and provenance | Scoped authority or output contract | Selected / skipped reason |
|---|---|---|---|---|
| Instruction | copilot-tracking.instructions.md | Evidence path match | Tracking artifact placement and content rules | Selected |
| Instruction | markdown.instructions.md and writing-style.instructions.md | Markdown artifact | Markdown and prose conventions | Selected |
| Skill | accessibility | Interactive finding disclosure | WCAG and ARIA method guidance; interaction, announcement, and reflow require adequate runtime or manual verification | Selected |
| Research specialist | none | Bounded UI question | Independent delegation unnecessary | Skipped; focused inline research is proportionate |

## User Participation and Research Decisions

| Checkpoint | Questions or no-interaction rationale | Answers / unanswered | Resulting decision or selected further research |
|---|---|---|---|
| Intake | Existing request defines the usability problem and desired outcome | No questions needed | Compare compact patterns and converge |
| Direction change | None | None | Brief unchanged |
| Convergence | Evidence supports responsive master-detail over inline expansion, popover, tabs, or modal-only presentation | No user input required | Select responsive master-detail with explicit accessibility guardrails |

## Scope and Success Criteria

* Scope: Findings presentation only; preserve all underlying evidence and review actions.
* Assumptions: The primary problem is vertical expansion, not finding quality.
* Success criteria:
  * Every research question is answered.
  * Code and external claims use stable evidence IDs.
  * Alternatives include trade-offs and contrarian evidence.
  * One recommendation is selected only after all three waves.

## Task Research Requests

* Explicit requests: Research a better way to show review findings without excessive vertical space.
* Inferred research questions: Which summary belongs in-row; where full details should open; how keyboard and screen-reader users retain context.
* Caller constraints and non-goals: Research first; no implementation during this phase.

## Direction Controls

| Control type | Direction or boundary | Source / checkpoint | Effect on active brief, evidence, or revalidation |
|---|---|---|---|
| Change | Replace the vertically expansive findings dropdown | User request | Compare compact alternatives |
| Narrow | Preserve access to full finding explanation and evidence | Existing product requirements | Reject lossy summaries |

## Research Questions

| # | Sub-question | Type | Priority | Status |
|---:|---|---|---|---|
| Q1 | What causes the current vertical expansion? | straightforward | H | open |
| Q2 | Which compact patterns fit the existing Fluent UI and table context? | depth | H | open |
| Q3 | Which pattern best preserves accessibility and evidence context? | depth | H | open |
| Q4 | What credible drawbacks challenge the preferred pattern? | depth | M | open |

## Prior Knowledge Gate

* Existing artifacts reviewed: Current conversation and prior findings-led UX decisions.
* Reused (verified) findings: Findings must retain agent impact, bounded evidence, and human review.
* Superseded / stale: No prior compact findings pattern has been selected.

## Research Cycle Log

### Cycle 1

* Active direction controls: Replace vertical dropdown; preserve complete evidence.
* Active research posture and completion basis: focused; stop when the current UI, credible compact alternatives, accessibility, and contrarian risks are evidenced.
* Explicit limits or deadline effect: none.

#### Wave 1: Wider

* Plan and independent lanes: Inspect current rendering and identify compact list, side panel, dialog, inline preview, and accordion alternatives; consult official interaction guidance.
* Worker evidence relationships or inline fallback: Inline because the bounded UI question is tightly coupled and low volume.
* Reflection: The current disclosure is semantically reasonable but structurally mismatched to the volume it controls: one table cell reveals a list of full finding explanations, impact statements, review labels, and nested evidence. Candidate patterns are (1) keep inline disclosure, (2) compact in-row preview, (3) modal dialog, (4) overlay drawer, and (5) inline drawer/master-detail. Fluent specifically positions inline drawers for simultaneous interaction with main and secondary content. GOV.UK warns against hiding information most users need, so the row must retain a meaningful always-visible status.

#### Wave 2: Deeper

* Parent-prioritized material from Wave 1: Compare inline drawer/master-detail with overlay drawer and modal dialog; establish responsive and accessibility behavior.
* Plan and independent lanes: Inspect existing width and responsive rules, existing dialog infrastructure, and official guidance for drawer anatomy, popover limits, focus order, landmarks, and reflow.
* Worker evidence relationships or inline fallback: Inline.
* Reflection: A responsive master-detail pattern best matches the task. On wide screens, a named inline complementary pane lets reviewers keep the document list visible and switch rows without repeated modal context changes. On narrow screens or at high zoom, that pane must become a modal overlay or dedicated stacked view because WCAG reflow applies to text inside table cells and Fluent says inline drawers commonly collapse at product-defined breakpoints. A popover is unsuitable because findings are essential and can contain structured, lengthy evidence.

#### Wave 3: Contrarian

* In-scope challenge targets and boundaries: Test whether a drawer hides context, squeezes the table, obscures keyboard focus, makes comparison harder, or hides review-critical information.
* Plan and independent lanes: Compare accordion and tabs guidance; inspect focus-obscured and responsive risks; challenge inline and overlay drawer variants separately.
* Worker evidence relationships or inline fallback: Inline.
* Reflection: The selected pattern remains strongest only with guardrails. An overlay that remains open while focus moves behind it risks obscuring focus; a desktop inline pane must reflow rather than cover the table; a narrow layout must not squeeze table-cell text. The row summary must expose the finding count and highest urgency because accordions, tabs, and drawers all hide some content. Accordion-only remains viable for familiar caseworkers and comparison, but it directly retains the unbounded vertical expansion the user wants removed.

#### Parent Synthesis and Disposition

| Material / claim | Evidence IDs | Parent disposition | Evidence-based rationale | Primary-artifact treatment |
|---|---|---|---|---|
| Move full details out of table-row flow | C1-C4, W1-W2 | accepted | Directly addresses unbounded row height while preserving information | Selected recommendation |
| Keep count, urgency, and action visible in every row | C2-C3, W6, W13 | accepted | Prevents critical findings from becoming undiscoverable | Required guardrail |
| Use inline detail pane at wide widths | C6, W2, W10, W14 | accepted | Preserves list context and avoids overlap when the layout reflows | Selected desktop behavior |
| Use modal/full-width detail at narrow widths | C7, W5, W8, W11-W12 | accepted | Prevents two cramped columns and defines focus containment | Selected responsive behavior |
| Use popover for full findings | W9 | rejected | Findings are essential, structured, and potentially lengthy | Rejected alternative |
| Keep nested row disclosure | C3-C4, W13 | rejected | Does not solve vertical expansion and nests evidence disclosures | Rejected alternative |
| Use modal dialog at all widths | W3, W5 | rejected | Unnecessarily blocks rapid movement between documents | Narrow-screen fallback only |

#### Cycle Re-entry Evaluation

* Another complete three-wave cycle needed: no.
* Trigger or stop basis: The current UI cause, credible alternatives, official design guidance, responsive constraints, accessibility behavior, and counter-evidence are covered; further likely sources are redundant.
* Revised brief or revalidation required: none.
* Readiness effect: Ready for planning or implementation.

## Evidence Log

* Delegation: Inline focused research.

### Codebase Evidence

| ID | Claim / finding | Location | Tool | Confidence | Notes |
|---|---|---|---|---|---|
| C1 | Each assessed document renders findings inside its table cell. | prototype/copilot-studio-knowledge-compiler/app.js:890 | code read | high | The cell also includes a checks-run line. |
| C2 | The current component is a native details disclosure whose summary shows finding and high-priority counts. | prototype/copilot-studio-knowledge-compiler/app.js:328 | code read | high | It returns a full result list when open. |
| C3 | Every finding includes explanation and may include agent impact, review status, and nested evidence. | prototype/copilot-studio-knowledge-compiler/app.js:238 | code read | high | This is valuable detail but creates unbounded row height. |
| C4 | The disclosure summary alone has a 52px minimum height; each open finding adds at least 24px vertical padding plus its text and evidence. | prototype/copilot-studio-knowledge-compiler/styles.css:2680 | code read | high | Finding list is a single column. |
| C5 | The page already has native modal-dialog infrastructure and focus-opening behavior that could be reused, but no existing findings drawer. | prototype/copilot-studio-knowledge-compiler/index.html:397 | code read | high | Reuse reduces implementation novelty only for a modal option. |
| C6 | The workspace can use up to 1440px, providing room for a desktop split view when findings rows become compact. | prototype/copilot-studio-knowledge-compiler/styles.css:343 | code read | high | Pane width still needs a product-defined minimum. |
| C7 | Existing responsive rules stack layouts at 960px, make dialogs viewport-sized below 760px, and convert discovery table rows into cards. | prototype/copilot-studio-knowledge-compiler/styles.css:2914 | code read | high | The findings pane can align with these established breakpoints. |

### External Evidence

| ID | Claim / finding | Source | URL | Retrieved | Version/date | Confidence |
|---|---|---|---|---|---|---|
| W1 | Fluent defines a drawer as a secondary surface for supplemental information related to the main content. | Fluent 2 Drawer | https://fluent2.microsoft.design/components/web/react/core/drawer/usage | 2026-09-12 | Current | high |
| W2 | Fluent recommends an inline drawer when users benefit from viewing and interacting with main and drawer content together. | Fluent 2 Drawer | https://fluent2.microsoft.design/components/web/react/core/drawer/usage | 2026-09-12 | Current | high |
| W3 | Fluent says overlay drawers are intrusive, modal by default, block content, and should be used cautiously for clear, quick tasks. | Fluent 2 Drawer | https://fluent2.microsoft.design/components/web/react/core/drawer/usage | 2026-09-12 | Current | high |
| W4 | WAI-ARIA defines a disclosure as a button controlling in-flow hidden content, with Enter or Space activation and aria-expanded state. | WAI-ARIA APG Disclosure | https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/ | 2026-09-12 | Current | high |
| W5 | A modal dialog makes the underlying page inert, traps Tab navigation, closes on Escape, and should restore focus to its invoker. | WAI-ARIA APG Modal Dialog | https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/ | 2026-09-12 | Current | high |
| W6 | GOV.UK recommends details for optional information but says not to hide information most users need. | GOV.UK Details | https://design-system.service.gov.uk/components/details/ | 2026-09-12 | Current | high |
| W7 | Fluent drawer anatomy requires a descriptive header and body; long drawer bodies should scroll, and drawer text should be concise and scannable. | Fluent 2 Drawer | https://fluent2.microsoft.design/components/web/react/core/drawer/usage | 2026-09-12 | Current | high |
| W8 | Fluent notes inline drawers commonly collapse at product-defined breakpoints and can be invoked again in the narrow layout. | Fluent 2 Drawer | https://fluent2.microsoft.design/components/web/react/core/drawer/usage | 2026-09-12 | Current | high |
| W9 | Fluent says popovers are for brief, nonessential context and recommends another surface such as a panel when information is essential or robust. | Fluent 2 Popover | https://fluent2.microsoft.design/components/web/react/core/popover/usage | 2026-09-12 | Current | high |
| W10 | WAI permits an aside element as a named complementary landmark for supporting content related to the main content. | WAI-ARIA APG Complementary Landmark | https://www.w3.org/WAI/ARIA/apg/patterns/landmarks/examples/complementary.html | 2026-09-12 | Current | high |
| W11 | WCAG 2.2 Reflow requires information and functionality to remain available at 320 CSS pixels; although tables can require two-dimensional layout, content inside individual cells still needs to reflow. | WCAG 2.2 Understanding 1.4.10 | https://www.w3.org/WAI/WCAG22/Understanding/reflow.html | 2026-09-12 | 2023 | high |
| W12 | WCAG 2.2 Focus Order requires keyboard focus to preserve meaning and operability and cautions against focus order that conflicts with the visual relationship. | WCAG 2.2 Understanding 2.4.3 | https://www.w3.org/WAI/WCAG22/Understanding/focus-order.html | 2026-09-12 | 2023 | high |
| W13 | GOV.UK says accordions may help familiar caseworkers reveal and compare related content, but users can miss hidden content and accordions require supporting user evidence. | GOV.UK Accordion | https://design-system.service.gov.uk/components/accordion/ | 2026-09-12 | Current | high |
| W14 | WCAG 2.2 Focus Not Obscured identifies persistent non-modal overlays as a risk and lists displacement, reflow, or modal focus containment as safe approaches. | WCAG 2.2 Understanding 2.4.11 | https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html | 2026-09-12 | 2023 | high |
| W15 | GOV.UK says tabs are unsuitable when users need to compare information across tabs and notes that tabs avoid pushing other content down only when one section at a time is appropriate. | GOV.UK Tabs | https://design-system.service.gov.uk/components/tabs/ | 2026-09-12 | Current | high |

### Contradictions / Conflicts

* GOV.UK recognizes accordions as useful for familiar caseworkers and comparing selectively revealed content (W13), but Shaper's current accordion-like row disclosure is the reported usability failure and its nested evidence creates unbounded height (C3-C4). Retain a compact row summary, not inline full detail.
* Fluent supports both inline and overlay drawers (W2-W3). Inline better preserves list context, while modal overlay is safer when space is constrained. The recommendation intentionally changes behavior at the established responsive breakpoint (C7).
* Hiding details improves scanability but can reduce discoverability (W6, W13, W15). Finding count, highest urgency, and a plainly labelled action must remain always visible.

## Findings Mapped to Questions and Evidence

| Question | Finding | Evidence IDs | Confidence | Decision or readiness implication |
|---|---|---|---|---|
| Q1 | The row expansion is unbounded because the table cell contains every full finding and nested evidence disclosure. | C1-C4 | high | Move long-form content out of row flow. |
| Q2 | Fluent supports drawers as contextual secondary surfaces and distinguishes simultaneous inline use from intrusive overlays. | W1-W3 | high | Prioritize an inline drawer/master-detail pattern for deeper evaluation. |
| Q3 | A meaningful summary must remain visible; hiding review-critical information entirely conflicts with progressive-disclosure guidance. | W4, W6 | high | Keep count, urgency, and review action in the row. |
| Q2 | A popover is too constrained and nonessential by design; a drawer supports structured contextual detail. | W7-W9 | high | Reject popover; use a drawer/pane. |
| Q3 | A named complementary pane is appropriate on wide layouts, but the design must adapt at narrow widths and preserve logical focus movement. | W8, W10-W12 | high | Use inline pane on wide screens and modal/full-width behavior on narrow screens; verify interaction and announcements dynamically. |
| Q4 | Drawers can obscure focus or compress content, while accordion and tabs can hide critical information or impair comparison. | C6-C7, W13-W15 | high | Require reflowing inline behavior, modal containment on narrow screens, and a meaningful always-visible summary. |

## Key Discoveries

* The vertical-space issue is structural, not cosmetic: each table row owns the complete detail hierarchy, including nested evidence.
* A compact row should answer three questions without opening anything: how many findings, whether any are high priority, and how to review them.
* A right-hand inline findings pane is the best desktop fit because it keeps documents and details simultaneously available.
* The pane must adapt to a modal/full-width view at the existing narrow-layout breakpoint; a fixed two-column view would fail the spirit of reflow.
* Popovers are not appropriate for essential multi-paragraph findings.
* Accessibility cannot be signed off from static markup alone. Keyboard traversal, focus visibility/restoration, accessibility-tree announcements, 200% zoom, 320px reflow, and text spacing require runtime or manual evidence.

## Alternatives and Decision State

### Selected Recommendation

* Approach: Responsive master-detail: compact summary/action in each document row; complete findings in a selected-document right-hand pane on wide screens; the same view becomes a modal or full-width overlay below the layout breakpoint.
* Rationale: Removes unbounded details from table flow while keeping the list available for rapid review, preserves all finding detail, fits Fluent's inline-drawer purpose, and supports reflow through an adaptive narrow-screen mode.
* Evidence refs: C1-C5, W1-W12.
* Implementation impact: Replace row-level details with a button showing finding count, high-priority count, and "Review findings"; add a named, scrollable detail surface with document title, check count, complete finding list, nested evidence, close control, selected-row styling, and controlled responsive semantics.
* Confidence: medium-high pending contrarian wave.

### Alternative: Compact inline preview

* Approach: Show a bounded number of finding chips or lines within each row.
* Trade-offs: Minimal interaction change but either remains vertically variable or hides important impact/evidence behind another control.
* Evidence refs: C3-C4, W6, W13.
* Rejection rationale: Does not fully solve the root cause and creates arbitrary truncation.

### Alternative: Side panel

* Approach: Keep the row compact and open full findings in a persistent side panel.
* Trade-offs: Requires responsive state and focus behavior but supports continued table interaction.
* Evidence refs: W1-W2, W7-W8, W10-W12.
* Rejection rationale: Selected, with responsive modal behavior rather than a fixed-width-only panel.

### Alternative: Modal dialog

* Approach: Open full findings in a modal dialog.
* Trade-offs: Existing native-dialog infrastructure lowers implementation effort and provides strong focus containment, but every review interrupts access to the document list.
* Evidence refs: C5, W3, W5.
* Rejection rationale: Use only as the narrow-screen presentation, not the sole desktop interaction.

## Open Questions, Risks, and Residual Uncertainty

* Blocking: None.
* Important: User testing should confirm the exact breakpoint and preferred pane width; start with the existing 960px layout breakpoint.
* Follow-up: Validate focus movement, focus restoration, selected-row announcement, scrolling, 200% zoom, 320px reflow, text spacing, and screen-reader output after implementation.
* Residual uncertainty: Whether frequent reviewers prefer the pane to remain open while selecting successive rows; default to persistent on desktop and explicitly closable.

## Current Decisions

| Decision | Status | Owner / source | Rationale | Evidence IDs | Implications |
|---|---|---|---|---|---|
| Preserve complete findings and evidence | confirmed | Existing product contract | Compactness cannot remove review evidence | Prior product direction | Reject lossy summaries |
| Use responsive master-detail | selected | Research synthesis | Best balance of compactness, context, completeness, and responsive accessibility | C1-C7, W1-W15 | Desktop inline pane; narrow modal/full-width detail |
| Keep a meaningful row summary | selected | Research synthesis | Critical status must not disappear behind progressive disclosure | W6, W13, W15 | Show count, highest urgency, and labelled review action |

## Unresolved Decisions

| Decision | Smallest evidence or answer needed | Owner | Impact | Blocker status |
|---|---|---|---|---|
| Exact desktop pane width and breakpoint | Browser validation with representative one-, five-, and ten-finding documents at desktop and 200% zoom | implementation | Visual density and reflow | follow-up |
| Whether pane remains open when selecting another row | Lightweight user test or observed reviewer workflow | product | Review speed | follow-up |

## Potential Next Research

| Priority | Research item | Expected value | Trigger | Selected? | Related questions / evidence |
|---|---|---|---|---|---|
| M | Reviewer usability test with several documents and mixed severities | Confirm pane persistence, width, and summary wording | After prototype | no | Q2-Q4 |
| M | Manual NVDA/VoiceOver and magnifier pass | Decide announcement and focus behavior | After implementation | yes, for validation | Q3-Q4 |

## Planning Readiness

* Status: Ready.
* Decision state: Responsive master-detail selected.
* Evidence basis: C1-C7 and W1-W15.
* Preconditions met: Current cause, alternatives, accessibility constraints, responsive behavior, and contrarian risks are documented.
* Blockers: None.
* Smallest action to change readiness: Not applicable; implementation can be scoped.

## Closeout Record

| Field | Record |
|---|---|
| Research execution status | Complete |
| Completed waves | Wider, Deeper, Contrarian |
| Lane evidence or inline fallback | Inline focused research |
| Research disposition | executed |
| Planning Readiness | Ready |
| Blockers | None |
| Continuation owner and state | user may request implementation |

## Advisory Next Step

| Field | Record |
|---|---|
| Research disposition | executed |
| Planning Readiness | Ready |
| Output mode and planning support | convergence; supports planning |
| Acting owner | user |
| Required gates or confirmations | User request to implement |
| Continuation result | advisory |
| Primary evidence file | .copilot-tracking/research/2026-09-12/compact-review-findings-research.md |
| Notes for planning or re-entry | Implement responsive master-detail and validate interaction, announcement, and reflow with adequate methods |

* Advisory only: rpi-research does not invoke a follow-on skill.
* Completion or limit-blocked basis: Focused research saturated after one complete three-wave cycle.

## Sources

* W1-W3, W7-W8 - Fluent 2 Drawer - https://fluent2.microsoft.design/components/web/react/core/drawer/usage (retrieved 2026-09-12, current)
* W4 - WAI-ARIA APG Disclosure - https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/ (retrieved 2026-09-12, current)
* W5 - WAI-ARIA APG Modal Dialog - https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/ (retrieved 2026-09-12, current)
* W6 - GOV.UK Details - https://design-system.service.gov.uk/components/details/ (retrieved 2026-09-12, current)
* W9 - Fluent 2 Popover - https://fluent2.microsoft.design/components/web/react/core/popover/usage (retrieved 2026-09-12, current)
* W10 - WAI-ARIA APG Complementary Landmark - https://www.w3.org/WAI/ARIA/apg/patterns/landmarks/examples/complementary.html (retrieved 2026-09-12, current)
* W11 - WCAG 2.2 Understanding 1.4.10 - https://www.w3.org/WAI/WCAG22/Understanding/reflow.html (retrieved 2026-09-12, 2023)
* W12 - WCAG 2.2 Understanding 2.4.3 - https://www.w3.org/WAI/WCAG22/Understanding/focus-order.html (retrieved 2026-09-12, 2023)
* W13 - GOV.UK Accordion - https://design-system.service.gov.uk/components/accordion/ (retrieved 2026-09-12, current)
* W14 - WCAG 2.2 Understanding 2.4.11 - https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html (retrieved 2026-09-12, 2023)
* W15 - GOV.UK Tabs - https://design-system.service.gov.uk/components/tabs/ (retrieved 2026-09-12, current)

## Artifact Self-Check

* [x] Every research question is answered.
* [x] Wider, Deeper, and Contrarian waves are complete.
* [x] Research posture and boundaries are recorded.
* [x] Every finding has stable evidence.
* [x] Alternatives and decision state are complete.
* [x] Planning Readiness is evidence-backed.

## Artifacts

| Artifact | Description |
|---|---|
| [.copilot-tracking/research/2026-09-12/compact-review-findings-research.md](.copilot-tracking/research/2026-09-12/compact-review-findings-research.md) | Primary research brief, three-wave evidence, alternatives, recommendation, and readiness decision |

## Next Steps

Request implementation of the responsive findings master-detail pattern. In an RPI workflow, the eligible next command is `/rpi-plan implement the responsive findings master-detail recommendation`.
