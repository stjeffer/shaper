---
title: Deploy Shaper to Azure
description: Build, deploy, smoke-test, and roll back Shaper on Azure Container Apps
ms.topic: how-to
---

## Deployed architecture

The deployment uses these Azure resources:

* Azure Container Apps for the authenticated HTTP and MCP service
* A ClamAV sidecar reachable only inside the Container App replica
* Azure Files for SQLite state, uploads, and immutable release artifacts
* Azure Container Registry with admin access disabled
* A user-assigned managed identity with `AcrPull`
* Log Analytics for container and platform logs
* The static Copilot Studio pitch prototype served by the same Container App

The application and scanner share one replica. The application listens on port
8000, exposes HTTPS through Container Apps ingress, and mounts persistent state
at `/mnt/state`.

> [!IMPORTANT]
> The bounded SQLite profile has `minReplicas` and `maxReplicas` fixed at one,
> uses rollback journaling instead of WAL, and accepts deployment downtime so
> the script can deactivate the current revision before starting its
> replacement. Do not bypass that script or increase either replica value until
> a managed transactional database adapter replaces SQLite.

## Prerequisites

Install Azure CLI with Bicep support, authenticate to the target subscription,
and prepare:

* An Entra application identifier URI for the API audience
* An OIDC issuer for the tenant
* Collection-scoped app roles such as `shaper:{collection}:query`
* Existing Azure OpenAI chat and embedding deployments
* An approved ClamAV image reference pinned by digest for production
* A short-lived bearer token for deployment smoke testing

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
export SHAPER_OIDC_AUDIENCE="api://YOUR_APPLICATION_ID"
export SHAPER_OIDC_ISSUER="https://login.microsoftonline.com/YOUR_TENANT_ID/v2.0"
export SHAPER_SCANNER_IMAGE="clamav/clamav-debian@sha256:APPROVED_DIGEST"
export SHAPER_SMOKE_TOKEN="SHORT_LIVED_TOKEN"

./scripts/deploy.sh \
  --resource-group rg-shaper-dev \
  --location eastus2 \
  --environment dev \
  --prefix shaper
```

The script performs two deployments. The first provisions the registry and
supporting resources. Azure Container Registry then builds the image from the
checked-out source. The second deploys the Container App, records the image
digest and revision, waits for liveness and readiness, and initializes a real
MCP session.

The deployment output includes a `Pitch prototype` URL at `/concept/`. This
static concept is intentionally unauthenticated so it can be used in a product
pitch; it contains no production data or credentials. Do not add customer or
tenant data to the prototype assets.

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
syntax. SharePoint, Entra, Azure OpenAI, and production corpus validation remain
credentialed integration activities.
