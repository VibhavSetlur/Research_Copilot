---
skill_id: "eli5_explainer"
version: "1.0.0"
category: "writing"
description: "Generate layman-friendly explanations of research findings, assumptions, and statistical concepts"
domain_compatibility: ["all"]
applies_to_phases: ["execute_analysis", "compile_outputs"]
---

# Skill: ELI5 Explainer (Explain Like I'm 5)

## Purpose

Generate beginner-friendly explanations alongside technical research outputs. This skill ensures that research findings are accessible to non-experts, students, and stakeholders who may not understand statistical jargon.

## When to Use

- When the target audience includes non-researchers
- When generating dashboards for stakeholders
- When the intake indicates a student or beginner user
- When creating `layman_summary.md` alongside `executive_summary.md`

## Protocol

### Step 1: Identify Technical Concepts

Scan the research findings for:
- Statistical tests (t-test, ANOVA, regression, etc.)
- Technical terms (heteroskedasticity, multicollinearity, etc.)
- Numerical results (p-values, effect sizes, confidence intervals)
- Methodological concepts (randomization, control groups, etc.)

### Step 2: Generate Plain-English Explanations

For each technical concept, create a plain-English explanation using these patterns:

#### Statistical Significance
**Technical**: "The effect was statistically significant (p < 0.05)"
**ELI5**: "We're confident this result isn't just random chance. If there were truly no effect, we'd see a result this extreme less than 5% of the time."

#### Effect Size
**Technical**: "Cohen's d = 0.5, 95% CI [0.2, 0.8]"
**ELI5**: "The difference is moderate — about half a standard deviation. We're 95% confident the true effect is between small (0.2) and large (0.8)."

#### Heteroskedasticity
**Technical**: "Heteroskedasticity detected (Breusch-Pagan p < 0.01)"
**ELI5**: "The spread of our prediction errors isn't consistent — our model is less certain for some values than others. This doesn't mean the results are wrong, but our confidence intervals might be too narrow."

#### Multicollinearity
**Technical**: "VIF > 10 for predictors X and Y"
**ELI5**: "Two of our input variables are so similar that the model can't tell which one is actually driving the result. It's like trying to figure out which twin committed a crime when they look identical."

#### R-squared
**Technical**: "R² = 0.45"
**ELI5**: "Our model explains 45% of the variation in the outcome. The other 55% is due to factors we didn't measure or random variation."

#### Confidence Interval
**Technical**: "95% CI [1.2, 3.4]"
**ELI5**: "If we repeated this study 100 times, about 95 of those studies would find an effect between 1.2 and 3.4. We can't be 100% sure, but we're pretty confident it's in this range."

#### P-value
**Technical**: "p = 0.03"
**ELI5**: "If there were truly no effect at all, there's only a 3% chance we'd see results this extreme just by random luck. That's pretty unlikely, so we think there's probably a real effect."

### Step 3: Generate Visual Explanations

For key findings, create simple visualizations that show WHY:

#### Why an Assumption Failed
Instead of just "Heteroskedasticity detected," create:
1. A residual plot showing the fan shape
2. An annotation: "See how the spread gets wider as X increases? That's heteroskedasticity."
3. A simple analogy: "Like a cone — narrow at one end, wide at the other."

#### Why a Result is Significant
1. Show the null distribution (what we'd expect if nothing was happening)
2. Mark where the observed result falls
3. Shade the area that represents the p-value
4. Annotate: "Our result is way out here — very unlikely to happen by chance"

#### Causal Diagram (DAG)
1. Draw simple boxes and arrows showing relationships
2. Use color: green for measured, red for unmeasured confounders
3. Annotate: "This arrow from Z to both X and Y means Z could be creating a fake relationship"

### Step 4: Generate layman_summary.md

Create `reports/summary/layman_summary.md` with this structure:

```markdown
# Research Findings — Plain English Summary

## What We Wanted to Know
[One sentence in plain language]

## What We Found
[Key findings in plain language, with ELI5 explanations]

## How Confident We Are
[Confidence level explained simply]

## What This Means
[Practical implications]

## What We Don't Know
[Limitations explained simply]

## What to Do Next
[Recommendations in plain language]

## Glossary
[Simple definitions of any technical terms used]
```

### Step 5: Interactive Dashboard Annotations

For the research dashboard, add ELI5 tooltips:
- Every statistical term gets a hover explanation
- Every plot has a "What am I looking at?" button
- Results are accompanied by "In plain English:" callouts

## Quality Rules

1. NEVER use jargon without immediately explaining it
2. ALWAYS use analogies that relate to everyday experience
3. NEVER oversimplify to the point of being wrong
4. ALWAYS preserve the uncertainty — don't make findings sound more certain than they are
5. ALWAYS include the "why" not just the "what"
6. Use short sentences (max 20 words)
7. Use active voice
8. Avoid acronyms without spelling them out first
