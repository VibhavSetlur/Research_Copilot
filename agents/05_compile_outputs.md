# Agent 05 — Compile Outputs

**Purpose:** Synthesize all analytical results, domain-specific outputs, and figures into a complete publication-ready research report and a spectacular, fully self-contained interactive research dashboard that serves as an end-to-end presentation of the entire study.

---

## Prerequisites

Load `agents/00_core_guardrails.md` into context before executing.

## Trigger Command

```
Load agents/00_core_guardrails.md. Execute agents/05_compile_outputs.md using data/03_analytical/, reports/figures/, docs/methods_log.md, and docs/papers_and_tools_cited.md as context.
```

---

## Input Spec

| Input | Location | Required |
|-------|----------|----------|
| Analytical outputs | `data/03_analytical/` | Yes |
| Effect size estimates | `data/03_analytical/*_effectsizes.json` | Yes |
| Figures (.png, .html) | `reports/figures/` | Yes |
| Figure captions | `reports/figures/*_caption.txt` | Yes |
| Methods log | `docs/methods_log.md` | Yes |
| Data dictionary | `docs/data_dictionary.md` | Yes |
| Tools and literature | `docs/papers_and_tools_cited.md` | Yes |

**Halt condition:** Any required input missing, or `data/03_analytical/` contains no result files → halt, log ERROR.

---

## Action Mechanics

### Part A — Formal Research Report (`reports/research_findings.md`)

Write an academic report in the register of a peer-reviewed journal article. Use IMRAD structure (Introduction, Methods, Results, Discussion). Zero colloquial language.

#### Required Sections

**Abstract** (structured, 250 words exactly):
- Background (1–2 sentences): Study context and gap in knowledge.
- Objective: One sentence.
- Methods (2–3 sentences): Design, data, estimator(s).
- Results (2–3 sentences): Primary findings with statistics and effect sizes.
- Conclusions (1–2 sentences): Practical and scientific implications.

**1. Introduction**
- Theoretical and empirical background (draw from `docs/papers_and_tools_cited.md` supporting literature).
- Explicit statement of the research gap.
- Study objectives and hypotheses (numbered).
- Brief overview of data and design.

**2. Data and Measures**
- Dataset provenance: source, collection method, time period, unit of analysis.
- Sample characteristics: reproduce Table 1 (descriptive statistics) from `docs/data_dictionary.md`.
- Measurement properties: reliability coefficients (Cronbach's α, McDonald's ω) and validity evidence where applicable.
- Data quality and missingness: summary from epistemic baseline, imputation strategies applied.

**3. Analytical Strategy**
- Primary planned estimator(s) — from `docs/papers_and_tools_cited.md`, citing key references.
- Assumption-testing protocol and significance thresholds used.
- Pivots taken — formatted as academic narrative: *"Levene's test indicated heteroscedasticity [F(1, 148) = 12.44, p = .0006]; accordingly, Welch's ANOVA was applied in lieu of the standard F-test."*
- Multiple testing correction approach if applicable.
- Software citation: all packages cited in APA 7th software format.

**4. Results**
For each research question:
- One paragraph of academic prose reporting the primary finding, referencing the table and figure inline (e.g., "Table 2"; "Figure 3A").
- Full APA-style statistical reporting: `F(2, 147) = 8.32, p = .0004, η²_p = .102, 95% CI [.023, .192]`.
- FDR-adjusted p-value reported alongside uncorrected value if multiple comparisons applied.
- Effect size interpretation paragraph: translate the magnitude into practical terms.

**5. Discussion**
- Interpretation of each finding relative to the a priori hypothesis (supported / partially supported / not supported).
- Comparison with supporting literature — how do findings align with or diverge from cited comparable studies?
- Theoretical implications.
- Limitations: sample, measurement, design, threats to validity, generalizability.
- Future directions.

**6. References**
- All packages in APA 7th software citation format.
- All papers from `docs/papers_and_tools_cited.md`, sorted alphabetically.

---

### Part B — Publication-Grade Table Outputs (`reports/tables/`)

Generate domain-appropriate tables in both Markdown and LaTeX:

| Table | When Required | Guardrail Row |
|---|---|---|
| Table 1: Sample Characteristics | Always | Descriptive Statistics format |
| Table 2+: Results per RQ | Always | Per estimator family format |
| Factor Loadings Table | TABULAR-SURVEY EFA/CFA | Factor Loadings format |
| Correlation Matrix | Always if N predictors ≤ 15 | Correlation Matrix format |
| Survival Table | BIOMEDICAL survival | Survival format |

LaTeX requirements:
```latex
\begin{table}[h!]
\centering
\caption{{Descriptive title stating finding}}
\label{tab:{rq_slug}}
\begin{tabular}{lrrrrrr}
\toprule
...
\midrule
...
\bottomrule
\end{tabular}
\footnotesize\textit{Note.} *p < .05. **p < .01. ***p < .001. CI = confidence interval.
\end{table}
```

---

### Part C — Interactive Publication Dashboard (`reports/dashboards/analysis_app.py`)

Write a fully complete, self-contained `marimo` notebook (preferred) or `panel` application. This is an **Interactive Research Paper** — a complete presentation of the entire study designed for any audience from domain experts to intelligent laypeople, with no knowledge of the underlying data required.

The dashboard must be visually spectacular: clean, dark-mode-capable, publication-grade typography, and no ornamentation without information content.

#### Tab 1 — Study Overview (The "Why & What")

Design as a landing page for the research paper:

