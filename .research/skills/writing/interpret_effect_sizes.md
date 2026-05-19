---
skill_id: "interpret_effect_sizes"
version: "7.0.0"
category: "writing"
domain_compatibility: ["all"]
required_tools: ["python"]
depends_on: ["inferential_parametric", "inferential_nonparametric"]
produces: ["reports/effect_size_interpretation.md"]
complexity: "intermediate"
---

# Skill: Interpret Effect Sizes

## Purpose
Translate statistical effect sizes into substantive, domain-meaningful interpretations with practical significance assessments.

## When to Use
- After inferential analysis
- Before writing discussion
- To avoid over-reliance on p-values

## When NOT to Use
- Only p-value reporting needed (not recommended)
- Effect sizes not computed

## Execution Protocol

### Step 1: Effect Size Classification
| Metric | Trivial | Small | Medium | Large | Very Large |
|--------|---------|-------|--------|-------|------------|
| Cohen's d | < 0.10 | 0.10-0.30 | 0.30-0.50 | 0.50-0.80 | > 0.80 |
| Pearson's r | < 0.05 | 0.05-0.10 | 0.10-0.30 | 0.30-0.50 | > 0.50 |
| R² | < 0.01 | 0.01-0.06 | 0.06-0.14 | 0.14-0.26 | > 0.26 |
| Odds Ratio | ~1.0 | 1.2-1.5 | 1.5-2.5 | 2.5-4.0 | > 4.0 |
| η² | < 0.01 | 0.01-0.06 | 0.06-0.14 | 0.14-0.26 | > 0.26 |

### Step 2: Contextual Interpretation
- Compare to prior literature: is this effect typical, larger, or smaller?
- Practical significance: what does this mean in real-world terms?
- Clinical/policy significance: does it meet minimal important difference?
- Cost-benefit: is the effect large enough to justify intervention cost?

### Step 3: Precision Assessment
- CI width: narrow = precise, wide = uncertain
- Does CI include trivial effects? If yes, result is inconclusive
- Does CI exclude meaningful effects? If yes, result supports null

### Step 4: Reporting
- Report effect size with CI and qualitative interpretation
- Avoid: "significant" without effect size
- Avoid: "no effect" when CI includes meaningful effects
- Use: "the effect was [magnitude], meaning [substantive interpretation]"

## Output Specification
- `reports/effect_size_interpretation.md`: effect size interpretations with contextual comparisons

## Validation Checks
- [ ] All effect sizes classified
- [ ] CI-based precision assessment done
- [ ] Practical significance discussed
- [ ] Comparison to literature included
