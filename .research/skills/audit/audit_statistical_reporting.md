---
skill_id: "audit_statistical_reporting"
version: "7.0.0"
category: "audit"
domain_compatibility: ["all"]
required_tools: ["python", "openai|anthropic|litellm"]
depends_on: ["write_imrad"]
produces: ["audit/statistical_reporting_audit.json"]
complexity: "intermediate"
---

# Skill: Statistical Reporting Audit

## Purpose
Verify that all statistical results are reported completely and correctly: test statistics, degrees of freedom, p-values, effect sizes, and confidence intervals.

## When to Use
- After manuscript written
- Before submission
- For quality assurance

## When NOT to Use
- Manuscript not yet complete
- Only exploratory analysis

## Execution Protocol

### Step 1: Completeness Check
For each reported statistical test, verify presence of:
- Test name (e.g., "independent-samples t-test")
- Test statistic value (e.g., t = 2.34)
- Degrees of freedom (e.g., df = 48)
- Exact p-value (e.g., p = .023, not p < .05)
- Effect size (e.g., d = 0.67)
- 95% confidence interval for effect size

### Step 2: Consistency Check
- Values in text match values in tables
- Values in tables match values in analysis output
- Percentages sum to 100% (or noted otherwise)
- Sample sizes consistent across sections

### Step 3: Formatting Check
- p-values: italicized, no leading zero (p = .023)
- Statistics: italicized (t, F, χ², r, β)
- Degrees of freedom: in parentheses, not italicized
- Effect sizes: reported with interpretation benchmarks
- Confidence intervals: square brackets, 95% specified

### Step 4: Multiple Testing Check
- If multiple tests: correction method stated
- Adjusted p-values reported alongside raw p-values
- Family-wise error rate or FDR controlled

### Step 5: Assumption Reporting
- For parametric tests: normality and homoscedasticity checks reported
- For regression: multicollinearity, residual diagnostics reported
- For violations: alternative methods or robust SEs stated

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| Completeness | All 6 elements present | Add missing elements |
| Consistency | All values match | Correct discrepancies |
| Formatting | APA/domain style | Fix formatting |
| Multiple testing | Correction applied | Add correction or justify |

## Output Specification
- `audit/statistical_reporting_audit.json`: per-test completeness, consistency, formatting results

## Validation Checks
- [ ] Every statistical test has all required elements
- [ ] No value discrepancies between text and tables
- [ ] Formatting follows domain standard
- [ ] Multiple testing addressed
