---
title: Shaper Platform Architecture
description: C4 architecture for the Shaper Knowledge Transformation Platform and its specialist agents
ms.date: 2026-09-10
ms.topic: concept
---

## Architectural position

Shaper is not an agent. It is an Azure-native Knowledge Transformation Platform
that coordinates bounded specialist agents while retaining deterministic control
of identity, authorization, evidence lineage, workflow, approval, and publication.

An agent is a capability role inside the platform. A role can use deterministic
analysis, model-assisted reasoning, or both. Calling a component an agent does
not grant it authority to modify source content or bypass human review.

The diagrams describe the planned platform architecture. Labels identify planned
elements that are not part of the current deployment. The current MVP runs the
API, orchestrator, specialist analysis roles, transformation kernel, and review
boundary in one Azure Container Apps container.

## System Context

```mermaid
---
config:
  flowchart:
    subGraphTitleMargin:
      bottom: 30
---
flowchart TB
    subgraph layout_top[" "]
        person_knowledge_practitioner(["`**Knowledge Practitioner**
*[Person]*
Assesses and governs enterprise knowledge`"])
        ext_product_clients["`**Product Clients (planned)**
*[External System]*
SharePoint, Copilot, Teams, and Foundry surfaces`"]
        ext_consuming_agents["`**Consuming Agents and Search**
*[External System]*
Uses approved agent-ready knowledge`"]
    end
    subgraph layout_center[" "]
        sys_shaper["`**Shaper**
*[Software System]*
Transforms unmanaged content into trusted knowledge`"]
    end
    subgraph layout_bottom[" "]
        ext_content_repositories["`**Enterprise Content Repositories**
*[External System]*
SharePoint, OneDrive, files, wikis, and knowledge bases`"]
        ext_azure_ai_services["`**Azure AI Services**
*[External System]*
Provides bounded model inference`"]
    end

    person_knowledge_practitioner -->|"`uses directly
*[HTTPS]*`"| sys_shaper
    person_knowledge_practitioner -->|"`uses planned experiences through`"| ext_product_clients
    ext_product_clients -->|"`calls platform capabilities
*[REST/HTTPS]*`"| sys_shaper
    ext_consuming_agents -->|"`retrieves approved knowledge from`"| sys_shaper
    sys_shaper -->|"`reads governed content from`"| ext_content_repositories
    sys_shaper -->|"`requests bounded inference from
*[HTTPS]*`"| ext_azure_ai_services

    classDef person fill:#08427b,stroke:#052e56,color:#ffffff
    classDef system fill:#1168bd,stroke:#0b4884,color:#ffffff
    classDef external fill:#999999,stroke:#6b6b6b,color:#ffffff

    class person_knowledge_practitioner person
    class sys_shaper system
    class ext_product_clients,ext_consuming_agents,ext_content_repositories,ext_azure_ai_services external

    style layout_top fill:none,stroke:none
    style layout_center fill:none,stroke:none
    style layout_bottom fill:none,stroke:none
```

## Containers

```mermaid
---
config:
  flowchart:
    subGraphTitleMargin:
      bottom: 30
---
flowchart TB
    subgraph layout_top[" "]
        person_knowledge_practitioner(["`**Knowledge Practitioner**
*[Person]*
Assesses and governs enterprise knowledge`"])
        ext_product_clients["`**Product Clients (planned)**
*[External System]*
SharePoint, Copilot, Teams, and Foundry surfaces`"]
        ext_consuming_agents["`**Consuming Agents and Search**
*[External System]*
Uses approved agent-ready knowledge`"]
    end

    subgraph layout_center[" "]
        subgraph sys_shaper["`**Shaper** *[Software System]*`"]
            ctr_shaper_api_orchestrator("`**Shaper API and Orchestrator**
*[Container: Python and FastAPI]*
Exposes capabilities and coordinates bounded agents`")
            ctr_specialist_workers("`**Specialist Workers (planned)**
*[Container: Azure Container Apps]*
Runs scalable specialist-agent jobs`")
            ctr_workflow_state[("`**Workflow State**
*[Container: SQLite today, PostgreSQL planned]*
Stores jobs, approvals, provenance, and checkpoints`")]
            ctr_knowledge_asset_store[("`**Knowledge Asset Store**
*[Container: Azure Files today, Blob Storage planned]*
Stores immutable uploads and approved releases`")]
            ctr_search_projection[("`**Knowledge Search Projection (planned)**
*[Container: Azure AI Search]*
Projects approved knowledge for retrieval`")]
        end
    end

    subgraph layout_bottom[" "]
        ext_content_repositories["`**Enterprise Content Repositories**
*[External System]*
SharePoint, OneDrive, files, wikis, and knowledge bases`"]
        ext_azure_ai_services["`**Azure AI Services**
