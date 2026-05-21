---
skill_id: "write_results_narrative"
version: "7.0.0"
category: "writing"
domain_compatibility: ["all"]
required_tools: ["python", "openai|anthropic|litellm"]
depends_on: ["inferential_parametric", "inferential_nonparametric", "descriptive_stats"]
produces: ["reports/sections/results_section.md"]
complexity: "intermediate"
---

# Skill: Write Results Narrative

## Purpose
Generate a structured results narrative reporting descriptive statistics, inferential test results, effect sizes, and diagnostic findings in domain-appropriate prose.

## When to Use
- After all analysis completed
- Before discussion section
- For manuscript assembly

## When NOT to Use
- Only tables/figures needed
- Results not yet computed

## Execution Protocol

### Step 1: Descriptive Results
- Sample characteristics: N, demographics, key variable summaries
- Table 1 reference: "Baseline characteristics are shown in Table 1"
- Note any data quality issues: missingness, outliers, exclusions

### Step 2: Primary Analysis
- Report each hypothesis test in order of importance
- Format: test name, statistic, df, p-value, effect size, 95% CI
- State: direction and magnitude of effect
- Interpret: in substantive (not statistical) terms

### Step 3: Secondary Analysis
- Exploratory analyses: clearly labeled as such
- Subgroup analyses: which subgroups, why tested
- Sensitivity analyses: alternative specifications and whether conclusions change

### Step 4: Diagnostic Results
- Assumption test results: normality, homoscedasticity, independence
- Model fit: R², AIC, convergence diagnostics
- Note: any assumption violations and how addressed

### Step 5: Non-Significant Results
- Report non-significant findings with same detail as significant
- Include: effect size and CI (not just "p > .05")
- Interpret: whether CI rules out meaningful effects

## Reporting Rules
- Always report exact p-values (not just < .05), except p < .001
- Always report effect sizes with CIs
- Never interpret non-significant as "no effect"
- Distinguish: statistical significance vs practical significance
- Label: exploratory vs confirmatory analyses

## Output Specification
- `reports/sections/results_section.md`: complete results narrative with table/figure references

## Validation Checks
- [ ] All hypothesis tests reported
- [ ] Effect sizes and CIs included
- [ ] Non-significant results reported
- [ ] Diagnostic results included
- [ ] Table and figure references correct
