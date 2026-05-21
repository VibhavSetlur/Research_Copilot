---
skill_id: "meta_analysis"
version: "1.0.0"
category: "analysis"
depends_on: ["literature_deep", "extract_claims"]
produces: ["03_synthesis/meta_analysis_results.json", "03_synthesis/outputs/figures/forest_plot.png", "03_synthesis/outputs/figures/funnel_plot.png"]
complexity: "intensive"
---

# Skill: Meta-Analysis

## Purpose
Pool effect sizes across studies from the evidence matrix. Compute weighted mean effects, test heterogeneity, generate forest and funnel plots.

---

## Protocol

### Step 1: Extract Effect Sizes
Read `reports/literature/evidence_matrix.json`. For each study, extract:
- Effect size (Cohen's d, log odds ratio, correlation r, or Hedges' g)
- Standard error of effect size
- Sample size (total, treatment, control)
- Study identifier

Convert all effects to a common metric if needed:
- r → Fisher's z: `z = 0.5 * ln((1+r)/(1-r))`, SE = `1/sqrt(N-3)`
- OR → log OR: `log(OR)`, SE computed from 2×2 cell counts
- t-statistic → d: `d = 2t/sqrt(df)`

### Step 2: Fixed-Effect Model (Inverse-Variance Weighting)
Compute weighted mean: `μ = Σ(w_i × θ_i) / Σ(w_i)` where `w_i = 1/SE_i²`
SE of pooled effect: `SE_μ = 1/sqrt(Σw_i)`
95% CI: `μ ± 1.96 × SE_μ`

### Step 3: Heterogeneity Test
Cochran's Q: `Q = Σ(w_i × (θ_i - μ)²)` with df = k-1, p-value from χ²(df)
I² statistic: `I² = max(0, (Q - df)/Q) × 100%`
Interpretation: I² < 25% = low, 25-75% = moderate, > 75% = high heterogeneity

### Step 4: Random-Effects Model (if I² > 50%)
DerSimonian-Laird estimator:
1. Compute between-study variance: `τ² = (Q - df) / (Σw_i - Σw_i²/Σw_i)`
2. Adjust weights: `w_i* = 1/(SE_i² + τ²)`
3. Pooled effect: `μ_RE = Σ(w_i* × θ_i) / Σ(w_i*)`
4. SE and CI as in Step 2 but with adjusted weights

### Step 5: Forest Plot
Generate `forest_plot.png`:
- Each study as a square (size ∝ weight) with horizontal CI line
- Pooled estimate as diamond at bottom
- Vertical line at null effect
- Labels: study name, effect size, 95% CI, weight %
- Subtitle: model type, Q, I², τ²

### Step 6: Funnel Plot (Publication Bias)
Generate `funnel_plot.png`:
- X-axis: effect size, Y-axis: standard error (inverted)
- Pseudo 95% confidence bounds (funnel shape)
- Egger's regression test: `regress(effect/SE on 1/SE)`, intercept ≠ 0 → asymmetry
- Trim-and-fill: estimate missing studies, adjust pooled effect

### Step 7: Output
Save to `03_synthesis/meta_analysis_results.json`:
- Per-study effect sizes and weights
- Fixed-effect pooled estimate with CI
- Heterogeneity: Q, df, p-value, I², τ²
- Random-effects pooled estimate (if applicable)
- Funnel plot asymmetry test results
- Model selection rationale

---

## Validation
- [ ] Effect sizes extracted from evidence matrix
- [ ] All effects converted to common metric
- [ ] Fixed-effect model computed with inverse-variance weights
- [ ] Heterogeneity: Q, I², τ² reported
- [ ] Random-effects model used if I² > 50%
- [ ] Forest plot generated with study labels and pooled diamond
- [ ] Funnel plot generated with Egger's test
- [ ] Results saved to JSON
