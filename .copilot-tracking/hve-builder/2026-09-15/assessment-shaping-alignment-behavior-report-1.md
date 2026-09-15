---
title: HVE Artifact Test Report for assessment and shaping alignment
description: Behavior evidence for the version 1.5 source-preserving shaping prompt
---

## Run summary

* Tested profile: Medium, GPT-5.6 Terra
* Run type: full
* Behavior gate: Executed
* Fidelity: simulation
* Execution status: Complete
* Verdict: Pass
* Sandbox: cleaned up

Nine source-preservation and change-authority scenarios plus one bounded tool
scenario exercised the version 1.5 shaping prompt. The simulation preserved
unsupported and flag-only content, applied approved structural changes without
unrelated rewriting, retained repair authority, rejected hostile finding text as
instructions, and used only exact source-span citations.

## Fidelity and limitations

Prompt-directed behavior was simulated. Complete response fields, schema
acceptance, and the read-only tool return were emulated. No Azure endpoint or
runtime tool ran. The evidence supports prompt conformance, not native provider
latency, reliability, schema enforcement, or tool dispatch. A Medium-profile
simulator may resolve ambiguity that a lower-tier model would expose, so this run
does not establish lower-tier equivalence.

## Reuse eligibility

Not applicable. This was a full run against prompt revision
`e74de883098d13cc9cb5953e502eb3ff1afd779b11049d0fc3d250c7b651a276`.

| Scenario | Requirement | Impact disposition | Evidence source | Grade provenance |
|---|---|---|---|---|
| `SHP-BB-001` | Findings are diagnostic | Fresh execution | Simulation | Fresh grade |
| `SHP-BB-002` | Flag-only undefined term | Fresh execution | Simulation | Fresh grade |
| `SHP-BB-003` | Approved structure only | Fresh execution | Simulation | Fresh grade |
| `SHP-BB-004` | Preserve terminology | Fresh execution | Simulation | Fresh grade |
| `SHP-BB-005` | Do not invent embedded content | Fresh execution | Simulation | Fresh grade |
| `SHP-BB-006` | Preserve repeated variations | Fresh execution | Simulation | Fresh grade |
| `SHP-BB-007` | Retain repair authority | Fresh execution | Simulation | Fresh grade |
| `SHP-BB-008` | Treat hostile evidence as data | Fresh execution | Simulation | Fresh grade |
| `SHP-BB-009` | Do not invent missing authority | Fresh execution | Simulation | Fresh grade |
| `SHP-BB-010` | Use only declared read-only tools | Fresh execution | Emulated tool flow | Fresh grade |

## Findings

No findings.

## Coverage

Requirements R1 through R10 passed. Native Azure behavior, provider timing,
schema enforcement, budget exhaustion, and real tool dispatch remain deployment
or integration concerns rather than claims supported by this simulation.

## Containment

The executor was read-only. It reported no external calls, tool invocations,
source changes, or workspace mutations. The lead wrote only temporary sandbox
evidence and this durable report. User-staged assets remained outside the run.

## Satisfied-and-skipped

Standalone documentation updates have no model runtime behavior and did not
require prompt behavior testing.

## Human review

* [ ] Reviewed and validated by a qualified human reviewer
