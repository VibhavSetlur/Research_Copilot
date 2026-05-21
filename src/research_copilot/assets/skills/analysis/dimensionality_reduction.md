---
skill_id: "dimensionality_reduction"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "scikit-learn", "scipy"]
depends_on: ["descriptive_stats"]
produces: ["analysis/03_analytical/dimred_results.json"]
complexity: "intermediate"
---

# Skill: Dimensionality Reduction

## Purpose
Reduce high-dimensional data to lower dimensions while preserving structure, for visualization, noise reduction, or feature engineering.

## When to Use
- Many correlated predictors (multicollinearity)
- Need to visualize high-dimensional data
- Feature engineering before modeling
- p >> n (more features than observations)

## When NOT to Use
- Few features (< 5)
- Interpretability of individual features is essential
- Features are already uncorrelated

## Decision Protocol

### Method Selection
| Goal | Method | Preserves |
|------|--------|-----------|
| Maximize variance explained | PCA | Global linear structure |
| Non-linear manifold | t-SNE | Local neighborhood structure |
| Non-linear + global | UMAP | Local + global structure |
| Supervised reduction | PLS | Covariance with outcome |
| Categorical data | MCA (Multiple Correspondence) | Chi-square distances |
| Mixed data types | FAMD | Both variance and association |

## Execution Protocol

### Step 1: Preprocessing
- Standardize all numeric features (mean=0, SD=1) — critical for PCA
- For count data: consider log(x+1) transform before PCA
- Handle missing values: impute before reduction (never drop)

### Step 2: PCA (default linear method)
- Compute: eigenvalues, eigenvectors of correlation matrix
- Variance explained per component: λᵢ / Σλ
- Cumulative variance explained
- Scree plot: eigenvalue vs component number

### Step 3: Component Selection
- Kaiser criterion: retain components with eigenvalue > 1
- Scree test: elbow point in scree plot
- Cumulative variance: retain enough for ≥ 70% total variance
- Parallel analysis: compare eigenvalues to random data (most rigorous)

### Step 4: Interpretation
- Component loadings: correlation between original features and components
- |loading| > 0.40: feature contributes meaningfully to component
- Name components based on highest-loading features
- Compute component scores for each observation

### Step 5: Non-Linear Methods (if PCA insufficient)
- t-SNE: perplexity = 30 (default), early exaggeration = 12
- UMAP: n_neighbors = 15, min_dist = 0.1
- Both require: standardization, careful parameter tuning
- Note: t-SNE and UMAP axes are not interpretable; use for visualization only

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| Cumulative variance | ≥ 70% in first k components | Information loss | Retain more components |
| Loadings | |loading| > 0.40 for some features | Component uninterpretable | Re-examine feature set |
| t-SNE/UMAP stability | Consistent across runs | Parameter sensitive | Try multiple perplexity/n_neighbors |
| Reconstruction error | Low | Poor representation | Use non-linear method |

### Red Flags
- **First component explains > 80%**: one dominant factor; check for data leakage
- **All loadings similar magnitude**: no clear structure; features may be noise
- **t-SNE shows clusters but PCA doesn't**: non-linear structure; trust t-SNE for viz, PCA for modeling
- **UMAP parameters change clusters dramatically**: structure is weak; report with caution

## Reporting Template
> "Principal component analysis was performed on [N] standardized variables. [K] components were retained based on [criterion], explaining [percentage]% of total variance. Component 1 ([percentage]% variance) was characterized by [features], Component 2 ([percentage]%) by [features]."

## Output Specification
- `analysis/03_analytical/dimred_results.json`: eigenvalues, variance explained, loadings, component scores, method parameters

## Validation Checks
- [ ] Features standardized before PCA
- [ ] Component selection criterion stated
- [ ] Loadings reported for interpretation
- [ ] Cumulative variance ≥ 70% (or justify lower)
