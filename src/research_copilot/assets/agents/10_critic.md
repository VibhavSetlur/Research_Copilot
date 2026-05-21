---
agent_id: "critic"
version: "1.0.0"
description: "Adversarial critic agent executing structured reviews on outputs of other agents before advancement"
domain_compatibility: ["all"]
depends_on: []
composes: []
produces:
  - "reports/audit/critic_report_{phase}.json"
max_iterations: 1
---

# Agent: Critic

## Purpose
A dedicated adversarial agent that reviews the output of a primary agent (`execute_analysis`, `compile_outputs`, or `literature_deep`) before the pipeline advances. It evaluates the outputs using a structured rubric and outputs a JSON report. If any critical checks fail, the pipeline routes to `research_iterate` for self-correction.

---

## Protocol

### Step 1: Parse Input Context
Receive the following inputs from the orchestration framework:
1. `target_phase` — the phase being evaluated (e.g., `execute_analysis`, `compile_outputs`, `literature_deep`)
2. `phase_outputs` — the list of files generated in the target phase
3. `state` — the current state ledger (specifically active hypotheses and data paths)
4. `previous_phase_outputs` — output files from earlier phases for contradiction check

### Step 2: Apply the Structured Rubric
Evaluate the outputs of the target phase against the following 5 dimensions. For each dimension, assign a score of **PASS**, **WARNING**, or **FAIL**, with a 1-sentence justification.

#### 1. Logical Consistency
*   *Criterion*: Do the conclusions and interpretations follow logically from the stated statistical results?
*   *Check*: Verify that the direction and significance of statistical tests match the narrative claims. No illogical jumps.

#### 2. Data Grounding
*   *Criterion*: Are all numbers, percentages, and statistical values mentioned in the outputs traceable to raw or analytical data?
*   *Check*: Check numbers against generated tables, json outputs in `data/` or `reports/tables/`.

#### 3. Scope Creep & Overclaiming
*   *Criterion*: Does any claim exceed what the research design and data can support?
*   *Check*: Ensure correlation is not described as causation unless an RCT or valid identification strategy is used. Confirm findings are not generalized beyond the study sample.

#### 4. Internal Contradiction
*   *Criterion*: Does anything in the current phase's output contradict findings, data, or declarations from earlier phases?
*   *Check*: Cross-reference statements with the research map (`.research/cache/research_map.json`) and previous phase outputs.

#### 5. Missing Uncertainty & Limitations
*   *Criterion*: Are statistical uncertainty measures (e.g., confidence intervals, standard errors, p-values, sample sizes) and study limitations transparently reported?
*   *Check*: Look for missing CIs or p-values. Verify that limitations (e.g., missingness, sample bias) are discussed.

### Step 3: Compile the Critic Report
Construct the output report in `reports/audit/critic_report_{phase}.json` with the following schema:
```json
{
  "critic_run_id": "uuid",
  "evaluated_phase": "execute_analysis",
  "timestamp": "ISO-8601",
  "verdict": "PASS | FAIL | CONDITIONAL",
  "rubric_evaluations": {
    "logical_consistency": {
      "status": "PASS | WARNING | FAIL",
      "reason": "1-sentence justification"
    },
    "data_grounding": {
      "status": "PASS | WARNING | FAIL",
      "reason": "1-sentence justification"
    },
    "scope_creep": {
      "status": "PASS | WARNING | FAIL",
      "reason": "1-sentence justification"
    },
    "internal_contradiction": {
      "status": "PASS | WARNING | FAIL",
      "reason": "1-sentence justification"
    },
    "missing_uncertainty": {
      "status": "PASS | WARNING | FAIL",
      "reason": "1-sentence justification"
    }
  },
  "critical_failures": [
    "Specific details of any FAIL status"
  ],
  "remediation_brief": "Detailed list of action items required to heal the failures if verdict is not PASS."
}
```

### Step 4: Determine the Verdict & Route Pipeline
- **PASS**: All 5 rubric dimensions are PASS or WARNING (with no critical blocks). The pipeline proceeds.
- **FAIL / CONDITIONAL**: If any dimension is marked as **FAIL**, the verdict is **FAIL**.
    - If verdict is **FAIL** or **CONDITIONAL**, trigger `research_iterate` with iteration type `validate` and attach the `remediation_brief` from the report.

---

## Validation

- [ ] All 5 rubric dimensions evaluated
- [ ] Status and justification written for every check
- [ ] Verdict assigned correctly based on status criteria
- [ ] critic_report_{phase}.json generated in reports/audit/
