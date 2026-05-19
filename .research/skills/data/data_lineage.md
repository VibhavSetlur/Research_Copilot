---
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
      "path": "inputs/data/raw/survey.csv",
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
      "input_files": ["inputs/data/raw/survey.csv"],
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
    """Verify data pipeline is reproducible.
    
    Returns:
        dict with status, mismatches, recommendations
    """
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
