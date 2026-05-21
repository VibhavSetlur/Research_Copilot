---
skill_id: "policy_brief"
version: "1.0.0"
category: "writing"
depends_on: ["abstract_generator", "results_table_generator"]
produces: ["03_synthesis/policy_brief.md", "03_synthesis/policy_brief.html"]
complexity: "quick"
---

# Skill: Policy Brief Generator

## Purpose
2-page policy brief for decision-makers. Zero jargon. Action-focused. Distinct from executive_summary — shorter and recommendation-driven.

---

## Protocol

### Step 1: Gather Inputs
`key_findings.json`, method summary, effect sizes, sample info, one key figure.

### Step 2: Generate Structure

**Headline Finding** (1 sentence): The single most important result, stated in plain language with one key number.

**Context** (~50 words): What problem does this address? Why does it matter now? No academic framing.

**Evidence** (3 bullets): Each bullet: finding + effect size in plain terms + practical implication. Example: "Program participants earned 12% more ($2,400/year) than non-participants, with effects largest for first-generation workers."

**Recommendations** (3 bullets): Action-oriented, specific, grounded in evidence. Each ties to a specific finding. Example: "Expand eligibility to first-generation workers, where effects are 2× larger."

**Caveats** (2 bullets): Honest limitations that affect implementation. Example: "Results based on one state; effects may differ in rural areas."

### Step 3: Generate Markdown
Format with clear headings, bullet lists, one embedded figure with caption. Total: ~400 words, fits on 2 pages.

### Step 4: Generate HTML
Print-ready HTML with clean typography, page break after first page, figure centered, footer with source citation. `@media print` rules for clean printing.

### Step 5: Quality Rules
- Zero jargon: no "regression," "p-value," "coefficient," "heteroscedasticity"
- Use plain numbers: "12% more" not "β = 0.12"
- Every claim traceable to a source file
- One figure maximum — the most policy-relevant one
- Recommendations must be grounded in findings, not speculation

---

## Output
- `03_synthesis/policy_brief.md` — Markdown source
- `03_synthesis/policy_brief.html` — Print-ready HTML

## Validation
- [ ] Headline finding is 1 sentence
- [ ] Context ≤ 50 words
- [ ] Exactly 3 evidence bullets with effect sizes
- [ ] Exactly 3 recommendations
- [ ] Exactly 2 caveats
- [ ] Zero statistical jargon
- [ ] One figure included
- [ ] Every claim has source file
- [ ] Total ≤ 400 words
