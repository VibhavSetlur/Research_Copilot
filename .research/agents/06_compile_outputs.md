---
agent_id: "compile_outputs"
version: "1.0.0"
description: "Compile results into a publication-style report and stakeholder-facing outputs."
domain_compatibility: ["all"]
depends_on:
  - "execute_analysis"
composes:
  - "write_imrad"
produces:
  - "reports/manuscript/research_findings.md"
---

# Agent: Compile Outputs

## Purpose
Compile results, figures, and logs into a final report package.

## Inputs
- `data/03_analytical/`
- `reports/logs/methods_log.md`
- `reports/papers_and_tools_cited.md`

## Execution Protocol
Execute the composed writing skills.
