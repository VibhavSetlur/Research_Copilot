---
skill_id: "spatial_analysis"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["ecology", "epidemiology", "geography"]
required_tools: ["python", "geopandas", "libpysal", "mapclassify"]
depends_on: ["profile_spatial", "descriptive_stats"]
produces: ["analysis/03_analytical/spatial_results.json"]
complexity: "advanced"
---

# Skill: Spatial Statistical Analysis

## Purpose
Model spatial dependence and heterogeneity using spatial regression, kriging, and spatial cluster detection.

## When to Use
- Spatial autocorrelation detected (Moran's I significant)
- Location matters for the research question
- Need to account for spatial dependence in regression

## When NOT to Use
- No spatial autocorrelation (standard regression is fine)
- Spatial resolution too coarse
- Only descriptive mapping needed

## Decision Protocol

### Method Selection
| Question | Method |
|----------|--------|
| Spatial pattern of point events | Kernel density, K-function |
| Spatial interpolation | Kriging (ordinary, universal) |
| Spatial cluster detection | Getis-Ord Gi*, SaTScan |
| Regression with spatial dependence | Spatial lag (SAR) or spatial error (SEM) |
| Spatially varying relationships | Geographically Weighted Regression (GWR) |
| Areal data with neighbors | CAR/BYM models |

## Execution Protocol

### Step 1: Spatial Weights Matrix
- Define neighbor structure: k-nearest neighbors, distance band, queen/rook contiguity
- Row-standardize weights (each row sums to 1)
- Check: no islands (observations with no neighbors)
- If islands: increase k or distance threshold

### Step 2: Spatial Regression Model Selection
- Run OLS first as baseline
- Lagrange Multiplier tests:
  - LM-lag significant → spatial lag model (SAR)
  - LM-error significant → spatial error model (SEM)
  - Both significant → compare robust LM tests
- SAR: y = ρWy + Xβ + ε (spillover effects)
- SEM: y = Xβ + u, u = λWu + ε (spatially correlated errors)

### Step 3: Model Fitting
- SAR: maximum likelihood or 2SLS
- SEM: maximum likelihood
- Report: spatial autoregressive coefficient (ρ or λ), SE, p-value
- Compare to OLS: AIC, log-likelihood, R²

### Step 4: Spatial Interpolation (Kriging)
- Compute empirical variogram: semivariance vs distance
- Fit variogram model: spherical, exponential, Gaussian
- Check: nugget, sill, range parameters
- Cross-validate: leave-one-out prediction error

### Step 5: Hot Spot Detection
- Getis-Ord Gi*: identifies clusters of high/low values
- Significance: z-score and p-value with multiple testing correction
- Output: hot spots (high-high), cold spots (low-low), not significant

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| Moran's I on residuals | Not significant | Spatial dependence remains | Try alternative spatial model |
| Variogram fit | Good fit to empirical | Poor variogram model | Try different model form |
| Kriging cross-validation | RMSE acceptable | Poor predictions | Increase search radius |
| Spatial model vs OLS | Lower AIC | No spatial improvement | Use OLS |

### Red Flags
- **ρ or λ near 1.0**: spatial process near non-stationary; results sensitive to weights specification
- **Islands in weights matrix**: observations disconnected; results for islands unreliable
- **Variogram shows no sill**: spatial correlation extends beyond study area
- **GWR bandwidth too small**: overfitting; local estimates unstable

## Reporting Template
> "Spatial dependence was assessed using Moran's I (I = [value], p = [value]). A spatial [lag/error] model was fitted, with spatial autoregressive coefficient ρ = [value] (SE = [value], p = [value]). The spatial model improved fit over OLS (ΔAIC = [value], ΔR² = [value])."

## Output Specification
- `analysis/03_analytical/spatial_results.json`: spatial weights specification, model coefficients, spatial parameters, variogram parameters, hot spot results

## Validation Checks
- [ ] Spatial weights matrix has no islands
- [ ] Spatial parameter (ρ or λ) in (-1, 1)
- [ ] Variogram parameters are positive
- [ ] Hot spots corrected for multiple testing
