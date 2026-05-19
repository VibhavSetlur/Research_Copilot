---
skill_id: "route_method"
version: "5.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "pyyaml", "notebooklm-py"]
estimated_tokens: 3000
depends_on: ["classify_domain", "profile_tabular"]
produces: ["analysis/methods_routing.json"]
---

# Skill: Analytical Methodology Routing

## Purpose
Route data profiles to appropriate analysis skills and audit choices using NotebookLM.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `brief_path` | Path | Yes | Path to brief |
| `profile_path` | Path | Yes | Path to profile |
| `notebook_id` | Str | No | NotebookLM ID |

## Execution Protocol
1. Classify study variables and model constraints.
2. Apply routing tree rules to select parametric, non-parametric, time-series, or spatial skills.
3. Validate choices using NotebookLM query.

## Diagnostics & Interpretation Guide (What to Look For)
- **NotebookLM warning flags**:
  - *Interpret*: The target domain literature uses alternative models.
  - *Action*: Append warnings recommending the alternative models to the routing JSON.

## Output Specification
Produces `analysis/methods_routing.json` mapping selected skills.

## Validation Criteria
- [ ] Output contains at least one validated skill ID.