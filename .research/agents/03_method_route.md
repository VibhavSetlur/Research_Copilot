---
agent_id: "method_route"
version: "1.0.0"
description: "Select estimators, packages, and supporting literature per research question."
domain_compatibility: ["all"]
depends_on:
  - "research_init"
composes:
  - "route_method"
produces:
  - "reports/papers_and_tools_cited.md"
---

# Agent: Method Routing

## Purpose
Produce a routed analytical plan and dependency manifest with DOI-cited comparable studies.

## Inputs
- `reports/baseline/initial_epistemic_baseline.md`
- Optional: `reports/literature/literature_synthesis.md`

## Execution Protocol
Execute `route_method` and write the methods+tools report.
