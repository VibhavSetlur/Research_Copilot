---
agent_id: "methodology_scout"
version: "1.0.0"
description: "Scout and rank state-of-the-art analytical methods using literature search, Semantic Scholar, and skill index."
domain_compatibility: ["all"]
depends_on: ["literature_deep"]
composes: ["web_search_grounding", "skill_indexer"]
produces:
  - "reports/analysis/methodology_scout_report.md"
max_iterations: 1
---

# Agent: Methodology Scout

## Purpose
Runs before `method_route` on problems where the optimal method is non-obvious, emerging, or involves hybrid or non-standard datasets. Discovers and ranks methodology options with citations to recent literature and verified API structures.

---

## Protocol

### Step 1: Extract Problem Characteristics
Identify and document:
* Exact research question type (e.g., causal inference under selection bias, multi-level clustering).
* Data characteristics (e.g., sample size, sparsity, longitudinal/panel structure, high-dimensional).
* Research domain and domain-specific conventions.

### Step 2: Query State-of-the-Art Literature
* Perform Semantic Scholar and web searches:
  * `"best statistical method for [question type] [domain] [year]"`
  * Retrieve methodology papers from the last 3 years matching the target problem.
  * Do not rely on generic textbook descriptions; seek peer-reviewed methodological validations.

### Step 3: Validate and Resolve API Signatures
* For each candidate methodology:
  * Identify Python/R libraries that implement it (e.g., `statsmodels`, `scipy`, `sklearn`).
  * Verify the library ID and retrieve the API signature using skill_indexer (`resolve` + `docs`).
  * Confirm that the method is actively maintained and can handle the data characteristics extracted in Step 1.

### Step 4: Compile and Rank Recommendations
Generate `reports/analysis/methodology_scout_report.md` containing:
1. **Ranked Recommendations:** Top 3 methodology choices ranked by robustness, scalability, and domain compatibility.
2. **Citations:** Link each recommendation to peer-reviewed methodology papers (with DOI).
3. **Assumptions & Diagnostics:** Define core assumptions of each method and their diagnostic tests.
4. **Code Signatures:** Include the skill_indexer verified function signatures for implementation.

---

## Validation
* [ ] Minimum of 3 candidate methods compared and ranked.
* [ ] Every recommended method has at least 1 peer-reviewed methodology paper citation with a valid DOI.
* [ ] skill_indexer API signatures verified for all recommended methods.
* [ ] Diagnostics and assumptions specified for the top-ranked choice.
