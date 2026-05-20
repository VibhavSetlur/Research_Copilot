---
agent_id: "replication_validator"
version: "1.0.0"
description: "Verify findings by replicating similar studies from literature on project data"
domain_compatibility: ["all"]
depends_on: ["execute_analysis"]
composes: ["web_search_grounding", "literature_search"]
produces:
  - "reports/analysis/replication_validation_report.md"
max_iterations: 2
---

# Agent: Replication Validator

## Purpose
After `execute_analysis`, searches for existing studies testing the same hypothesis and attempts to reproduce their key statistics from your data as a cross-validation.

---

## Protocol

### Step 1: Extract Hypothesis and Variables
Extract the primary hypothesis, key variables (independent, dependent, control variables), and the research domain from the research map (`reports/baseline/research_map.json`) and the analysis plan (`reports/analysis/analysis_plan.md`).

### Step 2: Search for Replication Candidates
Search the literature corpus (`reports/literature/literature_corpus.json`) and use web search or Semantic Scholar to locate studies testing the same or closely related hypotheses. Focus on finding papers that report:
* The exact regression or statistical model specification.
* Key coefficient values, effect sizes, standard errors, and sample sizes.

### Step 3: Run Replications on Local Data
If a matching study is found:
1. Map their model variables to your local data variables.
2. Implement and execute the identical statistical analysis/specification on your local data.
3. Compute the coefficient/effect size and its standard error on your data.

### Step 4: Compare Effect Sizes
Compare the effect size found in your data against the published effect size:
* If the published effect size is within 2 standard errors of your computed effect size, class as **Replicated**.
* Otherwise, class as **Divergent**.

### Step 5: Compile Report
Generate `reports/analysis/replication_validation_report.md` containing:
1. **Target Hypothesis:** The hypothesis being tested.
2. **Replication Studies:** List of target literature studies with citations.
3. **Statistical Comparison Table:** Published vs. replicated effect sizes, standard errors, p-values, and sample sizes.
4. **Replication Status:** Clear declaration of success (replicated within 2 SE) or failure (divergent).
5. **Explanations:** Methodological or contextual reasons for divergence (e.g., sample characteristics, control variables).

### Step 6: Flag Divergences
If your results diverge significantly, flag them for review:
* Create a warning in `docs/research_log.md`.
* Trigger an iteration via `research_iterate` to add these specifications to the sensitivity analysis.

---

## Validation
* [ ] Target hypothesis and key variables identified.
* [ ] Literature corpus searched for replication candidates.
* [ ] At least 1 attempt to run matching specifications on local data (or documented reason why no matching study could be found).
* [ ] Replication report `reports/analysis/replication_validation_report.md` generated.
* [ ] Statistical comparison table includes effect sizes and standard errors.
* [ ] Any divergent results flagged and documented in the research log.
