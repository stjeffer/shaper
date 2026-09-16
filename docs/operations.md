---
title: Operate Shaper
description: Monitor, recover, retain, and upgrade a hosted Shaper deployment
ms.topic: how-to
---

## Health and monitoring

`/health/live` proves that the ASGI process can answer requests.
`/health/ready` also probes the workflow state store, Knowledge Estate store,
malware scanner, and compile worker. In the hosted production composition, the
estate store is PostgreSQL. Container Apps removes the revision from traffic
when readiness fails and restarts it when liveness fails.

Query Log Analytics for startup errors, job transitions, scanner failures,
quota rejections, model usage, review decisions, and release publication.
Operational telemetry may correlate request, job, source, agent-run, candidate,
and release identifiers. Source bodies, credentials, and tokens are rejected or
redacted before rendering.

For document assessment, monitor discovery completion, failed document counts,
finding counts by stable code, high-priority finding counts, and evidence
coverage. Do not treat the internal readiness or effort heuristics as accuracy,
confidence, or service-level metrics. A changing finding count can mean that
content changed, checks changed, or extraction quality changed; investigate the
finding code and evidence rather than interpreting the count alone.

New discovery reports should include `agent_impact` for every structured
finding. A missing value on a historical report is compatible and uses a
presentation fallback. A missing value on a newly generated report indicates
contract drift and should be investigated before relying on the assessment.

### Azure OpenAI rate limits

One document transformation can require an initial shaping request and one
bounded repair request. Configure the chat deployment with at least 50,000 TPM;
100,000 TPM is recommended for concurrent or repair-heavy use.

When a run reports `Azure OpenAI rate limit was reached`, correlate its document
identifier with application logs and check for HTTP 429 responses. Confirm the
deployment's token rate limit:

```bash
az cognitiveservices account deployment show \
  --resource-group YOUR_OPENAI_RESOURCE_GROUP \
  --name YOUR_OPENAI_ACCOUNT \
  --deployment-name YOUR_CHAT_DEPLOYMENT \
  --query "properties.rateLimits[?key == 'token'] | [0].count" \
  --output tsv
```

Retry the failed transformation after the provider window resets. If a single
transformation repeatedly reaches the limit, increase deployment capacity
within the approved regional quota rather than disabling repair or
source-preservation validation.

## State and recovery

PostgreSQL is the authoritative store for Knowledge Estate registrations,
versions, reports, grants, proposals, decisions, transformations, reviews,
compile jobs, and review records.

The hosted process also creates a process-local in-memory SQLite store for
legacy compilation checkpoints and candidates. It is not a durable recovery
source.

The deployment provisions and mounts an Azure Files share at `/mnt/state`, but
the current Container App does not direct `SHAPER_UPLOAD_ROOT` or
`SHAPER_RELEASE_ROOT` to that mount. Quarantined uploads, the active release
pointer, and compiled release artifacts are therefore replica-local. A restart
or revision change can require the source to be uploaded again and the release
to be rebuilt.

Before recovery, snapshot PostgreSQL and validate the estate schema and report
records. Restart the Container App revision, re-upload any required source
assets, and rebuild or republish the active release. Verify its manifest and
unit hashes before restoring traffic. A missing or invalid current release
fails projection loading rather than silently serving unverified evidence.

## Retention

Upload assets default to 24-hour retention. Release cleanup retains the current
release, at least 11 successful releases, and releases younger than 90 days.
Change these values only through an approved records and privacy decision.

Do not delete `current.json` or mutate an immutable release in place. Publish a
new complete release and advance the pointer through the publication service.

## Security operations

Inbound HTTP and MCP requests require signed OIDC tokens with the configured
issuer and audience. Roles are collection-scoped. The shaping agent has no
filesystem, arbitrary HTTP, shell, permission, review, or publication tool.

Use a ClamAV image pinned by approved digest and monitor signature-update
failures. Readiness intentionally fails when the scanner is unavailable, so
unscanned direct uploads cannot enter the workflow.

Rotate credentials outside the image and Bicep parameter files. The current
deployment has no application secrets; Azure Files keys are held in the
Container Apps environment storage configuration, and registry pulls use
managed identity.

## Upgrade procedure

1. Run formatting, linting, strict typing, tests, coverage, and schema drift.
2. Run the synthetic 30-case evaluation and compare all strategies.
3. Run configured live SharePoint, Azure OpenAI, OIDC, and evaluation suites.
4. Obtain evaluation-owner and domain-reviewer approval for baseline changes.
5. Deploy a new Container Apps revision with the deployment script.
6. Verify health, MCP initialization, authorization, current release, and logs.
7. Run one Knowledge Estate discovery and verify that findings expose agent
   impact and evidence without a readiness score.
8. Approve one current improvement plan and verify that transformation progress
   reports complete-content, preservation, grounding, and optional quality-check
   results before opening the generated output.
9. Verify the Evaluation set contains up to 20 distinct, source-grounded
   questions balanced across documents, and fewer questions for sparse knowledge.
10. Approve one generated artifact and verify **Export approved HTML** downloads
    the exact reviewed artifact with its governed filename.
11. Retain the prior revision until the observation window completes.

The regression gate permits no deterministic pass-rate decrease, at most a
5-percentage-point model-assisted pass-rate decrease, and at most a 20-percent
increase in p95 latency or mean model-token use. Automatic publication remains
disabled until separately approved.
