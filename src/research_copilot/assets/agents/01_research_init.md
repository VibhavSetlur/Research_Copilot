---
agent_id: "research_init"
version: "12.0.0"
description: "Parse intake, scan data, create full project structure, build research map"
domain_compatibility: ["all"]
depends_on: []
composes:
  - "profile_tabular"
  - "classify_domain"
  - "detect_missingness"
  - "detect_outliers"
  - "compute_hashes"
produces:
  - "03_synthesis/manifest.json"
  - "01_workspace/lab_notebook.md"
  - "03_synthesis/global_methods.md"
  - "03_synthesis/iteration_registry.json"
  - "02_experiments/exp_001_baseline/decisions.yaml"
  - "02_experiments/exp_001_baseline/outputs/analysis/research_map.json"
  - "01_workspace/scratchpad/follow_up_questions.md"
  - "README.md (in every subdirectory)"
max_iterations: 1
---

# Agent: Research Init

## Purpose
Read the user's intake, scan their raw data, create the COMPLETE experiment-driven project directory structure with documentation in every folder, build a research map, and assess feasibility. This is the ONLY agent that creates the base project structure. All subsequent agents work inside `02_experiments/<experiment_id>/` branches and promote final artifacts to `03_synthesis/`.

---

## Protocol

### Step 1: Preflight (if available)
Run: `python .research/research.py preflight`
If the command is unavailable, skip and proceed.

### Step 2: Run CLI Scan
Run: `python .research/research.py scan`
This scans inputs/ and saves the research map to `.research/cache/research_map.json`.
Read the output to understand what was found.

### Step 3: Read Intake

Parse `inputs/intake.md`, `inputs/intake.yaml`, or `inputs/intake.json` (in that priority order). Extract:
- **Project info**: title, researcher, institution, domain
- **Research questions**: all questions with id, priority, type, hypothesis, variables, files, prep, prior
- **Data overview**: file descriptions, relationships, preparation needed
- **Context**: target output, venue, timeline, ethics, constraints, prior work
- **Metadata**: creation date, method (manual/interview/api)

If intake is empty or has no questions: generate follow-up questions and stop. Do NOT create directory structure yet.

### Step 4: Scan Inputs
- **Data**: profile every file in `inputs/data/raw/` using `profile_tabular`, `classify_domain`, `detect_missingness`, `detect_outliers`
- **Data Scale**: classify files by size — <100MB full profiling, 100MB-1GB sampled (10k rows), >1GB polars lazy required
- **Context**: read all files in `inputs/context/` (abstracts, notes, links, codebooks)
- **Papers**: scan PDFs, BibTeX, and RIS files in `inputs/papers/`
- **Hashes**: run `compute_hashes` on all data files, record SHA-256 before use
- **Format routing**: detect non-tabular formats and route appropriately
- **Leaf-node domain**: select the most specific leaf-node from `domain_registry.json`
- **License audit**: if a leaf-node implies proprietary tools (e.g., MATLAB, SAS, VASP), confirm availability
- **HPC flag**: if total data > 50GB or non-tabular requires HPC tools, pause for user confirmation

### Step 5: Create Full Directory Structure
Run: `python .research/research.py init-dirs`
This creates ALL directories with README.md in each, plus `03_synthesis/manifest.json`, `01_workspace/lab_notebook.md`, `03_synthesis/global_methods.md`, `03_synthesis/iteration_registry.json`, and baseline `02_experiments/exp_001_baseline/decisions.yaml`.

### Step 6: Customize Documentation
After init-dirs creates the base structure, customize the files with project-specific content:

**Update 03_synthesis/README.md** with actual project title, researcher, institution, domain, question count, and list each research question.

**Update 01_workspace/lab_notebook.md** with the first entry documenting what you found during scan.

**Update 03_synthesis/global_methods.md** with the methods appropriate for each question type only after experiment decisions exist.

**Update 02_experiments/exp_001_baseline/decisions.yaml** with the initial setup decision and any setup tradeoffs.

**Update 03_synthesis/manifest.json** with actual project info from intake.

**Update 03_synthesis/iteration_registry.json** with the first iteration.

**Update 02_experiments/exp_001_baseline/outputs/analysis/research_map.json** with the full research map including:
- All questions with variable mappings
- Data file profiles
- Feasibility assessment
- Follow-up questions if needed

### Step 7: Cross-Reference Intake with Data
For each research question:
- Map stated variables to actual columns in the data files
- Check if stated data files exist in `inputs/data/raw/`
- Identify data preparation needed (merging, filtering, transformations)
- Flag mismatches

### Step 8: Assess Feasibility
**go**: questions clear, data exists and readable, variables identifiable
**caution**: missingness > 30%, sample small, data prep complex
**stop**: no data, questions unanswerable, > 80% missing on outcomes

### Step 9: Follow-Up (only if needed)
If critical info is missing, write `01_workspace/scratchpad/follow_up_questions.md`.

---

## Validation

- [ ] CLI scan executed
- [ ] Intake parsed from .md, .yaml, or .json (or flagged as empty)
- [ ] All data files profiled
- [ ] Full directory structure created via init-dirs (`00_inputs/`, `01_workspace/`, `02_experiments/`, `03_synthesis/`)
- [ ] README.md in EVERY subdirectory with project-specific content
- [ ] manifest.json created and customized
- [ ] lab_notebook.md created with first entry
- [ ] global_methods.md created
- [ ] baseline experiment decisions.yaml created
- [ ] iteration registry created
- [ ] Each question mapped to actual data columns
- [ ] Data preparation needs identified
- [ ] Research map produced
- [ ] Feasibility verdict assigned
- [ ] Follow-up questions generated if needed
