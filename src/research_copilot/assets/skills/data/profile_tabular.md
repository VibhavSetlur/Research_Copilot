---
skill_id: "profile_tabular"
version: "7.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "pandas", "numpy", "scipy"]
depends_on: []
produces: ["data/01_ingested/profile_tabular.json", "data/01_ingested/schema_definition.yaml"]
complexity: "intermediate"
---

# Skill: Tabular Data Profiling

## Purpose
Perform structural and statistical profiling of raw tabular data to understand variable types, distributions, missingness, and data quality before any analysis.

## When to Use
- First skill executed on any new tabular dataset
- Before routing to analysis methods
- After data ingestion, before modeling

## When NOT to Use
- Data is unstructured text, images, or graphs (use domain-specific profilers)
- Dataset already profiled with matching hash

## Execution Protocol

### Step 1: File Ingestion
- Detect format from extension: CSV, TSV, Parquet, Excel, SAS (.sas7bdat), SPSS (.sav), Stata (.dta)
- Detect encoding: try UTF-8 → Latin-1 → CP-1252
- For CSV: auto-detect delimiter via `csv.Sniffer`
- For files >1GB: use chunked reading (`chunksize=100000`)
- **Quick Mode for files >100MB**: sample 10,000 rows, profile the sample, note in output that results are based on a sample. Use `pd.read_csv(path, nrows=10000)` or `df.sample(n=10000)` for non-CSV formats. Include warning: "Profile based on 10,000-row sample of {total_rows} rows. Full profile may differ."
- Downcast numerics: float64→float32, int64→int32 where safe
- Record SHA-256 hash of source file

### Step 2: Semantic Type Classification
Classify each column into exactly one type:
- **Identifier**: n_unique == n_rows, or matches ID patterns (UUID, sequential)
- **Categorical**: n_unique ≤ 50 AND (string OR low-cardinality numeric)
- **Continuous**: n_unique > 50 AND numeric dtype
- **Temporal**: datetime dtype OR matches date patterns (YYYY-MM-DD, timestamps)
- **Text**: string dtype, n_unique > 50, mean string length > 20
- **Boolean**: exactly 2 unique values (including 0/1, True/False, Yes/No)

### Step 3: Univariate Statistics
**Continuous**: N, mean, median, SD, IQR, min, max, skewness (G1), kurtosis (G2), CV, zero-count, negative-count, quantiles (1%, 5%, 10%, 25%, 50%, 75%, 90%, 95%, 99%)

**Categorical**: cardinality, mode + frequency, Shannon entropy H(X) and normalized H/H_max, top-10 categories, rare category count (<1% of observations)

**Temporal**: date range, span, frequency inference (daily/weekly/monthly/irregular), gap detection

### Step 4: Missingness Analysis
- Per-column missing count and proportion
- Flag columns exceeding 20% missing
- Compute missingness correlation matrix (binary indicators)
- If N < 5000: run Little's MCAR test
- Classify pattern: MCAR, MAR indicators, or MNAR indicators

### Step 5: Quality Screening
- Zero-variance columns: exactly 1 unique value → exclude from modeling
- Near-zero-variance: most frequent / second most frequent > 95:5 AND unique% < 10% → flag
- Duplicate rows: count and log
- Columns with all-null or all-same-value → flag for removal

### Step 6: Cross-Column Screening
- Numeric-numeric: Pearson + Spearman correlation; flag |r| > 0.90 (multicollinearity risk)
- Categorical-categorical: Cramér's V; flag V > 0.70
- Binary-continuous: point-biserial correlation

### Step 7: Schema Export
Generate Pandera-compatible YAML with: column dtypes, nullable constraints, unique constraints (identifiers), value ranges (min/max for numeric), allowed categories (for categorical)

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| Skewness | |G1| < 1.0 | Heavy skew; mean misleading | Use median/IQR; plan transformation |
| Missingness | < 20% per column | Systematic data loss | Document mechanism; plan imputation |
| Zero variance | None found | Uninformative column | Exclude from modeling |
| Perfect correlation | |r| < 1.0 | Redundant variables | Drop one of the pair |
| Cardinality | ≤ 50 for categorical | Too many levels | Group rare categories or target-encode |

### Red Flags
- **Negative values on theoretically positive variables** (age, price, count): data entry error or encoding issue
- **Dates parsed as strings**: specify format explicitly; check for mixed formats
- **ID columns classified as continuous**: override type to identifier
- **Memory overflow**: dataset too large → use `sample_size=100000` or switch to Polars/Dask

## Domain Conventions

| Domain | Key Variables to Expect | Plausibility Checks |
|--------|------------------------|---------------------|
| Epidemiology | patient_id, ICD codes, survival_time, event_status | Age ≤ 120, survival_time ≥ 0 |
| Econometrics | panel_id, year, gdp, wages, prices | No negative prices, rates in [-1, 1] |
| Psychology | participant_id, scale_scores, Likert items | Scores within scale bounds |
| Genomics | gene_id, chromosome, expression, p_value | p ∈ [0,1], expression ≥ 0 |

## Reporting Template
> "The dataset comprised N = [value] observations across P = [value] variables ([format], [size] MB, [encoding]). Variables: [count] continuous, [count] categorical, [count] temporal. Overall missingness: [percentage]%. [Count] variables exceeded the 20% missingness threshold. [Count] zero-variance columns excluded. [Count] variables showed substantial skewness (|G1| > 1.0)."

## Output Specification
- `data/01_ingested/profile_tabular.json`: full profile with metadata, dimensions, per-column stats, missingness, quality flags
- `data/01_ingested/schema_definition.yaml`: Pandera-compatible schema

## Validation Checks
- [ ] Column count in profile matches source file
- [ ] Row count matches source file
- [ ] Schema parses as valid YAML
- [ ] All proportions in [0, 1]
- [ ] Entropy values non-negative
- [ ] File hash recorded and reproducible
