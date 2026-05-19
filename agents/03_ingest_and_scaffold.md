# Agent 03 — Ingest and Scaffold

**Purpose:** Build the workspace directory structure calibrated to the data type and analytical plan. Parse raw data into immutable, hash-verified ingested files. Generate the data dictionary and environment setup.

---

## Prerequisites

Load `agents/00_core_guardrails.md` into context before executing.

## Trigger Command

```
Load agents/00_core_guardrails.md. Execute agents/03_ingest_and_scaffold.md using docs_input/initial_epistemic_baseline.md and docs/papers_and_tools_cited.md as context.
```

---

## Input Spec

| Input | Location | Required |
|-------|----------|----------|
| Epistemic baseline | `docs_input/initial_epistemic_baseline.md` | Yes |
| Tools and literature review | `docs/papers_and_tools_cited.md` | Yes |
| Raw data | `data_raw/` | Yes |

**Halt condition:** Any required input missing or unreadable → halt, log ERROR.

---

## Action Mechanics

### Step 1 — Domain-Calibrated Directory Construction

Create **only** the directories required for the classified data type(s) and analytical plan. Never create empty directories not tied to an agent output.

**Base structure (all types):**
```
data/01_ingested/
data/02_processed/
data/03_analytical/
scripts/
reports/figures/
reports/tables/
reports/dashboards/
docs/
environment/
```

**Type-specific additions:**

| Data Type | Additional Directories |
|---|---|
| `TEXT-CORPUS` | `data/01_ingested/raw_text/`, `data/02_processed/tokens/`, `data/02_processed/embeddings/` |
| `SPATIAL` | `data/01_ingested/vectors/`, `data/01_ingested/rasters/`, `reports/maps/` |
| `NETWORK` | `data/01_ingested/graphs/`, `reports/network_layouts/` |
| `TIME-SERIES` | `data/01_ingested/timeseries/`, `data/02_processed/differenced/` |
| `BIOMEDICAL` | `data/01_ingested/genomics/`, `data/01_ingested/imaging/`, `data/02_processed/normalized/` |
| `MIXED` | Parallel sub-trees per type: `data/tabular/`, `data/text/`, `data/spatial/` as applicable |

### Step 2 — Per-Directory README Generation

Write a `README.md` into every created directory specifying:
- Exact data format expected (e.g., `.parquet`, `.geojson`, `.npy`)
- Which script writes to this directory
- Which script reads from this directory
- Mapping to research question(s) served

### Step 3 — Ingestion & Formal Schema Validation Script (`scripts/01_validation.py`)

Write a production-grade, fully documented ingestion script:

1. **Load Strategy:**
   - File < 1 GB: use `pandas.read_*` with explicit `dtype` dict from the baseline profile.
   - File 1–10 GB: use `polars` with lazy evaluation (`.scan_parquet()`, `.scan_csv()`).
   - File > 10 GB: use `dask.dataframe` with explicit partitioning strategy.

2. **Strict Schema Validation with `pandera`:**
   ```python
   import pandera as pa
   schema = pa.DataFrameSchema({
       "age": pa.Column(float, pa.Check.in_range(0, 120), nullable=False),
       "income": pa.Column(float, pa.Check.greater_than_or_equal_to(0), nullable=True),
       "group": pa.Column(str, pa.Check.isin(["A", "B", "C"])),
   }, coerce=True, strict="filter")
   validated_df = schema.validate(raw_df, lazy=True)
   ```
   All schema bounds are derived from the epistemic baseline. Validation errors (`pandera.errors.SchemaErrors`) must be caught, written to `docs/methods_log.md`, and re-raised.

3. **Referential Integrity (multi-file):** For relational datasets (multi-table), verify primary/foreign key relationships. Log any orphaned foreign key rows.

4. **Serialization:** Write validated data to `data/01_ingested/` as Apache Parquet (columnar, snappy-compressed, strongly typed). For spatial data: `.gpkg` (GeoPackage). For text: `.parquet` with a `text` string column and document `id` column.

5. **Provenance:** Compute SHA-256 hash of each output file using:
   ```python
   import hashlib
   def sha256_file(path: str) -> str:
       h = hashlib.sha256()
       with open(path, "rb") as f:
           for chunk in iter(lambda: f.read(65536), b""):
               h.update(chunk)
       return h.hexdigest()
   ```
   Append to `docs/data_dictionary.md`.

### Step 4 — Enhanced Data Dictionary (`docs/data_dictionary.md`)

Write an exhaustive data dictionary. One row per variable:

| Field | Description |
|-------|-------------|
| Original column name | Exactly as in source file |
| Canonical name | snake_case renamed version |
| Data type | Python/Arrow dtype |
| Measurement level | nominal / ordinal / interval / ratio |
| Causal Role | Outcome (Y) / Treatment (T) / Confounder (W) / Mediator (M) / Moderator (E) / Instrument (Z) / ID / Time / Other |
| Value constraints | Mathematical bounds or exact category set from schema |
| Missingness (N, %) | Count and percentage in ingested file |
| MCAR/MAR/MNAR flag | Mechanism hypothesis from baseline |
| Transformation applied | e.g., log, standardize, dummy-encode |
| Research questions served | RQ numbers |
| SHA-256 hash (file) | Hash of the ingested Parquet file |
| Hash timestamp | ISO 8601 |

Also include:
- **Table 0: Sample Characteristics** — a complete descriptive statistics table formatted per guardrail Table Standards.
- **Figure 0: Missingness Heatmap** — a static missingness pattern matrix (`missingno.matrix()`) saved to `reports/figures/missingness_heatmap.png`.

### Step 5 — Environment Setup

Based on `docs/papers_and_tools_cited.md` dependency manifest:

1. Write `environment/requirements.txt` with all packages version-pinned. Include a commented group structure:
   ```
   # Core data
   pandas==2.2.1
   polars==0.20.13
   pyarrow==15.0.2

   # Validation
   pandera==0.18.3

   # Analysis
   statsmodels==0.14.1
   ...
   ```

2. Write `environment/setup_env.sh`:
   ```bash
   #!/usr/bin/env bash
   set -euo pipefail
   python -m venv environment/venv
   source environment/venv/bin/activate
   pip install --upgrade pip
   pip install -r environment/requirements.txt
   python -c "import pandas; print('Environment validated.')"
   ```

3. After installation, write `environment/env_manifest.json`:
   ```json
   {
     "generated": "ISO 8601",
     "platform": "linux|darwin|win32",
     "python_version": "3.x.y",
     "packages": [
       {"name": "pandas", "version": "2.x.y", "hash": "sha256:..."}
     ]
   }
   ```

---

## Output Spec

| Output | Location |
|--------|----------|
| Ingestion & validation script | `scripts/01_validation.py` |
| Data dictionary | `docs/data_dictionary.md` |
| Validated data | `data/01_ingested/*.parquet` (or `.gpkg` for spatial) |
| Missingness heatmap | `reports/figures/missingness_heatmap.png` |
| Directory READMEs | `{every created directory}/README.md` |
| Requirements | `environment/requirements.txt` |
| Setup script | `environment/setup_env.sh` |
| Environment manifest | `environment/env_manifest.json` (written by setup_env.sh at install time) |
