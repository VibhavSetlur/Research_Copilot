# Data Inventory

> Describe each file in `inputs/data/raw/`. The system will scan them automatically, but your notes help it understand context.

---

## Files

### [filename.csv]
- **What it contains**: [description]
- **Approximate size**: [rows × columns]
- **Key identifiers**: [patient_id, survey_id, etc.]
- **Time period**: [if applicable]
- **Known issues**: [missing values, inconsistencies, encoding problems, etc.]
- **How it was collected**: [survey, EHR, sensor, public dataset, etc.]

---

## Relationships Between Files

> If files need to be joined, describe how.

- [File A] and [File B] can be joined on [column name]
- [File C] is a subset of [File A] filtered by [condition]

---

## Data Preparation Needed

> What cleaning or transformation does the data need before analysis?

- [e.g., "Dates are in mixed formats — need to standardize"]
- [e.g., "Variable 'age' is sometimes in years, sometimes in months"]
- [e.g., "Need to merge 3 files on patient_id"]
- [e.g., "Survey responses need reverse-coding for items 3, 7, 12"]
