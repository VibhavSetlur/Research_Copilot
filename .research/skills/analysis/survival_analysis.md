---
skill_id: "survival_analysis"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["epidemiology", "medicine", "engineering"]
required_tools: ["python", "lifelines", "scipy", "pandas"]
depends_on: ["descriptive_stats"]
produces: ["analysis/03_analytical/survival_results.json"]
complexity: "advanced"
---

# Skill: Survival (Time-to-Event) Analysis

## Purpose
Model time-to-event data with censoring, estimate survival functions, and assess covariate effects on hazard rates.

## When to Use
- Outcome is time until an event (death, failure, recovery, churn)
- Some observations are censored (event not yet observed)
- Want to compare survival between groups or model covariate effects

## When NOT to Use
- No time-to-event outcome
- No censoring (all events observed)
- Event is not well-defined or time is not meaningful

## Decision Protocol

### Method Selection
| Question | Method |
|----------|--------|
| Describe survival over time | Kaplan-Meier estimator |
| Compare survival between groups | Log-rank test |
| Model covariate effects on hazard | Cox proportional hazards |
| Model covariate effects on survival time | Accelerated Failure Time (AFT) |
| Time-varying covariates | Extended Cox model |
| Competing risks | Fine-Gray subdistribution hazard |
| Recurrent events | Andersen-Gill model |

## Execution Protocol

### Step 1: Data Structure
- Define: duration (time from entry to event or censoring), event indicator (1 = event, 0 = censored)
- Check: no negative durations, no events at time 0
- Identify: entry time (left-truncation), exit time, event type

### Step 2: Descriptive Survival
- Kaplan-Meier estimator: Ŝ(t) = Π(1 - dᵢ/nᵢ) for tᵢ ≤ t
- Median survival time: time at which Ŝ(t) = 0.50
- Survival probabilities at key timepoints (e.g., 1-year, 5-year)
- Number at risk table over time

### Step 3: Group Comparison
- Log-rank test: compares observed vs expected events across groups
- If significant: pairwise log-rank tests with Bonferroni correction
- Report: chi-square statistic, df, p-value
- Visual: Kaplan-Meier curves with confidence bands

### Step 4: Cox Proportional Hazards Model
- Model: h(t|X) = h₀(t) × exp(β'X)
- Estimate: partial likelihood maximization
- Report: hazard ratios (HR = exp(β)), 95% CI, p-values
- Interpret: HR > 1 = increased hazard, HR < 1 = decreased hazard

### Step 5: Proportional Hazards Assumption
- Schoenfeld residuals test: null = PH holds
- If p < 0.05: PH violated for that covariate
- Visual: log(-log(S(t))) plots should be parallel
- If violated: add time-interaction term or use stratified Cox model

### Step 6: Model Diagnostics
- Residuals: martingale, deviance, Schoenfeld
- Influential observations: dfbeta, dfbetas
- Functional form: martingale residuals vs continuous covariates
- Overall fit: concordance index (C-statistic)

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| PH assumption | Schoenfeld p > 0.05 | Time-varying effect | Add time interaction or stratify |
| Censoring rate | < 50% | Heavy censoring | Results uncertain; report with caution |
| Concordance | > 0.60 | Poor discrimination | Add predictors or use flexible model |
| Influential points | No extreme dfbeta | Single observation drives result | Report sensitivity analysis |

### Red Flags
- **All events at same time**: discrete-time survival model needed
- **Censoring > 80%**: insufficient events; results unreliable
- **HR CI includes 1.0 with wide range**: underpowered; report as inconclusive
- **Non-monotonic KM curve**: data error (event before entry time)

## Reporting Template
> "Survival was estimated using the Kaplan-Meier method. Median survival was [value] months (95% CI [lower, upper]). The log-rank test indicated a significant difference between groups (χ² = [value], p = [value]). In the Cox model, [covariate] was associated with [increased/decreased] hazard (HR = [value], 95% CI [lower, upper], p = [value]). The proportional hazards assumption was [satisfied/violated]."

## Output Specification
- `analysis/03_analytical/survival_results.json`: KM estimates, log-rank results, Cox model coefficients, HRs, PH test results, diagnostics

## Validation Checks
- [ ] No negative durations
- [ ] Event indicator is binary (0/1)
- [ ] KM curve is monotonically non-increasing
- [ ] PH assumption tested and reported
- [ ] Concordance index reported
