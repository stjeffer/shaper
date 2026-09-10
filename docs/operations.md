---
title: Operate Shaper
description: Monitor, recover, retain, and upgrade a hosted Shaper deployment
ms.topic: how-to
---

## Health and monitoring

`/health/live` proves that the ASGI process can answer requests.
`/health/ready` also probes SQLite and ClamAV. Container Apps removes the
revision from traffic when readiness fails and restarts it when liveness fails.

Query Log Analytics for startup errors, job transitions, scanner failures,
quota rejections, model usage, review decisions, and release publication.
Operational telemetry may correlate request, job, source, agent-run, candidate,
and release identifiers. Source bodies, credentials, and tokens are rejected or
redacted before rendering.

## State and recovery

The Azure Files mount contains:

* `shaper.db` for jobs, checkpoints, records, and outbox state
* `uploads/` for quarantined, scanned upload assets
* `publication/current.json` for the active immutable release pointer
* `publication/releases/` for immutable release artifacts and manifests

Before recovery, copy the share or take a storage snapshot. Validate SQLite,
verify the active manifest and unit hashes, then restart the Container App
revision. A missing or invalid current release fails projection loading rather
than silently serving unverified evidence.

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
7. Retain the prior revision until the observation window completes.

The regression gate permits no deterministic pass-rate decrease, at most a
5-percentage-point model-assisted pass-rate decrease, and at most a 20-percent
increase in p95 latency or mean model-token use. Automatic publication remains
disabled until separately approved.
