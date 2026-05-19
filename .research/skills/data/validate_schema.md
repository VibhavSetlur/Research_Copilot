---
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
