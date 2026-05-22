# TODO.md — Research OS v3.0: Research Guidance Engine

*Generated: 2026‑05‑23 | Target: Complete rewrite for scalable, domain‑aware, AI‑guided research*

---

## 🧭 PHILOSOPHY SHIFT

**Old model:** Static tools for basic stats → AI chooses from a menu.  
**New model:** The OS provides **research reasoning protocols, domain analysis, literature search strategies, methodology decision trees, and writing/auditing standards**. The AI model does the “thinking” but follows these structured pathways, ensuring depth and reproducibility regardless of model size.

We no longer host `tool.descriptive.stats` or `tool.ttest`. Instead, the OS:
1. Analyzes the user’s inputs (data, context files, questions).
2. Determines the research domain and appropriate methodologies.
3. Guides the AI through literature search, method selection, and implementation using external libraries and APIs.
4. Logs every step, search, and decision for full provenance.

---

## 🗑️ PHASE 0: CLEANSE THE REPOSITORY

### 0.1 Delete Entire Directories (dead autonomous‑agent code)
- [ ] `src/research_os/cognition/`
- [ ] `src/research_os/collaboration/`
- [ ] `src/research_os/graph/`
- [ ] `src/research_os/execution/`
- [ ] `src/research_os/planning/`
- [ ] `src/research_os/provenance/`
- [ ] `src/research_os/replay/`
- [ ] `src/research_os/research_objects/`
- [ ] `src/research_os/agents/`
- [ ] `src/research_os/chat.py`

### 0.2 Remove All Old Skills and Assets
- [ ] Delete `src/research_os/assets/skills/` (the whole old MD set)
- [ ] Delete `src/research_os/assets/workflows/` (old YAML workflows)
- [ ] Delete `src/research_os/assets/agents/` (old prompt templates)

### 0.3 Clear Out `.research` Folder Concept
- [ ] Remove any creation of a `.research` directory from `project_ops.py` and config.
- [ ] Cache will be stored inside the workspace’s state folder: `workspace/.os_state/cache/`.

---

## 🧠 PHASE 1: BUILD THE RESEARCH GUIDANCE ENGINE

This is the new core. It replaces static tools with dynamic, context‑sensitive guidance.

### 1.1 Guidance Protocol Format
We use **YAML‑based decision graphs** (not just markdown) that the MCP server exposes as resources. Each protocol contains:
- **Conditions**: when to apply (based on data types, research question, domain).
- **Steps**: reasoning prompts, search strategies, tool suggestions (external libraries, not built‑in).
- **Checkpoints**: validation rules, assumptions to verify.
- **Outputs**: expected artifacts and their formats.

### 1.2 Initial Guidance Protocols to Create

- [ ] **`protocols/domain_analysis.yaml`**  
  Takes user input (files, questions, context) and returns a structured domain profile (e.g., epidemiology, economics, NLP) with suggested reporting standards (STROBE, CONSORT, etc.) and common methodological pitfalls.

- [ ] **`protocols/research_design.yaml`**  
  Given the research question type (causal, predictive, exploratory, descriptive), guides the AI through choosing an appropriate design (RCT, cohort, case‑control, cross‑sectional, quasi‑experimental, etc.) with reasoning steps.

- [ ] **`protocols/methodology_selection.yaml`**  
  A decision tree that, based on data characteristics (scale, distribution, missingness, dependencies) and research goals, recommends specific statistical approaches (e.g., “use mixed‑effects model because of repeated measures” or “apply DAG‑based backdoor adjustment for confounding”). It **does not** implement the method; it tells the AI *what* to use and *why*, and points to the relevant Python/R libraries (e.g., `statsmodels`, `lme4`, `DoWhy`).

- [ ] **`protocols/literature_search.yaml`**  
  Step‑by‑step search strategy: building query strings, selecting databases (PubMed, Semantic Scholar, arXiv, Google Scholar), deduplication, snowballing, and evaluating paper quality (using checklists like PRISMA, AMSTAR). It also instructs the AI to log every search string and result count.

- [ ] **`protocols/evidence_synthesis.yaml`**  
  How to extract claims from papers, assess strength (p‑values, effect sizes, sample sizes), and create an evidence matrix. Includes instructions for using `scholarly`, `semanticscholar`, and direct API calls, with logging.

