---
skill_id: "onboarding_guide"
version: "1.0.0"
category: "core"
depends_on: []
produces: ["user understanding"]
complexity: "quick"
---

# Skill: Onboarding Guide

## Purpose
Walk a new user through their first analysis in 5 steps. No pipeline knowledge required — just describe your research in plain English.

---

## 5-Step First Analysis

### Step 1: Drop Your Data
Place your data file(s) in `00_inputs/raw_data/`. Supported formats: CSV, TSV, Parquet, Excel (.xlsx), Stata (.dta), SPSS (.sav). No preprocessing needed — we handle encoding, delimiters, and type detection automatically.

### Step 2: Fill in 3 Required Fields
Open `inputs/intake.md` and fill in only these 3 fields:
- **Title**: What is this project called?
- **Question**: What do you want to find out?
- **Outcome variable**: What is the main thing you're measuring?

Everything else is optional. The system will infer domain, predictors, and methods from your data.

### Step 3: Say "Analyze My Data"
That's it. You don't need to know about profiling, assumption checking, or method selection. The system will:
1. Profile your data automatically
2. Detect variable types and missingness
3. Route to appropriate analysis methods
4. Run the analysis
5. Generate figures and tables

### Step 4: Review Key Findings
Open `03_synthesis/key_findings.md`. This contains:
- Summary of what the data shows
- Statistical results with effect sizes and confidence intervals
- Key figures with interpretations
- Limitations and caveats

### Step 5: Ask Follow-Up Questions
Not satisfied? Ask in plain English:
- "Why did we get this result?" → investigates
- "Try a different method" → switches methods
- "What if we control for X?" → adds variables
- "Check if this holds up" → robustness checks
- "How does this compare to literature?" → literature comparison
- "What else is in the data?" → exploratory analysis

---

## You Don't Need to Know the Pipeline

The system handles:
- Data profiling and quality checks
- Statistical assumption testing
- Method selection and routing
- Figure generation (colorblind-safe, publication-ready)
- Manuscript compilation
- Citation verification
- Audit and validation

Just describe your research. We handle the rest.

---

## Validation
- [ ] User placed data in `00_inputs/raw_data/`
- [ ] User filled 3 required intake fields
- [ ] User triggered analysis
- [ ] Key findings generated
- [ ] User able to ask follow-up questions
