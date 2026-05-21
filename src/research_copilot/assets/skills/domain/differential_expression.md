---
skill_id: "differential_expression"
version: "1.0.0"
category: "analysis"
domain_compatibility: ["genomics"]
required_tools: ["R", "DESeq2"]
depends_on: ["profile_genomic"]
produces: ["02_experiments/main/deg_results.csv"]
complexity: "advanced"
---

# Skill: Differential Expression Analysis

<objective>
Calculates differentially expressed genes using DESeq2 for negative binomial distributed counts.
</objective>
