---
skill_id: "walk_forward_validation"
version: "1.0.0"
category: "audit"
domain_compatibility: ["finance"]
required_tools: ["pandas"]
depends_on: ["strategy_backtester"]
produces: ["02_experiments/main/wfa_metrics.json"]
complexity: "advanced"
---

# Skill: Walk-Forward Validation

<objective>
Performs rolling or expanding window out-of-sample testing to detect overfitting.
</objective>
