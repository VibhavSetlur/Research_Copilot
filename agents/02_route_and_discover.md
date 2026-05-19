# Agent 02 — Route and Discover

**Purpose:** Given the data type classification, causal design, and research questions from the epistemic baseline, identify the optimal analytical methods, Python packages, and supporting literature. Performs rule-based routing first, then live external discovery for gaps.

---

## Prerequisites

Load `agents/00_core_guardrails.md` into context before executing.

## Trigger Command

```
Load agents/00_core_guardrails.md. Execute agents/02_route_and_discover.md using docs_input/initial_epistemic_baseline.md as context. Perform live web searches for any gaps identified.
```

---

## Input Spec

| Input | Location | Required |
|-------|----------|----------|
| Epistemic baseline | `docs_input/initial_epistemic_baseline.md` | Yes |

**Halt condition:** `initial_epistemic_baseline.md` missing or contains no data type classification → halt, log ERROR.

---

## Action Mechanics

### Step 1 — Internal Registry Lookup

Consult the extended routing table. Select the **most statistically rigorous** available estimator matching the data type, causal design, and analysis goal. Document the selection rationale.

#### Tabular Cross-Sectional

| Analysis Goal | Primary Method | Package | Robust Alternative |
|---|---|---|---|
| Causal inference (observational, RCT) | Double Machine Learning | `EconML` (`econml.dml.LinearDML`) | `DoWhy` (Propensity Weighting) |
| Causal inference (IV) | Two-Stage Least Squares | `linearmodels.iv.IV2SLS` | `statsmodels.sandbox.regression.gmm` |
| Causal inference (RDD) | Regression Discontinuity | `rdd` or `EconML` | Local linear regression |
| Binary outcome (balanced) | Logistic Regression | `statsmodels.Logit` | `sklearn.linear_model.LogisticRegressionCV` |
| Binary outcome (imbalanced) | Penalized logistic + SMOTE | `imbalanced-learn` + `sklearn` | XGBoost with `scale_pos_weight` |
| Count outcome | Negative Binomial GLM | `statsmodels.NegativeBinomial` | Zero-inflated models (`pscl`-style via `statsmodels`) |
| Ordinal outcome | Proportional odds logistic | `statsmodels.MNLogit` or `mord` | `sklearn` gradient boosting |
| Continuous outcome (parametric) | OLS + robust SE | `statsmodels.OLS.fit(cov_type='HC3')` | Huber M-estimator (`statsmodels.RLM`) |
| Continuous outcome (nonlinear) | Gradient boosting | `lightgbm.LGBMRegressor` | `xgboost.XGBRegressor` |
| High-dimensional features | LASSO / Elastic Net | `sklearn.linear_model.ElasticNetCV` | `EconML` Post-LASSO |
| Mediation analysis | ACME / Baron-Kenny | `pyprocessmacro` or `causalpy` | `semopy` SEM path model |
| Moderation / Interaction | OLS with interaction terms | `statsmodels` + `patsy` formulas | PROCESS Macro style via `pyprocessmacro` |

#### Tabular Panel / Longitudinal

| Analysis Goal | Primary Method | Package | Robust Alternative |
|---|---|---|---|
| Fixed effects (entity) | Within estimator | `linearmodels.PanelOLS(entity_effects=True)` | `statsmodels.MixedLM` |
| Random effects | GLS-based RE estimator | `linearmodels.RandomEffects` | `statsmodels.MixedLM` |
| Difference-in-Differences | Two-way FE DiD | `linearmodels.PanelOLS` (twoway) | `EconML` DiD / `did` R (via `rpy2`) |
| Staggered DiD | Callaway-Sant'Anna | `csdid` (Python) or `EconML` | Sun-Abraham estimator |
| Hierarchical / Multilevel | Mixed-effects linear model | `pymer4.Lmer` | `statsmodels.MixedLM` |
| Growth curve modeling | Latent growth model | `semopy` SEM | `pymer4` random-slope models |
| Dynamic panel | Arellano-Bond GMM | `linearmodels.BetweenOLS` + GMM | `rpy2` + `plm` package |

#### Survey / Psychometrics

