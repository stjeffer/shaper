---
title: Use Shaper through MCP
description: Configure, authorize, test, and operate the Shaper MCP interface
ms.date: 2026-09-17
ms.topic: how-to
---

## Overview

Shaper exposes an authenticated Model Context Protocol server over Streamable
HTTP:

```text
https://<shaper-host>/mcp/
```

The MCP interface uses the same application services, tenant boundary,
collection roles, source-version checks, optimistic concurrency, validation,
review, and publication controls as the REST API and browser workspace.

MCP clients can:

* Query approved knowledge and inspect its derivation
* Create and inspect Knowledge Estates
* Register URL and SharePoint source references
* Inspect document inventory and retained source state
* Run deterministic discovery and retrieve findings with agent impact
* Generate and review exact transformation proposals
* Record review-authorized proposal decisions
* Run one-document transformations with optional bounded repair
* Inspect artifact findings and current review revisions
* Approve an artifact with exact finding acknowledgment
* Retrieve exact, hash-verified approved HTML
* Generate up to 20 distinct source-grounded evaluation questions

Raw file and ZIP bytes use the existing authenticated REST upload endpoint.
After upload, the document and every later workflow stage are available through
MCP. This boundary avoids base64 expansion and preserves existing upload-size,
malware-scanning, archive-expansion, and source-retention controls.

## Prerequisites

You need:

* The Shaper HTTPS base URL
* An Entra access token issued by the configured tenant
* The Shaper API application UUID in the token's `aud` claim
* At least one collection-scoped application role
* An MCP client that supports Streamable HTTP and custom authorization headers

Collection roles use this format:

```text
shaper:<collection-id>:query
shaper:<collection-id>:compile
shaper:<collection-id>:review
shaper:<collection-id>:admin
```

The common workflow requires `query`, `compile`, and `review`. Estate archival
and purge remain REST or browser operations and require `admin`.

## Obtain an access token

Use an approved OAuth client configured for the Shaper API. The requested scope
uses the API identifier URI, while Shaper validates the application UUID in the
resulting token's audience claim.

For an interactive Azure CLI identity with an assigned Shaper application role:

```bash
export SHAPER_API_APP_ID="00000000-0000-0000-0000-000000000000"
export SHAPER_TOKEN="$(
  az account get-access-token \
    --scope "api://${SHAPER_API_APP_ID}/.default" \
    --query accessToken \
    --output tsv
)"
```

Use your organization's approved confidential-client flow for unattended
clients. Do not store tokens or client secrets in the repository, MCP
configuration, shell history, or logs.

## Configure an MCP client

Use these transport values:

| Setting | Value |
|---|---|
| Transport | Streamable HTTP |
| URL | `https://<shaper-host>/mcp/` |
| Authentication | OAuth bearer access token |
| Recommended request timeout | At least 210 seconds |

A representative MCP configuration is:

```json
{
  "servers": {
    "shaper": {
      "type": "http",
      "url": "https://<shaper-host>/mcp/",
      "headers": {
        "Authorization": "${input:shaper-authorization}"
      }
    }
  },
  "inputs": [
    {
      "id": "shaper-authorization",
      "type": "promptString",
      "description": "Enter Bearer followed by a short-lived Shaper access token",
      "password": true
    }
  ]
}
```

Configuration keys vary between clients. Preserve the endpoint, Streamable HTTP
transport, and authorization header when adapting the example.

## Verify MCP initialization

Set local variables without writing the token to disk:

```bash
export SHAPER_URL="https://<shaper-host>"
export SHAPER_AUTH_SCHEME="Bearer"
```

Initialize the protocol:

```bash
curl --fail --silent --show-error \
  --header "Authorization: ${SHAPER_AUTH_SCHEME} ${SHAPER_TOKEN}" \
  --header "Accept: application/json, text/event-stream" \
  --header "Content-Type: application/json" \
  --data '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-06-18",
      "capabilities": {},
      "clientInfo": {
        "name": "shaper-smoke",
        "version": "1.0"
      }
    }
  }' \
  "${SHAPER_URL}/mcp/"
```

A successful response contains a JSON-RPC `result`. Prefer a full MCP client for
subsequent calls because it manages protocol initialization and response
content types.

## Available tools

### Existing approved-knowledge tools

| Tool | Required role | Behavior |
|---|---|---|
| `knowledge.query` | `query` | Search the active approved evidence release |
| `knowledge.explain` | `query` | Explain one answer unit from source and derivation evidence |
| `knowledge.compile` | `compile` | Submit an idempotent legacy compile-by-reference job |
| `knowledge.job_status` | `compile` | Read compile-job status |

