---
skill_id: "inferential_nonparametric"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "scipy", "statsmodels"]
depends_on: ["descriptive_stats"]
produces: ["analysis/03_analytical/nonparametric_results.json"]
complexity: "intermediate"
---

# Skill: Non-Parametric Inferential Testing

## Purpose
Conduct distribution-free hypothesis tests when parametric assumptions are violated or data is ordinal.

## When to Use
- Parametric assumptions violated (normality, homoscedasticity)
- Data is ordinal (Likert scales, rankings)
- Sample size too small for CLT (N < 30 per group)
- Data has extreme outliers that cannot be removed

## When NOT to Use
- Parametric assumptions met (parametric tests are more powerful)
- Data is nominal categorical (use chi-square instead)
- Sample is large and approximately normal (parametric is fine)

## Decision Protocol

### Test Selection
| Parametric Equivalent | Non-Parametric Alternative | Design |
|----------------------|---------------------------|--------|
| Independent t-test | Mann-Whitney U (Wilcoxon rank-sum) | 2 independent groups |
| Paired t-test | Wilcoxon signed-rank | 2 paired groups |
| One-way ANOVA | Kruskal-Wallis H | 3+ independent groups |
| Repeated measures ANOVA | Friedman test | 3+ paired groups |
| Pearson correlation | Spearman rank correlation | Continuous association |
| Pearson correlation | Kendall's tau | Ordinal association, small N |

## Execution Protocol

### Step 1: Test Selection & Rationale
- Document why non-parametric is chosen (assumption violation, ordinal data, small N)
- Select appropriate test from decision table

### Step 2: Test Execution
- Run selected test
- Report: test statistic, exact p-value (not asymptotic if N < 20)
- For Mann-Whitney U: report U statistic and rank-biserial correlation
- For Kruskal-Wallis: report H statistic and epsilon-squared effect size

### Step 3: Effect Size Computation
**Mann-Whitney U:**
- Rank-biserial correlation: r_rb = 1 - (2U) / (n₁ × n₂)
- Common language effect size: probability that random X > random Y

**Kruskal-Wallis:**
- Epsilon-squared: ε² = (H - k + 1) / (N - k)
- Interpret: 0.01 = small, 0.04 = medium, 0.16 = large

**Spearman/Kendall:**
- Report correlation coefficient with 95% CI
- Interpret as monotonic (not linear) association

### Step 4: Post-Hoc Tests (Kruskal-Wallis only)
- If omnibus test significant: pairwise Mann-Whitney U with Holm-Bonferroni correction
- Report adjusted p-values for each pair

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| Ties | < 10% of observations | Many tied ranks | Use exact test or permutation |
| Sample size | N ≥ 10 per group | Very small | Use exact permutation test |
| Effect direction | Consistent with medians | Paradoxical result | Check for Simpson's paradox |

### Red Flags
- **Mann-Whitney significant but medians equal**: distributions differ in shape, not location; report distributional difference
- **Many ties (> 25%)**: rank-based tests lose power; consider permutation test
- **Kruskal-Wallis significant but no post-hoc pairs significant**: omnibus detects subtle differences; report with caution

## Reporting Template
> "Due to violation of normality assumptions (Shapiro-Wilk p < .001), a Mann-Whitney U test was conducted. [Group A] (Median = [value], N = [value]) scored significantly [higher/lower] than [Group B] (Median = [value], N = [value]), U = [value], p = [value], r_rb = [value], 95% CI [lower, upper]."

## Output Specification
- `analysis/03_analytical/nonparametric_results.json`: test results, effect sizes, CIs, rationale for non-parametric choice

## Validation Checks
- [ ] Test statistic matches rank-based formula
- [ ] p-value in [0, 1]
- [ ] Effect size in [-1, 1] for correlation measures
- [ ] Post-hoc tests corrected for multiple comparisons
