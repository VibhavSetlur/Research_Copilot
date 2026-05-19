---
agent_id: "research_init"
version: "1.0.0"
description: "Initialize the project: parse brief, profile data, classify design, and establish baseline."
domain_compatibility: ["all"]
depends_on: []
composes:
  - "parse_research_brief"
  - "profile_tabular"
  - "detect_missingness"
  - "detect_outliers"
  - "power_analysis"
  - "compute_hashes"
produces:
  - "reports/baseline/initial_epistemic_baseline.md"
  - "reports/data_quality/missingness_report.md"
  - "reports/data_quality/outlier_report.md"
  - "reports/analysis/power_analysis.md"
  - "reports/logs/file_hashes.md"
---

# Agent: Research Init

## Purpose
Execute a skills-composed initialization pass that produces the epistemic baseline and core profiling artifacts.

## Inputs
- `docs_input/research_brief.md`
- `data_raw/` (read-only)

## Execution Protocol
Execute each skill listed in the YAML frontmatter in the order provided unless a dependency requires otherwise.

## Outputs
See the `produces` contract in the frontmatter.