The numeric value returned by `knowledge.query` is retrieval relevance, not a
readiness score.

### Knowledge Estate read tools

| Tool | Required role | Behavior |
|---|---|---|
| `estate.assessment_checks` | Authenticated | List the 31 deterministic checks |
| `estate.list` | `query` | List estates and current assessment coverage |
| `estate.get` | `query` | Get one estate and its revision |
| `estate.source.list` | `query` | List registered sources |
| `estate.document.list` | `query` | List current documents and source-retention state |
| `estate.run.list` | `query` | List discovery, recommendation, and transformation runs |
| `estate.discovery.reports` | `query` | Get findings, evidence, remedies, and agent impact |
| `estate.proposal.list` | `query` | Get exact transformation proposals |
| `estate.decision.list` | `query` | Get current proposal decisions |
| `estate.artifact.list` | `query` | Get artifacts, revisions, status, and findings |
| `estate.artifact.review` | `review` | Get the review revision and required acknowledgment set |
| `estate.evaluation.list` | `query` | Generate a grounded evaluation set |

Discovery reports omit the legacy aggregate readiness score. They retain
individual findings, severity, evidence, remedies, and agent-impact language.
Evaluation-set responses contain no quality score.

### Knowledge Estate mutation tools

| Tool | Required role | Behavior |
|---|---|---|
| `estate.create` | `compile` | Create a distinct estate |
| `estate.update` | `compile` | Update an exact estate revision |
| `estate.source.register` | `compile` | Register a URL or SharePoint reference |
| `estate.discovery.start` | `compile` | Run deterministic discovery |
| `estate.recommendation.start` | `compile` | Generate proposals from selected discovery evidence |
| `estate.proposal.decide` | `review` | Approve or decline an exact proposal with a rationale |
| `estate.transformation.start` | `compile` | Transform one approved proposal |
| `estate.artifact.approve` | `review` | Approve an exact artifact and review revision |

Estate creation, source registration, discovery, recommendation, and
transformation starts are non-idempotent. A retry creates a separate,
auditable record or run. If a client times out, call `estate.run.list` before
retrying. `knowledge.compile` remains idempotent through its required
`idempotency_key`.

## Available resources

| Resource URI | Required role | Content |
|---|---|---|
| `knowledge://units/{unit_id}` | `query` | Approved evidence unit and derivation |
| `knowledge://sources/{source_id}` | `query` | Bounded source identity |
| `knowledge://releases/{release_id}` | `query` | Active release identity |
| `estate://documents/{estate_id}/{document_id}/{source_version}` | `query` | Normalized text for the exact current source version |
| `estate://artifacts/{artifact_id}/preview` | `review` | Hash-verified generated HTML before approval |
| `estate://artifacts/{artifact_id}/content` | `query` | Exact hash-verified approved HTML bytes |

The approved artifact resource rejects unapproved artifacts. Save the binary
resource bytes without decoding and re-encoding them when exact output identity
matters.

## Complete workflow example

### 1. Create an estate through MCP

Call `estate.create`:

```json
{
  "collection_id": "policy-knowledge",
  "name": "People policies",
  "description": "Current employee policy sources",
  "artifact_name_template": "shaper_{source_stem}.html",
  "generate_evaluations": true
}
```

Retain the returned `estate_id` and `revision`.

### 2. Stage file bytes through REST

```bash
export ESTATE_ID="<estate-id>"

curl --fail --silent --show-error \
  --header "Authorization: ${SHAPER_AUTH_SCHEME} ${SHAPER_TOKEN}" \
  --form "files=@./leave-policy.docx" \
  "${SHAPER_URL}/v1/estates/${ESTATE_ID}/uploads"
```

The response contains registered sources and current document identifiers. ZIP
files use the same endpoint and retain existing archive limits.

### 3. Run discovery

Call `estate.discovery.start`:

```json
{
  "estate_id": "<estate-id>"
}
```

Review each returned finding's:

* `code`
* `severity`
* `label`
* `explanation`
* `evidence`
* `agent_impact`

Use `estate.discovery.reports` to retrieve the stored reports later.

### 4. Generate proposals

Call `estate.recommendation.start` with the completed discovery run:

```json
{
  "estate_id": "<estate-id>",
  "discovery_run_id": "<discovery-run-id>",
  "document_ids": [
    "<document-id>"
  ]
}
```

Review the returned source version, proposed changes, rationale, expected
artifact name, and token estimate.

### 5. Record the human proposal decision

Call `estate.proposal.decide`:

```json
{
  "recommendation_id": "<recommendation-id>",
  "outcome": "approve",
  "reason": "The proposed changes are supported by the cited findings.",
  "expected_current_decision_id": null
}
```

