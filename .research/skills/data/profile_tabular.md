---
skill_id: "profile_tabular"
version: "3.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "pandas", "numpy", "pandera", "scipy"]
estimated_tokens: 3000
depends_on: []
produces: ["data/01_ingested/profile_tabular.json", "data/01_ingested/schema_definition.yaml"]
---

# Skill: Tabular Data Profiling

## Purpose
Perform deep structural and statistical profiling of raw tabular datasets (CSV, Parquet, SAS, SPSS/dta) to extract variables, distributions, and baseline schema metadata.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_path` | Path | Yes | Path to the raw data file |
| `missing_threshold` | Float | No | Proportion of missing values that triggers a warning (default: 0.20) |
| `cardinality_limit` | Int | No | Max unique categories to treat a variable as categorical (default: 50) |

## Execution Protocol

### Step 1: Physical File Parsing & Encoding Optimization
- Detect file format based on extension.
- Identify encoding: Iterate through `utf-8`, `latin-1`, `cp1252`. Fallback to binary byte scanning if all fail.
- Auto-detect CSV delimiter (e.g., `,`, `;`, `\t`) using Python's `csv.Sniffer`.
- Ingest using Pandas chunking (`chunksize=100000`) for large datasets to optimize memory footprint. Apply downcasting to numerical fields (`float64` to `float32`, `int64` to `int32`).

### Step 2: Semantic Type Classification
Categorize every column into one of five semantic types:
- **Identifier**: Primary/foreign keys (unique values matching row length).
- **Categorical**: Low-cardinality string/numeric columns (cardinality <= `cardinality_limit`).
- **Continuous**: High-cardinality numeric columns containing interval/ratio data.
- **Temporal**: Strings or numeric values matching datetime patterns (e.g., YYYY-MM-DD).
- **Text**: Long string columns with high token count variance.

### Step 3: Detailed Univariate Moments
- For Continuous columns, compute:
  - Central tendency: Mean, Median, Mode.
  - Dispersion: Range, Variance, Standard Deviation, Interquartile Range (IQR).
  - Shape: Skewness (Fisher-Pearson coefficient) and Kurtosis, including their Standard Errors to evaluate departure from normality.
- For Categorical columns:
  - Calculate cardinality and frequency counts of the top 10 values.
  - Calculate the Shannon Entropy score to measure category concentration.

### Step 4: Missingness & Zero-variance Screening
- Compute overall missing rate per column. If rate > `missing_threshold`, flag the column.
- Detect columns with zero variance (identical values across all rows) and exclude them from subsequent model pipelines.

### Step 5: Exporting Schema Definitions
- Save statistical summaries to `profile_tabular.json`.
- Construct a Pandera-compatible YAML schema defining data types, nullability, and unique constraints. Save as `schema_definition.yaml`.

## Output Specification
Produces in `data/01_ingested/`:
- `profile_tabular.json`
- `schema_definition.yaml`

## Validation Criteria
- [ ] Columns in output JSON exactly match columns in the raw dataset.
- [ ] Schema definition parses as a valid Pandera YAML document.
- [ ] Zero-variance columns are logged and flagged.