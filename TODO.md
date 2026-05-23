Based on a thorough line‑by‑line review of the current `main` branch, here is the final, comprehensive TODO. It addresses every structural flaw, missing component, and quality gap that stands between the current codebase and a clean, usable public release.

---

# TODO.md — Final Pre‑Release Completion

*Generated: 2026‑05‑23 | Target: v0.1.0 public release*

---

## 🔴 CRITICAL: Fix the README — Incorrect Workspace Tree

The current `README.md` shows a tree (lines 20‑22) that is wrong and misleading:

```
workspace/
├── .os_state/          # state_ledger.json
├── inputs/             # literature/ and raw_data/
├── methodology/        # protocols/
├── src/                # ← WRONG — does not exist in user workspace
├── synthesis/
└── workspace_logs/     # ← WRONG — logs are workspace/logs/
    └── analysis.md
```

**Required changes:**

- [ ] **Replace the entire Workspace File Tree section** with the correct structure:
  ```text
  <user-project>/
  ├── AGENTS.md                       # AI agent instructions
  ├── README.md                       # Auto-generated project overview
  ├── .cursor/rules/research-os.mdc   # Cursor-specific rules
  ├── .os_state/                      # INTERNAL — OS state
  │   ├── state_ledger.yaml           # Source of truth
  │   ├── manifest.json               # Full file inventory with checksums
  │   ├── checkpoints/                # Workspace snapshots
  │   └── cache/                      # API response cache
  ├── docs/                           # Human-written research docs
  │   ├── research_question.md
  │   ├── hypotheses.md
  │   └── glossary.md
  ├── inputs/                         # IMMUTABLE — researcher provided
  │   ├── researcher_config.yaml      # Researcher preferences & API keys
  │   ├── raw_data/                   # Source data (or symlinks)
  │   ├── literature/                 # PDFs
  │   ├── context/                    # Notes, past results, text files
  │   ├── intake.md                   # Auto-generated research brief
  │   └── literature_index.yaml       # Filename → citation key mapping
  ├── workspace/                      # ACTIVE — iterative experiments
  │   ├── methods.md                  # Append‑only method log
  │   ├── analysis.md                 # Chronological log + Mermaid workflow
  │   ├── citations.md                # Running bibliography with verified flags
  │   ├── workflow.mermaid            # Auto‑updated workflow diagram
  │   ├── workflow.png                # Rendered diagram
  │   ├── logs/                       # Execution logs
  │   │   ├── searches.log            # Every web search logged (JSON lines)
  │   │   ├── state_changes.log       # Before/after state diffs
  │   │   ├── notifications.log       # Researcher notifications
  │   │   ├── data_inventory.json     # Auto‑profiled data inventory
  │   │   └── 01_baseline.log         # Per‑step execution logs
  │   ├── 01_experiment_baseline/
  │   │   ├── README.md               # Goal, hypotheses, outcomes
  │   │   ├── conclusions.md          # Key findings, bugs, routing decisions
  │   │   ├── methods_research.md     # AI's research into methods for this step
  │   │   ├── data/                   # Derived data
  │   │   ├── scripts/                # Versioned (01_load_v1.py, 02_eda_v1.py)
  │   │   ├── outputs/
  │   │   │   ├── reports/
  │   │   │   ├── figures/
  │   │   │   ├── tables/
  │   │   │   └── dashboards/
  │   │   └── environment/            # Pinned dependencies
  │   ├── 02_data_preparation/
  │   │   └── ... (same structure)
  │   └── .os_state/                  # Symlink to root .os_state/
  ├── synthesis/                      # FINAL — populated on completion
  │   ├── abstract.md
  │   ├── paper.tex / paper.pdf
  │   ├── references.bib
  │   ├── workflow_diagram.png
  │   └── supplementary/
  └── environment/                    # Global environment
      ├── requirements.txt
      └── Dockerfile
  ```
- [ ] **Remove mentions of `src/`, `methodology/`, `workspace_logs/`** from the tree.
- [ ] **Remove mentions of `sys.branch.create` as "isolated experimentation"** — replace with explanation of numbered chronological steps and path system (see §5 below).

---

## 🔴 CRITICAL: Delete or Completely Rewrite `engine.py`

`src/research_os/engine.py` is a 195‑line, 20KB autonomous‑agent execution engine that contradicts the entire MCP‑native philosophy. It contains:

- **DAG node execution** with dead‑end auto‑recovery (lines 44‑67)
- **HITL "Explain‑to‑Proceed" gates** that pause for user approval (line 17: `_HITL_INTENTS`)
- **LLM callback integration** (`call_llm` parameter on line 88)
- **Imports from deleted directories** (`runtime/hooks.py`, `intent_router.py`, `schemas/validator.py`)
- **A ResearchLedger that writes to a hardcoded `03_synthesis/state_ledger.json`** path (line 31‑32)
- **References to `.research/cache/`** (line 170)

**Required action:**

- [ ] **Delete `engine.py` entirely.** It has no place in an MCP‑native server where the IDE does the thinking.
- [ ] **Check all imports across the codebase for `from research_os.engine import`** and remove them.
- [ ] **Check `src/research_os/__init__.py`** to ensure it does not import or expose `ResearchEngine`.

---

## 🔴 CRITICAL: Fix Scaffold to Build the Correct User Workspace

`scaffold_minimal_workspace()` in `project_ops.py` creates a structure that does not match what the user specified. Specific issues:

### 3.1 Wrong directory layout

- [ ] **`workspace/data/derived/`** — The function creates `workspace/data/derived/` at the top level (line 122‑123). This should not exist. Derived data belongs inside each numbered experiment step (`01_experiment_baseline/data/`).
- [ ] **`workspace/scripts/`** — Creates scripts at the top level (line 126). Scripts belong inside each experiment step (`01_experiment_baseline/scripts/`).
- [ ] **`workspace/figures/`, `workspace/reports/`, `workspace/dashboards/`** — Created as top‑level directories (lines 124‑127). These should be inside each numbered step's `outputs/` directory. Keep only `workspace/workflow.mermaid` and `workspace/workflow.png` at the top level.
- [ ] **`workspace/lab_notebook.md`** — Created (line 181‑186). This is redundant with `analysis.md` and `methods.md`. Remove.
- [ ] **`workspace/logs/decisions.yaml`** — Created (line 187‑194). Decisions should be logged into `workspace/analysis.md` via `mem.analysis.log`. Remove the separate `decisions.yaml`.
- [ ] **`workspace/.os_state` symlink** — Created correctly (lines 166‑170). Keep.

### 3.2 Config written to wrong location

- [ ] **Config written to `.os_state/config.yaml`** (line 152‑166) — Config should be written to `inputs/researcher_config.yaml` as the user specified. The `.os_state/` directory should only contain the state ledger, manifest, checkpoints, and cache — not user‑facing config.
- [ ] **Remove `llm_provider` field** from config (line 160) — No LLM provider is needed because the IDE AI is the intelligence. The researcher does not configure an LLM provider through Research OS.
- [ ] **Remove `branching: enabled: true`** from config (line 160) — The system uses chronological numbered steps, not git‑style branches. The config should reflect the path‑based system.

### 3.3 Missing directories and files

- [ ] **No `inputs/researcher_config.yaml` created** — The scaffold must create this file from a template, not write config to `.os_state/`.
- [ ] **No `workspace/citations.md` created** — Code exists at lines 140‑142 but needs to be verified that it actually writes.
- [ ] **No per‑step experiment structure created** — The scaffold should create `workspace/01_experiment_baseline/` with its full sub‑structure (README.md, data/, scripts/, outputs/, environment/) as a template for the first experiment.
- [ ] **No `workspace/workflow.mermaid` created** — Should be initialized with a starting graph node.

### 3.4 Git auto‑init

- [ ] **`_initialize_git()`** (lines 204‑209) auto‑runs `git init`, `git add .`, and `git commit` on the user's project. This is dangerous and presumptuous. **Either remove entirely or make it optional** with a prompt to the researcher via the IDE.

---

## 🟡 HIGH: Docs Folder — Massive Cleanup Required

The `docs/` directory has **24 files** across 3 subdirectories. Many are thin stubs, duplicates, or contradict the actual architecture.

### 4.1 Files to DELETE (thin stubs or duplicates)

