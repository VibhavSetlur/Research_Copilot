# Agent 04 — Execute Analysis

**Purpose:** Write and execute all transformation and analysis scripts. Implement the iterative assumption-pivot engine. Generate all publication-quality figures, effect size estimates, and statistical outputs across any analytical domain.

---

## Prerequisites

Load `agents/00_core_guardrails.md` into context before executing.

## Trigger Command

```
Load agents/00_core_guardrails.md. Execute agents/04_execute_analysis.md for Phase {RQ number or "all"} using data/01_ingested/ and docs/data_dictionary.md as context.
```

The `Phase {X}` parameter allows partial execution. Invoke per research question for incremental review.

---

## Input Spec

| Input | Location | Required |
|-------|----------|----------|
| Ingested data | `data/01_ingested/` | Yes |
| Data dictionary | `docs/data_dictionary.md` | Yes |
| Methods and literature review | `docs/papers_and_tools_cited.md` | Yes |
| Methods log | `docs/methods_log.md` | Yes (append target) |

**Halt condition:** Any required input missing, or SHA-256 hash mismatch on ingested data → halt, log ERROR.

---

## Action Mechanics

### Part A — Advanced Transformation Pipeline (`scripts/02_transformation.py`)

1. **Load & hash-verify.** Load from `data/01_ingested/`. Recompute SHA-256 and verify against `docs/data_dictionary.md`. Mismatch → halt, log ERROR.

2. **Missingness imputation (select by mechanism):**
   - MCAR + rate < 5% → listwise deletion. Log: cite Rubin (1976).
   - MAR + rate 5–30% → `sklearn.impute.IterativeImputer` (MICE, 10 iterations, `max_iter=10`, `random_state=42`). Log all MICE parameters.
   - MNAR or rate > 30% → flag for researcher decision; apply pattern-mixture or selection model if researcher approves; halt otherwise.
   - For text: fill strategy `"[MISSING]"` sentinel token.

3. **Feature engineering by data type:**
   - **Tabular:** Log-transform right-skewed continuous variables (Shapiro-Wilk p < .05, skewness > 1). Standardize using `RobustScaler` if heavy outliers present, else `StandardScaler`. One-hot encode nominal variables (drop-first to prevent multicollinearity). Polynomial features (up to degree 2) only if theoretically justified in research brief.
   - **Text:** Tokenize + compute TF-IDF baseline. Generate sentence embeddings using `sentence-transformers` (model: `all-MiniLM-L6-v2`) and save to `data/02_processed/embeddings/`. Dimensionality reduction via UMAP if embeddings > 384 dims and N < 10,000.
   - **Spatial:** Project to appropriate CRS (EPSG:4326 for global; local UTM zone for sub-national). Compute spatial weights matrix (Queen contiguity or KNN, document choice). Scale continuous raster covariates.
   - **Network:** Compute graph-level features (density, avg clustering coeff, diameter if N_nodes < 50,000). Node-level features (degree, betweenness, eigenvector centrality). Store as augmented node-attribute DataFrame.
   - **Time-series:** Test stationarity (ADF + KPSS both required). Difference if non-stationary (up to d=2). Decompose (STL) if seasonality suspected. Document all transformations with lag orders and differencing decisions.
   - **Biomedical:** Log-normalize count data (e.g., library-size normalization for RNA-seq). Handle batch effects via `ComBat` or `harmonypy`. Filter low-count genes/features.

4. **Train/test split (predictive models only):** Apply before any feature scaling or embedding fitting. Stratified split (80/10/10 train/val/test) using the outcome variable. Fit all scaling/imputation transforms on training set only; apply to val and test.

5. **Write output.** Save to `data/02_processed/`. Record SHA-256 hash in `docs/data_dictionary.md`.

---

### Part B — Rigorous Analytical Pipeline (`scripts/03_modeling.py`)

For each research question:

#### 1. Load & verify
Load hash-verified data from `data/02_processed/`. Verify hash.

#### 2. Run all required assumption & diagnostic checks

Select checks based on the planned estimator:

