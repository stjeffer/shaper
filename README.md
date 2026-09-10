---
title: Shaper
description: Transform unmanaged enterprise content into trusted, agent-ready knowledge
---

## Knowledge transformation for enterprise agents

Shaper is an Azure-native Knowledge Transformation Platform. It assesses
fragmented content estates, models the knowledge they contain, recommends
remediation, and prepares trusted knowledge assets for human-approved
publication.

> [!IMPORTANT]
> Shaper is not an agent. It is a platform that coordinates Assessment,
> Knowledge, Transformation, Governance, and Agent Readiness agents. The
> platform retains deterministic control of authorization, evidence lineage,
> workflow, approval, and publication.

Shaper fills the gap between content governance and content retrieval. It does
not replace SharePoint, a RAG pipeline, or an enterprise search service. Those
systems manage, find, and retrieve content. Shaper improves the quality,
consistency, authority, and agent readiness of the knowledge they consume.

## Product workflow

### Discover

Connect SharePoint sites, OneDrive locations, file shares, wikis, and knowledge
repositories. Shaper analyzes the estate without modifying source content and
produces an Agent Readiness Assessment.

### Understand

Build a knowledge model that groups related sources into business topics. The
assessment identifies review candidates for duplication, contradiction,
staleness, authority, ownership, and coverage.

### Recommend

Prioritize interventions such as consolidation, authority review, archival,
metadata enrichment, summaries, FAQs, procedures, and canonical business
guidance. Recommendations create value before any transformation runs.

### Transform

Prepare approved work through one of three modes:

* Safe mode creates derivative summaries, FAQs, metadata, knowledge cards, and
  topic summaries while leaving originals untouched
* Guided rewrite proposes document improvements for human review
* Knowledge consolidation prepares a canonical source, supporting FAQ,
  knowledge graph, and agent-ready knowledge package

All modes stop at an approval boundary. Publication remains a human-governed
action.

### Govern

Continuously detect new duplication, emerging contradictions, missing ownership,
stale knowledge, and unhealthy canonical sources. The current MVP identifies
conditions that require monitoring. Recurring schedules and managed checkpoints
remain production follow-up work.

## Agent Readiness Assessment

The assessment reports a score from 0 to 100 across three dimensions:

* Content quality: structure, readability, metadata completeness, and freshness
* Knowledge quality: duplication, contradictions, authority, and coverage
* Agent readiness: retrieval effectiveness, procedural clarity, FAQ coverage,
  chunking suitability, and semantic consistency

Every result includes metric explanations, evidence references, limitations,
and assessment coverage. Unavailable metrics do not silently receive positive
values. Duplicate and contradiction results are review-required candidates,
not autonomous decisions, and authority is never inferred from recency alone.

> [!IMPORTANT]
> The current score is an uncalibrated deterministic heuristic. It is not an
> accuracy percentage or model confidence score. Production quality claims
> require calibration against representative, human-reviewed estates.

## Current MVP

The implemented vertical slice includes:

* Named, durable Knowledge Estates containing SharePoint or URL registrations,
  individual uploads, and bounded ZIP bundles
* Immutable source versions and per-document readiness, evidence coverage, and
  reshaping-effort reports
* Selection-scoped recommendations with input/output token ranges, an expected
  total, and an enforced maximum before model use
* Append-only approve or decline decisions pinned to the exact source,
  recommendation, estimate, estimator, and model deployment
* Approved-only transformation into escaped semantic HTML using estate-owned
  names such as `shaper_{source_stem}.html`
* Separate human output review before an artifact can be retrieved
* PostgreSQL-backed Azure workflow state and local SQLite development state
* A live authenticated estate workspace at `/concept/`

SharePoint sources remain truthful registrations until Microsoft Graph consent
and synchronization are configured. Confluence, ServiceNow, arbitrary wiki
crawling, distributed workers, and score calibration remain follow-up work.