*[External System]*
Provides bounded model inference`"]
    end

    person_knowledge_practitioner --->|"`uses
*[HTTPS]*`"| ctr_shaper_api_orchestrator
    ext_product_clients --->|"`calls
*[REST/HTTPS]*`"| ctr_shaper_api_orchestrator
    ext_consuming_agents --->|"`queries approved knowledge through`"| ctr_shaper_api_orchestrator
    ctr_shaper_api_orchestrator -->|"`stores workflow evidence in`"| ctr_workflow_state
    ctr_shaper_api_orchestrator -->|"`stores immutable assets in`"| ctr_knowledge_asset_store
    ctr_shaper_api_orchestrator -->|"`dispatches planned asynchronous work to`"| ctr_specialist_workers
    ctr_specialist_workers -->|"`reads governed content from`"| ext_content_repositories
    ctr_specialist_workers -->|"`requests bounded inference from
*[HTTPS]*`"| ext_azure_ai_services
    ctr_specialist_workers -->|"`records workflow evidence in`"| ctr_workflow_state
    ctr_specialist_workers -->|"`writes approved assets to`"| ctr_knowledge_asset_store
    ctr_specialist_workers -->|"`projects approved knowledge into`"| ctr_search_projection
    ext_consuming_agents -->|"`queries approved knowledge in`"| ctr_search_projection

    classDef person fill:#08427b,stroke:#052e56,color:#ffffff
    classDef container fill:#438dd5,stroke:#2e6295,color:#ffffff
    classDef external fill:#999999,stroke:#6b6b6b,color:#ffffff

    class person_knowledge_practitioner person
    class ctr_shaper_api_orchestrator,ctr_specialist_workers,ctr_workflow_state,ctr_knowledge_asset_store,ctr_search_projection container
    class ext_product_clients,ext_consuming_agents,ext_content_repositories,ext_azure_ai_services external

    style layout_top fill:none,stroke:none
    style layout_center fill:none,stroke:none
    style layout_bottom fill:none,stroke:none
    style sys_shaper fill:none,stroke:#888888,stroke-dasharray:5 5,color:#888888
```

## Shaper API and Orchestrator Components

```mermaid
---
config:
  flowchart:
    subGraphTitleMargin:
      bottom: 30
---
flowchart TB
    subgraph layout_top[" "]
        person_knowledge_practitioner(["`**Knowledge Practitioner**
*[Person]*
Assesses and governs enterprise knowledge`"])
        ext_product_clients["`**Product Clients (planned)**
*[External System]*
SharePoint, Copilot, Teams, and Foundry surfaces`"]
        ext_consuming_agents["`**Consuming Agents and Search**
*[External System]*
Uses approved agent-ready knowledge`"]
    end

    subgraph layout_center[" "]
        subgraph ctr_shaper_api_orchestrator["`**Shaper API and Orchestrator**
*[Container]*`"]
            cmp_http_mcp_api["`**HTTP and MCP API**
*[Component: FastAPI and MCP]*
Authenticates and exposes platform capabilities`"]
            cmp_knowledge_transformation_orchestrator["`**Knowledge Transformation Orchestrator**
*[Component: Python]*
Coordinates one stateless platform analysis`"]
            cmp_assessment_agent["`**Assessment Agent**
*[Component]*
Audits content health`"]
            cmp_knowledge_agent["`**Knowledge Agent**
*[Component]*
Models topics, overlap, conflicts, and authority`"]
            cmp_transformation_agent["`**Transformation Agent**
*[Component]*
Proposes human-governed transformations`"]
            cmp_governance_agent["`**Governance Agent**
*[Component]*
Identifies conditions requiring continuous monitoring`"]
            cmp_agent_readiness_agent["`**Agent Readiness Agent**
*[Component]*
Measures usability for consuming agents`"]
            cmp_compilation_service["`**Compilation Service**
*[Component]*
Shapes submitted content into review candidates`"]
            cmp_review_service["`**Review Service**
*[Component]*
Enforces approval before publication`"]
        end
    end

    subgraph layout_bottom[" "]
        ctr_workflow_state[("`**Workflow State**
*[Container: SQLite today, PostgreSQL planned]*
Stores jobs, approvals, provenance, and checkpoints`")]
        ctr_knowledge_asset_store[("`**Knowledge Asset Store**
*[Container: Azure Files today, Blob Storage planned]*
Stores immutable uploads and approved releases`")]
        ext_azure_ai_services["`**Azure AI Services**
*[External System]*
Provides bounded model inference`"]
    end

    person_knowledge_practitioner --->|"`uses
*[HTTPS]*`"| cmp_http_mcp_api
    ext_product_clients --->|"`calls