| Estimator Family | Required Checks |
|---|---|
| OLS Regression | Normality of residuals (D'Agostino-Pearson, Shapiro-Wilk if N<50), Homoscedasticity (Breusch-Pagan + White's test), Independence (Durbin-Watson), Multicollinearity (VIF, threshold 5), Linearity (partial regression plots), Influential observations (Cook's D > 4/N) |
| ANOVA / t-test | Normality per group (Shapiro-Wilk), Homogeneity of variance (Levene's), Independence of observations, Sample size adequacy |
| Logistic Regression | Complete separation check, Hosmer-Lemeshow goodness-of-fit, Cook's D leverage, VIF |
| Mixed Effects / Panel | Nested residual normality, Random effects distribution check, Intraclass Correlation (ICC), Likelihood ratio test (FE vs. RE) |
| Time-Series | ADF + KPSS stationarity, Ljung-Box portmanteau test on residuals (Q-test), ARCH effects test |
| Survival | Proportional hazards assumption (Schoenfeld residuals), Log-log plot |
| SEM / Factor | χ², CFI ≥ .95, RMSEA ≤ .06, SRMR ≤ .08, modification indices |
| Spatial Regression | Moran's I on OLS residuals (spatial autocorrelation check), LM diagnostics (lag vs. error) |
| Causal (matching) | Covariate balance (SMD < .1 post-matching), Propensity score overlap (common support) |
| Causal (IV) | First-stage F-statistic > 10 (weak instrument test), Sargan-Hansen overidentification (if overidentified) |
| Bayesian | R-hat ≤ 1.01 (chain convergence), ESS > 400 (effective sample size), Posterior predictive check |

Log EVERY check result (pass or fail) to `docs/methods_log.md` with the structured format.

#### 3. Assumption-pivot logic

```
If ALL assumptions pass:
  → Execute primary estimator
  → Log: "Primary estimator executed. All diagnostics passed."

If ANY assumption fails:
  → Log failure to docs/methods_log.md with PIVOT block
  → Select the pre-specified robust alternative from docs/papers_and_tools_cited.md
  → Explicitly document which assumption failed, by how much, and why the chosen alternative corrects for it
  → Execute alternative
  → Log: "Robust alternative executed. See PIVOT block."
```

#### 4. Multiple testing correction

If > 3 hypotheses tested in the project:
- Compute Benjamini-Hochberg FDR-adjusted p-values via `statsmodels.stats.multitest.multipletests(method='fdr_bh')`.
- Report both uncorrected and FDR-adjusted p-values in all results files.
- Flag any RQ that crosses significance only at uncorrected level.

#### 5. Effect size computation (mandatory for all tests)

| Test | Effect Size Metric | Package |
|---|---|---|
| t-test | Cohen's d | `pingouin.compute_effsize` |
| ANOVA | η²_p and ω² | `pingouin.anova` |
| Logistic regression | Nagelkerke R², OR with 95% CI | `statsmodels` |
| OLS regression | R², adjusted R², Cohen's f² | `statsmodels` |
| Non-parametric | rank-biserial r | `pingouin.mwu` |
| Chi-square | Cramér's V | `scipy.stats.contingency.association` |
| SEM | RMSEA, CFI, TLI | `semopy` |
| Survival | Hazard Ratio + 95% CI | `lifelines` |

#### 6. Domain-specific additional outputs

- **TABULAR-SURVEY:** Cronbach's α, McDonald's ω, factor loadings table, factor score correlations.
- **TIME-SERIES:** Forecast with 80% and 95% prediction intervals. Residual ACF plot.
- **SPATIAL:** LISA cluster map (Moran scatterplot + choropleth). Local Moran's I significance map.
- **NETWORK:** Community membership table. Centrality distribution plots. Ego network analysis for top-N nodes.
- **TEXT-CORPUS:** Topic coherence scores. Topic-document matrix heatmap. Representative documents per topic.
- **BIOMEDICAL / SURVIVAL:** Kaplan-Meier curves with at-risk tables. Median survival with 95% CI. HR forest plot.

#### 7. Figure generation

Generate all figures per Section 2 of `agents/00_core_guardrails.md`:
- Select domain-specific figure type from the Figure Type Registry in guardrails.
- Generate Panel A (primary visual) and Panel B (diagnostic/assumption check) using `gridspec`.
- Generate Panel C if specified in the domain-specific row of the registry.
- Annotate all statistical results, equations, effect sizes, and plain-English interpretations directly on the canvas.
- Write three-part companion caption to `reports/figures/{rq_slug}_caption.txt`.
- Save `.pdf`, `.png` (300 DPI), and `.html` (Plotly interactive).

#### 8. Save results

```
data/03_analytical/{rq_slug}_results.json       ← raw numerical results
data/03_analytical/{rq_slug}_table.md           ← formatted markdown table
data/03_analytical/{rq_slug}_table.tex          ← formatted LaTeX table (booktabs)
data/03_analytical/{rq_slug}_effectsizes.json   ← all effect size estimates with CI
```

---

### Methods Log Entry Format (Append-Only)

```markdown
---
Timestamp: {ISO 8601}
Agent: 04_execute_analysis.md
Research Question: {RQ number and text}
Phase: assumption_check | primary_test | pivot | transformation | error
Test Conducted: {test name}
Statistic: {value, df, p-value}
Effect Size: {metric = value (95% CI [LL, UL])}
FDR-adjusted p: {value or "N/A — single hypothesis"}
Decision: PASS | FAIL | PIVOT | ERROR
If PIVOT:
  Failed assumption: {name}
  Failure statistic: {test, value, df, p}
  Alternative selected: {method + package==version}
  Rationale: {1–2 sentences citing statistical theory and literature (Author, Year)}
  Causal validity maintained: YES | NO | N/A
If ERROR:
  Traceback: {full traceback}
---
```

---

## Output Spec

| Output | Location |
|--------|----------|
| Transformation script | `scripts/02_transformation.py` |
| Modeling script | `scripts/03_modeling.py` |
| Processed data | `data/02_processed/` |
| Analytical results | `data/03_analytical/{rq_slug}_results.json` |
| Effect size estimates | `data/03_analytical/{rq_slug}_effectsizes.json` |
| Figures | `reports/figures/` (.pdf, .png, .html) |
| Figure captions | `reports/figures/{rq_slug}_caption.txt` |
| Methods log entries | `docs/methods_log.md` (appended) |
| Result tables | `data/03_analytical/{rq_slug}_table.{md,tex}` |