- [ ] **`protocols/analysis_plan.yaml`**  
  Guides the AI to break down the research into numbered experiments (`01_`, `02_`, …) in the workspace. Defines how to write a clear README for each step, what to log, and when to branch.

- [ ] **`protocols/writing_standards.yaml`**  
  Detailed guidance for writing each manuscript section according to common academic standards (IMRAD, APA, etc.), with examples and common pitfalls.

- [ ] **`protocols/figure_guidelines.yaml`**  
  Best practices for publication figures: chart selection, colorblind‑friendly palettes, labeling, resolution, and when to use specific plot types (forest plots, funnel plots, DAGs, etc.). Does not generate figures directly; instead instructs the AI to use `matplotlib`/`seaborn`/`plotly` with specific parameters.

- [ ] **`protocols/reproducibility.yaml`**  
  Checklist for making research fully reproducible: versioned scripts, environment pinning, random seeds, checksums, and verification steps.

- [ ] **`protocols/audit_and_validation.yaml`**  
  Post‑analysis audit: citation verification (3‑pass), causal language check, statistical assumption re‑check, code quality. Instructions for external tools (ruff, mypy) and manual checks.

### 1.3 MCP Exposure of Protocols
- [ ] **Implement `sys.guidance.get(protocol_name)`** — returns the full YAML content of a protocol as a resource.
- [ ] **Implement `sys.guidance.list`** — lists all available protocols with one‑line summaries.
- [ ] **The IDE can fetch protocols lazily** and use them to reason. The OS does not auto‑apply them; it only serves them.

---

## 🔧 PHASE 2: CORE MCP TOOLS (Minimal, Powerful)

We keep only the tools that are **OS‑level** (file I/O, state, web search, environment, code execution orchestration). No baked‑in analysis.

### 2.1 File & Workspace Management
- [ ] `sys.workspace.scaffold` — creates the directory structure (unchanged from previous TODO, but without `.research`).
- [ ] `sys.file.read` / `sys.file.write` — secure read/write within workspace with checksumming.
- [ ] `sys.file.list` — directory listing with metadata.
- [ ] `sys.file.delete` — with safeguard.

### 2.2 State & Branching
- [ ] `sys.state.get` / `sys.state.summary`
- [ ] `sys.checkpoint.create` / `sys.checkpoint.rollback` / `sys.checkpoint.list`
- [ ] `sys.branch.create` / `sys.branch.switch` / `sys.branch.list` / `sys.branch.merge`
- [ ] `mem.analysis.log` — appends to `workspace/analysis.md`
- [ ] `mem.methods.append` — appends structured method entry

### 2.3 Web & Literature Search (Real Research Capabilities)
- [ ] **`tool.search.semantic_scholar`** — query Semantic Scholar API, return structured results with citations.
- [ ] **`tool.search.pubmed`** — query PubMed (via Entrez) with MeSH expansion.
- [ ] **`tool.search.crossref`** — verify DOIs and metadata.
- [ ] **`tool.search.web`** — general web search using a **configurable backend** (Firecrawl, SerpAPI, or self‑hosted). This tool is essential for the AI to find documentation, tutorials, and domain‑specific resources. **Every query is logged** with timestamp and result count.
- [ ] **`tool.web.scrape`** — fetch and clean webpage content (using Firecrawl or BeautifulSoup). Logged.
- [ ] **`tool.literature.download`** — download a paper PDF (when legally available) into `inputs/literature/` and update the index.

### 2.4 Code Execution & Environment
- [ ] **`tool.python.exec`** — execute a Python script within a specified environment (from step’s `environment/`), capturing stdout/stderr, returning logs and output files.
- [ ] **`tool.package.install`** — install packages for the active step’s environment and freeze requirements.
- [ ] **`tool.env.freeze`** — snapshot current environment.
- [ ] **`tool.env.restore`** — restore from requirements.txt or Dockerfile.

### 2.5 Logging & Provenance
- [ ] **All search tools automatically log** to `workspace/logs/searches.log` (JSON lines: timestamp, tool, query, results count, sources).
- [ ] **`tool.log.decision`** — explicitly record a key reasoning step (e.g., “chose Mann‑Whitney because normality violated”).
- [ ] **Provenance tracking** for every output file (script, data, figure) stored in `.meta/` sidecars.

