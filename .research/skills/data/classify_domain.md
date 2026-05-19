---
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
