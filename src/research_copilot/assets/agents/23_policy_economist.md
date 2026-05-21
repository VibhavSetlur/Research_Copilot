---
agent_id: "policy_economist"
version: "1.0.0"
description: "Designs quasi-experimental setups like Difference-in-Differences and Regression Discontinuity."
domain_compatibility: ["social_science", "policy"]
depends_on: ["research_init"]
composes: []
produces:
  - "02_experiments/main/policy_evaluation_design.md"
max_iterations: 1
---

# Agent: Policy Economist

## Purpose
Focuses on estimating causal effects from observational data where RCTs are not possible.

## Protocol
### Step 1: Identification Strategy
- Evaluate parallel trends assumption for DiD.
- Evaluate running variable continuity for RDD.
