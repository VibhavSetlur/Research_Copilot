# Research OS: End-to-End Walkthrough

This walkthrough demonstrates how to use Research OS for a realistic research project from start to finish. We will be analyzing a dataset on air pollution and its effects on respiratory health.

## 1. Setup Your Environment

First, install Research OS with all features, create a project, and start the server:

```bash
# Install Research OS with all optional features
pip install "research-os[all] @ git+https://github.com/VibhavSetlur/Research-OS.git"

# Create a project directory
mkdir air-pollution-research
cd air-pollution-research

# Initialize the workspace
# You can optionally provide a --name, otherwise it defaults to the directory name
research-os init --name "Air Pollution and Respiratory Health"

# Start the MCP Server
research-os start --workspace .
```

Connect your AI IDE (like Cursor or Claude Desktop) to the running MCP server.

## 2. Ingest Data and Context

1. Drop your dataset (e.g. `air_quality_health_impacts.csv`) into `inputs/raw_data/`.
2. Add any background literature or PDFs into `inputs/literature/`.

## 3. Guide Your AI IDE

Once your IDE is connected, open a new chat and simply copy-paste these prompts in order:

### Prompt 1: Project Startup
> "I've put my data, literature PDFs, and research notes into the inputs folder. I want to investigate how air pollution affects respiratory hospital admissions across different cities. Can you start the analysis?"

*Because of Rule 15, the AI will automatically load the `project_startup` protocol. It will scan inputs, conduct a domain analysis, formalise hypotheses, use `sys.path.create` to create `01_baseline_eda`, and execute the EDA script—all autonomously.*

### Prompt 2: Continue to Modelling
> "Continue. Let's move on to the next step suggested by the analysis plan: building a baseline regression model."

*The AI will continue following the `data_analysis` protocol, potentially calling `sys.checkpoint.pending` for approval before executing.*

### Prompt 3: Log Decisions
> "Let's log our decision to use linear regression. Please use `log-decision` (or `tool.log.decision`) to record why we chose this method and why we handled missing values the way we did."

### Prompt 4: Literature & Context
> "Search PubMed for recent papers (from the last 3 years) on PM2.5 and respiratory hospital admissions. Download the top 2 relevant papers to `inputs/literature/` and summarize their findings."

### Prompt 5: Synthesis and Reporting
> "We are ready to synthesize our findings. Use `tool.synthesize` to generate a markdown report of our methodology, results, and literature context into the `synthesis/` directory."

By following this chronological path, all of your methods, decisions, code, and data transformations will be rigorously documented, making your research entirely reproducible.
