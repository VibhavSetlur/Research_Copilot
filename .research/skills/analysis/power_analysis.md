---
skill_id: "power_analysis"
version: "5.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "statsmodels"]
estimated_tokens: 2500
depends_on: []
produces: ["analysis/03_analytical/power_analysis_results.json"]
---

# Skill: Statistical Power Analysis

## Purpose
Determine required sample sizes or minimum detectable effect sizes (MDES).

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `test_type` | Str | Yes | e.g. 't-test' |
| `effect_size` | Float | Yes | Target effect size |

## Execution Protocol
1. Calculate sample size using standard formulas at power=0.80, alpha=0.05.
2. Graph MDES curve across sample ranges.

## Diagnostics & Interpretation Guide (What to Look For)
- **Required Sample Size exceeds available N**:
  - *Interpret*: The study is underpowered. High risk of Type II errors (false negatives).
  - *Action*: Warn researcher. Report MDES that can be detected with current sample size.

## Writing & Reporting Standards
> "A prospective power analysis indicated that a sample size of $N = 128$ per group is required to detect an effect size of Cohen's $d = 0.50$ with 80% power at alpha = .05."

## Reference Python Implementation
```python
from statsmodels.stats.power import TTestIndPower

def get_n(d):
    return TTestIndPower().solve_power(effect_size=d, alpha=0.05, power=0.80)
```

## Validation Criteria
- [ ] Output sample size is a positive integer.