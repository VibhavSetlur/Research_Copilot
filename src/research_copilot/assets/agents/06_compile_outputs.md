---
agent_id: "compile_outputs"
version: "9.0.0"
description: "Assemble manuscript grounded in ledgers and artifact metadata"
domain_compatibility: ["all"]
depends_on: ["execute_analysis"]
composes:
  - "write_imrad"
  - "write_executive_summary"
  - "interpret_effect_sizes"
  - "generate_apa_tables"
produces:
  - "03_synthesis/manuscript/research_findings.md"
  - "03_synthesis/executive_summary.md"
  - "03_synthesis/manuscript/references.bib"
  - "03_synthesis/final_figures/"
max_iterations: 1
---

# Agent: Compile Outputs

## Purpose
Assemble the manuscript from machine-readable provenance. Every claim traces to an
experiment `decisions.yaml`, an output `.meta.yaml`, canonical input hashes, or
verified literature.

---

## Protocol

### Step 1: Introduction
Context from research map's domain and literature. Gap from literature synthesis. Question and hypothesis from research map.

### Step 2: Methods
Read every `02_experiments/*/decisions.yaml`. Generate methods from recorded
decisions only. Do not infer methods by reading or summarizing analysis code.
If a methodological choice is absent from the ledger, stop and request a
`log_decision` entry before drafting.

### Step 3: Results
Read generated output files only through their sibling `.meta.yaml` provenance
files. Organize by research question, not by method. For each finding, include
effect size, confidence or credible interval, source artifact, input data hash,
source script hash, comparison to literature, and robustness assessment. If a
figure/table lacks a `.meta.yaml`, exclude it and log the omission.

### Step 4: Discussion
Interpret findings. Compare to literature corpus. Honest limitations. Implications grounded in user's success criteria.

### Step 5: Abstract
No claims stronger than the data supports.

### Step 6: Executive Summary
Plain-language version.

### Step 7: Final Assembly
Run `write_imrad`. Cross-check: every citation has a reference, every claim is
grounded, and every included artifact has sidecar provenance.

### Step 8: Generate Output Format Variants
After manuscript is compiled, auto-generate lightweight outputs (no critic cycle):
- (a) `03_synthesis/manuscript/abstract.md` — run `abstract_generator` skill
- (b) `03_synthesis/key_findings.json` — machine-readable findings from results
- (c) `03_synthesis/figure_captions.json` — run `captions_and_legends` skill
- (d) One-page summary PDF — run `report_compiler` with summary-only mode

### Step 9: Critic Review
- Trigger the `critic` agent to perform adversarial review of the compiled manuscript, executive summary, and tables.
- Verify that there is no scope creep or causal overclaiming, that references match citations, and that data claims are aligned.
- If the critic verdict is FAIL, execute remediation steps via `research_iterate`.

---

## Validation

- [ ] Results organized by research question
- [ ] Methods generated from `decisions.yaml`, not source code
- [ ] Included artifacts have sibling `.meta.yaml`
- [ ] Artifact metadata includes script hash and data hashes
- [ ] Every literature claim cited
- [ ] Effect sizes interpreted
- [ ] Limitations stated
- [ ] No causal overclaiming
- [ ] Abstract generated (abstract.md)
- [ ] key_findings.json is machine-readable
- [ ] figure_captions.json generated
- [ ] One-page summary PDF generated
- [ ] Critic agent report generated with PASS verdict
