---
agent_id: "generate_preregistration"
version: "1.0.0"
description: "Generate OSF-compatible pre-registration document after method_route, before execute_analysis"
domain_compatibility: ["all"]
depends_on: ["method_route"]
composes: []
produces:
  - "reports/literature/preregistration_{timestamp}.md"
  - "reports/literature/preregistration_{timestamp}.json"
max_iterations: 1
---

# Agent: Generate Pre-Registration

## Purpose

The gold standard in modern research is pre-registration — documenting hypotheses, methods, and analysis plans BEFORE seeing the results. This agent generates an exact, timestamped document matching the Open Science Framework (OSF) template.

This prevents:
- HARKing (Hypothesizing After Results are Known)
- P-hacking and data dredging
- Selective reporting of significant results
- Post-hoc method switching

## Placement in Pipeline

This agent runs AFTER `method_route` (when methods are selected) and BEFORE `execute_analysis` (when results are generated).

```
research_init → literature_deep → method_route → generate_preregistration → data_scaffold → execute_analysis → compile_outputs → audit_validate
```

## Protocol

### Step 1: Gather Required Information

Read the following files:
1. `inputs/intake.md` — research questions, hypotheses, variables
2. `reports/analysis/analysis_plan.md` — selected methods and tests
3. `docs/methodology.md` — methodological decisions and rationale
4. `reports/literature/evidence_matrix.md` — prior literature effect sizes
5. `.research/cache/state.json` — current pipeline state

### Step 2: Document Hypotheses

For each hypothesis:
1. State it clearly in directional form (if directional)
2. Specify the expected effect direction
3. Note the expected effect size (from literature or pilot data)
4. Specify the statistical test that will be used

### Step 3: Document the Analysis Plan

For each research question:
1. Primary analysis: exact statistical test, software, parameters
2. Covariates to be included (and why)
3. Handling of missing data
4. Exclusion criteria (if any)
5. Multiple comparison correction method

### Step 4: Document Power Analysis

Compute or estimate:
1. Target power: 0.80 (80%)
2. Minimum detectable effect size (from literature)
3. Required sample size for adequate power
4. Actual sample size available
5. Whether power is adequate (power_adequate: 0.80 threshold)

### Step 5: Generate Pre-Registration Document

Create `reports/literature/preregistration_{timestamp}.md` following the OSF template:

```markdown
# Pre-Registration Document

**Generated**: {timestamp}
**Project**: {title}
**Pre-Registration ID**: PREREG-{timestamp}

## 1. Research Questions
### Primary Research Question
[From intake]

## 2. Hypotheses
### Hypothesis 1
[Statement, expected direction, expected effect size]

## 3. Study Design
[Design type, data source, sample characteristics]

## 4. Variables
### Outcome Variable
[Name, measurement, scale]

### Key Predictors
[Names, measurement, scales]

### Control Variables
[Names and justification]

## 5. Power Analysis
[Power computation, MDES, required vs. actual sample size]

## 6. Statistical Analysis Plan
[Primary tests, covariates, missing data handling, exclusion criteria]

## 7. Robustness Checks
[Alternative specifications, subgroup analyses, sensitivity analyses]

## 8. Deviations Policy
[Any deviations will be documented in docs/changelog.md]

## 9. Significance Criteria
[Alpha level, one/two-tailed, multiple comparison correction]
```

### Step 6: Generate JSON Metadata

Create `reports/literature/preregistration_{timestamp}.json` with machine-readable metadata:

```json
{
  "preregistration_id": "PREREG-{timestamp}",
  "generated_at": "{ISO-8601}",
  "project": "{title}",
  "hypotheses": [...],
  "analysis_plan": {...},
  "power_analysis": {...},
  "osf_compatible": true
}
```

### Step 7: Update Pipeline State

Record the pre-registration in the state ledger:
```json
{
  "preregistration": {
    "id": "PREREG-{timestamp}",
    "path": "reports/literature/preregistration_{timestamp}.md",
    "timestamp": "{ISO-8601}",
    "hypotheses_count": N,
    "submitted_to_osf": false
  }
}
```

## Validation

- [ ] All hypotheses from intake documented
- [ ] Analysis plan matches method_route output
- [ ] Power analysis computed with power_adequate: 0.80 threshold
- [ ] Document is timestamped and immutable
- [ ] JSON metadata generated
- [ ] State ledger updated
- [ ] Document is OSF-compatible (can be submitted to osf.io/prereg/)
