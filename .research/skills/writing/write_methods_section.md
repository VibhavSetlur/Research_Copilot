---
skill_id: "write_methods_section"
version: "3.0.0"
category: "writing"
domain_compatibility: ["all"]
required_tools: ["python", "openai|anthropic"]
estimated_tokens: 3000
depends_on: ["parse_research_brief"]
produces: ["docs/methods_section.md"]
---

# Skill: Write Methods Section (Academic Standards)

## Purpose
Generate a peer-reviewed standard Methodology section based on the append-only methods log, aligning with reporting guidelines (e.g., STROBE, PRISMA, AERA).

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `methods_log_path` | Path | Yes | Path to the methods log file |
| `domain_reporting` | Str | Yes | Reporting standard (e.g., 'STROBE', 'PRISMA', 'APA') |

## Execution Protocol

### Step 1: Sub-section Outlining
Structure the section into four standard academic components:
1. **Study Design & Context**: Type of study (observational, RCT, cohort), setting, and timeline.
2. **Participants & Ingestion**: Selection criteria, final sample size calculation, and exclusions applied.
3. **Measures & Variables**: Detailed operationalization of variables and scaling.
4. **Statistical Analysis**: Statistical models defined with equations, software package names, version pinning, and alpha thresholds.

### Step 2: Narrative Generation
- Translate technical command runs from `methods_log.md` into descriptive, formal English.
- Insert mathematical model specifications in LaTeX format (e.g., `$$Y_i = \beta_0 + \beta_1 X_i + \epsilon_i$$`).
- Document all tests run to verify statistical assumptions (e.g., Shapiro-Wilk, Levene's) and state justifications for non-parametric fallbacks.
- Specify significance level conventions: e.g., "All tests used a two-sided significance threshold of alpha = .05."

### Step 3: Software Logging
- Explicitly state the statistical libraries utilized with their exact versions parsed from the execution manifest (e.g., "analyses were performed using Statsmodels version 0.14.0").

## Output Specification
Produces:
- `docs/methods_section.md` containing formatted LaTeX and narrative.

## Validation Criteria
- [ ] Section contains explicit descriptions of outlier removal or missingness handling.
- [ ] Mathematical equations for primary models are present in LaTeX format.
- [ ] Version numbers for primary packages (e.g., Pandas, Scipy) are declared.