- [ ] **`docs/AI_NATIVE_WORKFLOWS.md`** (4.5KB) — References tools that don't exist (`view.analyze_intent`, `tool.statistical.test`). Describes an autonomous‑agent workflow. Delete.
- [ ] **`docs/AUTHORING.md`** (2.8KB) — References `tool_impls.py` as the location for tools (wrong — tools live in `tools/actions/`). References non‑existent tools. Delete or rewrite.
- [ ] **`docs/AUTHORING_TOOLS.md`** (2KB) — Another authoring document. Merge into `AUTHORING.md` or delete the duplicate.
- [ ] **`docs/DOCKER_USAGE.md`** (2.1KB) — If a Dockerfile doesn't exist in root, remove references or create one.
- [ ] **`docs/EXAMPLE_WALKTHROUGH.md`** (1.7KB) — Only 1.7KB. Too thin to be useful. Either expand to a full walkthrough or merge into `tutorials/EXAMPLE_WALKTHROUGH.md`.
- [ ] **`docs/GUIDANCE_SYSTEM.md`** (2KB) — Duplicate of `docs/architecture/GUIDANCE_SYSTEM.md`. Keep one, delete the other.
- [ ] **`docs/IDE_INTEGRATION.md`** (4.3KB) — Should live in `docs/tutorials/` or `docs/manuals/`, not at the top level.
- [ ] **`docs/INSTALLATION.md`** (5KB) — Merge into `QUICKSTART.md` or keep as a standalone but ensure it doesn't duplicate.
- [ ] **`docs/ITERATIVE_RESEARCH_GUIDE.md`** (1.6KB) — Too thin. Expand or merge into `RESEARCHER_GUIDE.md`.
- [ ] **`docs/MCP_CLIENTS.md`** (1.6KB) — Merge into `IDE_INTEGRATION.md`.
- [ ] **`docs/MCP_INTEGRATION.md`** (5KB) — Duplicate of `IDE_INTEGRATION.md` concepts. Merge.
- [ ] **`docs/MODEL_SIZE_GUIDE.md`** (2KB) — Thin. Expand or merge into `RESEARCHER_GUIDE.md`.
- [ ] **`docs/SKILLS.md`** (1.8KB) — References old skills system. Delete or rewrite for protocol‑based guidance.
- [ ] **`docs/WORKSPACE_TAXONOMY.md`** (7.7KB) — This is the most important doc. Verify it shows the correct tree structure (not the one with `src/` and `methodology/`).

### 4.2 Final docs/ structure

After cleanup, the `docs/` folder should have exactly:

```
docs/
├── QUICKSTART.md                   # 5‑minute setup
├── INSTALLATION.md                 # Detailed installation
├── RESEARCHER_GUIDE.md             # Operational manual
├── WORKSPACE_TAXONOMY.md           # Full directory tree explanation
├── MCP_TOOLS_REFERENCE.md          # Auto‑generated tool reference
├── architecture/
│   ├── ARCHITECTURE.md             # System architecture
│   ├── AI_INTEGRATION.md           # How IDEs talk to Research OS
│   └── GUIDANCE_SYSTEM.md          # Protocol system explanation
├── tutorials/
│   ├── EXAMPLE_WALKTHROUGH.md      # Full mock research session
│   └── MODEL_SIZE_GUIDE.md         # Model‑size optimization
└── manuals/
    └── RESEARCHER_GUIDE.md         # (or keep at top level)
```

- [ ] **Reorganize all files into this structure.** Delete everything else.
- [ ] **Ensure every remaining doc has accurate content** — no references to non‑existent tools, no descriptions of autonomous‑agent behavior, no stale directory paths.

---

## 🟡 HIGH: Templates — Missing Major IDE Templates

The `templates/` directory has:
- `AGENTS.md` ✓
- `mcp_config.json` ✓
- `.windsurf/` — should be removed (user said Windsurf is not a priority)
- **Missing:** `.cursor/rules/research-os.mdc`
- **Missing:** Claude Desktop rules
- **Missing:** Antigravity rules
- **Missing:** OpenCode/Codex rules

**Required changes:**

- [ ] **Delete `templates/.windsurf/`** — Not needed.
- [ ] **Create `templates/.cursor/rules/research-os.mdc`** — Cursor‑specific rules file with the same content as `AGENTS.md` adapted to MDC format.
- [ ] **Create `templates/.claude/rules/research-os.md`** — Claude Desktop / Claude Code rules.
- [ ] **Create `templates/.antigravity/rules/research-os.md`** — Antigravity rules.
- [ ] **Create `templates/opencode.json`** — OpenCode MCP config (exists in scaffold but not in templates).
- [ ] **Ensure `templates/mcp_config.json`** is correct and ready to copy‑paste.

---

## 🟡 HIGH: Replace Branch System with Path‑Based Chronological Steps

The user explicitly wants **no git branches** for research iteration. The current system (`create_experiment_branch`, `switch_branch`, `merge_branches`) implements git‑style branching with state tracking — this is the wrong model.

### 5.1 The correct model: Numbered chronological experiment paths

