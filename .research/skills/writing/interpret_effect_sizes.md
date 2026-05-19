---
skill_id: "interpret_effect_sizes"
version: "3.0.0"
category: "writing"
domain_compatibility: ["all"]
required_tools: ["python"]
estimated_tokens: 2000
depends_on: []
produces: ["analysis/03_analytical/results_interpreted.json"]
---

# Skill: Interpret Effect Sizes (Standard Thresholds)

## Purpose
Apply statistical standards to categorize and interpret computed effect sizes based on domain-specific conventions.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `results_path` | Path | Yes | Path to results JSON containing raw effect sizes |
| `domain` | Str | Yes | Target scientific domain (e.g., 'psychology', 'epidemiology') |

## Execution Protocol

### Step 1: Threshold Extraction
- Load corresponding effect size interpretation maps:
  - **Cohen's d**: Small (>= 0.20), Medium (>= 0.50), Large (>= 0.80).
  - **Pearson's r**: Small (>= 0.10), Medium (>= 0.30), Large (>= 0.50).
  - **Odds Ratio (OR)**: Small (>= 1.50 or <= 0.67), Medium (>= 2.50 or <= 0.40), Large (>= 4.30 or <= 0.23).
  - **Eta-squared**: Small (>= 0.01), Medium (>= 0.06), Large (>= 0.14).

### Step 2: Categorization
- Match calculated effect sizes to classifications: "Trivial/Negligible", "Small", "Medium", or "Large".
- Check if confidence intervals overlap with the null effect (0 for differences, 1 for ratios). If they overlap, flag the effect as "Statistically Indeterminate" regardless of size.

### Step 3: Output Serialization
- Append qualitative interpretation strings and classification categories back to the JSON object.

## Output Specification
Produces:
- `analysis/03_analytical/results_interpreted.json`

## Validation Criteria
- [ ] Every statistical test in the output JSON contains a qualitative interpretation field.
- [ ] Overlapping confidence intervals with the null value are correctly flagged.