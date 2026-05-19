---
skill_id: "generate_apa_tables"
version: "7.0.0"
category: "writing"
domain_compatibility: ["psychology", "education", "social_sciences"]
required_tools: ["python", "pandas", "jinja2"]
depends_on: ["descriptive_stats", "inferential_parametric"]
produces: ["reports/tables/"]
complexity: "intermediate"
---

# Skill: Generate APA-Style Tables

## Purpose
Generate publication-ready tables in APA 7th edition format for descriptive statistics, regression results, and ANOVA tables.

## When to Use
- Results finalized
- Need tables for manuscript
- APA or similar formatting required

## When NOT to Use
- Only figures needed
- Non-APA format required (e.g., AMA, Chicago)

## Execution Protocol

### Step 1: Table 1 (Descriptive Statistics)
- Columns: Variable, M, SD, [Min, Max], Skew, Kurtosis, N
- For categorical: n (%)
- Grouped: if comparing groups, one column per group
- Footnotes: note any transformations, exclusions

### Step 2: Regression Table
- Columns: Predictor, B (or β), SE, 95% CI, p
- Organize: blocks of predictors (Step 1, Step 2, etc.)
- Bottom rows: R², ΔR², F, df
- Significance: * p < .05, ** p < .01, *** p < .001

### Step 3: ANOVA Table
- Columns: Source, SS, df, MS, F, p, η²
- Rows: between-groups, within-groups, total
- Post-hoc: pairwise comparisons with adjusted p-values

### Step 4: Formatting Rules (APA 7th)
- No vertical lines
- Horizontal lines: top, bottom, below column headers
- Font: same as manuscript (typically Times New Roman, 12pt)
- Table number and title above table
- Notes below table: general, specific, probability
- Decimal alignment: align on decimal point
- Leading zero: 0 for statistics that can exceed 1 (p, r), no 0 for statistics that cannot (F, t, χ²)

## Output Specification
- `reports/tables/`: individual table files in Markdown and LaTeX format

## Validation Checks
- [ ] No vertical lines
- [ ] Correct horizontal line placement
- [ ] Decimal formatting follows APA rules
- [ ] All statistics match computed values
- [ ] Table numbers sequential
