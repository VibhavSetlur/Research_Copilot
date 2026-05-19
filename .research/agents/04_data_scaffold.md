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

### Step 2: Validate
Run `validate_schema`. Check all required variables exist, types match, ranges plausible.

### Step 3: Transform
Apply only needed transformations:
- Missing data handling (per missingness mechanism)
- Outlier handling (per classification)
- Encoding, scaling, transformation (per analysis plan)

### Step 4: Execute
Write and run `analysis/01_validation.py`. Verify output. Compute hashes.

### Step 5: Data Dictionary
Document each variable: name, type, description, transformations, missingness handling.

---

## Validation

- [ ] All research map variables present in processed data
- [ ] Transformations justified
- [ ] Validation script runs without errors
- [ ] Hashes recorded
