---
title: Shaper API reference
description: Summary of the authenticated HTTP and MCP surface exposed by Shaper
ms.topic: reference
---

## Overview

Shaper exposes one ASGI process with:

* Authenticated HTTP endpoints under `/v1`
* MCP Streamable HTTP at `/mcp/`
* Liveness and dependency-aware readiness probes at `/health`
* The authenticated Knowledge Estates workspace at `/concept/`

All endpoints except `/health/live`, `/health/ready`, and `/v1/demo/analysis`
require an authenticated principal. Estate endpoints additionally require a
collection-scoped role (`shaper:{collection}:query`, `:compile`, or `:admin`
depending on the operation). See
[estate authorization](../docs/architecture.md#agent-responsibility-boundaries)
and the [feature guide](../docs/features.md) for the workflow these endpoints
support.

## Health

| Method & path | Purpose |
|---|---|
| `GET /health/live` | Confirms the ASGI process can answer requests |
| `GET /health/ready` | Also checks SQLite, PostgreSQL, ClamAV, and the compile worker |

## Knowledge Estates

| Method & path | Purpose |
|---|---|
| `GET /v1/estates` | List estates in the caller's collection |
| `POST /v1/estates` | Create a named Knowledge Estate |
| `GET /v1/estates/{estate_id}` | Get estate detail |
| `POST /v1/estates/{estate_id}/archive` | Make an estate read-only |
| `POST /v1/estates/{estate_id}/purge` | Permanently remove an archived estate's content |
| `GET /v1/estates/{estate_id}/sources` | List registered sources |
| `POST /v1/estates/{estate_id}/sources` | Register a URL/SharePoint source or upload a file/ZIP |
| `GET /v1/estates/{estate_id}/documents` | List current document versions |
| `GET /v1/estates/{estate_id}/runs` | Poll durable discovery, recommendation, and transformation runs |

## Discover and assess

| Method & path | Purpose |
|---|---|
| `POST /v1/estates/{estate_id}/discovery-runs` | Start assessment for all current documents |
| `GET /v1/estates/{estate_id}/discovery-reports` | Retrieve per-document readiness reports and Results |

## Recommend and decide

| Method & path | Purpose |
|---|---|
| `POST /v1/estates/{estate_id}/recommendation-runs` | Generate version-pinned transformation proposals for selected documents |
| `GET /v1/estates/{estate_id}/proposals` | List proposals with token estimates |
| `GET /v1/estates/{estate_id}/decisions` | List recorded approve/decline decisions |

## Transform and review

| Method & path | Purpose |
|---|---|
| `POST /v1/estates/{estate_id}/transformation-runs` | Transform approved proposals into semantic HTML artifacts |
| `GET /v1/estates/{estate_id}/artifacts` | List transformed artifacts |
| `POST /v1/artifacts/{artifact_id}/approve` | Record the second human review required before content can be retrieved |
| `GET /v1/artifacts/{artifact_id}/evaluation` | Get citation-coverage, structure, and validation checks |
| `GET /v1/artifacts/{artifact_id}/content` | Retrieve approved artifact content |

## Assessment, platform analysis, and evaluation

| Method & path | Purpose |
|---|---|
| `POST /v1/assessments` | Assess a single submitted document profile |
| `POST /v1/platform/analyses` | Run one synchronous analysis across Assessment, Knowledge, Transformation, Governance, and Agent Readiness roles |
| `POST /v1/evaluations/improvement` | Compare paired baseline/shaped evaluation outcomes (see [improvement reporting](../docs/improvement-reporting.md)) |
| `GET /v1/demo/analysis` | Unauthenticated demo analysis for exploration |

## Legacy compilation workflow

| Method & path | Purpose |
|---|---|
| `POST /v1/uploads` | Upload a document for compilation |
| `POST /v1/jobs` | Submit a compile job |
| `GET /v1/jobs/{job_id}` | Get job status |
| `POST /v1/jobs/{job_id}/cancel` | Cancel a job |
| `GET /v1/jobs/{job_id}/review` | Get review status for a compiled candidate |
| `POST /v1/jobs/{job_id}/review/approve` | Approve a compiled candidate for publication |
| `POST /v1/query` | Query published knowledge units |
| `GET /v1/units/{unit_id}/explain` | Get evidence lineage for a published unit |

## Session

| Method & path | Purpose |
|---|---|
| `GET /v1/session` | Get the authenticated caller's identity and collection grants |

## MCP

`/mcp/` exposes the same estate and query capabilities over MCP Streamable
HTTP for agent clients. It requires a bearer token and is excluded from
interactive Container Apps ingress handling.
