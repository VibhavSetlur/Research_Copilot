# Researcher Guide — Operational Manual

Welcome to Research OS. This guide walks you through running your first AI-assisted research project end-to-end.

## First Project Tutorial

### Step 1: Create a Project
Create an empty folder and start the MCP server:

```bash
mkdir my-research && cd my-research
python -m research_os.server
```

### Step 2: Scaffold the Workspace
In your AI IDE, prompt:
> "Scaffold my new project using `sys.workspace.scaffold` with the name 'My Study'."

This creates the full directory tree: `inputs/`, `workspace/`, `synthesis/`, `environment/`, `.os_state/`, and the first experiment step `workspace/01_experiment_baseline/`.

### Step 3: Populating `inputs/`
Place your source materials into the immutable `inputs/` directory:
- **Raw data** → `inputs/raw_data/` (CSV, Parquet, JSON, etc.)
- **Literature PDFs** → `inputs/literature/`
- **Notes and context** → `inputs/context/`

The OS will auto-detect these files and generate SHA-256 checksums in `inputs/intake.md`.

### Step 4: Load a Protocol
Tell the AI to load the appropriate guidance protocol:
> "Load the domain analysis protocol using `sys.guidance.get` and follow its steps."

Protocols are YAML files in `src/research_os/protocols/` that guide the AI through each research phase.

### Step 5: Run Experiments
Experiments run as numbered chronological steps under `workspace/`. To create the next step:
> "Create the next experiment path for data preparation using `sys.path.create`."

Each step (`01_experiment_baseline/`, `02_data_preparation/`, ...) contains:
- `README.md` — Goal, hypotheses, expected and actual outcomes
- `data/` — Derived data for this step
- `scripts/` — Versioned analysis scripts
- `outputs/figures/`, `outputs/reports/`, `outputs/tables/`, `outputs/dashboards/`
- `environment/` — Pinned dependencies

### Step 6: Reading `analysis.md`
Open `workspace/analysis.md` to see:
- A **Mermaid workflow diagram** showing completed (green), running (yellow), planned (grey), and failed (red) steps
- A **chronological log** with timestamps: `[2026-05-22T10:00:00] analysis: Running linear regression`

The AI appends to this file after every significant action via `mem.analysis.log`.

### Step 7: Understanding `workflow.png`
If `mmdc` (Mermaid CLI) is installed, the OS renders `workspace/workflow.mermaid` into `workspace/workflow.png` automatically. This gives you a visual snapshot of your research progress.

Install mmdc: `npm install -g @mermaid-js/mermaid-cli`

### Step 8: Abandoning a Dead End
If an experiment path is not working, tell the AI:
> "Abandon this path using `sys.path.abandon` and record why."

The directory is renamed (e.g., `02_data_preparation__DEAD_END/`) — files are preserved, not deleted.

### Step 9: Synthesize the Paper
Once all experiments are complete:
> "Run the writing standards protocol and synthesize the paper."

The OS populates `synthesis/` with `abstract.md`, `paper.tex`, `references.bib`, and `workflow_diagram.png`.

## Troubleshooting Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `WriteProtectedError` | Attempted to write to `inputs/` | Move derived data to `workspace/.../data/` |
| `Protocol not found` | Protocol name is misspelled | Run `sys.guidance.list` to see available protocols |
| `Workspace not found` | No `.os_state/` directory | Run `sys.workspace.scaffold` first |
| `mmdc not found` | Mermaid CLI not installed | `npm install -g @mermaid-js/mermaid-cli` |
| `Path already exists` | Experiment folder name conflict | Use a different name; numbers auto-increment |

## Config Interview Flow

During scaffold, you can provide configuration overrides:

```yaml
# inputs/researcher_config.yaml
project_id: "My Study"
research_question: "What is the effect of X on Y?"
domain: "social_science"
default_depth: "academic"
```

The AI may ask you to supply missing values (research question, domain, depth). Answer naturally — the AI will fill the config and regenerate `inputs/intake.md`.
