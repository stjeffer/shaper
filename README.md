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

Prepare approved work as source-grounded semantic HTML while leaving the
original immutable source untouched. By default, deterministic preservation
findings remain visible for human review instead of blocking artifact generation.
Reviewers can request one bounded automatic repair for the current run.

Source identity, source version, cited evidence, candidate schema, exclusion
authority, and retention of intentionally excluded content remain non-bypassable.
A missing exclusion audit note becomes a visible review finding rather than
destroying the artifact. Publication remains a separate human-governed action
that requires acknowledgment of the current findings.

### Govern

Continuously detect new duplication, emerging contradictions, missing ownership,
stale knowledge, and unhealthy canonical sources. The current MVP identifies
conditions that require monitoring. Recurring schedules and managed checkpoints
remain production follow-up work.

## Agent Readiness Assessment

The Assess experience reports evidence-grounded findings across content quality,
knowledge quality, and agent readiness. Each finding states what was detected,
why it can affect retrieval or agent answers, where the evidence appears, and
whether content-owner review is required.

Findings cover structure, readability, metadata, freshness, duplication,
contradictions, authority, coverage, retrieval effectiveness, procedural
clarity, FAQ coverage, chunking suitability, and semantic consistency.
Duplicate and contradiction findings remain review candidates rather than
autonomous decisions, and authority is never inferred from recency alone.

## Current MVP

The implemented vertical slice includes:

* Named, durable Knowledge Estates containing SharePoint or URL registrations,
  individual uploads, and bounded ZIP bundles
* Estate-list document counts and current-version assessment coverage, with
  explicit no-documents, not-assessed, partially-assessed, and assessed states
* Immutable source versions with per-document findings and evidence coverage
* A transparent catalogue explaining all 31 deterministic checks, what each
  checks, and its likely impact on retrieval or agent answers
* Selection-scoped recommendations with input/output token ranges, an expected
  total, and an enforced maximum before model use
* A run-level option to try one automatic repair from preservation findings
* Append-only approve or decline decisions pinned to the exact source,
  recommendation, estimate, estimator, and model deployment
* Approved-only transformation into escaped semantic HTML using estate-owned
  names such as `shaper_{source_stem}.html`
* Findings-led output review with before-and-after comparison and no score out
  of 100
* Separate human publication approval before an artifact can be exported
* PostgreSQL-backed Azure workflow state and local SQLite development state
* A live authenticated estate workspace at `/concept/`
* An authenticated MCP interface for the governed Knowledge Estate workflow,
  including findings, proposals, transformations, artifact approval, exact HTML
  retrieval, and grounded evaluation questions

SharePoint sources remain truthful registrations until Microsoft Graph consent
and synchronization are configured. Confluence, ServiceNow, arbitrary wiki
crawling, distributed workers, and quantitative readiness calibration remain
follow-up work.

## Azure architecture

The current development deployment packages Shaper as a non-root application
container with a ClamAV sidecar in one Azure Container Apps replica. One ASGI
process exposes:

* Authenticated HTTP endpoints on `/v1`
* MCP Streamable HTTP on `/mcp/`
* Liveness and dependency-aware readiness probes on `/health`
* The authenticated Knowledge Estates workspace on `/concept/`

Azure Database for PostgreSQL persists estates, workflows, decisions, token
usage, reviews, and Knowledge Estate artifact metadata and bytes. Azure Container
Registry, a user-assigned managed identity, Log Analytics, and a provisioned
Azure Files share support the deployment. The container image directs uploads
and legacy compilation releases to the mounted share. PostgreSQL remains
authoritative for Knowledge Estate records and generated artifact bytes. The
ClamAV sidecar scans uploads before inventory creation.
Container Apps authentication provides interactive Entra sign-in, while
persisted collection grants remain the application authorization boundary.

Product surfaces are prioritized as the Azure-native platform, REST API, Copilot
Agent, SharePoint integration, Teams integration, then Foundry integration.
SharePoint is a source and delivery surface, not the product boundary.

See [deployment guidance](docs/deployment.md) for the current and target Azure
topologies and [operations guidance](docs/operations.md) for monitoring,
recovery, and retention. See [platform architecture](docs/architecture.md) for
the C4 model and specialist-agent responsibility boundaries. See the
[feature guide](docs/features.md) for the current Knowledge Estate workflow,
content-focused Findings, approval boundaries, and lifecycle controls. Use the
[MCP guide](docs/mcp.md) to configure a client, stage uploads, run the governed
workflow, retrieve approved HTML, and test authorization. Use the
[document readiness checklist](docs/document-readiness-checklist.md) to review
source structure, ambiguity, consistency, provenance, retrieval suitability,
and parsing hygiene before ingestion. The
[business requirements document](docs/planning/brds/shaper-business-requirements.md)
defines the business goals, governance rules, requirements, acceptance criteria,
risks, and stakeholder approval gates.

## Architecture diagrams

The [platform architecture](docs/architecture.md) includes:

* A [system context diagram](docs/architecture.md#system-context) showing users,
  clients, content repositories, consuming agents, and Azure AI dependencies
* A [container diagram](docs/architecture.md#containers) separating current and
  planned runtime responsibilities
* A [current Azure deployment diagram](docs/architecture.md#current-azure-development-deployment)
  grounded in the Bicep and container configuration
* A [component diagram](docs/architecture.md#shaper-api-and-orchestrator-components)
  for orchestration, findings, transformation, review, and token estimation
* An [assessment evidence flow](docs/architecture.md#assessment-evidence-architecture)
  from immutable source evidence to plain-language Findings
* A [governed transformation flow](docs/architecture.md#governed-transformation-and-token-budget)
  covering estimates, exact approval, bounded shaping, preview, and publication
* An estate-wide evaluation-draft flow that balances up to 20 source-grounded
  questions across approved document plans

See the [wiki](wiki/Home.md) for a task-oriented guide covering what Shaper
does, how to get started and call the API, how to deploy it, and frequently
asked questions.

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
| `SHAPER_TRANSFORMATION_TOKEN_LIMIT` | Maximum estimated tokens across one initial-plus-repair transformation workflow; defaults to `200000` |
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
