---
skill_id: "power_analysis"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "scipy", "statsmodels"]
depends_on: ["descriptive_stats"]
produces: ["analysis/03_analytical/power_analysis.json"]
complexity: "intermediate"
---

# Skill: Power Analysis & Sample Size Calculation

## Purpose
Compute statistical power for planned or completed analyses, and determine required sample sizes for desired power levels.

## When to Use
- Before data collection: determine required sample size
- After analysis: compute achieved power (post-hoc)
- When interpreting non-significant results: was the study underpowered?

## When NOT to Use
- Effect size is completely unknown and cannot be estimated
- Only descriptive analysis planned (no hypothesis testing)

## Decision Protocol

### Test-Specific Power Calculation
| Test | Effect Size Metric | Inputs Needed |
|------|-------------------|---------------|
| t-test (independent) | Cohen's d | d, α, power, allocation ratio |
| t-test (paired) | Cohen's d_z | d_z, α, power |
| ANOVA | Cohen's f | f, α, power, groups, n per group |
| Correlation | Pearson's r | r, α, power |
| Chi-square | w (effect size) | w, α, power, df |
| Regression (multiple) | f² | f², α, power, predictors |
| Proportion test | h (Cohen's h) | h, α, power |

## Execution Protocol

### Step 1: Effect Size Estimation
**Sources (in order of preference):**
1. Meta-analysis of similar studies (most reliable)
2. Pilot study or preliminary data
3. Smallest effect size of theoretical/practical importance
4. Conventional benchmarks (Cohen's small/medium/large) as last resort

**Caution:** Do not use observed effect size from the same data for power analysis (circular reasoning)

### Step 2: A Priori Power Analysis (planning)
- Set α = 0.05 (or domain-specific threshold)
- Set desired power: 0.80 (minimum), 0.90 (recommended)
- Input effect size from Step 1
- Compute: required sample size N
- Account for expected attrition: N_adjusted = N / (1 - attrition_rate)

### Step 3: Post-Hoc Power Analysis (completed study)
- Input: actual sample size, observed effect size, α
- Compute: achieved power
- If power < 0.80: non-significant result may be due to low power, not null effect
- Report: "The study had [percentage]% power to detect an effect of d = [value]"

### Step 4: Sensitivity Analysis
- Vary effect size: what power for smaller/larger effects?
- Vary sample size: what effect size detectable with current N?
- Plot: power curve (power vs sample size for range of effect sizes)

### Step 5: Multiple Testing Adjustment
- If multiple hypotheses: adjust α before power calculation
- Bonferroni: α_adj = α / m tests
- Power decreases as α becomes more stringent
- Report: power for each hypothesis separately

## Diagnostics & Interpretation

| Result | Interpretation | Action |
|--------|---------------|--------|
| Power ≥ 0.80 | Adequately powered | Proceed with confidence |
| Power 0.50-0.80 | Underpowered | Interpret non-significant results cautiously |
| Power < 0.50 | Severely underpowered | Non-significant results are uninformative |
| Required N >> available | Infeasible study | Increase effect size (stronger manipulation) or accept lower power |

### Red Flags
- **Post-hoc power based on observed effect size**: circular; use observed CI instead
- **Power = 1.00**: effect size likely overestimated or N very large
- **Required N in thousands**: effect size too small to detect practically; reconsider research question
- **Different tests give different N**: use the largest N (most conservative)

## Reporting Template
> "An a priori power analysis using G*Power indicated that a sample of N = [value] was required to detect an effect of d = [value] with 80% power at α = .05 (two-tailed). Accounting for an expected attrition rate of [percentage]%, the target recruitment was N = [value]. The achieved sample of N = [value] provided [percentage]% power."

## Output Specification
- `analysis/03_analytical/power_analysis.json`: effect size, α, power, required N, achieved N, sensitivity analysis, power curve data

## Validation Checks
- [ ] Effect size source documented
- [ ] Power in [0, 1]
- [ ] Required N is positive integer
- [ ] Attrition adjustment applied if specified