| Analysis Goal | Primary Method | Package | Robust Alternative |
|---|---|---|---|
| Internal consistency | Cronbach's α (+ ω) | `pingouin.cronbach_alpha` | `semopy` CFA-based reliability |
| Exploratory Factor Analysis | PAF with oblimin rotation | `factor_analyzer.FactorAnalyzer` | `sklearn` PCA |
| Confirmatory Factor Analysis | Maximum likelihood SEM | `semopy.Model` | `lavaan` via `rpy2` |
| Structural Equation Modeling | Full SEM | `semopy` | `semopy` ESEM / `rpy2` lavaan |
| Item Response Theory | 2PL / 3PL model | `girth` or `cirt` | `mirt` via `rpy2` |
| Network psychometrics | Gaussian graphical model | `qgraph` via `rpy2` or `pyGGM` | `EBICglasso` |

#### Text / NLP

| Analysis Goal | Primary Method | Package | Robust Alternative |
|---|---|---|---|
| Topic modeling | BERTopic (transformer) | `bertopic` | `gensim` LDA (coherence-optimized) |
| Sentiment analysis | Transformer fine-tuned | `transformers` (e.g., `cardiffnlp/twitter-roberta`) | `VADER` + `TextBlob` ensemble |
| Zero-shot classification | Zero-shot pipeline | `transformers.pipeline("zero-shot-classification")` | `sklearn` TF-IDF + SVM |
| Named entity recognition | SpaCy transformer pipeline | `spacy` (`en_core_web_trf`) | `flair` |
| Text regression | Embeddings + OLS/RF | `sentence-transformers` + `sklearn` | `transformers` fine-tuned regression |
| Document similarity | Cosine on SBERT embeddings | `sentence-transformers` | `gensim` Word2Vec |
| Content analysis (quantitative) | Dictionary method | `empath` or custom dict + `pandas` | LLM-assisted labeling |

#### Time-Series

| Analysis Goal | Primary Method | Package | Robust Alternative |
|---|---|---|---|
| Forecasting (univariate) | Auto-ARIMA / SARIMA | `pmdarima.auto_arima` | `prophet` (seasonal, irregular) |
| Forecasting (multivariate) | VAR / VARMAX | `statsmodels.VAR` | `sktime` ML forecasters |
| Forecasting (neural) | N-BEATS / Temporal Fusion | `neuralforecast` | `sktime` + `pytorch-forecasting` |
| Intervention / causal impact | Bayesian Structural Time Series | `tfcausalimpact` | `statsmodels` UCM/SARIMAX |
| Stationarity testing | ADF + KPSS (both required) | `statsmodels.adfuller` + `.kpss` | Phillips-Perron test |
| Granger causality | F-test | `statsmodels.grangercausalitytests` | VAR Granger |
| Anomaly detection | Isolation Forest | `sklearn.ensemble.IsolationForest` | `pyod` ABOD |
| Change point detection | PELT algorithm | `ruptures` | `changepy` |
| Spectral analysis | FFT + Periodogram | `scipy.signal.periodogram` | `PyWavelets` |

#### Spatial

| Analysis Goal | Primary Method | Package | Robust Alternative |
|---|---|---|---|
| Spatial autocorrelation | Global + Local Moran's I | `esda.Moran` + `esda.Moran_Local` | `scipy.spatial` KD-tree |
| Spatial regression (lag/error) | Maximum likelihood spatial | `spreg.ML_Lag` / `spreg.ML_Error` (PySAL) | GWR via `mgwr` |
| Geographically weighted regression | GWR | `mgwr.gwr.GWR` | Spatial random effects |
| Point pattern analysis | Ripley's K / KDE | `pointpats.k` + `scipy.stats.gaussian_kde` | `shapely` + `geopandas` |
| Raster analysis | Zonal statistics | `rasterio` + `rasterstats` | `xarray` + `rioxarray` |

#### Network / Graph

| Analysis Goal | Primary Method | Package | Robust Alternative |
|---|---|---|---|
| Centrality analysis | Betweenness, Eigenvector, PageRank | `networkx` | `igraph` (large-scale) |
| Community detection | Louvain (modularity) | `python-louvain` | Leiden algorithm (`leidenalg`) |
| Link prediction | Node2Vec embeddings | `node2vec` | `stellargraph` GraphSAGE |
| Network regression | QAP test | `scipy` + manual permutation | `netcomp` |
| Temporal networks | Snapshot analysis | `networkx` per time slice | `teneto` |

