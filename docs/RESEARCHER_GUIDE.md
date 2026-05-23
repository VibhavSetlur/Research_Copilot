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

## Domain-Specific Config Templates

To quickstart your project with predefined reporting standards and protocols, you can use one of the ready-made templates located in `templates/configs/`. 

Available templates:
- `rct_config.yaml`
- `epidemiology_observational.yaml`
- `nlp_benchmark.yaml`
- `genomics.yaml`
- `economic_panel.yaml`

To use a template, simply copy it to your inputs directory:
```bash
cp templates/configs/rct_config.yaml inputs/researcher_config.yaml
```

## Advanced Quality Audits

Research OS now includes automated quality audit tools to verify the statistical integrity and reproducibility of your research before synthesis:
- **`tool.audit.statistical_power`**: Computes post-hoc power for tests and warns if power < 0.8.
- **`tool.audit.assumptions`**: Re-runs assumption checks (Shapiro-Wilk, Levene, etc.) on model outputs.
- **`tool.audit.figure_quality`**: Validates DPI, colorblind-friendliness, labels, and error bars.
- **`tool.audit.reproducibility_full`**: Runs a full Docker-based reproducibility check comparing checksums.

## Using Multiple Languages

Research OS supports orchestrating workflows across multiple languages (Python, R, Julia, Bash) natively within the same workspace.

### Executing Scripts
Instead of running everything in Python, use the language-specific executor tools:
- `tool.python.exec` for Python scripts.
- `tool.r.exec` for R scripts.
- `tool.julia.exec` for Julia scripts.
- `tool.bash.exec` for shell scripts.

### Sharing Data
To pass data between languages in the same step, use `tool.data.convert`. It efficiently converts tabular data between formats like `.csv`, `.parquet`, `.rds`, and `.feather` allowing you to read/write native formats for each language.

### Environment Snapshots
Pinning dependencies for multi-language projects is fully automated via `sys.env.snapshot`. This single tool will scan the workspace and save:
- `requirements.txt` (via pip)
- `renv.lock` (for R)
- `Project.toml` (for Julia)
- `environment.yml` (for conda)

To guarantee ultimate reproducibility, you can then call `sys.env.docker.generate` to create a `Dockerfile` that contains instructions to install all saved runtimes and pinned packages.
