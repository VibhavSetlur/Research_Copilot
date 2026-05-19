---
agent_id: "execute_analysis"
version: "1.0.0"
description: "Run transformations, modeling, diagnostics, and produce figures/tables per RQ."
domain_compatibility: ["all"]
depends_on:
  - "data_scaffold"
composes:
  - "descriptive_stats"
  - "inferential_parametric"
produces:
  - "reports/logs/methods_log.md"
  - "data/03_analytical/"
---

# Agent: Execute Analysis

## Purpose
Execute the analysis plan per research question and maintain an append-only methods log.

## Inputs
- `data/01_ingested/`
- `reports/data_dictionary.md`
- `reports/papers_and_tools_cited.md`

## Execution Protocol
Execute the composed analysis skills and write outputs to `data/03_analytical/`.