If another decision already exists, first read it through
`estate.decision.list` and submit its identifier as
`expected_current_decision_id`.

### 6. Transform one approved proposal

Call `estate.transformation.start`:

```json
{
  "estate_id": "<estate-id>",
  "recommendation_id": "<recommendation-id>",
  "enforce_preservation_checks": false
}
```

Set `enforce_preservation_checks` to `true` to request at most one automatic
repair from preservation findings. Remaining reviewable findings are retained
with the artifact. Source identity, source version, evidence, candidate schema,
exclusion authority, and retained excluded content remain non-bypassable.

This tool accepts one recommendation per call. Configure the client timeout to
at least 210 seconds. If the transport times out, inspect `estate.run.list`
before retrying because a run may have completed.

### 7. Inspect and approve the artifact

Call `estate.artifact.review`:

```json
{
  "artifact_id": "<artifact-id>"
}
```

Review the preview resource:

```text
estate://artifacts/<artifact-id>/preview
```

Then call `estate.artifact.approve` with the exact values returned by the review
tool:

```json
{
  "artifact_id": "<artifact-id>",
  "reason": "The reshaped content and all current findings were reviewed.",
  "expected_review_revision": 1,
  "expected_artifact_revision": 1,
  "acknowledged_finding_ids": [
    "content.example_finding"
  ]
}
```

The acknowledgment list must exactly match
`required_acknowledged_finding_ids`. Use an empty list when the review tool
returns no findings. Stale revisions or mismatched acknowledgments fail without
publication.

### 8. Retrieve approved HTML

Read:

```text
estate://artifacts/<artifact-id>/content
```

The resource returns the same hash-verified bytes as:

```text
GET /v1/artifacts/<artifact-id>/download
```

### 9. Generate evaluation questions

Call `estate.evaluation.list`:

```json
{
  "estate_id": "<estate-id>",
  "recommendation_run_id": "<recommendation-run-id>"
}
```

The response contains up to 20 distinct questions balanced across selected
documents. Each item includes source identity, expected answer, context,
keywords, suggested Foundry evaluators, and Copilot Studio test methods. Sparse
estates return fewer questions rather than duplicate filler.

## Test locally

Run the focused Python MCP and Knowledge Estate tests:

```bash
PYTHONPATH=src uv run pytest \
  tests/test_interfaces.py \
  tests/test_estate_interfaces.py \
  tests/test_artifacts.py \
  tests/test_shaping.py \
  -q
```

Run lint and strict typing:

```bash
PYTHONPATH=src uv run ruff check .
PYTHONPATH=src uv run mypy
```

Run the complete Python suite and coverage gate:

```bash
PYTHONPATH=src uv run pytest --cov=shaper --cov-report=term-missing
```

## Test a deployment

Set `SHAPER_SMOKE_TOKEN` before running the deployment script. The script checks
liveness, readiness, and MCP initialization without printing the token:

```bash
export SHAPER_SMOKE_TOKEN="${SHAPER_TOKEN}"

./scripts/deploy.sh \
  --resource-group <resource-group> \
  --location <location> \
  --environment <environment> \
  --prefix <prefix>
```

After deployment:

1. Initialize `/mcp/`.
2. List tools and confirm the Knowledge Estate tools are present.
3. Call `estate.list` with an authorized collection.
4. Call it with a token lacking that collection role and confirm denial.
5. Stage one test document through REST.
6. Complete discovery, recommendation, decision, transformation, review,
   approval, and approved-content retrieval through MCP.
7. Compare MCP approved HTML bytes with the REST download.
8. Review logs for authorization, provider, scanner, or persistence errors.

## Troubleshooting

### Authentication fails

Confirm:

* The token issuer exactly matches `SHAPER_OIDC_ISSUER`
* The token `aud` claim is the API application UUID in `SHAPER_OIDC_AUDIENCE`
* The `roles` claim contains the required `shaper:<collection-id>:<role>` value
* The token is current and signed by a key in the issuer metadata

### A workflow appears to time out

Set the MCP client timeout to at least 210 seconds for transformation. Call
`estate.run.list` before retrying. Workflow starts are non-idempotent, so a
blind retry can create a second run and additional model usage.

### A proposal decision fails

Reload proposals and current decisions. Confirm the source version is current
and pass the latest decision identifier as `expected_current_decision_id`.

### Artifact approval fails

Call `estate.artifact.review` again. Use the returned review revision, artifact
revision, and complete `required_acknowledged_finding_ids` list. Do not reuse
values from an earlier review.

### Approved content is unavailable

Confirm the artifact status is `approved` and the caller has `query` for the
estate collection. A hash mismatch is treated as an integrity failure and does
not return content.
