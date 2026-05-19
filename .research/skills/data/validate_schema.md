---
skill_id: "validate_schema"
version: "3.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "pandera", "pyyaml"]
estimated_tokens: 3000
depends_on: ["profile_tabular"]
produces: ["data/01_ingested/validation_results.json"]
---

# Skill: Schema Validation

## Purpose
Validate datasets against a target Pandera schema to enforce formatting, value range constraints, and database type safety.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_path` | Path | Yes | Path to dataset |
| `schema_path` | Path | Yes | Path to YAML schema file |

## Execution Protocol

### Step 1: Schema Loading
- Parse `schema_definition.yaml`. Convert parameters into a Pandera `DataFrameSchema` object.

### Step 2: Column & Type Checks
- Match column names exactly. Case-sensitive.
- Enforce strict type conversions (e.g. check string columns do not contain floats).

### Step 3: Range & Value Constraint Checks
- Enforce range boundaries (e.g. values must be between minimum and maximum bounds).
- Enforce categorical list checks (e.g. string values must match list options).
- Enforce regular expression matches on format strings (e.g., date formats).

### Step 4: Violation Extraction
- Execute validation catch blocks. If checks fail, capture detailed `SchemaErrors` mapping column name, error type, invalid value, and row index.

## Output Specification
Produces:
- `data/01_ingested/validation_results.json` mapping pass/fail status and violation lists.

## Validation Criteria
- [ ] Output JSON contains a top-level `passed` boolean.
- [ ] If `passed` is false, `errors` contains detailed lists of offending row indices.