---
skill_id: "propensity_score_matching"
version: "1.0.0"
category: "analysis"
domain_compatibility: ["clinical"]
required_tools: ["sklearn"]
depends_on: []
produces: ["02_experiments/main/matched_cohort.csv"]
complexity: "advanced"
---

# Skill: Propensity Score Matching

<objective>
Matches treated and control observational units based on covariates to approximate an RCT.
</objective>
