# Research Copilot (v2) — Skills-First Architecture

Welcome to the **Research Copilot**, an autonomous data research platform designed to automate literature search, data profiling, statistical analysis, and dashboard generation.

This repository uses a **Skills-First Architecture**, meaning capabilities (like outlier detection, causal inference, and visualization) are modular and dynamic. You can use it across any domain, powered by any LLM.

---

## 🚀 Quick Start

### 1. Initialize Your Project
```bash
research init --domain epidemiology
```
This generates the `.research/` directory containing all skills, agents, and configuration. 
*(Available domains: epidemiology, econometrics, psychology, genomics, nlp_computational, ecology, finance, education)*

### 2. Prepare Your Brief
Open `.research/config.yaml` to specify your research questions and hypotheses.
Drop your raw data files into the `data/` directory (or wherever specified by your config).

### 3. Run the Research Workflow
```bash
# Run a full publication workflow
research run --workflow full_publication

# Or run specific skills
research run --skill power_analysis
```

---

## Core Architecture

The v2 overhaul transitions the system from monolithic, linear prompts to a modular DAG execution engine.

### Directory Structure
```
.research/
├── skills/                    # Reusable capabilities (e.g., data profiling, stats)
├── agents/                    # Workflow orchestrators that compose skills
├── domains/                   # Domain-specific configs (reporting standards, stats)
├── workflows/                 # Pre-built DAGs (e.g., quick_exploratory)
├── config.yaml                # Project configuration
└── state/                     # Runtime checkpoints and DAG visualizer output
```

### Key Features
1. **DAG Workflow Visualization:** Every action creates a node in a live directed acyclic graph (`workflow_dag.mermaid`).
2. **Recursive Literature Search:** Automatically performs citation chaining via Semantic Scholar, arXiv, and PubMed.
3. **Data Versioning:** Use `research data add` or `research data remove` to track lineage.
4. **Interactive Dashboard:** Auto-generates an 8-tab Plotly Dash application with your findings.
5. **NotebookLM Integration:** Export directly to NotebookLM with `research notebooklm import`.

---

## 🛠 Advanced Usage

### The `research` CLI

- **Literature:** 
  `research literature search "keywords"`
  `research literature snowball <doi>`
- **Visualization:**
  `research viz dashboard`
- **Audit:**
  `research audit full`

For migration from v1 to v2, see [MIGRATION.md](MIGRATION.md).
For contributing new skills or domains, see [CONTRIBUTING.md](CONTRIBUTING.md).
