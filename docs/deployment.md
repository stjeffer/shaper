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
* A provisioned Azure Files share mounted at `/mnt/state`
* Azure Container Registry with admin access disabled
* A user-assigned managed identity with `AcrPull`
* Log Analytics for container and platform logs
* The live authenticated Knowledge Estates workspace served by the same
  Container App

The application and scanner share one replica. The application listens on port
8000, exposes HTTPS through Container Apps ingress, and mounts the Azure Files
share at `/mnt/state`.

See the
[current Azure development deployment diagram](architecture.md#current-azure-development-deployment)
for the runtime nodes, container instances, managed services, and request paths.

PostgreSQL stores estate state, compile jobs, collection grants, decisions,
token usage, and output review. A process-local SQLite store supports only
legacy compilation checkpoints and candidates; it is not authoritative estate
state and cannot create a cross-revision file lock.

The container image sets `SHAPER_UPLOAD_ROOT` to `/mnt/state/uploads` and
`SHAPER_RELEASE_ROOT` to `/mnt/state/publication`. Uploads and legacy compiled
release files therefore use the mounted Azure Files share and survive revision
changes. Knowledge Estate records, including generated artifact bytes, remain
authoritative in PostgreSQL.

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

The platform assessment endpoint accepts canonical document profiles and returns
immutable dimensions, evidence coverage, findings, topic clusters, and ranked
interventions. Knowledge Estate discovery produces per-document reports with
completed checks, evidence coverage, and structured findings.
Each new finding includes a plain-language explanation of its likely effect on
retrieval or agent answers plus bounded source evidence. The workspace presents
those findings instead of a score out of 100.

Transformation results are proposals only. The current development topology
does not crawl an enterprise estate, run recurring governance schedules, or
execute estate-wide source changes.

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

## Deploy Knowledge Estate workflow updates

Knowledge Estate assessment, approval, progress streaming, and transformation
logic ship in the application image. Deploy them through the standard revision
workflow above. No separate front-end deployment is required because the
Container App serves the workspace assets.

The workspace stylesheet and local theme bootstrap use the versioned `fluent2-v10`
asset query. The bootstrap loads the application module with the same version.
These versions prevent a new revision from reusing an older control palette or
application bundle from a browser or edge cache. The Microsoft Teams accent is
fixed in the shipped assets. The workspace deliberately uses the Teams light
theme, including a subtle purple-tinted canvas and white raised surfaces, so no
theme selector or server-side theme configuration is required.

The local `fluent-theme.js` bootstrap loads the pinned
`@fluentui/web-components` 2.6.1 module from the workspace `vendor` directory.
The image also includes the Fluent UI, Fluent System Icons, and bundled
`tabbable` MIT license notices. The bootstrap sets light-theme provider
luminance through the public Fluent Design Token API before loading `app.js`.
Buttons, fields, selects, checkboxes, tabs, menus, dialogs, progress indicators,
accordions, links, and data grids use the official Fluent custom elements
without reaching into component shadow parts. Interface symbols use locally
packaged Microsoft Fluent System Icons rather than text glyphs or emoji.
The hidden native file input is the sole exception because the browser file
chooser requires it; a Fluent button invokes that input. The workspace therefore
does not depend on a public CDN or a corresponding content-security exception at
runtime.

The image packages separate shaping and model-assisted evaluation system prompts
as Markdown resources under `shaper/prompts`. Callers select the required prompt
explicitly, and startup fails rather than silently substituting instructions when
a resource is missing or blank. After deployment, transformation and evaluation
therefore use the prompt versions built into that exact image revision.

The `agent_impact` field is an additive, optional field in persisted
`DocumentFinding` JSON. Existing reports remain readable and require no
relational database migration. New discovery runs populate the field. Historical
reports use the browser's code-keyed impact fallback until they are regenerated.

The transformation estimator is version `1.3`. It reserves an initial candidate
and up to three bounded repair attempts. Proposals created by estimator version
`1.2` remain stored, but the new revision rejects them before model use because
their approved token maximum covered only two calls. Run **Create improvement
plan** again and obtain a new approval before transforming those documents. No
database migration is required.

The authenticated
`POST /v1/estates/{estate_id}/transformation-runs/stream` endpoint returns
newline-delimited JSON events for actual document and validation stages. The
browser uses this stream to report complete-content, source-preservation,
grounding, and optional deterministic quality-check results. Processing remains
inside the application process. A client disconnect requests cancellation before
the next model action or document; an in-flight provider request may finish
first. This endpoint is not a durable background queue.

After the revision becomes ready:

1. Open the authenticated workspace at `/concept/`.
2. Confirm the workspace uses the Microsoft Teams purple accent, exposes no
   theme selector, and renders official Fluent primary and lightweight actions
   without an additional host-level border.
3. Confirm the shell uses the fixed Teams light palette: a subtle purple-tinted
   canvas, white raised surfaces, and Teams purple only for selection and primary
   actions.
4. Confirm the estate list reflows without horizontal scrolling at a 320-pixel
   viewport and remains usable at 200% browser zoom.
5. Confirm keyboard focus remains visible on actions and tabs, then verify
   controls remain distinguishable in Windows forced-colours mode.
6. Confirm buttons, fields, selects, checkboxes, tabs, menus, dialogs, progress
   indicators, accordions, links, and the assessment data grid expose their
   expected Fluent roles and accessible names.
7. Run discovery for an estate with at least one known content issue.
8. Confirm the Assess data grid contains **Document** and **Findings**, with no
   readiness-score or reshaping-effort column.
9. Expand a finding and confirm it shows the detected condition, **Agent
   impact**, review status, and source evidence.
10. Select a document and request recommendations.
11. Confirm the proposal rationale describes the number and likely impact of
   content findings without a score out of 100.
12. Approve the new proposal and confirm the transformation controls appear above
   the **Assessment results** and **Evaluation set** tabs.
13. Start transformation and confirm the live progress surface names each check,
   updates results as stages complete, and opens the generated output when the run
   completes.
14. If the estate contains a proposal created with estimator version `1.2`,
   confirm transformation stops before model use and instructs the reviewer to
   create and approve a current improvement plan.

Forward compatibility is automatic: the newer revision reads reports that do
not contain `agent_impact`. The reverse direction is not automatic because
domain contracts reject unknown fields. Before rolling back to a revision that
predates `agent_impact`, stop new discovery work and either retain the newer
revision for report reads or restore the estate store to a compatible
pre-deployment snapshot. Reports created by an older revision remain valid in
the newer application.

Rollback does not require a schema restore for this update. A revision using
estimator version `1.2` rejects proposals created with version `1.3`; recreate
and approve the improvement plan after rollback rather than attempting to reuse
the newer token estimate.

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

Rollback changes compute while retaining PostgreSQL estate and workflow state.
Replica-local uploads and compiled releases are not guaranteed to be available
to the prior revision. The service is unavailable between deactivation and
successful activation. Verify `/health/ready`, initialize `/mcp/`, and recreate
or republish any required release after activating the prior revision.

## Deployment boundaries

Live deployment requires a configured Azure subscription and cannot be proven
by local tests. Local validation covers Python behavior, the evaluation gate,
container configuration, Bicep syntax when Azure CLI is available, and shell
syntax. SharePoint, Entra, Azure OpenAI, managed state, asynchronous workers, and
production corpus validation remain credentialed integration activities.
