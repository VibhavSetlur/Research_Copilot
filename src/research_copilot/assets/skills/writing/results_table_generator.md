---
skill_id: "results_table_generator"
version: "1.0.0"
category: "writing"
depends_on: ["execute_analysis"]
produces: ["03_synthesis/tables/results_table.md", "03_synthesis/tables/results_table.tex", "03_synthesis/tables/results_table.html"]
complexity: "quick"
---

# Skill: Results Table Generator

## Purpose
Auto-generates APA/journal-formatted results tables from analysis JSON files. Three output formats from one data source.

---

## Protocol

### Step 1: Scan
Find all `*_results.json` in `02_experiments/*/outputs/analysis/`.

### Step 2: Extract Data
Parse each JSON for: variable name (`variable`/`predictor`/`term`), coefficient (`coef`/`estimate`/`beta`/`b`), SE (`se`/`std_err`), 95% CI (`ci_lower`/`ci_upper`), p-value (`pvalue`/`p_value`/`p`), N (`nobs`/`n`).

### Step 3: Classify Table Type
- **Regression**: has `coef`, `se`, `pvalue` per predictor → coefficient table with CI
- **ANOVA**: has `source`, `df`, `F`, `pvalue` per term → ANOVA summary
- **Descriptive**: has `mean`, `sd`, `min`, `max`, `n` per variable → descriptive statistics

### Step 4: Generate Markdown
GitHub-flavored table with columns: Variable, *b*, *SE*, 95% CI, *p*. Italicize statistics. Note below table: N, model fit (R², F, df, p). Significance footnote: *p* < .05, **p* < .01, ***p* < .001.

### Step 5: Generate LaTeX (booktabs)
`\begin{table}` with `\toprule`, `\midrule`, `\bottomrule`. No vertical lines. Negative signs use `$-$`. Italicize statistics. Use `tablenotes` for footnotes. Column alignment: left for variables, right for numbers.

### Step 6: Generate HTML
Styled table with `<caption>`, `<thead>`, `<tbody>`. No inline styles. Use CSS class `results-table`. Footnote paragraph below table with significance legend.

### Step 7: Format p-values
0.000 → `< .001`. 0.001-0.009 → `< .01`. 0.010-0.999 → exact, 3 decimals. No leading zero.

### Step 8: Write Output
Save all three formats to `03_synthesis/tables/`. Write `table_manifest.json` indexing all tables with source files.

---

## Validation
- [ ] No vertical lines in any format
- [ ] Significance footnote present
- [ ] All coefficients have SE and CI
- [ ] p-values formatted correctly (no leading zero, 3 decimals)
- [ ] Table number and title present
- [ ] Model fit statistics in note
