# Delete Knowledge Estate Phase Details

<!-- rpi:phase id=P01 -->
## P01: Implement Safe Estate Deletion

### Context

The backend already provides administrator-authorized purge with a tombstone and exact phrase confirmation. The authenticated workspace does not expose it.

<!-- rpi:task id=P01-T01 -->
### P01-T01: Add the Confirmed Delete Interaction

* Targets: `index.html`, `styles.css`, and `app.js`.
* Completion evidence: A destructive estate-heading action opens a named modal; exact-name matching gates submission; success uses the purge endpoint and refreshes the portfolio; cancel and failure preserve state.

<!-- rpi:task id=P01-T02 -->
### P01-T02: Validate and Deploy

* Targets: static architecture tests, browser interaction checks, JavaScript syntax, Azure build and deployment.
* Completion evidence: Targeted checks pass and the healthy live revision serves the updated cache-keyed assets.
