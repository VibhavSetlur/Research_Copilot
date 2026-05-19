---
skill_id: "clustering"
version: "5.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "scikit-learn"]
estimated_tokens: 2500
depends_on: ["descriptive_stats"]
produces: ["analysis/03_analytical/clustering_results.json"]
---

# Skill: Clustering Analysis

## Purpose
Segment data using K-Means and evaluate cluster coherence.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_path` | Path | Yes | Dataset path |
| `features` | List | Yes | Features list |

## Execution Protocol
1. Standardize numerical features.
2. Run K-Means iterating K (2 to 6). Calculate Silhouette scores.
3. Choose K maximizing Silhouette score.

## Diagnostics & Interpretation Guide (What to Look For)
- **Silhouette Coefficient < 0.20**:
  - *Interpret*: Weak cluster separation; observations overlap significantly.
  - *Action*: Re-evaluate feature selections, drop noisy features, or try GMM.

## Writing & Reporting Standards
> "Observations were clustered using K-Means. The optimal partition ($K = 3$) was determined by maximizing the Silhouette score ($s = .43$)."

## Reference Python Implementation
```python
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

def run_kmeans(df, features):
    X = StandardScaler().fit_transform(df[features])
    km = KMeans(n_clusters=3)
    labels = km.fit_predict(X)
    return silhouette_score(X, labels)
```

## Validation Criteria
- [ ] Silhouette score is reported.