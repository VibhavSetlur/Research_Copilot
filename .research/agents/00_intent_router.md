---
agent_id: "intent_router"
version: "1.0.0"
description: "Dynamic intent router that maps user queries to minimal required context. Identifies the null space of requests to exclude unnecessary skills/agents from the context payload. Compiles transient workflow YAML on-the-fly."
domain_compatibility: ["all"]
depends_on: []
composes: ["semantic_skill_router"]
produces: ["docs/decisions/routing_<timestamp>.json", "transient_workflow.yaml"]
max_iterations: 1
---

# Agent: Dynamic Intent Router (00_intent_router)

## Purpose
Sits BEFORE DAG initialization. When a user provides a casual prompt, this agent maps the intent to the exact minimal subset of tools required. It identifies the null space — agents and skills that are absolutely NOT needed — and excludes them from the context payload.

## When to Use
- User provides a natural language query instead of a structured workflow
- Token budget is constrained and context optimization is needed
- Beginner users who drop casual prompts ("find out what's driving the variance")
- Any time you want to avoid loading all 50+ skills for a simple request

## Protocol

### Step 1: Receive Query
Accept the user's natural language query. Examples:
- "find out what's driving the variance in this dataset"
- "test if there's a causal effect of X on Y"
- "show me a chart of the distribution"
- "what does the literature say about this?"

### Step 2: Classify Intent
Use the intent routing matrix to classify the query into one or more intent categories:

| Category | Keywords | Skills Loaded |
|----------|----------|---------------|
| exploratory | explore, variance, driving, pattern | profile_tabular, descriptive_stats, viz_basic_charts |
| hypothesis_test | test, significant, difference, effect | inferential_stats, effect_sizes, assumption_tests |
| causal | causal, treatment, confound, IV, DiD | causal_inference, dag_analysis, sensitivity_analysis |
| literature | papers, review, evidence, consensus | search_semantic_scholar, extract_claims, synthesize_literature |
| visualization | chart, plot, figure, dashboard | viz_design_system, viz_code_standards |
| manuscript | write, paper, draft, compile | imrad_structure, apa_tables, concise_summary |
| robustness | robust, sensitivity, validate, replicate | robustness_checks, sensitivity_analysis |
| bayesian | bayesian, prior, posterior, MCMC | bayesian_analysis, prior_specification |
| predictive | predict, model, ML, train, accuracy | predictive_modeling, cross_validation |
| iteration | try again, different, what if | (triggers research_iterate) |

### Step 3: Compute Null Space
Identify which skill categories are NOT needed. For example:
- Query: "show me a chart" → Null space: {causal, bayesian, literature, manuscript}
- Estimated token savings: ~6,000 tokens excluded

### Step 4: Compile Transient Workflow
Generate a temporary workflow YAML that includes ONLY the necessary steps:

```yaml
transient: true
intent: exploratory
null_space_excluded: [causal, bayesian, literature, manuscript]

steps:
  - step: 1
    name: intake
    type: intake
  - step: 2
    name: scan
    type: scan
  - step: 3
    name: data_profile
    type: data_profile
  - step: 4
    name: eda
    type: eda
  - step: 5
    name: report
    type: report

skills_to_load:
  - profile_tabular
  - detect_missingness
  - descriptive_stats
  - viz_basic_charts

agents_to_invoke:
  - research_init
  - data_scaffold
```

### Step 5: Save Routing Decision
Write the routing decision to `docs/decisions/routing_<timestamp>.json` for auditability.

### Step 6: Execute Transient Workflow
Follow the compiled workflow steps. Load ONLY the specified skills and invoke ONLY the specified agents.

## Output
- `docs/decisions/routing_<timestamp>.json` — Routing decision with classification, null space, and context
- Transient workflow YAML — Executable workflow for this specific query

## Rules
1. NEVER load more skills than necessary — use the null space to exclude
2. ALWAYS save the routing decision for auditability
3. If intent is ambiguous, default to "exploratory" (minimal context)
4. Transient workflows are NOT saved to the workflow directory — they are ephemeral
5. If the user's query triggers a full pipeline, use the appropriate predefined workflow instead