- **Hero Header:** Study title, institution (if applicable), date, and DOI (if available). Clean sans-serif typography.
- **Abstract Panel:** Structured abstract displayed with clearly labeled sections (Background, Objective, Methods, Results, Conclusions) in a clean card layout.
- **Hypotheses Board:** Numbered list of all RQs. Each RQ has a color-coded status badge: `SUPPORTED` (teal), `PARTIALLY SUPPORTED` (amber), `NOT SUPPORTED` (slate-gray), `INCONCLUSIVE` (orange). Badge color driven by the data in `data/03_analytical/`.
- **Key Findings Carousel:** 3 high-impact statistical findings stated in plain English: *"Participants receiving the intervention showed 24% higher recovery rates (HR = 0.76, p = .002)."*
- **Study Metadata Card:** Dataset source, N (total and per group), time period, design type, domain.

#### Tab 2 — Data Explorer (The "Dataset")

- **Global Cohort Filters:** Dropdowns and range sliders for all group/stratum variables. All panels on this tab update dynamically.
- **KPI Metrics Row:** Large styled metric cards showing: active N, mean of primary outcome (M ± SD), missingness rate of outcome variable. Update on filter.
- **Variable Selector Scatter:** Dropdowns to select any X and Y variable. Renders interactive Plotly scatter with Pearson's r and Spearman's ρ computed on the fly. Annotate correlation coefficient on plot.
- **Distribution Panels:** Histograms + KDE for every variable in the data dictionary. Toggle between pre-transformation and post-transformation distributions.
- **Correlation Heatmap:** Interactive Plotly heatmap of the full correlation matrix. Cells show r value; hover shows exact r, p-value, N. Cells with |r| < .1 de-emphasized.
- **Data Table:** Full paginated, searchable, sortable display of the analytical dataset.

#### Tab 3 — Methodology (The "How")

- **Pipeline Flowchart:** A Mermaid diagram (rendered in Marimo or as an SVG) showing the complete analytical pipeline: Raw Data → Schema Validation → Imputation Strategy → Transformations → Assumption Checks → Primary/Pivot Estimator → Results.
- **Assumption Audit Table:** Interactive, searchable table derived from `docs/methods_log.md`. Columns: RQ, Assumption Tested, Test Statistic, df, p-value, Decision (PASS/FAIL), Pivot Taken (Y/N). Color-coded rows (green/red).
- **Pivot Decision Panels:** For every PIVOT in the methods log, render a dedicated panel showing: the failed test statistic, the mathematical reason the original estimator was invalid, the chosen alternative and its statistical properties, the peer-reviewed citation justifying the choice.
- **Software & Reproducibility Registry:** Table of all packages (name, version, license, role). Button to download `environment/requirements.txt`.

#### Tab 4 — Results & Interpretations (The "So What")

For each Research Question, display a complete, self-contained analysis panel:

**Sub-Tab per RQ (collapsible panels or navigable):**

- **RQ Statement:** Full hypothesis stated clearly.
- **Visual Panel (Panel A):** The primary Plotly interactive figure (scatter, KM curve, choropleth, etc.) with synchronized filter controls. Custom hover templates per guardrail standards.
- **Diagnostic Panel (Panel B):** The corresponding assumption-check figure (residual plot, Q-Q, survival log-log, etc.).
- **Results Table:** Publication-grade HTML table with β̂, SE, CI, t/z/F/χ², p, p_FDR, and effect size columns.
- **Statistical Interpretation Card:** Precise academic interpretation of results.
- **Plain-English Summary Card:** A clean, bold summary in non-technical language: *"The treatment group recovered 1.8× faster than the control group — an effect large enough to be clinically meaningful."*
- **Effect Size Context Card:** Benchmarks the effect size against domain standards (e.g., Cohen's d = 0.50 is a medium effect in psychological research; 0.65 indicates the treated group outperformed 74% of the control group).

#### Tab 5 — Literature & Citations (The "Context")

- **Supporting Studies Table:** Interactive table of all supporting literature from `docs/papers_and_tools_cited.md`. Columns: Authors, Year, Title, Journal, Key Method, Relevant Finding, DOI (hyperlinked). Sortable by year, journal, or method.
- **Method Provenance Panel:** For each estimator used, display: the foundational paper, the year the method was established, and why this study's use is methodologically appropriate.
- **Full APA 7th Reference List:** Complete formatted bibliography. Copy-to-clipboard button for each reference.

#### Styling & Execution Standards

- **Color System:** Custom token-based CSS. Light mode: background `#F8F9FA`, surface `#FFFFFF`, primary accent `#2E6EA6`, secondary `#E07B39`. Dark mode: background `#1A1A2E`, surface `#16213E`, primary `#4FC3F7`, secondary `#FFB74D`.
- **Typography:** `Inter` or `Source Sans Pro` from Google Fonts for UI; `Times New Roman` fallback for all statistical annotations and tables (matching static figures).
- **Hover Templates:** Every Plotly trace has a custom HTML hover template. No default dictionary dumps.
- **Responsive Layout:** The app must render correctly at 1280px, 1440px, and 1920px widths without overflow.
- **Self-Contained Executable:** Runnable with:
  ```bash
  marimo run reports/dashboards/analysis_app.py
  # or
  panel serve reports/dashboards/analysis_app.py --show
  ```
  All data file paths must use `pathlib.Path(__file__).parent.parent` to resolve relative to project root.
- **Download Buttons:** Every tab must have a "Download as PDF" or "Export Data (CSV)" button where relevant.

---

## Output Spec

| Output | Location |
|--------|----------|
| Research report | `reports/research_findings.md` |
| LaTeX tables | `reports/tables/{rq_slug}_table.tex` |
| Markdown tables | `reports/tables/{rq_slug}_table.md` |
| Sample characteristics (Table 1) | `reports/tables/table1_sample_characteristics.{md,tex}` |
| Interactive dashboard | `reports/dashboards/analysis_app.py` |
