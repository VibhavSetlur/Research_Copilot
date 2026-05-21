---
skill_id: "clustering"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "scikit-learn", "scipy"]
depends_on: ["descriptive_stats", "dimensionality_reduction"]
produces: ["analysis/03_analytical/clustering_results.json"]
complexity: "intermediate"
---

# Skill: Clustering Analysis

## Purpose
Partition observations into meaningful groups using multiple clustering algorithms and validate cluster quality.

## When to Use
- Exploratory: discover natural groupings in data
- Segmentation: identify subpopulations for targeted analysis
- After dimensionality reduction (cluster in reduced space)

## When NOT to Use
- Known group labels exist (use classification, not clustering)
- Data has no structure (uniform distribution)
- Only 1-2 features (clustering unreliable in very low dimensions)

## Decision Protocol

### Method Selection
| Data Structure | Method | Strengths |
|---------------|--------|-----------|
| Spherical clusters, known k | K-Means | Fast, scalable |
| Unknown k, varying density | DBSCAN | Finds arbitrary shapes, detects noise |
| Probabilistic assignment | Gaussian Mixture Models | Soft clustering, model-based |
| Hierarchical structure | Agglomerative clustering | Dendrogram, flexible linkage |
| High-dimensional | Spectral clustering | Captures non-convex shapes |
| Categorical data | K-Modes | Handles categories directly |

## Execution Protocol

### Step 1: Feature Preparation
- Standardize numeric features (mean=0, SD=1)
- For mixed data: Gower distance or separate encoding
- Consider: cluster in PCA-reduced space if p > 10

### Step 2: K-Means (default)
- Iterate k = 2 to 10
- For each k: run 10 times with different initializations (avoid local optima)
- Select optimal k using:
  - Elbow method: inertia vs k plot
  - Silhouette score: mean silhouette across all points
  - Gap statistic: compare to null reference distribution

### Step 3: Alternative Methods
- DBSCAN: eps = distance at knee of k-distance plot, min_samples = 2×dimensionality
- GMM: select components by BIC, allow full covariance
- Agglomerative: try ward, complete, average linkage; compare cophenetic correlation

### Step 4: Cluster Validation
**Internal validation:**
- Silhouette score: > 0.50 = reasonable, > 0.70 = strong
- Calinski-Harabasz index: higher = better
- Davies-Bouldin index: lower = better

**Stability:**
- Bootstrap: resample data, re-cluster, compare assignments (Adjusted Rand Index)
- If ARI < 0.50: clusters are unstable; report with caution

### Step 5: Cluster Characterization
- Per cluster: mean/median of each feature
- Identify distinguishing features: ANOVA or Kruskal-Wallis per feature
- Profile each cluster with a descriptive name
- Compute cluster sizes and proportions

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| Silhouette | > 0.25 | Weak separation | Try different method or features |
| Stability (ARI) | > 0.50 | Unstable clusters | Increase sample or reduce features |
| Cluster size | No cluster < 5% | Tiny clusters | Increase k or change method |
| Feature discrimination | ≥ 2 features differ | Clusters not meaningful | Reconsider clustering goal |

### Red Flags
- **Silhouette < 0.10**: no real cluster structure; data may be uniform
- **One cluster contains > 80% of points**: default cluster; method not discriminating
- **Clusters differ on only 1 feature**: not multidimensional clustering; use simple split
- **DBSCAN labels all points as noise**: eps too small or no density structure

## Reporting Template
> "Clustering was performed using [method] on [N] observations across [P] standardized features. The optimal number of clusters (k = [value]) was selected by [criterion] (silhouette = [value]). Cluster 1 ([n] observations, [percentage]%) was characterized by [features]. Cluster profiles differed significantly on [features] (all p < .05)."

## Output Specification
- `analysis/03_analytical/clustering_results.json`: cluster assignments, validation metrics, cluster profiles, method parameters, stability results

## Validation Checks
- [ ] Optimal k justified by ≥ 2 criteria
- [ ] Silhouette score reported
- [ ] Cluster stability assessed
- [ ] Each cluster characterized by distinguishing features
