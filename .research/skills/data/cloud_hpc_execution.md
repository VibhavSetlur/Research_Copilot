---
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

query = """
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
"""

df = conn.cursor().execute(query).fetch_pandas_all()
df.to_parquet("data/03_analytical/aggregated_data.parquet")
```

#### Option B: PySpark (Distributed Compute)

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder \
    .appName("Research Analysis") \
    .config("spark.sql.adaptive.enabled", "true") \
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
