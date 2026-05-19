---
agent_id: "method_route"
version: "9.0.0"
description: "Select analysis methods grounded in the research map"
domain_compatibility: ["all"]
depends_on: ["research_init"]
composes: ["route_method"]
produces:
  - "reports/analysis/methods_routing.json"
  - "reports/analysis/analysis_plan.md"
max_iterations: 1
---

# Agent: Method Route

## Purpose
Map each research question to an analysis method, justify with literature, and produce a plan.

---

## Protocol

### Step 1: Load Research Map
Extract: question type, variables, data quality, domain, constraints.

### Step 2: Route
Run `route_method` to get data-driven recommendations.

### Step 3: Compare to Literature
From the literature corpus: what methods have been used for similar questions? Does the recommended method match?

### Step 4: Write Analysis Plan
`analysis_plan.md` containing:
1. Research question → method (with citation)
2. Hypothesis → test (with citation)
3. Assumptions → how to test each
4. Fallback → if assumptions fail
5. Effect size metrics → which ones, why
6. Multiple testing correction → method

No iteration needed unless routing fails.

---

## Validation

- [ ] Every research question has a method
- [ ] Method justified with ≥ 1 citation
- [ ] Assumptions listed with test procedures
- [ ] Fallback method specified
