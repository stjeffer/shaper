# Delete Knowledge Estate Research

## Research Brief

* Topic: Add a safe, discoverable way to delete a knowledge estate.
* Purpose: Support administrator-requested estate removal from the authenticated workspace.
* Scope: Existing estate lifecycle API, authorization, confirmation semantics, portfolio state, and UI.
* Non-goals: Redesign archival policy or add bulk deletion.
* Posture: Focused, based on a bounded feature request and existing lifecycle implementation.
* Output mode: Convergence.

## Cycle 1

### Wider Wave

* C1: `src/shaper/interfaces/http.py:433` exposes archive and purge operations.
* C2: `src/shaper/interfaces/http.py:447` requires the exact phrase `PURGE {estate name}` before removal.
* C3: `src/shaper/application/estates.py:507` restricts purge to collection administrators and writes a tombstone after deleting estate content.
* C4: `prototype/copilot-studio-knowledge-compiler/app.js:196` renders the portfolio but exposes no lifecycle-removal action.

### Deeper Wave

* C5: `src/shaper/application/estates.py:526` removes stored bytes before repository records, preserving the existing deletion boundary.
* C6: `tests/test_estates.py:355` proves that exact confirmation leaves a tombstone and removes estate and source records.
* C7: `prototype/copilot-studio-knowledge-compiler/index.html:100` already has an estate heading suitable for one contextual destructive action.

### Contrarian Wave

* Archive-only behavior would be recoverable but does not satisfy the explicit deletion request.
* A one-click list-row trash icon would be faster but creates a high accidental-deletion risk.
* Reimplementing backend deletion would duplicate an already tested and authorized purge path.

## Synthesis

* Selected approach: Add a contextual Delete estate action to the estate heading and an explicit confirmation dialog that requires the exact estate name. The browser constructs the backend's guarded purge phrase and refreshes the portfolio after success.
* Rejected alternatives: archive-only does not delete; one-click deletion is insufficiently safe; new backend semantics are unnecessary.
* Risk: Deletion is irreversible. Mitigate with explicit warning, exact-name input, disabled submit until matching, server-side phrase confirmation, and existing administrator authorization.
* Research disposition: Executed.
* Planning Readiness: Ready.

## Evidence Coverage

* Existing backend contract: C1, C2, C3, C5, C6.
* UI gap and insertion point: C4, C7.
* No external research was needed because the repository already defines the governing semantics.
