---
agent_id: "compile_outputs"
version: "9.0.0"
description: "Assemble manuscript grounded in research map"
domain_compatibility: ["all"]
depends_on: ["execute_analysis"]
composes:
  - "write_imrad"
  - "write_executive_summary"
  - "interpret_effect_sizes"
  - "generate_apa_tables"
produces:
  - "reports/manuscript/research_findings.md"
  - "reports/manuscript/executive_summary.md"
  - "reports/manuscript/references.bib"
  - "reports/tables/"
max_iterations: 1
---

# Agent: Compile Outputs

## Purpose
Assemble the manuscript. Every claim traces to the research map, data, or literature.

---

## Protocol

### Step 1: Introduction
Context from research map's domain and literature. Gap from literature synthesis. Question and hypothesis from research map.

### Step 2: Methods
Design, data, variables from research map. Analysis from analysis plan with citations.

### Step 3: Results
Organize by research question (not by method). For each: finding with effect size + CI, comparison to literature, robustness assessment.

### Step 4: Discussion
Interpret findings. Compare to literature corpus. Honest limitations. Implications grounded in user's success criteria.

### Step 5: Abstract
No claims stronger than the data supports.

### Step 6: Executive Summary
Plain-language version.

### Step 7: Final Assembly
Run `write_imrad`. Cross-check: every citation has a reference, every claim is grounded.

### Step 8: Critic Review
- Trigger the `critic` agent to perform adversarial review of the compiled manuscript, executive summary, and tables.
- Verify that there is no scope creep or causal overclaiming, that references match citations, and that data claims are aligned.
- If the critic verdict is FAIL, execute remediation steps via `research_iterate`.

---

## Validation

- [ ] Results organized by research question
- [ ] Every literature claim cited
- [ ] Effect sizes interpreted
- [ ] Limitations stated
- [ ] No causal overclaiming
- [ ] Critic agent report generated with PASS verdict

