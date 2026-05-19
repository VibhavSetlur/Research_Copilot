---
skill_id: "generate_apa_tables"
version: "3.0.0"
category: "writing"
domain_compatibility: ["all"]
required_tools: ["python", "pandas", "tabulate"]
estimated_tokens: 2500
depends_on: ["interpret_effect_sizes"]
produces: ["reports/tables/"]
---

# Skill: Generate APA Tables (LaTeX/Markdown)

## Purpose
Convert raw descriptive and inferential statistics into publication-ready APA-7th styled tables in Markdown and LaTeX.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `descriptive_results` | Path | Yes | Path to descriptive_stats.json |
| `inferential_results` | Path | Yes | Path to results_interpreted.json |

## Execution Protocol

### Step 1: Layout Designing
- Descriptive Tables: Format as Variable name, Stratified Columns, and overall metrics. Format continuous values as `Mean (SD)` and categorical as `n (%)`.
- Regression/Inferential Tables: Column structure must represent: Parameter, Coefficient (b), Standard Error (SE), 95% Confidence Interval [LL, UL], test statistic (t/z/F), and p-value.

### Step 2: LaTeX Generation Rules
- Enforce the three-line rule:
  - Header top line (`\toprule`).
  - Header bottom line (`\midrule`).
  - Table bottom line (`\bottomrule`).
- Remove all vertical lines (`|`).
- Place table titles **above** the table.

### Step 3: Markdown Generation
- Format markdown tables using standard GFM headers.

## Output Specification
Produces in `reports/tables/`:
- `descriptive_table.md`
- `descriptive_table.tex`
- `inferential_table.md`
- `inferential_table.tex`

## Validation Criteria
- [ ] LaTeX output does not contain the vertical cell separator character (`|`).
- [ ] Table headers explicitly define measurement units where applicable.