---
title: Getting started with Shaper
description: Run Shaper locally, create a Knowledge Estate, and call the API
ms.topic: how-to
---

## Prerequisites

* Python 3.11
* [`uv`](https://docs.astral.sh/uv/) for dependency management and running
  commands

## Install and run locally

```bash
uv sync
uv run uvicorn shaper.interfaces.http:app --reload
```

The lockfile excludes packages uploaded in the most recent 30 days. Local
tests use deterministic fakes; cloud adapters and live integration tests
require explicit credentials.

Before committing changes, run the same checks as CI:

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest --cov=shaper
uv run shaper-schema --check
```

## Configure runtime settings

All settings use the `SHAPER_` prefix (for example `SHAPER_COLLECTION_ID`,
`SHAPER_DATABASE_PATH`, `SHAPER_OIDC_ISSUER`). See the
[runtime configuration table](../README.md#runtime-configuration) in the
README for the full list and each setting's purpose. Production startup fails
when collection, identity, compatibility, or PostgreSQL settings are absent.

## Use the authenticated workspace

Once the service is running and authentication is configured, sign in at
`/concept/` to use the Knowledge Estate workspace. The workspace walks
through four task-oriented stages for an estate:

1. **Sources** — create a named estate, register URL or SharePoint sources,
   and upload individual files or bounded ZIP bundles.
2. **Discover and assess** — run discovery to produce a readiness report per
   document, with evidence-grounded Results such as weak structure,
   freshness risk, or missing question coverage.
3. **Recommend** — generate version-pinned transformation proposals for
   selected documents and record an approve or decline decision.
4. **Transform and review** — approved proposals produce escaped semantic
   HTML artifacts (`shaper_{source_stem}.html`) that require a separate
   human review before the content can be retrieved.

See the [feature guide](../docs/features.md) for full detail on each stage,
the Results catalog, and estate lifecycle (archive and purge).

## Call the API directly

Shaper also exposes an authenticated REST API under `/v1` and an MCP
Streamable HTTP endpoint at `/mcp/`. Every request carries a signed OIDC
access token in the `Authorization` header. `SHAPER_AUTH_SCHEME` is
normally the RFC 6750 scheme name for OAuth 2.0 access tokens. Obtain
`SHAPER_AUTH_SCHEME` and `SHAPER_ACCESS_TOKEN` from your OIDC provider using
the client-credentials or delegated flow configured for
`SHAPER_OIDC_ISSUER`/`SHAPER_OIDC_AUDIENCE`. Then export both values, followed by the combined header as
`$SHAPER_AUTH_HEADER`, before running the following minimal estate-driven
flow:

```bash
export SHAPER_AUTH_SCHEME="..."     # obtained from your OIDC provider
export SHAPER_ACCESS_TOKEN="..."    # obtained from your OIDC provider
export SHAPER_AUTH_HEADER="Authorization: ${SHAPER_AUTH_SCHEME} ${SHAPER_ACCESS_TOKEN}"

# Create an estate
curl -X POST "$SHAPER_URL/v1/estates" \
  -H "$SHAPER_AUTH_HEADER" \
  -H "Content-Type: application/json" \
  -d '{"name": "policy-knowledge", "description": "Policy documents"}'

# Register a source
curl -X POST "$SHAPER_URL/v1/estates/{estate_id}/sources" \
  -H "$SHAPER_AUTH_HEADER" \
  -H "Content-Type: application/json" \
  -d '{"kind": "url", "location": "https://example.com/policy.pdf"}'

# Start discovery (assessment) for the estate
curl -X POST "$SHAPER_URL/v1/estates/{estate_id}/discovery-runs" \
  -H "$SHAPER_AUTH_HEADER"

# Poll workflow runs until the discovery run reaches a terminal state
curl "$SHAPER_URL/v1/estates/{estate_id}/runs" -H "$SHAPER_AUTH_HEADER"

# Retrieve discovery reports once the run completes
curl "$SHAPER_URL/v1/estates/{estate_id}/discovery-reports" \
  -H "$SHAPER_AUTH_HEADER"
```

See [API Reference](API-Reference.md) for the complete endpoint summary and
[improvement reporting](../docs/improvement-reporting.md) for the paired
evaluation contract used to measure knowledge-shaping improvement.

## Deploy to Azure

Local development is useful for exploration, but production use requires an
Azure deployment with PostgreSQL, Container Apps, and a ClamAV scanning
sidecar. See [Deployment](Deployment.md) for a summary and
[docs/deployment.md](../docs/deployment.md) for full prerequisites, the
deploy script, and rollback steps.