#### Biomedical / Omics

| Analysis Goal | Primary Method | Package | Robust Alternative |
|---|---|---|---|
| Differential expression | DESeq2-style NB model | `pydeseq2` | `edgeR` via `rpy2` |
| Single-cell RNA-seq | Leiden clustering + UMAP | `scanpy` | `seurat` via `rpy2` |
| Survival analysis | Cox proportional hazards | `lifelines.CoxPHFitter` | `scikit-survival` |
| Competing risks | Fine-Gray model | `scikit-survival` | `lifelines` |
| Genome-wide association | GWAS linear/logistic | `pandas-plink` + `statsmodels` | `plink2` (via subprocess) |
| Medical image analysis | Pre-trained CNN features | `torchvision` + `sklearn` | `monai` |

#### Bayesian Modeling (Any Domain)

| Analysis Goal | Primary Method | Package | Robust Alternative |
|---|---|---|---|
| Bayesian regression | MCMC / NUTS | `PyMC` | `numpyro` |
| Bayesian hierarchical | Partial pooling model | `PyMC` | `Bambi` (formula interface) |
| Bayesian inference + priors | Probabilistic programming | `numpyro` | `PyMC` |
| Approximate inference | Variational inference | `PyMC` ADVI | `numpyro` SVI |

### Step 2 — Gap Identification

Flag any RQ not covered by the internal registry with severity HIGH. Proceed to Step 3 for all flagged gaps.

### Step 3 — Live External Discovery (Flagged Gaps Only)

**Mandatory for gaps.** Perform live web searches across:
- Google Scholar, PubMed, arXiv, SSRN, Semantic Scholar
- PyPI, GitHub, conda-forge
- Domain-specific registries (Bioconductor, CRAN, HuggingFace Hub)

For each gap, identify:
1. The state-of-the-art method (post-2018, peer-reviewed, DOI required).
2. A Python implementation meeting ALL of: ≥1,000 GitHub stars or ≥10,000 monthly PyPI downloads; active maintenance (last commit <12 months); test suite present.
3. At least one comparable published study using this method on similar data.

Document findings in the External Discovery Log.

### Step 4 — Online Literature Enrichment (All RQs)

For every research question, search Google Scholar / Semantic Scholar for 3–5 highly-cited papers (>50 citations, preferably >200) that:
- Used the same or closely related method on similar data type and domain.
- Were published in a top-tier venue (Nature, Science, JAMA, PLOS ONE, etc.).

Extract: author(s), year, title, journal, DOI, key methods used, and how this informs the current analysis. Cite in `docs/papers_and_tools_cited.md`.

### Step 5 — Dependency Risk Assessment

For every selected package:

| Package | Version | License | Last Release | GitHub Stars | Open Issues | Transitive Dep Of |
|---------|---------|---------|--------------|--------------|-------------|-------------------|

---

## Output Spec

| Output | Location |
|--------|----------|
| Methods and literature review | `docs/papers_and_tools_cited.md` |

### `papers_and_tools_cited.md` Schema

```markdown
# Analytical Methods and Tools
Generated: {ISO 8601}
Agent: 02_route_and_discover.md

## Per Research Question

### RQ{N}: {Full question text}

**Causal Design:** {e.g., Observational OLS | DiD | RCT | IV}
**Method:** {Full method name}
**Package:** `{package}=={version}`
**Mathematical Basis:** {1–2 sentence description of the estimator, citing the foundational paper}
**Key Reference:** {Author, Year. Title. Journal. DOI: ...}
**Selection Rationale:** {Why this estimator is appropriate given the data, design, and assumptions}
**Failure Alternative:** {Package and method if primary assumptions fail}

**Supporting Literature:**
1. {Author, Year. Title. Journal. DOI. Key finding relevant to this analysis.}
2. {...}
3. {...}

## Dependency Manifest
| Package | Version | License | Last Release | GitHub Stars | Open Issues | Transitive Dep Of |
|---------|---------|---------|--------------|--------------|-------------|-------------------|

## External Discovery Log
| RQ | Gap | Sources Searched | Selected Package | DOI / URL | Rationale |
|----|-----|-----------------|-----------------|-----------|-----------|
```
