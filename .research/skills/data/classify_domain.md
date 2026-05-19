---
skill_id: "classify_domain"
version: "3.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "pandas", "yaml"]
estimated_tokens: 2500
depends_on: ["profile_tabular"]
produces: ["data/01_ingested/domain_classification.json"]
---

# Skill: Classify Domain

## Purpose
Analyze variables and structures to classify the scientific domain of a dataset, selecting relevant analytical pipelines.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `profile_path` | Path | Yes | Path to profile_tabular.json |

## Execution Protocol

### Step 1: Signature Extraction
- Load tabular profiles. Extract:
  - Column name tokens.
  - Value ranges.
  - Time interval frequency (if present).
  - Spatial columns.

### Step 2: Pattern Classification
- Compare signatures to domain templates:
  - **Epidemiology**: Presence of mortality/morbidity, survival time, patient ID, binary disease markers.
  - **Econometrics**: Presence of panels, panel units (state/country), time dimensions, continuous economic outputs (GDP/wage), instrumental variables.
  - **Genomics**: Presence of sequence data, gene names, chromosome identifiers, mutation codes.
  - **NLP**: High-variance text columns, word frequencies.
  - **Ecology**: Spatial coordinates, species listings, temperature/soil variables.

### Step 3: Output Classification
- Select the best domain match based on confidence scores.

## Output Specification
Produces:
- `data/01_ingested/domain_classification.json` containing classified domain and confidence scores.

## Validation Criteria
- [ ] Confidence score is bounded between 0 and 1.