# 📘 Researcher Guide: Operational Manual

Welcome to the Research OS! This operational manual will walk you through launching your first AI-assisted research project.

## 🏁 Tutorial: Your First Project

Let's run a complete research workflow from start to finish.

**Step 1: Scaffold the Workspace**
Start your MCP-enabled AI IDE (Cursor, Windsurf, etc.) and prompt it:
> "Initialize a new project using `sys.workspace.scaffold` with the name 'Climate Analysis'."

**Step 2: Initialize Configuration**
> "Run `sys.config.init` and show me the resulting `inputs/researcher_config.yaml` file so I can add my API keys."

**Step 3: Load the Protocol**
> "Load the domain analysis protocol using `sys.guidance.get {'protocol_name': 'domain_analysis'}` and follow its steps."

**Step 4: Execute Research**
As the agent runs the protocol, it will perform searches, write analysis scripts, and log findings.

## 🗂️ How to Populate the `inputs/` Directory

The `inputs/` folder is the **immutable foundation** of your project. Agents are structurally blocked from modifying it.

- **Data Science / ML**: Place `.csv`, `.parquet`, or `.h5` files into `inputs/raw_data/`.
- **Bioinformatics**: Place `.fasta`, `.fastq`, or `.bam` files into `inputs/raw_data/`.
- **Literature Reviews**: Place PDF papers into `inputs/literature/`. Update the `inputs/literature_index.yaml` file to map files to citations.

*Example structure:*
```
inputs/
  raw_data/
    climate_measurements_2020.csv
    satellite_imagery.zip
  literature/
    smith_2023_warming.pdf
```

## 📊 Tracking Progress

You don't need to read every single line of Python code the agent writes. Instead, monitor these two files:

1. **`workspace/analysis.md`**: This is the chronological narrative of your research. Check here for statistical results, key findings, and interpretation of graphs.
2. **`.os_state/execution_dag.json` (and compiled `workflow.png`)**: This visualizes the directed acyclic graph (DAG) of the data pipeline. Check this to see what scripts were run and which datasets were generated.

## 🛠️ MCP Tool Cheat Sheet

Here are the most critical commands you can ask your AI agent to run:

- **`sys.checkpoint.create`**: Snapshot the entire workspace before a risky move.
- **`sys.branch.create`**: Branch the research to test an alternative hypothesis safely.
- **`sys.guidance.get`**: Load a structured research methodology (e.g., `literature_search`, `analysis_plan`).
- **`tool.log.decision`**: Log a methodological choice (e.g., dropping outliers).
- **`tool.data.sample`**: Sample a massive dataset so the agent can write the script cheaply before running it on the full data.
- **`sys.state.minimal_context`**: Get a quick <=500-token summary of the current project state.

## ⚠️ Troubleshooting

**Error: `WriteProtectedError: Cannot modify raw inputs.`**
- *Cause:* The agent tried to clean data in `inputs/raw_data/`.
- *Fix:* Tell the agent to write the cleaned dataset to `workspace/data/derived/` instead.

**Error: `Firecrawl search failed: API key not set`**
- *Cause:* Missing credentials in `inputs/researcher_config.yaml`.
- *Fix:* Open the YAML file, populate `api_keys.firecrawl`, and tell the agent to retry the search.

**Error: `File too large (>50MB). Use tool.data.sample instead.`**
- *Cause:* The agent attempted to read a massive raw data file directly into its context window.
- *Fix:* Instruct the agent to run `tool.data.sample` to read the first 100 rows instead.