*[REST/HTTPS]*`"| cmp_http_mcp_api
    ext_consuming_agents --->|"`queries approved knowledge through`"| cmp_http_mcp_api
    cmp_http_mcp_api -->|"`requests estate analysis from
*[in-process call]*`"| cmp_knowledge_transformation_orchestrator
    cmp_knowledge_transformation_orchestrator -->|"`requests content-health evidence from
*[in-process call]*`"| cmp_assessment_agent
    cmp_knowledge_transformation_orchestrator -->|"`requests knowledge evidence from
*[in-process call]*`"| cmp_knowledge_agent
    cmp_knowledge_transformation_orchestrator -->|"`requests transformation proposals from
*[in-process call]*`"| cmp_transformation_agent
    cmp_knowledge_transformation_orchestrator -->|"`requests governance evidence from
*[in-process call]*`"| cmp_governance_agent
    cmp_knowledge_transformation_orchestrator -->|"`requests readiness evidence from
*[in-process call]*`"| cmp_agent_readiness_agent
    cmp_http_mcp_api -->|"`submits bounded shaping work to
*[in-process call]*`"| cmp_compilation_service
    cmp_compilation_service -->|"`requests structured inference from
*[HTTPS]*`"| ext_azure_ai_services
    cmp_compilation_service -->|"`submits candidates to
*[in-process call]*`"| cmp_review_service
    cmp_review_service -->|"`stores approval state in`"| ctr_workflow_state
    cmp_compilation_service -->|"`publishes approved releases to`"| ctr_knowledge_asset_store

    classDef person fill:#08427b,stroke:#052e56,color:#ffffff
    classDef component fill:#85bbf0,stroke:#5d82a8,color:#000000
    classDef container fill:#438dd5,stroke:#2e6295,color:#ffffff
    classDef external fill:#999999,stroke:#6b6b6b,color:#ffffff

    class person_knowledge_practitioner person
    class cmp_http_mcp_api,cmp_knowledge_transformation_orchestrator,cmp_assessment_agent,cmp_knowledge_agent,cmp_transformation_agent,cmp_governance_agent,cmp_agent_readiness_agent,cmp_compilation_service,cmp_review_service component
    class ctr_workflow_state,ctr_knowledge_asset_store container
    class ext_product_clients,ext_consuming_agents,ext_azure_ai_services external

    style layout_top fill:none,stroke:none
    style layout_center fill:none,stroke:none
    style layout_bottom fill:none,stroke:none
    style ctr_shaper_api_orchestrator fill:none,stroke:#888888,stroke-dasharray:5 5,color:#888888
```

## Agent responsibility boundaries

| Specialist role       | Owns                                                            | Does not own                                      |
|-----------------------|-----------------------------------------------------------------|---------------------------------------------------|
| Assessment Agent      | Content health, metadata, staleness, ownership, readability     | Topic authority or source mutation                |
| Knowledge Agent       | Topics, entities, relationships, overlap, conflicts, authority  | Approval or publication                           |
| Transformation Agent  | Canonicalization, FAQ, summary, metadata, and procedure proposals | Autonomous overwrite or publication             |
| Governance Agent      | Duplicate, contradiction, ownership, freshness, authority health | Current recurring scheduling in the MVP          |
| Agent Readiness Agent | Retrieval, clarity, FAQ, chunking, consistency, prioritized work | Accuracy or model-confidence claims               |

The Knowledge Agent is the central knowledge-understanding role. It turns
document-level evidence into topic and relationship evidence that informs
recommendations, transformation proposals, readiness, and later governance
checks. The deterministic orchestrator owns the sequence and shared assessment
identity, so no specialist can silently redefine the evidence boundary.

## Current implementation boundary

The authenticated `POST /v1/platform/analyses` endpoint performs one synchronous,
stateless analysis. It creates one immutable estate assessment and coordinates
all five specialist roles over that evidence. Every result references the same
assessment identity.

The Transformation Agent output is proposal-only and reports that estate-wide
execution is unavailable. The separate compilation service can shape one
submitted upload, but it still requires independent validation and human approval
before publication.

Continuous governance currently means identifying monitorable conditions.
Recurring scans, managed schedules, durable source checkpoints, and distributed
workers remain planned capabilities.

## Product surface order

1. Azure-native platform
2. REST API
3. Copilot Agent
4. SharePoint integration
5. Teams integration
6. Foundry integration

SharePoint remains an important source, dashboard, review, and delivery surface.
It does not define the Shaper system boundary.

## Sources and notation

C4 concepts are based on the [C4 Model](https://c4model.com/) by Simon Brown,
licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Mermaid syntax follows the [Mermaid flowchart documentation](https://mermaid.js.org/syntax/flowchart.html),
licensed under the [MIT License](https://github.com/mermaid-js/mermaid/blob/develop/LICENSE).
