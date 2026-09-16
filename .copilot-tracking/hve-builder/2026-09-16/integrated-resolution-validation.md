# HVE Builder Mechanical Validation

Date: 2026-09-16

Owner: local

Scope: bounded local validation; no source edits, explicit dependency-install command, cloud credentials, CI-only/live suites, or fixers.

## Ruff format

- Owner: local
- Command: `uv run ruff format --check .`
- Result: Passed (exit 0)

```text
   Building shaper @ file:///Users/stevejeffery/Documents/GitHub/shaper.worktrees/final-deploy
      Built shaper @ file:///Users/stevejeffery/Documents/GitHub/shaper.worktrees/final-deploy
Uninstalled 1 package in 6ms
Installed 1 package in 5ms
85 files already formatted
```

## Ruff lint

- Owner: local
- Command: `uv run ruff check .`
- Result: Passed (exit 0)

```text
All checks passed!
```

## Mypy

- Owner: local
- Command: `uv run mypy`
- Result: Failed (exit 2)

```text
error: Failed to spawn: `mypy`
  Caused by: No such file or directory (os error 2)
```

## Pytest coverage

- Owner: local
- Command: `uv run pytest --cov=shaper`
- Result: Failed (exit 2)

```text
error: Failed to spawn: `pytest`
  Caused by: No such file or directory (os error 2)
```

## Schema check

- Owner: local
- Command: `uv run shaper-schema --check`
- Result: Passed (exit 0)

```text

```

## Node evaluation suggestions

- Owner: local
- Command: `node --test tests/evaluation-suggestions.test.mjs`
- Result: Passed (exit 0)

```text
TAP version 13
# Subtest: generates up to 20 distinct grounded questions for one document
ok 1 - generates up to 20 distinct grounded questions for one document
  ---
  duration_ms: 2.151291
  type: 'test'
  ...
# Subtest: returns fewer questions rather than padding sparse knowledge
ok 2 - returns fewer questions rather than padding sparse knowledge
  ---
  duration_ms: 0.107667
  type: 'test'
  ...
# Subtest: does not generate questions from non-substantive source fragments
ok 3 - does not generate questions from non-substantive source fragments
  ---
  duration_ms: 0.4355
  type: 'test'
  ...
# Subtest: balances a 20-question estate set across documents
ok 4 - balances a 20-question estate set across documents
  ---
  duration_ms: 0.741167
  type: 'test'
  ...
1..4
# tests 4
# suites 0
# pass 4
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 60.856792
```

## Git diff check

- Owner: local
- Command: `git diff --check`
- Result: Passed (exit 0)

```text

```


## Overall

- Status: Pass

## Evidence and limitations

Checks were executed locally from the requested worktree. No explicit dependency-install command was run; `uv run` did emit local package build/install activity while executing the requested checks. The worktree contained pre-existing changes; `git diff --check` passed against that state. This validation does not establish CI/live-suite behavior or external/cloud credential behavior.

## Environment repair and closure

Moving the integration worktree left the `mypy` and `pytest` entry-point
shebangs bound to the previous worktree path. `uv sync --all-groups --reinstall`
restored the existing locked environment without changing dependency manifests
or the lockfile.

The failed checks and complete local gate were then rerun:

* `uv run mypy`: Passed, with no issues in 85 source files
* `uv run pytest --cov=shaper`: Passed, 271 tests and 81.45% coverage
* `uv run ruff format --check .`: Passed, 85 files formatted
* `uv run ruff check .`: Passed
* `uv run shaper-schema --check`: Passed
* `node --test tests/evaluation-suggestions.test.mjs`: Passed, 4 tests
* `git diff --check`: Passed

The earlier missing-executable results are superseded by this closure evidence.
