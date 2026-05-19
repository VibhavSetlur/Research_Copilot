# Agent 01 — Initialize

**Purpose:** Ingest raw data and the research brief to produce a structured epistemic baseline. This agent writes zero analysis code. It only reads, profiles, and documents.

---

## Prerequisites

Load `agents/00_core_guardrails.md` into context before executing.

## Trigger Command

```
Load agents/00_core_guardrails.md. Execute agents/01_initialize.md against all files in data_raw/ and docs_input/research_brief.md.
```

---

## Input Spec

| Input | Location | Format | Required |
|-------|----------|--------|----------|
| Raw data files | `data_raw/` | Any (CSV, XLSX, JSON, Parquet, SHP, GeoJSON, SQL dump, PDF, TXT, audio, image manifest, etc.) | Yes |
| Research brief | `docs_input/research_brief.md` | Markdown | Yes |

**Halt conditions (fail before any action):**
- `data_raw/` contains no files, or all files have zero size → halt, log ERROR
- `docs_input/research_brief.md` missing, contains no hypothesis/RQ, or identifies no outcome variable → halt, log ERROR
- Detected data format is binary and unrecognizable (e.g., encrypted) → halt, log ERROR with format guidance

---

## Action Mechanics

### Step 1 — Advanced File Inventory & Modality Detection

List all files in `data_raw/`. For each file record:
- Full filename, size in bytes, and MIME type detected via file-signature magic bytes (not file extension alone).
- Structural modality: flat tabular, relational/multi-table, hierarchical JSON/XML, raw text corpus, spatial vector, spatial raster, graph edge-list, audio/image manifest.
- For tabular files: row count, column count, and delimiter/encoding detected.

### Step 2 — Deep Structural & Epistemic Profiling

For every file:

**Tabular/Structured:**
- Dimensions ($N \times P$), inferred dtypes with explicit detection of mixed-type columns.
- Missingness: global percentage, per-column percentage, and a Little's MCAR test (if $N < 5000$; else pattern correlation matrix) to hypothesize MCAR, MAR, or MNAR mechanism.
- Outlier screening: IQR fence (Tukey, 1977) and modified Z-score (|$M_i$| > 3.5) per numeric column.
- Cardinality of all categorical columns; detection of high-cardinality columns (>50 unique levels) that may require hashing or embedding.
- Descriptive statistics: N valid, M, SD, Median, IQR, Skewness ($g_1$, SE), Kurtosis ($g_2$, SE), Min, Max.
- Relational integrity: duplicate rows, potential composite keys, foreign-key style relationships across multiple files.

**Temporal:**
- DateTime index detection and validation (ISO 8601).
- Irregular interval detection and gap analysis.
- Seasonal decomposition suitability check.

**Text Corpus:**
- Vocabulary size, average document length, language detection (via `langdetect`).
- Presence of HTML/markdown artifacts, encoding issues.

**Spatial:**
- CRS detection, bounding box, geometry type, null geometries.

**Network/Graph:**
- Node count, edge count, density, number of connected components, presence of self-loops.

### Step 3 — Domain & Data Type Classification

Assign exactly one **primary type code** and zero or more secondary codes. Document specific signals justifying each decision.

| Code | Primary Type | Trigger Signals | Default Base Stack |
|------|-------------|----------------|--------------------|
| `TABULAR-CROSS` | Cross-sectional tabular | Single time point, independent observations | `pandas`, `scipy`, `statsmodels` |
| `TABULAR-PANEL` | Panel / longitudinal | Entity ID + time index; repeated measures; nested clustering | `linearmodels`, `statsmodels`, `pymer4` |
| `TABULAR-SURVEY` | Survey / psychometrics | Likert scales, ordinal variables, scale items, skip patterns | `pingouin`, `factor_analyzer`, `semopy` |
| `TEXT-CORPUS` | Unstructured text | Long-string columns, PDFs, `.txt` files, corpora | `spacy`, `transformers`, `BERTopic` |
| `TIME-SERIES` | Temporal sequence | Monotonic DateTime index; regular/irregular intervals | `statsmodels`, `sktime`, `prophet`, `neuralprophet` |
| `SPATIAL` | Geographic / spatial | Coordinate columns, `.shp`, `.geojson`, `.tif`, rasters | `geopandas`, `PySAL`, `rasterio`, `xarray` |
| `NETWORK` | Graph / relational | Edge lists, adjacency matrices, `.graphml` | `networkx`, `igraph`, `torch_geometric` |
| `BIOMEDICAL` | Genomic / clinical / imaging | FASTA, FASTQ, DICOM, `.vcf`, clinical trial tables | `biopython`, `scanpy`, `nibabel` |
| `MIXED` | Multi-modal | Two or more of the above in the same project | Routed sub-pipelines per type |

