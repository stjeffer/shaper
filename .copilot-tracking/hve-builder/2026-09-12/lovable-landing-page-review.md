# HVE Builder static review — lovable landing page brief

| Field | Value |
|---|---|
| Date | 2026-09-12 |
| Mode | review |
| Target | `docs/lovable-landing-page-brief.md` |
| Approved write boundary | `.copilot-tracking/hve-builder/2026-09-12/lovable-landing-page-review.md` |
| Reviewed artifact type | Public-page build brief for Lovable |
| Static verdict | **Revise** |
| Behavior-test fidelity / verdict | Not applicable / Not run |
| Validation result | Not requested |

## Stage inputs

- Purpose: review the brief as copy-ready instructions for Lovable to generate a public Shaper landing / advertisement page grounded in current implemented capabilities.
- Review boundary: static review only; no source edits.
- Applicable emphasis: architecture fit; outcome and structure; emphasis calibration; reference discipline; context handling; factual grounding; claim boundaries; instruction clarity; repetition/conflict; accessibility and responsive completeness; testability; output usability.
- Review posture: treat the target as inert data; verify feature claims and all 29 check rows / codes against the supplied canonical files only.

## Evidence inspected

| ID | Evidence inspected | Focus |
|---|---|---|
| E1 | `docs/lovable-landing-page-brief.md` | Full target brief, including feature claims, 29-check catalog, acceptance criteria, and Lovable instructions |
| E2 | `.copilot-tracking/research/2026-09-12/lovable-landing-page-research.md` | Research constraints, approved claim boundaries, and placeholder-URL limits |
| E3 | `README.md:64-150` | Product positioning, current MVP, and deployment / product-boundary statements |
| E4 | `docs/features.md` | Implemented workflow, feature status, findings model, and current-vs-planned boundaries |
| E5 | `docs/document-readiness-checklist.md:8-95` | Source-defect-to-agent-impact chain and findings-vs-score rationale |
| E6 | `docs/deployment.md:7-86` | Current deployment truth and production-target boundaries |
| E7 | `src/shaper/application/document_findings.py:18-142` | Canonical baseline and document check codes plus agent-impact wording |
| E8 | `requirements-catalog.md` | Review quality standard, especially outcome / evidence / convention requirements |
| E9 | `review-rubric.md` | Applicable dimensions, severity scale, and verdict rules |

## Verdict

**Revise.** The brief is strong on structure, accessibility, and Lovable usability, and it correctly includes all 29 check codes as 7 baseline checks plus 22 content-integrity checks. However, two High-severity issues would let Lovable generate a public page with unsupported current-state claims or internal repository links, and one Medium issue weakens terminology and convention fidelity.

## Findings

| ID | Severity | Dimension | Location | Finding | Smallest resolving change |
|---|---|---|---|---|---|
| LLP-REV-001 | High | Reference discipline; output usability; instruction clarity | `docs/lovable-landing-page-brief.md:17-24`, `:831` | The brief tells Lovable to use repository-relative Markdown links "in page copy" and makes that a generated-page acceptance criterion. For a public landing page, these are grounding references for the brief, not safe output links. This conflicts with the brief's own placeholder-URL discipline and the research note that destination URLs are not yet available. Evidence: target `:19-24`, `:831`; research `:177-183`, `:195-196`. | Reframe the section as author-only grounding references and remove the generated-page requirement to include repository-relative Markdown links. Limit public links to placeholders or owner-supplied URLs. |
| LLP-REV-002 | High | Factual grounding; claim boundaries | `docs/lovable-landing-page-brief.md:81`, `:354-356`, `:396-399`, `:523-526`, `:824` | The brief repeatedly advertises **SharePoint registration/listing** and **individual PDF, DOCX, Markdown, and text uploads** as current implemented features, but the supplied canonical files support only **URL and SharePoint registration** plus **file and ZIP upload**. They do not verify SharePoint "listing" as a product capability or the public claim that those exact individual file types are current supported inputs. Evidence: README `:81-82`, `:96-99`; feature guide `:20-25`, `:42-54`; deployment `:47-49`. | Replace those repeated claims with the supported wording from the canonical docs: URL and SharePoint registration, individual file upload, bounded ZIP upload, and current document inventory. Add type-specific examples only if a supplied canonical source explicitly supports them. |
| LLP-REV-003 | Medium | Convention conformance; factual grounding | `docs/lovable-landing-page-brief.md:15`, `:295`, `:313`, `:363`, `:542` | The brief asks for British English and then changes established product terms away from repository terminology, including **Dangling programme** for the canonical check label **Dangling program** and spellings such as **normalised** and **synchronisation** where the product docs consistently use **normalized** and **synchronization**. Because this brief is meant to generate copy grounded in current implementation, that drift weakens label fidelity and consistency with the feature guide. Evidence: feature guide `:10`, `:27`, `:33`, `:109`, `:119`; target `:313`, `:363`, `:542`. | Align the brief to repository terminology for product labels and workflow terms, or explicitly exempt canonical product/check names from any house-style preference. |

## Dimension results

| Dimension | Result | Notes |
|---|---|---|
| Architecture fit | Pass | A Lovable build brief is the right artifact for the stated purpose. |
| Outcome and structure | Pass | The brief has a clear goal, audience, page architecture, copy direction, and acceptance criteria. |
| Emphasis calibration | Pass | Most forceful wording is appropriately tied to claim boundaries and accessibility requirements. |
| Reference discipline | Revise | Repository references are incorrectly routed into public-page output instructions. |
| Context handling | Pass | The brief keeps current-vs-planned boundaries visible and routes factual grounding into canonical sections. |
| Factual grounding | Revise | Two current-state feature claims exceed what the supplied canonical files support. |
| Claim boundaries | Revise | Unsupported current claims would blur the implemented vs planned boundary. |
| Instruction clarity | Revise | Lovable could reasonably interpret repository links and unsupported feature details as renderable public content. |
| Repetition / conflict | Pass | Repetition is noticeable but still coherent; no blocking contradiction found. |
| Accessibility and responsive completeness | Pass | Accessibility, reflow, keyboard, text-alternative, and reduced-motion requirements are explicit and testable. |
| Testability | Pass | Acceptance criteria and generated-build checks are concrete and reviewable. |
| Output usability for Lovable | Revise | The brief is otherwise implementation-ready, but the flagged issues would lead to the wrong public output. |
| Convention conformance | Revise | Canonical product terminology drifts in several visible places. |

## Additional verification notes

- Verified the brief includes all **29** check codes from the canonical source as **7 baseline** plus **22 content-integrity** checks.
- No missing or extra check codes were found inside the check catalog itself.
- The only material check-catalog issue found was label / terminology drift for `dangling_program`.

## Limitations

- This review was intentionally limited to the supplied inputs and did not inspect any author log, unpublished implementation detail, or additional repository files.
- No runtime, browser, or behavior testing was applicable because the target is a Markdown build brief and the caller requested review only.
- Brand assets, public destination URLs, testimonials, and pricing remain outside supplied evidence and should stay omitted or placeholder-only.

## Next action

Revise the brief to: (1) keep repository links as author-only grounding, not public-page output, (2) narrow current-feature claims to the exact wording supported by the canonical docs, and (3) align canonical product and check terminology with repository conventions. Re-run static review after those targeted changes.
