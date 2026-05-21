---
skill_id: "parse_research_brief"
version: "7.0.0"
category: "writing"
domain_compatibility: ["all"]
required_tools: ["python", "pyyaml"]
depends_on: []
produces: ["briefs/parsed_research_brief.json"]
complexity: "intermediate"
---

# Skill: Parse Research Brief

## Purpose
Extract structured research parameters from a natural language research brief: questions, variables, hypotheses, domain, and constraints.

## When to Use
- First step in any research pipeline
- When researcher provides a free-text brief
- Before any analysis or literature search

## When NOT to Use
- Research parameters already structured
- Only exploratory analysis with no specific question

## Execution Protocol

### Step 1: Question Extraction
- Identify primary research question(s)
- Classify question type: descriptive, comparative, associational, causal, predictive, exploratory
- Extract: independent variable(s), dependent variable(s), covariates

### Step 2: Hypothesis Formulation
- Extract stated hypotheses (directional or non-directional)
- If no hypothesis stated: generate null and alternative hypotheses
- Specify: expected effect direction and magnitude (if stated)

### Step 3: Domain & Context
- Identify research domain from keywords and variable names
- Extract: population of interest, setting, time period
- Identify: reporting standard (APA, STROBE, AEA, etc.)

### Step 4: Constraints & Preferences
- Extract: significance level preference (default α = 0.05)
- Extract: analysis method preferences (if any)
- Extract: output format preferences
- Note: any ethical constraints or data use restrictions

### Step 5: Validation
- Check: all required fields populated
- Check: variables referenced in hypotheses exist in data (if data available)
- Check: question type is answerable with available data
- Flag: ambiguities for researcher clarification

## Output Specification
- `briefs/parsed_research_brief.json`: structured brief with questions, hypotheses, variables, domain, constraints

## Validation Checks
- [ ] At least one research question identified
- [ ] Question type classified
- [ ] Variables mapped to roles (IV, DV, covariate)
- [ ] Domain identified
- [ ] Ambiguities flagged
