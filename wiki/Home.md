---
title: Shaper Wiki
description: Home page for the Shaper project wiki
ms.topic: overview
---

## Welcome

Shaper is an Azure-native **Knowledge Transformation Platform**. It assesses
fragmented enterprise content estates, models the knowledge they contain,
recommends remediation, and prepares trusted, agent-ready knowledge assets for
human-approved publication.

> [!IMPORTANT]
> Shaper is not an agent. It is a platform that coordinates Assessment,
> Knowledge, Transformation, Governance, and Agent Readiness agents while
> retaining deterministic control of authorization, evidence lineage,
> workflow, approval, and publication.

This wiki is the entry point for understanding, using, and operating Shaper.
It summarizes the project and links to the detailed reference documentation
kept under [`docs/`](../docs) in the repository.

## What Shaper does

* **Discover** — connect SharePoint sites, OneDrive locations, file shares,
  and knowledge repositories, and produce an Agent Readiness Assessment
  without modifying source content.
* **Understand** — build a knowledge model that groups related sources into
  business topics and surfaces duplication, contradiction, staleness,
  authority, ownership, and coverage risks.
* **Recommend** — prioritize interventions such as consolidation, authority
  review, archival, metadata enrichment, summaries, FAQs, and canonical
  guidance before any transformation runs.
* **Transform** — prepare approved work through safe-mode derivatives, guided
  rewrite proposals, or knowledge consolidation, all stopping at a human
  approval boundary.
* **Govern** — continuously detect new duplication, emerging contradictions,
  missing ownership, and unhealthy canonical sources.

See the [main README](../README.md) for the full product description and
[feature guide](../docs/features.md) for the current Knowledge Estate
workflow, Results, approvals, and lifecycle controls.

## Wiki contents

| Page | Purpose |
|---|---|
| [Getting Started](Getting-Started.md) | Run Shaper locally, create your first Knowledge Estate, and call the API |
| [API Reference](API-Reference.md) | Summary of the authenticated HTTP and MCP surface |
| [Deployment](Deployment.md) | How to deploy Shaper to Azure |
| [FAQ](FAQ.md) | Common questions about scope, safety, and limitations |

## Deep-dive reference documentation

The `docs/` folder holds the authoritative technical reference:

* [Feature guide](../docs/features.md) — Knowledge Estate workflow, Results,
  recommendations, transformation, and lifecycle controls
* [Platform architecture](../docs/architecture.md) — C4 model and
  specialist-agent responsibility boundaries
* [Deployment guidance](../docs/deployment.md) — current and target Azure
  topologies, prerequisites, deploy, and rollback steps
* [Operations guidance](../docs/operations.md) — monitoring, recovery,
  retention, security operations, and upgrade procedure
* [Improvement reporting](../docs/improvement-reporting.md) — paired
  evaluation measurement contract and claim safeguards

## Current status

Shaper is an MVP. Named Knowledge Estates, document assessment, evidence-based
Results, human-approved recommendations, and semantic HTML transformation are
implemented today. SharePoint synchronization, Confluence/ServiceNow
connectors, distributed workers, and score calibration remain planned work.
See [current MVP](../README.md#current-mvp) for the full boundary.
