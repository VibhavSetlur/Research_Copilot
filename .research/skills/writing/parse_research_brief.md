---
skill_id: "parse_research_brief"
version: "3.0.0"
category: "writing"
domain_compatibility: ["all"]
required_tools: ["python", "pyyaml"]
estimated_tokens: 2000
depends_on: []
produces: ["docs/parsed_research_brief.json"]
---

# Skill: Parse Research Brief

## Purpose
Parse, validate, and extract structured goals, hypotheses, and constraints from the researcher's raw Markdown brief.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `brief_path` | Path | Yes | Path to the raw research_brief.md file |

## Execution Protocol

### Step 1: Document Structure Parsing
- Load `research_brief.md`.
- Validate that it contains the 9 mandatory sections:
  1. Study Title
  2. Research Domain
  3. Hypotheses/Questions
  4. Dataset Description
  5. Variable Taxonomy
  6. Design Context
  7. Exclusion Criteria
  8. Deliverables
  9. Known Issues

### Step 2: Extraction and Normalization
- Extract hypotheses and format them as an array of structured objects containing: `id`, `text`, `null_hypothesis`, and `dependent_variable`.
- Parse variables and categorize them into `independent`, `dependent`, `confounders`, or `covariates`.
- Extract text parameters for sample exclusion criteria.

### Step 3: Validation checks
- Ensure at least one hypothesis and one dependent variable are declared.
- Output warning logs if the domain field does not match any of the standard system domain profiles.

## Output Specification
Produces:
- `docs/parsed_research_brief.json` containing normalized parameters.

## Validation Criteria
- [ ] Output JSON contains the `hypotheses` and `variables` keys.
- [ ] No section headers are empty.