If classification is ambiguous, classify as `MIXED`, document all candidate codes with evidence, and flag for manual review with severity HIGH.

### Step 4 — Research Brief Parsing & Causal Mapping

Extract and rigorously structure:
- **Hypotheses:** All stated RQs (numbered), directional claims, and null hypotheses.
- **Variable Taxonomy:** Map every named variable to its strict epistemic role:
  - Outcome/Dependent (Y)
  - Treatment/Exposure (T)
  - Confounder/Covariate (W)
  - Mediator (M)
  - Moderator/Effect Modifier (E)
  - Instrumental Variable (Z)
  - Cluster/Group ID (G)
  - Time Index (T_idx)
- **Causal Design:** Parse for explicit randomization or natural experiment design (RCT, RDD, DiD, IV, Matching, Synthetic Control, Interrupted Time Series). If observational, flag the identification threat.
- **Stated Constraints:** Exclusion criteria, time windows, sub-group restrictions.
- **Domain Context:** Identify the substantive research domain (public health, economics, ecology, neuroscience, etc.) to ensure domain-specific norms are applied downstream (e.g., clinical significance thresholds, CONSORT/STROBE reporting standards).

### Step 5 — Variable-to-Hypothesis Matrix

Create a detailed matrix. For each RQ:

| RQ | Outcome (Y) | Treatment/Predictor (T or X) | Covariates (W) | Mediators (M) | Moderators (E) | Required Design | Power Notes |
|----|-------------|------------------------------|----------------|---------------|----------------|-----------------|-------------|

Include statistical power assessment based on the literature-standard effect size for this domain. Flag if $N$ is underpowered.

### Step 6 — Rigorous Risk Register

| Issue | Variable(s) | Severity | Evidence | Recommended Mitigation |
|-------|-------------|----------|----------|------------------------|
| Data Leakage Risk | {col} | HIGH | Measured after outcome | Exclude from feature matrix |
| Severe Multicollinearity | {col1, col2} | HIGH | r > 0.80 detected | Ridge, PCA, or drop |
| MNAR Missingness | {col} | HIGH | Missingness correlated with outcome | Pattern-mixture model |
| MAR Missingness | {col} | MEDIUM | Missingness predicts by other vars | MICE imputation |
| Class Imbalance | {col} | MEDIUM | Minority class < 15% | SMOTE, weighted loss |
| Near-Zero Variance | {col} | MEDIUM | Variance < threshold | Drop or bin |
| Small Sub-Group N | {col} | MEDIUM | N < 30 in stratum | Report; consider collapsing |
| Construct Validity | {scale} | LOW | No reliability reported | Run Cronbach's α |

---

## Output Spec

| Output | Location |
|--------|----------|
| Epistemic baseline | `docs_input/initial_epistemic_baseline.md` |

### `initial_epistemic_baseline.md` Schema

```markdown
# Initial Epistemic Baseline
Generated: {ISO 8601}
Agent: 01_initialize.md

## 1. Data Inventory & Modality
{File-by-file table: filename, size, MIME, modality, dimensions, encoding}

## 2. Deep Structural Profiles
{Per-file: dtype audit, missingness mechanism (MCAR/MAR/MNAR heuristic), outlier summary, relational structure, temporal gaps or spatial CRS}

## 3. Data Type Classification
Primary: {CODE}
Secondary: {CODE, CODE}
Domain: {e.g., Public Health, Ecology, Finance}
Rationale: {Paragraph citing specific profile signals}

## 4. Research Question & Causal Mapping
{Hypothesis-to-variable taxonomy table}
{Causal design: RCT / Quasi-experimental (DiD, RDD, IV) / Observational}
{Identification threats if observational}

## 5. Variable-to-Hypothesis Matrix
{Full table as specified above}

## 6. Power Analysis Summary
{Per-RQ: assumed effect size (cite domain literature), required N, observed N, adequacy verdict}

## 7. Risk Register
{Full table with all identified issues}
```
