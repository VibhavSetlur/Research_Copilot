---
skill_id: "spatial_analysis"
version: "5.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "libpysal", "spreg", "esda"]
estimated_tokens: 3000
depends_on: ["descriptive_stats", "profile_spatial"]
produces: ["analysis/03_analytical/spatial_results.json"]
---

# Skill: Spatial Autocorrelation & Regression

## Purpose
Formulate spatial weights, run Moran's I autocorrelation, and fit Spatial Autoregressive models.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_path` | Path | Yes | Path to spatial dataset |
| `value_col` | Str | Yes | Value column name |
| `independent` | List | Yes | Predictors |

## Methodological Framework
- **Spatial Lag Model (SAR)**:
  $$Y = \rho W Y + X\beta + \epsilon$$
  where $W$ is the spatial weight matrix and $\rho$ is the spatial autoregressive coefficient.

## Step-by-Step Analytical Protocol
1. Construct Queen adjacency spatial weights matrix. Row-standardize.
2. Run Moran's I test.
3. Fit Spatial Lag (SAR) or Spatial Error (SEM) models.

## Diagnostics & Interpretation Guide (What to Look For)
- **Moran's I pseudo p < .05**:
  - *Interpret*: Significant spatial clustering is present. Standard OLS would violate independence assumptions.
  - *Action*: Proceed with Spatial Lag or Spatial Error modeling.

## Writing & Reporting Standards
> "Significant spatial autocorrelation was detected in $Y$ (Moran's $I = .42, p < .001$), prompting a Spatial Lag model. The spatial autoregressive coefficient was significant ($\rho = .31, p < .001$)."

## Reference Python Implementation
```python
import libpysal
from esda.moran import Moran
from spreg import ML_Lag

def run_spatial(gdf, val_col, indeps):
    w = libpysal.weights.Queen.from_dataframe(gdf)
    w.transform = 'R'
    moran = Moran(gdf[val_col], w)
    
    y = gdf[val_col].values.reshape(-1, 1)
    X = gdf[indeps].values
    model = ML_Lag(y, X, w=w)
    return moran.I, model.summary
```

## Validation Criteria
- [ ] Spatial weights matrix is row-standardized.