# Quick Start — Research Copilot Template

## For Template Users: Setup Your Project

This is a **template repository**. You copy files into your own project — you don't clone this as your project.

### Step 1: Copy the system to your project

```bash
# Clone the template temporarily
git clone https://github.com/your-org/research-copilot-template.git _rcp_tmp

# Copy ONLY these 4 things to your project folder
cp -r _rcp_tmp/.research ./
cp -r _rcp_tmp/inputs ./
cp -r _rcp_tmp/environment ./
cp _rcp_tmp/AGENTS.md ./

# Clean up
rm -rf _rcp_tmp
```

Your project now has:
```
your-project/
├── .research/      # The entire system (don't edit)
├── inputs/         # Your data goes here
├── environment/    # Dependencies and setup scripts
└── AGENTS.md       # AI agent instructions
```

### Step 2: Set up your environment

```bash
# Using venv
bash environment/setup.sh
source environment/venv/bin/activate

# OR using Conda
bash environment/setup_conda.sh
conda activate research-copilot
```

### Step 3: Add your data and fill out the intake

1. Drop data files into `inputs/data/raw/`
2. Open `inputs/intake.md` and fill in your project info, research questions, and data description

### Step 4: Open your AI agent

Open opencode, Cursor, Claude Code, or any AI agent in your project folder and paste:

```
I'm using the Research Copilot system.

1. System: .research/ — CLI, agents, skills, workflows, scripts
2. Data: inputs/ — my data and intake form
3. Environment: environment/ — requirements.txt, setup scripts

Start by running:
  python .research/research.py preflight
  python .research/research.py scan
  python .research/research.py status

Then read inputs/intake.md and begin:
  python .research/research.py agent research_init

Optional: run format routing if you have non-tabular data
  python .research/research.py format-scan
```

### Step 5: The AI does the rest

The AI will:
1. Scan your data and intake
2. Create `docs/`, `reports/`, `data/`, `scripts/` directories
3. Build a research map and assess feasibility
4. Run through the full pipeline: literature → methods → analysis → manuscript → audit

At any point you can:
- Ask: "What did you find?"
- Iterate: "Try a different method"
- Approve/reject at gates: `python .research/research.py approve method_route`

---

## For Template Maintainers: Development

This repo is the source template. Key directories:

| Directory | Purpose |
|-----------|---------|
| `.research/` | All system code — agents, skills, CLI, hooks, scripts, schemas |
| `inputs/` | Template intake form and empty data directories |
| `environment/` | requirements.txt and setup scripts |
| `AGENTS.md` | AI instructions (copied to user projects) |

NOT copied to user projects:
- `README.md` — this is for the template repo
- `.gitignore` — users write their own
- `TODO.md` — development tracking
- `LICENSE` — users choose their own

### Adding new features

1. New agent → `.research/agents/NN_name.md`
2. New skill → `.research/skills/<category>/name.md`
3. New domain → `.research/domains/name.yaml`
4. New CLI command → add to `.research/research.py`
5. New utility script → `.research/scripts/utils/name.py`

### Testing

```bash
# Verify all modules import correctly
python3 -c "import sys; sys.path.insert(0, '.research/core'); from hooks import hook_engine; print('OK')"

# Run the CLI
python3 .research/research.py --help

# Test hook system
python3 .research/research.py hooks
```
