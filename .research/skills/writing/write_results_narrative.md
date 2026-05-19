---
skill_id: "write_results_narrative"
version: "3.0.0"
category: "writing"
domain_compatibility: ["all"]
required_tools: ["python", "openai|anthropic"]
estimated_tokens: 3000
depends_on: ["interpret_effect_sizes"]
produces: ["docs/results_section.md"]
---

# Skill: Write Results Narrative (APA Guidelines)

## Purpose
Write a rigorous, narrative results section integrating statistics, effect sizes, and figure citations following standard APA guidelines.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `interpreted_results_path` | Path | Yes | Path to results_interpreted.json |
| `figures_manifest_path` | Path | Yes | Path to generated figures directory/list |

## Execution Protocol

### Step 1: Statistical Reporting Formatting
Format all statistics in strict compliance with APA 7th edition rules:
- **Italicize symbols**: *p*, *F*, *t*, *df*, *r*, *N*, *d*, *OR*, *b*.
- **Decimal Precision**: Report means, standard deviations, and test statistics to two decimal places (e.g., *t*(24) = 3.42). Report *p*-values to three decimal places (e.g., *p* = .012).
- **P-Value Decimal Rule**: Never report a p-value with a leading zero (e.g., write `p = .04` not `p = 0.04`). Write `p < .001` instead of `p = .000` or `p = 0.00`.
- **Confidence Intervals**: Always report confidence intervals in brackets alongside effect sizes: e.g., "Cohen's *d* = 0.45, 95% CI [0.12, 0.78]".

### Step 2: Narrative Generation
- Organize narrative chronologically, mirroring the hypotheses stated in the brief.
- Provide descriptive baselines first (e.g., "The final sample size was *N* = 432...").
- Report significant positive findings, significant negative findings, and null/insignificant findings with equal objectivity.
- Integrate the qualitative effect size descriptors derived from `interpret_effect_sizes`.

### Step 3: Citation Placement
- Insert explicit references to tables and figures before discussing the values in detail (e.g., "As illustrated in Figure 1, group means differed...").

## Output Specification
Produces:
- `docs/results_section.md`

## Validation Criteria
- [ ] No *p*-values contain a leading zero.
- [ ] Statistical symbols are correctly formatted (italicized).
- [ ] Every statistical test includes a point estimate, degrees of freedom (where applicable), *p*-value, and 95% CI bounds.