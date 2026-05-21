---
skill_id: "methods_checklist"
version: "1.0.0"
category: "writing"
depends_on: ["compile_outputs"]
produces: ["03_synthesis/methods_checklist.md"]
complexity: "quick"
---

# Skill: Methods Checklist

## Purpose
Generate a pre-submission checklist mapped to the reporting standard. Each item: requirement, status (yes/no/partial), location in manuscript if yes.

---

## Protocol

### Step 1: Detect Reporting Standard
From domain config or study design:
- Observational cohort/case-control → **STROBE** (22 items)
- Randomized trial → **CONSORT** (25 items)
- Systematic review → **PRISMA** (27 items)
- APA empirical study → **APA JARS** (18 items)
- Diagnostic accuracy → **STARD** (30 items)
- Default → **APA** general

### Step 2: Scan Manuscript
Read `03_synthesis/manuscript/`. For each checklist item, search for evidence:
- **Yes**: keyword/phrase found in manuscript (note section and line)
- **Partial**: partial evidence (e.g., mentions limitation but no sensitivity analysis)
- **No**: no evidence found

### Step 3: Generate Checklist
Format as markdown table:

| # | Requirement | Status | Location | Notes |
|---|------------|--------|----------|-------|
| 1 | Study design stated | Yes | Methods, para 1 | "prospective cohort" |
| 2 | Setting described | Yes | Methods, para 2 | Location, dates |
| 3 | Participants eligibility | Partial | Methods, para 3 | Inclusion stated, exclusion missing |

### Step 4: Summary
At end: "X of Y items met, Z partial, W missing." List missing items as action items.

---

## STROBE Key Items (22 total)
Title/abstract, background, objectives, study design, setting, participants, variables, data sources, bias, study size, quantitative variables, statistical methods, participants flow, descriptive data, outcome data, main results, other analyses, key results, limitations, interpretation, generalizability, funding.

## CONSORT Key Items (25 total)
Title/abstract, background, trial design, participants, interventions, outcomes, sample size, randomization, blinding, statistical methods, participant flow, recruitment, baseline data, numbers analyzed, outcomes/estimation, ancillary analyses, harms, limitations, generalizability, interpretation, trial registration, protocol access, funding.

## PRISMA Key Items (27 total)
Title, abstract, rationale, objectives, eligibility, information sources, search strategy, selection process, data collection, items, risk of bias, synthesis methods, reporting bias, certainty assessment, study selection, study characteristics, risk of bias in studies, results of syntheses, reporting biases, certainty of evidence, discussion, limitations, conclusions, registration, protocol, support, competing interests.

---

## Validation
- [ ] Reporting standard detected
- [ ] All checklist items evaluated
- [ ] Each item has status (yes/no/partial)
- [ ] Yes/partial items have manuscript location
- [ ] Summary counts provided
- [ ] Missing items listed as action items
- [ ] Output saved to `03_synthesis/methods_checklist.md`
