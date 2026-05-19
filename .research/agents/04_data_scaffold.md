---
agent_id: "data_scaffold"
version: "1.0.0"
description: "Create data/ analysis/ reports/ structure and strict validation/ingestion contracts."
domain_compatibility: ["all"]
depends_on:
  - "research_init"
  - "method_route"
composes:
  - "validate_schema"
  - "compute_hashes"
produces:
  - "analysis/01_validation.py"
  - "reports/data_dictionary.md"
  - "environment/requirements.txt"
---

# Agent: Data Scaffold

## Purpose
Build the calibrated directory structure, write ingestion/validation code, and generate the data dictionary.

## Inputs
- `data_raw/`
- `reports/baseline/initial_epistemic_baseline.md`
- `reports/papers_and_tools_cited.md`

## Execution Protocol
Generate and execute the validation script, then populate the data dictionary.
