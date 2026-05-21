# Getting Started

Install Research Copilot, create a project, and run your first analysis.

## Prerequisites

- Python 3.10 or later
- pip or uv

## 1. Install

```bash
pip install research-copilot
```

For full features (dashboards, export, MCP):

```bash
pip install research-copilot[all]
```

## 2. Create a Project

```bash
# Option A: Create in current directory
rcp init my-project
cd my-project

# Option B: Create in a specific location
rcp init /path/to/my-project
cd /path/to/my-project
```

This creates the project structure with `.research/config.yaml` (system config), `00_inputs/` (raw data), and `environment/` (dependencies).

## 3. Set Up the Environment

```bash
bash environment/setup.sh
source environment/venv/bin/activate
```

Or with Conda:

```bash
bash environment/setup_conda.sh
conda activate research-copilot
```

Verify everything is ready:

```bash
rcp preflight
```

## 4. Add Your Data

Place data files in `00_inputs/raw_data/`. Supported formats:

| Format | Extension | Notes |
|--------|-----------|-------|
| CSV | `.csv` | Auto-detects delimiter and encoding |
| TSV | `.tsv` | Tab-separated |
| Parquet | `.parquet` | Fast, columnar |
| Excel | `.xlsx`, `.xls` | First sheet by default |
| Stata | `.dta` | Versions 10-17 |
| SPSS | `.sav` | IBM SPSS |
| SAS | `.sas7bdat` | SAS datasets |

Files >100MB are automatically sampled for profiling. Files >1GB require polars lazy frames.

## 5. Describe Your Research

### Option A: Conversational Interview (Recommended)

```bash
rcp intake-interview --start
```

The AI asks 5 questions in plain English and generates `00_inputs/intake.md` automatically.

### Option B: Manual

Edit `00_inputs/intake.md` directly. Only 3 fields are required:

```markdown
- **Project title**: Your project name
- **Primary research question**: What do you want to find out?
- **Outcome variable**: What is the main thing you're measuring?
```

## 6. Run the Pipeline

Open your AI IDE (Cursor, opencode, Claude Desktop) and say:

> "Start the research pipeline."

Or run commands manually:

```bash
rcp status          # Check project state
rcp scan            # Scan your data
```

The `research_init` agent creates the full directory structure under `01_workspace/`, `02_experiments/`, and `03_synthesis/`.

## 7. Review Results

When the pipeline completes, open:

- `03_synthesis/key_findings.md` — Summary of results
- `03_synthesis/manuscript/` — Draft manuscript
- `02_experiments/exp_001_baseline/outputs/figures/` — Generated figures

## 8. Iterate

Ask follow-up questions in plain English:

| You Say | What Happens |
|---------|-------------|
| "Why did we get this result?" | Investigates existing results |
| "Try a different method" | Switches analytical approach |
| "What if we control for X?" | Adds variables, re-runs |
| "Check if this holds up" | Runs sensitivity analysis |
| "How does this compare to literature?" | Compares to prior work |
| "What else is in the data?" | Exploratory analysis |

Each iteration creates a new experiment branch — previous results are never deleted.

## Next Steps

- [Workflows](WORKFLOWS.md) — Choose a pipeline type for your research
- [CLI Reference](CLI_REFERENCE.md) — All available commands
- [MCP Integration](MCP_INTEGRATION.md) — Connect your AI IDE
- [Architecture](ARCHITECTURE.md) — How the system works