- Each experiment runs **consecutively**, not in parallel branches.
- Experiments are numbered: `01_experiment_baseline/`, `02_data_preparation/`, `03_hypothesis_testing/`, etc.
- If the researcher wants to abandon a path (e.g., after `02` and `03` they realize it's a dead end), they don't "delete" the folders — they **rename** them to indicate the path was stopped (e.g., `02_data_preparation__DEAD_END/`, `03_hypothesis_testing__ABANDONED/`) and create a new `04_alternative_approach/`.
- The `analysis.md` log records every path change, dead end, and reroute.

### 5.2 Required tool changes

- [ ] **Remove `sys.branch.create`, `sys.branch.switch`, `sys.branch.list`, `sys.branch.merge`** from `TOOL_DEFINITIONS` and from `tools/actions/branch.py`.
- [ ] **Replace with `sys.path.create`** — Creates the next numbered experiment directory (e.g., `workspace/02_data_preparation/`) with full sub‑structure.
- [ ] **Add `sys.path.abandon`** — Renames a path directory to indicate it's been stopped (e.g., appends `__ABANDONED__` or `__DEAD_END__`) and records the rationale in `analysis.md`. Files are preserved, not deleted.
- [ ] **Add `sys.path.list`** — Lists all experiment paths with their status (active, completed, abandoned, dead_end).
- [ ] **Update `state_ledger.yaml`** to track paths instead of branches:
  ```yaml
  current_path: "03_hypothesis_testing"
  paths:
    - id: "01_experiment_baseline"
      status: "completed"
    - id: "02_data_preparation"
      status: "abandoned"
      rationale: "Data quality insufficient for this approach"
    - id: "03_hypothesis_testing"
      status: "active"
  ```

### 5.3 Versioned scripts within each path

- [ ] **Scripts within each path are versioned** (e.g., `01_load_data_v1.py`, `01_load_data_v2.py`) — this is already the plan. The `sys.path.create` tool should create a `scripts/` directory with a `README.md` explaining the versioning convention.
- [ ] **No git branches are created for the researcher** — the OS should never run `git branch` or `git checkout`. The only git operation is the initial `git init` (if enabled).

---

## 🟡 HIGH: Remove or Repurpose Unused `src/research_os/` Directories

### 6.1 Empty or near‑empty directories

- [ ] **`src/research_os/assets/prompts/`** — Empty directory. Delete or populate with onboarding prompt templates.
- [ ] **`src/research_os/assets/data/`** — Empty directory. Delete.
- [ ] **`src/research_os/prompts/`** — Empty directory (separate from assets/prompts). Delete or consolidate.
- [ ] **`src/research_os/schemas/`** — Check contents. If only empty `__init__.py`, populate with actual JSON schemas for intake, analysis log, and synthesis output validation or delete.

### 6.2 `semantic_state.py` (state/semantic_state.py)

- [ ] **Evaluate `src/research_os/state/semantic_state.py`** — 1,370 bytes. If it's an incomplete semantic state layer that isn't wired into the MCP server, delete it. The state ledger is the single source of truth.

### 6.3 `engine.py` imports validation

- [ ] **`engine.py` imports from `runtime/hooks.py`, `intent_router.py`, `utils/asset_manager.py`, `utils/dag_manager.py`** — When deleting `engine.py`, verify these dependencies are not used elsewhere. If they are only used by `engine.py`, delete them too.

### 6.4 `.pre-commit-config.yaml`

- [ ] **Check `.pre-commit-config.yaml`** — This file exists in the repo root. If the researcher doesn't want pre‑commit hooks, remove it. If kept, ensure it's documented.

---

## 🟢 MEDIUM: Tests — Ensure They Don't Clutter & Add Missing Coverage

### 7.1 Current test quality

Tests use `tempfile.TemporaryDirectory()` which is correct — they don't pollute the real workspace. However:

- [ ] **`test_core.py`** — Only tests scaffold, branching, and log_decision (25 lines). Add tests for: `sys.path.create`, `sys.path.abandon`, `sys.path.list` (when implemented).
- [ ] **`test_state.py`** — 198 lines, comprehensive. Verify it tests the new path‑based system (not branches).
- [ ] **`test_protocols.py`** — 9.4KB. Good. Verify all 10 protocols load correctly.
- [ ] **`test_actions.py`** — 12KB. Verify all action imports are correct.
- [ ] **`tests/integration/`** — Empty directory. Add `test_full_workflow.py` that mocks an end‑to‑end research session.

### 7.2 Add scratch/ to .gitignore for tests

- [ ] **Ensure `.gitignore` includes `scratch/`** so test artifacts are never committed.
- [ ] **Verify all tests pass** with `pytest` after the structural changes above.

---

## 🟢 MEDIUM: Documentation Accuracy & Completeness

### 8.1 ARCHITECTURE.md

- [ ] **Replace ASCII diagram** — Current diagram (lines 6‑39) references non‑existent tools. Replace with a diagram showing the actual MCP tool categories: `sys.*`, `tool.*`, `mem.*`.
- [ ] **Remove references to autonomous agents**, supervisors, critics, planners.

### 8.2 RESEARCHER_GUIDE.md

- [ ] **Expand** to be an operational manual (currently 1.4KB — too thin).
- [ ] **Add sections:** First Project tutorial, populating `inputs/`, reading `analysis.md`, understanding `workflow.png`, troubleshooting common errors, config interview flow.
- [ ] **Remove any references** to `sys.branch.*` tools and replace with `sys.path.*` tools.

### 8.3 WORKSPACE_TAXONOMY.md

- [ ] **Verify** it shows the correct directory tree (as in §1 above).
- [ ] **Add explanation** of the path‑based chronological step system.

### 8.4 AGENTS.md

- [ ] **Add rule:** "If you are a small model, always load the light protocol first."
- [ ] **Add rule:** "Before any Python execution, check `workspace/logs/data_inventory.json` for dataset size."
- [ ] **Add rule:** "Never modify `inputs/raw_data/` or `inputs/literature/`. The OS will block you."
- [ ] **Add rule:** "Every factual claim must be backed by a `tool.search.*` call and the result logged to `workspace/logs/searches.log`."

---

## 🔵 LOW: Final Polish

### 9.1 Version consistency

- [ ] **`src/research_os/__init__.py`** — Version should be `0.1.0`, matching `pyproject.toml`.
- [ ] **`pyproject.toml`** — Package name should be `research-os` (already correct).

### 9.2 Badge URLs

- [ ] **Fix PyPI badge URL** in README.md — Should point to `research-os` package.
- [ ] **Fix tests badge URL** — Should point to `VibhavSetlur/Research-OS` (capitalization matters).

### 9.3 Remove placeholder content

- [ ] **README.md line 6** — Remove placeholder image URL.
- [ ] **README.md** — Remove `*(Pre-Release Build)*` tag.

### 9.4 Code quality

- [ ] **Run `ruff check .` and `ruff format .`** across the entire codebase.
- [ ] **Remove any `__pycache__/` directories** that may have been committed.

---

## 📋 FINAL CHECKLIST BEFORE RELEASE

- [ ] README shows correct workspace tree (no `src/`, no `methodology/`, no `workspace_logs/`)
- [ ] `engine.py` deleted or completely rewritten
- [ ] `scaffold_minimal_workspace()` builds the correct directory structure
- [ ] Config written to `inputs/researcher_config.yaml`, not `.os_state/config.yaml`
- [ ] No `llm_provider` in config
- [ ] Git auto‑init is optional or removed
- [ ] Docs folder reduced from 24 files to ~12 well‑organized files
- [ ] Templates cover Cursor, Claude, Antigravity, Codex
- [ ] Branch system replaced with path‑based chronological steps
- [ ] Empty asset directories deleted or populated
- [ ] All tests pass
- [ ] No documentation references non‑existent tools
- [ ] Package installs with `pip install research-os`
- [ ] `python -m research_os.server` starts without import errors

---

## 📊 EFFORT ESTIMATE

| Priority | Area | Tasks | Est. Effort |
|----------|------|-------|-------------|
| 🔴 Critical | README fix | §1 | 1 hour |
| 🔴 Critical | Delete/rewrite engine.py | §2 | 2 hours |
| 🔴 Critical | Scaffold rebuild | §3 | 5 hours |
| 🟡 High | Docs cleanup | §4 | 4 hours |
| 🟡 High | Templates | §5 | 2 hours |
| 🟡 High | Path system | §6 | 5 hours |
| 🟡 High | Unused directories | §7 | 2 hours |
| 🟢 Medium | Tests | §8 | 3 hours |
| 🟢 Medium | Doc accuracy | §9 | 3 hours |
| 🔵 Low | Polish | §10 | 2 hours |
| | | **Total** | **~29 hours** |

---

*This is the complete, final TODO. Start with the Critical items — the README tree and `engine.py` are actively misleading to anyone who clones the repository. Then rebuild the scaffold to create the correct user workspace, clean the docs, and implement the path‑based step system.*