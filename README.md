---
title: Shaper
description: Compile source documents into versioned, answer-ready evidence units
---

## Hosting model

Shaper is packaged as one non-root OCI container and deployed to Azure Container
Apps. One ASGI process exposes:

* Authenticated HTTP endpoints on `/v1`
* MCP Streamable HTTP on `/mcp/`
* Liveness and dependency-aware readiness probes on `/health`

The Azure deployment also provisions Azure Container Registry, a user-assigned
managed identity, Log Analytics, and an Azure Files share mounted at
`/mnt/state`. A ClamAV sidecar scans direct uploads before they enter the compile
workflow.

The current SQLite state profile is deliberately constrained to one replica.
Horizontal scaling requires a managed transactional database adapter.

See [deployment](docs/deployment.md) for Azure deployment and rollback, and
[operations](docs/operations.md) for monitoring, recovery, and retention.

## What Shaper produces

Shaper converts policies, FAQs, and related source documents into complete,
immutable releases of source-grounded answer units. Each unit retains source
versions, exact supporting spans, derivation metadata, review state, and
conflict information.

The bounded shaping agent can only read spans, neighboring context, approved
taxonomy, and conflicts. Deterministic application code owns authorization,
budgets, validation, human review, indexing, and publication.

## Local development

Python 3.11 and `uv` are required.

```bash
uv sync
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest --cov=shaper
uv run shaper-schema --check
```

The lockfile excludes packages uploaded in the most recent 30 days. Cloud
adapters and live integration tests require explicit credentials; local tests
use deterministic fakes.

## Runtime configuration

All settings use the `SHAPER_` prefix.

| Setting | Purpose |
|---|---|
| `SHAPER_COLLECTION_ID` | Collection served by this deployment |
| `SHAPER_DATABASE_PATH` | SQLite workflow-state path |
| `SHAPER_RELEASE_ROOT` | Root containing `current.json` and immutable releases |
| `SHAPER_UPLOAD_ROOT` | Quarantined upload staging root |
| `SHAPER_OIDC_ISSUER` | Trusted OIDC issuer |
| `SHAPER_OIDC_AUDIENCE` | Required token audience |
| `SHAPER_PUBLIC_URL` | Externally reachable HTTPS service URL |
| `SHAPER_CLAMD_HOST` | Private ClamAV daemon host |
| `SHAPER_CLAMD_PORT` | Private ClamAV daemon port |
| `SHAPER_AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint |
| `SHAPER_AZURE_OPENAI_DEPLOYMENT` | Chat model deployment |
| `SHAPER_AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | Embedding model deployment |
| `SHAPER_AZURE_OPENAI_USE_MANAGED_IDENTITY` | Use workload identity instead of an API key |

Production startup fails when the collection or identity settings are absent.
The readiness probe fails when SQLite or ClamAV is unavailable.

## Evaluation status

The repository includes a 30-case synthetic regression dataset and programmatic
comparison gates. It proves evaluation and blocking mechanics only. A
representative corpus, evaluation-design interview, sample review, configured
live run, evaluation-owner approval, and domain-reviewer approval remain
required before production quality claims or automatic publication.
