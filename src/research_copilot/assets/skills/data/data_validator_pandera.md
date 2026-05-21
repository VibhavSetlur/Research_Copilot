---
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
