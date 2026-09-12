---
title: Deploy Shaper
description: Summary of deploying Shaper to Azure Container Apps
ms.topic: how-to
---

## Summary

Shaper's current development deployment packages the platform as one
non-root OCI container on Azure Container Apps, backed by Azure Database for
PostgreSQL, Azure Files, Azure Container Registry, and a ClamAV sidecar. The
full deployment topology, prerequisites, deploy script, and rollback
procedure are documented in [docs/deployment.md](../docs/deployment.md).

## Quick reference

1. Install Azure CLI with Bicep support and authenticate to the target
   subscription.
2. Prepare an Entra API application, OIDC issuer, collection-scoped app
   roles, and existing Azure OpenAI chat/embedding deployments.
3. Validate the Bicep template:

   ```bash
   az bicep build --file bicep/main.bicep
   az deployment group validate \
     --resource-group YOUR_RESOURCE_GROUP \
     --template-file bicep/main.bicep \
     --parameters bicep/dev.bicepparam
   ```

4. Export required runtime values (collection ID, Azure OpenAI settings,
   OIDC audience/issuer, scanner image digest) and run:

   ```bash
   ./scripts/deploy.sh \
     --resource-group rg-shaper-dev \
     --location eastus2 \
     --environment dev \
     --prefix shaper
   ```

   The script provisions PostgreSQL and supporting resources, builds and
   pushes the container image, deploys the Container App with interactive
   Entra authentication, and waits for liveness and readiness.

5. To roll back, deactivate the current Container Apps revision and
   reactivate the last healthy revision, then shift ingress traffic weight.
   Rollback changes compute only; the prior revision reuses the persisted
   Azure Files state.

See [docs/deployment.md](../docs/deployment.md) for the full current and
target Azure topologies, and [docs/operations.md](../docs/operations.md) for
monitoring, recovery, retention, security operations, and the upgrade
procedure.

## Deployment boundaries

Live deployment requires a configured Azure subscription and cannot be proven
by local tests alone. Local validation covers Python behavior, the evaluation
gate, container configuration, Bicep syntax, and shell syntax. SharePoint,
Entra, Azure OpenAI, managed state, asynchronous workers, and production
corpus validation remain credentialed integration activities.
