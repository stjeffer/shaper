---
title: Shaper FAQ
description: Frequently asked questions about Shaper's scope, safety, and limitations
ms.topic: faq
---

## Is Shaper an AI agent?

No. Shaper is a platform that coordinates bounded specialist agents
(Assessment, Knowledge, Transformation, Governance, and Agent Readiness)
while retaining deterministic control of authorization, evidence lineage,
workflow, approval, and publication. See
[platform architecture](../docs/architecture.md) for the full boundary.

## Does Shaper replace SharePoint, RAG pipelines, or enterprise search?

No. Shaper fills the gap between content governance and content retrieval.
It improves the quality, consistency, authority, and agent readiness of the
knowledge those systems consume; it does not manage, find, or retrieve
content itself.

## Can Shaper modify my source documents automatically?

No. Every transformation mode stops at a human approval boundary. Safe mode
creates derivative summaries and metadata while leaving originals untouched;
guided rewrite proposes changes for human review; knowledge consolidation
prepares a canonical source and supporting package. Publication remains a
human-governed action, and approved artifacts require a second human review
before their content can be retrieved.

## What does the readiness score mean?

The 0–100 readiness score is an uncalibrated deterministic heuristic across
content quality, knowledge quality, and agent readiness dimensions. It is
not an accuracy percentage or model-confidence score. Production quality
claims require calibration against a representative, human-reviewed estate.
See [improvement reporting](../docs/improvement-reporting.md) for how paired
evaluation results are measured and gated.

## Does registering a SharePoint source synchronize its content?

Not yet. SharePoint entries are truthful registrations until Microsoft Graph
consent and synchronization are configured. Confluence, ServiceNow, arbitrary
wiki crawling, and distributed workers remain follow-up work. See
[current MVP](../README.md#current-mvp) for the complete implementation
boundary.

## Where is workflow and estate state stored?

Azure Database for PostgreSQL persists estates, workflows, decisions, token
usage, reviews, and artifact manifests in Azure deployments. A process-local
SQLite store supports local development state and legacy compilation
checkpoints only.

## How do I get help with deployment or operations?

See [Deployment](Deployment.md) and [docs/operations.md](../docs/operations.md)
for monitoring, recovery, retention, and the upgrade procedure.