---

## 📁 PHASE 3: REVISED USER‑SIDE DIRECTORY STRUCTURE

Remove `.research`, keep inputs as the sole guide, and store all OS state inside `workspace/.os_state/`.

```
<user-project>/
├── README.md
├── docs/                          # Human-written research docs
│   ├── research_question.md
│   ├── hypotheses.md
│   └── glossary.md
├── inputs/                        # IMMUTABLE — provided by user
│   ├── data/                      # Raw data (or symlinks)
│   ├── literature/                # PDFs
│   ├── context/                   # Notes, past results, text files
│   └── intake.md                  # Auto-generated brief
├── workspace/                     # ACTIVE
│   ├── methods.md                 # Append‑only method log
│   ├── analysis.md                # Chronological log + workflow diagram
│   ├── citations.md               # Verified bibliography
│   ├── logs/
│   │   ├── searches.log           # Every web search logged
│   │   ├── state_changes.log
│   │   └── <step>.log
│   ├── figures/                   # Cross‑step shared figures
│   ├── dashboards/
│   ├── workflow.mermaid
│   ├── workflow.png
│   ├── 01_experiment_baseline/
│   │   ├── README.md
│   │   ├── conclusions.md
│   │   ├── methods_research.md    # AI’s research into methods for this step
│   │   ├── data/                  # Derived data
│   │   ├── scripts/               # Versioned (01_..._v1.py)
│   │   ├── outputs/
│   │   │   ├── reports/
│   │   │   ├── fi
│   │   │   ├── reports/
│   │   │   ├── figures/
│   │   │   ├── tables/
│   │   │   └── dashboards/
│   │   └── environment/           # Pinned dependencies
│   ├── 02_ ...
│   └── .os_state/                 # INTERNAL
│       ├── state_ledger.yaml
│       ├── checkpoints/
│       ├── cache/                 # Transient cache (e.g., API responses)
│       └── manifest.json
├── synthesis/                     # FINAL
│   ├── abstract.md
│   ├── paper.tex / paper.pdf
│   ├── references.bib
│   ├── workflow_diagram.png
│   └── supplementary/
└── environment/                   # Global environment (optional)
```

---

## 📚 PHASE 4: DOCUMENTATION & ONBOARDING

- [ ] **Rewrite `README.md`** — emphasize the guidance philosophy, show a demo of the AI doing complex research with only the OS as guide.
- [ ] **`QUICKSTART.md`** — 3 steps: init, paste MCP config, start a conversation.
- [ ] **`docs/GUIDANCE_SYSTEM.md`** — explain the protocol system and how to extend it.
- [ ] **`docs/RESEARCHER_GUIDE.md`** — for the human researcher: how to use the OS, interpret logs, and interact with the AI.
- [ ] **`docs/AI_INTEGRATION.md`** — for IDE / model providers: how the MCP server communicates and how to use the protocols.
- [ ] **`docs/EXAMPLE_WALKTHROUGH.md`** — a full mock research project from raw data to paper, showing the AI reasoning under OS guidance.

---

## 🧪 PHASE 5: TESTING & VALIDATION

- [ ] Unit tests for all state machine operations.
- [ ] Integration test: scaffold → branch → guided analysis → synthesis.
- [ ] Test web search logging and traceability.
- [ ] Test reproducibility: run same workflow twice, verify identical checksums.
- [ ] Continuous integration with GitHub Actions.

---

## 🚀 PHASE 6: ROLLOUT SEQUENCE

| Priority | Task | Effort |
|----------|------|--------|
| 🔴 | Phase 0: Codebase cleanse | 1 day |
| 🔴 | Phase 1: Build guidance protocols (YAML design & initial 10 protocols) | 1.5 weeks |
| 🟡 | Phase 2: Implement core MCP tools (file, state, search, exec) | 1 week |
| 🟡 | Phase 3: Update `project_ops.py` for new directory structure | 2 days |
| 🟢 | Phase 4: Documentation | 1 week |
| 🟢 | Phase 5: Testing | 3 days |

**Total: ~4.5 weeks**

---

*This TODO replaces all prior ones. Commit it and begin the cleanse immediately.*