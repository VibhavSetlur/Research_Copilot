---
skill_id: "write_methods_section"
version: "7.0.0"
category: "writing"
domain_compatibility: ["all"]
required_tools: ["python", "openai|anthropic|litellm"]
depends_on: ["parse_research_brief", "detect_missingness"]
produces: ["reports/sections/methods_section.md"]
complexity: "intermediate"
---

# Skill: Write Methods Section

## Purpose
Generate a complete, domain-appropriate methods section covering study design, data, variables, analytical procedures, and ethical considerations.

## When to Use
- After analysis plan determined
- Before results section
- For manuscript assembly

## When NOT to Use
- Only results needed
- Methods already written

## Execution Protocol

### Step 1: Study Design Description
- Design type: cross-sectional, longitudinal, experimental, quasi-experimental, observational
- Setting: where and when data was collected
- Participants/sample: N, inclusion/exclusion criteria, recruitment method
- For experiments: randomization procedure, blinding, control condition

### Step 2: Data Description
- Data source: survey, administrative records, experimental, scraped, public dataset
- Time period: collection dates
- Variables: list with operational definitions
- Measurement instruments: validated scales, custom measures

### Step 3: Analytical Procedures
- Software: name and version
- Preprocessing: cleaning, transformation, imputation method
- Statistical tests: each test with rationale
- Model specifications: formula, covariates, interaction terms
- Assumption checks: which tests, results
- Multiple testing correction: method used
- Significance level: α threshold

### Step 4: Missing Data Handling
- Extent of missingness: per variable
- Mechanism: MCAR, MAR, or MNAR (with test results)
- Handling method: complete-case, imputation, weighting
- Sensitivity analysis: alternative methods tested

### Step 5: Ethical Considerations
- IRB approval: status and number
- Informed consent: obtained or waived
- Data privacy: anonymization, secure storage
- Conflicts of interest: declared or none

## Reporting Standards by Domain
| Domain | Standard | Required Elements |
|--------|----------|------------------|
| Medicine/Epi | STROBE | Flow diagram, confounder justification |
| Psychology | APA 7th | Reliability coefficients, manipulation checks |
| Economics | AEA | Data availability statement, pre-registration |
| Education | AERA | Sampling frame, response rate |

## Output Specification
- `reports/sections/methods_section.md`: complete methods section

## Validation Checks
- [ ] All analysis methods described
- [ ] Software and versions specified
- [ ] Missing data handling documented
- [ ] Ethical considerations addressed
- [ ] Domain reporting standard followed
