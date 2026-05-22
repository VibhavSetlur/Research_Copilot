SKILL_PROMPTS = {
    "SKILL_TEMPLATE": """---
skill_id: "skill_id_here"
version: "1.0.0"
category: "data|analysis|literature|visualization|writing|audit|integration"
domain_compatibility: ["all"]
required_tools: []
depends_on: []
produces: []
complexity: "basic|intermediate|advanced"
---

# Skill: {Human-Readable Name}

<objective>
One sentence: what this skill does and when it fires.
</objective>

<routing_logic>
IF condition_1 → use method_A
ELIF condition_2 → use method_B
ELSE → use method_C with caveat
</routing_logic>

<protocol>
### Step 1: Pre-checks
- Validate inputs
- Check assumptions
- Flag violations before proceeding

### Step 2: Core Procedure
- Numbered steps with branching
- Include parameter defaults
- Note where domain conventions differ

### Step 3: Diagnostics
- Run diagnostic tests
- Interpret each result
- Branch based on pass/fail

### Step 4: Robustness
- Sensitivity checks
- Alternative specifications
- Compare conclusions across methods
</protocol>

<constraints>
- Check assumption A before proceeding.
- Do not use method B if condition C is met.
</constraints>

<output_schema>
{
  "summary": "human-readable summary",
  "diagnostics": {"pass": true},
  "metrics": {}
}
</output_schema>
""",
    "validate_schema": """---
skill_id: "validate_schema"
version: "7.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "pandera", "pydantic"]
depends_on: ["profile_tabular"]
produces: ["data/01_ingested/validation_report.json"]
complexity: "basic"
---

# Skill: Schema Validation

## Purpose
Validate incoming data against a predefined schema to ensure structural integrity, type correctness, and constraint compliance before analysis.

## When to Use
- On every new data ingestion
- After data transformations
- Before running analysis pipelines
- When data source changes version or format

## When NOT to Use
- Exploratory analysis on unknown data (profile first)
- Schema not yet defined (run profile_tabular first)

## Execution Protocol

### Step 1: Load Schema
- Load YAML schema from `data/01_ingested/schema_definition.yaml`
- If no schema exists, generate from profile_tabular output
- Verify schema covers all columns in incoming data

### Step 2: Structural Validation
- Column presence: all required columns exist
- Column count: no unexpected extra columns (warn, don't fail)
- Row count: within expected range (if bounds defined)

### Step 3: Type Validation
- Each column matches expected dtype (int, float, string, datetime, bool)
- Check for mixed-type columns (strings in numeric columns)
- Verify datetime parseability

### Step 4: Constraint Validation
- **Range constraints**: numeric values within [min, max]
- **Category constraints**: categorical values in allowed set
- **Uniqueness constraints**: identifier columns have unique values
- **Nullability**: non-nullable columns have no nulls
- **String constraints**: length, pattern (regex) matching

### Step 5: Cross-Column Validation
- Derived columns match source (e.g., age = current_year - birth_year ± 1)
- Logical constraints (e.g., end_date ≥ start_date, discharge_diagnosis present only if admitted)
- Sum constraints (e.g., category proportions sum to 1.0 ± 0.01)

### Step 6: Report Generation
- Pass/fail per constraint
- For failures: column, constraint type, count of violations, sample violating values
- Overall verdict: PASS (all critical), WARN (non-critical only), FAIL (critical violations)

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| Required columns present | All found | Identify missing columns; check source |
| Type match | All correct | Coerce if safe, otherwise flag |
| Range bounds | All within | Investigate out-of-range values |
| Uniqueness | All unique | Check for duplicates or key collision |
| Nullability | No unexpected nulls | Check if null is valid or data loss |

### Red Flags
- **Critical column missing**: cannot proceed; halt pipeline
- **Type mismatch on numeric column**: may indicate encoding issue (e.g., "N/A" in numeric field)
- **> 10% constraint violations**: schema may be outdated; regenerate from current data
- **Cross-column violation**: logic error in data or schema; investigate

## Reporting Template
> "Schema validation [PASSED/FAILED/WARNED]. [N] of [M] constraints passed. Violations: [list]. Data [is/is not] suitable for downstream analysis."

## Output Specification
- `data/01_ingested/validation_report.json`: per-constraint results, violation details, overall verdict

## Validation Checks
- [ ] All schema constraints tested
- [ ] Violations include sample values
- [ ] Overall verdict assigned (PASS/WARN/FAIL)
- [ ] Report timestamped with source file hash
""",
    "profile_spatial": """---
skill_id: "profile_spatial"
version: "7.0.0"
category: "data"
domain_compatibility: ["ecology", "epidemiology", "geography"]
required_tools: ["python", "geopandas", "shapely", "pyproj"]
depends_on: ["profile_tabular"]
produces: ["data/01_ingested/spatial_profile.json"]
complexity: "advanced"
---

# Skill: Spatial Data Profiling

## Purpose
Profile geospatial data to understand coordinate systems, spatial extent, topology, and spatial autocorrelation structure.

## When to Use
- Dataset contains coordinates (lat/lon), geometries, or spatial identifiers
- Before spatial analysis, mapping, or geostatistical modeling
- When merging datasets by location

## When NOT to Use
- No spatial information in data
- Spatial resolution is too coarse for analysis (e.g., country-level only)

## Execution Protocol

### Step 1: Spatial Reference Identification
- Detect coordinate reference system (CRS): EPSG code or WKT string
- If lat/lon columns: assume EPSG:4326 (WGS84)
- If projected coordinates: identify projection type
- Flag unknown or missing CRS

### Step 2: Spatial Extent
- Bounding box: min/max latitude, min/max longitude
- Centroid: geographic center of all observations
- Spatial span: maximum pairwise distance (km)
- Area coverage: convex hull area

### Step 3: Point Pattern Analysis
- Point density: points per unit area
- Nearest neighbor distances: mean, median, SD
- Clark-Evans index: R < 1 = clustered, R = 1 = random, R > 1 = dispersed
- Ripley's K function (if N > 100): assess clustering at multiple scales

### Step 4: Spatial Autocorrelation
- Construct spatial weights matrix (k-nearest neighbors or distance band)
- Global Moran's I: overall spatial autocorrelation
- Local Moran's I (LISA): identify hot spots, cold spots, spatial outliers
- Geary's C: alternative measure (more sensitive to local differences)

### Step 5: Topology Checks
- Duplicate coordinates: count and flag
- Points outside expected bounds: e.g., lat outside [-90, 90], lon outside [-180, 180]
- Points on land vs water (if applicable)
- Coordinate precision: sufficient for analysis scale

### Step 6: Aggregation Unit Assessment (if polygon data)
- Polygon count, area distribution
- Modifiable Areal Unit Problem (MAUP) risk: results may change with different aggregation
- Neighbor relationships: queen vs rook contiguity

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| CRS defined | Known projection | Coordinates ambiguous | Assign CRS based on context |
| Moran's I p > 0.05 | No spatial autocorrelation | Spatial dependence present | Use spatial regression models |
| Coordinate bounds | All valid | Impossible coordinates | Correct or remove invalid points |
| Point density | Adequate for scale | Too sparse or too dense | Adjust analysis resolution |

### Red Flags
- **Swapped lat/lon**: points in ocean or wrong continent; verify coordinate order
- **Mixed CRS**: some points in different projection; unify before analysis
- **Spatial clustering (R < 0.5)**: non-independence violates standard regression assumptions
- **MAUP risk**: results at one aggregation level may not hold at another

## Output Specification
- `data/01_ingested/spatial_profile.json`: CRS, bounding box, extent, point pattern analysis, spatial autocorrelation results, topology flags

## Validation Checks
- [ ] CRS is identified or assigned
- [ ] All coordinates within valid bounds
- [ ] Spatial autocorrelation tested
- [ ] Point pattern classified (clustered/random/dispersed)
""",
    "profile_tabular": """---
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
""",
    "cloud_hpc_execution": """---
skill_id: "cloud_hpc_execution"
version: "1.0.0"
category: "data"
description: "Remote execution for TB-scale data — SQL for cloud warehouses, PySpark for distributed compute, Slurm for HPC clusters"
domain_compatibility: ["all"]
applies_to_phases: ["data_scaffold", "execute_analysis"]
---

# Skill: Cloud & HPC Execution

## Purpose

When data exceeds local machine capacity (TB-scale), this skill enables the AI to write queries for cloud data warehouses (Snowflake, BigQuery, Redshift), PySpark for distributed compute, or Slurm batch scripts for university supercomputers. Only aggregated results are pulled back to the local machine.

## Detection

The `data_scale_detector` identifies when data is too large for local processing:
- **Local OK**: < 10GB (polars + pyarrow chunking)
- **Cloud/HPC needed**: >= 10GB or data already in cloud storage

## Protocol

### Step 1: Identify Execution Environment

Check for environment indicators:
1. Is data in cloud storage? (S3, GCS, Azure Blob paths)
2. Is a cloud warehouse available? (credentials in environment variables)
3. Is an HPC cluster available? (Slurm commands work)
4. What is the data scale profile?

### Step 2: Choose Execution Strategy

| Data Location | Size | Strategy |
|--------------|------|----------|
| Local | < 10GB | polars lazy + pyarrow (local) |
| Local | >= 10GB | Upload to cloud OR use HPC |
| S3/GCS | Any | PySpark on EMR/Dataproc |
| Snowflake | Any | SQL pushdown |
| BigQuery | Any | SQL pushdown |
| HPC filesystem | Any | Slurm batch job |

### Step 3: Generate Execution Code

#### Option A: SQL Pushdown (Snowflake/BigQuery)

```python
# For Snowflake
import snowflake.connector

conn = snowflake.connector.connect(
    user=os.environ['SNOWFLAKE_USER'],
    password=os.environ['SNOWFLAKE_PASSWORD'],
    account=os.environ['SNOWFLAKE_ACCOUNT'],
    warehouse='COMPUTE_WH',
    database='RESEARCH_DB',
    schema='PUBLIC',
)

query = \"\"\"
SELECT
    outcome_var,
    predictor_var,
    control_1,
    control_2,
    COUNT(*) as n,
    AVG(outcome_var) as mean_outcome,
    STDDEV(outcome_var) as sd_outcome
FROM research_data
WHERE outcome_var IS NOT NULL
  AND predictor_var IS NOT NULL
GROUP BY outcome_var, predictor_var, control_1, control_2
\"\"\"

df = conn.cursor().execute(query).fetch_pandas_all()
df.to_parquet("data/03_analytical/aggregated_data.parquet")
```

#### Option B: PySpark (Distributed Compute)

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder \\
    .appName("Research Analysis") \\
    .config("spark.sql.adaptive.enabled", "true") \\
    .getOrCreate()

# Read from cloud storage
df = spark.read.parquet("s3://bucket/data/raw/")

# Data processing (executed on cluster)
processed = (
    df
    .filter(F.col("outcome_var").isNotNull())
    .withColumn("log_outcome", F.log(F.col("outcome_var")))
    .groupBy("predictor_var")
    .agg(
        F.mean("outcome_var").alias("mean_outcome"),
        F.stddev("outcome_var").alias("sd_outcome"),
        F.count("*").alias("n"),
    )
)

# Only pull aggregated results back
result = processed.toPandas()
result.to_parquet("data/03_analytical/aggregated_data.parquet")

spark.stop()
```

#### Option C: Slurm Batch Script

Generate `scripts/slurm_job_{timestamp}.sh`:

```bash
#!/bin/bash
#SBATCH --job-name=research_analysis
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --output=logs/slurm_%j.out
#SBATCH --error=logs/slurm_%j.err

module load python/3.11
source /path/to/venv/bin/activate

python scripts/02_analysis.py --input data/02_processed/ --output data/03_analytical/
```

Submit with: `sbatch scripts/slurm_job_{timestamp}.sh`

### Step 4: Data Lineage Tracking

Regardless of execution environment, record:
1. Where computation happened (local, cloud, HPC)
2. What query/script was executed
3. What data was pulled back (aggregated only)
4. SHA-256 hash of aggregated results

Update `docs/data_lineage.json`:
```json
{
  "execution_environment": "snowflake",
  "query_hash": "sha256_of_query",
  "input_location": "snowflake://RESEARCH_DB.PUBLIC.research_data",
  "output_location": "data/03_analytical/aggregated_data.parquet",
  "output_hash": "sha256_of_output",
  "rows_processed": 1000000000,
  "rows_returned": 10000,
  "compression_ratio": 0.00001
}
```

### Step 5: Cost Estimation

For cloud execution, estimate and log costs:
- Snowflake: credits consumed × credit cost
- BigQuery: bytes processed × cost per TB
- EMR/Dataproc: instance-hours × hourly rate

Log to `.research/cache/cost_log.jsonl`:
```json
{
  "timestamp": "2026-01-15T10:30:00Z",
  "service": "snowflake",
  "credits": 2.5,
  "estimated_cost_usd": 5.00,
  "query_type": "aggregation"
}
```

## Quality Rules

1. NEVER pull raw data from cloud to local — only aggregated results
2. ALWAYS use parameterized queries (no SQL injection)
3. ALWAYS log execution environment and costs
4. ALWAYS verify aggregated results match expected row counts
5. ALWAYS use the most cost-effective strategy for the data size
6. ALWAYS test queries on a small sample before full execution
7. ALWAYS document the execution environment in data lineage
""",
    "profile_network": """---
skill_id: "profile_network"
version: "7.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "networkx", "pandas"]
depends_on: ["profile_tabular"]
produces: ["data/01_ingested/network_profile.json"]
complexity: "advanced"
---

# Skill: Network Data Profiling

## Purpose
Profile graph/network data to understand connectivity, centrality, community structure, and topological properties.

## When to Use
- Data represents relationships between entities (edges between nodes)
- Before network analysis, community detection, or graph ML
- When data has source-target or adjacency structure

## When NOT to Use
- Data is tabular without relational structure
- Network is trivially small (< 5 nodes)

## Execution Protocol

### Step 1: Graph Construction
- Identify node list and edge list
- Determine: directed vs undirected, weighted vs unweighted, bipartite vs monopartite
- Build graph using NetworkX
- Verify: no self-loops (unless expected), no duplicate edges (unless multigraph)

### Step 2: Basic Graph Properties
- Node count (N), edge count (E)
- Density: E / [N(N-1)/2] for undirected
- Average degree, degree distribution
- Connected components: count, size distribution
- Largest connected component: node count, proportion of total

### Step 3: Centrality Analysis
- Degree centrality: most connected nodes
- Betweenness centrality: nodes bridging communities
- Closeness centrality: nodes closest to all others
- Eigenvector centrality: nodes connected to other important nodes
- Report top-10 nodes by each measure

### Step 4: Community Structure
- Detect communities: Louvain or Leiden algorithm
- Number of communities, modularity score (Q)
- Community size distribution
- Inter-community vs intra-community edge ratio

### Step 5: Path Analysis
- Average shortest path length
- Graph diameter (longest shortest path)
- Clustering coefficient (local and global)
- Small-world check: high clustering + short path length

### Step 6: Degree Distribution Fitting
- Fit power law, exponential, log-normal to degree distribution
- Determine best-fitting distribution
- If power law: estimate exponent γ (scale-free if 2 < γ < 3)

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| Graph connected | Single component or giant component | Fragmented network | Analyze components separately |
| Modularity Q > 0.3 | Community structure present | No clear communities | Use alternative clustering |
| Degree distribution | Fits known model | Unknown structure | Use non-parametric methods |
| Density | 0.01 - 0.5 | Too sparse or too dense | Check for missing edges or over-reporting |

### Red Flags
- **Isolated nodes (> 20% of network)**: data collection incomplete; consider removing or treating separately
- **Single hub dominates**: star topology; results driven by one node
- **Disconnected graph**: analyze largest component only, report fragmentation
- **Bipartite treated as monopartite**: project correctly before analysis

## Output Specification
- `data/01_ingested/network_profile.json`: graph properties, centrality rankings, community structure, path metrics, degree distribution fit

## Validation Checks
- [ ] Graph is constructible from edge list
- [ ] Node and edge counts consistent
- [ ] Centrality measures sum to expected totals
- [ ] Modularity score in [-0.5, 1]
""",
    "data_lineage": """---
skill_id: "data_lineage"
version: "1.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "pandas"]
depends_on: ["profile_tabular", "compute_hashes"]
produces: ["docs/data_lineage.json"]
complexity: "intermediate"
---

# Skill: Data Lineage Tracking

## Purpose
Create a machine-readable record of every data transformation from raw input to analytical dataset. Enables full reproducibility: given raw data + lineage = exact reproduction of analysis-ready data.

## When to Use
- After ANY data transformation (cleaning, merging, filtering)
- Before running analysis on processed data
- When sharing data pipeline with collaborators
- For audit trail in regulated research

---

## Lineage Model

Each transformation is recorded as a **node** with:
- `id`: unique identifier (e.g., "transform_001")
- `type`: clean | merge | filter | transform | aggregate | encode
- `input_files`: list of source file paths
- `output_file`: resulting file path
- `operation`: human-readable description
- `parameters`: exact parameters used
- `timestamp`: when transformation was applied
- `script`: which script performed the transformation
- `input_hash`: hash of input files (verifies raw data unchanged)
- `output_hash`: hash of output file (verifies output unchanged)
- `row_count_before`: rows before transformation
- `row_count_after`: rows after transformation
- `column_count_before`: columns before
- `column_count_after`: columns after

---

## Lineage File Structure

`docs/data_lineage.json`:
```json
{
  "schema_version": "1.0.0",
  "project": "[title]",
  "created": "[date]",
  "last_updated": "[date]",
  "raw_files": [
    {
      "path": "00_inputs/raw_data/survey.csv",
      "hash": "sha256:abc123...",
      "rows": 1500,
      "columns": 45,
      "size_kb": 234.5,
      "ingested_date": "2026-05-19"
    }
  ],
  "pipeline": [
    {
      "id": "transform_001",
      "type": "clean",
      "input_files": ["00_inputs/raw_data/survey.csv"],
      "output_file": "data/01_ingested/survey_clean.csv",
      "operation": "Standardized encoding, normalized column names, coded missing values",
      "parameters": {
        "encoding": "utf-8",
        "column_case": "snake_case",
        "missing_codes": {"": "NaN", "NULL": "NaN", "-999": "NaN"}
      },
      "timestamp": "2026-05-19T10:30:00",
      "script": "scripts/01_data_prep.py",
      "input_hash": "sha256:abc123...",
      "output_hash": "sha256:def456...",
      "row_count_before": 1500,
      "row_count_after": 1487,
      "column_count_before": 45,
      "column_count_after": 45,
      "rows_removed": 13,
      "rows_removed_reason": "Duplicate records (n=8), invalid dates (n=5)"
    },
    {
      "id": "transform_002",
      "type": "merge",
      "input_files": ["data/01_ingested/survey_clean.csv", "data/01_ingested/demographics_clean.csv"],
      "output_file": "data/02_processed/merged_dataset.csv",
      "operation": "Left join survey and demographics on participant_id",
      "parameters": {
        "how": "left",
        "on": "participant_id",
        "indicator": true
      },
      "timestamp": "2026-05-19T11:00:00",
      "script": "scripts/01_data_prep.py",
      "input_hash": "sha256:def456...,sha256:ghi789...",
      "output_hash": "sha256:jkl012...",
      "row_count_before": "1487 + 1500",
      "row_count_after": 1487,
      "column_count_before": "45 + 12",
      "column_count_after": 56,
      "merge_stats": {
        "matched": 1450,
        "left_only": 37,
        "right_only": 50
      }
    }
  ],
  "analytical_datasets": [
    {
      "name": "analysis_q1.csv",
      "path": "data/03_analytical/analysis_q1.csv",
      "hash": "sha256:mno345...",
      "rows": 1420,
      "columns": 18,
      "derived_from": ["transform_002", "transform_005"],
      "question": "Q1: What is the effect of X on Y?",
      "variables": {
        "outcome": ["outcome_score"],
        "predictor": ["treatment_group"],
        "covariates": ["age", "gender", "baseline_score"]
      }
    }
  ],
  "integrity_check": {
    "all_raw_hashes_match": true,
    "all_transforms_reproducible": true,
    "last_verified": "2026-05-19T12:00:00"
  }
}
```

---

## Execution Protocol

### Step 1: Record Raw Files
When data is first scanned:
1. Compute SHA-256 hash of each raw file
2. Record file metadata (rows, columns, size)
3. Store in `raw_files` array

### Step 2: Record Each Transformation
After EVERY data operation:
1. Generate unique transform ID (transform_XXX)
2. Record input/output file paths
3. Record operation type and parameters
4. Compute input and output hashes
5. Record row/column counts before and after
6. Append to `pipeline` array

### Step 3: Record Analytical Datasets
When analysis-ready data is created:
1. Record which pipeline steps produced it
2. Record variable roles (outcome, predictor, covariate)
3. Record which research question it serves
4. Store in `analytical_datasets` array

### Step 4: Verify Integrity
Periodically (and before analysis):
1. Re-hash all raw files — compare to stored hashes
2. If hash mismatch: raw data changed, pipeline may be invalid
3. Re-hash analytical datasets — compare to stored hashes
4. Update `integrity_check` with results

---

## Transformation Types

| Type | Description | Required Parameters |
|------|-------------|-------------------|
| `clean` | Encoding, column names, missing values | encoding, column_case, missing_codes |
| `merge` | Join two or more datasets | how, on, indicator |
| `filter` | Subset rows by condition | condition, rows_removed, reason |
| `transform` | Create/modify columns | new_columns, formula |
| `aggregate` | Group and summarize | group_by, agg_functions |
| `encode` | Categorical encoding | method, mapping |
| `impute` | Missing value imputation | method, variables, parameters |
| `scale` | Normalization/standardization | method, variables |
| `split` | Train/test split | test_size, random_state, stratify |

---

## Reproducibility Check

```python
def verify_lineage(lineage_path, raw_dir):
    \"\"\"Verify data pipeline is reproducible.
    
    Returns:
        dict with status, mismatches, recommendations
    \"\"\"
    import json, hashlib
    
    with open(lineage_path) as f:
        lineage = json.load(f)
    
    results = {
        "status": "pass",
        "mismatches": [],
        "recommendations": []
    }
    
    # Check raw file integrity
    for raw_file in lineage["raw_files"]:
        file_hash = compute_sha256(raw_dir / raw_file["path"])
        if file_hash != raw_file["hash"]:
            results["status"] = "fail"
            results["mismatches"].append({
                "file": raw_file["path"],
                "expected": raw_file["hash"],
                "actual": file_hash,
                "issue": "Raw file has been modified since pipeline was created"
            })
    
    # Check pipeline completeness
    transform_ids = [t["id"] for t in lineage["pipeline"]]
    for i, t in enumerate(lineage["pipeline"]):
        if not t.get("output_hash"):
            results["status"] = "warn"
            results["recommendations"].append(
                f"Transform {t['id']} missing output hash"
            )
    
    return results
```

---

## Integration with research_init

During `research_init`:
1. Scan raw files → record hashes in lineage
2. Create empty lineage file
3. AI updates lineage after each data transformation

## Integration with data_scaffold

During `data_scaffold`:
1. Record every cleaning step
2. Record every merge operation
3. Record every filter/transform
4. Final analytical datasets recorded with variable roles

---

## Validation Checks
- [ ] All raw files have SHA-256 hashes recorded
- [ ] Every transformation has input and output hashes
- [ ] Row/column counts are consistent across pipeline
- [ ] Analytical datasets trace back to raw files
- [ ] Integrity check passes (raw hashes match)
- [ ] Lineage file is valid JSON with correct schema
""",
    "profile_text": """---
skill_id: "profile_text"
version: "7.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "pandas", "nltk|spacy"]
depends_on: ["profile_tabular"]
produces: ["data/01_ingested/text_profile.json"]
complexity: "intermediate"
---

# Skill: Text Corpus Profiling

## Purpose
Profile text columns to understand corpus size, vocabulary richness, language distribution, readability, and structural properties.

## When to Use
- Dataset contains free-text columns (surveys, documents, social media)
- Before NLP analysis (topic modeling, sentiment, embeddings)
- To assess text quality and preprocessing needs

## When NOT to Use
- Text is already tokenized or preprocessed
- Only a few short string fields (e.g., names, labels)

## Execution Protocol

### Step 1: Basic Corpus Statistics
- Document count (N), total tokens, total characters
- Per-document: token count, character count, sentence count, word count
- Average document length, SD, min, max
- Empty document count and proportion

### Step 2: Vocabulary Analysis
- Vocabulary size (unique types)
- Type-token ratio (TTR = types / tokens)
- Hapax legomena: words appearing exactly once
- Top-20 most frequent tokens (excluding stopwords)
- Average word length, SD

### Step 3: Language Detection
- Detect language per document (if multilingual suspected)
- Report language distribution
- Flag documents with low-confidence language detection

### Step 4: Readability Assessment
- Flesch-Kincaid Grade Level
- Flesch Reading Ease score
- Gunning Fog Index
- Average sentence length
- Proportion of complex words (> 3 syllables)

### Step 5: Quality Screening
- Duplicate documents: exact match count
- Near-duplicates: Jaccard similarity > 0.90 on token sets
- Documents with excessive special characters (> 20% non-alphanumeric)
- Documents with extremely short length (< 3 tokens)
- Documents with extremely long length (> 99th percentile)

### Step 6: Structural Properties
- Paragraph count per document
- Punctuation density
- Proportion of uppercase characters (shouting detection)
- URL/email/mention count (for social media text)
- Hashtag count (for social media)

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| TTR | 0.4 - 0.8 | Lexically impoverished or overly diverse | Check for boilerplate or mixed languages |
| Readability | Grade 6-16 | Too simple or too complex | Adjust preprocessing or segment corpus |
| Language consistency | Single dominant language | Multilingual corpus | Split by language or use multilingual models |
| Duplicate rate | < 5% | Significant duplication | Deduplicate before analysis |

### Red Flags
- **> 30% empty or near-empty documents**: data collection issue; filter before analysis
- **Extreme length skew**: few very long documents dominate; consider truncation or weighting
- **High special character ratio**: encoding issues or non-text data; inspect raw bytes
- **All documents identical length**: possible template or form data; not suitable for topic modeling

## Output Specification
- `data/01_ingested/text_profile.json`: corpus stats, vocabulary analysis, language distribution, readability scores, quality flags

## Validation Checks
- [ ] Document count matches source
- [ ] Vocabulary size ≤ total tokens
- [ ] Readability scores in plausible ranges
- [ ] Language codes are valid ISO 639
""",
    "classify_domain": """---
skill_id: "classify_domain"
version: "7.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "pandas"]
depends_on: ["profile_tabular"]
produces: ["data/01_ingested/domain_classification.json"]
complexity: "intermediate"
---

# Skill: Research Domain Classification

## Purpose
Analyze data structure, variable names, and value patterns to classify the scientific domain and auto-select appropriate analytical pipelines.

## When to Use
- After profiling, before method routing
- When domain is unknown or ambiguous
- To validate researcher-specified domain

## When NOT to Use
- Domain explicitly specified by researcher with high confidence
- Data is synthetic or benchmark (no real domain)

## Decision Protocol

### Classification by Data Signatures
| Domain | Key Variable Patterns | Structural Signals |
|--------|----------------------|-------------------|
| **Epidemiology** | patient_id, diagnosis, ICD-10, survival_time, event_status, bmi, bp, age | Binary disease outcome, time-to-event, comorbidity counts |
| **Econometrics** | firm_id, state, year, gdp, wage, price, cpi, employment | Panel structure (entity × time), instrumental variables |
| **Psychology** | participant_id, scale_score, likert, cronbach_alpha, condition | Repeated measures, randomization groups, validated scales |
| **Genomics** | gene_id, chromosome, position, expression, fold_change, p_value, fdr | Thousands of features (genes), few samples, multiple testing |
| **NLP/Text** | text, tokens, sentiment, topic, embedding, length | High-variance text columns, word frequencies, document IDs |
| **Ecology** | species, site, latitude, longitude, temperature, abundance, richness | Spatial coordinates, species counts, environmental covariates |
| **Finance** | ticker, date, return, volume, price, market_cap, beta | Time series, panel of firms, risk factors |
| **Education** | student_id, school_id, test_score, grade, intervention | Hierarchical (students within schools), pre/post measures |

## Execution Protocol

### Step 1: Signal Extraction
- Extract column name tokens (split on underscores, camelCase)
- Match tokens against domain keyword dictionaries
- Analyze value patterns: ranges, distributions, cardinality
- Detect structural patterns: panel, cross-sectional, hierarchical, time series

### Step 2: Scoring
- For each domain, compute match score:
  - Keyword matches in column names (weight: 0.4)
  - Value pattern matches (weight: 0.3)
  - Structural pattern matches (weight: 0.3)
- Normalize scores to [0, 1]

### Step 3: Classification
- Primary domain: highest scoring domain (score > 0.3 required)
- Secondary domain: if second-highest score within 0.15 of primary
- If no domain exceeds 0.3: classify as "general/multidisciplinary"

### Step 4: Pipeline Recommendation
- Map classified domain to default skill set
- Map to reporting standard (STROBE, APA, AEA, etc.)
- Map to preferred visualizations
- Map to significance conventions

## Diagnostics & Interpretation

| Confidence Score | Interpretation | Action |
|-----------------|----------------|--------|
| > 0.7 | Strong domain match | Use domain-specific pipeline |
| 0.4 - 0.7 | Moderate match | Use domain pipeline with manual review |
| 0.3 - 0.4 | Weak match | Present options to researcher |
| < 0.3 | No clear domain | Use general statistical pipeline |

## Output Specification
- `data/01_ingested/domain_classification.json`: primary domain, confidence scores for all domains, secondary domain (if applicable), recommended skill set, reporting standard

## Validation Checks
- [ ] Primary domain score > 0.3
- [ ] All domain scores sum to ≤ number of domains
- [ ] Recommended skills exist in skill registry
- [ ] Classification logged with rationale
""",
    "detect_missingness": """---
skill_id: "detect_missingness"
version: "7.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "pandas", "numpy", "scipy"]
depends_on: ["profile_tabular"]
produces: ["data/01_ingested/missingness_report.json"]
complexity: "intermediate"
---

# Skill: Missing Data Mechanism Detection & Strategy Selection

## Purpose
Diagnose the mechanism of missingness (MCAR, MAR, MNAR) and recommend appropriate handling strategies based on pattern, proportion, and mechanism.

## When to Use
- After profiling reveals missing data
- Before any analysis that requires complete cases
- When > 5% of any analysis variable is missing

## When NOT to Use
- Dataset has zero missing values
- Missingness is by design (e.g., skip patterns in surveys)

## Decision Protocol

### Missingness Mechanism
```
IF Little's MCAR test p > 0.05 → MCAR (missing completely at random)
ELIF missingness predictable from observed data → MAR (missing at random)
ELIF missingness depends on the missing value itself → MNAR (missing not at random)
ELSE → Assume MAR (conservative default)
```

### Strategy Selection by Mechanism
| Mechanism | Missing < 5% | Missing 5-20% | Missing > 20% |
|-----------|-------------|---------------|---------------|
| MCAR | Complete-case | Multiple imputation | Multiple imputation + sensitivity |
| MAR | Complete-case | Multiple imputation (MICE) | Multiple imputation + pattern-mixture |
| MNAR | Complete-case | Selection models | Pattern-mixture + sensitivity analysis |

## Execution Protocol

### Step 1: Missingness Pattern Mapping
- Compute missingness matrix: binary indicator per cell
- Visualize: heatmap or `missingno` matrix plot
- Compute pairwise missingness: which variables are missing together
- Identify monotone patterns (if A missing → B also missing)

### Step 2: Quantify Missingness
- Per-variable: count, proportion, 95% CI for proportion
- Overall: total missing cells / total cells
- By subgroup: missing rate stratified by each categorical variable
- Flag variables exceeding 20% missing

### Step 3: Mechanism Testing
**Little's MCAR Test** (N < 5000):
- Null hypothesis: data is MCAR
- If p < 0.05: reject MCAR → data is MAR or MNAR

**Missingness Correlation:**
- For each pair of variables, correlate missingness indicators
- Significant correlations suggest MAR (missingness in A depends on observed B)

**Pattern Analysis:**
- Compare distributions of observed vs missing cases for each variable
- If distributions differ systematically → MAR or MNAR

### Step 4: Strategy Recommendation
Based on mechanism + proportion, recommend:
1. **Complete-case analysis**: only if MCAR and < 5% missing
2. **Single imputation** (median/mode): only for descriptive stats, never for inference
3. **Multiple imputation (MICE)**: default for MAR, 5-20 imputations
4. **Maximum likelihood**: if using SEM or mixed models
5. **Inverse probability weighting**: if missingness mechanism is well-modeled
6. **Sensitivity analysis**: always for MNAR or > 20% missing

### Step 5: Imputation Quality Checks (if imputing)
- Compare distributions of observed vs imputed values
- Check that imputed values are plausible (within observed range for bounded variables)
- Verify between-imputation variance is reasonable
- Run analysis on each imputed dataset; check result consistency

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| Little's MCAR p > 0.05 | MCAR plausible | Data not MCAR | Use MAR/MNAR methods |
| Missingness correlation | No strong correlations | MAR likely | Include predictors in imputation model |
| Imputed vs observed | Similar distributions | Imputation model misspecified | Add more predictors, change method |
| Between-imputation variance | Reasonable | Too few imputations | Increase m to 20-50 |

### Red Flags
- **> 40% missing on key outcome**: results will be highly uncertain; consider alternative data source
- **Missingness differs by treatment group**: threatens internal validity; must model missingness mechanism
- **MNAR suspected**: any imputation assumes untestable assumptions; report sensitivity bounds
- **Monotone missingness**: dropout pattern; use mixed models or pattern-mixture models

## Domain Conventions

| Domain | Common Missingness Pattern | Preferred Method |
|--------|--------------------------|-----------------|
| Clinical trials | Dropout (MNAR) | Mixed models, pattern-mixture |
| Survey research | Item nonresponse (MAR) | MICE with auxiliary variables |
| Longitudinal | Attrition (MAR/MNAR) | FIML, multiple imputation |
| EHR data | Informative missingness (MNAR) | Selection models, sensitivity analysis |

## Reporting Template
> "Missing data was assessed across [N] variables. Overall missingness was [percentage]%. Little's MCAR test [was/was not] significant (p = [value]), suggesting data were [MCAR/MAR]. Missingness was handled using [method] with [details]. Sensitivity analysis using [alternative method] yielded [consistent/divergent] results."

## Output Specification
- `data/01_ingested/missingness_report.json`: mechanism classification, per-variable missingness, pattern matrix, recommended strategy, imputation parameters

## Validation Checks
- [ ] Mechanism classified (MCAR/MAR/MNAR with rationale)
- [ ] Strategy recommended matching mechanism and proportion
- [ ] No variable with > 20% missing left unaddressed
- [ ] If imputed: quality checks performed and logged
""",
    "profile_genomic": """---
skill_id: "profile_genomic"
version: "7.0.0"
category: "data"
domain_compatibility: ["genomics", "bioinformatics"]
required_tools: ["python", "pandas", "numpy", "scipy"]
depends_on: ["profile_tabular"]
produces: ["data/01_ingested/genomic_profile.json"]
complexity: "advanced"
---

# Skill: Genomic Data Profiling

## Purpose
Profile genomic data (gene expression, variant calls, sequencing data) to understand data quality, batch effects, normalization status, and biological signal.

## When to Use
- Data contains gene-level measurements (expression, methylation, variants)
- Before differential expression, enrichment, or genomic modeling
- When merging genomic datasets from multiple sources

## When NOT to Use
- Data is clinical/phenotypic only (no molecular measurements)
- Data is already processed through standard QC pipeline

## Execution Protocol

### Step 1: Data Structure Identification
- Identify data type: RNA-seq counts, microarray intensity, variant calls, methylation beta values
- Determine: genes (rows) × samples (columns) or vice versa
- Verify gene identifiers: Ensembl IDs, gene symbols, RefSeq
- Check for duplicate gene entries

### Step 2: Quality Metrics (RNA-seq)
- Library size per sample: total reads, distribution
- Gene detection rate: genes with count > 0 per sample
- Mitochondrial gene proportion: high % indicates poor quality
- Ribosomal RNA proportion: high % indicates poor depletion
- GC content bias: correlation between GC% and expression

### Step 3: Normalization Assessment
- Detect if data is normalized: check for non-integer values, log-transformed range
- If raw counts: recommend TMM (edgeR) or DESeq2 median-of-ratios
- If log-transformed: verify base (log2 vs natural log)
- Check for zero-inflation: proportion of zero counts per gene and per sample

### Step 4: Batch Effect Detection
- If batch information available: compare distributions across batches
- PCA: color by batch vs biological condition
- If batch clusters separately from biology: batch effect present
- Quantify: proportion of variance explained by batch

### Step 5: Biological Signal Assessment
- Sample clustering: do biological replicates cluster together?
- Differential expression pilot: top variable genes separate conditions?
- Outlier samples: samples that don't cluster with any group

### Step 6: Multiple Testing Context
- Count of genes/features: determines multiple testing burden
- Expected proportion of true positives (π₀ estimation)
- Recommend FDR method: Benjamini-Hochberg (default), Storey's q-value

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| Library size CV < 0.3 | Consistent sequencing depth | Variable depth | Normalize for library size |
| Batch PCA | Biological clustering | Batch-driven clustering | Apply ComBat or removeBatchEffect |
| Replicate correlation | r > 0.9 | Poor reproducibility | Investigate sample quality |
| Zero proportion | < 80% for RNA-seq | Excessive zeros | Consider zero-inflated models |

### Red Flags
- **Gene symbols confused with dates** (SEPT2, MARCH1): common Excel conversion error; use Ensembl IDs
- **Negative expression values**: already log-transformed with offset; verify transformation
- **All samples identical**: technical replicate or data copy error
- **Chromosome identifiers missing**: cannot perform genomic context analysis

## Output Specification
- `data/01_ingested/genomic_profile.json`: data type, quality metrics, normalization status, batch effect assessment, biological signal indicators

## Validation Checks
- [ ] Gene identifiers are valid and non-duplicate
- [ ] Sample count matches metadata
- [ ] Normalization status determined
- [ ] Batch effect assessed (if batch info available)
""",
    "detect_outliers": """---
skill_id: "detect_outliers"
version: "7.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "pandas", "numpy", "scipy"]
depends_on: ["profile_tabular"]
produces: ["data/01_ingested/outlier_report.json"]
complexity: "intermediate"
---

# Skill: Outlier Detection & Characterization

## Purpose
Identify, classify, and characterize outliers using multiple complementary methods to distinguish data errors from legitimate extreme values.

## When to Use
- After profiling, before any modeling
- When descriptive stats show extreme skewness or kurtosis
- When domain knowledge suggests plausible value bounds

## When NOT to Use
- Data is already cleaned and validated
- Sample size < 20 (outlier tests unreliable)
- All values are categorical/nominal

## Decision Protocol

### Method Selection
| Data Distribution | Primary Method | Secondary Method |
|-------------------|---------------|-------------------|
| Approximately normal | Z-score (|z| > 3) | Grubbs' test |
| Skewed or unknown | IQR fence (1.5× or 3×) | Modified Z-score (MAD) |
| Multivariate | Mahalanobis distance | Isolation Forest |
| Time series | Rolling IQR | STL decomposition residuals |
| Small sample (N < 30) | Dixon's Q test | Visual inspection only |

## Execution Protocol

### Step 1: Univariate Detection
**IQR Method (default, robust to non-normality):**
- Q1, Q3 = 25th, 75th percentiles
- IQR = Q3 - Q1
- Lower fence = Q1 - 1.5×IQR (mild), Q1 - 3×IQR (extreme)
- Upper fence = Q3 + 1.5×IQR (mild), Q3 + 3×IQR (extreme)
- Flag values beyond fences; classify as mild or extreme

**Modified Z-Score (MAD-based, more robust):**
- MAD = median(|Xi - median(X)|)
- Mi = 0.6745 × (Xi - median) / MAD
- Flag |Mi| > 3.5

**Z-Score (only if approximately normal):**
- Flag |z| > 3 for outliers, |z| > 4 for extreme
- Verify normality first (Shapiro-Wilk or visual Q-Q)

### Step 2: Multivariate Detection
- Compute Mahalanobis distance: D² = (x - μ)' Σ⁻¹ (x - μ)
- Compare to χ²(p) critical value at α = 0.001
- Flag observations exceeding critical value
- Alternative: Isolation Forest with contamination=0.05

### Step 3: Contextual Classification
For each flagged outlier, classify:
- **Data error**: impossible value (negative age, BMI > 100), typo (decimal shift), duplicate entry
- **Legitimate extreme**: plausible but rare (income > $1M, age > 90)
- **Novel observation**: represents a distinct subpopulation
- **Measurement artifact**: instrument saturation, detection limit

### Step 4: Impact Assessment
- Compute statistics with and without outliers
- Compare: mean shift %, SD change %, correlation changes
- If outlier removal changes conclusions → report both versions
- Never silently drop outliers; always document

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| Outlier proportion | < 5% of observations | Systematic issue | Investigate data collection process |
| Single-method flag | Flagged by ≥ 2 methods | Confirmed outlier | Classify and document |
| Influence check | Cook's D < 4/n | Influential point | Report sensitivity analysis |

### Red Flags
- **> 10% flagged as outliers**: method too sensitive or data fundamentally non-standard; widen thresholds
- **All outliers in one subgroup**: subgroup may have different data-generating process; stratify analysis
- **Outliers drive the entire effect**: effect disappears without them → report as exploratory only
- **Impossible values**: data error → correct if source available, otherwise exclude with documentation

## Domain Conventions

| Domain | Plausible Bounds | Common Outlier Sources |
|--------|-----------------|----------------------|
| Clinical | HR: 20-300, BP: 40-300, Temp: 30-45°C | Unit errors (lb vs kg), decimal shifts |
| Finance | Returns: -100% to +1000%, Volume > 0 | Flash crashes, data feed errors |
| Survey | Likert: 1-5, Age: 0-120 | Straight-lining, satisficing responses |
| Genomics | Expression: ≥ 0, p-value: [0,1] | Batch effects, probe failures |

## Reporting Template
> "Outlier detection was performed using [method] on [N] variables. [Count] observations ([percentage]%) were flagged as outliers, of which [count] were classified as data errors and [count] as legitimate extreme values. Sensitivity analysis showed that excluding outliers changed the mean of [variable] by [percentage]% but did not alter the direction of [key finding]."

## Output Specification
- `data/01_ingested/outlier_report.json`: per-variable outlier counts, flagged row indices, classification, impact assessment

## Validation Checks
- [ ] At least two detection methods applied
- [ ] Each outlier classified (error/legitimate/novel/artifact)
- [ ] Impact assessment computed
- [ ] No outliers silently dropped
""",
    "smart_imputer": """---
skill_id: "smart_imputer"
version: "1.0.0"
category: "data"
depends_on: ["detect_missingness", "profile_tabular"]
produces: ["02_experiments/<exp>/outputs/analysis/imputation_diagnostics.json"]
complexity: "standard"
---

# Skill: Smart Imputer

## Purpose
Handle missing data with mechanism-appropriate imputation. Replaces generic missingness handling with targeted strategies.

---

## Protocol

### Step 1: Diagnose Mechanism
Use `detect_missingness` output. Classify each variable's missingness as MCAR, MAR, or MNAR. If unknown, default to MAR (conservative).

### Step 2: Select Strategy by Mechanism × Proportion

| Mechanism | < 5% missing | 5-20% missing | > 20% missing |
|-----------|-------------|---------------|---------------|
| **MCAR** | Median/mode fill for descriptive; listwise deletion for analysis | MICE with 5 imputations | MICE with 20 imputations + sensitivity analysis |
| **MAR** | MICE with 5 imputations | MICE with 10-20 imputations | MICE + pattern-mixture model + sensitivity bounds |
| **MNAR** | Listwise deletion + sensitivity bounds | Selection model or pattern-mixture | Pattern-mixture + wide sensitivity bounds; flag results as highly uncertain |

### Step 3: MCAR — Simple Imputation
For <5% missing: median (continuous) or mode (categorical). Use `sklearn.impute.SimpleImputer(strategy='median')`. Only for descriptive stats — never for inference. For analysis: listwise deletion.

### Step 4: MAR — MICE (Multiple Imputation by Chained Equations)
Use `sklearn.impute.IterativeImputer` or `statsmodels` MICE. Steps:
1. Build imputation model for each variable with missing values, using all other variables as predictors
2. Run 5-20 imputations (more for higher missingness)
3. Analyze each imputed dataset separately
4. Combine results using Rubin's rules: pooled estimate = mean of estimates, pooled SE = sqrt(mean(SE²) + (1+1/m)×between-imputation variance)

Include auxiliary variables (variables correlated with missingness) in the imputation model even if not in the analysis model.

### Step 5: MNAR — Pattern Mixture / Sensitivity Bounds
MNAR requires untestable assumptions. Use:
- **Pattern mixture model**: stratify by missingness pattern, estimate within each stratum, combine with weights
- **Sensitivity bounds**: compute best-case and worst-case scenarios by imputing at extreme values (e.g., min and max for continuous)
- **Selection model**: jointly model outcome and missingness mechanism (requires strong assumptions)

Always report sensitivity bounds alongside point estimates.

### Step 6: Diagnostics
After imputation, validate:
1. Compare distributions of observed vs imputed values (should be similar but not identical)
2. Check imputed values are plausible (within observed range for bounded variables)
3. Verify between-imputation variance is reasonable (too low = model overconfident; too high = too few imputations)
4. Run analysis on each imputed dataset; check result consistency

### Step 7: Output
Save to `02_experiments/<exp>/outputs/analysis/imputation_diagnostics.json`:
- Mechanism classification per variable
- Imputation method used, number of imputations
- Before/after missingness proportions
- Distribution comparison (observed vs imputed)
- Rubin's rules pooled estimates (if MICE)
- Sensitivity bounds (if MNAR)

---

## Validation
- [ ] Mechanism classified before imputation
- [ ] Strategy matches mechanism × proportion table
- [ ] MICE uses ≥5 imputations
- [ ] Rubin's rules applied for pooled estimates
- [ ] Diagnostics: observed vs imputed distributions compared
- [ ] MNAR: sensitivity bounds reported
- [ ] Imputation diagnostics JSON saved
""",
    "profile_temporal": """---
skill_id: "profile_temporal"
version: "7.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "pandas", "numpy"]
depends_on: ["profile_tabular"]
produces: ["data/01_ingested/temporal_profile.json"]
complexity: "intermediate"
---

# Skill: Temporal Data Profiling

## Purpose
Profile time-indexed data to understand temporal structure, frequency, seasonality, gaps, and stationarity properties.

## When to Use
- Dataset has datetime columns
- Data is time series or panel (longitudinal)
- Before time series analysis or forecasting

## When NOT to Use
- No temporal columns exist
- Time is not analytically relevant (e.g., timestamp is metadata only)

## Execution Protocol

### Step 1: Temporal Column Identification
- Identify all datetime columns
- Determine primary time index (most granular, most complete)
- Identify secondary time indices (e.g., event dates, cohort dates)

### Step 2: Temporal Range & Span
- Min/max dates, total span (days, months, years)
- Number of unique time points
- Time point frequency: infer from median interval (daily, weekly, monthly, quarterly, annual, irregular)

### Step 3: Gap Detection
- Compute intervals between consecutive time points
- Identify gaps: intervals > 2× median interval
- Classify gaps: expected (weekends, holidays) vs unexpected
- Report gap count, total gap duration, largest gap

### Step 4: Seasonality Assessment
- Decompose by time unit: day-of-week, month-of-year, quarter
- Compute mean value per time unit
- Visualize: seasonal plot, autocorrelation function (ACF)
- Flag strong seasonal patterns (coefficient of variation across seasons > 0.20)

### Step 5: Stationarity Screening
- Visual inspection: rolling mean and rolling SD plots
- Augmented Dickey-Fuller test: null = unit root (non-stationary)
- If non-stationary: determine differencing order (d) needed
- Check for structural breaks: Chow test or visual inspection

### Step 6: Panel Structure (if applicable)
- Identify cross-sectional units (e.g., firms, individuals, regions)
- Compute: N units, T time points, balanced vs unbalanced panel
- For unbalanced: entry/exit patterns, attrition rate
- Gap analysis per unit

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| ADF p < 0.05 | Stationary | Non-stationary series | Difference or use ARIMA/SARIMAX |
| Gap frequency | < 5% of intervals | Irregular sampling | Interpolate or use irregular-time models |
| Seasonality strength | CV < 0.20 across seasons | Strong seasonality | Include seasonal terms or use SARIMAX |
| Panel balance | Balanced or > 80% complete | High attrition | Use unbalanced panel methods |

### Red Flags
- **Non-chronological ordering**: sort by time index before any analysis
- **Multiple time zones**: standardize to single timezone (UTC preferred)
- **Future dates in historical data**: data entry error or projection; flag
- **Duplicate timestamps**: aggregate or investigate (multiple events at same time)

## Output Specification
- `data/01_ingested/temporal_profile.json`: time range, frequency, gaps, seasonality assessment, stationarity test results, panel structure (if applicable)

## Validation Checks
- [ ] Time index is monotonically non-decreasing
- [ ] Date range is plausible (no year 1900 or 2100 unless expected)
- [ ] Frequency is classified
- [ ] Stationarity test result recorded
""",
    "data_validator_pandera": """---
skill_id: "data_validator_pandera"
version: "1.0.0"
category: "data"
depends_on: ["profile_tabular"]
produces: ["02_experiments/<exp>/outputs/analysis/validation_report.json"]
complexity: "standard"
---

# Skill: Data Validator (Pandera)

## Purpose
Complete Pandera-based schema validation. Auto-generate schema from profile, run validation, report exact failures, suggest corrections.

---

## Protocol

### Step 1: Auto-Generate Schema from Profile
Read `profile_tabular.json` output. Build a `pandera.DataFrameSchema`:
- **Numeric columns**: `Column(pandera.Float, checks=[InRange(min=profile_min, max=profile_max)], nullable=has_nulls)`
- **Categorical columns**: `Column(pandera.String, checks=[Isin(categories=observed_values)], nullable=has_nulls)`
- **Boolean columns**: `Column(pandera.Bool, nullable=False)`
- **Datetime columns**: `Column(pandera.DateTime, nullable=has_nulls)`
- **Identifier columns**: `Column(..., unique=True, nullable=False)`

### Step 2: Run Validation
Call `schema.validate(df, lazy=True)` to collect ALL errors (not just the first). Wrap in try/except `pandera.errors.SchemaErrors`.

### Step 3: Report Failures
For each failure, report:
- Column name
- Constraint violated (e.g., "value 150 exceeds max 100")
- Number of violating rows
- Sample of violating values (first 5)
- Row indices of violations

### Step 4: Generate Correction Suggestions
For each failure type, suggest a fix:
- **Range violation**: expand range to include observed values, or flag as outliers
- **Category violation**: add new category to allowed set, or recode to "other"
- **Type mismatch**: coerce type if safe (e.g., "1" → 1), otherwise flag
- **Null violation**: mark column as nullable, or investigate source of nulls
- **Uniqueness violation**: check for duplicate records, or remove unique constraint

### Step 5: Output
Save validation report to `02_experiments/<exp>/outputs/analysis/validation_report.json`:
- Schema used (serialized)
- Per-column pass/fail
- Violation details with samples
- Correction suggestions
- Overall verdict: PASS / WARN (non-critical failures) / FAIL (critical failures)

---

## Pandera Schema Template

```python
import pandera as pa
from pandera import Column, Check

schema = pa.DataFrameSchema({
    "age": Column(pa.Float, checks=[pa.Check.in_range(0, 120)], nullable=True),
    "income": Column(pa.Float, checks=[pa.Check.in_range(0, None)], nullable=True),
    "gender": Column(pa.String, checks=[pa.Check.isin(["M", "F", "Other"])], nullable=False),
    "score": Column(pa.Float, checks=[pa.Check.in_range(0, 100)], nullable=False),
    "participant_id": Column(pa.String, unique=True, nullable=False),
})
```

---

## Validation
- [ ] Schema auto-generated from profile_tabular
- [ ] Validation runs with lazy=True (collects all errors)
- [ ] Each failure reports column, constraint, count, sample values
- [ ] Correction suggestions provided for each failure
- [ ] Overall verdict assigned (PASS/WARN/FAIL)
- [ ] Report saved as JSON
""",
    "parse_papers": """---
skill_id: "parse_papers"
version: "1.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "playwright", "beautifulsoup4"]
depends_on: []
produces: ["inputs/context/paper_summaries/"]
complexity: "intermediate"
---

# Skill: Parse Papers from URLs or PDFs

## Purpose
Extract text, abstracts, and key sections from papers via URLs (using Playwright for JS-rendered pages) or local PDFs, producing structured summaries for the research context.

## When to Use
- User provided URLs to papers in `inputs/context/`
- Papers are behind JS-rendered sites (ScienceDirect, Springer, etc.)
- Need to extract abstracts/findings from paper PDFs
- Building literature context from web sources

## When NOT to Use
- Papers already provided as PDFs in `inputs/papers/`
- Only DOI/bibliographic data needed

## Execution Protocol

### Step 1: Source Discovery
- Scan `inputs/context/` for files containing URLs (`.md`, `.txt`, `.links`)
- Scan `inputs/papers/` for PDF files
- Collect all sources into a list

### Step 2: URL Parsing (Playwright)
For each URL:
- Launch Playwright browser (headless)
- Navigate to URL, wait for page load
- Extract: title, abstract, authors, year, journal, DOI
- If paywalled: extract abstract only (usually visible)
- Save as: `inputs/context/paper_summaries/{sanitized_title}.md`

```python
from playwright.sync_api import sync_playwright

def parse_paper_url(url, output_path):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)

        # Extract common paper metadata
        title = page.query_selector("h1, .article-title, #title")
        abstract = page.query_selector(".abstract, #abstract, .summary")

        content = {
            "url": url,
            "title": title.inner_text() if title else "",
            "abstract": abstract.inner_text() if abstract else "",
        }

        # Save summary
        with open(output_path, "w") as f:
            f.write(f"# {content['title']}\\n\\n")
            f.write(f"**URL**: {url}\\n\\n")
            f.write(f"## Abstract\\n\\n{content['abstract']}\\n")

        browser.close()
```

### Step 3: PDF Parsing
For each PDF in `inputs/papers/`:
- Extract text using `pypdf` or `pdfplumber`
- Identify: title, abstract, section headers, conclusion
- Save as: `inputs/context/paper_summaries/{filename}.md`

### Step 4: Summary Index
Create `inputs/context/paper_summaries/INDEX.md` listing all parsed papers with:
- Title, source (URL or PDF), abstract, key findings (if extractable)

## Diagnostics

| Check | Pass | Fail → Action |
|-------|------|---------------|
| URL loads | Page loads in 30s | URL may be dead; log and skip |
| Abstract found | Abstract extracted | Page structure unknown; save full text |
| PDF readable | Text extracted | Scanned PDF; needs OCR (skip) |

## Output Specification
- `inputs/context/paper_summaries/`: individual paper summaries
- `inputs/context/paper_summaries/INDEX.md`: index of all parsed papers

## Validation Checks
- [ ] Each source (URL or PDF) produces a summary file
- [ ] Summaries contain at least title and abstract
- [ ] INDEX.md lists all summaries
- [ ] Failed sources logged with reason
""",
    "compute_hashes": """---
skill_id: "compute_hashes"
version: "7.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "hashlib"]
depends_on: []
produces: ["data/01_ingested/hash_manifest.json"]
complexity: "basic"
---

# Skill: Data Integrity Hashing

## Purpose
Compute and record cryptographic hashes for all data files to enable integrity verification, provenance tracking, and reproducibility auditing.

## When to Use
- Immediately after data ingestion
- After any data transformation
- Before and after analysis runs
- When sharing data between systems

## When NOT to Use
- Files are ephemeral/temporary
- Data is streaming (use checkpoint hashing instead)

## Execution Protocol

### Step 1: File Discovery
- Scan `data_raw/` and `data/` directories recursively
- Identify all data files: CSV, Parquet, Excel, JSON, SAS, SPSS, Stata, Feather
- Exclude: code files, documentation, hidden files

### Step 2: Hash Computation
- Compute SHA-256 for each file
- For files > 1GB: read in 8192-byte chunks to avoid memory overflow
- Record: file path, hash, file size, modification timestamp

### Step 3: Manifest Generation
- Create JSON manifest with all file entries
- Include metadata: computation timestamp, tool version, OS
- Sort entries by file path for deterministic output

### Step 4: Verification (if previous manifest exists)
- Compare current hashes to previous manifest
- Identify: new files, modified files, deleted files, unchanged files
- Report delta summary

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| Hash matches previous | File unchanged | Investigate modification source |
| File size consistent | Size matches expectation | Check for truncation or corruption |
| All files accounted | No unexpected changes | Verify intentional vs accidental |

## Output Specification
- `data/01_ingested/hash_manifest.json`: file paths, SHA-256 hashes, sizes, timestamps, delta from previous manifest

## Validation Checks
- [ ] All data files hashed
- [ ] Hashes are reproducible (recompute matches)
- [ ] Manifest is valid JSON
- [ ] Delta correctly identifies changes
""",
    "onboarding_guide": """---
skill_id: "onboarding_guide"
version: "1.0.0"
category: "core"
depends_on: []
produces: ["user understanding"]
complexity: "quick"
---

# Skill: Onboarding Guide

## Purpose
Walk a new user through their first analysis in 5 steps. No pipeline knowledge required — just describe your research in plain English.

---

## 5-Step First Analysis

### Step 1: Drop Your Data
Place your data file(s) in `00_inputs/raw_data/`. Supported formats: CSV, TSV, Parquet, Excel (.xlsx), Stata (.dta), SPSS (.sav). No preprocessing needed — we handle encoding, delimiters, and type detection automatically.

### Step 2: Fill in 3 Required Fields
Open `inputs/intake.md` and fill in only these 3 fields:
- **Title**: What is this project called?
- **Question**: What do you want to find out?
- **Outcome variable**: What is the main thing you're measuring?

Everything else is optional. The system will infer domain, predictors, and methods from your data.

### Step 3: Say "Analyze My Data"
That's it. You don't need to know about profiling, assumption checking, or method selection. The system will:
1. Profile your data automatically
2. Detect variable types and missingness
3. Route to appropriate analysis methods
4. Run the analysis
5. Generate figures and tables

### Step 4: Review Key Findings
Open `03_synthesis/key_findings.md`. This contains:
- Summary of what the data shows
- Statistical results with effect sizes and confidence intervals
- Key figures with interpretations
- Limitations and caveats

### Step 5: Ask Follow-Up Questions
Not satisfied? Ask in plain English:
- "Why did we get this result?" → investigates
- "Try a different method" → switches methods
- "What if we control for X?" → adds variables
- "Check if this holds up" → robustness checks
- "How does this compare to literature?" → literature comparison
- "What else is in the data?" → exploratory analysis

---

## You Don't Need to Know the Pipeline

The system handles:
- Data profiling and quality checks
- Statistical assumption testing
- Method selection and routing
- Figure generation (colorblind-safe, publication-ready)
- Manuscript compilation
- Citation verification
- Audit and validation

Just describe your research. We handle the rest.

---

## Validation
- [ ] User placed data in `00_inputs/raw_data/`
- [ ] User filled 3 required intake fields
- [ ] User triggered analysis
- [ ] Key findings generated
- [ ] User able to ask follow-up questions
""",
    "synthesize_parallel_results": """# Synthesize Parallel Results

## Purpose
Merges outputs from parallel analysis runs, verifies results integrity, detects potential logical or empirical conflicts, and updates the central research map and state ledger.

## Protocol

### 1. Integrity Verification
Before merging, confirm that all parallel tasks executed successfully:
- Read the parallel execution results JSON (`*_results.json`).
- Verify that every worker task has a `success: true` flag.
- Compute SHA-256 hashes of generated task outputs and cross-check against recorded values (if available in lineage logs).

### 2. Conflict Detection
Analyze the findings from the independent question directories (`reports/analysis/q{N}/`):
- **Contradictory Effects:** Check if Q{N} and Q{M} analyze the same outcome variable and predictors but yield contradictory coefficient signs or directional claims.
- **Varying Significance:** Detect cases where the same effect is highly significant in one subset/specification but non-significant in another, and log this difference.
- **Robustness Discrepancies:** Detect if a model passes sensitivity tests in one worker but fails in another.
- **Reporting:** If conflicts are detected, flag them clearly in the combined output report as critical warnings.

### 3. Consolidation & Merging
- Merge individual question result JSON files into a single, unified `reports/analysis/combined_results.json`.
- Structure the consolidated payload by research question ID.
- Include metadata about the parallel run (execution date, total elapsed time, success rate).

### 4. Research Map Update
Update `reports/baseline/research_map.json` or `docs/manifest.json`:
- Mark status of analyzed questions as `completed`.
- Populate outcome findings, effect sizes, p-values, and confidence intervals under each question.

### CLI Reference
```bash
python -m research_copilot.utils.synthesize_results --results-file <results_json_path>
```
""",
    "auto_debug": """# Auto-Debugging Sandbox

## Purpose
When any Python script fails, automatically capture the error, diagnose the issue, rewrite only the failing function, and retry. Max 3 iterations before creating a dead end entry.

## Invocation
Triggered automatically when a script executed by any agent exits with a non-zero status code.

## Protocol

### Step 1: Capture Failure Context
When a script fails, collect:
1. **Full traceback** — complete Python traceback from stderr
2. **Last 20 lines of stdout** — what was printed before the crash
3. **Script content** — full source of the failing script
4. **Environment info** — Python version, installed packages, working directory
5. **Input files** — list of files the script was reading (from the script's open() calls)

### Step 2: Diagnose the Error
Classify the error type:
- `ImportError` — missing package or wrong module name
- `FileNotFoundError` — wrong file path or missing input
- `KeyError/IndexError` — wrong column name or array index
- `ValueError` — invalid data type or shape mismatch
- `TypeError` — wrong argument type
- `SyntaxError` — code syntax issue
- `RuntimeError` — convergence failure, memory error, etc.

### Step 3: Build Debug Prompt
Bundle the context into a structured debug prompt:
```
DEBUG REQUEST
=============
Script: {script_path}
Error Type: {error_type}
Traceback:
{full_traceback}

Last 20 lines of stdout:
{stdout_tail}

Script content:
{full_script}

Environment:
- Python: {python_version}
- Working directory: {cwd}
- Key packages: {package_versions}

TASK: Fix ONLY the failing function. Do NOT rewrite the entire script.
Return the corrected function code only.
```

### Step 4: LLM Rewrites the Failing Function
- Extract the failing function name from the traceback
- Read only that function's source code
- Generate a corrected version
- Replace ONLY that function in the script (not the entire file)

### Step 5: Retry Execution
- Run the script again with the fix applied
- Capture result (success or new error)
- If success: log the fix, continue pipeline
- If new error: go back to Step 1 (max 3 iterations)

### Step 6: Max Iterations Reached
If still failing after 3 attempts:
1. Create dead end entry: `docs/dead_ends/debug_{script_name}_{timestamp}.md`
2. Document: what was tried, what errors persisted, what manual intervention is needed
3. Alert user with the full debug log
4. Do NOT continue pipeline with broken script

### Step 7: Log All Debug Attempts
Every debug attempt is logged in `docs/dead_ends/debug_{script_name}_{timestamp}.md`:
```
---
Script: {script_path}
Attempt: 1/3
Error Type: {error_type}
Original Error: {traceback_snippet}
Fix Applied: {description of change}
Result: {success|new_error}
New Error (if any): {new_traceback}
---
```

## Implementation

### Python Helper: `research_copilot.utils.auto_debug`
```bash
python -m research_copilot.utils.auto_debug --script <path> --max-attempts 3
```

The script:
1. Executes the target script and captures output
2. On failure: parses traceback, identifies failing function
3. Outputs a structured JSON debug bundle for the LLM to process
4. Applies the LLM's fix and retries
5. Logs all attempts

### Debug Bundle JSON Format
```json
{
  "script": "scripts/02_analysis.py",
  "attempt": 1,
  "max_attempts": 3,
  "error_type": "ValueError",
  "traceback": "full traceback text",
  "stdout_tail": "last 20 lines",
  "failing_function": "compute_correlation",
  "failing_line": 47,
  "environment": {
    "python_version": "3.11.5",
    "cwd": "/project/root",
    "packages": {"pandas": "2.2.0", "scipy": "1.12.0"}
  },
  "input_files": ["data/03_analytical/analysis_q1.csv"]
}
```

## Integration

- Called automatically by agents when a script fails
- Also available as a CLI tool: `research debug <script_path>`
- All debug logs are append-only — never overwrite previous attempts
- Successful fixes are recorded in the state ledger
""",
    "cache_manager": """# Cache & Memoization Manager

## Purpose
Enables persistent local caching of web search queries, API calls, paper abstracts, computed statistics, and deterministic LLM sub-calls using a SQLite database. This reduces external API costs, avoids redundant computational steps, and guarantees reproducibility.

## Protocol

### Cache Database Structure
All cached objects are stored in `.research/cache/research_cache.db`.

| Table | Key | Value Schema | TTL / Expiration |
|---|---|---|---|
| **`web_searches`** | `query_hash` (md5 of query) | `{results: [...], timestamp: ISO8601, expires_at: ISO8601}` | 7 days for papers, 1 day for news/general |
| **`api_calls`** | `endpoint_params_hash` | `{response: {...}, timestamp: ISO8601}` | 30 days default (customizable) |
| **`paper_abstracts`** | `doi` (normalized) | `{abstract: "...", title: "...", authors: "...", verified_at: ISO8601}` | Permanent (no expiration) |
| **`computed_stats`** | `data_op_hash` (data hash + operation string) | `{result: {...}, timestamp: ISO8601}` | Permanent / changes if data hash changes |
| **`llm_calls`** | `prompt_hash` | `{response: "...", model: "...", timestamp: ISO8601}` | Permanent (for deterministic prompt/settings) |

### Cache Hit / Miss Workflow
1. **Compute Hash:** Construct the key using a cryptographic hash (MD5 or SHA-256) of the input parameters or content.
2. **Lookup:** Search the target table for the computed key.
3. **Validate Expiration:** 
   - If key exists and `expires_at` (if present) is in the future, return cached content. Increment `cache_hits` in the state ledger (`state.json`).
   - If key exists but is expired, delete the key. Proceed to step 4.
4. **Cache Miss:** Execute the action (web search, compute, API request).
5. **Write Back:** Store the new result, timestamp, and expiration in the database. Increment `cache_misses` in `state.json`.

### CLI Reference
```bash
python -m research_copilot.utils.cache_manager --clear
python -m research_copilot.utils.cache_manager --stats
```
""",
    "minimal_context_loader": """---
skill_id: "minimal_context_loader"
version: "1.0.0"
category: "core"
depends_on: []
produces: []
complexity: "quick"
---

# Skill: Minimal Context Loader

## Purpose
Load only what's needed for each task. Never load all skills or agents at once. Stay under 20k tokens of context per task.

---

## Protocol

### Rule 1: One Skill at a Time
Before any analysis, call `rcp skills <skill_name>` to load exactly 1 skill. Match the skill to the current step. Do NOT load all skills.

### Rule 2: One Agent at a Time
Before invoking an agent, call `rcp agent <agent_name>` to load exactly 1 agent. Do NOT preload multiple agents.

### Rule 3: Load State Once
Read `03_synthesis/state_ledger.json` at the start of each conversation. Use it as the single source of truth for phase, decisions, and file pointers.

### Context Budget

| Resource | Token Cost | When to Load |
|----------|-----------|--------------|
| 1 skill | ~2,000 | Before executing a specific step |
| 1 agent | ~3,000 | Before invoking an agent |
| 1 workflow | ~1,000 | When routing a multi-step task |
| State ledger | ~2,000 | At conversation start (once) |
| **Total per task** | **<20,000** | **Hard limit** |

### Loading Order

1. Read state ledger (~2k tokens) — understand current phase
2. Load 1 skill (~2k tokens) — the one needed for the next step
3. If agent needed: load 1 agent (~3k tokens)
4. Execute step
5. Release context: skill context is discarded after step completes
6. Repeat for next step

### Anti-Patterns
- Loading all 40+ skills at once (~80k tokens) — NEVER do this
- Pre-loading agents you might need later — load on demand
- Re-reading state ledger every step — read once, cache in memory
- Loading full literature corpus — use knowledge graph queries instead

### When to Break the Rule
Only load multiple skills simultaneously when a single step explicitly requires cross-skill coordination (e.g., visualization + statistical test in one figure). Maximum 4 skills at once.
""",
    "parse_research_brief": """# Skill: Parse Research Brief

> Converts a free-form paragraph description of research into a structured intake form.

## Purpose
When a user pastes a paragraph description of their research (voice transcript, email, or free-form text), this skill structures it into a valid intake format that can be used by `research_init`.

---

## Protocol

### Step 1: Read Input Text
1. Accept free-form text from user (pasted paragraph, voice transcript, email body)
2. Save raw input to `inputs/raw_brief.txt`

### Step 2: Extract Project Metadata
Parse the text for:
- **Project title**: Look for phrases like "study on", "research about", "investigating"
- **Researcher name**: Look for "by", "I am", named entities
- **Institution**: Look for university, organization names
- **Domain/field**: Look for discipline keywords (psychology, economics, biology, etc.)

### Step 3: Extract Research Questions
Identify research questions by:
- Sentences ending with "?"
- Phrases like "we want to know", "the goal is to determine", "whether"
- Implicit questions from objectives ("to examine the relationship between X and Y")

For each question, determine:
- **Type**: descriptive, comparative, associational, causal, predictive, exploratory
- **Outcome variable**: What is being measured/predicted
- **Predictor variable**: What is being manipulated/compared
- **Hypothesis**: Directional prediction if stated

### Step 4: Extract Data Information
Look for:
- Data source mentions ("survey data", "experimental data", "archival records")
- Sample size mentions ("N=500", "500 participants")
- Variable mentions ("age", "income", "test scores")
- Data format hints ("Excel file", "CSV", "database")

### Step 5: Extract Context and Constraints
Look for:
- Target output ("journal article", "report", "presentation")
- Timeline/deadline mentions
- Ethics considerations
- Prior research mentions

### Step 6: Generate Structured Intake
Create `inputs/intake.yaml` from extracted information:

```yaml
title: "[extracted title]"
researcher: "[extracted name]"
institution: "[extracted institution]"
domain: "[extracted domain]"
questions:
  - text: "[question 1]"
    type: "[type]"
    hypothesis: "[hypothesis]"
    outcome: "[outcome variable]"
    predictor: "[predictor variable]"
  - text: "[question 2]"
    type: "[type]"
    hypothesis: "[hypothesis]"
    outcome: "[outcome variable]"
    predictor: "[predictor variable]"
data:
  - description: "[data description]"
    format: "[format]"
    estimated_size: "[sample size]"
    variables: ["var1", "var2"]
target_output: "[journal/report/etc.]"
timeline: "[if mentioned]"
notes: "[additional context]"
```

### Step 7: Generate Confidence Report
Create `inputs/brief_parsing_report.json`:

```json
{
  "schema_version": "1.0.0",
  "timestamp": "ISO 8601",
  "source": "inputs/raw_brief.txt",
  "confidence": {
    "title": "HIGH|MEDIUM|LOW",
    "researcher": "HIGH|MEDIUM|LOW|NOT_FOUND",
    "institution": "HIGH|MEDIUM|LOW|NOT_FOUND",
    "domain": "HIGH|MEDIUM|LOW",
    "questions": "HIGH|MEDIUM|LOW",
    "data": "HIGH|MEDIUM|LOW"
  },
  "missing_fields": ["list of fields that could not be extracted"],
  "requires_user_confirmation": true
}
```

### Step 8: Present for Confirmation
1. Show generated intake to user
2. Highlight fields with LOW confidence or NOT_FOUND
3. Ask user to confirm or correct
4. Write confirmed intake to `inputs/intake.yaml` and `inputs/intake.md`

---

## Extraction Heuristics

### Question Type Detection
| Keywords | Type |
|----------|------|
| "how many", "what is the distribution", "describe" | descriptive |
| "compare", "difference between", "versus" | comparative |
| "relationship", "association", "correlation", "linked" | associational |
| "effect of", "impact", "causes", "influence" | causal |
| "predict", "forecast", "will" | predictive |
| "explore", "understand", "patterns" | exploratory |

### Domain Detection
| Keywords | Domain |
|----------|--------|
| "patient", "clinical", "treatment", "disease" | epidemiology |
| "student", "learning", "education", "achievement" | education |
| "market", "stock", "financial", "investment" | finance |
| "gene", "protein", "expression", "sequencing" | genomics |
| "behavior", "cognitive", "psychological", "mental" | psychology |
| "voter", "policy", "election", "political" | political_science |
| "temperature", "climate", "emission", "carbon" | climate_science |
| "social", "community", "inequality", "demographic" | sociology |

---

## Integration
- Called by: User pastes free-form text, or CLI command `research parse-brief`
- Outputs to: `inputs/intake.yaml`, `inputs/intake.md`, `inputs/brief_parsing_report.json`
- Requires: User confirmation before proceeding to `research_init`
""",
    "parallel_orchestrator": """# Parallel Orchestrator

## Purpose
Enables concurrent execution of independent research tasks (such as multiple research questions, sensitivity analysis variants, figure generation, or citation verification batches) to optimize speed and resource utilization while ensuring thread safety and data isolation.

## Protocol

### 1. Independence Assessment
Before executing tasks in parallel, verify that they are independent:
- **No Shared State:** They must not modify the same variables or shared state in memory.
- **No File Contention:** They must write to distinct, isolated file paths.
- **Resources:** Ensure there are sufficient system resources (CPU cores/memory) for the requested `max_workers`.

### 2. Isolated Workspace Allocation
Each parallel worker must operate in an isolated subdirectory to avoid conflicts:
- For research questions: `data/03_analytical/q{N}/` and `reports/analysis/q{N}/`.
- For figure generation: `reports/figures/q{N}/`.
- For table generation: `reports/tables/q{N}/`.

### 3. Execution Setup
Invoke the parallel runner script (`.research/scripts/utils/parallel_runner.py`):
```bash
python -m research_copilot.utils.parallel_runner --tasks <tasks_json_file> --max-workers <num>
```
Tasks must be defined in a JSON file listing the script paths, arguments, and target output directories.

### 4. Concurrency Safety & State Locking
To prevent race conditions during parallel execution:
- **Ledger Writes:** Workers must never write directly to `state.json` or the research log concurrently. All ledger updates must be managed using a file lock mechanism (e.g., `portalocker` or a custom atomic rename-based lock).
- **Execution Log:** Log worker-specific tracebacks and outputs to temporary files inside their isolated workspace.
- **Error Handling:** If any single worker fails, capture its error traceback, log it to the dead ends registry under the worker's context, and mark the overall parallel run status as incomplete.

### 5. Transition to Synthesis
Once all parallel tasks finish execution:
1. Verify completion of all task outputs.
2. Read all worker results.
3. Pass control to the Synthesizer Skill (`synthesize_parallel_results.md`) to verify output integrity, check for contradictions, and merge outputs.
""",
    "token_budget": """# Token Budget Manager

## Purpose
Monitors context window usage and automatically compresses/summarizes earlier context when approaching limits. Never let token overflow silently corrupt outputs.

## Protocol

### Token Tracking
1. Track tokens used per agent invocation
2. Update the global ledger (`state.json`) with current usage via `ResearchLedger.track_tokens()`
3. Default context window: 200,000 tokens (adjustable per model)

### Compression Thresholds

| Usage | Action |
|-------|--------|
| 0-60% | Normal operation, full context available |
| 60-80% | Summarize completed phases into 3-sentence abstracts. Keep only essential skill docs. |
| 80-90% | Flush non-essential skill docs from context. Keep only the active skill being executed. Compress literature review to key findings only. |
| 90-100% | Force checkpoint save. Split into new conversation with state transfer prompt. Include: current phase, state.json summary, last results, next steps. |

### State Transfer Prompt Template
When splitting at 90%+:
```
CONTEXT TRANSFER — Research Copilot Session Continuation

Previous session state:
- Run ID: {run_id}
- Phase: {phase} (step {step})
- Completed checkpoints: {checkpoints}
- Active hypotheses: {hypotheses}
- Last result: {last_result_summary}
- Next step: {next_action}

Continue from here. Do NOT repeat completed work.
```

### Token Estimation
- 1 token ≈ 4 characters for English text
- 1 token ≈ 0.75 words
- Code: 1 token ≈ 2-3 characters
- JSON: count braces, brackets, quotes as overhead

### Implementation for Agents
Before each major output:
1. Estimate tokens in accumulated context
2. Compare against `token_budget.limit` in state.json
3. If threshold exceeded: apply compression rules above
4. Log compression action in state.json errors array with type "token_compression"

### CLI Reference
```bash
research budget          # Show token budget usage by phase
research state           # Shows token budget in ledger summary
```
""",
    "progress_reporter": """---
skill_id: "progress_reporter"
version: "1.0.0"
category: "core"
depends_on: []
produces: ["stdout progress lines"]
complexity: "quick"
---

# Skill: Progress Reporter

## Purpose
Emit machine-parseable progress lines at each major step. Enables real-time feedback without verbose logging. Future UI can render progress bars from these lines.

---

## Protocol

### Step 1: Format Progress Line
Every progress line follows this format:
```
[PHASE: <phase_name> | STEP: <current>/<total> | STATUS: <status_text> | ETA: <estimate>]
```

### Step 2: Emit at Each Step
Call at the start of each major step. Update STATUS as step progresses:
- `starting` — step just began
- `running <subtask>` — actively working
- `complete` — step finished
- `failed: <reason>` — step failed

### Step 3: Phase Step Counts
Know the step count for each phase:
- `research_init`: 5 steps
- `literature_deep`: 7 steps
- `method_route`: 4 steps
- `data_scaffold`: 6 steps
- `execute_analysis`: 8 steps
- `compile_outputs`: 5 steps
- `audit_validate`: 9 steps
- `research_iterate`: variable (report as `X/?`)

### Step 4: ETA Estimation
- `quick` skills: ~30s
- `standard` skills: ~3 min
- `intensive` skills: ~10 min
- Adjust based on actual elapsed time from previous steps

---

## Examples

```
[PHASE: execute_analysis | STEP: 3/8 | STATUS: running assumption_checks | ETA: ~3 min]
[PHASE: execute_analysis | STEP: 3/8 | STATUS: running normality_tests | ETA: ~2 min]
[PHASE: execute_analysis | STEP: 4/8 | STATUS: complete | ETA: ~5 min]
[PHASE: literature_deep | STEP: 2/7 | STATUS: running semantic_scholar_search | ETA: ~1 min]
[PHASE: audit_validate | STEP: 7/9 | STATUS: running claim_trace | ETA: ~4 min]
[PHASE: compile_outputs | STEP: 1/5 | STATUS: starting manuscript_assembly | ETA: ~8 min]
```

---

## Machine Parsing
Line starts with `[PHASE:` and ends with `]`. Fields separated by ` | `. Each field is `KEY: VALUE`.

Regex: `^\\[PHASE: (.+?) \\| STEP: (\\d+)/(\\d+|\\?) \\| STATUS: (.+?) \\| ETA: (.+?)\\]$`

---

## Validation
- [ ] Line format matches `[PHASE: ... | STEP: ... | STATUS: ... | ETA: ...]`
- [ ] Phase name is valid
- [ ] Step numbers are accurate
- [ ] Status is descriptive
- [ ] ETA is reasonable estimate
""",
    "schema_enforcement": """# Skill: Schema Enforcement

> Validates all inter-agent data payloads against Pydantic schemas before acceptance.

## Purpose
Ensure that malformed output from one agent cannot corrupt the next agent's input. Every agent output must validate against a Pydantic schema before being accepted.

---

## Protocol

### Step 1: Load Schema Registry
1. Read `.research/schemas/` directory for available schemas
2. Match current agent/task to appropriate schema
3. Load the Pydantic model for validation

### Step 2: Validate Agent Output
For each agent output:
1. Parse the output into the expected data structure
2. Run validation against the appropriate Pydantic model
3. If validation passes: accept output, proceed
4. If validation fails: reject output, trigger auto-healing

### Step 3: Handle Validation Failures
1. Log validation error to `docs/dead_ends/schema_validation_error.md`
2. Extract specific field(s) that failed validation
3. Provide specific error message to agent
4. Allow agent to retry with corrected output
5. Max 3 retry attempts before dead end

---

## Schema Definitions

### Research Question Schema
```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
from datetime import datetime

class ResearchQuestion(BaseModel):
    text: str = Field(..., min_length=10, description="The research question text")
    type: Literal["descriptive", "comparative", "associational", "causal", "predictive", "exploratory"]
    hypothesis: str = Field(..., min_length=10, description="The hypothesis to test")
    outcome: str = Field(..., description="Outcome variable name")
    predictor: str = Field(..., description="Predictor variable name")
    covariates: Optional[List[str]] = Field(default=[], description="Covariate variables")
    files: Optional[List[str]] = Field(default=[], description="Data files needed")
    prep: Optional[str] = Field(default=None, description="Data preparation needed")

    @validator("text")
    def question_must_end_with_question_mark(cls, v):
        if not v.strip().endswith("?"):
            raise ValueError("Research question must end with a question mark")
        return v
```

### Research Map Schema
```python
class ResearchMap(BaseModel):
    schema_version: str = Field(..., pattern=r"^\\d+\\.\\d+\\.\\d+$")
    project: dict = Field(..., description="Project metadata")
    questions: List[ResearchQuestion] = Field(..., min_items=1)
    data: dict = Field(..., description="Data file information")
    domain: dict = Field(..., description="Domain configuration")
    feasibility: dict = Field(..., description="Feasibility assessment")
    follow_up: List[str] = Field(default=[], description="Follow-up questions")

    @validator("questions")
    def at_least_one_question(cls, v):
        assert len(v) >= 1, "Must have at least one research question"
        return v

    @validator("feasibility")
    def feasibility_must_have_verdict(cls, v):
        assert "verdict" in v, "Feasibility must include a verdict"
        assert v["verdict"] in ["go", "caution", "stop"], "Invalid feasibility verdict"
        return v
```

### Literature Corpus Schema
```python
class PaperEntry(BaseModel):
    doi: Optional[str] = Field(default=None, description="Digital Object Identifier")
    title: str = Field(..., min_length=5)
    authors: List[str] = Field(..., min_items=1)
    year: int = Field(..., ge=1900, le=2030)
    journal: Optional[str] = Field(default=None)
    abstract: Optional[str] = Field(default=None)
    citations: Optional[int] = Field(default=None, ge=0)
    relevance_score: Optional[float] = Field(default=None, ge=0, le=1)
    verification_status: Literal["verified", "unverified", "retracted"] = Field(default="unverified")

class LiteratureCorpus(BaseModel):
    schema_version: str = Field(..., pattern=r"^\\d+\\.\\d+\\.\\d+$")
    papers: List[PaperEntry] = Field(..., min_items=1)
    search_queries: List[str] = Field(default=[], description="Search queries used")
    last_updated: str = Field(..., description="ISO 8601 timestamp")

    @validator("papers")
    def at_least_one_paper(cls, v):
        assert len(v) >= 1, "Corpus must contain at least one paper"
        return v
```

### Analysis Results Schema
```python
class StatisticalTest(BaseModel):
    test_name: str = Field(..., description="Name of statistical test")
    statistic: float = Field(..., description="Test statistic value")
    degrees_of_freedom: Optional[float] = Field(default=None)
    p_value: float = Field(..., ge=0, le=1, description="Exact p-value")
    effect_size: float = Field(..., description="Effect size estimate")
    effect_size_type: str = Field(..., description="Type of effect size (cohens_d, r, eta_squared, etc.)")
    confidence_interval: List[float] = Field(..., min_items=2, max_items=2, description="[lower, upper]")
    sample_size: int = Field(..., gt=0)
    assumptions_checked: List[str] = Field(default=[], description="Assumptions verified")

class AnalysisResults(BaseModel):
    question_id: str = Field(..., description="Research question identifier (Q1, Q2, etc.)")
    tests: List[StatisticalTest] = Field(..., min_items=1)
    conclusion: str = Field(..., min_length=20)
    limitations: List[str] = Field(default=[])
    data_file: str = Field(..., description="Path to analytical data used")
    script: str = Field(..., description="Path to analysis script")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
```

### Audit Report Schema
```python
class AuditCheck(BaseModel):
    check_name: str = Field(..., description="Name of audit check")
    status: Literal["PASS", "FAIL", "CONDITIONAL"]
    details: str = Field(..., description="Detailed findings")
    remediation: Optional[str] = Field(default=None, description="Fix instructions if FAIL")

class AuditReport(BaseModel):
    audit_type: str = Field(..., description="Type of audit")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    checks: List[AuditCheck] = Field(..., min_items=1)
    overall_verdict: Literal["PASS", "FAIL", "CONDITIONAL"]
    failures: List[str] = Field(default=[], description="List of failed check names")
    auto_healing_attempts: int = Field(default=0, ge=0, le=3)
```

### State Ledger Schema
```python
class TokenBudget(BaseModel):
    used: int = Field(..., ge=0)
    remaining: int = Field(..., ge=0)
    limit: int = Field(..., gt=0)

class ResearchState(BaseModel):
    run_id: str = Field(..., description="UUID for this research run")
    project: str = Field(..., description="Project title")
    phase: str = Field(..., description="Current pipeline phase")
    step: int = Field(..., ge=0)
    checkpoints: dict = Field(default={}, description="Phase completion status")
    active_hypotheses: List[dict] = Field(default=[])
    dead_ends: List[str] = Field(default=[])
    loaded_data: List[str] = Field(default=[])
    token_budget: TokenBudget = Field(...)
    last_checkpoint: str = Field(..., description="ISO 8601 timestamp")
    errors: List[str] = Field(default=[])
    resumable_from: Optional[str] = Field(default=None)
```

---

## Validation Function

```python
# .research/schemas/validator.py
from pydantic import ValidationError
from typing import Any, Type
import json

def validate_payload(data: Any, schema_type: Type[BaseModel]) -> dict:
    \"\"\"Validate data against a Pydantic schema.
    
    Args:
        data: The data to validate (dict or JSON string)
        schema_type: The Pydantic model class to validate against
    
    Returns:
        dict: Validated data as dict
    
    Raises:
        ValidationError: If data doesn't match schema
    \"\"\"
    if isinstance(data, str):
        data = json.loads(data)
    
    try:
        validated = schema_type(**data)
        return validated.model_dump()
    except ValidationError as e:
        raise ValidationError(
            f"Schema validation failed for {schema_type.__name__}:\\n{e}"
        )
```

---

## Integration
- Called by: Every agent before writing output files
- Interceptors: `pre_ledger_commit` hook runs schema validation
- Blocks pipeline if: Validation fails after 3 retry attempts
- Location: `.research/schemas/`
""",
    "ideation_evaluator": """---
skill_id: "ideation_evaluator"
version: "1.0.0"
description: "Triage random researcher thoughts into scratchpad notes, queued tasks, or isolated experiment branches before execution."
category: "core"
---

# Skill: Ideation Evaluator

Use this skill when the user introduces a random jump mid-workflow: a new robustness concern, a paper/link, a half-formed metric, a CSV, or a question like "did we check X?"

## Protocol

1. Do not immediately execute analysis code.
2. Capture the thought in `01_workspace/scratchpad/` when it came from an external note/file, or append it directly to `01_workspace/lab_notebook.md` when it came through chat.
3. Classify the thought:
   - `log_only`: contextual note that does not change current work.
   - `queue_later`: plausible follow-up, but not blocking the active experiment.
   - `branch_now`: a concrete hypothesis, robustness check, or method switch that could change results.
   - `intake_gap`: missing information that blocks interpretation.
4. Append a lab notebook entry with timestamp, source, classification, rationale, active experiment, and recommended action.
5. If classification is `branch_now`, propose a new experiment id using `exp_<next_number>_<short_slug>` and ask whether to pause the current experiment and branch.
6. If classification is `queue_later`, add a TODO-style item to `01_workspace/scratchpad/queued_ideas.md`.

## Branching Rule

Create an experiment branch only after the user approves or when the user explicitly asks to explore the idea now. The branch must live under:

```text
02_experiments/exp_<NNN>_<slug>/
  scripts/
  outputs/
    figures/
    tables/
    artifacts/
    analysis/
  decisions.yaml
```

The first decision in `decisions.yaml` must record the parent experiment and the reason for divergence.

## Response Template

When triaging a random jump, respond briefly:

```text
I logged this in `01_workspace/lab_notebook.md` as <classification>.
Recommendation: <branch now | queue | log only>, because <one-sentence rationale>.
Should I create `<experiment_id>` from `<active_experiment>`, or keep it queued?
```
""",
    "context7_lookup": """# Skill: Docs-First Code Generation via Context7

## Purpose
Prevents agents from inventing APIs or using deprecated function signatures by enforcing a "docs-first" generation pattern. Any code using scientific or plotting libraries must base its syntax on current documentation retrieved dynamically.

## Mandatory Libraries
Must be used for: `scipy`, `statsmodels`, `pandas`, `sklearn`, `lifelines`, `pymc`, `networkx`, `geopandas`, `altair`, `bokeh`, `panel`, `holoviews`, `dash`, `plotly`.

## Protocol

1. **Resolve Library ID:**
   Before querying documentation, resolve the standard library name to its unique Context7 ID.
   ```bash
   python -m research_copilot.utils.context7_lookup resolve <library_name>
   ```

2. **Query Documentation:**
   Using the resolved ID, query the specific topic or function name to fetch the current API signature, parameters, and example usage.
   ```bash
   python -m research_copilot.utils.context7_lookup docs <library_id> <topic_or_function>
   ```

3. **Incorporate in Generation:**
   Construct imports and calls strictly adhering to the returned signatures. Never rely on base training weights for library syntax.

4. **Cache Integration:**
   All documentation searches are cached in the research SQLite database (`.research/cache/research_cache.db`) with a TTL of 30 days to avoid redundant lookups.
""",
    "validate_intake": """# Skill: Validate Intake

> Runs before `research_init`. Ensures intake form is complete, coherent, and answerable.

## Purpose
Validate the intake form before any research begins. Catch unanswerable questions, missing variables, and incoherent specifications early.

---

## Protocol

### Step 1: Load Intake Form
1. Read `inputs/intake.md`
2. Check for alternative formats: `inputs/intake.json`, `inputs/intake.yaml`
3. If none found, report: "No intake form found. Create inputs/intake.md"

### Step 2: Check Required Fields
Verify all required fields are present AND filled (not placeholder text):

| Field | Validation |
|-------|-----------|
| Project title | Non-empty, not "[Your answer]" |
| Researcher name | Non-empty |
| Institution | Non-empty |
| Domain | Must match a domain in `.research/domains/` or be "custom" |
| Research questions | At least one question with text, type, hypothesis |
| Data files | At least one data file described |
| Target output | Specified (journal, report, presentation) |

### Step 3: Validate Research Questions
For each research question:

1. **Question is answerable** — Not circular, not untestable, not purely philosophical
2. **Type is valid** — Must be one of: descriptive, comparative, associational, causal, predictive, exploratory
3. **Variables are named** — Outcome and predictor variables specified
4. **Hypothesis direction stated** — If not, generate one and ask for confirmation
5. **Variables exist in data** — Cross-reference against `schema_cache.json`

### Step 4: Validate Data Specifications
1. Check that named variables exist in data files (using schema cache)
2. Verify data format is supported (CSV, TSV, Parquet, Excel, SPSS, Stata, SAS)
3. Check for minimum sample size feasibility based on question type

### Step 5: Validate Domain
1. Check domain against `.research/domains/` directory
2. If domain matches a config file, load domain-specific requirements
3. If domain is "custom", note that default standards will apply

### Step 6: Generate Validation Report
Output: `reports/baseline/intake_validation.json`

```json
{
  "schema_version": "1.0.0",
  "timestamp": "ISO 8601",
  "overall_status": "PASS|FAIL|CONDITIONAL",
  "field_validation": {
    "project_title": {"status": "PASS", "value": "..."},
    "researcher": {"status": "PASS", "value": "..."},
    "domain": {"status": "PASS", "value": "...", "matched_config": "psychology.yaml"}
  },
  "question_validation": [
    {
      "question_id": "Q1",
      "status": "PASS",
      "type_valid": true,
      "variables_found_in_data": true,
      "hypothesis_direction": "positive",
      "issues": []
    }
  ],
  "data_validation": {
    "files_found": 2,
    "formats_supported": true,
    "schema_matched": true,
    "issues": []
  },
  "generated_hypotheses": [
    {
      "question_id": "Q2",
      "generated_hypothesis": "...",
      "requires_confirmation": true
    }
  ],
  "issues": [],
  "recommendations": []
}
```

### Step 7: Gate Decision
- **PASS**: All validations pass, proceed to `research_init`
- **CONDITIONAL**: Minor issues (e.g., hypothesis direction missing but generated), proceed with notes
- **FAIL**: Critical issues (no data files, unanswerable questions), block and report to user

---

## Validation Rules

### Unanswerable Question Detection
Flag questions that:
- Are purely normative ("Should we...?")
- Require data not available and not collectable
- Are tautological or circular
- Are too broad to operationalize

### Variable Existence Check
For each named variable:
1. Look up in `schema_cache.json`
2. If not found, flag as MISSING
3. Suggest closest matching variable names from schema

### Domain Matching
1. Normalize domain name (lowercase, strip spaces)
2. Match against available `.research/domains/*.yaml` files
3. If no match, use `custom_template.yaml` defaults

---

## Integration
- Called by: `research_init` agent before any processing
- Outputs to: `reports/baseline/intake_validation.json`
- Blocks pipeline if: FAIL status
""",
    "assumption_validator": """# Assumption Validator (Pre-Execution Gate)

## Purpose
Before any analysis script runs, this skill verifies its statistical assumptions against the data profile. If a required assumption fails, it blocks execution of the primary method, logs the failure to dead ends, and routes to a designated fallback method.

---

## Protocol

For each analytical task:
1. **Identify the Method**: Detect the method planned for the research question (e.g., OLS regression, t-test, ANOVA).
2. **Retrieve Stated Assumptions**: Read the planned assumptions from the methodology layout.
3. **Execute Statistical Assumption Tests**: Run specific validation checks on the actual input datasets.
4. **Determine Pass/Fail**: Evaluate the test statistics and p-values against standard criteria.
5. **Route Execution**:
   - **PASS**: Allow the primary script to execute.
   - **FAIL**: Block execution, log to dead ends, and trigger the fallback method (e.g., nonparametric alternative).

---

## Statistical Tests & Fallback Mapping

| Method | Assumption | Statistical Test | Criteria | Fallback Method |
|---|---|---|---|---|
| **t-test (independent)** | Normality of groups | Shapiro-Wilk test | $p \\ge 0.05$ | Mann-Whitney U test |
| | Homogeneity of variance | Levene's test | $p \\ge 0.05$ | Welch's t-test |
| **ANOVA (one-way)** | Normality of residuals | Shapiro-Wilk or Kolmogorov-Smirnov | $p \\ge 0.05$ | Kruskal-Wallis test |
| | Homogeneity of variances | Levene's test | $p \\ge 0.05$ | Welch's ANOVA |
| **OLS Regression** | Linearity | Harvey-Collier or Ramsey RESET | $p \\ge 0.05$ | Generalized Additive Models (GAM) / Polynomial |
| | Homoscedasticity | Breusch-Pagan or White test | $p \\ge 0.05$ | Weighted Least Squares (WLS) or robust errors |
| | Normality of residuals | Jarque-Bera or Shapiro-Wilk | $p \\ge 0.05$ | Robust regression (RLM) or bootstrapping |
| | No Multicollinearity | Variance Inflation Factor (VIF) | $VIF < 5$ (or $< 10$) | Ridge/Lasso Regression or drop collinear feature |
| | Independence of residuals | Durbin-Watson test | $1.5 < DW < 2.5$ | Newey-West standard errors or ARMA modeling |
| **Time Series (ARIMA)** | Stationarity | Augmented Dickey-Fuller (ADF) | $p < 0.05$ | Differencing ($d \\ge 1$) or detrending |

---

## Output Validation Report

The validator generates `reports/analysis/assumption_validation_{question_id}.json` with the following structure:

```json
{
  "question_id": "q1",
  "planned_method": "OLS",
  "timestamp": "2026-05-19T21:30:00Z",
  "verdict": "PASS | FAIL",
  "results": [
    {
      "assumption": "Normality of residuals",
      "test_name": "Shapiro-Wilk",
      "statistic": 0.985,
      "p_value": 0.123,
      "status": "PASS",
      "message": "Residuals are normally distributed."
    },
    {
      "assumption": "Homoscedasticity",
      "test_name": "Breusch-Pagan",
      "statistic": 12.4,
      "p_value": 0.002,
      "status": "FAIL",
      "message": "Heteroscedasticity detected (p < 0.05)."
    }
  ],
  "routing": {
    "action": "execute_fallback | execute_primary",
    "target_method": "Robust Regression (RLM)",
    "reason": "Failed Homoscedasticity assumption."
  }
}
```

---

## Sample-Size-Adaptive Normality Testing

The choice of normality test depends on sample size. Use this decision table before running any parametric test:

| Sample Size (N) | Normality Test | Rationale |
|-----------------|---------------|-----------|
| N < 30 | Exact tests (permutation / bootstrap) | Shapiro-Wilk unreliable at very small N; exact tests have correct Type I error |
| 30 ≤ N < 5000 | Shapiro-Wilk | Most powerful omnibus test for normality in this range |
| N ≥ 5000 | Kolmogorov-Smirnov (with Lilliefors correction) | Shapiro-Wilk becomes oversensitive at large N; KS is more stable |

### Implementation Note

For N ≥ 5000, supplement with visual diagnostics (Q-Q plot, histogram) because ANY formal test will reject trivial deviations. Use effect-size-based normality assessment: skewness |< 2| and kurtosis |< 7| as practical thresholds.

---

## Fallback Chain: OLS → Robust → Nonparametric

When OLS assumptions fail, follow this cascade. Each step has a 1-line rationale:

| Step | Method | Trigger | Rationale |
|------|--------|---------|-----------|
| 1 | **OLS** (baseline) | All assumptions pass | Most efficient estimator under Gauss-Markov conditions |
| 2 | **OLS + Robust SE** (HC3) | Heteroscedasticity only | Preserves coefficient estimates; corrects standard errors for unequal variance |
| 3 | **RLM** (Huber/bisquare) | Outliers or non-normal residuals | Down-weights influential observations; resistant to heavy-tailed errors |
| 4 | **Bootstrap** (percentile or BCa) | Non-normal residuals + small N | Distribution-free inference; valid for any sample size with 1000+ resamples |
| 5 | **Nonparametric** (rank-based / permutation) | Multiple assumption failures | Makes no distributional assumptions; valid under minimal conditions |

### Decision Rules

- If ONLY heteroscedasticity fails → Step 2 (Robust SE). Do NOT abandon OLS coefficients.
- If heteroscedasticity + non-normality → Step 3 (RLM).
- If multicollinearity (VIF > 10) → Ridge/Lasso BEFORE applying fallback chain.
- If N < 30 AND assumptions fail → Step 4 (Bootstrap) or Step 5 (Nonparametric).
- Document which step was used and why in the experiment `decisions.yaml`.

---

## Integration

- Run automatically prior to script execution.
- If a check fails, the orchestrator updates `.research/cache/state.json` with the fallback target and writes a dead end entry describing the violation to `docs/dead_ends/`.
- CLI Command: `python -m research_copilot.utils.assumption_validator --data <path> --config <config_path>`
""",
    "github_release": """---
skill_id: "github_release"
version: "7.0.0"
category: "integration"
domain_compatibility: ["all"]
required_tools: ["python", "subprocess", "gh-cli"]
depends_on: ["audit_reproducibility"]
produces: ["integration/github_release_log.json"]
complexity: "intermediate"
---

# Skill: GitHub Release Packaging

## Purpose
Package and publish the complete research project (code, data, results, documentation) as a versioned GitHub release for public sharing and archiving.

## When to Use
- Research complete and audited
- Ready for public sharing
- Journal requires code/data availability

## When NOT to Use
- Research not yet complete
- Data contains sensitive information
- Embargo period not expired

## Execution Protocol

### Step 1: Repository Preparation
- Create or update GitHub repository
- Structure:
  ```
  ├── data_raw/          # Raw data (if shareable)
  ├── data_processed/    # Cleaned data
  ├── analysis/          # Analysis scripts
  ├── reports/           # Manuscript, figures, tables
  ├── literature/        # Literature corpus
  ├── requirements.txt   # Dependencies
  ├── README.md          # Project documentation
  └── LICENSE            # Usage license
  ```

### Step 2: Sensitivity Review
- Check: no personal identifiers in data
- Check: no API keys or credentials in code
- Check: no sensitive information in comments
- If sensitive: anonymize or exclude

### Step 3: Documentation
- README must include:
  - Project title and authors
  - Research question
  - How to reproduce (step-by-step)
  - Data availability statement
  - Citation information
  - License

### Step 4: Release Creation
- Tag: semantic version (v1.0.0)
- Commit: all files with descriptive message
- Push: to main branch
- Create GitHub release with:
  - Release notes (summary of findings)
  - Attached manuscript PDF
  - Attached key figures
  - DOI badge (if Zenodo archived)

## Output Specification
- `integration/github_release_log.json`: repository URL, release tag, commit hash, attached files

## Validation Checks
- [ ] No sensitive data in repository
- [ ] README complete
- [ ] Requirements.txt up to date
- [ ] Release accessible via URL
- [ ] License file present
""",
    "zotero_sync": """---
skill_id: "zotero_sync"
version: "7.0.0"
category: "integration"
domain_compatibility: ["all"]
required_tools: ["python", "pyzotero", "bibtexparser"]
depends_on: ["generate_bibtex"]
produces: ["integration/zotero_sync_log.json"]
complexity: "intermediate"
---

# Skill: Zotero Reference Sync

## Purpose
Sync the research bibliography to a Zotero library for reference management, annotation, and citation insertion.

## When to Use
- Literature corpus built
- BibTeX file generated
- Researcher uses Zotero for reference management

## When NOT to Use
- Researcher uses different reference manager
- Only a few references (manual entry sufficient)

## Execution Protocol

### Step 1: Zotero Connection
- Connect to Zotero API using user ID and API key
- Verify: connection successful, library accessible
- Identify: target collection (create if not exists)

### Step 2: Reference Import
- Parse BibTeX file into individual entries
- For each entry:
  - Check if already in Zotero (by DOI)
  - If new: create Zotero item with all fields
  - If existing: update metadata if changed
- Tag: all imported items with project tag

### Step 3: Attachment Linking
- If PDFs available: attach to Zotero items
- If URLs available: add as linked URLs
- Verify: attachments accessible

### Step 4: Sync Log
- Record: items added, updated, skipped (duplicates)
- Record: any import errors
- Output: sync summary

## Output Specification
- `integration/zotero_sync_log.json`: items added, updated, skipped, errors

## Validation Checks
- [ ] All BibTeX entries processed
- [ ] No duplicate items created
- [ ] Project tag applied to all items
- [ ] Errors logged and reported
""",
    "preprint_submit": """# Skill: Preprint Submission Helper

> Prepares submission packages for arXiv, bioRxiv, medRxiv, and SSRN.

## Purpose
Generate ready-to-submit packages for preprint servers. Does NOT auto-submit — requires human approval.

---

## Protocol

### Step 1: Load Manuscript and Metadata
1. Read `reports/manuscript/research_findings.md`
2. Load project metadata from `docs/manifest.json`
3. Load literature corpus for reference validation

### Step 2: Determine Target Preprint Server
Based on domain and content:
- **arXiv**: Physics, mathematics, computer science, quantitative biology, quantitative finance, statistics, electrical engineering, economics
- **bioRxiv**: Biological sciences
- **medRxiv**: Health sciences, clinical research
- **SSRN**: Social sciences, law, economics, humanities

### Step 3: Prepare arXiv Submission Package

#### 3.1 Generate Metadata JSON
Create `reports/manuscript/preprint/arxiv_metadata.json`:
```json
{
  "title": "Manuscript title",
  "authors": [
    {"name": "Author Name", "affiliation": "Institution", "orcid": "0000-0000-0000-0000"}
  ],
  "abstract": "Abstract text (max 1920 characters)",
  "categories": ["stat.AP", "cs.AI"],
  "comments": "X pages, Y figures",
  "doi": "",
  "journal_ref": "",
  "report_no": "",
  "msc_class": "",
  "acm_class": ""
}
```

#### 3.2 Validate PDF
1. Check PDF exists: `reports/manuscript/manuscript.pdf`
2. Validate PDF/A compliance (arXiv requirement)
3. Check font embedding (all fonts must be embedded)
4. Verify page size (letter or A4)
5. Check file size (< 10 MB recommended)

#### 3.3 Check Category
1. Suggest appropriate arXiv categories based on content
2. Primary category must be selected
3. Secondary categories optional (max 2)
4. Available categories:
   - `stat.AP` — Applications
   - `stat.ME` — Methodology
   - `stat.ML` — Machine Learning
   - `cs.AI` — Artificial Intelligence
   - `cs.LG` — Machine Learning
   - `q-bio.QM` — Quantitative Methods
   - `q-fin.ST` — Statistical Finance
   - `econ.EM` — Econometrics

#### 3.4 Generate Submission Checklist
Create `reports/manuscript/preprint/arxiv_checklist.md`:
- [ ] PDF validates (fonts embedded, PDF/A compliant)
- [ ] Abstract ≤ 1920 characters
- [ ] Categories selected
- [ ] Authors listed with affiliations
- [ ] No confidential information
- [ ] License selected (arXiv perpetual license or CC-BY)
- [ ] Endorsement obtained (if first-time submitter)

### Step 4: Prepare bioRxiv/medRxiv Submission Package

#### 4.1 Validate Format
1. Check manuscript format requirements:
   - Word or LaTeX source accepted
   - PDF generated from source
   - Figures embedded or separate
2. Verify abstract structure (bioRxiv: unstructured, ≤250 words)
3. Check for required statements:
   - Competing interests
   - Author contributions
   - Data availability
   - Ethics approval (if applicable)

#### 4.2 Generate Submission Checklist
Create `reports/manuscript/preprint/biorxiv_checklist.md`:
- [ ] Manuscript formatted per guidelines
- [ ] Abstract ≤ 250 words
- [ ] Competing interests declared
- [ ] Author contributions listed
- [ ] Data availability statement included
- [ ] Ethics approval statement (if applicable)
- [ ] All authors agree to submission
- [ ] Corresponding author designated

#### 4.3 medRxiv Specific
Additional requirements for medRxiv:
- [ ] Clinical trial registration number (if applicable)
- [ ] Funding statement
- [ ] Patient consent statement

### Step 5: Prepare SSRN Submission Package

#### 5.1 Format Abstract
1. SSRN abstract: ≤ 300 words
2. Include keywords (5-10)
3. Generate JEL classification codes (for economics)

#### 5.2 Generate Metadata
Create `reports/manuscript/preprint/ssrn_metadata.json`:
```json
{
  "title": "Manuscript title",
  "authors": ["Author Name"],
  "abstract": "Abstract text",
  "keywords": ["keyword1", "keyword2"],
  "jel_codes": ["C10", "C18"],
  "date": "YYYY-MM-DD"
}
```

#### 5.3 Generate Submission Checklist
Create `reports/manuscript/preprint/ssrn_checklist.md`:
- [ ] Abstract ≤ 300 words
- [ ] Keywords provided (5-10)
- [ ] JEL codes assigned (if economics)
- [ ] Author affiliations current
- [ ] No confidential information

### Step 6: Package Output
Create `reports/manuscript/preprint/` directory with:
- `arxiv_metadata.json` — arXiv metadata
- `arxiv_checklist.md` — arXiv submission checklist
- `biorxiv_checklist.md` — bioRxiv/medRxiv checklist
- `ssrn_metadata.json` — SSRN metadata
- `ssrn_checklist.md` — SSRN checklist
- `manuscript.pdf` — Ready-to-submit PDF
- `source/` — LaTeX source files (if applicable)

### Step 7: Human Approval Gate
1. Present submission package to user
2. User reviews all checklists
3. User confirms readiness
4. User manually submits to chosen preprint server
5. DO NOT auto-submit under any circumstances

---

## Integration
- Called by: `compile_outputs` agent or user request
- Requires: Complete manuscript, PDF generated
- Outputs to: `reports/manuscript/preprint/`
- Does NOT: Auto-submit to any server
""",
    "audit_reproducibility": """---
skill_id: "audit_reproducibility"
version: "7.0.0"
category: "audit"
domain_compatibility: ["all"]
required_tools: ["python", "hashlib", "subprocess"]
depends_on: ["compute_hashes"]
produces: ["audit/reproducibility_audit.json"]
complexity: "intermediate"
---

# Skill: Reproducibility Audit

## Purpose
Verify that the entire research pipeline can be reproduced from raw data to final results in a clean environment.

## When to Use
- After all analysis completed
- Before finalizing manuscript
- For submission to reproducible research journals

## When NOT to Use
- Analysis still in progress
- Data not yet finalized

## Execution Protocol

### Step 1: Environment Documentation
- Record: Python version, OS, all package versions (pip freeze)
- Verify: requirements.txt or environment.yml specifies exact versions
- Check: no system-level dependencies (all pip-installable)

### Step 2: Data Integrity
- Recompute SHA-256 hashes for all raw data files
- Compare to hash manifest from compute_hashes
- Flag: any file with mismatched hash (modified or corrupted)

### Step 3: Script Execution
- In a clean environment (new virtualenv or container):
  - Install dependencies from requirements.txt
  - Run each analysis script in dependency order
  - Record: exit code, execution time, warnings
- Verify: all scripts exit with code 0

### Step 4: Output Verification
- Compare regenerated outputs to original outputs
- Numerical tolerance: results within 1e-6 of original (floating-point variation acceptable)
- Exact match: tables, figures (pixel-perfect for figures may not be possible)
- Flag: any output that differs beyond tolerance

### Step 5: Documentation Completeness
- Check: README explains how to reproduce
- Check: data availability statement included
- Check: code repository link provided
- Check: analysis pipeline documented (workflow DAG)

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| Hash match | All files unchanged | Investigate modification; restore from backup |
| Script execution | All exit 0 | Debug failing script |
| Output match | Within tolerance | Check for non-deterministic operations |
| Documentation | Complete | Fill gaps before submission |

## Output Specification
- `audit/reproducibility_audit.json`: pass/fail per check, details of failures, environment snapshot

## Validation Checks
- [ ] All data hashes verified
- [ ] All scripts execute successfully
- [ ] Outputs match within tolerance
- [ ] Documentation complete
""",
    "audit_code_quality": """---
skill_id: "audit_code_quality"
version: "7.0.0"
category: "audit"
domain_compatibility: ["all"]
required_tools: ["python", "pylint|flake8", "black"]
depends_on: []
produces: ["audit/code_quality_audit.json"]
complexity: "basic"
---

# Skill: Code Quality Audit

## Purpose
Assess analysis code for quality, readability, reproducibility, and best practices.

## When to Use
- After analysis scripts written
- Before sharing code publicly
- For code review

## When NOT to Use
- Code is exploratory/throwaway
- Only results matter (not code)

## Execution Protocol

### Step 1: Style Check
- PEP 8 compliance: naming, indentation, line length
- Consistent formatting: run black formatter
- Docstrings: all functions have docstrings with Args, Returns, Examples
- Comments: explain why, not what

### Step 2: Reproducibility Check
- Random seeds set for all stochastic operations
- No hardcoded paths: use relative paths or config
- No hardcoded parameters: use config files or function arguments
- Version control: all code in git with meaningful commits

### Step 3: Error Handling
- Try/except blocks for file I/O and API calls
- Meaningful error messages (not just "Error occurred")
- Input validation: check types, ranges, missing values
- Logging: not just print statements

### Step 4: Complexity Check
- Function length: < 50 lines (refactor if longer)
- Nesting depth: < 4 levels
- Cyclomatic complexity: < 10 per function
- No code duplication: DRY principle

### Step 5: Dependency Check
- All imports used (no unused imports)
- No circular imports
- Dependencies listed in requirements.txt
- No deprecated function calls

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| PEP 8 | No violations | Run black and fix remaining |
| Docstrings | All functions documented | Add missing docstrings |
| Reproducibility | Seeds set, no hardcoded values | Fix reproducibility issues |
| Complexity | All functions < 50 lines | Refactor long functions |

## Output Specification
- `audit/code_quality_audit.json`: per-file quality scores, violation details, recommendations

## Validation Checks
- [ ] All Python files pass style check
- [ ] All functions documented
- [ ] No hardcoded paths or parameters
- [ ] Random seeds set
""",
    "audit_visualizations": """# Skill: Audit Visualizations

> Audit #8: Run figure validation on every figure in `reports/figures/`.

## Purpose
Automated figure validation that checks DPI, colorblind safety, axis labels, font sizes, and file size. Any figure below standard = FAIL.

---

## Protocol

### Step 1: Scan Figures Directory
1. List all figure files in `reports/figures/`
2. Include subdirectories (e.g., `reports/figures/q1/`)
3. Supported formats: PNG, PDF, SVG
4. Skip: `.gitkeep`, `README.md`

### Step 2: Run Figure Validator
Execute `python -m research_copilot.utils.figure_validator --directory reports/figures/`

For each figure, run checks:

| Check | Standard | Method |
|-------|----------|--------|
| DPI | ≥ 300 | Read image metadata |
| Axis labels | Present | OCR-based detection |
| Colorblind safe | Okabe-Ito palette | Color extraction + palette matching |
| No truncated axes | Origin visible | Axis range analysis |
| Font size | ≥ 8pt | OCR-based font size estimation |
| File size | ≤ 5 MB | File system check |
| No rainbow/jet | Perceptually uniform | Colormap detection |
| No pie charts | N/A | Visual pattern detection |
| No 3D charts | N/A | Visual pattern detection |
| Effect size shown | With p-value | Text annotation detection |
| Confidence intervals | Present | Visual element detection |

### Step 3: Generate Validation Report
Create `reports/audit/visualization_audit.json`:

```json
{
  "schema_version": "1.0.0",
  "timestamp": "ISO 8601",
  "total_figures": 12,
  "summary": {
    "pass": 10,
    "fail": 2,
    "warnings": 3
  },
  "figures": [
    {
      "file": "reports/figures/fig_001_q1_scatter.png",
      "checks": {
        "dpi": {"status": "PASS", "value": 300},
        "axis_labels": {"status": "PASS", "x_label": "X variable", "y_label": "Y variable (units)"},
        "colorblind_safe": {"status": "PASS", "palette": "okabe_ito"},
        "no_truncated_axes": {"status": "PASS"},
        "font_size": {"status": "PASS", "minimum": 10},
        "file_size": {"status": "PASS", "size_mb": 1.2},
        "no_rainbow_colormap": {"status": "PASS"},
        "no_pie_chart": {"status": "PASS"},
        "no_3d_chart": {"status": "PASS"},
        "effect_size_shown": {"status": "PASS", "value": "r=0.42"},
        "confidence_intervals": {"status": "PASS"}
      },
      "overall_status": "PASS"
    },
    {
      "file": "reports/figures/fig_002_q2_bar.png",
      "checks": {
        "dpi": {"status": "FAIL", "value": 150, "required": 300},
        "axis_labels": {"status": "PASS"},
        "colorblind_safe": {"status": "FAIL", "palette": "default_matplotlib"},
        "font_size": {"status": "WARNING", "minimum": 7, "required": 8},
        "overall_status": "FAIL"
      },
      "remediation": {
        "dpi": "Re-render at 300 DPI using saved figure parameters",
        "colorblind_safe": "Re-render with Okabe-Ito substitution"
      }
    }
  ]
}
```

### Step 4: Verdict
- **PASS:** All figures meet all standards
- **CONDITIONAL:** Some figures have warnings (minor issues that don't block)
- **FAIL:** Any figure fails a critical check (DPI, colorblind safety, missing axis labels)

### Step 5: Auto-Healing
If FAIL or CONDITIONAL:
1. For DPI failures: Re-render at 300 DPI using saved figure parameters
2. For colorblind palette violations: Re-render with Okabe-Ito substitution
3. For missing axis labels: Add labels with units
4. For font size warnings: Re-render with larger fonts
5. For rainbow/jet colormaps: Re-render with viridis or perceptually uniform palette
6. Re-run validation after fixes

### Step 6: Generate Summary Report
Create `reports/audit/visualization_audit_summary.md`:
- List of all figures with pass/fail status
- Specific remediation steps for failed figures
- Overall verdict

---

## Integration
- Called by: `audit_validate` agent as Audit #8
- Uses: `figure_validator.py` script
- Outputs to: `reports/audit/visualization_audit.json`
- Blocks manuscript if: FAIL verdict
""",
    "audit_claim_trace": """# Skill: Audit Claim Trace

> Audit #7: Every factual claim in manuscript traced to computed data OR verified citation.

## Purpose
Build a claim-to-evidence graph for the entire manuscript. Any claim with a broken trace is flagged as UNSUPPORTED and blocked from final output.

---

## Protocol

### Step 1: Extract Claims from Manuscript
1. Read `reports/manuscript/research_findings.md`
2. Identify factual claims using pattern matching:
   - Numeric claims: "X is associated with Y (r=0.42)"
   - Comparative claims: "Group A scored higher than Group B"
   - Literature claims: "Prior studies show effects between 0.3-0.5"
   - Causal claims: "X causes Y"
3. For each claim, record:
   - Claim text
   - Location in manuscript (section, paragraph)
   - Claim type (numeric, comparative, literature, causal)

### Step 2: Trace Numeric Claims to Data
For each numeric claim:
1. Search analysis outputs in `reports/analysis/` for matching values
2. Trace to source data file:
   - Check `docs/data_lineage.json` for transformation chain
   - Verify SHA-256 hash of source data matches
3. Record trace:
   ```
   Claim: "X is associated with Y (r=0.42)"
     └── Source: reports/analysis/q1/results.json (line 47)
         └── Input: data/03_analytical/analysis_q1.csv (hash: abc123)
             └── Raw: 00_inputs/raw_data/survey.csv (hash: def456)
   ```

### Step 3: Trace Literature Claims to Verified Citations
For each literature claim:
1. Find the citation(s) supporting the claim
2. Check `reports/literature/citation_verification_report.json`
3. Verify citation passed all three verification passes
4. Record trace:
   ```
   Claim: "Prior studies show effects between 0.3-0.5"
     └── Source: DOI:10.xxxx/yyyy (CrossRef verified ✓, content verified ✓, retraction check ✓)
   ```

### Step 4: Build Claim-to-Evidence Graph
Create `reports/audit/claim_trace_report.json`:

```json
{
  "schema_version": "1.0.0",
  "timestamp": "ISO 8601",
  "total_claims": 87,
  "summary": {
    "fully_traced": 78,
    "partially_traced": 5,
    "unsupported": 4
  },
  "claims": [
    {
      "claim_id": "C001",
      "claim_text": "X is associated with Y (r=0.42, p=0.003)",
      "claim_type": "numeric",
      "location": "Section 3.2, paragraph 2",
      "trace": {
        "status": "FULLY_TRACED",
        "source_file": "reports/analysis/q1/results.json",
        "data_file": "data/03_analytical/analysis_q1.csv",
        "data_hash": "abc123",
        "raw_file": "00_inputs/raw_data/survey.csv",
        "raw_hash": "def456"
      }
    },
    {
      "claim_id": "C002",
      "claim_text": "Prior studies show effects between 0.3-0.5",
      "claim_type": "literature",
      "location": "Section 2.1, paragraph 3",
      "trace": {
        "status": "FULLY_TRACED",
        "source": "DOI:10.xxxx/yyyy",
        "verification": {
          "existence": "PASS",
          "content": "PASS",
          "retraction": "PASS"
        }
      }
    },
    {
      "claim_id": "C003",
      "claim_text": "This effect is universal across populations",
      "claim_type": "causal",
      "location": "Section 4.1, paragraph 1",
      "trace": {
        "status": "UNSUPPORTED",
        "reason": "No data supports universality claim; only tested on single population",
        "remediation": "Qualify claim to reflect actual sample, or remove"
      }
    }
  ],
  "unsupported_claims": [
    {
      "claim_id": "C003",
      "claim_text": "...",
      "location": "...",
      "remediation": "..."
    }
  ]
}
```

### Step 5: Verdict
- **PASS:** All claims fully traced
- **CONDITIONAL:** Some claims partially traced (missing intermediate step in data lineage)
- **FAIL:** Any claim unsupported

### Step 6: Auto-Healing
If FAIL or CONDITIONAL:
1. For unsupported claims: Search analysis outputs for supporting data
2. If no supporting data found: Flag as UNSUPPORTED, remove from manuscript
3. For partially traced claims: Complete the trace by finding missing intermediate files
4. Re-run claim tracer after fixes

---

## Integration
- Called by: `audit_validate` agent as Audit #7
- Uses: `claim_tracer.py` script
- Outputs to: `reports/audit/claim_trace_report.json`
- Blocks manuscript if: FAIL verdict
""",
    "audit_claim_tracer": """# Claim Tracer — Evidence Graph Builder

## Purpose
Builds a claim-to-evidence graph for the entire manuscript. Every factual claim must be traceable to either computed data or a verified citation. Any claim with a broken trace is flagged as UNSUPPORTED and blocked from final output.

## Invocation
Run by `audit_validate` agent as Audit #7 after the manuscript is compiled.

## Protocol

### Step 1: Extract All Claims from Manuscript
Parse the manuscript (`reports/manuscript/research_findings.md`) and identify all factual claims:

**Claim types:**
1. **Statistical claims:** "X is associated with Y (r=0.42, p<0.001)"
2. **Literature claims:** "Prior studies show effects between 0.3-0.5"
3. **Descriptive claims:** "The sample consisted of 1,234 participants"
4. **Methodological claims:** "We used a mixed-effects model following Bates et al. (2015)"
5. **Comparative claims:** "Our results are consistent with Smith et al. (2023)"

### Step 2: Trace Each Claim

For each claim, build a trace chain:

**Type A: Computed from Data**
```
Claim: "X is associated with Y (r=0.42)"
  └── Source: reports/analysis/q1/results.json (line 47)
      └── Input: data/03_analytical/analysis_q1.csv (hash: abc123)
          └── Raw: 00_inputs/raw_data/survey.csv (hash: def456)
              └── Script: scripts/02_analysis.py (function: compute_correlation)
```

**Type B: From Literature**
```
Claim: "Prior studies show effects between 0.3-0.5"
  └── Source: DOI:10.xxxx/yyyy (CrossRef verified ✓, content verified ✓)
      └── Abstract: Semantic Scholar API (fetched 2026-05-19)
      └── Corpus entry: reports/literature/literature_corpus.json (entry #12)
```

**Type C: From Web Search**
```
Claim: "Python 3.12 introduced a 10% speedup"
  └── Source: https://docs.python.org/3/whatsnew/3.12.html
      └── Search: reports/literature/search_log.json (entry #5)
      └── Verified: 2026-05-19 via Context7
```

### Step 3: Validate Traces

For each trace, verify:
1. **Source file exists** — the referenced file is present in the project
2. **Data hash matches** — the data file hasn't been modified since the claim was made
3. **Citation is verified** — if the claim cites a paper, it passed all 3 verification passes
4. **Number matches** — the statistic in the claim matches the computed value exactly

### Step 4: Build Report

Output: `reports/audit/claim_trace_report.json`

```json
{
  "schema_version": "1.0.0",
  "generated_at": "ISO 8601",
  "total_claims": 47,
  "summary": {
    "fully_traced": 42,
    "partially_traced": 3,
    "unsupported": 2
  },
  "verdict": "PASS|FAIL",
  "claims": [
    {
      "id": "claim_001",
      "text": "X is associated with Y (r=0.42, p=0.003)",
      "type": "statistical",
      "location": "research_findings.md:line_47",
      "trace": {
        "source_type": "computed_data",
        "source_file": "reports/analysis/q1/results.json",
        "data_file": "data/03_analytical/analysis_q1.csv",
        "data_hash": "abc123",
        "raw_file": "00_inputs/raw_data/survey.csv",
        "raw_hash": "def456",
        "script": "scripts/02_analysis.py",
        "verified": true
      },
      "status": "fully_traced"
    }
  ]
}
```

**Verdict Rules:**
- PASS: all claims fully traced
- FAIL: any claim is unsupported
- CONDITIONAL: some claims partially traced but none unsupported

### Step 5: Flag Unsupported Claims

Any claim that cannot be traced is flagged:
```
UNSUPPORTED CLAIM:
  Text: "..."
  Location: research_findings.md:line_X
  Reason: No source file found / citation not verified / data hash mismatch
  Action: Remove from manuscript or provide trace
```

## Integration

- Runs as part of `audit_validate` (Audit #7)
- Uses `citation_verification_report.json` from Audit #6
- Uses `data_lineage.json` for data hash verification
- Unsupported claims = gate FAIL
""",
    "quality_gate": """---
skill_id: "quality_gate"
version: "1.0.0"
category: "audit"
domain_compatibility: ["all"]
required_tools: ["python"]
depends_on: []
produces: ["docs/quality_gates/gate_XXX_[phase].md"]
complexity: "intermediate"
---

# Skill: Quality Gate Checks

## Purpose
Automated phase completion checks that prevent the pipeline from advancing until all requirements are met. Each phase has a checklist. The AI cannot proceed until the gate passes.

## When to Use
- After completing each pipeline phase
- Before moving to the next phase
- When the user asks "is this phase complete?"
- During audit to verify pipeline integrity

---

## Gate Definitions

### Gate 1: research_init
**File**: `docs/quality_gates/gate_001_research_init.md`

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Intake form is filled (no `[Your answer]` placeholders) | ☐ | |
| 2 | At least one research question is defined | ☐ | |
| 3 | Data files exist in 00_inputs/raw_data/ | ☐ | |
| 4 | Data files are readable (correct format, not corrupted) | ☐ | |
| 5 | Research map is created (reports/baseline/research_map.json) | ☐ | |
| 6 | Feasibility verdict is assigned (go/caution/stop) | ☐ | |
| 7 | Full directory structure is created (docs/, reports/, data/, scripts/) | ☐ | |
| 8 | README.md exists in every subdirectory | ☐ | |
| 9 | manifest.json is created and valid | ☐ | |
| 10 | research_log.md has first entry | ☐ | |
| 11 | Iteration registry is created | ☐ | |
| 12 | Follow-up questions generated if needed | ☐ | |

**Pass criteria**: All required checks (1-7) pass. Warnings (8-12) noted but don't block.

### Gate 2: literature_deep
**File**: `docs/quality_gates/gate_002_literature_deep.md`

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Literature corpus exists (reports/literature/literature_corpus.json) | ☐ | |
| 2 | Minimum paper count met (config: literature_min_papers, default 10) | ☐ | |
| 3 | Evidence matrix is created (reports/literature/evidence_matrix.md) | ☐ | |
| 4 | Each research question has mapped literature | ☐ | |
| 5 | Gap analysis is written | ☐ | |
| 6 | Papers are deduplicated | ☐ | |
| 7 | Citation information is complete (authors, year, title, DOI) | ☐ | |

**Pass criteria**: All checks pass. If paper count < minimum, gate fails with warning.

### Gate 3: method_route
**File**: `docs/quality_gates/gate_003_method_route.md`

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Analysis plan exists (reports/analysis/analysis_plan.md) | ☐ | |
| 2 | Each research question has assigned method | ☐ | |
| 3 | Method is appropriate for question type | ☐ | |
| 4 | Assumptions are listed for each method | ☐ | |
| 5 | Power analysis is conducted (if applicable) | ☐ | |
| 6 | Alternative methods considered and documented | ☐ | |
| 7 | Multiple testing correction plan is specified | ☐ | |

**Pass criteria**: All checks pass. Method must be justified for each question type.

### Gate 4: data_scaffold
**File**: `docs/quality_gates/gate_004_data_scaffold.md`

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Ingested data exists in data/01_ingested/ | ☐ | |
| 2 | Processed data exists in data/02_processed/ | ☐ | |
| 3 | Analytical datasets exist in data/03_analytical/ | ☐ | |
| 4 | Data lineage is recorded (docs/data_lineage.json) | ☐ | |
| 5 | Missingness is documented (< config: missingness_warning) | ☐ | |
| 6 | Outliers are identified and handled | ☐ | |
| 7 | Variable types are correct (numeric, categorical, etc.) | ☐ | |
| 8 | Analytical datasets have correct variables for each question | ☐ | |
| 9 | Data integrity check passes (raw hashes match) | ☐ | |

**Pass criteria**: All checks pass. Missingness > warning threshold requires documentation.

### Gate 5: execute_analysis
**File**: `docs/quality_gates/gate_005_execute_analysis.md`

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Results exist for ALL research questions | ☐ | |
| 2 | Each result has effect size with confidence interval | ☐ | |
| 3 | Each result has p-value (exact, not thresholded) | ☐ | |
| 4 | Assumption checks are performed and documented | ☐ | |
| 5 | Non-significant results reported with same detail | ☐ | |
| 6 | Figures are generated for each question | ☐ | |
| 7 | Tables are generated for each question | ☐ | |
| 8 | Results are compared to prior literature | ☐ | |
| 9 | Sensitivity analysis is performed | ☐ | |
| 10 | Robustness checks are documented | ☐ | |

**Pass criteria**: All checks pass. Missing results for any question = gate fails.

### Gate 6: compile_outputs
**File**: `docs/quality_gates/gate_006_compile_outputs.md`

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Manuscript draft exists (reports/manuscript/) | ☐ | |
| 2 | All required sections present (Intro, Methods, Results, Discussion, Limitations) | ☐ | |
| 3 | All figures referenced in manuscript | ☐ | |
| 4 | All tables referenced in manuscript | ☐ | |
| 5 | References are complete and formatted | ☐ | |
| 6 | Key findings summary exists (reports/summary/key_findings.md) | ☐ | |
| 7 | Executive summary exists (reports/summary/executive_summary.md) | ☐ | |
| 8 | Causal language audit passed (if causal analysis) | ☐ | |

**Pass criteria**: All checks pass. Missing sections = gate fails.

### Gate 7: audit_validate
**File**: `docs/quality_gates/gate_007_audit_validate.md`

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Full audit report exists (reports/audit/full_audit_report.md) | ☐ | |
| 2 | Statistical reporting audit passes | ☐ | |
| 3 | Reproducibility audit passes (scripts run end-to-end) | ☐ | |
| 4 | Code quality audit passes | ☐ | |
| 5 | Causal language audit passes (if applicable) | ☐ | |
| 6 | All previous gates passed | ☐ | |
| 7 | No unresolved follow-up questions | ☐ | |

**Pass criteria**: All checks pass. Any failed audit = gate fails.

---

## Gate Execution Protocol

### Step 1: Create Gate File
When a phase completes, create `docs/quality_gates/gate_XXX_[phase].md` with the checklist.

### Step 2: Evaluate Each Check
For each check:
- Mark ☑ if passed
- Mark ☐ if failed
- Add notes explaining why

### Step 3: Determine Gate Status
- **PASS**: All required checks passed
- **FAIL**: One or more required checks failed
- **WARN**: All required checks passed but warnings exist

### Step 4: Report to User
If gate fails:
1. List all failed checks
2. Explain what needs to be fixed
3. Do NOT proceed to next phase

If gate passes:
1. Confirm all checks passed
2. Note any warnings
3. Proceed to next phase

### Step 5: Record in Research Log
Append gate result to `docs/research_log.md`:
```markdown
### [Date] — Quality Gate: [phase]
- **Status**: PASS / FAIL / WARN
- **Checks**: X/Y passed
- **Failed**: [list if any]
- **Warnings**: [list if any]
```

---

## CLI Integration

`rcp status` — Run state and quality gate check.

---

## Validation Checklist
- [ ] Gate file created for the phase
- [ ] All checks evaluated with status
- [ ] Gate status determined (PASS/FAIL/WARN)
- [ ] Result recorded in research log
- [ ] User informed of gate status
- [ ] Pipeline blocked if gate fails
""",
    "audit_figure_completeness": """---
skill_id: "audit_figure_completeness"
version: "2.0.0"
category: "audit"
domain_compatibility: ["all"]
required_tools: ["python", "os", "re"]
estimated_tokens: 2500
depends_on: ["write_imrad"]
produces: ["figure_completeness_report.json"]
---

# Skill: Audit Figure Completeness

## Purpose
Verify that all figures referenced in text exist and have appropriate captions.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `manuscript_path` | Path | Yes | Path to manuscript |
| `figures_dir` | Path | Yes | Path to figures directory |

## Execution Protocol

### Step 1: Reference Extraction
- Extract all 'Figure X' references from manuscript

### Step 2: File Verification
- Check that `figures_dir` contains files corresponding to each reference

### Step 3: Caption Check
- Ensure every figure has a descriptive caption in the markdown

## Output Specification
- Mapping of references to files

## Validation Criteria
- [ ] Every referenced figure must physically exist
- [ ] Every figure file must be referenced at least once in text
""",
    "audit_causal_language": """---
skill_id: "audit_causal_language"
version: "7.0.0"
category: "audit"
domain_compatibility: ["all"]
required_tools: ["python", "openai|anthropic|litellm"]
depends_on: ["causal_inference"]
produces: ["audit/causal_language_audit.json"]
complexity: "intermediate"
---

# Skill: Causal Language Audit

## Purpose
Scan manuscript text for causal claims that are not justified by the study design, and flag overstatements.

## When to Use
- After manuscript written
- Before submission
- When study is observational (not experimental)

## When NOT to Use
- Study is a randomized experiment (causal language is appropriate)
- Only descriptive analysis (no claims made)

## Execution Protocol

### Step 1: Claim Extraction
- Scan all sections (abstract, results, discussion, conclusion)
- Extract sentences containing causal language:
  - Strong: "causes", "leads to", "results in", "produces", "effect of"
  - Moderate: "associated with", "predicts", "related to", "influences"
  - Weak: "linked to", "corresponds to", "co-occurs with"

### Step 2: Design Assessment
- Classify study design: RCT, quasi-experimental, observational, cross-sectional
- Determine justified causal strength:
  - RCT: strong causal claims justified
  - Quasi-experimental: moderate causal claims (with caveats)
  - Observational: associational language only
  - Cross-sectional: correlational language only

### Step 3: Mismatch Detection
- Compare claim strength to design-justified strength
- Flag: claims stronger than design supports
- For each flagged claim: suggest alternative wording

### Step 4: Confounding Acknowledgment
- Check: does discussion acknowledge potential confounding?
- Check: are alternative explanations considered?
- Check: limitations section addresses causal inference limits

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| No overclaims | All claims ≤ design strength | Rewrite flagged sentences |
| Confounding acknowledged | Yes | Add to limitations |
| Alternative explanations | ≥ 2 discussed | Add to discussion |

## Output Specification
- `audit/causal_language_audit.json`: flagged claims, suggested rewrites, design assessment

## Validation Checks
- [ ] All sections scanned
- [ ] Flagged claims have suggested alternatives
- [ ] Design correctly classified
- [ ] Confounding acknowledged in limitations
""",
    "audit_citations": """# Skill: Audit Citations

> Audit #6: Three-pass citation verification as part of `audit_validate` pipeline.

## Purpose
Verify every citation in the manuscript through three passes: existence, content, and retraction. All three passes must pass for a PASS verdict.

---

## Protocol

### Step 1: Extract Citations from Manuscript
1. Read `reports/manuscript/research_findings.md`
2. Extract all DOIs, arXiv IDs, and PubMed IDs using regex
3. Cross-reference with `reports/literature/bibliography.bib`
4. Build citation list: `{doi, arxiv_id, pubmed_id, claim_text, location_in_manuscript}`

### Step 2: Pass 1 — Existence Check
For every citation:

#### DOI Verification
1. Call CrossRef API: `https://api.crossref.org/works/{doi}`
2. Verify: title, authors, year match claimed citation
3. Flag: any DOI returning 404 or metadata mismatch

#### arXiv Verification
1. Call arXiv API: `http://export.arxiv.org/api/query?id_list={arxiv_id}`
2. Verify: title, authors, year match claimed citation
3. Flag: any arXiv ID not found

#### PubMed Verification
1. Call NCBI E-utilities: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pubmed_id}`
2. Verify: title, authors, year match claimed citation
3. Flag: any PubMed ID not found

**Output:** `reports/literature/citation_verification_report.json` with `existence_check` status per citation

### Step 3: Pass 2 — Content Verification
For each citation used to support a claim:

1. Fetch abstract from Semantic Scholar API
2. Run validation: "Does this abstract support the claim '[claim text]'?"
3. Response options: YES / NO / PARTIAL with 1-sentence justification
4. Flag PARTIAL or NO responses for human review
5. Never use a citation that fails Pass 2 without explicit `[UNVERIFIED]` tag

**Output:** Update `citation_verification_report.json` with `content_check` status

### Step 4: Pass 3 — Retraction Check
For every cited paper:

1. Query Retraction Watch database API
2. Query CrossRef for retraction notices linked to DOI
3. **Hard block:** Retracted papers cannot appear as supporting evidence
4. **Warn:** Papers with expressions of concern

**Output:** Update `citation_verification_report.json` with `retraction_check` status

### Step 5: Generate Verification Report
Create `reports/literature/citation_verification_report.json`:

```json
{
  "schema_version": "1.0.0",
  "timestamp": "ISO 8601",
  "total_citations": 45,
  "summary": {
    "all_pass": 38,
    "existence_fail": 2,
    "content_fail": 3,
    "content_partial": 2,
    "retracted": 0,
    "expression_of_concern": 1
  },
  "citations": [
    {
      "doi": "10.xxxx/yyyy",
      "title": "Paper title",
      "existence_check": {"status": "PASS", "verified_title": "...", "verified_year": 2024},
      "content_check": {"status": "PASS", "supports_claim": true, "justification": "..."},
      "retraction_check": {"status": "PASS", "retracted": false},
      "overall_status": "VERIFIED",
      "location_in_manuscript": "Section 3.2, paragraph 2"
    }
  ],
  "failures": [
    {
      "doi": "10.xxxx/zzzz",
      "failure_type": "existence_fail",
      "reason": "DOI returns 404",
      "remediation": "Search CrossRef by title+author, find correct DOI"
    }
  ]
}
```

### Step 6: Verdict
- **PASS:** All citations verified (existence + content + retraction)
- **CONDITIONAL:** Some citations partial_match or expression_of_concern
- **FAIL:** Any citation retracted, or >10% unverified

### Step 7: Auto-Healing
If FAIL or CONDITIONAL:
1. For existence failures: Search CrossRef by title+author, find correct DOI
2. For content mismatches: Remove citation from claim, flag for manual replacement
3. For retractions: Remove citation from manuscript entirely, find replacement
4. Re-run verification after fixes

---

## Integration
- Called by: `audit_validate` agent as Audit #6
- Uses: `citation_verifier.py` script
- Outputs to: `reports/literature/citation_verification_report.json`
- Blocks manuscript if: FAIL verdict
""",
    "audit_statistical_reporting": """---
skill_id: "audit_statistical_reporting"
version: "7.0.0"
category: "audit"
domain_compatibility: ["all"]
required_tools: ["python", "openai|anthropic|litellm"]
depends_on: ["write_imrad"]
produces: ["audit/statistical_reporting_audit.json"]
complexity: "intermediate"
---

# Skill: Statistical Reporting Audit

## Purpose
Verify that all statistical results are reported completely and correctly: test statistics, degrees of freedom, p-values, effect sizes, and confidence intervals.

## When to Use
- After manuscript written
- Before submission
- For quality assurance

## When NOT to Use
- Manuscript not yet complete
- Only exploratory analysis

## Execution Protocol

### Step 1: Completeness Check
For each reported statistical test, verify presence of:
- Test name (e.g., "independent-samples t-test")
- Test statistic value (e.g., t = 2.34)
- Degrees of freedom (e.g., df = 48)
- Exact p-value (e.g., p = .023, not p < .05)
- Effect size (e.g., d = 0.67)
- 95% confidence interval for effect size

### Step 2: Consistency Check
- Values in text match values in tables
- Values in tables match values in analysis output
- Percentages sum to 100% (or noted otherwise)
- Sample sizes consistent across sections

### Step 3: Formatting Check
- p-values: italicized, no leading zero (p = .023)
- Statistics: italicized (t, F, χ², r, β)
- Degrees of freedom: in parentheses, not italicized
- Effect sizes: reported with interpretation benchmarks
- Confidence intervals: square brackets, 95% specified

### Step 4: Multiple Testing Check
- If multiple tests: correction method stated
- Adjusted p-values reported alongside raw p-values
- Family-wise error rate or FDR controlled

### Step 5: Assumption Reporting
- For parametric tests: normality and homoscedasticity checks reported
- For regression: multicollinearity, residual diagnostics reported
- For violations: alternative methods or robust SEs stated

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| Completeness | All 6 elements present | Add missing elements |
| Consistency | All values match | Correct discrepancies |
| Formatting | APA/domain style | Fix formatting |
| Multiple testing | Correction applied | Add correction or justify |

## Output Specification
- `audit/statistical_reporting_audit.json`: per-test completeness, consistency, formatting results

## Validation Checks
- [ ] Every statistical test has all required elements
- [ ] No value discrepancies between text and tables
- [ ] Formatting follows domain standard
- [ ] Multiple testing addressed
""",
    "eli5_explainer": """---
skill_id: "eli5_explainer"
version: "1.0.0"
category: "writing"
description: "Generate layman-friendly explanations of research findings, assumptions, and statistical concepts"
domain_compatibility: ["all"]
applies_to_phases: ["execute_analysis", "compile_outputs"]
---

# Skill: ELI5 Explainer (Explain Like I'm 5)

## Purpose

Generate beginner-friendly explanations alongside technical research outputs. This skill ensures that research findings are accessible to non-experts, students, and stakeholders who may not understand statistical jargon.

## When to Use

- When the target audience includes non-researchers
- When generating dashboards for stakeholders
- When the intake indicates a student or beginner user
- When creating `layman_summary.md` alongside `executive_summary.md`

## Protocol

### Step 1: Identify Technical Concepts

Scan the research findings for:
- Statistical tests (t-test, ANOVA, regression, etc.)
- Technical terms (heteroskedasticity, multicollinearity, etc.)
- Numerical results (p-values, effect sizes, confidence intervals)
- Methodological concepts (randomization, control groups, etc.)

### Step 2: Generate Plain-English Explanations

For each technical concept, create a plain-English explanation using these patterns:

#### Statistical Significance
**Technical**: "The effect was statistically significant (p < 0.05)"
**ELI5**: "We're confident this result isn't just random chance. If there were truly no effect, we'd see a result this extreme less than 5% of the time."

#### Effect Size
**Technical**: "Cohen's d = 0.5, 95% CI [0.2, 0.8]"
**ELI5**: "The difference is moderate — about half a standard deviation. We're 95% confident the true effect is between small (0.2) and large (0.8)."

#### Heteroskedasticity
**Technical**: "Heteroskedasticity detected (Breusch-Pagan p < 0.01)"
**ELI5**: "The spread of our prediction errors isn't consistent — our model is less certain for some values than others. This doesn't mean the results are wrong, but our confidence intervals might be too narrow."

#### Multicollinearity
**Technical**: "VIF > 10 for predictors X and Y"
**ELI5**: "Two of our input variables are so similar that the model can't tell which one is actually driving the result. It's like trying to figure out which twin committed a crime when they look identical."

#### R-squared
**Technical**: "R² = 0.45"
**ELI5**: "Our model explains 45% of the variation in the outcome. The other 55% is due to factors we didn't measure or random variation."

#### Confidence Interval
**Technical**: "95% CI [1.2, 3.4]"
**ELI5**: "If we repeated this study 100 times, about 95 of those studies would find an effect between 1.2 and 3.4. We can't be 100% sure, but we're pretty confident it's in this range."

#### P-value
**Technical**: "p = 0.03"
**ELI5**: "If there were truly no effect at all, there's only a 3% chance we'd see results this extreme just by random luck. That's pretty unlikely, so we think there's probably a real effect."

### Step 3: Generate Visual Explanations

For key findings, create simple visualizations that show WHY:

#### Why an Assumption Failed
Instead of just "Heteroskedasticity detected," create:
1. A residual plot showing the fan shape
2. An annotation: "See how the spread gets wider as X increases? That's heteroskedasticity."
3. A simple analogy: "Like a cone — narrow at one end, wide at the other."

#### Why a Result is Significant
1. Show the null distribution (what we'd expect if nothing was happening)
2. Mark where the observed result falls
3. Shade the area that represents the p-value
4. Annotate: "Our result is way out here — very unlikely to happen by chance"

#### Causal Diagram (DAG)
1. Draw simple boxes and arrows showing relationships
2. Use color: green for measured, red for unmeasured confounders
3. Annotate: "This arrow from Z to both X and Y means Z could be creating a fake relationship"

### Step 4: Generate layman_summary.md

Create `reports/summary/layman_summary.md` with this structure:

```markdown
# Research Findings — Plain English Summary

## What We Wanted to Know
[One sentence in plain language]

## What We Found
[Key findings in plain language, with ELI5 explanations]

## How Confident We Are
[Confidence level explained simply]

## What This Means
[Practical implications]

## What We Don't Know
[Limitations explained simply]

## What to Do Next
[Recommendations in plain language]

## Glossary
[Simple definitions of any technical terms used]
```

### Step 5: Interactive Dashboard Annotations

For the research dashboard, add ELI5 tooltips:
- Every statistical term gets a hover explanation
- Every plot has a "What am I looking at?" button
- Results are accompanied by "In plain English:" callouts

## Quality Rules

1. NEVER use jargon without immediately explaining it
2. ALWAYS use analogies that relate to everyday experience
3. NEVER oversimplify to the point of being wrong
4. ALWAYS preserve the uncertainty — don't make findings sound more certain than they are
5. ALWAYS include the "why" not just the "what"
6. Use short sentences (max 20 words)
7. Use active voice
8. Avoid acronyms without spelling them out first
""",
    "export_latex": """# Skill: Export LaTeX

> Converts `research_findings.md` to publication-ready LaTeX manuscript.

## Purpose
Transform the assembled markdown manuscript into a LaTeX document formatted for academic publication.

---

## Protocol

### Step 1: Select Template
Load domain config from `.research/domains/<domain>.yaml`. Priority: user-specified → domain default → `article`.

| Domain | Template |
|--------|----------|
| Default | `article` |
| Physics/Astronomy | `revtex4-2` |
| Elsevier | `elsarticle` |
| APA | `apa7` |
| PNAS | `pnas-new` |

### Step 2: Convert with Pandoc
Run pandoc with `--citeproc --bibliography=<bib_path> --standalone`. Use a Lua filter to wrap images in figure environments and convert tables to booktabs format.

### Step 3: Handle Figures
- Single column: `\\includegraphics[width=\\linewidth]{path}`
- Double column (width > `\\columnwidth`): use `\\begin{figure*}...\\end{figure*}` (starred, floats to next page top)
- Multi-panel: use `subcaption` package, each subfigure gets its own `\\label{}`, main caption references "(A) ... (B) ..."
- Wide tables exceeding page width: use `sidewaystable` from `rotating` package
- Supplementary items: place after `\\appendix`, label as S1, S2, etc.

### Step 4: Handle Tables
Convert to booktabs: `\\toprule`, `\\midrule`, `\\bottomrule`. No vertical lines. For number formatting, use `siunitx` with `S` column type and `{}` wrapped headers.

### Step 5: Handle Bibliography
Convert citations to `\\cite{}`. Generate `.bib` from `literature_corpus.json`. Styles: APA→`apalike`, Nature→`nature`, ACS→`achemso`, default→`plainnat`.

### Step 6: Preamble
Include: `graphicx`, `subcaption`, `booktabs`, `rotating`, `threeparttable`, `siunitx`, `longtable`, `appendix`, `float`, `amssymb`, `hyperref`. Set `pdf.fonttype = 42` for font embedding.

### Step 7: Compile
Run `pdflatex` → `bibtex` → `pdflatex` → `pdflatex` (3 passes for cross-refs). Max 3 attempts. Log errors to `docs/dead_ends/`.

## Output
- `reports/manuscript/manuscript.tex`
- `reports/manuscript/manuscript.bib`
- `reports/manuscript/manuscript.pdf` (if pdflatex available)

## Validation
- [ ] All `\\cite{}` resolved (no `??`)
- [ ] All `\\ref{}` resolved
- [ ] No vertical lines in tables
- [ ] Figures use booktabs
- [ ] PDF compiles without errors
""",
    "policy_brief": """---
skill_id: "policy_brief"
version: "1.0.0"
category: "writing"
depends_on: ["abstract_generator", "results_table_generator"]
produces: ["03_synthesis/policy_brief.md", "03_synthesis/policy_brief.html"]
complexity: "quick"
---

# Skill: Policy Brief Generator

## Purpose
2-page policy brief for decision-makers. Zero jargon. Action-focused. Distinct from executive_summary — shorter and recommendation-driven.

---

## Protocol

### Step 1: Gather Inputs
`key_findings.json`, method summary, effect sizes, sample info, one key figure.

### Step 2: Generate Structure

**Headline Finding** (1 sentence): The single most important result, stated in plain language with one key number.

**Context** (~50 words): What problem does this address? Why does it matter now? No academic framing.

**Evidence** (3 bullets): Each bullet: finding + effect size in plain terms + practical implication. Example: "Program participants earned 12% more ($2,400/year) than non-participants, with effects largest for first-generation workers."

**Recommendations** (3 bullets): Action-oriented, specific, grounded in evidence. Each ties to a specific finding. Example: "Expand eligibility to first-generation workers, where effects are 2× larger."

**Caveats** (2 bullets): Honest limitations that affect implementation. Example: "Results based on one state; effects may differ in rural areas."

### Step 3: Generate Markdown
Format with clear headings, bullet lists, one embedded figure with caption. Total: ~400 words, fits on 2 pages.

### Step 4: Generate HTML
Print-ready HTML with clean typography, page break after first page, figure centered, footer with source citation. `@media print` rules for clean printing.

### Step 5: Quality Rules
- Zero jargon: no "regression," "p-value," "coefficient," "heteroscedasticity"
- Use plain numbers: "12% more" not "β = 0.12"
- Every claim traceable to a source file
- One figure maximum — the most policy-relevant one
- Recommendations must be grounded in findings, not speculation

---

## Output
- `03_synthesis/policy_brief.md` — Markdown source
- `03_synthesis/policy_brief.html` — Print-ready HTML

## Validation
- [ ] Headline finding is 1 sentence
- [ ] Context ≤ 50 words
- [ ] Exactly 3 evidence bullets with effect sizes
- [ ] Exactly 3 recommendations
- [ ] Exactly 2 caveats
- [ ] Zero statistical jargon
- [ ] One figure included
- [ ] Every claim has source file
- [ ] Total ≤ 400 words
""",
    "paper_compiler": """---
skill_id: "paper_compiler"
version: "1.0.0"
category: "writing"
depends_on: ["export_latex", "write_imrad", "generate_apa_tables"]
produces: ["03_synthesis/manuscript/paper.pdf"]
complexity: "standard"
---

# Skill: Paper Compiler

## Purpose
Takes assembled manuscript, figure metadata, and bibliography, then compiles a submission-ready PDF.

---

## Protocol

### Step 1: Validate Figures
Check all expected figures exist at 300 DPI. Use PIL to open PNG/JPG and check `dpi` info (must be ≥300). PDF figures are vector — skip DPI check. Missing figures = halt compilation. Low DPI = warning but proceed.

### Step 2: Assemble Manuscript
Collect from `03_synthesis/manuscript/`: `research_findings.md` (main body), each figure's `.meta.yaml` (captions), `bibliography.bib`, `global_methods.md`.

### Step 3: Convert to LaTeX
Run pandoc: `--standalone --citeproc --bibliography=<bib> --cite-method=biblatex --lua-filter=latex_filter.lua`. The Lua filter wraps images in figure environments and converts tables to booktabs.

### Step 4: Insert Figure Environments
For each figure, insert `\\begin{figure}[htbp]` with `\\includegraphics`, caption from `.meta.yaml` or `.interpret.md`, and `\\label{}`. Caption priority: `.interpret.md` > `.meta.yaml` > auto-generated.

### Step 5: Compile PDF
Run: `pdflatex` → `bibtex` → `pdflatex` → `pdflatex` (3 passes for cross-references). Use `-interaction=nonstopmode`.

### Step 6: Validate
Check PDF exists and is non-empty. Verify no `??` unresolved references. Check `.log` for overfull/underfull hbox warnings.

---

## Output
- `03_synthesis/manuscript/paper.pdf`
- `03_synthesis/manuscript/manuscript.tex`
- `03_synthesis/manuscript/compilation_report.json`

## Validation
- [ ] All figures at 300 DPI or vector PDF
- [ ] Bibliography resolves all citations
- [ ] No `??` in output
- [ ] PDF compiles without errors (max 3 attempts)
- [ ] Figure captions include statistical annotations
- [ ] Tables use booktabs (no vertical lines)

## Error Handling
Missing figure → halt and report. Low DPI → compile with warning. BibTeX error → fix common issues (missing braces). pdflatex not found → output `.tex` only. Unresolved refs → run third pass, report remaining.
""",
    "write_results_narrative": """---
skill_id: "write_results_narrative"
version: "7.0.0"
category: "writing"
domain_compatibility: ["all"]
required_tools: ["python", "openai|anthropic|litellm"]
depends_on: ["inferential_parametric", "inferential_nonparametric", "descriptive_stats"]
produces: ["reports/sections/results_section.md"]
complexity: "intermediate"
---

# Skill: Write Results Narrative

## Purpose
Generate a structured results narrative reporting descriptive statistics, inferential test results, effect sizes, and diagnostic findings in domain-appropriate prose.

## When to Use
- After all analysis completed
- Before discussion section
- For manuscript assembly

## When NOT to Use
- Only tables/figures needed
- Results not yet computed

## Execution Protocol

### Step 1: Descriptive Results
- Sample characteristics: N, demographics, key variable summaries
- Table 1 reference: "Baseline characteristics are shown in Table 1"
- Note any data quality issues: missingness, outliers, exclusions

### Step 2: Primary Analysis
- Report each hypothesis test in order of importance
- Format: test name, statistic, df, p-value, effect size, 95% CI
- State: direction and magnitude of effect
- Interpret: in substantive (not statistical) terms

### Step 3: Secondary Analysis
- Exploratory analyses: clearly labeled as such
- Subgroup analyses: which subgroups, why tested
- Sensitivity analyses: alternative specifications and whether conclusions change

### Step 4: Diagnostic Results
- Assumption test results: normality, homoscedasticity, independence
- Model fit: R², AIC, convergence diagnostics
- Note: any assumption violations and how addressed

### Step 5: Non-Significant Results
- Report non-significant findings with same detail as significant
- Include: effect size and CI (not just "p > .05")
- Interpret: whether CI rules out meaningful effects

## Reporting Rules
- Always report exact p-values (not just < .05), except p < .001
- Always report effect sizes with CIs
- Never interpret non-significant as "no effect"
- Distinguish: statistical significance vs practical significance
- Label: exploratory vs confirmatory analyses

## Output Specification
- `reports/sections/results_section.md`: complete results narrative with table/figure references

## Validation Checks
- [ ] All hypothesis tests reported
- [ ] Effect sizes and CIs included
- [ ] Non-significant results reported
- [ ] Diagnostic results included
- [ ] Table and figure references correct
""",
    "write_imrad": """---
skill_id: "write_imrad"
version: "7.0.0"
category: "writing"
domain_compatibility: ["all"]
required_tools: ["python", "openai|anthropic|litellm", "pandoc"]
depends_on: ["write_methods_section", "write_results_narrative", "synthesize_literature", "generate_bibtex"]
produces: ["reports/research_findings.md"]
complexity: "advanced"
---

# Skill: Write IMRAD Manuscript

## Purpose
Assemble a complete IMRAD-format academic manuscript from component sections, with integrated literature review, results interpretation, and formatted references.

## When to Use
- All component sections written
- Final manuscript assembly
- Ready for submission or review

## When NOT to Use
- Sections not yet complete
- Only a report (not manuscript) needed

## Execution Protocol

### Step 1: Introduction
- Context: background and significance
- Literature gap: what is unknown (from literature synthesis)
- Research question: clearly stated
- Hypotheses: specific and testable
- Objectives: primary and secondary

### Step 2: Methods
- Insert methods_section.md
- Verify: all analysis methods described
- Verify: ethical considerations included

### Step 3: Results
- Insert results_section.md
- Verify: all hypotheses addressed
- Verify: tables and figures referenced correctly
- Add: table and figure captions

### Step 4: Discussion
- Interpret findings: what do results mean?
- Compare to literature: consistent or contradictory with prior work?
- Mechanisms: plausible explanations for findings
- Limitations: statistical, methodological, generalizability
- Implications: theoretical, practical, policy
- Future research: specific directions

### Step 5: References
- Insert formatted references from references.bib
- Use pandoc-citeproc for citation formatting
- Verify: all in-text citations have reference entries
- Verify: all reference entries cited in text

### Step 6: Final Checks
- Title: concise, informative, includes key variables
- Abstract: structured (Background, Methods, Results, Conclusion)
- Keywords: 3-6 domain-appropriate terms
- Word count: within journal limits
- Formatting: journal-specific style guide

## Output Specification
- `reports/research_findings.md`: complete IMRAD manuscript

## Validation Checks
- [ ] All four IMRAD sections present
- [ ] In-text citations match reference list
- [ ] Tables and figures referenced
- [ ] Abstract matches manuscript content
- [ ] Word count within limits
""",
    "results_table_generator": """---
skill_id: "results_table_generator"
version: "1.0.0"
category: "writing"
depends_on: ["execute_analysis"]
produces: ["03_synthesis/tables/results_table.md", "03_synthesis/tables/results_table.tex", "03_synthesis/tables/results_table.html"]
complexity: "quick"
---

# Skill: Results Table Generator

## Purpose
Auto-generates APA/journal-formatted results tables from analysis JSON files. Three output formats from one data source.

---

## Protocol

### Step 1: Scan
Find all `*_results.json` in `02_experiments/*/outputs/analysis/`.

### Step 2: Extract Data
Parse each JSON for: variable name (`variable`/`predictor`/`term`), coefficient (`coef`/`estimate`/`beta`/`b`), SE (`se`/`std_err`), 95% CI (`ci_lower`/`ci_upper`), p-value (`pvalue`/`p_value`/`p`), N (`nobs`/`n`).

### Step 3: Classify Table Type
- **Regression**: has `coef`, `se`, `pvalue` per predictor → coefficient table with CI
- **ANOVA**: has `source`, `df`, `F`, `pvalue` per term → ANOVA summary
- **Descriptive**: has `mean`, `sd`, `min`, `max`, `n` per variable → descriptive statistics

### Step 4: Generate Markdown
GitHub-flavored table with columns: Variable, *b*, *SE*, 95% CI, *p*. Italicize statistics. Note below table: N, model fit (R², F, df, p). Significance footnote: *p* < .05, **p* < .01, ***p* < .001.

### Step 5: Generate LaTeX (booktabs)
`\\begin{table}` with `\\toprule`, `\\midrule`, `\\bottomrule`. No vertical lines. Negative signs use `$-$`. Italicize statistics. Use `tablenotes` for footnotes. Column alignment: left for variables, right for numbers.

### Step 6: Generate HTML
Styled table with `<caption>`, `<thead>`, `<tbody>`. No inline styles. Use CSS class `results-table`. Footnote paragraph below table with significance legend.

### Step 7: Format p-values
0.000 → `< .001`. 0.001-0.009 → `< .01`. 0.010-0.999 → exact, 3 decimals. No leading zero.

### Step 8: Write Output
Save all three formats to `03_synthesis/tables/`. Write `table_manifest.json` indexing all tables with source files.

---

## Validation
- [ ] No vertical lines in any format
- [ ] Significance footnote present
- [ ] All coefficients have SE and CI
- [ ] p-values formatted correctly (no leading zero, 3 decimals)
- [ ] Table number and title present
- [ ] Model fit statistics in note
""",
    "write_executive_summary": """---
skill_id: "write_executive_summary"
version: "7.0.0"
category: "writing"
domain_compatibility: ["all"]
required_tools: ["python", "openai|anthropic|litellm"]
depends_on: ["write_results_narrative"]
produces: ["reports/executive_summary.md"]
complexity: "basic"
---

# Skill: Write Executive Summary

## Purpose
Generate a concise, non-technical summary of research findings for stakeholders, policymakers, or decision-makers.

## When to Use
- Results finalized
- Need to communicate to non-research audience
- Policy brief or briefing document

## When NOT to Use
- Only academic audience
- Results preliminary

## Execution Protocol

### Step 1: Key Findings
- 3-5 main findings in plain language
- Each finding: what was found, how big the effect is, confidence level
- No statistical jargon: no p-values, CIs, or test names

### Step 2: Context
- Why this research matters
- What question was asked
- How it was studied (one sentence)

### Step 3: Implications
- What the findings mean for practice or policy
- Recommended actions (if applicable)
- Caveats: limitations in plain language

### Step 4: Format
- Length: 1-2 pages maximum
- Structure: headings, bullet points, short paragraphs
- Visual: include 1-2 key figures (simplified)

## Output Specification
- `reports/executive_summary.md`: plain-language summary

## Validation Checks
- [ ] No statistical jargon
- [ ] All findings supported by results
- [ ] Limitations acknowledged
- [ ] Length ≤ 2 pages
""",
    "methods_checklist": """---
skill_id: "methods_checklist"
version: "1.0.0"
category: "writing"
depends_on: ["compile_outputs"]
produces: ["03_synthesis/methods_checklist.md"]
complexity: "quick"
---

# Skill: Methods Checklist

## Purpose
Generate a pre-submission checklist mapped to the reporting standard. Each item: requirement, status (yes/no/partial), location in manuscript if yes.

---

## Protocol

### Step 1: Detect Reporting Standard
From domain config or study design:
- Observational cohort/case-control → **STROBE** (22 items)
- Randomized trial → **CONSORT** (25 items)
- Systematic review → **PRISMA** (27 items)
- APA empirical study → **APA JARS** (18 items)
- Diagnostic accuracy → **STARD** (30 items)
- Default → **APA** general

### Step 2: Scan Manuscript
Read `03_synthesis/manuscript/`. For each checklist item, search for evidence:
- **Yes**: keyword/phrase found in manuscript (note section and line)
- **Partial**: partial evidence (e.g., mentions limitation but no sensitivity analysis)
- **No**: no evidence found

### Step 3: Generate Checklist
Format as markdown table:

| # | Requirement | Status | Location | Notes |
|---|------------|--------|----------|-------|
| 1 | Study design stated | Yes | Methods, para 1 | "prospective cohort" |
| 2 | Setting described | Yes | Methods, para 2 | Location, dates |
| 3 | Participants eligibility | Partial | Methods, para 3 | Inclusion stated, exclusion missing |

### Step 4: Summary
At end: "X of Y items met, Z partial, W missing." List missing items as action items.

---

## STROBE Key Items (22 total)
Title/abstract, background, objectives, study design, setting, participants, variables, data sources, bias, study size, quantitative variables, statistical methods, participants flow, descriptive data, outcome data, main results, other analyses, key results, limitations, interpretation, generalizability, funding.

## CONSORT Key Items (25 total)
Title/abstract, background, trial design, participants, interventions, outcomes, sample size, randomization, blinding, statistical methods, participant flow, recruitment, baseline data, numbers analyzed, outcomes/estimation, ancillary analyses, harms, limitations, generalizability, interpretation, trial registration, protocol access, funding.

## PRISMA Key Items (27 total)
Title, abstract, rationale, objectives, eligibility, information sources, search strategy, selection process, data collection, items, risk of bias, synthesis methods, reporting bias, certainty assessment, study selection, study characteristics, risk of bias in studies, results of syntheses, reporting biases, certainty of evidence, discussion, limitations, conclusions, registration, protocol, support, competing interests.

---

## Validation
- [ ] Reporting standard detected
- [ ] All checklist items evaluated
- [ ] Each item has status (yes/no/partial)
- [ ] Yes/partial items have manuscript location
- [ ] Summary counts provided
- [ ] Missing items listed as action items
- [ ] Output saved to `03_synthesis/methods_checklist.md`
""",
    "journal_formatter": """# Skill: Journal Formatter

> Reformats assembled manuscript for a specific journal's requirements.

## Purpose
Take the assembled manuscript and adapt it to meet a specific journal's submission guidelines.

---

## Protocol

### Step 1: Load Manuscript and Target Journal
1. Read `reports/manuscript/research_findings.md`
2. Load target journal specification (from user input or domain config)
3. Load journal requirements from internal database

### Step 2: Check Word Count Compliance
1. Count words in each section:
   - Abstract
   - Main text (Introduction through Discussion)
   - References
2. Compare against journal limits:
   - **Nature family**: Abstract ≤150 words, Main text ≤3000 words
   - **Lancet family**: Abstract ≤300 words, Main text ≤3500 words
   - **PLOS family**: No strict limit, but ≤6000 recommended
   - **APA journals**: Abstract ≤250 words, varies by journal
   - **AEA journals**: Abstract ≤150 words, varies by journal
   - **Elsevier general**: Varies by journal, check specific guidelines
3. If over limit:
   - Flag sections needing compression
   - Suggest specific cuts (redundant text, verbose explanations)
   - Do NOT auto-truncate without user approval

### Step 3: Format Abstract
1. Check abstract structure requirements:
   - **Structured** (Background, Methods, Results, Conclusion): Nature, Lancet, PLOS
   - **Unstructured** (single paragraph): APA, many Elsevier journals
2. Reformat abstract to match target structure
3. Verify abstract word limit compliance

### Step 4: Convert Reference Format
1. Load bibliography from `reports/literature/bibliography.bib`
2. Convert to target citation style:
   - **Vancouver**: Numbered, author-title-journal-year-volume-pages
   - **APA**: Author-date, italicized journal and volume
   - **AMA**: Superscript numbers, specific punctuation
   - **Nature**: Superscript numbers, abbreviated journal names
   - **ACS**: Varied (superscript, numbered, or author-year)
3. Use Pandoc or CSL processor for conversion:
   ```bash
   pandoc manuscript.md -o manuscript_formatted.md \\
     --citeproc \\
     --csl=<journal_csl_style.csl>
   ```
4. Verify all references are present and correctly formatted

### Step 5: Format Figure Numbering and Captions
1. Check journal figure requirements:
   - Numbering style (Figure 1, Fig. 1, Figure 1.)
   - Caption placement (below figure, separate file)
   - Caption format (legend style, bold labels)
   - Resolution requirements (typically 300+ DPI)
2. Reformat all figure references and captions
3. Generate figure submission checklist

### Step 6: Organize Supplementary Materials
1. Identify content that should move to supplementary:
   - Additional analyses
   - Robustness checks
   - Extended tables
   - Additional figures
2. Create `reports/manuscript/supplementary/` directory
3. Generate supplementary material document

### Step 7: Generate Cover Letter
Create `reports/manuscript/cover_letter.md`:
1. Address to journal editor
2. Include:
   - Manuscript title
   - Brief summary of findings
   - Statement of novelty and significance
   - Confirmation of originality (not under consideration elsewhere)
   - Suggested reviewers (if requested)
   - Conflict of interest statement
3. Use journal-appropriate tone and format

### Step 8: Generate Submission Checklist
Create `reports/manuscript/submission_checklist.md`:

| Item | Status |
|------|--------|
| Word count within limits | ✓/✗ |
| Abstract formatted correctly | ✓/✗ |
| References in correct style | ✓/✗ |
| Figures meet resolution requirements | ✓/✗ |
| Figure captions formatted | ✓/✗ |
| Tables formatted | ✓/✗ |
| Supplementary materials organized | ✓/✗ |
| Cover letter drafted | ✓/✗ |
| Conflict of interest statement | ✓/✗ |
| Data availability statement | ✓/✗ |
| Ethics approval statement | ✓/✗ |
| Author contributions statement | ✓/✗ |

### Step 9: Output
Files produced:
- `reports/manuscript/manuscript_<journal>.md` — Formatted manuscript
- `reports/manuscript/cover_letter.md` — Cover letter
- `reports/manuscript/submission_checklist.md` — Submission checklist
- `reports/manuscript/supplementary/` — Supplementary materials directory
- `reports/manuscript/references_<journal>.md` — Formatted references

---

## Supported Journals

### Nature Family
- Nature, Nature Medicine, Nature Genetics, etc.
- Abstract: ≤150 words, unstructured
- Main text: ≤3000 words
- References: Numbered superscript
- Figures: Separate files, 300+ DPI

### Lancet Family
- The Lancet, Lancet Global Health, etc.
- Abstract: ≤300 words, structured
- Main text: ≤3500 words
- References: Vancouver style

### PLOS Family
- PLOS ONE, PLOS Biology, PLOS Medicine
- Abstract: ≤300 words, structured
- No strict word limit
- References: Author-year

### APA Journals
- Psychological Science, Journal of Applied Psychology, etc.
- Abstract: ≤250 words
- References: APA 7th edition
- Tables: APA format

### AEA Journals
- American Economic Review, Journal of Political Economy, etc.
- Abstract: ≤150 words
- References: Author-year
- Tables: Economics format

### Elsevier General
- Varies by journal, check specific guidelines
- Common: numbered references, structured abstracts

---

## Integration
- Called by: `compile_outputs` agent or `export --format <journal>` CLI
- Requires: Manuscript complete, bibliography available
- Outputs to: `reports/manuscript/`
""",
    "write_methods_section": """---
skill_id: "write_methods_section"
version: "7.0.0"
category: "writing"
domain_compatibility: ["all"]
required_tools: ["python", "openai|anthropic|litellm"]
depends_on: ["parse_research_brief", "detect_missingness"]
produces: ["reports/sections/methods_section.md"]
complexity: "intermediate"
---

# Skill: Write Methods Section

## Purpose
Generate a complete, domain-appropriate methods section covering study design, data, variables, analytical procedures, and ethical considerations.

## When to Use
- After analysis plan determined
- Before results section
- For manuscript assembly

## When NOT to Use
- Only results needed
- Methods already written

## Execution Protocol

### Step 1: Study Design Description
- Design type: cross-sectional, longitudinal, experimental, quasi-experimental, observational
- Setting: where and when data was collected
- Participants/sample: N, inclusion/exclusion criteria, recruitment method
- For experiments: randomization procedure, blinding, control condition

### Step 2: Data Description
- Data source: survey, administrative records, experimental, scraped, public dataset
- Time period: collection dates
- Variables: list with operational definitions
- Measurement instruments: validated scales, custom measures

### Step 3: Analytical Procedures
- Software: name and version
- Preprocessing: cleaning, transformation, imputation method
- Statistical tests: each test with rationale
- Model specifications: formula, covariates, interaction terms
- Assumption checks: which tests, results
- Multiple testing correction: method used
- Significance level: α threshold

### Step 4: Missing Data Handling
- Extent of missingness: per variable
- Mechanism: MCAR, MAR, or MNAR (with test results)
- Handling method: complete-case, imputation, weighting
- Sensitivity analysis: alternative methods tested

### Step 5: Ethical Considerations
- IRB approval: status and number
- Informed consent: obtained or waived
- Data privacy: anonymization, secure storage
- Conflicts of interest: declared or none

## Reporting Standards by Domain
| Domain | Standard | Required Elements |
|--------|----------|------------------|
| Medicine/Epi | STROBE | Flow diagram, confounder justification |
| Psychology | APA 7th | Reliability coefficients, manipulation checks |
| Economics | AEA | Data availability statement, pre-registration |
| Education | AERA | Sampling frame, response rate |

## Output Specification
- `reports/sections/methods_section.md`: complete methods section

## Validation Checks
- [ ] All analysis methods described
- [ ] Software and versions specified
- [ ] Missing data handling documented
- [ ] Ethical considerations addressed
- [ ] Domain reporting standard followed
""",
    "parse_research_brief": """---
skill_id: "parse_research_brief"
version: "7.0.0"
category: "writing"
domain_compatibility: ["all"]
required_tools: ["python", "pyyaml"]
depends_on: []
produces: ["briefs/parsed_research_brief.json"]
complexity: "intermediate"
---

# Skill: Parse Research Brief

## Purpose
Extract structured research parameters from a natural language research brief: questions, variables, hypotheses, domain, and constraints.

## When to Use
- First step in any research pipeline
- When researcher provides a free-text brief
- Before any analysis or literature search

## When NOT to Use
- Research parameters already structured
- Only exploratory analysis with no specific question

## Execution Protocol

### Step 1: Question Extraction
- Identify primary research question(s)
- Classify question type: descriptive, comparative, associational, causal, predictive, exploratory
- Extract: independent variable(s), dependent variable(s), covariates

### Step 2: Hypothesis Formulation
- Extract stated hypotheses (directional or non-directional)
- If no hypothesis stated: generate null and alternative hypotheses
- Specify: expected effect direction and magnitude (if stated)

### Step 3: Domain & Context
- Identify research domain from keywords and variable names
- Extract: population of interest, setting, time period
- Identify: reporting standard (APA, STROBE, AEA, etc.)

### Step 4: Constraints & Preferences
- Extract: significance level preference (default α = 0.05)
- Extract: analysis method preferences (if any)
- Extract: output format preferences
- Note: any ethical constraints or data use restrictions

### Step 5: Validation
- Check: all required fields populated
- Check: variables referenced in hypotheses exist in data (if data available)
- Check: question type is answerable with available data
- Flag: ambiguities for researcher clarification

## Output Specification
- `briefs/parsed_research_brief.json`: structured brief with questions, hypotheses, variables, domain, constraints

## Validation Checks
- [ ] At least one research question identified
- [ ] Question type classified
- [ ] Variables mapped to roles (IV, DV, covariate)
- [ ] Domain identified
- [ ] Ambiguities flagged
""",
    "abstract_generator": """---
skill_id: "abstract_generator"
version: "1.0.0"
category: "writing"
depends_on: ["execute_analysis", "compile_outputs"]
produces: ["03_synthesis/manuscript/abstract_apa.md", "03_synthesis/manuscript/abstract_nature.md", "03_synthesis/manuscript/abstract_plain.md", "03_synthesis/manuscript/abstract_tweet.txt"]
complexity: "quick"
---

# Skill: Abstract Generator

## Purpose
Generates abstracts in four formats from computed results. Every claim grounded in data with source file tags. No hallucination.

---

## Inputs
`key_findings.json`, `decisions.yaml` (method summary), `*_results.json` (effect sizes), data profile (sample info), `intake.md` (research question). All required.

---

## Protocol

### Step 1: Extract Grounded Facts
Build fact table from inputs. Each fact must have a `source_file`. If no source, exclude from abstract.

### Step 2: APA Structured (~250 words)
Four sections: **Background** (1-2 sentences, research question), **Methods** (1-2 sentences, design/sample/method), **Results** (2-3 sentences with effect sizes + CIs + p-values), **Conclusion** (1 sentence, grounded in results). Every numerical claim includes effect size + CI + p-value. No causal language unless design supports it.

### Step 3: Nature-Style Unstructured (~150 words)
Single paragraph, no headers. Structure: problem (1 sentence) → what we did (1 sentence) → findings with numbers (2-3 sentences) → meaning (1 sentence). Lead with most important finding. Include at least one effect size with CI.

### Step 4: Plain Language (~100 words)
Non-specialist audience. No statistical jargon. Use "X out of Y" or "about Z%" instead of effect sizes. Every claim still traceable to source file.

### Step 5: Tweet-Length (280 chars)
One key finding with one number. Implication in ≤5 words. Include `#Research` or domain hashtag.

### Step 6: Source Tagging
Output `abstract_sources.json` with: abstract type, word count, array of claims (each with text, source_file, effect_size, CI, p_value), generated_at timestamp.

---

## Anti-Hallucination Rules
1. Empty `key_findings.json` → output "No findings available."
2. Missing effect size → exclude that finding.
3. Unknown sample size → do NOT invent one.
4. Never use "proves", "confirms", "demonstrates" — use "suggests", "is associated with".
5. Exploratory analysis → state "These findings are exploratory and require confirmation."

---

## Validation
- [ ] Every numerical claim has source file
- [ ] No causal language without design justification
- [ ] APA ≤ 250 words, Nature ≤ 150, Plain ≤ 100, Tweet ≤ 280 chars
- [ ] Plain language: no jargon
- [ ] Effect sizes include CIs
- [ ] p-values formatted correctly
""",
    "generate_apa_tables": """---
skill_id: "generate_apa_tables"
version: "7.0.0"
category: "writing"
domain_compatibility: ["psychology", "education", "social_sciences"]
required_tools: ["python", "pandas", "jinja2"]
depends_on: ["descriptive_stats", "inferential_parametric"]
produces: ["reports/tables/"]
complexity: "intermediate"
---

# Skill: Generate APA-Style Tables

## Purpose
Generate publication-ready tables in APA 7th edition format for descriptive statistics, regression results, and ANOVA tables.

## When to Use
- Results finalized
- Need tables for manuscript
- APA or similar formatting required

## When NOT to Use
- Only figures needed
- Non-APA format required (e.g., AMA, Chicago)

## Execution Protocol

### Step 1: Table 1 (Descriptive Statistics)
- Columns: Variable, M, SD, [Min, Max], Skew, Kurtosis, N
- For categorical: n (%)
- Grouped: if comparing groups, one column per group
- Footnotes: note any transformations, exclusions

### Step 2: Regression Table
- Columns: Predictor, B (or β), SE, 95% CI, p
- Organize: blocks of predictors (Step 1, Step 2, etc.)
- Bottom rows: R², ΔR², F, df
- Significance: * p < .05, ** p < .01, *** p < .001

### Step 3: ANOVA Table
- Columns: Source, SS, df, MS, F, p, η²
- Rows: between-groups, within-groups, total
- Post-hoc: pairwise comparisons with adjusted p-values

### Step 4: Formatting Rules (APA 7th)
- No vertical lines
- Horizontal lines: top, bottom, below column headers
- Font: same as manuscript (typically Times New Roman, 12pt)
- Table number and title above table
- Notes below table: general, specific, probability
- Decimal alignment: align on decimal point
- Leading zero: 0 for statistics that can exceed 1 (p, r), no 0 for statistics that cannot (F, t, χ²)

## Output Specification
- `reports/tables/`: individual table files in Markdown and LaTeX format

## Validation Checks
- [ ] No vertical lines
- [ ] Correct horizontal line placement
- [ ] Decimal formatting follows APA rules
- [ ] All statistics match computed values
- [ ] Table numbers sequential
""",
    "interpret_effect_sizes": """---
skill_id: "interpret_effect_sizes"
version: "7.0.0"
category: "writing"
domain_compatibility: ["all"]
required_tools: ["python"]
depends_on: ["inferential_parametric", "inferential_nonparametric"]
produces: ["reports/effect_size_interpretation.md"]
complexity: "intermediate"
---

# Skill: Interpret Effect Sizes

## Purpose
Translate statistical effect sizes into substantive, domain-meaningful interpretations with practical significance assessments.

## When to Use
- After inferential analysis
- Before writing discussion
- To avoid over-reliance on p-values

## When NOT to Use
- Only p-value reporting needed (not recommended)
- Effect sizes not computed

## Execution Protocol

### Step 1: Effect Size Classification
| Metric | Trivial | Small | Medium | Large | Very Large |
|--------|---------|-------|--------|-------|------------|
| Cohen's d | < 0.10 | 0.10-0.30 | 0.30-0.50 | 0.50-0.80 | > 0.80 |
| Pearson's r | < 0.05 | 0.05-0.10 | 0.10-0.30 | 0.30-0.50 | > 0.50 |
| R² | < 0.01 | 0.01-0.06 | 0.06-0.14 | 0.14-0.26 | > 0.26 |
| Odds Ratio | ~1.0 | 1.2-1.5 | 1.5-2.5 | 2.5-4.0 | > 4.0 |
| η² | < 0.01 | 0.01-0.06 | 0.06-0.14 | 0.14-0.26 | > 0.26 |

### Step 2: Contextual Interpretation
- Compare to prior literature: is this effect typical, larger, or smaller?
- Practical significance: what does this mean in real-world terms?
- Clinical/policy significance: does it meet minimal important difference?
- Cost-benefit: is the effect large enough to justify intervention cost?

### Step 3: Precision Assessment
- CI width: narrow = precise, wide = uncertain
- Does CI include trivial effects? If yes, result is inconclusive
- Does CI exclude meaningful effects? If yes, result supports null

### Step 4: Reporting
- Report effect size with CI and qualitative interpretation
- Avoid: "significant" without effect size
- Avoid: "no effect" when CI includes meaningful effects
- Use: "the effect was [magnitude], meaning [substantive interpretation]"

## Output Specification
- `reports/effect_size_interpretation.md`: effect size interpretations with contextual comparisons

## Validation Checks
- [ ] All effect sizes classified
- [ ] CI-based precision assessment done
- [ ] Practical significance discussed
- [ ] Comparison to literature included
""",
    "report_compiler": """---
skill_id: "report_compiler"
version: "1.0.0"
category: "writing"
depends_on: ["paper_compiler", "results_table_generator", "captions_and_legends"]
produces: ["03_synthesis/report/report.pdf", "03_synthesis/report/report.docx", "03_synthesis/report/report.html"]
complexity: "standard"
---

# Skill: Report Compiler

## Purpose
Generates a formatted research report (not journal article) in 3 formats: PDF via WeasyPrint, DOCX via python-docx, HTML. Used when `target_output` is "report" not "journal_article".

---

## Protocol

### Step 1: Gather Content
Collect: `key_findings.json`, `global_methods.md`, all figures with `.interpret.md` files, results tables, analysis JSONs, `figure_captions.json`.

### Step 2: Structure Report
Five sections in order:

1. **Executive Summary** (1 page): headline finding, key results with effect sizes, bottom-line recommendation
2. **Key Findings** (2-3 pages): one subsection per research question, each with finding statement, effect size + CI + p-value, associated figure with caption, comparison to prior work
3. **Methods** (1-2 pages): study design, sample, measures, analysis methods (from `global_methods.md`), assumption checks
4. **Full Results** (variable length): detailed results per question, all tables (from results_table_generator), diagnostic figures, robustness checks
5. **Appendix**: supplementary tables, full model outputs, sensitivity analyses, data dictionary

### Step 3: Generate PDF (WeasyPrint)
Build HTML with embedded CSS (page breaks, headers, footers, page numbers). Render with WeasyPrint: `HTML(string=html).write_pdf(output_path)`. Use `@page` rules for margins, headers, footers. Insert page breaks before each major section.

### Step 4: Generate DOCX (python-docx)
Create document with styles: Heading 1 (sections), Heading 2 (subsections), Normal (body), Caption (figures/tables). Insert figures as images with captions. Build tables from results data. Set page margins to 1 inch.

### Step 5: Generate HTML
Single-page HTML with anchor navigation, embedded CSS, all figures inline. Responsive layout. Print-friendly via `@media print`.

### Step 6: Auto-Include Figures
For each figure in experiment outputs, insert into appropriate section with caption from `figure_captions.json`. Place in Results or Appendix based on importance (primary findings in Results, diagnostics in Appendix).

---

## Output
- `03_synthesis/report/report.pdf` — WeasyPrint PDF
- `03_synthesis/report/report.docx` — python-docx document
- `03_synthesis/report/report.html` — Single-page HTML

## Validation
- [ ] All 5 sections present and in order
- [ ] All figures included with captions
- [ ] Effect sizes with CIs in Key Findings
- [ ] Page numbers in PDF
- [ ] DOCX opens without errors
- [ ] HTML responsive on mobile
- [ ] Print layout clean
""",
    "regression_discontinuity": """---
skill_id: "regression_discontinuity"
version: "1.0.0"
category: "analysis"
domain_compatibility: ["social_science", "policy"]
required_tools: ["statsmodels"]
depends_on: []
produces: ["02_experiments/main/rdd_estimates.json"]
complexity: "advanced"
---

# Skill: Regression Discontinuity Design

<objective>
Estimates local average treatment effects by exploiting a sharp cutoff in a running variable.
</objective>
""",
    "differential_expression": """---
skill_id: "differential_expression"
version: "1.0.0"
category: "analysis"
domain_compatibility: ["genomics"]
required_tools: ["R", "DESeq2"]
depends_on: ["profile_genomic"]
produces: ["02_experiments/main/deg_results.csv"]
complexity: "advanced"
---

# Skill: Differential Expression Analysis

<objective>
Calculates differentially expressed genes using DESeq2 for negative binomial distributed counts.
</objective>
""",
    "walk_forward_validation": """---
skill_id: "walk_forward_validation"
version: "1.0.0"
category: "audit"
domain_compatibility: ["finance"]
required_tools: ["pandas"]
depends_on: ["strategy_backtester"]
produces: ["02_experiments/main/wfa_metrics.json"]
complexity: "advanced"
---

# Skill: Walk-Forward Validation

<objective>
Performs rolling or expanding window out-of-sample testing to detect overfitting.
</objective>
""",
    "strategy_backtester": """---
skill_id: "strategy_backtester"
version: "1.0.0"
category: "analysis"
domain_compatibility: ["finance"]
required_tools: ["pandas", "backtrader"]
depends_on: []
produces: ["02_experiments/main/backtest_results.csv"]
complexity: "advanced"
---

# Skill: Strategy Backtester

<objective>
Executes a vectorized or event-driven backtest on financial time-series.
</objective>
""",
    "difference_in_differences": """---
skill_id: "difference_in_differences"
version: "1.0.0"
category: "analysis"
domain_compatibility: ["social_science", "policy"]
required_tools: ["statsmodels", "linearmodels"]
depends_on: []
produces: ["02_experiments/main/did_estimates.json"]
complexity: "advanced"
---

# Skill: Difference-in-Differences

<objective>
Estimates the causal effect of a treatment by comparing pre/post changes between treatment and control groups.
</objective>
""",
    "propensity_score_matching": """---
skill_id: "propensity_score_matching"
version: "1.0.0"
category: "analysis"
domain_compatibility: ["clinical"]
required_tools: ["sklearn"]
depends_on: []
produces: ["02_experiments/main/matched_cohort.csv"]
complexity: "advanced"
---

# Skill: Propensity Score Matching

<objective>
Matches treated and control observational units based on covariates to approximate an RCT.
</objective>
""",
    "profile_genomic": """---
skill_id: "profile_genomic"
version: "1.0.0"
category: "data"
domain_compatibility: ["genomics"]
required_tools: ["fastqc", "multiqc"]
depends_on: []
produces: ["02_experiments/main/qc_report.html"]
complexity: "basic"
---

# Skill: Genomic Data Profiling

<objective>
Runs FastQC/MultiQC on raw FASTQ files to determine sequencing quality.
</objective>

<protocol>
### Step 1: Pre-checks
- Validate inputs are FASTQ format.

### Step 2: Core Procedure
- Run FastQC on all files.
- Aggregate with MultiQC.
</protocol>
""",
    "survival_analysis": """---
skill_id: "survival_analysis"
version: "1.0.0"
category: "analysis"
domain_compatibility: ["clinical"]
required_tools: ["lifelines"]
depends_on: []
produces: ["02_experiments/main/kaplan_meier.png"]
complexity: "intermediate"
---

# Skill: Survival Analysis

<objective>
Fits Kaplan-Meier curves and Cox Proportional Hazards models to time-to-event data.
</objective>
""",
    "route_method": """---
skill_id: "route_method"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "pyyaml"]
depends_on: ["classify_domain", "profile_tabular", "detect_missingness"]
produces: ["analysis/methods_routing.json"]
complexity: "advanced"
---

# Skill: Analytical Method Routing

## Purpose
Route data profiles to appropriate analysis skills based on data characteristics, research question, and domain conventions.

## When to Use
- After profiling and domain classification
- Before executing any analysis
- To generate an analysis plan from data characteristics

## When NOT to Use
- Analysis method already specified by researcher
- Only one analysis method is applicable

## Decision Protocol

### Routing Tree
```
1. What is the research question type?
   ├── "Describe" → descriptive_stats
   ├── "Compare groups" → go to 2
   ├── "Test association" → go to 3
   ├── "Predict" → go to 4
   ├── "Causal effect" → causal_inference
   ├── "Discover structure" → clustering or dimensionality_reduction
   └── "Model time" → time_series_analysis

2. Compare groups:
   ├── 2 groups, continuous DV → check normality
   │   ├── Normal → inferential_parametric (t-test)
   │   └── Non-normal → inferential_nonparametric (Mann-Whitney)
   ├── 3+ groups, continuous DV → inferential_parametric (ANOVA) or inferential_nonparametric (Kruskal-Wallis)
   ├── Binary DV → logistic regression
   ├── Time-to-event DV → survival_analysis
   └── Repeated measures → mixed_effects

3. Test association:
   ├── Both continuous → inferential_parametric (Pearson) or inferential_nonparametric (Spearman)
   ├── Both categorical → chi-square
   ├── One continuous, one categorical → point-biserial
   └── Spatial data → spatial_analysis

4. Predict:
   ├── Continuous outcome → multiple regression
   ├── Binary outcome → logistic regression
   ├── Count outcome → Poisson/negative binomial regression
   ├── Time-to-event → survival_analysis
   └── High-dimensional predictors → dimensionality_reduction + regression
```

## Execution Protocol

### Step 1: Input Assembly
- Load: research brief (question type, variables of interest)
- Load: data profile (variable types, distributions, missingness)
- Load: domain classification (domain, reporting standard)

### Step 2: Variable Role Assignment
- Identify: outcome variable(s), predictor variable(s), covariates
- Map each variable to its role based on research brief
- If ambiguous: present options to researcher

### Step 3: Method Selection
- Apply routing tree based on: question type, DV type, IV type
- Check assumptions for selected method
- If assumptions violated: route to alternative method
- If multiple methods applicable: rank by appropriateness

### Step 4: Dependency Resolution
- For each selected method, check depends_on skills
- Build execution order: skills with no dependencies first
- Flag circular dependencies (should not occur)

### Step 5: Output Routing Plan
- List skills in execution order
- For each skill: inputs required, outputs produced, assumptions to check
- Include fallback methods if primary method fails

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| Question type identified | Clear routing | Ask researcher to clarify |
| Variables mapped to roles | Complete | Flag unmapped variables |
| Assumptions checkable | Data supports method | Route to alternative |
| Dependencies satisfiable | All prerequisites met | Run missing prerequisite skills |

### Red Flags
- **No method matches**: research question may not be answerable with available data
- **Multiple equally valid methods**: present both, compare results
- **Routing suggests causal method but data is cross-sectional**: warn about causal limitations
- **Domain-specific method not available**: use general method with domain-appropriate reporting

## Complexity Budget

Every method is tagged with a runtime complexity tier. The intent router uses these tags to enforce depth constraints — exploratory queries MUST NOT invoke `intensive` methods.

### Complexity Tiers

| Tier | Runtime | When to Use | Examples |
|------|---------|-------------|----------|
| **quick** | <2 min | Exploratory queries, "show me the data", quick look, sanity checks | descriptive_stats, profile_tabular, correlation_matrix, histogram, scatter_plot, chi-square, t-test |
| **standard** | 5–15 min | Planned analysis, hypothesis testing, publication methods | multiple_regression, logistic_regression, ANOVA, factor_analysis, mediation_analysis, bootstrap CI |
| **intensive** | >15 min | Publication-only, final validation, complex models | MCMC/Bayesian, mixed_effects, structural_equation_model, permutation_tests (10k+), cross-validated ML, survival_analysis, time_series_ARIMA |

### Depth Enforcement Rules

- `depth: exploratory` → ONLY `quick` methods allowed. Block any `standard` or `intensive` method.
- `depth: standard` → `quick` + `standard` allowed. `intensive` requires explicit user approval.
- `depth: publication` → all tiers allowed. No restrictions.

### Intent Router Integration

When the intent router classifies a query as `exploratory`:
1. Filter out all methods tagged `intensive`
2. Filter out all methods tagged `standard` unless explicitly requested
3. Select the simplest `quick` method that answers the question
4. If no `quick` method is appropriate, ask: "This requires a more complex analysis. Proceed?"

### Method Complexity Tags

```
descriptive_stats          → quick
profile_tabular            → quick
correlation_matrix         → quick
t_test                     → quick
chi_square                 → quick
histogram                  → quick
scatter_plot               → quick
multiple_regression        → standard
logistic_regression        → standard
ANOVA                      → standard
factor_analysis            → standard
mediation_analysis         → standard
bootstrap_ci               → standard
mixed_effects              → intensive
bayesian_mcmc              → intensive
structural_equation_model  → intensive
survival_analysis          → intensive
time_series_arima          → intensive
permutation_test           → intensive
cross_validated_ml         → intensive
```

## Output Specification
- `analysis/methods_routing.json`: ordered skill list, variable role assignments, assumption checks, fallback methods, execution dependencies

## Validation Checks
- [ ] At least one analysis method selected
- [ ] Execution order respects dependencies
- [ ] Each method's assumptions are checkable with available data
- [ ] Fallback methods specified for each primary method
""",
    "bayesian_modeling": """---
skill_id: "bayesian_modeling"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "pymc", "arviz"]
depends_on: ["descriptive_stats"]
produces: ["analysis/03_analytical/bayesian_results.json"]
complexity: "advanced"
---

# Skill: Bayesian Hierarchical Modeling

## Purpose
Specify, sample, and evaluate Bayesian models with proper prior specification, MCMC convergence diagnostics, and posterior predictive checks.

## When to Use
- Prior information available and should be incorporated
- Hierarchical/multilevel data structure
- Small sample sizes where frequentist estimates are unstable
- Need full posterior distributions (not just point estimates)
- Model comparison via Bayes factors or LOO-CV

## When NOT to Use
- No prior information and non-informative priors would be used anyway
- Computational resources insufficient for MCMC
- Simple descriptive question only

## Execution Protocol

### Step 1: Prior Specification
**Principles:**
- Use weakly informative priors by default (regularize, don't dominate)
- Prior predictive check: simulate from prior alone; are predictions plausible?
- Domain-informed priors: use literature to set prior means and SDs

**Default priors:**
- Intercept: Normal(0, 10) on standardized outcome
- Slopes: Normal(0, 2.5) on standardized predictors
- Group-level SDs: HalfNormal(0, 1) or HalfStudentT(3, 1)
- Residual SD: HalfNormal(0, 1)
- Correlation parameters: LKJ(η=2)

### Step 2: Model Specification
- Define likelihood: distribution of Y given parameters
- Define linear predictor: link function and predictors
- For hierarchical models: random intercepts and/or slopes
- Non-centered parameterization for group-level effects (avoids funnel problem)

### Step 3: MCMC Sampling
- Sampler: NUTS (No-U-Turn Sampler)
- Chains: 4 (minimum), draws: 2000 per chain, tuning: 1000
- Target acceptance: 0.95 (increase to 0.99 if divergences)
- Initialize: adapt_diag or jitter+adapt_diag
- Random seed: set for reproducibility

### Step 4: Convergence Diagnostics
**Required checks (ALL must pass):**
- R-hat (R̂) < 1.05 for all parameters (ideally < 1.01)
- Effective sample size (ESS) > 400 for all parameters
- Divergent transitions = 0
- No max-tree-depth hits
- Trace plots: chains mix well, no trends

**If diagnostics fail:**
- Divergences > 0: increase target_accept to 0.99, reparameterize
- R̂ > 1.05: increase tuning steps, check priors
- Low ESS: increase draws, check for high autocorrelation

### Step 5: Posterior Summarization
- Point estimates: posterior mean or median
- Uncertainty: 95% HDI (Highest Density Interval)
- Probability of direction: P(β > 0) or P(β < 0)
- ROPE (Region of Practical Equivalence): proportion of posterior within [-0.1, 0.1] of null

### Step 6: Posterior Predictive Checks
- Simulate replicated data from posterior predictive distribution
- Compare replicated data to observed: do they look similar?
- Test statistic: mean, SD, max, min of replicated vs observed
- If replicated data systematically differs: model misspecified

### Step 7: Model Comparison
- LOO-CV (Leave-One-Out Cross-Validation): expected log predictive density
- WAIC: Watanabe-Akaike Information Criterion
- Bayes factors: for nested models (use bridge sampling)
- Prefer: LOO-CV for predictive accuracy, Bayes factors for hypothesis testing

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| R̂ < 1.05 | Chains converged | Non-convergence | Increase tuning, check priors |
| ESS > 400 | Adequate sampling | Poor mixing | Increase draws, reparameterize |
| Divergences = 0 | Stable sampling | Numerical instability | Increase target_accept, non-centered param |
| PPC passes | Model fits data | Model misspecified | Add predictors, change likelihood |

### Red Flags
- **R̂ > 1.1**: chains haven't mixed; results unreliable
- **All posterior mass on one side of zero**: strong effect, but check prior influence
- **PPC fails dramatically**: model doesn't capture key data features
- **Prior dominates posterior**: prior too informative relative to data

## Reporting Template
> "We estimated a Bayesian [model type] using PyMC with 4 MCMC chains, 2,000 draws, and 1,000 tuning steps. Weakly informative priors were used throughout. Convergence was confirmed (all R̂ < 1.01, ESS > 400, zero divergences). The posterior mean for [parameter] was [value] (95% HDI [lower, upper]), with P(β > 0) = [probability]. Posterior predictive checks confirmed adequate model fit."

## Output Specification
- `analysis/03_analytical/bayesian_results.json`: posterior summaries, HDIs, convergence diagnostics, PPC results, model comparison metrics

## Validation Checks
- [ ] All R̂ < 1.05
- [ ] All ESS > 400
- [ ] Zero divergent transitions
- [ ] PPC passes visual inspection
- [ ] Prior predictive check shows plausible predictions
""",
    "inferential_nonparametric": """---
skill_id: "inferential_nonparametric"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "scipy", "statsmodels"]
depends_on: ["descriptive_stats"]
produces: ["analysis/03_analytical/nonparametric_results.json"]
complexity: "intermediate"
---

# Skill: Non-Parametric Inferential Testing

## Purpose
Conduct distribution-free hypothesis tests when parametric assumptions are violated or data is ordinal.

## When to Use
- Parametric assumptions violated (normality, homoscedasticity)
- Data is ordinal (Likert scales, rankings)
- Sample size too small for CLT (N < 30 per group)
- Data has extreme outliers that cannot be removed

## When NOT to Use
- Parametric assumptions met (parametric tests are more powerful)
- Data is nominal categorical (use chi-square instead)
- Sample is large and approximately normal (parametric is fine)

## Decision Protocol

### Test Selection
| Parametric Equivalent | Non-Parametric Alternative | Design |
|----------------------|---------------------------|--------|
| Independent t-test | Mann-Whitney U (Wilcoxon rank-sum) | 2 independent groups |
| Paired t-test | Wilcoxon signed-rank | 2 paired groups |
| One-way ANOVA | Kruskal-Wallis H | 3+ independent groups |
| Repeated measures ANOVA | Friedman test | 3+ paired groups |
| Pearson correlation | Spearman rank correlation | Continuous association |
| Pearson correlation | Kendall's tau | Ordinal association, small N |

## Execution Protocol

### Step 1: Test Selection & Rationale
- Document why non-parametric is chosen (assumption violation, ordinal data, small N)
- Select appropriate test from decision table

### Step 2: Test Execution
- Run selected test
- Report: test statistic, exact p-value (not asymptotic if N < 20)
- For Mann-Whitney U: report U statistic and rank-biserial correlation
- For Kruskal-Wallis: report H statistic and epsilon-squared effect size

### Step 3: Effect Size Computation
**Mann-Whitney U:**
- Rank-biserial correlation: r_rb = 1 - (2U) / (n₁ × n₂)
- Common language effect size: probability that random X > random Y

**Kruskal-Wallis:**
- Epsilon-squared: ε² = (H - k + 1) / (N - k)
- Interpret: 0.01 = small, 0.04 = medium, 0.16 = large

**Spearman/Kendall:**
- Report correlation coefficient with 95% CI
- Interpret as monotonic (not linear) association

### Step 4: Post-Hoc Tests (Kruskal-Wallis only)
- If omnibus test significant: pairwise Mann-Whitney U with Holm-Bonferroni correction
- Report adjusted p-values for each pair

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| Ties | < 10% of observations | Many tied ranks | Use exact test or permutation |
| Sample size | N ≥ 10 per group | Very small | Use exact permutation test |
| Effect direction | Consistent with medians | Paradoxical result | Check for Simpson's paradox |

### Red Flags
- **Mann-Whitney significant but medians equal**: distributions differ in shape, not location; report distributional difference
- **Many ties (> 25%)**: rank-based tests lose power; consider permutation test
- **Kruskal-Wallis significant but no post-hoc pairs significant**: omnibus detects subtle differences; report with caution

## Reporting Template
> "Due to violation of normality assumptions (Shapiro-Wilk p < .001), a Mann-Whitney U test was conducted. [Group A] (Median = [value], N = [value]) scored significantly [higher/lower] than [Group B] (Median = [value], N = [value]), U = [value], p = [value], r_rb = [value], 95% CI [lower, upper]."

## Output Specification
- `analysis/03_analytical/nonparametric_results.json`: test results, effect sizes, CIs, rationale for non-parametric choice

## Validation Checks
- [ ] Test statistic matches rank-based formula
- [ ] p-value in [0, 1]
- [ ] Effect size in [-1, 1] for correlation measures
- [ ] Post-hoc tests corrected for multiple comparisons
""",
    "inferential_parametric": """---
skill_id: "inferential_parametric"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "scipy", "statsmodels", "pandas"]
depends_on: ["descriptive_stats", "detect_outliers"]
produces: ["analysis/03_analytical/parametric_results.json"]
complexity: "intermediate"
---

# Skill: Parametric Inferential Testing

## Purpose
Conduct parametric hypothesis tests (t-tests, ANOVA, regression) with assumption verification and effect size reporting.

## When to Use
- Research question involves comparing groups or testing associations
- Data meets parametric assumptions (normality, homoscedasticity, independence)
- Sample size adequate for asymptotic approximations (N ≥ 30 per group)

## When NOT to Use
- Assumptions severely violated → use inferential_nonparametric
- Sample size too small → use exact tests
- Data is dependent/paired → use paired tests or mixed_effects

## Decision Protocol

### Test Selection
| Design | DV Type | IV Type | Test |
|--------|---------|---------|------|
| 2 independent groups | Continuous | Binary (2 levels) | Independent t-test (Welch) |
| 2 paired groups | Continuous | Binary (2 levels, repeated) | Paired t-test |
| 3+ independent groups | Continuous | Categorical (3+ levels) | One-way ANOVA |
| 3+ paired groups | Continuous | Categorical (repeated) | Repeated measures ANOVA |
| 2×2 design | Continuous | 2 categorical factors | Two-way ANOVA |
| Continuous association | Continuous | Continuous | Pearson correlation / Linear regression |
| Continuous outcome, multiple predictors | Continuous | Mixed | Multiple regression (OLS) |

## Execution Protocol

### Step 1: Assumption Verification
**Normality:**
- Shapiro-Wilk (N < 5000) or Kolmogorov-Smirnov (N ≥ 5000)
- Visual: Q-Q plot
- If violated but N > 30 per group: CLT applies, proceed with caution

**Homoscedasticity (equal variances):**
- Levene's test (robust to non-normality) or Brown-Forsythe
- If p < 0.05: use Welch correction (unequal variance t-test, Welch ANOVA)

**Independence:**
- Study design check: are observations independent?
- If repeated measures: use paired tests or mixed_effects skill
- If clustered: use cluster-robust SEs

**Linearity (regression):**
- Residual vs fitted plot: check for patterns
- If non-linear: add polynomial terms or use GAM

### Step 2: Test Execution
- Run selected test
- Report: test statistic, degrees of freedom, p-value, exact p (not just < 0.05)
- Compute effect size: Cohen's d (t-test), η² (ANOVA), R² (regression)
- Compute 95% CI for effect size and mean differences

### Step 3: Multiple Comparison Correction
- If > 1 hypothesis tested: apply correction
- Default: Bonferroni (conservative) or Holm-Bonferroni (step-down, less conservative)
- For exploratory analyses: Benjamini-Hochberg FDR control
- Report both raw and adjusted p-values

### Step 4: Regression Diagnostics (if regression)
- Multicollinearity: VIF > 10 indicates problematic collinearity
- Residual normality: Shapiro-Wilk on residuals
- Residual homoscedasticity: Breusch-Pagan test
- Influential points: Cook's D > 4/n
- If diagnostics fail: report robust SEs (HC3) or use robust regression

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| Normality | p > 0.05 or N > 30 | Non-normal | Non-parametric or transform |
| Homoscedasticity | Levene p > 0.05 | Unequal variances | Welch correction |
| VIF | < 10 | Multicollinearity | Remove correlated predictor |
| Cook's D | < 4/n | Influential observation | Report sensitivity analysis |

### Red Flags
- **p = 0.000**: report as p < 0.001, never p = 0.000
- **Effect size trivial (d < 0.10) but p < 0.05**: large sample driving significance; report effect size prominently
- **Significant but CI includes null**: check computation; this is impossible
- **VIF > 100**: perfect collinearity; one predictor is linear combination of others

## Domain Conventions

| Domain | Effect Size | Small | Medium | Large |
|--------|------------|-------|--------|-------|
| Psychology | Cohen's d | 0.20 | 0.50 | 0.80 |
| Medicine | Cohen's d | 0.20 | 0.50 | 0.80 |
| Education | Cohen's d | 0.20 | 0.50 | 0.80 |
| Economics | Standardized β | 0.10 | 0.30 | 0.50 |

## Reporting Template
> "An independent-samples Welch t-test indicated that [Group A] (M = [value], SD = [value], N = [value]) scored significantly [higher/lower] than [Group B] (M = [value], SD = [value], N = [value]), t([df]) = [value], p = [value], d = [value], 95% CI [lower, upper]. Levene's test indicated [equal/unequal] variances, F([df]) = [value], p = [value]."

## Output Specification
- `analysis/03_analytical/parametric_results.json`: test results, effect sizes, CIs, assumption test results, multiple comparison adjustments

## Validation Checks
- [ ] Test statistic matches formula
- [ ] p-value in [0, 1]
- [ ] Effect size in plausible range
- [ ] CI direction consistent with test statistic sign
- [ ] All assumptions tested and reported
""",
    "causal_inference": """---
skill_id: "causal_inference"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "dowhy", "econml|doubleml", "scikit-learn"]
depends_on: ["descriptive_stats"]
produces: ["analysis/03_analytical/causal_results.json"]
complexity: "advanced"
---

# Skill: Causal Inference & Identification

## Purpose
Estimate causal effects (ATE, CATE) using structural causal models, double machine learning, and refutation testing.

## When to Use
- Research question is causal ("does X cause Y?") not associational
- Observational data with potential confounding
- RCT data (use simple difference-in-means, but validate randomization)

## When NOT to Use
- Only associational question asked
- No plausible identification strategy
- Treatment and outcome measured simultaneously with no temporal ordering

## Decision Protocol

### Method Selection
| Design | Data Type | Method |
|--------|-----------|--------|
| RCT | Any | Difference-in-means (validate randomization) |
| Observational, measured confounders | Any | Propensity score matching / weighting |
| Observational, high-dimensional confounders | Any | Double Machine Learning (DML) |
| Natural experiment | Binary treatment | Instrumental Variables (2SLS) |
| Policy intervention, panel data | Panel | Difference-in-Differences (DiD) |
| Threshold-based assignment | Continuous running variable | Regression Discontinuity (RDD) |
| Time-varying treatment | Longitudinal | Marginal Structural Models (MSM) |

## Execution Protocol

### Step 1: Causal Model Specification
- Define: treatment (D), outcome (Y), confounders (X), instruments (Z), mediators (M)
- Draw causal DAG: nodes = variables, edges = causal relationships
- Identify backdoor paths: all non-causal paths from D to Y
- Determine identification strategy: backdoor criterion, frontdoor criterion, or IV

### Step 2: Confounder Selection
- Include pre-treatment variables that affect both D and Y
- Exclude: mediators (on causal path D → M → Y), colliders (D → C ← Y), instruments (Z → D, Z ⊥ Y)
- Validate confounder list against domain literature

### Step 3: Effect Estimation
**Propensity Score Methods:**
- Estimate propensity: P(D=1|X) using logistic regression or ML
- Check overlap: propensity distributions should overlap between treated and control
- Match: nearest neighbor (1:1 or 1:k), caliper = 0.2 × SD of logit
- Weight: IPTW (inverse probability of treatment weighting)
- Check balance: standardized mean differences < 0.10 after matching/weighting

**Double Machine Learning:**
- Nuisance models: ML for Y|X and D|X (Random Forest, Lasso, or gradient boosting)
- Cross-fitting: split data into K folds, estimate nuisances on K-1 folds
- Orthogonalized residuals: Ỹ = Y - Ê[Y|X], D̃ = D - Ê[D|X]
- Final estimate: OLS of Ỹ on D̃
- Report: ATE, SE, 95% CI

### Step 4: Refutation Testing (DoWhy)
- **Placebo treatment**: replace D with random noise → effect should be 0
- **Random common cause**: add random confounder → estimate should be stable
- **Data subset**: remove 50% of data → estimate should be stable
- **Unobserved confounder**: simulate hidden confounder → sensitivity bound

### Step 5: Heterogeneous Treatment Effects (CATE)
- If treatment effect varies by subgroup: estimate CATE
- Methods: causal forest, meta-learners (T-learner, S-learner, X-learner)
- Report: which subgroups benefit most/least

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| Propensity overlap | Distributions overlap | No common support | Trim to overlap region |
| Balance | SMD < 0.10 | Residual confounding | Add interaction terms, re-match |
| Placebo refuter | p > 0.05 | Unobserved confounding | Reconsider identification strategy |
| Common cause stability | Estimate change < 5% | Model unstable | Increase regularization |

### Red Flags
- **No overlap in propensity scores**: treated and control are fundamentally different; cannot estimate causal effect
- **Placebo refuter significant**: model finds effect in random noise → severe misspecification
- **CATE varies wildly**: treatment effect highly heterogeneous; report subgroup-specific effects
- **IV weak (F-stat < 10)**: instrument too weak; biased 2SLS estimates

## Reporting Template
> "We estimated the causal effect of [treatment] on [outcome] using [method]. The ATE was [value] (SE = [value], 95% CI [lower, upper], p = [value]). Causal identification was validated through [refutation tests]. Placebo treatment refutation yielded ATE = [value] (p = [value]), supporting the validity of our identification strategy."

## Output Specification
- `analysis/03_analytical/causal_results.json`: ATE, CATE, SEs, CIs, refutation results, propensity diagnostics, causal DAG

## Validation Checks
- [ ] Causal DAG specified and justified
- [ ] Confounders pre-treatment only
- [ ] Propensity overlap verified
- [ ] At least 2 refutation tests passed
- [ ] Effect size plausible given domain knowledge
""",
    "power_analysis": """---
skill_id: "power_analysis"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "scipy", "statsmodels"]
depends_on: ["descriptive_stats"]
produces: ["analysis/03_analytical/power_analysis.json"]
complexity: "intermediate"
---

# Skill: Power Analysis & Sample Size Calculation

## Purpose
Compute statistical power for planned or completed analyses, and determine required sample sizes for desired power levels.

## When to Use
- Before data collection: determine required sample size
- After analysis: compute achieved power (post-hoc)
- When interpreting non-significant results: was the study underpowered?

## When NOT to Use
- Effect size is completely unknown and cannot be estimated
- Only descriptive analysis planned (no hypothesis testing)

## Decision Protocol

### Test-Specific Power Calculation
| Test | Effect Size Metric | Inputs Needed |
|------|-------------------|---------------|
| t-test (independent) | Cohen's d | d, α, power, allocation ratio |
| t-test (paired) | Cohen's d_z | d_z, α, power |
| ANOVA | Cohen's f | f, α, power, groups, n per group |
| Correlation | Pearson's r | r, α, power |
| Chi-square | w (effect size) | w, α, power, df |
| Regression (multiple) | f² | f², α, power, predictors |
| Proportion test | h (Cohen's h) | h, α, power |

## Execution Protocol

### Step 1: Effect Size Estimation
**Sources (in order of preference):**
1. Meta-analysis of similar studies (most reliable)
2. Pilot study or preliminary data
3. Smallest effect size of theoretical/practical importance
4. Conventional benchmarks (Cohen's small/medium/large) as last resort

**Caution:** Do not use observed effect size from the same data for power analysis (circular reasoning)

### Step 2: A Priori Power Analysis (planning)
- Set α = 0.05 (or domain-specific threshold)
- Set desired power: 0.80 (minimum), 0.90 (recommended)
- Input effect size from Step 1
- Compute: required sample size N
- Account for expected attrition: N_adjusted = N / (1 - attrition_rate)

### Step 3: Post-Hoc Power Analysis (completed study)
- Input: actual sample size, observed effect size, α
- Compute: achieved power
- If power < 0.80: non-significant result may be due to low power, not null effect
- Report: "The study had [percentage]% power to detect an effect of d = [value]"

### Step 4: Sensitivity Analysis
- Vary effect size: what power for smaller/larger effects?
- Vary sample size: what effect size detectable with current N?
- Plot: power curve (power vs sample size for range of effect sizes)

### Step 5: Multiple Testing Adjustment
- If multiple hypotheses: adjust α before power calculation
- Bonferroni: α_adj = α / m tests
- Power decreases as α becomes more stringent
- Report: power for each hypothesis separately

## Diagnostics & Interpretation

| Result | Interpretation | Action |
|--------|---------------|--------|
| Power ≥ 0.80 | Adequately powered | Proceed with confidence |
| Power 0.50-0.80 | Underpowered | Interpret non-significant results cautiously |
| Power < 0.50 | Severely underpowered | Non-significant results are uninformative |
| Required N >> available | Infeasible study | Increase effect size (stronger manipulation) or accept lower power |

### Red Flags
- **Post-hoc power based on observed effect size**: circular; use observed CI instead
- **Power = 1.00**: effect size likely overestimated or N very large
- **Required N in thousands**: effect size too small to detect practically; reconsider research question
- **Different tests give different N**: use the largest N (most conservative)

## Reporting Template
> "An a priori power analysis using G*Power indicated that a sample of N = [value] was required to detect an effect of d = [value] with 80% power at α = .05 (two-tailed). Accounting for an expected attrition rate of [percentage]%, the target recruitment was N = [value]. The achieved sample of N = [value] provided [percentage]% power."

## Output Specification
- `analysis/03_analytical/power_analysis.json`: effect size, α, power, required N, achieved N, sensitivity analysis, power curve data

## Validation Checks
- [ ] Effect size source documented
- [ ] Power in [0, 1]
- [ ] Required N is positive integer
- [ ] Attrition adjustment applied if specified
""",
    "mixed_effects": """---
skill_id: "mixed_effects"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "statsmodels", "linearmodels"]
depends_on: ["descriptive_stats"]
produces: ["analysis/03_analytical/mixed_effects_results.json"]
complexity: "advanced"
---

# Skill: Mixed-Effects (Multilevel) Modeling

## Purpose
Fit hierarchical models with fixed and random effects to account for nested or crossed data structures.

## When to Use
- Data has hierarchical structure (students in schools, patients in hospitals, repeated measures)
- Observations are not independent within groups
- Want to model both population-level and group-level effects
- Unbalanced designs (different group sizes)

## When NOT to Use
- No grouping structure in data
- Only a few groups (< 5): fixed effects more appropriate
- All groups have identical effects (no variation to model)

## Decision Protocol

### Model Selection
| Structure | Random Effects | Model |
|-----------|---------------|-------|
| Nested, intercepts vary | Random intercepts | LMM: y ~ X + (1 \\| group) |
| Nested, slopes vary | Random intercepts + slopes | LMM: y ~ X + (1 + X \\| group) |
| Crossed classification | Crossed random effects | LMM: y ~ X + (1 \\| group1) + (1 \\| group2) |
| Binary outcome | Random intercepts | GLMM: logit(y) ~ X + (1 \\| group) |
| Count outcome | Random intercepts | GLMM: log(y) ~ X + (1 \\| group) + offset |

## Execution Protocol

### Step 1: Data Structure Verification
- Identify grouping variables (cluster IDs)
- Compute: number of groups, group sizes, ICC (intraclass correlation)
- ICC > 0.05: multilevel modeling justified
- Check for crossed vs nested structure

### Step 2: Random Effects Specification
- Start with random intercepts only (simplest)
- Add random slopes if theory suggests effect varies by group
- Avoid: random slopes for variables with few levels within groups
- Check: sufficient observations per group for random slope estimation (≥ 10)

### Step 3: Model Fitting
- Estimator: REML (restricted maximum likelihood) for variance components
- For GLMM: Laplace approximation or adaptive Gaussian quadrature
- Convergence: check optimizer converged without warnings
- If convergence fails: simplify random effects structure, increase iterations

### Step 4: Model Comparison
- Compare nested models via likelihood ratio test (LRT)
- Compare non-nested models via AIC/BIC
- Test: random intercept vs random intercept+slope
- Test: varying covariance structures (compound symmetry, AR(1), unstructured)

### Step 5: Diagnostics
- Residual normality: Q-Q plot of level-1 residuals
- Random effects normality: Q-Q plot of BLUPs
- Homoscedasticity: residuals vs fitted plot
- Influence: Cook's D for groups (leave-one-group-out)

### Step 6: Inference
- Fixed effects: Wald tests with Satterthwaite or Kenward-Roger df approximation
- Random effects: variance components with 95% CI
- Compute ICC: proportion of variance at group level
- Compute marginal R² (fixed only) and conditional R² (fixed + random)

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| ICC > 0.05 | Multilevel structure | No group-level variation | Use single-level model |
| Convergence | Optimizer converged | Estimation failed | Simplify model, rescale predictors |
| Random effects normality | Approximately normal | Non-normal BLUPs | Check for outliers, consider robust |
| Residual homoscedasticity | Constant variance | Heteroscedasticity | Model variance structure |

### Red Flags
- **Random effect variance = 0**: no group-level variation; drop random effect
- **Singular fit**: random effects covariance matrix not full rank; simplify structure
- **ICC > 0.50**: most variation is between groups; few effective observations
- **Convergence warnings**: results may be unreliable; try different optimizer

## Reporting Template
> "A linear mixed-effects model was fitted with [fixed effects] as fixed effects and random intercepts for [grouping variable]. The ICC was [value], indicating [percentage]% of variance at the group level. The effect of [predictor] was significant, β = [value], SE = [value], t([df]) = [value], p = [value]. Conditional R² = [value], marginal R² = [value]."

## Output Specification
- `analysis/03_analytical/mixed_effects_results.json`: fixed effects, random effects variance components, ICC, model comparison, diagnostics

## Validation Checks
- [ ] Model converged without warnings
- [ ] ICC computed and reported
- [ ] Both marginal and conditional R² reported
- [ ] Random effects structure justified
""",
    "time_series_analysis": """---
skill_id: "time_series_analysis"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["finance", "econometrics", "ecology"]
required_tools: ["python", "statsmodels", "scipy"]
depends_on: ["descriptive_stats", "profile_temporal"]
produces: ["analysis/03_analytical/time_series_results.json"]
complexity: "advanced"
---

# Skill: Time Series Analysis

## Purpose
Model temporal dependencies using ARIMA/SARIMAX, test for stationarity, and diagnose residual autocorrelation.

## When to Use
- Data is a single time series or panel with temporal structure
- Goal is forecasting, trend detection, or intervention analysis
- Temporal autocorrelation is present

## When NOT to Use
- Data is cross-sectional (no time ordering)
- Time series is too short (N < 30 for ARIMA)
- Only descriptive trend needed (plot and summarize)

## Decision Protocol

### Method Selection
| Pattern | Method |
|---------|--------|
| Stationary, no seasonality | ARMA(p, q) |
| Non-stationary, no seasonality | ARIMA(p, d, q) |
| Seasonal pattern | SARIMAX(p, d, q)(P, D, Q, s) |
| With exogenous predictors | SARIMAX with exog |
| Structural break | Interrupted time series |
| Volatility clustering | GARCH |
| Multiple series | VAR (Vector Autoregression) |

## Execution Protocol

### Step 1: Stationarity Assessment
- Visual: plot series, rolling mean, rolling SD
- ADF test: null = unit root (non-stationary); reject if p < 0.05
- KPSS test: null = stationary; reject if p < 0.05
- If non-stationary: difference (d = 1) and retest
- If seasonal non-stationary: seasonal difference (D = 1)

### Step 2: Model Identification
- ACF plot: identify MA order (q) from significant lags
- PACF plot: identify AR order (p) from significant lags
- Auto-ARIMA: search (p, d, q) grid, minimize AIC
- Seasonal: identify (P, D, Q) from seasonal ACF/PACF

### Step 3: Model Fitting
- Fit SARIMAX via maximum likelihood
- Check: optimizer converged, no singularities
- For SARIMAX: specify seasonal period (s = 12 for monthly, s = 4 for quarterly, s = 7 for daily)

### Step 4: Residual Diagnostics
- Ljung-Box test: null = residuals are white noise; p > 0.05 = pass
- Residual ACF: no significant autocorrelation
- Residual normality: Jarque-Bera test, Q-Q plot
- Residual homoscedasticity: plot residuals vs fitted

### Step 5: Model Selection
- Compare candidate models via AIC, BIC
- Prefer: lowest AIC (predictive accuracy) or BIC (parsimony)
- Out-of-sample validation: hold out last 20% of series, forecast, compare to actual

### Step 6: Forecasting
- Generate point forecasts and prediction intervals
- Forecast horizon: ≤ 1/3 of series length (beyond that, uncertainty explodes)
- Report: forecast values, 95% prediction intervals, fan chart

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| ADF p < 0.05 | Stationary | Non-stationary | Difference series |
| Ljung-Box p > 0.05 | White noise residuals | Residual autocorrelation | Increase p or q |
| Residual normality | Approximately normal | Non-normal | Check for outliers, use robust |
| Forecast accuracy | MAPE < 20% | Poor forecasts | Try alternative model |

### Red Flags
- **ACF decays very slowly**: long memory process; consider ARFIMA
- **Seasonal pattern not captured**: increase seasonal order or use STL decomposition
- **Forecast intervals too wide**: high uncertainty; report with appropriate caution
- **Structural break detected**: pre-break and post-break dynamics differ; model separately

## Reporting Template
> "The time series was modeled using a SARIMAX([p,d,q])([P,D,Q],[s]) model selected by minimizing AIC. The series was [stationary/differenced once]. Residual diagnostics confirmed no remaining autocorrelation (Ljung-Box Q = [value], p = [value]). The model explained [percentage]% of variance (R² = [value])."

## Output Specification
- `analysis/03_analytical/time_series_results.json`: model order, coefficients, diagnostics, forecast values, prediction intervals

## Validation Checks
- [ ] Stationarity tested and addressed
- [ ] Model order justified (AIC/PACF/ACF)
- [ ] Ljung-Box test reported
- [ ] Forecast horizon ≤ 1/3 of series length
""",
    "spatial_analysis": """---
skill_id: "spatial_analysis"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["ecology", "epidemiology", "geography"]
required_tools: ["python", "geopandas", "libpysal", "mapclassify"]
depends_on: ["profile_spatial", "descriptive_stats"]
produces: ["analysis/03_analytical/spatial_results.json"]
complexity: "advanced"
---

# Skill: Spatial Statistical Analysis

## Purpose
Model spatial dependence and heterogeneity using spatial regression, kriging, and spatial cluster detection.

## When to Use
- Spatial autocorrelation detected (Moran's I significant)
- Location matters for the research question
- Need to account for spatial dependence in regression

## When NOT to Use
- No spatial autocorrelation (standard regression is fine)
- Spatial resolution too coarse
- Only descriptive mapping needed

## Decision Protocol

### Method Selection
| Question | Method |
|----------|--------|
| Spatial pattern of point events | Kernel density, K-function |
| Spatial interpolation | Kriging (ordinary, universal) |
| Spatial cluster detection | Getis-Ord Gi*, SaTScan |
| Regression with spatial dependence | Spatial lag (SAR) or spatial error (SEM) |
| Spatially varying relationships | Geographically Weighted Regression (GWR) |
| Areal data with neighbors | CAR/BYM models |

## Execution Protocol

### Step 1: Spatial Weights Matrix
- Define neighbor structure: k-nearest neighbors, distance band, queen/rook contiguity
- Row-standardize weights (each row sums to 1)
- Check: no islands (observations with no neighbors)
- If islands: increase k or distance threshold

### Step 2: Spatial Regression Model Selection
- Run OLS first as baseline
- Lagrange Multiplier tests:
  - LM-lag significant → spatial lag model (SAR)
  - LM-error significant → spatial error model (SEM)
  - Both significant → compare robust LM tests
- SAR: y = ρWy + Xβ + ε (spillover effects)
- SEM: y = Xβ + u, u = λWu + ε (spatially correlated errors)

### Step 3: Model Fitting
- SAR: maximum likelihood or 2SLS
- SEM: maximum likelihood
- Report: spatial autoregressive coefficient (ρ or λ), SE, p-value
- Compare to OLS: AIC, log-likelihood, R²

### Step 4: Spatial Interpolation (Kriging)
- Compute empirical variogram: semivariance vs distance
- Fit variogram model: spherical, exponential, Gaussian
- Check: nugget, sill, range parameters
- Cross-validate: leave-one-out prediction error

### Step 5: Hot Spot Detection
- Getis-Ord Gi*: identifies clusters of high/low values
- Significance: z-score and p-value with multiple testing correction
- Output: hot spots (high-high), cold spots (low-low), not significant

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| Moran's I on residuals | Not significant | Spatial dependence remains | Try alternative spatial model |
| Variogram fit | Good fit to empirical | Poor variogram model | Try different model form |
| Kriging cross-validation | RMSE acceptable | Poor predictions | Increase search radius |
| Spatial model vs OLS | Lower AIC | No spatial improvement | Use OLS |

### Red Flags
- **ρ or λ near 1.0**: spatial process near non-stationary; results sensitive to weights specification
- **Islands in weights matrix**: observations disconnected; results for islands unreliable
- **Variogram shows no sill**: spatial correlation extends beyond study area
- **GWR bandwidth too small**: overfitting; local estimates unstable

## Reporting Template
> "Spatial dependence was assessed using Moran's I (I = [value], p = [value]). A spatial [lag/error] model was fitted, with spatial autoregressive coefficient ρ = [value] (SE = [value], p = [value]). The spatial model improved fit over OLS (ΔAIC = [value], ΔR² = [value])."

## Output Specification
- `analysis/03_analytical/spatial_results.json`: spatial weights specification, model coefficients, spatial parameters, variogram parameters, hot spot results

## Validation Checks
- [ ] Spatial weights matrix has no islands
- [ ] Spatial parameter (ρ or λ) in (-1, 1)
- [ ] Variogram parameters are positive
- [ ] Hot spots corrected for multiple testing
""",
    "descriptive_stats": """---
skill_id: "descriptive_stats"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "pandas", "numpy", "scipy"]
depends_on: ["profile_tabular"]
produces: ["analysis/03_analytical/descriptive_results.json"]
complexity: "basic"
---

# Skill: Descriptive Statistical Analysis

## Purpose
Compute robust descriptive statistics with bootstrapped uncertainty estimates for all analysis variables.

## When to Use
- After profiling, before any inferential testing
- For Table 1 / baseline characteristics
- To understand variable distributions before model selection

## When NOT to Use
- Data not yet profiled
- Only inferential results needed (descriptive is still recommended)

## Execution Protocol

### Step 1: Weight Application
- If sampling weights specified: compute weighted mean, weighted variance
- Weighted mean: μ_w = Σ(w_i × x_i) / Σ(w_i)
- Weighted variance: σ²_w = Σ[w_i × (x_i - μ_w)²] / (Σw_i - 1)
- Log effective sample size after weighting

### Step 2: Continuous Variable Summaries
Per variable compute: N, mean, SD, median, IQR, skewness (G1), kurtosis (G2), min, max, SE of mean, SE of median
- If |G1| > 1.0: report median/IQR as primary, mean/SD as secondary
- If |G1| ≤ 1.0: report mean/SD as primary

### Step 3: Categorical Variable Summaries
Per variable: N, category frequencies, proportions, mode, Shannon entropy
- Present as count (percentage) format

### Step 4: Bootstrapped Uncertainty
- B = 10,000 bootstrap resamples
- Compute BCa (bias-corrected and accelerated) 95% CI for mean and median
- BCa adjusts for skewness in bootstrap distribution
- If bootstrap CI much wider than parametric CI: heavy-tailed distribution

### Step 5: Grouped Descriptives
- If grouping variable specified (e.g., treatment vs control):
  - Compute descriptives per group
  - Compute standardized mean difference (Cohen's d) between groups
  - Flag variables with |d| > 0.25 (potential imbalance)

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| Skewness | |G1| < 1.0 | Non-normal; median preferred | Use non-parametric tests |
| Bootstrap CI width | Similar to parametric CI | Heavy tails / outliers | Report bootstrap CI, not parametric |
| Group balance | |d| < 0.25 | Covariate imbalance | Adjust in model or match |

### Red Flags
- **Mean and median differ by > 1 SD**: distribution heavily skewed; do not use mean for inference
- **SD > mean for positive-only variable**: extreme skew or outliers; consider log transform
- **Bootstrap failed to converge**: increase B or check for degenerate distribution

## Reporting Template
> "Continuous variables are reported as mean (SD) or median [IQR] based on distributional symmetry. Categorical variables are reported as n (%). Bootstrapped 95% BCa confidence intervals (10,000 resamples) are provided for all estimates."

## Output Specification
- `analysis/03_analytical/descriptive_results.json`: per-variable statistics, bootstrap CIs, group comparisons, effect sizes

## Validation Checks
- [ ] N matches non-null count for each variable
- [ ] Bootstrap CIs within variable range
- [ ] Proportions sum to 1.0 per categorical variable
- [ ] Cohen's d correctly signed
""",
    "network_analysis": """---
skill_id: "network_analysis"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "networkx", "scipy"]
depends_on: ["profile_network", "descriptive_stats"]
produces: ["analysis/03_analytical/network_results.json"]
complexity: "advanced"
---

# Skill: Network Statistical Analysis

## Purpose
Perform statistical analysis on network data including community detection, centrality-based inference, and network comparison.

## When to Use
- Research question involves relationships, influence, or connectivity
- Need to identify key nodes, communities, or structural patterns
- Comparing networks across conditions or time

## When NOT to Use
- Network is trivially small (< 10 nodes)
- Only descriptive network stats needed (use profile_network)
- Edges are not meaningful (random associations)

## Execution Protocol

### Step 1: Network Construction Validation
- Verify edge list: no self-loops (unless intentional), no duplicate edges
- Confirm: directed vs undirected, weighted vs unweighted
- Check: largest connected component includes ≥ 80% of nodes

### Step 2: Centrality-Based Analysis
- Compute centrality measures: degree, betweenness, closeness, eigenvector
- Identify top-k nodes by each measure
- Test: do central nodes differ on outcome variables?
- Correlate centrality with node attributes (point-biserial or Spearman)

### Step 3: Community Detection & Validation
- Detect communities: Louvain (modularity optimization) or Leiden (improved)
- Report: number of communities, modularity Q, community sizes
- Validate: conductance (ratio of external to internal edges per community)
- Characterize communities: what attributes define each community?

### Step 4: Network Comparison
- If comparing two or more networks:
  - Global: density, average clustering, diameter, assortativity
  - Degree distribution: Kolmogorov-Smirnov test
  - Community structure: compare modularity, number of communities
  - Node-level: compare centrality distributions

### Step 5: Statistical Network Modeling
- ERGM (Exponential Random Graph Model): model probability of edge formation
- Terms: edges (density), nodematch (homophily), gwesp (transitivity)
- Check: MCMC convergence, goodness-of-fit
- SAOM (Stochastic Actor-Oriented Model): for longitudinal networks

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| Giant component | > 80% of nodes | Fragmented network | Analyze components separately |
| Modularity Q | > 0.3 | No clear communities | Use alternative clustering |
| ERGM GOF | Model reproduces observed stats | Model misspecified | Add/change terms |
| Centrality correlation | Significant | Central nodes differ | Report attribute-centrality relationship |

### Red Flags
- **Degree distribution has extreme outliers**: few nodes dominate; results driven by hubs
- **Modularity Q < 0.1**: no meaningful community structure
- **ERGM degenerate**: model produces unrealistic networks; simplify terms
- **Network density > 0.80**: nearly complete graph; little structure to analyze

## Reporting Template
> "The network comprised N = [value] nodes and E = [value] edges (density = [value]). Community detection identified [count] communities (modularity Q = [value]). [Node attribute] was significantly associated with degree centrality (r = [value], p = [value])."

## Output Specification
- `analysis/03_analytical/network_results.json`: centrality rankings, community structure, network comparison results, ERGM coefficients

## Validation Checks
- [ ] Network is constructible and connected
- [ ] Centrality measures sum to expected totals
- [ ] Modularity in [-0.5, 1]
- [ ] ERGM converges and passes GOF
""",
    "dimensionality_reduction": """---
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
""",
    "clustering": """---
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
""",
    "nlp_analysis": """---
skill_id: "nlp_analysis"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "scikit-learn", "gensim|bertopic", "spacy"]
depends_on: ["profile_text"]
produces: ["analysis/03_analytical/nlp_results.json"]
complexity: "advanced"
---

# Skill: Text Analysis & Topic Modeling

## Purpose
Extract latent topics, compute text representations, and perform statistical analysis on text corpora.

## When to Use
- Research question involves text content (themes, sentiment, discourse)
- Need to reduce text to quantifiable features
- Comparing text across groups or over time

## When NOT to Use
- Text is too short (< 10 words per document)
- Only keyword counting needed (use simple frequency analysis)
- Corpus is too small (< 50 documents)

## Decision Protocol

### Method Selection
| Goal | Method |
|------|--------|
| Discover latent themes | LDA, NMF, or BERTopic |
| Document similarity | TF-IDF + cosine similarity, or embeddings |
| Sentiment analysis | VADER, TextBlob, or fine-tuned transformer |
| Text classification | Naive Bayes, SVM, or fine-tuned LLM |
| Keyword extraction | RAKE, YAKE, or KeyBERT |
| Topic evolution over time | Dynamic Topic Modeling |

## Execution Protocol

### Step 1: Text Preprocessing
- Lowercase, remove punctuation, remove numbers (optional)
- Remove stopwords (domain-specific list if available)
- Lemmatize (not stem: preserves interpretability)
- Remove documents with < 3 tokens after preprocessing
- Remove tokens appearing in < 2 documents or > 95% of documents

### Step 2: Topic Modeling
**LDA (Latent Dirichlet Allocation):**
- Iterate k = 2 to 20 topics
- Select optimal k by: coherence score (C_v), perplexity, or silhouette
- Report: top-10 terms per topic, topic proportions per document
- Interpret: name each topic based on top terms

**BERTopic (modern alternative):**
- Uses sentence embeddings + HDBSCAN + class-based TF-IDF
- Auto-detects number of topics
- More coherent topics than LDA
- Supports dynamic topic modeling

### Step 3: Topic Validation
- Coherence score C_v: > 0.50 = interpretable, > 0.60 = good
- Topic diversity: measure overlap between top terms
- Human validation: sample documents from each topic, check coherence
- Stability: run multiple times with different seeds; check consistency

### Step 4: Downstream Analysis
- Topic prevalence by group: chi-square or ANOVA on topic proportions
- Topic prevalence over time: trend analysis
- Document-level: correlate topic proportions with outcome variables
- Topic networks: which topics co-occur in documents?

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| Coherence C_v | > 0.50 | Topics uninterpretable | Adjust k, change preprocessing |
| Topic diversity | > 0.70 | Topics overlap heavily | Increase alpha, reduce k |
| Stability | Consistent across runs | Unstable topics | Increase corpus size or iterations |
| Coverage | > 80% docs assigned | Many docs unassigned | Lower threshold or add "other" topic |

### Red Flags
- **Dominant topic (> 50% of documents)**: preprocessing too aggressive or k too small
- **Topics differ only by function words**: stopwords not properly removed
- **Coherence decreases as k increases**: overfitting; choose smaller k
- **BERTopic produces single "miscellaneous" topic**: embeddings not discriminative; try different model

## Reporting Template
> "Topic modeling was performed using [LDA/BERTopic] with k = [value] topics selected by [criterion]. The average coherence score was C_v = [value]. Top topics included: [Topic 1 name] ([percentage]% of documents), [Topic 2 name] ([percentage]%). Topic prevalence differed significantly between [groups] (χ² = [value], p = [value])."

## Output Specification
- `analysis/03_analytical/nlp_results.json`: topic assignments, coherence scores, top terms per topic, topic proportions, downstream analysis results

## Validation Checks
- [ ] Optimal k justified by coherence or other criterion
- [ ] Each topic is interpretable and named
- [ ] Coherence score reported
- [ ] Topic proportions sum to 1.0 per document
""",
    "longitudinal_analysis": """---
skill_id: "longitudinal_analysis"
version: "1.0.0"
category: "analysis"
depends_on: ["profile_tabular", "assumption_validator"]
produces: ["02_experiments/<exp>/outputs/analysis/longitudinal_results.json"]
complexity: "intensive"
---

# Skill: Longitudinal Analysis

## Purpose
Analyze repeated-measures and panel data. Covers paired t-tests, repeated measures ANOVA, linear mixed effects (LME), and latent growth curve (LGC) models.

---

## Protocol

### Step 1: Detect Data Structure
Identify:
- **Subject ID column**: unique identifier for each participant/unit
- **Time column**: measurement occasion (numeric or ordered categorical)
- **Outcome variable(s)**: repeated measurements
- **Covariates**: time-invariant (e.g., gender) and time-varying (e.g., treatment status)

Count: number of subjects (N), number of time points (T), balance (balanced vs unbalanced).

### Step 2: Select Method by Decision Table

| Time Points | Trend | Individual Differences | Method |
|-------------|-------|----------------------|--------|
| 2 | Any | Not needed | Paired t-test |
| 2 | Any | Need to adjust for covariates | ANCOVA on change score |
| 3+ | Linear | Not needed | Repeated measures ANOVA |
| 3+ | Linear | Yes (random slopes) | LME: `outcome ~ time + (1 + time \\| subject)` |
| 3+ | Nonlinear | Yes | LME with polynomial time or splines |
| 3+ | Any | Latent trajectory classes | Latent Growth Curve (SEM) |
| Irregular spacing | Any | Yes | LME with continuous time |
| Unbalanced | Any | Yes | LME (handles missing time points) |

### Step 3: Paired t-Test (2 Time Points)
`scipy.stats.ttest_rel(time1, time2)`. Report: mean difference, 95% CI, t(df), p-value, Cohen's d_z = mean_diff / SD_diff.

### Step 4: Repeated Measures ANOVA (3+ Time Points, Balanced)
`pingouin.rm_anova(dv, subject, within, data)`. Check sphericity with Mauchly's test. If violated, apply Greenhouse-Geisser correction. Report: F(df_num, df_den), p, η²_p (partial eta-squared).

### Step 5: Linear Mixed Effects Model
Use `statsmodels.MixedLM` or `statsmodels` formula API:
```python
import statsmodels.formula.api as smf
model = smf.mixedlm("outcome ~ time + treatment + time:treatment",
                    data=df, groups=df["subject_id"],
                    re_formula="~time")
result = model.fit(reml=True)
```
Report: fixed effects (β, SE, 95% CI, p), random effects variance components, ICC, AIC/BIC.

### Step 6: Nonlinear Trends
Add polynomial terms: `time + time² + time³`, or use splines:
```python
from patsy import dmatrix
spline_basis = dmatrix("bs(time, df=4, degree=3)", {"time": df["time"]})
```
Compare models with likelihood ratio test or AIC.

### Step 7: Latent Growth Curve Model (SEM)
Use `semopy` or manual specification:
- Intercept factor: loadings fixed to 1 at all time points
- Slope factor: loadings fixed to 0, 1, 2, ... (linear) or time values
- Estimate: mean and variance of intercept and slope factors
- Fit indices: CFI, TLI, RMSEA, SRMR

### Step 8: Diagnostics
- Residual plots: residuals vs fitted, residuals vs time
- Random effects: check normality of BLUPs
- Influence: Cook's D for mixed models
- Missing data: verify MAR assumption, compare completers vs dropouts

### Step 9: Output
Save to `02_experiments/<exp>/outputs/analysis/longitudinal_results.json`:
- Method used with rationale
- Fixed effects table (β, SE, CI, p)
- Random effects variance components
- Model fit indices (AIC, BIC, ICC)
- Diagnostics results
- Predicted trajectories plot data

---

## Validation
- [ ] Data structure identified (N subjects, T time points, balanced/unbalanced)
- [ ] Method selected per decision table
- [ ] Sphericity checked (if RM ANOVA)
- [ ] Random effects structure justified
- [ ] Model fit indices reported
- [ ] Diagnostics: residuals, random effects normality
- [ ] Results saved to JSON
""",
    "survival_analysis": """---
skill_id: "survival_analysis"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["epidemiology", "medicine", "engineering"]
required_tools: ["python", "lifelines", "scipy", "pandas"]
depends_on: ["descriptive_stats"]
produces: ["analysis/03_analytical/survival_results.json"]
complexity: "advanced"
---

# Skill: Survival (Time-to-Event) Analysis

## Purpose
Model time-to-event data with censoring, estimate survival functions, and assess covariate effects on hazard rates.

## When to Use
- Outcome is time until an event (death, failure, recovery, churn)
- Some observations are censored (event not yet observed)
- Want to compare survival between groups or model covariate effects

## When NOT to Use
- No time-to-event outcome
- No censoring (all events observed)
- Event is not well-defined or time is not meaningful

## Decision Protocol

### Method Selection
| Question | Method |
|----------|--------|
| Describe survival over time | Kaplan-Meier estimator |
| Compare survival between groups | Log-rank test |
| Model covariate effects on hazard | Cox proportional hazards |
| Model covariate effects on survival time | Accelerated Failure Time (AFT) |
| Time-varying covariates | Extended Cox model |
| Competing risks | Fine-Gray subdistribution hazard |
| Recurrent events | Andersen-Gill model |

## Execution Protocol

### Step 1: Data Structure
- Define: duration (time from entry to event or censoring), event indicator (1 = event, 0 = censored)
- Check: no negative durations, no events at time 0
- Identify: entry time (left-truncation), exit time, event type

### Step 2: Descriptive Survival
- Kaplan-Meier estimator: Ŝ(t) = Π(1 - dᵢ/nᵢ) for tᵢ ≤ t
- Median survival time: time at which Ŝ(t) = 0.50
- Survival probabilities at key timepoints (e.g., 1-year, 5-year)
- Number at risk table over time

### Step 3: Group Comparison
- Log-rank test: compares observed vs expected events across groups
- If significant: pairwise log-rank tests with Bonferroni correction
- Report: chi-square statistic, df, p-value
- Visual: Kaplan-Meier curves with confidence bands

### Step 4: Cox Proportional Hazards Model
- Model: h(t|X) = h₀(t) × exp(β'X)
- Estimate: partial likelihood maximization
- Report: hazard ratios (HR = exp(β)), 95% CI, p-values
- Interpret: HR > 1 = increased hazard, HR < 1 = decreased hazard

### Step 5: Proportional Hazards Assumption
- Schoenfeld residuals test: null = PH holds
- If p < 0.05: PH violated for that covariate
- Visual: log(-log(S(t))) plots should be parallel
- If violated: add time-interaction term or use stratified Cox model

### Step 6: Model Diagnostics
- Residuals: martingale, deviance, Schoenfeld
- Influential observations: dfbeta, dfbetas
- Functional form: martingale residuals vs continuous covariates
- Overall fit: concordance index (C-statistic)

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| PH assumption | Schoenfeld p > 0.05 | Time-varying effect | Add time interaction or stratify |
| Censoring rate | < 50% | Heavy censoring | Results uncertain; report with caution |
| Concordance | > 0.60 | Poor discrimination | Add predictors or use flexible model |
| Influential points | No extreme dfbeta | Single observation drives result | Report sensitivity analysis |

### Red Flags
- **All events at same time**: discrete-time survival model needed
- **Censoring > 80%**: insufficient events; results unreliable
- **HR CI includes 1.0 with wide range**: underpowered; report as inconclusive
- **Non-monotonic KM curve**: data error (event before entry time)

## Reporting Template
> "Survival was estimated using the Kaplan-Meier method. Median survival was [value] months (95% CI [lower, upper]). The log-rank test indicated a significant difference between groups (χ² = [value], p = [value]). In the Cox model, [covariate] was associated with [increased/decreased] hazard (HR = [value], 95% CI [lower, upper], p = [value]). The proportional hazards assumption was [satisfied/violated]."

## Output Specification
- `analysis/03_analytical/survival_results.json`: KM estimates, log-rank results, Cox model coefficients, HRs, PH test results, diagnostics

## Validation Checks
- [ ] No negative durations
- [ ] Event indicator is binary (0/1)
- [ ] KM curve is monotonically non-increasing
- [ ] PH assumption tested and reported
- [ ] Concordance index reported
""",
    "meta_analysis": """---
skill_id: "meta_analysis"
version: "1.0.0"
category: "analysis"
depends_on: ["literature_deep", "extract_claims"]
produces: ["03_synthesis/meta_analysis_results.json", "03_synthesis/outputs/figures/forest_plot.png", "03_synthesis/outputs/figures/funnel_plot.png"]
complexity: "intensive"
---

# Skill: Meta-Analysis

## Purpose
Pool effect sizes across studies from the evidence matrix. Compute weighted mean effects, test heterogeneity, generate forest and funnel plots.

---

## Protocol

### Step 1: Extract Effect Sizes
Read `reports/literature/evidence_matrix.json`. For each study, extract:
- Effect size (Cohen's d, log odds ratio, correlation r, or Hedges' g)
- Standard error of effect size
- Sample size (total, treatment, control)
- Study identifier

Convert all effects to a common metric if needed:
- r → Fisher's z: `z = 0.5 * ln((1+r)/(1-r))`, SE = `1/sqrt(N-3)`
- OR → log OR: `log(OR)`, SE computed from 2×2 cell counts
- t-statistic → d: `d = 2t/sqrt(df)`

### Step 2: Fixed-Effect Model (Inverse-Variance Weighting)
Compute weighted mean: `μ = Σ(w_i × θ_i) / Σ(w_i)` where `w_i = 1/SE_i²`
SE of pooled effect: `SE_μ = 1/sqrt(Σw_i)`
95% CI: `μ ± 1.96 × SE_μ`

### Step 3: Heterogeneity Test
Cochran's Q: `Q = Σ(w_i × (θ_i - μ)²)` with df = k-1, p-value from χ²(df)
I² statistic: `I² = max(0, (Q - df)/Q) × 100%`
Interpretation: I² < 25% = low, 25-75% = moderate, > 75% = high heterogeneity

### Step 4: Random-Effects Model (if I² > 50%)
DerSimonian-Laird estimator:
1. Compute between-study variance: `τ² = (Q - df) / (Σw_i - Σw_i²/Σw_i)`
2. Adjust weights: `w_i* = 1/(SE_i² + τ²)`
3. Pooled effect: `μ_RE = Σ(w_i* × θ_i) / Σ(w_i*)`
4. SE and CI as in Step 2 but with adjusted weights

### Step 5: Forest Plot
Generate `forest_plot.png`:
- Each study as a square (size ∝ weight) with horizontal CI line
- Pooled estimate as diamond at bottom
- Vertical line at null effect
- Labels: study name, effect size, 95% CI, weight %
- Subtitle: model type, Q, I², τ²

### Step 6: Funnel Plot (Publication Bias)
Generate `funnel_plot.png`:
- X-axis: effect size, Y-axis: standard error (inverted)
- Pseudo 95% confidence bounds (funnel shape)
- Egger's regression test: `regress(effect/SE on 1/SE)`, intercept ≠ 0 → asymmetry
- Trim-and-fill: estimate missing studies, adjust pooled effect

### Step 7: Output
Save to `03_synthesis/meta_analysis_results.json`:
- Per-study effect sizes and weights
- Fixed-effect pooled estimate with CI
- Heterogeneity: Q, df, p-value, I², τ²
- Random-effects pooled estimate (if applicable)
- Funnel plot asymmetry test results
- Model selection rationale

---

## Validation
- [ ] Effect sizes extracted from evidence matrix
- [ ] All effects converted to common metric
- [ ] Fixed-effect model computed with inverse-variance weights
- [ ] Heterogeneity: Q, I², τ² reported
- [ ] Random-effects model used if I² > 50%
- [ ] Forest plot generated with study labels and pooled diamond
- [ ] Funnel plot generated with Egger's test
- [ ] Results saved to JSON
""",
    "search_semantic_scholar": """---
skill_id: "search_semantic_scholar"
version: "7.0.0"
category: "literature"
domain_compatibility: ["all"]
required_tools: ["python", "requests"]
depends_on: []
produces: ["literature/semantic_scholar_results.json"]
complexity: "basic"
---

# Skill: Semantic Scholar API Search

## Purpose
Query the Semantic Scholar Graph API to retrieve academic papers with citation metadata, abstracts, and influence metrics.

## When to Use
- Initial literature search for any research topic
- Finding highly-cited papers in a domain
- Building a seed corpus for snowball citation search

## When NOT to Use
- Need biomedical-specific search (use search_pubmed)
- Need preprint-only search (use search_arxiv)
- API rate limit exhausted (cache results first)

## Execution Protocol

### Step 1: Query Construction
- Extract key terms from research brief
- Construct query: combine terms with AND/OR operators
- Use field-specific search: `title:term`, `abstract:term`
- Limit query length to avoid API truncation

### Step 2: API Request
- Endpoint: `https://api.semanticscholar.org/graph/v1/paper/search`
- Fields: title, abstract, year, authors, citationCount, referenceCount, influentialCitationCount, externalIds (DOI), publicationVenue, fieldsOfStudy
- Parameters: limit (default 50, max 100), offset (pagination), year range, fieldsOfStudy filter
- Handle rate limiting: 100 requests/5 minutes without API key, exponential backoff on HTTP 429

### Step 3: Result Processing
- Filter: remove papers without abstracts (unless seminal)
- Filter: remove papers outside year range (if specified)
- Deduplicate: by DOI
- Sort: by citationCount (default) or relevance
- Score: compute relevance score based on query term overlap in title + abstract

### Step 4: Quality Assessment
- Flag papers with: citationCount = 0 (may be very new or low quality)
- Flag predatory journals (check publication venue)
- Prioritize: papers in top-tier venues, high citation counts, recent publications

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| Results returned | ≥ 10 papers | Broaden query or check API |
| Abstracts present | > 80% have abstracts | Accept without abstracts for seminal papers |
| Year distribution | Spans relevant period | Adjust year filter |
| Citation distribution | Mix of highly-cited and recent | Query may be too narrow |

## Output Specification
- `literature/semantic_scholar_results.json`: paper objects with title, authors, year, abstract, DOI, citationCount, relevance score, fieldsOfStudy

## Validation Checks
- [ ] All papers have valid DOI or externalId
- [ ] Results ≤ limit parameter
- [ ] No duplicate DOIs
- [ ] Relevance scores computed
""",
    "search_arxiv": """---
skill_id: "search_arxiv"
version: "7.0.0"
category: "literature"
domain_compatibility: ["all"]
required_tools: ["python", "requests", "feedparser"]
depends_on: []
produces: ["literature/arxiv_results.json"]
complexity: "basic"
---

# Skill: arXiv Preprint Search

## Purpose
Search arXiv for preprints in physics, mathematics, computer science, quantitative biology, and related fields.

## When to Use
- Need latest preprints not yet peer-reviewed
- CS, physics, math, statistics, or quantitative biology research
- Tracking cutting-edge developments

## When NOT to Use
- Need peer-reviewed literature only
- Non-quantitative fields (humanities, social sciences)

## Execution Protocol

### Step 1: Query Construction
- Use arXiv API query syntax: `ti:"term"` (title), `au:"name"` (author), `abs:"term"` (abstract)
- Category filters: cs.AI, cs.LG, stat.ML, q-bio, physics, math, etc.
- Combine with AND (`AND`), OR (`OR`), NOT (`ANDNOT`)

### Step 2: API Request
- Endpoint: `http://export.arxiv.org/api/query`
- Parameters: search_query, max_results (default 10, max 30000), sortBy (relevance/lastUpdatedDate/submittedDate), sortOrder
- Parse Atom XML response using feedparser

### Step 3: Result Processing
- Extract: arXiv ID, title, authors, abstract, categories, published date, updated date, DOI (if available)
- Filter: by category, date range
- Deduplicate: by arXiv ID
- Note: preprints may have multiple versions; use latest version

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| Results returned | ≥ 5 papers | Broaden category filter |
| Recent papers | Within last 2 years | Adjust date filter |
| Abstracts present | 100% | Always available on arXiv |

## Output Specification
- `literature/arxiv_results.json`: paper objects with arXiv ID, title, abstract, authors, categories, dates, DOI

## Validation Checks
- [ ] All papers have valid arXiv ID
- [ ] Categories are valid arXiv categories
- [ ] Results sorted by specified criterion
""",
    "generate_bibtex": """---
skill_id: "generate_bibtex"
version: "7.0.0"
category: "literature"
domain_compatibility: ["all"]
required_tools: ["python", "bibtexparser|pybtex"]
depends_on: ["search_semantic_scholar", "extract_claims"]
produces: ["literature/references.bib"]
complexity: "basic"
---

# Skill: BibTeX Reference Generation

## Purpose
Generate a complete, validated BibTeX file from the literature corpus for use in manuscript writing.

## When to Use
- After literature search and claim extraction
- Before writing IMRAD manuscript
- Need formatted references for any output

## When NOT to Use
- Only in-text citations needed
- Reference manager (Zotero, EndNote) already has entries

## Execution Protocol

### Step 1: Entry Collection
- Gather all papers from corpus with: DOI, title, authors, year, journal, volume, pages
- For each paper: determine entry type (article, inproceedings, book, chapter, misc)

### Step 2: BibTeX Entry Generation
- Generate standard BibTeX entry per paper:
  - `@article`: journal articles (most common)
  - `@inproceedings`: conference papers
  - `@book`: books
  - `@incollection`: book chapters
  - `@misc`: preprints, reports
- Citation key: AuthorYearFirstWord (e.g., Smith2024Causal)
- Ensure all required fields present per entry type

### Step 3: Validation
- Check: all entries parse as valid BibTeX
- Check: no duplicate citation keys
- Check: all entries have DOI or URL
- Validate author names: "Last, First" format
- Validate year: 4-digit integer

### Step 4: Organization
- Sort entries alphabetically by citation key
- Add comments grouping by theme (optional)
- Generate entry count by type and year

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| All entries parse | Valid BibTeX | Fix formatting errors |
| No duplicate keys | Unique keys | Regenerate conflicting keys |
| DOI present | > 90% | Search for missing DOIs |
| Author format | "Last, First" | Reformat author strings |

## Output Specification
- `literature/references.bib`: complete BibTeX file with all corpus papers

## Validation Checks
- [ ] File parses as valid BibTeX
- [ ] Entry count matches corpus size
- [ ] No duplicate citation keys
- [ ] All entries have required fields for their type
""",
    "snowball_citations": """---
skill_id: "snowball_citations"
version: "7.0.0"
category: "literature"
domain_compatibility: ["all"]
required_tools: ["python", "requests"]
depends_on: ["search_semantic_scholar"]
produces: ["literature/citation_graph.json", "literature/snowball_corpus.json"]
complexity: "intermediate"
---

# Skill: Snowball Citation Search

## Purpose
Expand a seed set of papers through forward chaining (papers that cite them) and backward chaining (papers they cite) to build a comprehensive literature corpus.

## When to Use
- After initial search has identified seed papers
- Need comprehensive coverage of a research area
- Building evidence matrix for systematic review

## When NOT to Use
- Only a few papers needed
- Seed papers are not well-chosen (garbage in, garbage out)
- API rate limits exhausted

## Execution Protocol

### Step 1: Seed Paper Selection
- Start with 5-20 highly-relevant papers from initial search
- Prioritize: high citation count, recent, review articles, seminal works
- Record: DOI, title, year for each seed

### Step 2: Backward Chaining (References)
- For each seed paper: fetch its reference list
- From Semantic Scholar: `paper/{id}/references`
- Filter references: keep those with abstracts and DOIs
- Add to corpus if not already present

### Step 3: Forward Chaining (Citations)
- For each seed paper: fetch papers that cite it
- From Semantic Scholar: `paper/{id}/citations`
- Filter: keep papers within research scope (year, field)
- Add to corpus if not already present

### Step 4: Recursive Expansion
- For each newly added paper: repeat backward and forward chaining
- Maximum depth: 2 (seed → references/citations → their references/citations)
- Stop when: no new papers found, depth limit reached, or corpus size limit

### Step 5: Deduplication & Ranking
- Deduplicate by DOI
- Rank by: citation count, recency, relevance to research question
- Compute: network centrality in citation graph (papers cited by many others are central)

### Step 6: Corpus Finalization
- Output: unified corpus with all papers
- Output: citation graph (nodes = papers, edges = citation relationships)
- Output: relevance scores for each paper

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| Corpus growth | New papers found at each depth | Seed papers too narrow |
| Citation graph connected | Most papers connected | Disconnected subgraphs; add bridging seeds |
| Relevance maintained | > 70% papers relevant | Chaining drifted from topic; tighten filters |

### Red Flags
- **Corpus explodes (> 500 papers)**: topic too broad; narrow scope or reduce depth
- **No new papers at depth 1**: seed papers are very new or obscure
- **Citation graph has isolated nodes**: papers with no citation links in API data

## Output Specification
- `literature/citation_graph.json`: nodes (papers), edges (citation relationships)
- `literature/snowball_corpus.json`: deduplicated, ranked paper corpus with relevance scores

## Validation Checks
- [ ] No duplicate DOIs in corpus
- [ ] Citation graph edges reference valid nodes
- [ ] Depth limit respected
- [ ] All papers have DOI or arXiv ID
""",
    "extract_claims": """---
skill_id: "extract_claims"
version: "7.0.0"
category: "literature"
domain_compatibility: ["all"]
required_tools: ["python", "openai|anthropic|litellm"]
depends_on: ["search_semantic_scholar", "snowball_citations"]
produces: ["literature/evidence_matrix.json"]
complexity: "intermediate"
---

# Skill: Claim Extraction from Literature

## Purpose
Extract key claims, methods, findings, and limitations from each paper in the corpus into a structured evidence matrix.

## When to Use
- After literature search and snowballing
- Before literature synthesis
- Need structured comparison across papers

## When NOT to Use
- Only bibliographic data needed
- Corpus too large (> 200 papers; sample first)

## Execution Protocol

### Step 1: Paper Preparation
- For each paper: compile title, abstract, full text (if available)
- If full text not available: work with abstract + key sections
- Format: structured prompt for LLM extraction

### Step 2: Claim Extraction (per paper)
Extract the following fields:
- **Research question**: what does this paper investigate?
- **Methodology**: study design, sample size, analytical method
- **Key findings**: main results with effect sizes and p-values
- **Claims**: specific assertions made by authors
- **Limitations**: acknowledged limitations
- **Conflicts of interest**: funding sources, author disclosures
- **Replication status**: has this been replicated? (check citation context)

### Step 3: Evidence Matrix Construction
- Rows: papers (identified by DOI)
- Columns: claims/hypotheses from research brief
- Cells: support (+), contradict (-), neutral (0), not addressed (N/A)
- Add confidence rating: high (direct evidence), medium (indirect), low (speculative)

### Step 4: Quality Assessment
- Study design quality: RCT > cohort > case-control > cross-sectional > case report
- Sample size adequacy: powered for primary outcome?
- Statistical rigor: appropriate methods, multiple testing addressed?
- Replication: confirmed by independent studies?

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| Claims extracted | All papers processed | Some papers lack sufficient text |
| Evidence matrix filled | > 80% cells populated | Claims too specific; broaden |
| Quality scores assigned | All papers scored | Insufficient methodological detail |

## Output Specification
- `literature/evidence_matrix.json`: per-paper claims, methods, findings, quality scores, evidence matrix (papers × claims)

## Validation Checks
- [ ] Each paper has at least one claim extracted
- [ ] Evidence matrix covers all research brief hypotheses
- [ ] Quality scores use consistent scale
- [ ] Confidence ratings assigned
""",
    "related_work_writer": """---
skill_id: "related_work_writer"
version: "1.0.0"
category: "literature"
depends_on: ["literature_deep", "extract_claims"]
produces: ["03_synthesis/manuscript/related_work.md"]
complexity: "standard"
---

# Skill: Related Work Writer

## Purpose
Generate the Related Work / Literature Review section from the evidence matrix and paper clusters. Produces 3-5 themed paragraphs grounded strictly in cited papers.

---

## Protocol

### Step 1: Load Evidence Matrix & Clusters
Read `reports/literature/evidence_matrix.json` and `reports/literature/paper_clusters.json`. If no clusters exist, create them by grouping papers by methodology (RCT, observational, review, meta-analysis).

### Step 2: Select Themes
Choose 3-5 clusters to cover, prioritized by:
1. Relevance to the research question (highest first)
2. Recency (last 5 years preferred)
3. Methodological rigor (RCTs > longitudinal > cross-sectional)
4. Citation count (proxy for influence)

Skip clusters with < 2 papers or relevance score < 0.3.

### Step 3: Write Theme Paragraphs
For each selected cluster, write one paragraph:
1. **Opening sentence**: Introduce the theme (e.g., "Several randomized trials have examined the effect of X on Y...")
2. **Evidence summary**: Cite 3-5 papers with findings (e.g., "Smith et al. (2021) found a 15% reduction (95% CI: 8-22%, p<0.01), consistent with Jones et al. (2022)...")
3. **Consensus**: Note where papers agree
4. **Contradictions**: Note where papers disagree and possible reasons (different populations, methods, sample sizes)
5. **Gap**: End with what this cluster leaves unanswered

### Step 4: Write Positioning Paragraph
Final paragraph positions the present study:
1. Summarize the overall state of the literature in 1 sentence
2. Identify the specific gap the present study addresses
3. State how the present study fills this gap (method, population, analysis)
4. Template: "The present study addresses gap X by [method] in [population], extending prior work by [novel contribution]."

### Step 5: Grounding Check
Every claim must be traceable to a paper in the evidence matrix. For each sentence:
- Verify the cited paper exists in the corpus
- Verify the claim matches the paper's extracted findings
- If a claim cannot be grounded, remove it or mark as "author interpretation"

### Step 6: Output
Save to `03_synthesis/manuscript/related_work.md`:
- 3-5 theme paragraphs, each with 3-5 citations
- 1 positioning paragraph
- All citations in author-year format
- Bibliography entries cross-referenced with `references.bib`

---

## Paragraph Template

```
### [Theme Name]

[Opening sentence introducing the theme with 1-2 citations.] [Evidence sentence with specific findings, effect sizes, and sample sizes from 2-3 papers.] [Consensus sentence noting agreement across studies.] [Contradiction sentence if applicable, noting possible methodological reasons.] [Gap sentence: what this theme leaves unanswered.]
```

---

## Validation
- [ ] 3-5 theme paragraphs written
- [ ] Each paragraph cites 3-5 papers
- [ ] Every claim grounded in evidence matrix
- [ ] Positioning paragraph identifies specific gap
- [ ] No hallucinated citations or findings
- [ ] Output saved to `03_synthesis/manuscript/related_work.md`
""",
    "search_pubmed": """---
skill_id: "search_pubmed"
version: "7.0.0"
category: "literature"
domain_compatibility: ["epidemiology", "medicine", "biology"]
required_tools: ["python", "requests", "BeautifulSoup"]
depends_on: []
produces: ["literature/pubmed_results.json"]
complexity: "basic"
---

# Skill: PubMed/MEDLINE Search

## Purpose
Search PubMed for biomedical literature using E-utilities API with MeSH term support and systematic review filtering.

## When to Use
- Biomedical, clinical, or public health research
- Need MeSH (Medical Subject Headings) indexing
- Systematic review or meta-analysis literature search

## When NOT to Use
- Non-biomedical topic (use search_semantic_scholar)
- Need preprints (use search_arxiv or bioRxiv)

## Execution Protocol

### Step 1: Query Construction
- Translate research question to PICO format (Population, Intervention, Comparison, Outcome)
- Map terms to MeSH headings using MeSH database
- Construct E-utilities query with MeSH terms and free-text keywords
- Use Boolean operators: AND (intersection), OR (synonyms), NOT (exclusion)

### Step 2: API Request
- E-utilities endpoint: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`
- Step 1: `esearch.fcgi` to get PMIDs
- Step 2: `efetch.fcgi` to get full records (abstract, authors, MeSH terms)
- Rate limit: 10 requests/second without API key
- Filters: publication type (clinical trial, review, meta-analysis), species, language, date range

### Step 3: Result Processing
- Extract: PMID, title, abstract, authors, journal, year, MeSH terms, publication types
- Deduplicate: by PMID
- Score: relevance based on MeSH term match and abstract keyword overlap
- Flag: retracted publications (check PMID against retraction database)

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| Results returned | ≥ 10 papers | Broaden MeSH terms |
| MeSH terms assigned | > 70% | Include free-text search |
| Abstracts present | > 90% | Accept older papers without abstracts |

## Output Specification
- `literature/pubmed_results.json`: paper objects with PMID, title, abstract, authors, year, MeSH terms, publication types, relevance score

## Validation Checks
- [ ] All papers have valid PMID
- [ ] No duplicate PMIDs
- [ ] MeSH terms validated against MeSH database
- [ ] Results sorted by relevance
""",
    "web_search_grounding": """# Web Search Grounding — Anti-Hallucination Fact Verification

## Purpose
For any factual claim an agent makes that is NOT derived from an uploaded paper or computed from data, this skill must be invoked. Prevents agents from inventing statistics, facts, or references.

## When to Invoke

Invoke this skill whenever:
- Making a numeric claim (percentages, counts, statistics) not computed from project data
- Stating a fact about the real world not sourced from the literature corpus
- Referencing library/framework documentation or API behavior
- Making claims about current events, policies, or standards

## Search Sources (in priority order)

### 1. Context7 (`/context7`)
For library/framework documentation claims:
- Use `context7_resolve-library-id` to get the library ID
- Use `context7_query-docs` to fetch current documentation
- Mandatory for: scipy, statsmodels, pandas, sklearn, lifelines, pymc, networkx, geopandas, altair, bokeh, panel, holoviews, dash, plotly

### 2. Semantic Scholar API
For academic claims:
- `https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=10&fields=title,abstract,authors,year,citationCount`
- Use to verify academic statistics, effect sizes, methodological claims

### 3. CrossRef API
For publication metadata:
- `https://api.crossref.org/works?query={query}&select=title,author,published,DOI`
- Use to verify publication dates, author lists, journal names

### 4. NCBI E-utilities (PubMed)
For biomedical facts:
- `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmax=10`
- Use to verify biomedical statistics, prevalence rates, clinical findings

## Protocol

### Step 1: Identify the Claim
Extract the specific factual claim that needs grounding:
```
Claim: "X affects Y by approximately Z%"
Source type needed: empirical_study | documentation | statistic | policy
```

### Step 2: Select Search Source
Based on claim type:
- Library API → Context7
- Academic finding → Semantic Scholar
- Publication fact → CrossRef
- Biomedical fact → PubMed
- General fact → Semantic Scholar (broadest coverage)

### Step 3: Execute Search
- Formulate a precise search query
- Include year constraints if the claim is time-sensitive
- Execute the search via the appropriate API

### Step 4: Record Search
Store every search in `reports/literature/search_log.json`:
```json
{
  "timestamp": "ISO 8601",
  "claim": "The claim being verified",
  "query": "The exact search query",
  "source": "semantic_scholar|crossref|pubmed|context7",
  "results_count": 5,
  "top_result": {
    "title": "...",
    "url": "...",
    "snippet": "..."
  },
  "verified": true,
  "evidence": "Brief summary of supporting evidence"
}
```

### Step 5: Tag the Claim
In any output, tag claims based on verification status:
- `[VERIFIED: source]` — Confirmed by web search
- `[DATA: file_path]` — Computed from project data
- `[LITERATURE: DOI]` — From verified literature corpus
- `[UNVERIFIED]` — Could not be verified — requires human review

## Enforcement Rules

1. **No naked numbers:** No numeric claim may appear in manuscript without a trace to either computed data or a verified web source
2. **No invented APIs:** Library function calls must be verified via Context7
3. **No assumed facts:** If a fact cannot be verified, state uncertainty explicitly
4. **Log everything:** Every search is recorded with query, source, results, and timestamp
5. **Cache results:** Store verified facts in the research cache to avoid re-searching

## CLI Reference
```bash
# Search log is at: reports/literature/search_log.json
# Each entry is append-only — never modify previous entries
```
""",
    "verify_citations": """# Citation Verification — Three-Pass Anti-Hallucination Pipeline

## Purpose
Every citation must be triple-verified before appearing in any output. This skill is invoked by the `audit_validate` agent and the `citation_verifier.py` script.

## Protocol

### Pass 1 — Existence Check

For every citation in the bibliography or manuscript:

1. **DOI citations:** Call CrossRef API (`api.crossref.org/works/{doi}`)
   - Confirm title, authors, year match the claimed citation
   - Flag: 404 response or metadata mismatch

2. **arXiv IDs:** Call arXiv API (`export.arxiv.org/api/query?id_list={id}`)
   - Confirm title, authors, year match
   - Flag: not found or metadata mismatch

3. **PubMed IDs:** Call NCBI E-utilities (`eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=text&rettype=abstract`)
   - Confirm title, authors, year match
   - Flag: not found or metadata mismatch

4. **ISBN/Book citations:** Flag for manual review (no automated existence check)

**Output per citation:**
```json
{
  "citation": "Author et al., Year",
  "identifier": "10.xxxx/yyyy",
  "identifier_type": "doi",
  "pass_1": {
    "status": "verified|mismatch|not_found|skipped",
    "title": "Actual title from API",
    "authors": ["Author1", "Author2"],
    "year": 2024,
    "claimed_title": "Title as cited in manuscript",
    "claimed_year": 2024,
    "title_match": true,
    "year_match": true,
    "error": null
  }
}
```

### Pass 2 — Content Verification

For each citation used to support a specific claim:

1. Fetch abstract from Semantic Scholar API (`api.semanticscholar.org/graph/v1/paper/{identifier}`)
2. Evaluate: "Does this abstract support the claim '[claim text]'?"
3. Response: YES / NO / PARTIAL with 1-sentence justification
4. Flag PARTIAL or NO for human review
5. Never use a citation that fails Pass 2 without explicit `[UNVERIFIED]` tag

**Output per citation:**
```json
{
  "citation": "Author et al., Year",
  "claim": "The specific claim this citation supports",
  "pass_2": {
    "status": "supported|unsupported|partial|no_abstract",
    "justification": "The abstract reports X which supports/contradicts the claim because...",
    "abstract_snippet": "First 200 chars of abstract"
  }
}
```

### Pass 3 — Retraction Check

1. Query Retraction Watch database for the paper
2. Query CrossRef for retraction notices linked to DOI
3. **Hard block:** retracted papers cannot appear as supporting evidence
4. **Warn:** papers with expressions of concern

**Output per citation:**
```json
{
  "citation": "Author et al., Year",
  "pass_3": {
    "status": "clear|retracted|expression_of_concern|unknown",
    "retraction_date": null,
    "retraction_reason": null,
    "source": "crossref|retraction_watch|none"
  }
}
```

## Final Verification Report

Output: `reports/literature/citation_verification_report.json`

```json
{
  "schema_version": "1.0.0",
  "generated_at": "ISO 8601 timestamp",
  "total_citations": 42,
  "summary": {
    "fully_verified": 38,
    "unverified": 2,
    "retracted": 0,
    "partial_match": 2,
    "not_found": 0
  },
  "verdict": "PASS|FAIL",
  "citations": [
    {
      "citation": "...",
      "identifier": "...",
      "pass_1": {...},
      "pass_2": {...},
      "pass_3": {...},
      "overall_status": "verified|unverified|retracted|partial"
    }
  ]
}
```

**Verdict Rules:**
- PASS: all citations verified (pass 1 + pass 2 + pass 3 clear)
- FAIL: any citation is retracted, or >10% are unverified
- CONDITIONAL: some citations are partial_match or not_found but <10%

## Integration

- `audit_validate` agent runs this as Audit #6
- Any UNVERIFIED citation = gate FAIL
- Retracted paper = immediate FAIL, remove from manuscript
- Run via: `python -m research_copilot.utils.citation_verifier --bibliography reports/literature/bibliography.bib`
""",
    "literature_zotero_integration": """---
skill_id: "literature_zotero_integration"
version: "1.0.0"
category: "literature"
description: "Sync with Zotero/Mendeley libraries, read highlighted notes, and export bibliography.bib back to reference managers"
domain_compatibility: ["all"]
applies_to_phases: ["literature_deep"]
---

# Skill: Zotero & Semantic Scholar Integration

## Purpose

Extend literature search beyond PubMed/arXiv by integrating with the researcher's personal reference manager (Zotero or Mendeley). The agent reads the user's existing library, incorporates their highlights and notes, and outputs a formatted bibliography that syncs back to their reference manager.

## Protocol

### Step 1: Detect Reference Manager

Check for available integrations:
1. **Zotero**: Check for `ZOTERO_USER_ID` and `ZOTERO_API_KEY` environment variables
2. **Zotero local**: Check for Zotero SQLite database at `~/.zotero/zotero/*/zotero.sqlite`
3. **Mendeley**: Check for `MENDELEY_CLIENT_ID` and `MENDELEY_CLIENT_SECRET`
4. **BibTeX file**: Check for `.bib` files in `inputs/papers/`

### Step 2: Zotero API Integration

If Zotero credentials are available:

```python
import requests
from pyzotero import zotero

# Connect to Zotero library
zot = zotero.Zotero(library_id, 'user', api_key)

# Get items from a specific collection (if specified)
items = zot.collection_items(collection_key)

# Or search by tags
items = zot.items(tags='research-copilot')

# Extract metadata
for item in items:
    data = {
        'title': item['data'].get('title', ''),
        'authors': item['data'].get('creators', []),
        'year': item['data'].get('date', '')[:4],
        'doi': item['data'].get('DOI', ''),
        'abstract': item['data'].get('abstractNote', ''),
        'tags': [t['tag'] for t in item['data'].get('tags', [])],
        'notes': [],
        'highlights': [],
    }
    
    # Get notes (user's annotations)
    notes = zot.item_notes(item['key'])
    for note in notes:
        data['notes'].append(note['data'].get('note', ''))
    
    # Get attachments (for PDF extraction if needed)
    attachments = zot.item_children(item['key'])
```

### Step 3: Semantic Scholar API Enhancement

Supplement Zotero items with Semantic Scholar data:

```python
import requests

def enrich_with_semantic_scholar(doi):
    \"\"\"Get citation count, influential citations, and tldr from Semantic Scholar.\"\"\"
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}"
    params = {
        "fields": "title,authors,year,citationCount,influentialCitationCount,tldr,abstract,fieldsOfStudy",
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

# For each paper, enrich with:
# - Citation count (impact measure)
# - Influential citation count (quality measure)
# - TLDR (quick summary)
# - Fields of study (relevance check)
```

### Step 4: Process User Highlights and Notes

Extract key insights from user's annotations:

```python
from bs4 import BeautifulSoup

def extract_highlights(note_html):
    \"\"\"Extract highlighted text and user comments from Zotero notes.\"\"\"
    soup = BeautifulSoup(note_html, 'html.parser')
    
    highlights = []
    for blockquote in soup.find_all('blockquote'):
        highlight = {
            'text': blockquote.get_text().strip(),
            'comment': '',
        }
        # Get user's comment after the highlight
        next_elem = blockquote.find_next_sibling()
        if next_elem and next_elem.name == 'p':
            highlight['comment'] = next_elem.get_text().strip()
        highlights.append(highlight)
    
    return highlights
```

### Step 5: Build Enhanced Evidence Matrix

Combine Zotero library with search results:

```markdown
| Paper | DOI | Citations | User Rating | Key Finding | Relevance |
|-------|-----|-----------|-------------|-------------|-----------|
| [Title] | doi | N | ⭐⭐⭐⭐ | [From user notes] | High |
```

User ratings derived from:
- Number of highlights (more highlights = more important)
- Presence of user comments (engaged with = important)
- Collection membership (in research collection = relevant)

### Step 6: Generate Enhanced Bibliography

Create `reports/literature/bibliography.bib` with enriched entries:

```bibtex
@article{key,
  title = {Title},
  author = {Author1 and Author2},
  journal = {Journal},
  year = {2024},
  doi = {10.xxxx/xxxxx},
  citation_count = {42},
  influential_citations = {5},
  fields_of_study = {Economics, Econometrics},
  user_highlights = {3},
  user_notes = {Yes},
  relevance_score = {0.85},
  abstract = {Abstract text},
  tldr = {AI-generated summary},
}
```

### Step 7: Sync Back to Zotero (Optional)

If the user wants the bibliography synced back:

```python
def sync_to_zotero(bibliography, collection_name="Research Copilot"):
    \"\"\"Create a new Zotero collection with the bibliography.\"\"\"
    # Create collection
    collection = zot.create_collections([{'name': collection_name}])
    collection_key = collection[0]['key']
    
    # Add items
    for entry in bibliography:
        item = {
            'itemType': 'journalArticle',
            'title': entry['title'],
            'creators': entry['authors'],
            'DOI': entry['doi'],
            'date': entry['year'],
            'abstractNote': entry['abstract'],
            'tags': [{'tag': 'research-copilot'}, {'tag': entry['relevance']}],
        }
        zot.create_items([item])
```

## Quality Rules

1. NEVER modify the user's Zotero library without explicit permission
2. ALWAYS preserve the original Zotero data — create new collections, don't modify existing
3. ALWAYS respect API rate limits (Zotero: 100 req/min, Semantic Scholar: 100 req/5min)
4. ALWAYS cache API responses to avoid redundant calls
5. ALWAYS handle missing DOIs gracefully (search by title instead)
6. ALWAYS include user's own notes and highlights in the evidence matrix
7. NEVER share API keys or library data
""",
    "synthesize_literature": """---
skill_id: "synthesize_literature"
version: "7.0.0"
category: "literature"
domain_compatibility: ["all"]
required_tools: ["python", "openai|anthropic|litellm"]
depends_on: ["extract_claims"]
produces: ["literature/literature_synthesis.md", "literature/gap_analysis.md"]
complexity: "advanced"
---

# Skill: Literature Synthesis & Gap Analysis

## Purpose
Synthesize the evidence matrix into a narrative review identifying consensus, contradictions, and research gaps.

## When to Use
- After claim extraction from all papers
- Before writing introduction or discussion sections
- Need to position research within existing literature

## When NOT to Use
- Evidence matrix not yet built
- Only annotated bibliography needed

## Execution Protocol

### Step 1: Thematic Clustering
- Group papers by: methodology, theoretical framework, or dependent variable
- Identify dominant themes (topics addressed by ≥ 3 papers)
- Identify niche themes (addressed by 1-2 papers)

### Step 2: Consensus Assessment
- For each claim/hypothesis: count supporting, contradicting, and neutral papers
- Compute directional agreement: percentage of papers supporting the claim
- Classify: strong consensus (> 80% agree), moderate (60-80%), contested (40-60%), no consensus (< 40%)

### Step 3: Contradiction Analysis
- For contested claims: identify sources of disagreement
  - Methodological differences (design, sample, measures)
  - Contextual differences (population, setting, time period)
  - Analytical differences (statistical method, covariate adjustment)
- Determine if contradictions are resolvable or fundamental

### Step 4: Gap Identification
- **Evidence gaps**: claims with no empirical testing
- **Methodological gaps**: claims tested only with weak designs
- **Population gaps**: claims tested only in specific populations
- **Temporal gaps**: claims not tested recently (> 5 years)
- **Integration gaps**: claims tested in isolation, not in combination

### Step 5: Synthesis Narrative
- Structure: introduction → themes → consensus → contradictions → gaps → implications
- Cite papers using Author-Year format with DOI
- For each theme: summarize findings, note quality of evidence, identify gaps
- Conclude with: how the current research addresses identified gaps

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| Themes identified | ≥ 2 themes | Literature too narrow or diverse |
| Consensus classified | All claims classified | Insufficient papers per claim |
| Gaps identified | ≥ 1 gap | Literature is complete; rare |
| Citations complete | All claims cited | Missing references |

## Output Specification
- `literature/literature_synthesis.md`: narrative synthesis with citations
- `literature/gap_analysis.md`: structured gap analysis with priority ranking

## Validation Checks
- [ ] All claims from evidence matrix addressed
- [ ] Consensus percentages computed
- [ ] At least one research gap identified
- [ ] All citations have DOI or Author-Year format
""",
    "viz_d3_templates": """# Skill: D3.js Figure Templates & Jinja2 Injection

## Purpose
Some visualizations (such as Sankey/alluvial flow, chord diagrams, and animated timelines) cannot be produced cleanly or with professional quality in Python. This skill describes how to inject Python data structures into standalone D3.js HTML/JS templates using the Jinja2 template engine.

## Installation
Ensure Jinja2 is installed:
```bash
pip install jinja2
```

## Protocol & Best Practices
1. **Separation of Concerns:** Keep D3.js boilerplate and CSS rendering separate in an HTML template file.
2. **Inject Clean JSON:** Use the `to_json()` method or `json.dumps()` in Python to format data into JSON string literals, then output with raw Jinja escaping (`{{ data | safe }}`) inside a `<script>` tag.
3. **Handle Local Resources:** Embed D3.js libraries directly (via CDN or local file links if offline compatibility is required).

## Code Template

### HTML Template (`sankey_template.html`)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sankey Diagram</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://unpkg.com/d3-sankey@0.12.3/dist/d3-sankey.min.js"></script>
    <style>
        .node rect { fill-opacity: 0.9; shape-rendering: crispEdges; }
        .node text { pointer-events: none; text-shadow: 0 1px 0 #fff; font-family: sans-serif; font-size: 10px; }
        .link { fill: none; stroke: #000; stroke-opacity: 0.2; }
        .link:hover { stroke-opacity: 0.5; }
    </style>
</head>
<body>
    <div id="chart"></div>
    <script>
        // Inject Python data structure directly
        const graph = {{ data_json | safe }};
        const width = 800;
        const height = 500;

        const svg = d3.select("#chart").append("svg")
            .attr("width", width)
            .attr("height", height);

        const sankey = d3.sankey()
            .nodeWidth(15)
            .nodePadding(10)
            .extent([[1, 1], [width - 1, height - 6]]);

        const {nodes, links} = sankey(graph);

        // Nodes & Links rendering logic
        svg.append("g")
            .selectAll("rect")
            .data(nodes)
            .join("rect")
            .attr("x", d => d.x0)
            .attr("y", d => d.y0)
            .attr("height", d => d.y1 - d.y0)
            .attr("width", d => d.x1 - d.x0)
            .attr("fill", "steelblue");

        svg.append("g")
            .attr("fill", "none")
            .selectAll("g")
            .data(links)
            .join("path")
            .attr("d", d3.sankeyLinkHorizontal())
            .attr("stroke", "#888")
            .attr("stroke-width", d => Math.max(1, d.width));
    </script>
</body>
</html>
```

### Python Injection Code
```python
import json
from jinja2 import Template

def generate_sankey_diagram(nodes: list, links: list, template_path: str, output_path: str):
    data = {"nodes": nodes, "links": links}
    
    with open(template_path, "r") as f:
        template_str = f.read()
        
    template = Template(template_str)
    rendered_html = template.render(data_json=json.dumps(data))
    
    with open(output_path, "w") as f:
        f.write(rendered_html)
        
    print(f"Successfully generated D3 Sankey: {output_path}")
```
""",
    "figure_inferential": """---
skill_id: "figure_inferential"
version: "8.0.0"
category: "visualization"
domain_compatibility: ["all"]
required_tools: ["python", "matplotlib", "seaborn", "plotly", "statsmodels"]
depends_on: ["viz_design_system", "viz_code_standards", "inferential_parametric", "inferential_nonparametric"]
produces: ["reports/figures/inferential/"]
complexity: "intermediate"
---

# Skill: Inferential Statistics Figures

## Purpose
Publication-quality figures for inferential test results: effect sizes, CIs, model diagnostics, p-value functions.

---

## Effect Size Figures

### Forest Plot
Point estimates with CI error bars, null reference line (dashed), sorted by effect size or p-value. Color: significant (blue), non-significant (gray). Optional diamond for pooled estimate.

### Dot-and-Whisker Plot
Coefficients sorted by absolute magnitude. Dot = point estimate, whisker = CI. Grouped by model if multiple models. Null reference line.

### Caterpillar Plot
Ranked effect sizes (largest first) with CI bars. Color by significance. Best for many estimates (meta-analysis, multilevel).

---

## Model Diagnostic Plots

### Four-Panel Diagnostic
(1) Residuals vs Fitted — check homoscedasticity, LOWESS smooth. (2) Q-Q Plot — check normality, reference line. (3) Scale-Location — sqrt(|std residuals|) vs fitted, LOWESS smooth. (4) Residuals vs Leverage — Cook's D contours (0.5, 1.0), label high-leverage points.

### Six-Panel Regression Diagnostics Grid (Publication Standard)
Extends four-panel with two partial regression plots. Panels 1-4 same as above. Panel 5: partial regression for top predictor by |t-statistic| — shows relationship after controlling for all other variables, OLS line with 95% CI. Panel 6: same for second-top predictor. Use `statsmodels.graphics.regressionplots.plot_partreg2`. Label observations exceeding Cook's D threshold (4/n). Use for final manuscript; four-panel is sufficient for exploratory checks.

---

## Group Comparison Figures

### Mean Comparison Plot
Group means with 95% CI error bars. Optional raw data points (jittered). Sorted by mean descending. Significance brackets between groups.

### Raincloud Plot (Inferential)
Half-violin + box + raw data. Statistical test result annotation. Effect size with CI. Significance marker.

---

## P-value Visualization

### P-value Function Plot (Confidence Curve)
X-axis: effect size values. Y-axis: p-value for each hypothesized value. Horizontal line at alpha threshold. Shaded region = CI. Shows full p-value curve, not just threshold.

### Volcano Plot
X-axis: effect size. Y-axis: -log10(p-value). Color: significant vs non-significant. Label top significant results. Threshold lines for p-value and effect size.

---

## Statistical Annotation

Significance markers: ns (p>.05), * (p≤.05), ** (p≤.01), *** (p≤.001), **** (p≤.0001). Always show estimate + 95% CI. Format: `β = 0.42 [0.18, 0.66]`. Never show p-value alone. Report exact p-values.

Significance brackets: horizontal line connecting groups with *, **, ***, or ns label. Proper vertical offset.

---

## Output Standards

### File Naming
`fig_inf_001_forest_[question].png`, `fig_inf_002_diagnostics_[model].png`, `fig_inf_003_volcano_[analysis].png`

### Format
Primary: PNG at 300 DPI. Editable: SVG for line art. Size: single column (3.35") or double column (6.89").

---

## Validation
- [ ] Effect sizes match computed values exactly
- [ ] CIs correctly plotted
- [ ] Null line clearly marked
- [ ] Diagnostic plots include reference lines
- [ ] Significance markers follow standard
- [ ] P-values reported exactly
- [ ] Design system theme applied
- [ ] Colorblind-safe palettes
- [ ] All axes labeled with units
""",
    "captions_and_legends": """---
skill_id: "captions_and_legends"
version: "1.0.0"
category: "visualization"
depends_on: ["execute_analysis", "viz_design_system"]
produces: ["03_synthesis/figure_captions.json"]
complexity: "quick"
---

# Skill: Captions and Legends

## Purpose
Generate publication-quality figure captions grounded in analysis results. Used by `paper_compiler` and `research_website`.

---

## Protocol

### Step 1: Gather Data
For each figure: read `.meta.yaml` (source info), `.interpret.md` (statistical interpretation), analysis results JSON (effect sizes, CIs, p-values).

### Step 2: Generate Caption
Format: **Figure N.** _Title._ Description. Statistical annotation (test, effect size, 95% CI, N, significance). Notes on color/symbols.

Components:
- **Figure N.**: sequential number
- _Title._: concise relationship description (from `.meta.yaml` or auto-generated)
- Description: what the figure shows visually (from `.interpret.md`)
- Statistical annotation: test name, effect size, 95% CI, p-value, N
- Notes: color coding, symbols, significance markers

### Step 3: Save Captions
Output `03_synthesis/figure_captions.json` keyed by figure filename. Each entry: `figure_number`, `title`, `caption_markdown`, `caption_latex`, `caption_plain`, `statistical_annotation` (test, effect_size, ci_lower, ci_upper, p_value, n), `source_files`.

### Step 4: Format Variants
- **Markdown**: `**Figure 1.** _Title._ Description. Annotation. Notes.`
- **LaTeX**: `\\textbf{Figure 1.} \\textit{Title.} Description. Annotation. Notes.`
- **Plain**: `Figure 1. Title. Description. Annotation. Notes.`

### Step 5: Significance Legend
Standard: `*p < .05, **p < .01, ***p < .001`. Include in captions, table footnotes, dashboard tooltips.

---

## Validation
- [ ] Every figure has a caption
- [ ] Each caption includes effect size + CI + p-value + N
- [ ] Captions grounded in analysis results (no hallucination)
- [ ] Sequential figure numbers
- [ ] Three format variants generated
- [ ] Source files traced for every claim
""",
    "viz_pygwalker": """# Skill: Zero-Code Exploratory Analysis with PyGWalker

## Purpose
PyGWalker (Python binding of Graphic Walker) embeds a Tableau-like drag-and-drop explorer interface directly into your Jupyter notebook or exported HTML. It allows researchers to perform high-fidelity exploratory data analysis (EDA) without writing code.

## Installation
```bash
pip install pygwalker
```

## Protocol & Best Practices
1. **Prepare Data First:** Clean datasets, set proper data types, and rename columns to human-readable names prior to initializing PyGWalker.
2. **Export Spec Files:** To save your visualization setup across sessions, always specify a config path using the `spec` parameter so it writes your visual settings to a JSON file.
3. **Use HTML Export for Dashboards:** Generate a standalone HTML report containing the interactive explorer layout for non-technical stakeholders.

## Code Template

```python
import pygwalker as pyg
import pandas as pd
from pathlib import Path

def launch_explorer(df: pd.DataFrame, spec_name: str = "dw_spec.json"):
    \"\"\"
    Launch interactive Graphic Walker explorer.
    Writes/reads visual specifications to/from a spec JSON file.
    \"\"\"
    spec_path = Path(".research/cache") / spec_name
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    
    walker = pyg.walk(
        df,
        spec=str(spec_path),
        use_kernel_calc=True,
        show_cloud_tool=False
    )
    return walker

def export_explorer_html(df: pd.DataFrame, output_path: str):
    \"\"\"
    Exports a standalone HTML page with the full drag-and-drop explorer app.
    \"\"\"
    pyg.to_html(df, output_path)
    print(f"Explorer exported to standalone HTML: {output_path}")
```
""",
    "auto_figure_selector": """---
skill_id: "auto_figure_selector"
version: "1.0.0"
category: "visualization"
depends_on: ["viz_design_system", "profile_tabular"]
produces: ["02_experiments/<exp>/outputs/figures/auto_selected_figure.png"]
complexity: "quick"
---

# Skill: Auto Figure Selector

## Purpose
Takes variable types, N, and question type → returns optimal figure type with rationale.

---

## Protocol

### Step 1: Input Analysis
Gather from data profile: variable types (continuous, categorical, binary, ordinal, time), sample size N, research question type, number of variables.

### Step 2: Decision Table

| X | Y | N | Question | Figure |
|---|---|---|----------|--------|
| continuous | continuous | any | association | Scatter + regression + CI band |
| continuous | continuous | >5000 | association | Hexbin / 2D density |
| categorical (2 levels) | continuous | any | comparison | Raincloud plot |
| categorical (2 levels) | continuous | <200 | comparison | Strip + boxplot overlay |
| categorical (3+ levels) | continuous | >200 | comparison | Violin plot |
| categorical (3+ levels) | continuous | <200 | comparison | Strip + boxplot overlay |
| time | continuous | any | trend | Line + confidence ribbon |
| categorical | categorical | any | association | Mosaic plot / grouped bar |
| multiple (regression) | continuous | any | prediction | Coefficient forest plot |
| continuous (5+ vars) | continuous (5+ vars) | any | correlation | Clustered heatmap |
| continuous | binary | any | classification | ROC curve |
| time | event | any | survival | Kaplan-Meier curve |
| any | any | <30 | exploratory | Raw data + summary |

### Step 3: Generate Figure
Write the appropriate plotting function using design system theme. Use `get_figsize()` for dimensions. Apply Okabe-Ito palette. Label axes with variable names.

### Step 4: Output
Return: figure type, rationale, figure size preset, estimated runtime. Save figure to experiment outputs. Generate `.interpret.md` alongside.

---

## Validation
- [ ] Figure type matches decision table
- [ ] Design system theme applied
- [ ] Colorblind-safe palette
- [ ] Axes labeled
- [ ] `.interpret.md` generated
""",
    "viz_wordcloud": """# Skill: Word Clouds for NLP & Text Corpora

## Purpose
Word clouds provide a quick visual representation of text data, where the size of each word indicates its frequency or statistical importance (e.g. TF-IDF weight).

## Installation
```bash
pip install wordcloud
```

## Protocol & Best Practices
1. **Pre-Process Text:** Remove stop words, punctuation, perform lemmatization or stemming, and lowercase all terms prior to rendering.
2. **Constrain Shape & Color:** Use a mask image (e.g. circle or rectangle) to keep word boundaries clean. Apply a custom color function to bind word colors to the Okabe-Ito palette instead of using random default colors.
3. **Use Frequency Maps:** Pass predefined keyword-frequency dictionaries (e.g. `generate_from_frequencies`) rather than feeding raw text directly to the renderer for fine-grained control.

## Code Template

```python
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import random

def color_func_okabe_ito(word, font_size, position, orientation, random_state=None, **kwargs):
    # Okabe-Ito colors excluding black/yellow for better contrast
    colors = ["#E69F00", "#56B4E9", "#009E73", "#0072B2", "#D55E00", "#CC79A7"]
    return random.choice(colors)

def generate_wordcloud(frequencies: dict, output_path: str):
    wordcloud = WordCloud(
        background_color="white",
        width=800,
        height=400,
        max_words=100,
        color_func=color_func_okabe_ito,
        prefer_horizontal=0.7
    ).generate_from_frequencies(frequencies)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(output_path, dpi=300)
    plt.close()
```
""",
    "dashboard_executive": """---
skill_id: "dashboard_executive"
version: "8.0.0"
category: "visualization"
domain_compatibility: ["all"]
required_tools: ["python", "dash", "plotly", "dash-bootstrap-components"]
depends_on: ["viz_design_system", "viz_code_standards", "dashboard_overview"]
produces:
  - "reports/dashboards/executive_dashboard.py"
  - "reports/dashboards/executive_summary.pdf"
complexity: "advanced"
---

# Skill: Executive Summary Dashboard

## Purpose
Generate a high-level dashboard for non-technical stakeholders: key findings, implications, and actionable insights WITHOUT statistical jargon. Plain language. Clear visuals. Actionable takeaways.

## When to Use
- Results need to be communicated to non-researchers
- Policy or business decision support
- Quick overview before deep dive
- Grant reports, stakeholder updates

## When NOT Use
- Only technical audience
- Results not yet finalized
- Findings are preliminary or inconclusive

---

## Design Philosophy

1. **No statistical jargon** — No p-values, CIs, test statistics in labels
2. **Plain language** — Write for a 10th-grade reading level
3. **Action-oriented** — Every finding leads to a recommendation
4. **Visual first** — Numbers support visuals, not the reverse
5. **Honest about uncertainty** — Caveats visible, not hidden

---

## Layout

```
┌─────────────────────────────────────────────────┐
│  [Project Title]                                 │
│  Executive Summary — [Date]                      │
│  "One-sentence summary of the main finding"      │
├─────────────────────────────────────────────────┤
│  KEY FINDINGS                                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │ Finding  │ │ Finding  │ │ Finding  │        │
│  │ 1        │ │ 2        │ │ 3        │        │
│  │ [Big #]  │ │ [Big #]  │ │ [Big #]  │        │
│  │ ↑ or ↓   │ │ ↑ or ↓   │ │ →        │        │
│  └──────────┘ └──────────┘ └──────────┘        │
├─────────────────────────────────────────────────┤
│  WHAT THIS MEANS                                 │
│  ┌───────────────────────────────────────────┐  │
│  │  Visual: Simplified comparison/trend      │  │
│  │  (bar chart, line, or icon-based)         │  │
│  └───────────────────────────────────────────┘  │
│                                                  │
│  Plain language explanation of the main result   │
│  (2-3 sentences, no statistics)                  │
├─────────────────────────────────────────────────┤
│  RECOMMENDATIONS                                 │
│  ┌───────────────────────────────────────────┐  │
│  │ 🔴 HIGH: [Action] — [Why]                 │  │
│  │ 🟡 MEDIUM: [Action] — [Why]               │  │
│  │ 🟢 LOW: [Action] — [Why]                  │  │
│  └───────────────────────────────────────────┘  │
├─────────────────────────────────────────────────┤
│  CAVEATS & LIMITATIONS                           │
│  • [Limitation 1 — plain language]              │
│  • [Limitation 2 — plain language]              │
│  • [What we don't know yet]                     │
├─────────────────────────────────────────────────┤
│  EVIDENCE STRENGTH                               │
│  Finding 1: ████████░░ Strong (80%)             │
│  Finding 2: ██████░░░░ Moderate (60%)           │
│  Finding 3: ████░░░░░░ Preliminary (40%)        │
└─────────────────────────────────────────────────┘
```

---

## Component Specifications

### Finding Card
```python
def create_finding_card(
    finding_number,
    statement,        # Plain language: "Treatment improved outcomes"
    key_number,       # "12%" or "3.2 points"
    direction,        # "up", "down", "no_change"
    evidence_strength, # "strong", "moderate", "preliminary"
    context,          # "Compared to control group"
):
    \"\"\"Create a finding card for non-technical audience.\"\"\"
```

### Recommendation Row
```python
def create_recommendation(
    action,           # What to do
    rationale,        # Why (linked to finding)
    priority,         # "high", "medium", "low"
    evidence,         # "strong", "moderate", "preliminary"
):
    \"\"\"Create a recommendation with priority badge.\"\"\"
```

### Evidence Bar
```python
def create_evidence_bar(label, strength_pct, strength_label):
    \"\"\"Create a visual evidence strength indicator.\"\"\"
```

---

## Visual Standards

### Colors for Executive Dashboard
- **Positive finding**: `#009E73` (green) with ↑ arrow
- **Negative finding**: `#D55E00` (vermillion) with ↓ arrow
- **No change**: `#999999` (gray) with → arrow
- **High priority**: `#D55E00` (vermillion)
- **Medium priority**: `#E69F00` (orange)
- **Low priority**: `#009E73` (green)

### Chart Types (Executive-Friendly)
- **Comparison**: Horizontal bar chart (sorted by value)
- **Trend**: Line chart with clear direction
- **Proportion**: Stacked bar (not pie chart)
- **Distribution**: Simplified histogram with mean line

### Chart Rules
- NO error bars (explain uncertainty in text instead)
- NO statistical annotations
- NO axis truncation for bar charts
- ALWAYS include clear title explaining what the chart shows
- ALWAYS use plain language labels (not variable names)

---

## Plain Language Translation

| Statistical Term | Executive Translation |
|-----------------|----------------------|
| "p < 0.05" | "This finding is statistically reliable" |
| "p > 0.05" | "We cannot confidently say there is a difference" |
| "95% CI [0.2, 0.8]" | "The true effect is likely between 0.2 and 0.8" |
| "R² = 0.45" | "This explains about 45% of the variation" |
| "β = 0.32" | "For each unit increase, the outcome increases by 0.32" |
| "OR = 2.1" | "The odds are about 2 times higher" |
| "Not significant" | "The data does not show a clear effect" |
| "Effect size d = 0.5" | "A moderate difference between groups" |

---

## Evidence Strength Classification

| Strength | Criteria | Visual |
|----------|---------|--------|
| **Strong** | p < 0.01, large effect, robust to sensitivity | ████████░░ (80%) |
| **Moderate** | p < 0.05, medium effect, some sensitivity | ██████░░░░ (60%) |
| **Preliminary** | p < 0.10, small effect, sensitive to specs | ████░░░░░░ (40%) |
| **Inconclusive** | p > 0.10 or conflicting results | ██░░░░░░░░ (20%) |

---

## Export Formats

### PDF Summary
- One-page layout
- Print-ready (300 DPI)
- Includes: findings, recommendations, caveats
- Generated via WeasyPrint or ReportLab

### Presentation Slides
- 3-5 slides maximum
- One finding per slide
- Visual-first, text-minimal
- Export-ready for PowerPoint/Google Slides

---

## Implementation Steps

1. **Extract findings** — From analysis results, identify 3-5 key findings
2. **Translate to plain language** — Remove all statistical jargon
3. **Classify evidence strength** — Based on p-values, effect sizes, robustness
4. **Generate recommendations** — Link each finding to an action
5. **Build dashboard** — Using component architecture from overview dashboard
6. **Create PDF** — One-page executive summary
7. **Validate** — No statistical terms in labels, all findings supported by data

---

## Output Specification
- `reports/dashboards/executive_dashboard.py`: Runnable Dash app
- `reports/dashboards/executive_summary.pdf`: One-page PDF summary

## Validation Checks
- [ ] Zero statistical jargon in visible labels
- [ ] All findings supported by analysis results
- [ ] Evidence strength correctly classified
- [ ] Caveats and limitations prominently displayed
- [ ] Recommendations are actionable and specific
- [ ] Plain language translation accurate
- [ ] PDF renders correctly at print resolution
- [ ] Color choices follow design system
- [ ] Charts are executive-appropriate (no error bars, no annotations)
- [ ] Runs on port 8050 without errors
""",
    "prisma_flow_diagram": """---
skill_id: "prisma_flow_diagram"
version: "1.0.0"
category: "visualization"
domain_compatibility: ["all"]
required_tools: ["python", "matplotlib", "graphviz"]
depends_on: ["viz_design_system", "viz_code_standards"]
produces: ["reports/figures/prisma_diagram.png", "reports/figures/prisma_diagram.svg"]
complexity: "intermediate"
---

# Skill: PRISMA Flow Diagram

## Purpose
Generate a PRISMA 2020-compliant flow diagram showing the study selection process from identification through inclusion. Required for systematic reviews and meta-analyses.

## When to Use
- After literature pipeline completes
- For systematic review manuscripts
- When reporting study selection process

## When NOT to Use
- Not a systematic review
- Literature search not yet complete

---

## PRISMA 2020 Flow Structure

```
┌─────────────────────────────────┐
│         IDENTIFICATION          │
│                                 │
│ Records identified from:        │
│   Databases (n = XXX)           │
│   Registers (n = XXX)           │
│                                 │
│ Total records: n = XXX          │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│         SCREENING               │
│                                 │
│ Records screened: n = XXX       │
│ Records excluded: n = XXX       │
│   (reasons listed)              │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│        SOUGHT FOR RETRIEVAL     │
│                                 │
│ Reports sought for retrieval:   │
│   n = XXX                       │
│ Reports not retrieved: n = XXX  │
│   (reasons)                     │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│         ASSESSED                │
│                                 │
│ Reports assessed for            │
│   eligibility: n = XXX          │
│ Reports excluded: n = XXX       │
│   Reason 1 (n = XX)             │
│   Reason 2 (n = XX)             │
│   Reason 3 (n = XX)             │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│         INCLUDED                │
│                                 │
│ Studies included in review:     │
│   n = XXX                       │
│ Studies included in meta-       │
│   analysis: n = XXX             │
└─────────────────────────────────┘
```

---

## Implementation

### Data Input
Read from `reports/literature/prisma_flow.json`:
```json
{
  "identification": {
    "databases": 234,
    "registers": 45,
    "other_sources": 23,
    "total": 302
  },
  "deduplication": {
    "duplicates_removed": 81,
    "after_dedup": 221
  },
  "screening": {
    "screened": 221,
    "excluded": 145,
    "exclusion_reasons": {
      "not relevant topic": 78,
      "wrong study design": 34,
      "wrong population": 23,
      "not peer reviewed": 10
    }
  },
  "retrieval": {
    "sought": 76,
    "not_retrieved": 4,
    "not_retrieved_reasons": {
      "full text unavailable": 3,
      "language barrier": 1
    }
  },
  "assessment": {
    "assessed": 72,
    "excluded": 26,
    "exclusion_reasons": {
      "insufficient data": 12,
      "wrong outcome measure": 8,
      "duplicate publication": 4,
      "methodological flaws": 2
    }
  },
  "inclusion": {
    "included_in_review": 46,
    "included_in_meta_analysis": 28
  }
}
```

### Figure Generation
```python
def create_prisma_flow(prisma_data, output_path, format="png"):
    \"\"\"Create PRISMA 2020 flow diagram.
    
    Features:
    - 5-phase layout (Identification → Screening → Retrieval → Assessment → Included)
    - Numbers at each stage
    - Exclusion reasons listed
    - Clean, publication-ready styling
    - Design system colors and fonts
    \"\"\"
```

---

## Styling

- **Box style**: Rounded rectangle, white fill, dark border
- **Arrow style**: Solid, dark gray, 1.5pt
- **Font**: Inter/sans-serif, 10pt body, 12pt section headers
- **Colors**: 
  - Box background: `#FFFFFF`
  - Box border: `#333333`
  - Section header: `#0072B2` (blue)
  - Numbers: bold
  - Exclusion reasons: `#666666` (gray)
- **Size**: Double column (17.5cm wide)
- **DPI**: 300 for print

---

## Validation Checks
- [ ] Numbers are internally consistent
- [ ] All PRISMA 2020 phases present
- [ ] Exclusion reasons sum to total excluded
- [ ] Design system theme applied
- [ ] Font sizes meet publication standard
- [ ] Output in both PNG and SVG formats
""",
    "figure_gallery": """---
skill_id: "figure_gallery"
version: "1.0.0"
category: "visualization"
depends_on: ["viz_design_system", "figure_descriptive", "figure_inferential"]
produces: ["03_synthesis/figure_gallery.html"]
complexity: "quick"
---

# Skill: Figure Gallery Generator

## Purpose
Static HTML gallery where each figure panel shows the image, `.interpret.md` content, statistical annotation, and download link. Clean grid with lightbox. Pure HTML/CSS/vanilla JS.

---

## Protocol

### Step 1: Scan for Figures
Find all `.png` files in `outputs/figures/` that have sibling `.interpret.md` files. Also check for `.meta.yaml` sidecars.

### Step 2: Parse Interpretation Files
Extract sections from each `.interpret.md`: Visual Description, Statistical Interpretation (test, effect size, CI, p-value, N), Key Takeaway, Caveats.

### Step 3: Generate HTML
Single `index.html` with: header (project title, date), CSS grid gallery (`grid-template-columns: repeat(auto-fill, minmax(500px, 1fr))`), lightbox overlay.

**CSS**: responsive grid, card styling with shadow, figure images at 100% width with hover opacity transition, stat annotation box with left accent border, caveats section with muted text. Lightbox: fixed overlay, 90% max image size, close on click outside or Escape key. Mobile: single column at 768px.

**JS**: lightbox open on image click (set `src` and `alt`), close on overlay click or X button or Escape key.

### Step 4: Generate Figure Cards
Each card: image (clickable for lightbox), figure number + title from `.meta.yaml`, stat annotation box (test, effect size, CI, p-value, N), key takeaway paragraph, caveats paragraph, download link to PNG.

### Step 5: Copy Figures
Copy all figures to `03_synthesis/figure_gallery_files/figures/`. Reference by relative path in HTML.

---

## Output
- `03_synthesis/figure_gallery.html` — static HTML gallery
- `03_synthesis/figure_gallery_files/figures/` — copied figures

## Validation
- [ ] All figures with `.interpret.md` included
- [ ] Lightbox opens on click, closes on Escape/X/overlay
- [ ] Download links work
- [ ] Responsive grid (single column mobile)
- [ ] Statistical annotations on every figure
- [ ] No external JS dependencies
""",
    "research_website": """---
skill_id: "research_website"
version: "1.0.0"
category: "visualization"
depends_on: ["paper_compiler", "results_table_generator", "figure_descriptive", "figure_inferential"]
produces: ["03_synthesis/website/index.html"]
complexity: "standard"
---

# Skill: Research Website Generator

## Purpose
Generate a self-contained research website as a single `index.html` with embedded CSS/JS. No server needed — shareable via file link or static hosting.

---

## Protocol

### Step 1: Gather Inputs
Collect: `research_findings.md`, `key_findings.json`, all figures + `.interpret.md` files, analysis results JSONs, `global_methods.md`, `bibliography.bib`.

### Step 2: Build HTML Structure
Single `index.html` with sections: nav (sticky), abstract, methods (collapsible), results, interactive data explorer (Plotly CDN), data download, footer. Use Plotly CDN (`plotly-2.27.0.min.js`) for interactive figures.

### Step 3: Embedded CSS
Use CSS custom properties for theming (`--color-primary: #0072B2`, etc). Responsive nav, max-width 960px content, card styling with subtle shadows, figure panels with centered images, results tables with clean borders, collapsible sections with max-height transition. Mobile: nav wraps at 768px.

### Step 4: Section Content
- **Abstract**: Title, authors, structured abstract, key findings bullets
- **Methods** (collapsible, default closed): study design, sample, measures, analysis methods, assumption checks
- **Results**: per research question — question text, primary finding with effect size + CI, figures with `.interpret.md` content, results table
- **Data Explorer**: embed Plotly figures via `data-plotly` attributes. JS reads JSON and calls `Plotly.newPlot()`. Include: distributions, correlation heatmap, forest plot. Interactive: zoom, pan, hover.
- **Data Download**: links to raw data, processed data (CSV/Parquet), analysis scripts, manuscript PDF

### Step 5: Embedded JS
Collapsible sections (toggle `open` class on click). Smooth scroll for nav links. Plotly rendering: query `[data-plotly]`, parse JSON, call `Plotly.newPlot(el, data.data, data.layout, {responsive: true})`. Remove lasso/select tools via `modeBarButtonsToRemove`.

### Step 6: Figure Embedding
Option A: base64 encode PNG inline (`data:image/png;base64,...`). Option B (for large figures): copy to `03_synthesis/website/figures/` and reference by relative path. Each figure panel: image, caption from `.interpret.md`, download link.

---

## Output
- `03_synthesis/website/index.html` — self-contained website
- `03_synthesis/website/figures/` — copied figures (if not base64)
- `03_synthesis/website/data/` — downloadable data (optional)

## Validation
- [ ] Single HTML, no external deps except Plotly CDN
- [ ] All sections render
- [ ] Collapsible methods works
- [ ] Plotly figures interactive
- [ ] Download links functional
- [ ] Responsive at 375px
- [ ] All figures have alt text
- [ ] No broken links
""",
    "figure_causal_dag": """---
skill_id: "figure_causal_dag"
version: "8.0.0"
category: "visualization"
domain_compatibility: ["all"]
required_tools: ["python", "networkx", "matplotlib", "graphviz"]
depends_on: ["viz_design_system", "viz_code_standards", "causal_inference"]
produces: ["reports/figures/causal_dag.png", "reports/figures/causal_dag.svg"]
complexity: "intermediate"
---

# Skill: Causal DAG Visualization

## Purpose
Render causal directed acyclic graphs showing hypothesized relationships between treatment, outcome, confounders, mediators, and colliders.

## When to Use
- After causal model specified
- For methods section figure
- Communicating identification strategy

---

## Node Types & Styling

| Node Type | Shape | Color | Description |
|-----------|-------|-------|-------------|
| Treatment | Rectangle | `#0072B2` (blue) | Exposure/intervention |
| Outcome | Rectangle | `#009E73` (green) | Dependent variable |
| Confounder | Ellipse | `#999999` (gray) | Common cause |
| Mediator | Diamond | `#E69F00` (orange) | On causal path |
| Collider | Hexagon | `#D55E00` (vermillion) | Common effect |
| Instrument | Triangle | `#56B4E9` (sky blue) | IV variable |
| Unmeasured | Dashed border | `#CC79A7` (red) | Not observed |

## Edge Types

| Edge Type | Style | Meaning |
|-----------|-------|---------|
| Causal | Solid arrow | Direct causal effect |
| Unmeasured path | Dashed arrow | Hypothesized but unmeasured |
| Backdoor path | Red highlight | Confounding path |
| Blocked path | ⊥ symbol | Adjusted/blocked |

---

## Layout Rules

1. **Hierarchical layout**: Treatment at top, outcome at bottom
2. **Confounders**: Between treatment and outcome
3. **Mediators**: On the causal path between treatment and outcome
4. **Colliders**: Where two arrows meet
5. **Minimize edge crossings**: Use force-directed or Sugiyama layout
6. **Node spacing**: Enough room for labels

---

## Annotation

- Label each node with variable name
- Add legend for node types
- Note identification strategy (backdoor set, frontdoor, IV)
- Include minimal adjustment set
- Highlight backdoor paths in red

---

## Validation Checks
- [ ] Graph is acyclic (no cycles)
- [ ] All variables from causal model included
- [ ] Backdoor paths identified
- [ ] Minimal adjustment set specified
- [ ] Node types correctly styled
- [ ] Design system colors used
""",
    "viz_design_system": """---
skill_id: "viz_design_system"
version: "2.0.0"
category: "visualization"
domain_compatibility: ["all"]
required_tools: ["python", "matplotlib", "seaborn", "plotly"]
depends_on: []
produces: ["scripts/utils/viz_theme.py"]
complexity: "intermediate"
---

# Skill: Visualization Design System

## Purpose
Unified visual language for ALL figures and dashboards. No ad-hoc styling. No inconsistent colors. No non-accessible palettes.

## Principles
Accessibility first, scientific integrity, consistency, reproducibility (theme is code), publication-ready, minimalist clarity.

---

## Minimalist Design
- Data-ink ratio: every pixel must serve the data
- Remove top/right spines, keep bottom/left thin (0.8pt)
- Subtle grid lines only (alpha ≤ 0.15), horizontal only
- 5-8 ticks per axis, round to meaningful values
- Direct labeling over legends
- No 3D, shadows, gradients on bars, pie charts, rainbow/jet colormaps
- Single focal point per figure

---

## Color System

### Okabe-Ito (categorical ONLY)
`#0072B2` blue, `#E69F00` orange, `#009E73` green, `#F0E442` yellow, `#56B4E9` sky_blue, `#D55E00` vermillion, `#CC79A7` red, `#000000` black

### Sequential
Default: `viridis`. Diverging: `RdBu_r` or `coolwarm`. Single hue: `Blues`, `Greens`.

### Semantic
Positive=`#009E73`, Negative=`#D55E00`, Null=`#999999`, Significant=`#0072B2`, Non-sig=`#999999`, Warning=`#E69F00`, Error=`#D55E00`

### NEVER Use
Rainbow/jet, default matplotlib colors, pure red/green combos, >8 categorical colors.

---

## Typography
Font stack: Inter → Source Sans 3 → Helvetica Neue → Arial. Sizes: title 14pt bold, axis labels 11pt, ticks 10pt, annotations 9pt, caption 10pt italic. Never below 8pt. Sentence case for titles. Proper statistical notation (italic *p*, *N*, Greek β).

---

## Spacing & Layout
Figure margins: left 0.12, right 0.05, bottom 0.12, top 0.08, wspace 0.25, hspace 0.30. Golden ratio (1.618) for aspect ratio. Dashboards: 12-column Bootstrap grid.

---

## Figure Size Presets

| Preset | Width | Height | Use |
|--------|-------|--------|-----|
| `single_column` | 3.35" | 2.07" | Most journal figures |
| `double_column` | 6.89" | 4.26" | Full-page figures |
| `square` | 3.35" | 3.35" | Heatmaps, scatter matrices |
| `wide` | 6.89" | 3.5" | Time series, horizontal layouts |
| `poster` | 12" | 8" | Conference posters |

Use `get_figsize(preset)` to retrieve. Raises ValueError on unknown preset.

## Font Embedding
Always set `plt.rcParams['pdf.fonttype'] = 42` and `plt.rcParams['ps.fonttype'] = 42` before saving. Journals reject Type 3 fonts. For SVG, set `svg.fonttype = "none"` to convert text to paths. Verify with `pdffonts` — all fonts must show "embedded: yes".

---

## Axis & Scale Rules
- Label axes with variable name AND units
- Bar charts: y-axis must start at zero
- Line charts: y-axis can start non-zero (clearly indicated)
- Log scale MUST be labeled
- Comma separators for numbers > 999
- Rotate x-axis labels if > 10 characters

---

## Statistical Annotations
Significance: ns (p>.05), * (p≤.05), ** (p≤.01), *** (p≤.001), **** (p≤.0001). Always show effect size with CI. Format: `β = 0.42 [0.18, 0.66]`. Never show p-value alone. Default 95% CI. Label confidence level. Never use SE bars without labeling.

---

## Chart Selection
Distribution→histogram/violin/raincloud (not pie). Comparison→sorted bar/dot plot (not 3D bar). Correlation→scatter+regression line. Time series→line+ribbon. Proportions→stacked bar/mosaic. Model results→forest plot/dot-and-whisker. Missing data→missingness matrix. Causal→DAG with annotations.

---

## Accessibility
Colorblind-safe (test with Coblis/Color Oracle). Color is never the only differentiator — use patterns, shapes, labels. Text contrast ≥4.5:1 (WCAG AA). All figures have alt text. Tables have proper headers. Interactive elements have ARIA labels.

---

## Theme Module
Create `scripts/utils/viz_theme.py` with: `OKABE_ITO` palette list, `SEMANTIC` color dict, `apply_matplotlib_theme()` (sets rcParams for fonts, colors, grid, spines, DPI=300, fonttype=42), `apply_plotly_theme()` (returns layout dict with font, colors, margins, grid). Apply theme module to every figure — no manual styling.

---

## Validation Checklist
- [ ] Okabe-Ito or approved sequential/diverging palette
- [ ] Colorblind-safe
- [ ] Axes labeled with units
- [ ] Font sizes ≥8pt print, ≥10pt web
- [ ] No chart junk
- [ ] Statistical annotations follow standard
- [ ] Effect sizes with CIs
- [ ] Alt text provided
- [ ] Figure size matches journal format
- [ ] DPI ≥300, fonts embedded (pdf.fonttype=42)
- [ ] Theme module applied
- [ ] Top/right spines removed
- [ ] Grid lines subtle (alpha ≤ 0.2)
- [ ] .interpret.md file generated
""",
    "figure_descriptive": """---
skill_id: "figure_descriptive"
version: "8.0.0"
category: "visualization"
domain_compatibility: ["all"]
required_tools: ["python", "matplotlib", "seaborn", "plotly"]
depends_on: ["viz_design_system", "viz_code_standards", "descriptive_stats"]
produces: ["reports/figures/descriptive/"]
complexity: "basic"
---

# Skill: Descriptive Statistics Figures

## Purpose
Generate publication-quality figures summarizing descriptive statistics. Every figure uses the design system theme, proper sizing, and accessibility standards.

## When to Use
- After descriptive statistics computed
- For Table 1 visualizations
- Exploratory data analysis

---

## Figure Specifications

### Distribution Plots

#### Histogram + KDE
```python
def plot_distribution(df, column, ax=None, bins=30, add_stats=True):
    \"\"\"Histogram with KDE overlay and statistics.
    
    Features:
    - Density histogram (area = 1)
    - KDE curve overlay
    - Mean (solid line) and median (dashed line)
    - Statistics box: mean, median, SD, skewness, N
    - Proper axis labels with units
    \"\"\"
```

#### Violin Plot (Grouped)
```python
def plot_violin_grouped(df, value_col, group_col, ax=None):
    \"\"\"Violin plot comparing distributions across groups.
    
    Features:
    - Violin shape (distribution density)
    - Box plot inside (median, IQR)
    - Individual data points (jittered, if N < 200)
    - Color: Okabe-Ito palette
    - Sorted by median (descending)
    \"\"\"
```

#### Raincloud Plot
```python
def plot_raincloud(df, value_col, group_col, ax=None):
    \"\"\"Raincloud plot: half-violin + box + raw data.
    
    Features:
    - Half-violin (distribution shape)
    - Box plot (median, IQR, whiskers)
    - Jittered raw data points
    - Best for: group comparisons with moderate N
    \"\"\"
```

### Categorical Plots

#### Bar Chart (Sorted)
```python
def plot_categorical_bar(df, column, ax=None, normalize=True):
    \"\"\"Bar chart of category frequencies, sorted descending.
    
    Features:
    - Sorted by frequency (highest first)
    - Proportion labels on bars
    - Count labels below bars
    - Color: single hue (Blues)
    - Horizontal orientation (better for long labels)
    \"\"\"
```

#### Stacked Bar (Cross-tabulation)
```python
def plot_stacked_bar(df, row_col, col_col, ax=None, normalize="row"):
    \"\"\"Stacked bar chart for cross-tabulation.
    
    Features:
    - Proportional stacking
    - Legend with category labels
    - Color: Okabe-Ito palette
    - Normalize by row, column, or total
    \"\"\"
```

### Multivariate Plots

#### Correlation Heatmap
```python
def plot_correlation_heatmap(df, columns=None, ax=None, 
                              method="pearson", annot=True):
    \"\"\"Correlation matrix heatmap.
    
    Features:
    - Diverging colormap (RdBu_r, centered at 0)
    - Annotated with r values (2 decimal places)
    - Sorted by hierarchical clustering
    - Square cells
    - Colorbar with labeled scale
    \"\"\"
```

#### Pairplot (Subset)
```python
def plot_pairplot(df, columns=None, max_vars=6, hue=None):
    \"\"\"Pairplot for key variables (max 6×6).
    
    Features:
    - Diagonal: histogram + KDE
    - Off-diagonal: scatter + regression line
    - Color by hue variable if specified
    - Size: 3" × 3" per panel
    \"\"\"
```

---

## Output Standards

### File Naming
```
fig_desc_001_distribution_[variable].png
fig_desc_002_violin_[value]_by_[group].png
fig_desc_003_correlation_heatmap.png
fig_desc_004_pairplot_[vars].png
```

### Format
- **Primary**: PNG at 300 DPI
- **Editable**: SVG (for line art)
- **Size**: Single column (3.35" wide) or double column (6.89" wide)

---

## Validation Checks
- [ ] All figures have axis labels with units
- [ ] Colorblind-safe palettes used
- [ ] No overlapping text or labels
- [ ] Figures match descriptive statistics values
- [ ] Font sizes meet minimum (10pt)
- [ ] Design system theme applied
- [ ] Statistical annotations follow standards
""",
    "figure_missingness": """---
skill_id: "figure_missingness"
version: "8.0.0"
category: "visualization"
domain_compatibility: ["all"]
required_tools: ["python", "matplotlib", "seaborn", "missingno"]
depends_on: ["viz_design_system", "viz_code_standards", "detect_missingness"]
produces: ["reports/figures/missingness/"]
complexity: "basic"
---

# Skill: Missingness Visualization

## Purpose
Generate figures showing missing data patterns, mechanisms, and impact on analysis.

## When to Use
- After missingness analysis
- For methods section (missing data handling)
- Diagnosing missingness mechanisms

---

## Figure Specifications

### Missingness Matrix
```python
def plot_missingness_matrix(df, max_rows=1000, ax=None):
    \"\"\"Heatmap of missing data pattern.
    
    Features:
    - Rows: observations (sampled if N > max_rows)
    - Columns: variables (sorted by missingness)
    - Missing: dark color, Present: light color
    - Sparkline on right: missingness per row
    - Bar chart on bottom: missingness per column
    \"\"\"
```

### Missingness Bar Chart
```python
def plot_missingness_bars(df, ax=None, sort=True):
    \"\"\"Horizontal bar chart of missing proportions.
    
    Features:
    - Sorted: highest missingness at top
    - Annotated: exact percentage on each bar
    - Color gradient: green (0%) → yellow (20%) → red (50%+)
    - Threshold line: warning level (20%)
    \"\"\"
```

### Missingness Correlation
```python
def plot_missingness_correlation(df, ax=None):
    \"\"\"Heatmap of pairwise missingness correlations.
    
    Features:
    - Binary indicators: 1 if missing, 0 if present
    - Phi coefficient (for binary-binary correlation)
    - Diverging colormap
    - Only show variables with > 5% missingness
    \"\"\"
```

### Missingness by Subgroup
```python
def plot_missingness_by_subgroup(df, group_col, ax=None):
    \"\"\"Missing rate in other variables by subgroup.
    
    Features:
    - Grouped bar chart
    - One bar per variable, grouped by category
    - Identifies MAR mechanism
    \"\"\"
```

---

## Output Standards

### File Naming
```
fig_miss_001_matrix.png
fig_miss_002_bars.png
fig_miss_003_correlation.png
fig_miss_004_by_subgroup.png
```

## Validation Checks
- [ ] Matrix shows correct missing pattern
- [ ] Bar chart percentages match computed values
- [ ] Correlation matrix is symmetric
- [ ] Subgroup analysis includes all categories
- [ ] Design system theme applied
""",
    "shareable_dashboard": """# Skill: Shareable Dashboard

> Generates Quarto `.qmd` + standalone Plotly HTML dashboard with interactive figures.

## Purpose
Dual output: a Quarto source file (renderable to HTML/PDF/DOCX) and a standalone HTML dashboard using `plotly.offline` for zero-server interactivity.

---

## Protocol

### Step 1: Gather Content
Collect from experiment outputs: data table, all figures with `.interpret.md` files, results JSONs, key findings, and figure captions.

### Step 2: Generate Quarto `.qmd`
Create a `.qmd` with YAML front matter specifying `html`, `pdf`, and `docx` formats. Include sections: Summary, Data Overview (with `df.describe()` code block), Results (figures via `pio.show()`), Methods, and Data. Use `code-fold: true` for clean rendering.

### Step 3: Generate Standalone HTML
Build a single HTML file with these components:

**(a) Data table with filtering** — Paginated table (max 100 rows shown). Add text search input that filters rows via JS `textContent.toLowerCase().includes()`. Add column dropdown filter. Include Previous/Next pagination buttons.

**(b) Figure gallery** — CSS grid layout (`grid-template-columns: repeat(auto-fill, minmax(400px, 1fr))`). Each card: image, caption from `.interpret.md`, statistical annotation. Responsive: single column on mobile.

**(c) Results summary cards** — 3-card grid: Sample Size (N), Significant Findings (X of Y), Effect Size Range. Each card: large value, label, subtitle.

**(d) Download buttons** — Links for CSV data, PNG figures, LaTeX tables. Add `window.print()` button.

### Step 4: Embed Plotly Figures
Use `plotly.io.to_html(fig, include_plotlyjs='cdn', full_html=False)` for each figure. Embed in the HTML with Plotly CDN loaded in `<head>`.

### Step 5: Assemble
Combine all components into one HTML file with embedded CSS and JS. No external dependencies except Plotly CDN.

## Output
- `03_synthesis/dashboard/dashboard.qmd` — Quarto source
- `03_synthesis/dashboard/dashboard.html` — Standalone interactive HTML
- `03_synthesis/dashboard/figures/` — Copied figures
- `03_synthesis/dashboard/data/` — Downloadable data

## Render Commands
```
quarto render dashboard.qmd --to html
quarto render dashboard.qmd --to pdf
quarto render dashboard.qmd --to docx
```

## Validation
- [ ] `.qmd` renders without errors
- [ ] `.html` opens with no console errors
- [ ] Table filtering works
- [ ] Plotly figures interactive
- [ ] Download buttons functional
- [ ] Responsive on mobile
""",
    "viz_altair": """# Skill: Declarative Charts with Altair

## Purpose
Altair is a declarative statistical visualization library for Python, based on the Vega and Vega-Lite visualization grammars. It allows creating interactive, layered charts where the chart specification matches the statistical properties of the data.

## Installation
```bash
pip install altair vega_datasets
```

## Protocol & Best Practices
1. **Use Declarative Mappings:** Define charts by mapping data columns to visual encoding channels (e.g., `x`, `y`, `color`, `size`) rather than drawing shapes manually.
2. **Handle Large Datasets Wisely:** By default, Altair limits dataset size to 5000 rows to prevent bloated HTML. For larger datasets, use `.pre_transform_data()` or enable the JSON data transformer:
   ```python
   import altair as alt
   alt.data_transformers.enable('json')
   ```
3. **Always Set Explicit Data Types:** Append type shorthand to column names to avoid parsing errors:
   - `:Q` for Quantitative (numerical)
   - `:O` for Ordinal (ordered categorical)
   - `:N` for Nominal (unordered categorical)
   - `:T` for Temporal (dates/times)
4. **Color Safe Palettes:** Bind categorical colors to the Okabe-Ito palette.

## Code Template

```python
import altair as alt
import pandas as pd

def create_interactive_scatter(df: pd.DataFrame, x_col: str, y_col: str, color_col: str) -> alt.Chart:
    # Okabe-Ito color palette
    okabe_ito = ["#000000", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7"]
    
    # Selection interval for panning and zooming
    brush = alt.selection_interval(resolve='global')
    
    chart = alt.Chart(df).mark_circle(size=60).encode(
        x=alt.X(f"{x_col}:Q", scale=alt.Scale(zero=False), title=x_col.replace("_", " ").title()),
        y=alt.Y(f"{y_col}:Q", scale=alt.Scale(zero=False), title=y_col.replace("_", " ").title()),
        color=alt.condition(
            brush, 
            alt.Color(f"{color_col}:N", scale=alt.Scale(range=okabe_ito), title=color_col.title()), 
            alt.value('lightgray')
        ),
        tooltip=[x_col, y_col, color_col]
    ).add_params(
        brush
    ).properties(
        width=500,
        height=350,
        title=f"{y_col.title()} vs {x_col.title()}"
    )
    
    return chart
```
""",
    "figure_validator": """# Skill: Figure Quality Enforcement

## Purpose
Ensures all generated research figures meet publication-quality standards. Running this validation prior to committing outputs prevents cut-off axes, low resolutions, massive file sizes, and non-inclusive color palettes from entering the final manuscript.

## Protocol & Quality Checklist

Before any generated figure is accepted:
1. **DPI Minimum (300 DPI):** Ensure the output image contains metadata specifying at least 300 DPI, or is of equivalent resolution (width $\\ge 1200\\text{px}$).
2. **Margin Axis Labels:** Verify left and bottom margins contain variance in pixels indicating ticks and labels are present and not missing.
3. **No Axis Truncation:** Ensure non-background pixels do not touch the image edge (preventing layout clipping).
4. **Colorblind Safe Check:** Avoid pure saturated red-green pairings. Restrict categorical elements to the Okabe-Ito palette.
5. **File Size Bounds:** Constrain individual figures to $\\le 5\\text{MB}$.

## Integration

Run the validator script automatically at the end of visualization steps:
```bash
python -m research_copilot.utils.figure_validator path/to/figure.png
```
If the script returns a `FAIL` (exit code 1), the visual output is rejected, and the pipeline blocks until the plotting code is adjusted (e.g. adding `plt.tight_layout()` or setting correct DPI parameters).
""",
    "viz_3d_surface": """# Skill: 3D Response Surface Plots with Plotly

## Purpose
3D response surfaces are designed to visualize statistical response models, optimization spaces, or parameter sweeps where the output depends on two continuous variables. 

## Protocol & Best Practices
1. **Never Decorative:** Do not use 3D plots for simple multi-category distributions or basic tables where a 2D heatmap or faceted layout would convey the same information. Only use 3D when modeling a continuous response function $z = f(x, y)$.
2. **Include 2D Projection Contours:** Always project contour lines onto the bottom plane of the 3D box so the quantitative values can be read without perspective distortion.
3. **Use Perceptually Uniform Colormaps:** Apply uniform continuous colormaps like `viridis`, `magma`, or `plasma`. Never use `rainbow` or `jet`.

## Code Template

```python
import plotly.graph_objects as go
import numpy as np
import pandas as pd

def create_response_surface(x_grid: np.ndarray, y_grid: np.ndarray, z_matrix: np.ndarray, 
                            x_label: str, y_label: str, z_label: str, output_path: str):
    fig = go.Figure(data=[go.Surface(
        z=z_matrix, 
        x=x_grid, 
        y=y_grid,
        colorscale='Viridis',
        contours = {
            # Project contours onto z-axis (bottom plane)
            "z": {"show": True, "start": float(z_matrix.min()), "end": float(z_matrix.max()), "size": (z_matrix.max()-z_matrix.min())/10, "project": {"z": True}}
        }
    )])
    
    fig.update_layout(
        title=f"Response Surface for {z_label}",
        scene = {
            "xaxis_title": x_label,
            "yaxis_title": y_label,
            "zaxis_title": z_label,
        },
        autosize=False,
        width=800,
        height=600,
        margin=dict(l=65, r=50, b=65, t=90)
    )
    
    fig.write_html(output_path)
    print(f"Generated 3D Response Surface: {output_path}")
```
""",
    "viz_holoviews": """# Skill: Declarative Multi-Dimensional Plotting with HoloViews

## Purpose
HoloViews focuses on declaring data structures (e.g., Curves, Scatters, HeatMaps) rather than writing plotting code. It integrates directly with Bokeh, Matplotlib, and Plotly backends to render complex multi-dimensional relationships instantly.

## Installation
```bash
pip install holoviews panel
```

## Protocol & Best Practices
1. **Declare Dimensions Explicitly:** Annotate dimensions as `kdims` (key dimensions, representing independent variables/indices) and `vdims` (value dimensions, representing dependent variables/metrics).
2. **Utilize Containers:** Use container classes like `Layout`, `Overlay` (for layered figures), and `NdOverlay` (for multidimensional comparison across parameters) to organize figures cleanly.
3. **Switch Backends Gracefully:** Use `hv.extension('bokeh')` or `hv.extension('matplotlib')` at the beginning of the script depending on whether static or interactive export is needed.

## Code Template

```python
import holoviews as hv
import pandas as pd
hv.extension('bokeh')

def create_holoviews_layout(df: pd.DataFrame, x_col: str, y_col: str, group_col: str) -> hv.Layout:
    # Key dimensions (independent) and Value dimensions (dependent)
    kdims = [x_col]
    vdims = [y_col, group_col]
    
    # Create dataset
    ds = hv.Dataset(df, kdims=kdims + [group_col], vdims=y_col)
    
    # Generate overlaid curves grouped by group_col
    curves = ds.to(hv.Curve, x_col, y_col).overlay(group_col)
    
    # Generate scatter points overlay
    points = ds.to(hv.Scatter, x_col, y_col).overlay(group_col)
    
    # Combine curves and points, layout horizontally
    layout = (curves * points).opts(
        hv.opts.Curve(width=500, height=350, tools=['hover'], line_width=2),
        hv.opts.Scatter(size=6, alpha=0.8)
    )
    
    return layout
```
""",
    "viz_circos": """# Skill: Genomic & Network Circular Layouts (Circos)

## Purpose
Genomic and high-dimensional network datasets are often best represented in circular layouts (Circos style), enabling the depiction of relationships between multiple chromosomes, loci, or network groups in a single dense figure.

## Installation
```bash
pip install pycirclize
```

## Protocol & Best Practices
1. **Define Rings and Tracks:** Structure sectors representing genome chromosomes or network modules, then place concentric track layers containing histograms, scatters, or heatmaps within those sectors.
2. **Establish Chord Links:** Draw links inside the circle to represent structural variations, correlation linkages, or flow between regions.
3. **Limit High Density:** Overly cluttered Circos plots lose informational value. Filter links using statistical significance thresholds (e.g. correlation $|r| > 0.6$ or FDR $p < 0.05$) before drawing chords.

## Code Template

```python
from pycirclize import Circos
import pandas as pd
import matplotlib.pyplot as plt

def create_circular_network_plot(nodes_df: pd.DataFrame, links_df: pd.DataFrame, output_path: str):
    # nodes_df: name, size
    # links_df: source, target, weight
    
    sectors = {row["name"]: row["size"] for _, row in nodes_df.iterrows()}
    circos = Circos(sectors, space=5)
    
    # Style tracks
    for sector in circos.sectors:
        track = sector.add_track((95, 100))
        track.rect(fill_color="#56B4E9", line_color="black")
        track.text(sector.name, color="black", r=108, size=10)
    
    # Plot links between nodes
    for _, link in links_df.iterrows():
        src = link["source"]
        tgt = link["target"]
        w = link["weight"]
        
        # Color chord by weight
        color = "#D55E00" if w > 0 else "#0072B2"
        
        # Draw link chord
        circos.link((src, 0, sectors[src]), (tgt, 0, sectors[tgt]), color=color, alpha=0.6)
        
    fig = circos.plotfig()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
```
""",
    "dashboard_results": """---
skill_id: "dashboard_results"
version: "8.0.0"
category: "visualization"
domain_compatibility: ["all"]
required_tools: ["python", "dash", "plotly", "dash-bootstrap-components", "statsmodels"]
depends_on: ["viz_design_system", "viz_code_standards", "inferential_parametric", "inferential_nonparametric"]
produces:
  - "reports/dashboards/results_dashboard.py"
  - "reports/dashboards/components/results/"
complexity: "advanced"
---

# Skill: Results Dashboard

## Purpose
Build an interactive dashboard for exploring statistical analysis results: effect sizes, model coefficients, diagnostics, and model comparisons. Built with component architecture, proper statistical visualization, and reproducibility.

## When to Use
- After inferential analysis completed
- For results review and sensitivity analysis
- Comparing multiple model specifications
- Peer review preparation

---

## Architecture

### File Structure
```
reports/dashboards/
  results_dashboard.py
  components/
    results/
      __init__.py
      forest_plot.py          # Interactive forest plot component
      coefficient_table.py    # Sortable results table
      model_comparison.py     # Side-by-side model comparison
      sensitivity.py          # Sensitivity analysis controls
      diagnostics.py          # Model diagnostic plots
```

---

## Layout

### Tab 1: Effect Sizes
```
┌─────────────────────────────────────────────────┐
│  Effect Sizes                                    │
├─────────────────────────────────────────────────┤
│  [Dropdown: Question] [Dropdown: Method]        │
│  [Checkbox: Show non-significant]               │
├─────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────┐   │
│  │  Forest Plot                             │   │
│  │  • Effect sizes with 95% CI bars        │   │
│  │  • Color: significant vs non-significant │   │
│  │  • Null reference line                   │   │
│  │  • Hover: full statistics                │   │
│  └──────────────────────────────────────────┘   │
├─────────────────────────────────────────────────┤
│  Results Table                                   │
│  Variable | Estimate | 95% CI | SE | p | adj. p │
│  [Sortable] [Filterable] [Exportable]           │
└─────────────────────────────────────────────────┘
```

### Tab 2: Model Comparison
```
┌─────────────────────────────────────────────────┐
│  Model Comparison                                │
├─────────────────────────────────────────────────┤
│  [Multi-select: Models to compare]              │
├─────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────┐   │
│  │  Coefficient Comparison Plot             │   │
│  │  • Dot-and-whisker for each model        │   │
│  │  • Color by model                        │   │
│  │  • Highlight unstable coefficients       │   │
│  └──────────────────────────────────────────┘   │
├─────────────────────────────────────────────────┤
│  Model Fit Table                                 │
│  Model | AIC | BIC | R² | Log-Likelihood | N   │
└─────────────────────────────────────────────────┘
```

### Tab 3: Sensitivity Analysis
```
┌─────────────────────────────────────────────────┐
│  Sensitivity Analysis                            │
├─────────────────────────────────────────────────┤
│  Controls:                                       │
│  [ ] Exclude outliers                           │
│  [ ] Remove covariate: [dropdown]               │
│  [ ] Subgroup: [dropdown]                       │
│  [ ] Alternative method: [dropdown]             │
├─────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────┐   │
│  │  Sensitivity Plot                        │   │
│  │  • Base estimate (bold line)             │   │
│  │  • Sensitivity estimates (lighter lines) │   │
│  │  • Color: changes conclusion vs not      │   │
│  └──────────────────────────────────────────┘   │
├─────────────────────────────────────────────────┤
│  Sensitivity Summary                             │
│  Specification | Estimate | 95% CI | Conclusion │
│  [Highlight: specifications that change result] │
└─────────────────────────────────────────────────┘
```

---

## Component Specifications

### Forest Plot
```python
def create_forest_plot(
    results_df,
    title="Effect Sizes",
    show_null_line=True,
    color_by_significance=True,
    sort_by="estimate",
    sort_order="descending",
):
    \"\"\"Publication-quality forest plot.
    
    Features:
    - Sorted by effect size or p-value
    - Color-coded by significance
    - Null reference line
    - Hover with full statistics
    - Proper CI error bars
    \"\"\"
```

### Coefficient Table
```python
def create_coefficient_table(
    results_df,
    columns=None,
    sort_by="p_value",
    sort_order="ascending",
    highlight_significant=True,
    show_adjusted_p=True,
):
    \"\"\"Interactive dash-table for results.
    
    Features:
    - Sortable by any column
    - Color-coded significance
    - Export to CSV
    - Conditional formatting
    \"\"\"
```

### Model Comparison Plot
```python
def create_model_comparison(
    models_dict,  # {model_name: results_df}
    highlight_unstable=True,
    threshold=0.1,  # Coefficient change threshold
):
    \"\"\"Side-by-side coefficient comparison.
    
    Features:
    - Dot-and-whisker for each model
    - Highlight coefficients that change > threshold
    - Model fit statistics table
    \"\"\"
```

### Sensitivity Analysis
```python
def create_sensitivity_plot(
    base_estimate,
    sensitivity_results,  # List of (spec_name, estimate, ci_lower, ci_upper)
    highlight_conclusion_changes=True,
):
    \"\"\"Sensitivity analysis visualization.
    
    Features:
    - Base estimate as reference
    - All sensitivity specs overlaid
    - Color: changes conclusion vs doesn't
    - Summary table with all specs
    \"\"\"
```

---

## Statistical Visualization Standards

### Forest Plot Rules
- Sort by effect size (largest first) or p-value (smallest first)
- Null line clearly visible (dashed, gray)
- Significant results in blue, non-significant in gray
- Hover shows: estimate, CI, p-value, adjusted p-value, N
- Y-axis labels: variable names (not codes)
- X-axis: labeled with effect size metric (β, OR, RR, etc.)

### Coefficient Table Rules
- Show: estimate, SE, 95% CI, p-value, adjusted p-value
- Sort by p-value by default
- Highlight significant rows (subtle background color)
- Show N for each estimate
- Format numbers: 3 decimal places for estimates, 4 for p-values
- Scientific notation for very small p-values (p < 0.001)

### Model Comparison Rules
- Show coefficients for ALL models side by side
- Highlight coefficients that change > 10% across models
- Include model fit statistics (AIC, BIC, R², log-likelihood)
- Order models: simplest to most complex
- Use consistent color per model

### Sensitivity Analysis Rules
- Base estimate clearly marked
- Show ALL sensitivity specifications
- Color-code: specifications that change the conclusion
- Report: which specifications alter the conclusion
- Never hide sensitivity results that contradict main finding

---

## Interactive Features

### Filters
- **Question selector**: Filter results by research question
- **Method selector**: Choose analysis method
- **Significance filter**: Show/hide non-significant results
- **Variable filter**: Select specific variables
- **Model selector**: Choose which models to compare

### Downloads
- **Forest plot PNG**: High-resolution export
- **Results CSV**: Full results table
- **Model comparison CSV**: All model coefficients
- **Sensitivity report**: Full sensitivity analysis summary

### Tooltips
- **Statistical terms**: Explain estimate, CI, p-value
- **Variable names**: Show variable definition
- **Method descriptions**: Explain analysis approach

---

## Implementation Steps

1. **Create result components** — forest_plot.py, coefficient_table.py, model_comparison.py, sensitivity.py
2. **Load pre-computed results** — From analysis output files
3. **Build main app** — Import components, define layout
4. **Implement callbacks** — Filter updates, comparison toggles
5. **Add download handlers** — PNG, CSV exports
6. **Test** — Verify all tabs, filters, downloads
7. **Validate** — All figures pass design system checks

---

## Output Specification
- `reports/dashboards/results_dashboard.py`: Runnable Dash app
- `reports/dashboards/components/results/`: Result components

## Validation Checks
- [ ] Forest plot correctly shows effect sizes and CIs
- [ ] Coefficient table matches analysis output
- [ ] Model comparison highlights unstable coefficients
- [ ] Sensitivity analysis shows all specifications
- [ ] Filters correctly subset results
- [ ] Downloads produce correct files
- [ ] No hardcoded colors or sizes
- [ ] All figures pass design system validation
- [ ] Runs on port 8050 without errors
- [ ] Statistical values match computed results exactly
""",
    "dashboard_explorer": """---
skill_id: "dashboard_explorer"
version: "8.0.0"
category: "visualization"
domain_compatibility: ["all"]
required_tools: ["python", "dash", "plotly", "dash-bootstrap-components", "pandas"]
depends_on: ["viz_design_system", "viz_code_standards", "profile_tabular"]
produces:
  - "reports/dashboards/data_explorer.py"
  - "reports/dashboards/components/explorer/"
complexity: "intermediate"
---

# Skill: Interactive Data Explorer Dashboard

## Purpose
Build an interactive dashboard for exploring raw and processed data: filtering, sorting, visualizing distributions, and profiling variables. Built with component architecture and automatic plot type selection.

## When to Use
- After data profiling
- For exploratory data analysis
- Collaborative data review
- Data quality assessment

---

## Architecture

### File Structure
```
reports/dashboards/
  data_explorer.py
  components/
    explorer/
      __init__.py
      data_table.py           # Paginated, filterable table
      variable_profile.py     # Auto-type-aware variable plots
      bivariate.py            # Auto-type-aware bivariate plots
      filters.py              # Filter panel
      summary_cards.py        # Data summary metrics
```

---

## Layout

```
┌─────────────────────────────────────────────────┐
│  Data Explorer — [Dataset Name]                  │
├─────────────────────────────────────────────────┤
│  [Dropdown: Dataset]  [N = XXXX]  [p = XX vars] │
├─────────────────────────────────────────────────┤
│  Summary Cards                                   │
│  [Rows] [Columns] [Missing %] [Duplicates]       │
├─────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────────────────┐  │
│  │ Variable    │  │  Variable Distribution    │  │
│  │ Selector    │  │  (auto-type plot)         │  │
│  │             │  │                           │  │
│  │ [Search]    │  │                           │  │
│  │ [Type filt] │  │                           │  │
│  └─────────────┘  └──────────────────────────┘  │
├─────────────────────────────────────────────────┤
│  Bivariate Explorer                              │
│  X: [Dropdown]  Y: [Dropdown]  Color: [Dropdown]│
│  ┌──────────────────────────────────────────┐   │
│  │  Auto-type bivariate plot                │   │
│  └──────────────────────────────────────────┘   │
├─────────────────────────────────────────────────┤
│  Filter Panel                                    │
│  [Condition builder] [Apply] [Reset] [Export]   │
├─────────────────────────────────────────────────┤
│  Data Table (paginated, sortable, filterable)   │
└─────────────────────────────────────────────────┘
```

---

## Auto-Type Plot Selection

### Univariate (Single Variable)
| Variable Type | Plot Type | Features |
|--------------|-----------|----------|
| Continuous | Histogram + KDE + rug | Density overlay, mean/median lines |
| Categorical | Bar chart | Sorted by frequency, proportions on hover |
| Ordinal | Bar chart | Preserves order, frequency labels |
| Temporal | Line plot | Time axis, trend line, seasonality |
| Binary | Donut chart | Proportions, counts |
| Text | Length histogram | Word count distribution |

### Bivariate (Two Variables)
| X Type | Y Type | Plot Type | Features |
|--------|--------|-----------|----------|
| Continuous | Continuous | Scatter + regression line | Confidence band, correlation |
| Continuous | Categorical | Violin plot | Distribution per category |
| Categorical | Continuous | Box plot | Median, IQR, outliers |
| Categorical | Categorical | Stacked bar | Proportions, counts |
| Temporal | Continuous | Line plot | Time series, trend |
| Continuous | Temporal | Line plot | Time on x-axis |

---

## Component Specifications

### Variable Profile Plot
```python
def create_variable_profile(df, column):
    \"\"\"Auto-generate appropriate plot based on variable type.
    
    Returns:
        go.Figure with appropriate plot type
    \"\"\"
    col_type = infer_column_type(df[column])
    plot_funcs = {
        "continuous": histogram_with_kde,
        "categorical": bar_chart_proportions,
        "ordinal": ordered_bar_chart,
        "temporal": time_series_plot,
        "binary": donut_chart,
    }
    return plot_funcs[col_type](df, column)
```

### Bivariate Plot
```python
def create_bivariate_plot(df, x_col, y_col, color_col=None):
    \"\"\"Auto-generate bivariate plot based on variable types.
    
    Returns:
        go.Figure with appropriate plot type
    \"\"\"
    x_type = infer_column_type(df[x_col])
    y_type = infer_column_type(df[y_col])
    # Dispatch to appropriate plot function
```

### Filter Panel
```python
def create_filter_panel(df):
    \"\"\"Generate filter controls for each variable type.
    
    Continuous: Range slider
    Categorical: Multi-select dropdown
    Temporal: Date range picker
    Binary: Toggle switch
    \"\"\"
```

---

## Data Table Features

- **Pagination**: 50 rows per page (configurable)
- **Sorting**: Click column header to sort
- **Filtering**: Per-column filter controls
- **Conditional formatting**:
  - Missing values: highlighted in orange
  - Outliers: highlighted in red
  - Duplicate rows: highlighted in yellow
- **Export**: Filtered subset as CSV
- **Column types**: Color-coded header by semantic type

---

## Filter System

### Filter Types
- **Range**: Min/max slider for continuous variables
- **Category**: Multi-select checkbox for categorical
- **Date**: Date range picker for temporal
- **Text**: Contains/starts with/equals for text
- **Missing**: Show/hide missing values

### Filter Logic
- Multiple filters combine with AND
- Live N counter shows filtered sample size
- Reset button clears all filters
- Export button downloads filtered data

---

## Performance

- **DataTable**: Virtualized rendering (only visible rows)
- **Plots**: Cached per variable (don't recompute on tab switch)
- **Filters**: Debounced (wait 300ms after last input)
- **Large datasets**: Sample to 10,000 rows for plots, show full in table

---

## Implementation Steps

1. **Create explorer components** — data_table.py, variable_profile.py, bivariate.py, filters.py
2. **Build main app** — Import components, define layout
3. **Implement type inference** — Auto-detect variable types
4. **Wire callbacks** — Variable selector → plot, filters → table
5. **Add export** — CSV download of filtered data
6. **Test** — Verify all plot types, filters, table features

---

## Output Specification
- `reports/dashboards/data_explorer.py`: Runnable Dash app
- `reports/dashboards/components/explorer/`: Explorer components

## Validation Checks
- [ ] DataTable loads without error
- [ ] Variable plots render correctly for ALL types
- [ ] Bivariate plots dispatch to correct type combination
- [ ] Filters correctly subset data
- [ ] Live N counter updates with filters
- [ ] Export produces valid CSV with filtered data
- [ ] Conditional formatting works (missing, outliers, duplicates)
- [ ] No hardcoded colors or sizes
- [ ] All figures pass design system validation
- [ ] Runs on port 8050 without errors
""",
    "figure_workflow_dag": """---
skill_id: "figure_workflow_dag"
version: "8.0.0"
category: "visualization"
domain_compatibility: ["all"]
required_tools: ["python", "networkx", "matplotlib"]
depends_on: ["viz_design_system", "viz_code_standards"]
produces: ["reports/figures/workflow_dag.png", "reports/workflow_dag.mermaid"]
complexity: "intermediate"
---

# Skill: Workflow DAG Visualization

## Purpose
Generate a visual representation of the entire research workflow as a directed acyclic graph, showing skill execution order and data flow.

## When to Use
- After analysis pipeline executed
- For reproducibility documentation
- Tracking research provenance

---

## Node Types

| Status | Color | Description |
|--------|-------|-------------|
| Completed | `#009E73` (green) | Successfully executed |
| Failed | `#D55E00` (vermillion) | Execution error |
| Skipped | `#999999` (gray) | Not applicable |
| Running | `#0072B2` (blue) | In progress |

## Layout

- **Direction**: Left-to-right (topological order)
- **Node size**: Proportional to execution time
- **Labels**: skill_id + status icon
- **Edges**: Dependency relationships

## Mermaid Export

Generate Mermaid.js flowchart syntax for embedding in markdown:

```mermaid
flowchart LR
    A[research_init] --> B[literature_deep]
    B --> C[method_route]
    C --> D[data_scaffold]
    D --> E[execute_analysis]
    E --> F[compile_outputs]
    F --> G[audit_validate]
```

---

## Validation Checks
- [ ] Graph is acyclic
- [ ] All executed skills included
- [ ] Dependencies correctly represented
- [ ] Mermaid syntax validates
- [ ] Design system colors used
""",
    "viz_code_standards": """---
skill_id: "viz_code_standards"
version: "1.0.0"
category: "visualization"
domain_compatibility: ["all"]
required_tools: ["python", "matplotlib", "seaborn", "plotly", "dash"]
depends_on: ["viz_design_system"]
produces: ["scripts/utils/viz_helpers.py"]
complexity: "intermediate"
---

# Skill: Visualization Code Standards

## Purpose
Professional code quality for ALL visualization and dashboard code. No spaghetti plots. No hardcoded values. No untested rendering.

---

## Architecture Rules

1. **Modular design**: Main entry point (`03_figures.py`) imports from `utils/viz_theme.py`, `utils/viz_helpers.py`, `utils/viz_validation.py`.
2. **Function-based plotting**: NEVER inline plotting code. Every plot type is a function.
3. **Configuration over hardcoding**: Use theme constants for colors, sizes, paths. Never `color="#FF0000"` or `dpi=150`.
4. **Data validation before plotting**: Check required columns exist, min rows ≥3, not all null.
5. **Error handling**: All plotting functions return `{"status": "success/error", "path": ...}` dicts.

---

## Dashboard Architecture

Component-based structure: main app (≤200 lines) imports from `components/cards.py`, `components/charts.py`, `components/tables.py`, `components/filters.py`, `components/layout.py`. Assets in `assets/custom.css`. Data pre-computed to `data/dashboard_cache.parquet` — never load raw data in callbacks.

Every component is a function returning a Dash component. Use `@lru_cache` for data loading. Callbacks show loading spinners. Use `dash.no_update` when input hasn't changed.

---

## Plotly Figure Standards

Build figures with `go.Figure()`, add traces, set layout. Use `template=plotly_template` from theme. Sort data before plotting. Add null reference lines with `fig.add_vline()`. Use `customdata` for hover templates. Responsive sizing: `autosize=True, height=400` for dashboards. Fixed sizing: `width=689, height=430` for static journal figures.

---

## CSS Standards

Import Inter font. Card styling: border, border-radius 8px, hover shadow. Tables: 12px font, bold headers. Tabs: active tab has 3px bottom border in accent color. Loading states: accent color. Print styles: hide non-print elements, remove shadows.

---

## Performance

Cache data with `@lru_cache(maxsize=32)`. Load pre-computed parquet, not raw data. Only recompute when callback input changes (`if not ctx.triggered: return dash.no_update`).

---

## Accessibility Annotation

**Every figure MUST have screen reader metadata.**

### Plotly
Set `fig.update_layout(meta={'alt_text': '...'})`. Add `aria-label` on the containing `html.Div`. Make focusable with `tabIndex=0`.

### matplotlib
Pass `metadata={'Title': '...', 'Description': '...'}` to `fig.savefig()`. Set figure title.

### Alt Text Template
`[Figure type] of [N] observations showing [relationship]. [Key finding with statistics]. [Visual encoding note].`

Examples:
- "Scatter plot of 1,234 observations showing positive association between income and life satisfaction. β = 0.34, 95% CI [0.21, 0.47], p < .001."
- "Forest plot of 5 coefficients. Three significant (blue), two non-significant (gray). Effects range 0.12 to 0.67."

### Dashboard ARIA
Wrap figures in `html.Div(dcc.Graph(figure=fig), role="img", aria-label=alt_text, tabIndex=0)`. Tables: `role="table", aria-label="..."`.

### Validation
`check_figure_accessibility(fig)` — checks for alt_text in Plotly meta or title in matplotlib axes. Returns `{"accessible": bool, "issues": [...]}`.

---

## Anti-Patterns (NEVER)
1. Inline plotting — all plots must be functions
2. Hardcoded colors — use theme constants
3. No error handling — every function catches errors
4. No validation — validate data before plotting
5. No alt text — every figure needs accessibility metadata
6. Spaghetti callbacks — use component pattern
7. Raw data in dashboard — use pre-computed cache
8. No loading states — show spinners
9. Inconsistent sizing — use theme constants
10. No testing — validate figures and test dashboards

---

## Validation Checklist
- [ ] Uses theme module (viz_theme.py)
- [ ] All plots are functions
- [ ] Data validated before plotting
- [ ] Error handling in all functions
- [ ] No hardcoded colors, sizes, or paths
- [ ] Component-based dashboard architecture
- [ ] CSS follows design system
- [ ] Proper labels and titles
- [ ] Alt text on every figure
- [ ] Cached data, lazy loading
- [ ] Validation functions pass

---

## Dashboard Smoke Test

**Requires:** `pip install dash[testing]`

Do NOT call `app.layout` directly — this does not trigger callbacks. Use one of these approaches:

### Option 1: Layout value (quick check)
```python
from app import app
layout = app._layout_value()  # Returns the resolved layout tree
assert layout is not None
```

### Option 2: Dash testing (full callback test)
```python
from dash.testing.application_runners import DashRunner
from app import app

runner = DashRunner()
with runner(app) as drv:
    drv.wait_for_element("#main-content")
    assert drv.find_element("#main-content").is_displayed()
```

### Option 3: pytest-dash (CI-friendly)
```python
def test_dashboard_loads(dash_duo):
    from app import app
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#main-content")
    assert dash_duo.find_element("#main-content").is_displayed()
```
""",
    "viz_bokeh": """# Skill: High-Performance Interactive Plots with Bokeh

## Purpose
Bokeh is a powerful library for creating interactive, browser-ready visualizations. It excels at handling very large or streaming datasets and supports custom JavaScript callbacks for low-latency client-side interaction.

## Installation
```bash
pip install bokeh
```

## Protocol & Best Practices
1. **Always Use ColumnDataSource:** Bind data to a `ColumnDataSource` to enable seamless hover tooltips, selections, and synchronization.
2. **Explicitly Configure Tools:** Enable specific tools (e.g., pan, box_zoom, wheel_zoom, reset, hover, save) and disable unnecessary ones.
3. **Format Tooltips Nicely:** Use HTML/CSS within `HoverTool` to present high-density, readable hover cards.
4. **Theme Alignment:** Apply a consistent theme (background colors, grid line patterns, fonts) matching the project design system.

## Code Template

```python
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.io import output_file
import pandas as pd

def create_bokeh_scatter(df: pd.DataFrame, x_col: str, y_col: str, label_col: str, output_path: str):
    output_file(output_path)
    
    source = ColumnDataSource(df)
    
    # Setup hover tools
    hover = HoverTool(tooltips=\"\"\"
        <div style="padding: 5px; font-family: sans-serif;">
            <strong>@{%s}</strong><br>
            %s: @{%s}{0.00}<br>
            %s: @{%s}{0.00}
        </div>
    \"\"\" % (label_col, x_col, x_col, y_col, y_col))
    
    p = figure(
        title=f"{y_col.title()} vs {x_col.title()}",
        x_axis_label=x_col.replace("_", " ").title(),
        y_axis_label=y_col.replace("_", " ").title(),
        tools=["pan,box_zoom,wheel_zoom,reset,save", hover],
        width=600,
        height=400
    )
    
    # Styled according to project rules
    p.background_fill_color = "#FAFAFA"
    p.grid.grid_line_color = "#E5E5E5"
    
    p.circle(
        x=x_col, 
        y=y_col, 
        size=10, 
        source=source, 
        color="#0072B2", 
        alpha=0.7, 
        hover_color="#D55E00"
    )
    
    return p
```
""",
    "viz_venn": """# Skill: Venn Diagram Set Overlap Plotting

## Purpose
Set overlap visualization displays relationships, intersections, and exclusive counts across multiple categorical lists or cohorts. It provides structured insights into sample similarities, gene enrichment overlap, or feature overlap.

## Installation
```bash
pip install matplotlib-venn
```

## Protocol & Best Practices
1. **Limit Sets to Three:** Venn diagrams become unreadable and lose proportional geometric meaning when representing more than 3 sets. For 4 or more sets, use UpSet plots (`upsetplot`) instead.
2. **Always Use Proportional Layouts:** Use `venn2` and `venn3` to construct layouts where circle areas correspond proportionally to subset sizes.
3. **Okabe-Ito Colors:** Style overlapping areas using transparency and colors from the project palette.

## Code Template

```python
import matplotlib.pyplot as plt
from matplotlib_venn import venn3
from typing import Set

def plot_cohort_overlap(set_a: Set[Any], set_b: Set[Any], set_c: Set[Any], 
                        label_a: str, label_b: str, label_c: str, output_path: str):
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Custom palette
    color_a = "#E69F00"
    color_b = "#56B4E9"
    color_c = "#009E73"
    
    v = venn3(
        [set_a, set_b, set_c],
        set_labels=(label_a, label_b, label_c),
        ax=ax
    )
    
    # Apply theme styling
    if v.get_patch_by_id('100'): v.get_patch_by_id('100').set_color(color_a)
    if v.get_patch_by_id('010'): v.get_patch_by_id('010').set_color(color_b)
    if v.get_patch_by_id('001'): v.get_patch_by_id('001').set_color(color_c)
    
    # Add titles and labels
    ax.set_title("Cohort Sample Overlap Analysis", fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
```
""",
    "dashboard_overview": """---
skill_id: "dashboard_overview"
version: "8.0.0"
category: "visualization"
domain_compatibility: ["all"]
required_tools: ["python", "dash", "plotly", "dash-bootstrap-components", "pandas"]
depends_on: ["viz_design_system", "viz_code_standards", "figure_descriptive", "figure_inferential"]
produces:
  - "reports/dashboards/overview_dashboard.py"
  - "reports/dashboards/components/"
  - "reports/dashboards/assets/custom.css"
complexity: "advanced"
---

# Skill: Interactive Overview Dashboard

## Purpose
Generate a publication-grade interactive dashboard integrating all research outputs. Component-based architecture, responsive design, accessibility.

## When to Use
- After all analysis completed
- Interactive exploration, sharing with collaborators, conference presentations

## When NOT to Use
- Only static reports needed, analysis incomplete, data under NDA

---

## Architecture

### File Structure
```
reports/dashboards/
  overview_dashboard.py       # Main app (≤200 lines)
  components/
    cards.py, charts.py, tables.py, filters.py, layout.py
  assets/custom.css
  data/dashboard_cache.parquet
```

### Design Rules
1. Main app ≤200 lines — all logic in component files
2. No raw data loading in callbacks — use pre-computed parquet cache
3. Every component is a function returning a Dash component
4. Theme applied globally via `viz_theme.py`
5. Bootstrap 12-column responsive grid
6. Loading spinners on every callback

---

## Tab Structure

### Tab 1: Overview
Metric cards (N obs, variables, results, significant findings, effect size range), main finding visualization, correlation heatmap of key variables, research questions summary table with status.

### Tab 2: Data Explorer
Dataset selector dropdown, variable selector, filter panel with live N counter, variable distribution plot, bivariate plot (X vs Y), paginated/sortable/filterable data table.

### Tab 3: Results
Question selector, method selector, forest plot (effect sizes + CIs), sortable results table with columns: Variable, Estimate, 95% CI, p, Adjusted p.

### Tab 4: Diagnostics
Model selector, 2×3 grid: Residuals vs Fitted, Q-Q Plot, Scale-Location, Cook's D, VIF Values, Missingness Pattern.

---

## Component Specifications

- **Metric card**: `create_metric_card(title, value, subtitle, color, icon, trend)` — standardized card with semantic color
- **Chart container**: `create_chart_container(figure, title, footer, height)` — wraps any Plotly figure in a card with loading state
- **Filter panel**: `create_filter_panel(filters, id_prefix)` — generates dropdown, range slider, date picker, checkbox controls

## Interactive Features
- Variable multi-select, subgroup filter, numeric range sliders, method selector, live N counter
- PNG export per figure, CSV export for tables, PDF report via WeasyPrint
- Tooltips for statistical terms, variable descriptions, method info

## Styling
Use Bootstrap FLATLY or LUX theme, Okabe-Ito palette, Inter font, 12-column grid, card shadows on hover. NEVER use default Plotly colors, inline CSS, hardcoded sizes, >8 colors per figure, 3D/pie charts.

## Accessibility
All figures have `aria-label`, color is never the only differentiator, keyboard navigation works, WCAG AA contrast (4.5:1 minimum), screen reader can navigate tabs.

---

## Generate Static Export

After building the Dash app, export each figure as standalone HTML and assemble into `dashboard_static.html`:

1. **Extract figures**: Call each component's figure-building function directly (bypass Dash callbacks). Use `plotly.io.to_html(fig, include_plotlyjs='cdn', full_html=False)` for each figure.

2. **Jinja2 template**: Create a template with sections for Overview (summary cards), Results (main_finding, correlation_heatmap, forest_plot), and Diagnostics (residuals_plot). Use `{{ fig_html | safe }}` to embed Plotly HTML. Include Plotly CDN in `<head>`.

3. **Assemble**: Render template with figures dict, summary_cards list, and timestamp. Write to `reports/dashboards/dashboard_static.html`.

4. **Usage**: `generate_static_export(app, data_cache_path, output_dir, summary_cards)` — call after Dash app is built. Output is shareable without Python, interactive via Plotly CDN.

---

## Validation
- [ ] Main app ≤200 lines
- [ ] All components are functions in separate files
- [ ] No raw data loading in callbacks
- [ ] Design system theme applied globally
- [ ] All 4 tabs render without errors
- [ ] Filters update figures correctly
- [ ] Download buttons functional
- [ ] Loading states shown during computation
- [ ] Accessibility: alt text, contrast, keyboard nav
- [ ] Static export generates valid HTML
""",
    "viz_panel": """# Skill: Dashboard App Development with Panel

## Purpose
Panel provides a Pythonic way to build interactive dashboards and web applications that connect widgets to plots, tables, and computations. It supports any plotting backend and can run both in Jupyter Notebooks and standalone web servers.

## Installation
```bash
pip install panel
```

## Protocol & Best Practices
1. **Component-Based Architecture:** Write dashboards as modular component groups. Avoid single-file monolithic layouts.
2. **Use Reactive Classes:** Leverage `param.Parameterized` or `pn.depends` to bind widget states to rendering functions automatically.
3. **Use Markdown/HTML Templates:** Use native layout features like `pn.Row`, `pn.Column`, and custom HTML templates to make dashboards look premium and clean.

## Code Template

```python
import panel as pn
import pandas as pd
import param
import plotly.express as px

pn.extension()

class ResearchExplorer(param.Parameterized):
    # Setup interactive parameters
    x_metric = param.Selector(objects=[])
    y_metric = param.Selector(objects=[])
    color_by = param.Selector(objects=[])
    
    def __init__(self, df: pd.DataFrame, **params):
        super().__init__(**params)
        self.df = df
        
        # Populate selector parameters dynamically
        cols = list(df.select_dtypes(include='number').columns)
        cat_cols = list(df.select_dtypes(exclude='number').columns)
        
        self.param.x_metric.objects = cols
        self.param.y_metric.objects = cols
        self.param.color_by.objects = cat_cols
        
        # Set default values
        if cols:
            self.x_metric = cols[0]
            self.y_metric = cols[-1] if len(cols) > 1 else cols[0]
        if cat_cols:
            self.color_by = cat_cols[0]

    @pn.depends('x_metric', 'y_metric', 'color_by')
    def view_plot(self):
        fig = px.scatter(
            self.df, 
            x=self.x_metric, 
            y=self.y_metric, 
            color=self.color_by,
            title=f"Plot of {self.y_metric} vs {self.x_metric} color-coded by {self.color_by}"
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig

def build_dashboard(df: pd.DataFrame) -> pn.layout.Column:
    explorer = ResearchExplorer(df)
    
    dashboard = pn.Column(
        pn.pane.Markdown("# Research Explorer Dashboard"),
        pn.Row(
            pn.Column(
                pn.Param(explorer.param, widgets={
                    'x_metric': pn.widgets.Select,
                    'y_metric': pn.widgets.Select,
                    'color_by': pn.widgets.Select
                }),
                width=250
            ),
            explorer.view_plot,
        )
    )
    return dashboard
```
""",
}
