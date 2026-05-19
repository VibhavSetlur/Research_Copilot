# Core Guardrails — Universal Compliance Layer (V2 Canonical)

> **Injected into every agent execution context. All rules are non-negotiable and apply across every research domain.**

These guardrails are **canonical** for the skills-first architecture and live at:
- `.research/agents/00_core_guardrails.md`

---

## V2 Protocols (Skills-First)

### 1) Skill Composition Protocol

- Every `.research/agents/*.md` file MUST begin with YAML frontmatter specifying:
  - `agent_id` (str), `version` (str)
  - `composes` (list of `skill_id`)
  - `produces` (list of project-relative output paths)
  - Optional: `depends_on` (list), `domain_compatibility` (list)
- Every `.research/skills/**/*.md` file MUST begin with YAML frontmatter specifying:
  - `skill_id` (str), `version` (str), `category` (str)
  - `required_tools` (list), `depends_on` (list), `produces` (list)

If required frontmatter is missing, halt and log **ERROR**.

### 2) Provider Adaptability Layer

- All generated code must be Python 3.10+ compatible.
- Prefer dependencies installable via `pip` without system-level packages.
- If a system dependency is unavoidable, explicitly document it and provide a fallback.

### 3) Data Lineage Requirements

Every file produced by a skill must begin with a YAML frontmatter *comment* containing:
- `producing_skill`
- `producing_agent`
- `timestamp_utc`
- `inputs_sha256` (mapping from input path → sha256)
- `orchestrator_version`

Example for Markdown/JSON:

```yaml
---
producing_skill: "detect_missingness"
producing_agent: "research_init"
timestamp_utc: "2026-05-19T00:00:00Z"
inputs_sha256:
  data_raw/mydata.csv: "..."
orchestrator_version: "1.0.0"
---
```

Example for Python:

```python
# ---
# producing_skill: "validate_schema"
# producing_agent: "data_scaffold"
# timestamp_utc: "2026-05-19T00:00:00Z"
# inputs_sha256:
#   data_raw/mydata.csv: "..."
# orchestrator_version: "1.0.0"
# ---
```

### 4) Recursive Depth Limits (Literature)

- Recursion depth defaults to `literature_recursion_depth` in `.research/config.yaml` (default: 3).
- Do not exceed the configured depth unless explicitly overridden.

---

## Code Standards

- All Python scripts set `numpy.random.seed(42)` and `random.seed(42)` at the top of the file, before any imports that consume randomness.
- Every function must have a complete NumPy-style docstring: `Parameters`, `Returns`, `Raises`, and `Notes`. The `Notes` section must contain the statistical or methodological theory justifying the function's design.
- Explicit type hints on all function signatures: `def compute_vif(design_matrix: pd.DataFrame) -> pd.Series`.
- Comments document *why*, never *what*. The code communicates what. The comment communicates scientific reasoning.
  - Non-compliant: `# Drop null rows`
  - Compliant: `# Listwise deletion applied under MCAR assumption. MAR or MNAR mechanisms require IterativeImputer (MICE) to prevent systematic bias in coefficient estimates (Rubin, 1987).`
- Import discipline: all stdlib, then third-party, then local — separated by blank lines.

---

## Documentation Standards

- Zero colloquial language in any generated markdown or log file. Prohibited: "Now we'll", "Let's look at", "Feel free to", "As mentioned", "It's worth noting", "You can see", "simply", "just", "interesting", "clearly".
- All numerical outputs formatted to consistent decimal precision: 4 decimal places for test statistics and p-values, 2 for descriptive statistics, exact for counts.
- Every p-value reported with its test statistic, degrees of freedom, and test name: `F(2, 147) = 8.3201, p = .0004`. Never `p < .05` alone.
- Effect sizes are mandatory alongside every significant result: Cohen's d, η²_p, ω², Cramér's V, or equivalent, depending on design.
- Confidence intervals must accompany every point estimate: `β̂ = 1.42, 95% CI [0.91, 1.93]`.

---

## Data Provenance

- `data_raw/` is immutable. No agent may write to or modify files in `data_raw/`.
- No script may read from `data_raw/` except controlled ingestion/validation scripts under `analysis/` (e.g., `analysis/01_validation.py`).
- Every dataset written to disk: compute SHA-256 hash and append to `reports/data_dictionary.md` with ISO 8601 timestamp and producing script name.

---

## Failure Handling

- Any unhandled exception must be caught at the top level, logged to `reports/logs/methods_log.md` with full traceback and ISO 8601 timestamp, and re-raised. Silent failures are not permitted.
- If a required input file is missing or malformed, halt immediately and write an error block to `reports/logs/methods_log.md` before exiting.

---

## Methods Log Protocol (Append-Only)

Every decision, pivot, transformation, or failure appends a structured block to `reports/logs/methods_log.md`:

