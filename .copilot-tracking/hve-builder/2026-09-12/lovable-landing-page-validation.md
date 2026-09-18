# Lovable landing page validation

- Target: `docs/lovable-landing-page-brief.md`
- Owner: local
- Overall validation: Pass

## Checks

1. `git diff --check -- docs/lovable-landing-page-brief.md .copilot-tracking/research/2026-09-12/lovable-landing-page-research.md .copilot-tracking/hve-builder/2026-09-12/`
   - Owner: local
   - Status: Passed
   - Result: clean

2. Relative Markdown links
   - Owner: local
   - Status: Passed
   - Result: 4/4 resolved after ignoring fragments

3. Backtick check codes vs `DOCUMENT_CHECK_CODES` + `BASELINE_CHECK_CODES`
   - Owner: local
   - Status: Passed
   - Result: 29/29 matched; no missing or extra codes

4. H1 / required anchors / required phrases
   - Owner: local
   - Status: Passed
   - Result: exactly one H1; all 10 nav anchors present; required phrases present

5. Current feature-claim guardrails
   - Owner: local
   - Status: Passed
   - Result: no current claim says `registration/listing`; no upload-contract claim enumerates PDF/DOCX/Markdown/text as implemented

## Unexpected mutations

- None observed.

## Limitations

- Markdown-link resolution checked only for relative paths in the target file.
- Phrase validation used exact/mechanical text matching.