## Azure architecture

The current development deployment packages Shaper as one non-root OCI
container on Azure Container Apps. One ASGI process exposes:

* Authenticated HTTP endpoints on `/v1`
* MCP Streamable HTTP on `/mcp/`
* Liveness and dependency-aware readiness probes on `/health`
* The authenticated Knowledge Estates workspace on `/concept/`

Azure Database for PostgreSQL persists estates, workflows, decisions, token
usage, reviews, and artifact manifests. Azure Container Registry, a
user-assigned managed identity, Log Analytics, and an Azure Files share support
the deployment. A ClamAV sidecar scans uploads before inventory creation.
Container Apps authentication provides interactive Entra sign-in, while
persisted collection grants remain the application authorization boundary.

Product surfaces are prioritized as the Azure-native platform, REST API, Copilot
Agent, SharePoint integration, Teams integration, then Foundry integration.
SharePoint is a source and delivery surface, not the product boundary.

See [deployment guidance](docs/deployment.md) for the current and target Azure
topologies and [operations guidance](docs/operations.md) for monitoring,
recovery, and retention. See [platform architecture](docs/architecture.md) for
the C4 model and specialist-agent responsibility boundaries.

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
adapters and live integration tests require explicit credentials. Local tests
use deterministic fakes.

## Runtime configuration

All settings use the `SHAPER_` prefix.

| Setting | Purpose |
|---|---|
| `SHAPER_COLLECTION_ID` | Collection served by this deployment |
| `SHAPER_DATABASE_PATH` | SQLite workflow-state path |
| `SHAPER_POSTGRES_URL` | Required production PostgreSQL connection URL |
| `SHAPER_RELEASE_ROOT` | Root containing `current.json` and immutable releases |
| `SHAPER_UPLOAD_ROOT` | Quarantined upload staging root |
| `SHAPER_OIDC_ISSUER` | Trusted OIDC issuer |
| `SHAPER_OIDC_AUDIENCE` | Required token audience |
| `SHAPER_PUBLIC_URL` | Externally reachable HTTPS service URL |
| `SHAPER_TRUST_INGRESS_IDENTITY` | Trust Container Apps identity headers |
| `SHAPER_BOOTSTRAP_TENANT_ID` | Tenant for the initial collection administrator |
| `SHAPER_BOOTSTRAP_PRINCIPAL_ID` | Object ID for the initial collection administrator |
| `SHAPER_CLAMD_HOST` | Private ClamAV daemon host |
| `SHAPER_CLAMD_PORT` | Private ClamAV daemon port |
| `SHAPER_AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint |
| `SHAPER_AZURE_OPENAI_DEPLOYMENT` | Chat model deployment |
| `SHAPER_AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | Embedding model deployment |
| `SHAPER_AZURE_OPENAI_USE_MANAGED_IDENTITY` | Use workload identity instead of an API key |

Production startup fails when collection, identity, process-local compatibility
state, or PostgreSQL settings are absent. The readiness probe checks local
compatibility state, PostgreSQL, ClamAV, and the compile worker.

## Evaluation status

The repository includes a 30-case synthetic regression dataset and
programmatic comparison gates for the existing transformation kernel. It proves
evaluation and blocking mechanics only. A representative corpus,
evaluation-design interview, sample review, configured live run,
evaluation-owner approval, and domain-reviewer approval remain required before
production quality claims or automatic publication.

Authenticated callers can submit unchanged baseline and shaped outcomes to
`POST /v1/evaluations/improvement`. The report returns baseline and shaped pass
rates, absolute and relative change, sample size, paired-case movements, a
deterministic 95% bootstrap interval, limitations, and a content-addressed input
hash. It labels unreviewed or underpowered results as observation-only and never
presents evaluator confidence as accuracy.

See [improvement reporting](docs/improvement-reporting.md) for the request
contract, metric interpretation, and claim safeguards.
