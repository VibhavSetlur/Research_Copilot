---
agent_id: "execute_analysis"
version: "9.0.0"
description: "Run analysis plan, compare findings to literature, test robustness"
domain_compatibility: ["all"]
depends_on: ["data_scaffold"]
composes:
  - "descriptive_stats"
  - "inferential_parametric"
  - "inferential_nonparametric"
  - "causal_inference"
  - "bayesian_modeling"
  - "mixed_effects"
  - "survival_analysis"
  - "time_series_analysis"
  - "spatial_analysis"
  - "network_analysis"
  - "nlp_analysis"
  - "dimensionality_reduction"
  - "clustering"
produces:
  - "analysis/03_analytical/"
  - "reports/figures/"
  - "reports/tables/"
  - "reports/logs/methods_log.md"
max_iterations: 2
---

# Agent: Execute Analysis

## Purpose
Run the analysis plan. Compare every finding to the literature. Test robustness.

---

## Protocol

### Step 1: Descriptives
Run `descriptive_stats`. Compare distributions to what the user expected. Flag surprises.

### Step 2: Test Assumptions
For each method in the analysis plan: test assumptions using `assumption_registry.json`.
If one fails → use fallback. Log it.

### Step 3: Primary Analysis
Generate scripts in the correct runtime (`.py`, `.R`, `.sh`, `.nf`, `.jl`) and execute via `executor.py`.
Never invent command syntax; pull it from `tool_registry.json`.
Map result to the research question: supports or contradicts hypothesis? Compare effect size to literature expectations.

### Step 4: Sensitivity (only if primary finding is significant)
Test robustness: different outlier treatment, different missing data handling, different model spec. Record which checks support vs weaken the finding.

### Step 5: Compare to Literature
For the primary finding: find 2-3 papers from the literature corpus with similar or contradictory results. Explain convergence or divergence.

### Step 6: Assess Against Success Criteria
Did the user's minimum success criteria get met? Report honestly.

### Step 7: Generate Outputs
Figures, tables, methods log. Organize results by research question, not by method.

### Step 8: Critic Review
- Trigger the `critic` agent to perform adversarial review of the statistical outputs, figures, and tables.
- Verify logical consistency, data grounding, and that limitations or statistical uncertainty (CIs, p-values) are reported correctly.
- If the critic verdict is FAIL, execute remediation steps via `research_iterate`.

---

## Validation

- [ ] Primary question answered
- [ ] Assumptions tested
- [ ] Sensitivity tests run (if finding significant)
- [ ] Finding compared to ≥ 2 literature sources
- [ ] Results organized by research question
- [ ] Critic agent report generated with PASS verdict

