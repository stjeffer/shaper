---
title: Deploy Shaper to Azure
description: Build, deploy, smoke-test, and roll back Shaper on Azure Container Apps
ms.topic: how-to
---

## Current development architecture

The deployment uses these Azure resources:

* Azure Container Apps for the authenticated HTTP and MCP service
* A ClamAV sidecar reachable only inside the Container App replica
* Azure Database for PostgreSQL 16 for durable workflow and review state
* Azure Files for uploads and immutable release artifacts
* Azure Container Registry with admin access disabled
* A user-assigned managed identity with `AcrPull`
* Log Analytics for container and platform logs
* The live authenticated Knowledge Estates workspace served by the same
  Container App

The application and scanner share one replica. The application listens on port
8000, exposes HTTPS through Container Apps ingress, and mounts persistent state
at `/mnt/state`.

PostgreSQL stores estate state, compile jobs, collection grants, decisions,
token usage, and output review. A process-local SQLite store supports only
legacy compilation checkpoints and candidates; it is not authoritative estate
state and cannot create a cross-revision file lock.

The current service exposes compile, review, publish, query, and MCP capabilities
together with authenticated `POST /v1/assessments` and
`POST /v1/platform/analyses`. The platform endpoint synchronously coordinates
Assessment, Knowledge, Transformation, Governance, and Agent Readiness roles over
one immutable assessment. These roles run in the application container today;
they are responsibility boundaries, not separate deployments.

The authenticated estate API exposes source registration, file and ZIP upload,
discovery, per-document reports, recommendations, decisions, transformations,
token usage, artifact review, archive, and purge. Container Apps authentication
redirects browser users to Entra. Bearer-authenticated MCP remains excluded from
interactive ingress handling and is validated by the application.

The assessment accepts canonical document profiles and returns immutable
readiness metrics, evidence coverage, findings, topic clusters, and ranked
interventions. Transformation results are proposals only. The current
development topology does not crawl an enterprise estate, run recurring
governance schedules, or execute estate-wide source changes.

## Production target architecture

The production topology separates the knowledge transformation engine from
source and delivery systems:

* Microsoft Graph connectors use delta queries and durable checkpoints to
  discover SharePoint and OneDrive content incrementally
* Azure Container Apps hosts the API and independently scalable workers
* Azure Service Bus carries bounded, retryable assessment and transformation jobs
* Azure Database for PostgreSQL stores workflow state, approvals, provenance,
  assessment metadata, and source checkpoints
* Azure Blob Storage or governed SharePoint libraries store immutable source
  snapshots and canonical knowledge packages
* Azure OpenAI supports bounded, evidence-grounded shaping tasks
* Azure AI Search optionally projects approved knowledge for retrieval without
  becoming the canonical authority
* Managed identities, private endpoints, Key Vault, and Log Analytics provide
  workload identity, network isolation, secret management, and observability

SharePoint remains an input and delivery surface. The Shaper service owns
assessment, knowledge modeling, recommendations, transformation proposals, and
approval state. Production connectors and managed asynchronous processing are
planned follow-up work, not capabilities of the current development topology.
Separating each specialist agent into a worker is a target operational choice,
not a requirement for preserving its application responsibility boundary.

## Prerequisites

Install Azure CLI with Bicep support, authenticate to the target subscription,
and prepare:

* An Entra API application UUID and its identifier URI for OAuth scope requests
* An OIDC issuer for the tenant
* Collection-scoped app roles such as `shaper:{collection}:query`
* Existing Azure OpenAI chat and embedding deployments
* An approved ClamAV image reference pinned by digest for production
* Permission to create an application credential for Container Apps
  authentication, or `SHAPER_ENTRA_CLIENT_SECRET`
* A short-lived bearer token for optional MCP deployment smoke testing

The Bicep deployment does not create tenant-level Entra applications or grant
SharePoint permissions. Those operations require separate tenant governance.

## Validate the template