```
---
Timestamp: {ISO 8601}
Agent: {agent filename}
Research Question: {RQ number and text, or "N/A"}
Phase: assumption_check | primary_test | pivot | transformation | error
Test Conducted: {test name or operation}
Statistic: {value, df, p-value or "N/A"}
Effect Size: {metric name = value, e.g., Cohen's d = 0.65}
Decision: PASS | FAIL | PIVOT | ERROR
If PIVOT:
  Failed assumption: {assumption name}
  Failure statistic: {test name, statistic value, df, p}
  Alternative selected: {method name and package==version}
  Rationale: {1–2 sentences citing statistical theory with author and year}
  Causal validity maintained: YES | NO | N/A
If ERROR:
  Traceback: {full traceback}
---
```

---

## Figure Standards

All figures must meet or exceed the publication standards of *Nature*, *Science*, *JAMA*, *PNAS*, *Cell*, and APA-style journals.

### 1) Typography & Styling (Static Matplotlib/Seaborn)

Initialize matplotlib using publication rcParams at the top of every script generating figures:

```python
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams.update({
    "figure.dpi": 300,
    "figure.figsize": (8, 5),
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "legend.framealpha": 0.6,
    "legend.edgecolor": "0.8",
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "grid.alpha": 0.15,
    "grid.linestyle": "--",
    "grid.linewidth": 0.5,
    "patch.linewidth": 0.5,
    "lines.linewidth": 1.5,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.05,
})
```

- Color palettes: use colorblind-safe, muted palettes. Primary sequence: `[#2E6EA6, #E07B39, #3D9A6E, #9B59B6, #C0392B]`.

### 2) Domain-Specific Figure Types

Select the appropriate figure type based on analysis goal. The wrong figure type is a methodological violation.

| Analysis Goal | Required Figure(s) |
|---|---|
| Linear regression | Scatter + OLS line + 95% CI band + residual vs. fitted panel |
| Multiple regression | Coefficient forest plot with CI bars, partial regression plots |
| Binary outcome (logistic) | ROC curve + calibration plot + predicted probability histogram |
| Group mean comparison (2+ groups) | Grouped box/violin + individual data points jittered |
| Longitudinal / time-series | Line plot with confidence bands; ACF/PACF panels |
| Survival / event-time | Kaplan-Meier curves with at-risk table |
| Factor / scale structure | Eigenvalue scree plot + factor loading heatmap |
| Spatial / geographic | Choropleth or point map with Moran's I annotation |
| Network / graph | Force-directed layout colored by community + centrality histogram |
| Text / NLP | Topic word cloud + topic proportion bar + coherence curve |
| Causal inference | Love plot (SMD balance) + propensity score histogram overlap |
| Bayesian | Posterior density plots + trace plots + credible interval comparison |
| High-dimensional | UMAP/t-SNE embedding + variable importance bar chart |

### 3) On-Image Interpretive & Statistical Annotations

Figures must embed interpretation directly on the canvas so any reader understands without consulting a caption.

### 4) Required Diagnostic Sub-Panels (by Test Family)

| Primary Test | Panel A | Panel B | Panel C (if applicable) |
|---|---|---|---|
| OLS Regression | Scatter + fitted line | Residual vs. Fitted | Normal Q-Q of residuals |
| Logistic Regression | ROC curve | Calibration plot | — |
| ANOVA / t-test | Box/violin plot | Residual Q-Q | Levene's test bar |
| Time-series | Observed + fitted | ACF of residuals | Forecast horizon plot |
| Survival | Kaplan-Meier curve | Cumulative hazard | Log-log plot (PH check) |
| SEM / Factor | Path diagram or loading heatmap | Fit index table | Residual correlation matrix |
| Spatial | Choropleth map | Moran scatterplot | — |

### 5) File Formats & Naming Convention

- `reports/figures/{rq_slug}_{figure_type}.pdf` — vector for journal submission
- `reports/figures/{rq_slug}_{figure_type}.png` — 300 DPI raster for markdown/reports
- `reports/figures/{rq_slug}_{figure_type}.html` — self-contained interactive
- `reports/figures/{rq_slug}_{figure_type}_caption.txt` — companion caption

---

## Table Standards

Tables must be presentation-ready for journal submission without further editing.

| Table Type | Required Columns |
|---|---|
| OLS Regression | Predictor, β̂, SE, 95% CI [LL, UL], t, p, β* |
| Logistic Regression | Predictor, β̂, OR, SE, 95% CI [LL, UL], z, p |
| ANOVA | Source, SS, df, MS, F, p, η²_p |
| Descriptive Statistics | Variable, N, M (SD), Median [IQR], Min–Max, Skewness, Kurtosis |
| Correlation Matrix | Variable pairs, r (or ρ), p, N |
| Survival | Group, N Events, Median Survival (95% CI), Log-rank χ², p |
| Factor Loadings | Item, F1, F2, ..., Communality (h²), Uniqueness |

- Significance flagged in footnotes only: `*p < .05, **p < .01, ***p < .001`.
- All tables saved as `{rq_slug}_table.md` and `{rq_slug}_table.tex` (booktabs style).
- Sample characteristics table always required as a standalone `Table 1`.
