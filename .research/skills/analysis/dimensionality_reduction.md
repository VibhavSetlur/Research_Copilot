---
skill_id: "dimensionality_reduction"
version: "5.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "scikit-learn"]
estimated_tokens: 2500
depends_on: ["descriptive_stats"]
produces: ["analysis/03_analytical/dim_reduction_results.json"]
---

# Skill: Dimensionality Reduction

## Purpose
Project high-dimensional datasets into low-dimensional spaces while optimizing components.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_path` | Path | Yes | Path to dataset |
| `features` | List | Yes | Target features |

## Execution Protocol
1. Standardize features to mean=0, variance=1.
2. Fit PCA. Apply Kaiser Criterion (eigenvalues > 1.0) and Scree plot elbow detection to select components.

## Diagnostics & Interpretation Guide (What to Look For)
- **Low Cumulative Explained Variance (< 60% on first 2 components)**:
  - *Interpret*: Linear projections fail to capture most information.
  - *Action*: Switch to non-linear projections (t-SNE or UMAP) for visualization.

## Writing & Reporting Standards
> "PCA was run on standardized features. Using the Kaiser criterion (eigenvalues > 1.0), three components were retained, explaining 73.2% of total variance."

## Reference Python Implementation
```python
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def run_pca(df, features):
    X = StandardScaler().fit_transform(df[features])
    pca = PCA()
    pca.fit(X)
    return pca.explained_variance_ratio_
```

## Validation Criteria
- [ ] Input data is standardized before PCA.