```bash
az bicep build --file bicep/main.bicep
az deployment group validate \
  --resource-group YOUR_RESOURCE_GROUP \
  --template-file bicep/main.bicep \
  --parameters bicep/dev.bicepparam
```

The development parameter file intentionally skips the Container App and uses
placeholder identity values. Supply real values through the deployment script.

## Deploy

Export runtime values without writing tokens to a parameter file:

```bash
export SHAPER_COLLECTION_ID="policy-knowledge"
export SHAPER_AZURE_OPENAI_ACCOUNT="YOUR_OPENAI_ACCOUNT"
export SHAPER_AZURE_OPENAI_CHAT_DEPLOYMENT="YOUR_CHAT_DEPLOYMENT"
export SHAPER_AZURE_OPENAI_EMBEDDING_DEPLOYMENT="YOUR_EMBEDDING_DEPLOYMENT"
export SHAPER_AZURE_OPENAI_RESOURCE_GROUP="YOUR_OPENAI_RESOURCE_GROUP"
export SHAPER_OIDC_AUDIENCE="YOUR_APPLICATION_ID"
export SHAPER_OIDC_ISSUER="https://login.microsoftonline.com/YOUR_TENANT_ID/v2.0"
export SHAPER_SCANNER_IMAGE="clamav/clamav-debian@sha256:APPROVED_DIGEST"
# Optional overrides:
export SHAPER_ENTRA_CLIENT_SECRET="ROTATABLE_APPLICATION_SECRET"
export SHAPER_POSTGRES_ADMIN_PASSWORD="STRONG_DATABASE_PASSWORD"
export SHAPER_SMOKE_TOKEN="SHORT_LIVED_TOKEN"

./scripts/deploy.sh \
  --resource-group rg-shaper-dev \
  --location eastus2 \
  --environment dev \
  --prefix shaper
```

The script provisions PostgreSQL and supporting resources, builds the image in
Azure Container Registry, deploys the Container App and interactive
authentication, registers its callback URL, and waits for liveness and
readiness. It initializes a real MCP session when `SHAPER_SMOKE_TOKEN` is set.
When application or database secrets are omitted, the script creates bounded
deployment credentials without writing them to the repository.

For Entra v2 client-credential tokens, set `SHAPER_OIDC_AUDIENCE` to the API
application UUID emitted in the token's `aud` claim. The `api://` identifier URI
is used in the OAuth scope request, but it is not the expected JWT audience.

The deployment output includes the live workspace URL at `/concept/`. Its
data-free signed-out shell is public and explicitly initiates interactive Entra
sign-in; all session and estate APIs remain protected. The bootstrap principal
receives an administrator grant for the configured collection; subsequent
access is resolved exclusively from persistent collection grants.

## Roll back

List revisions and identify the last healthy revision:

```bash
az containerapp revision list \
  --name ca-shaper-dev \
  --resource-group rg-shaper-dev \
  --query "[].{name:name,active:properties.active,traffic:properties.trafficWeight}" \
  --output table
```

Deactivate the current revision before activating the selected prior revision:

```bash
az containerapp revision deactivate \
  --name ca-shaper-dev \
  --resource-group rg-shaper-dev \
  --revision CURRENT_REVISION

az containerapp revision activate \
  --name ca-shaper-dev \
  --resource-group rg-shaper-dev \
  --revision PREVIOUS_REVISION

az containerapp ingress traffic set \
  --name ca-shaper-dev \
  --resource-group rg-shaper-dev \
  --revision-weight PREVIOUS_REVISION=100
```

Rollback changes compute only. The prior revision reuses the persistent Azure
Files state. The service is unavailable between deactivation and successful
activation. Verify `/health/ready`, initialize `/mcp/`, and inspect the active
release pointer after activating the prior revision.

## Deployment boundaries

Live deployment requires a configured Azure subscription and cannot be proven
by local tests. Local validation covers Python behavior, the evaluation gate,
container configuration, Bicep syntax when Azure CLI is available, and shell
syntax. SharePoint, Entra, Azure OpenAI, managed state, asynchronous workers, and
production corpus validation remain credentialed integration activities.
