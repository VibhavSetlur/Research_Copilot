---
agent_id: "data_scaffold"
version: "9.0.0"
description: "Build validated data pipeline from research map variables"
domain_compatibility: ["all"]
depends_on: ["research_init", "method_route"]
composes: ["validate_schema", "compute_hashes"]
produces:
  - "analysis/01_validation.py"
  - "data/02_processed/"
  - "reports/data_dictionary.md"
  - "environment/requirements.txt"
max_iterations: 1
---

# Agent: Data Scaffold

## Purpose
Transform raw data into analysis-ready format using only the variables the research map needs.

---

## Protocol

### Step 1: Load Research Map
Extract: outcome variables, predictors, covariates, missingness mechanism, outlier classification.

### Step 2: Format Router
Read `.research/cache/data_format_manifest.json` if present; otherwise run `research format-scan`.
Only apply Pandera to files marked `pandera_applicable: true`.

### Step 3: Validate
Run `validate_schema` for tabular files only. Check required variables exist, types match, ranges plausible.
For non-tabular formats, run domain-specific QC (e.g., FASTQ header check, NIFTI header check).

### Step 4: Transform
Apply only needed transformations:
- Missing data handling (per missingness mechanism)
- Outlier handling (per classification)
- Encoding, scaling, transformation (per analysis plan)

### Step 5: Execute
Write and run `analysis/01_validation.py`. Verify output. Compute hashes.

### Step 6: Tool Capability Check
Run `python .research/scripts/utils/tool_capability_check.py` and record `tool_availability_report.json`.
If critical tools are `MISSING_REQUIRES_CONTAINER`, stop and request user action.

### Step 7: Data Dictionary
Document each variable: name, type, description, transformations, missingness handling.

---

## Validation

- [ ] All research map variables present in processed data
- [ ] Transformations justified
- [ ] Validation script runs without errors
- [ ] Hashes recorded
