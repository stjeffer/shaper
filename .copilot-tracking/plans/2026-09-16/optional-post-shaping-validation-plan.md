<!-- markdownlint-disable-file -->
# RPI Plan: Optional post-shaping validation

## Metadata

* Task ID: optional-post-shaping-validation
* Scope: Full plan
* Status: In progress

## User Decisions and Requirements

* Preservation diagnostics must not block all reshaping.
* The browser control must govern the transformation run, not estate evaluation settings.
* Evidence-integrity failures remain non-bypassable.
* Retained findings must be visible before publication and acknowledged during approval.
* User-facing scores out of 100 must not appear.

<!-- rpi:phase id=P01 -->
## P01 Implement validation authority

<!-- rpi:task id=P01-T01 -->
### P01-T01 Separate integrity gates from preservation diagnostics

* [x] Preserve non-bypassable source and exclusion checks.
* [x] Convert bypassed preservation blockers into review findings.

<!-- rpi:task id=P01-T02 -->
### P01-T02 Wire run-level control

* [x] Extend transformation request contracts.
* [x] Pass the setting through streaming and application layers.
* [x] Remove the estate-setting side effect.

<!-- rpi:phase id=P02 -->
## P02 Implement artifact review governance

<!-- rpi:task id=P02-T01 -->
### P02-T01 Persist and present findings

* [x] Store validation findings on generated artifacts.
* [x] Present findings without score cards.

<!-- rpi:task id=P02-T02 -->
### P02-T02 Require acknowledgment

* [x] Require approval to acknowledge the artifact's complete finding set.

<!-- rpi:phase id=P03 -->
## P03 Validate, document, and deploy

<!-- rpi:task id=P03-T01 -->
### P03-T01 Add regression coverage

* [x] Cover advisory preservation behavior.
* [x] Cover non-bypassable integrity behavior.

<!-- rpi:task id=P03-T02 -->
### P03-T02 Update documentation

* [x] Align architecture, features, deployment, and operations guidance.

<!-- rpi:task id=P03-T03 -->
### P03-T03 Validate and release

* [x] Run repository validation.
* [ ] Commit, push, deploy, and verify production.

## Follow-Up Items

* None.
