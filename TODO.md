I have now completed my thorough review of the repository. Here is the comprehensive final TODO.

---

# TODO.md — Final Pre-Release Completion

*Generated: 2026-05-23 | Target: v0.1.0 — fully ready for public release*

---

## 🔴 CRITICAL: Delete `.research/` — Autonomous-Agent Config Still Exists

The directory `.research/config.yaml` (20 lines) remains in the repository. Its content is entirely wrong for the MCP-native architecture: it references `rcp init` (old CLI name), `schema_version: 9.0.0`, `intent_routing`, `knowledge_graph`, `semantic_filesystem`, `interpretative_coupling`, `branching.enabled: true`, `default_workflow: quick_exploratory` — all concepts from the deleted autonomous-agent code. This directory **must not exist** in the repository.

- [ ] **Delete `.research/` directory entirely** — this includes `.research/config.yaml`. Project config now lives exclusively in `inputs/researcher_config.yaml`.
- [ ] **Verify `.gitignore`** already ignores `.os_state/` (it does, line 222) so the actual OS state is not committed by accident.

---

## 🔴 CRITICAL: Fix `.env.example` — Remove LLM Provider Keys

`.env.example` (18 lines) lists `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` as "Required: Core LLM Provider" with instructions to obtain them from platform.openai.com and console.anthropic.com. **Research OS does not use LLM provider keys.** The intelligence comes from the user's AI IDE (Cursor, Claude Code, Antigravity, etc.). The researcher never configures an LLM provider through Research OS.

- [ ] **Remove `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` sections entirely.**
- [ ] **Keep only the "External Research Tools" section** — `SEMANTIC_SCHOLAR_API_KEY`, `CROSSREF_API_KEY` (mailto), `NCBI_API_KEY`.
- [ ] **Add `FIRECRAWL_API_KEY`** — this is the primary web search backend and the most important API key for the system.
- [ ] **Add `SERPAPI_API_KEY`** — the fallback web search backend.
- [ ] **Header comment should read:** `# Research OS — External Research API Keys`.

---

## 🔴 CRITICAL: Implement `sys.path.*` Tools (Replace Branch System)

**The Problem:** Throughout the documentation (`AGENTS.md` lines 24-26, `RESEARCHER_GUIDE.md` lines 21-24, `WORKSPACE_TAXONOMY.md` lines 41-44) the system references `sys.path.create`, `sys.path.abandon`, and `sys.path.list` — a path-based chronological experiment system. **However, these tools do not exist in the codebase.** The `sys.branch.*` tools (`sys.branch.create`, `sys.branch.switch`, `sys.branch.list`, `sys.branch.merge`) still live in `TOOL_DEFINITIONS` (server.py lines 103-115) and have handler implementations (server.py lines 285-296). This is a **documentation-to-code mismatch** that would break any AI agent trying to follow the documented workflow.

### Required Changes:

- [ ] **Create `src/research_os/tools/actions/path.py`** with three functions:
  - `create_path(name: str, root: Path) -> dict` — Auto-increments the experiment number (looks at existing `0x_*` dirs), creates `workspace/<next_number>_<name>/` with full sub-structure (README.md, conclusions.md, data/, scripts/, outputs/reports/, outputs/figures/, outputs/tables/, outputs/dashboards/, environment/).
  - `abandon_path(path_name: str, rationale: str, root: Path) -> dict` — Renames the numbered directory (e.g., `02_data_preparation/` → `02_data_preparation__DEAD_END/`), appends the abandonment rationale to `workspace/analysis.md`. Files are preserved, not deleted.
  - `list_paths(root: Path) -> dict` — Returns all numbered experiment directories with their status (active, completed, dead_end, abandoned).

- [ ] **Add to `TOOL_DEFINITIONS` in `server.py`:**
  - `sys.path.create` — category: workspace
  - `sys.path.abandon` — category: workspace
  - `sys.path.list` — category: workspace

- [ ] **Remove `sys.branch.*` tools from `TOOL_DEFINITIONS`** (sys.branch.create, sys.branch.switch, sys.branch.list, sys.branch.merge).

- [ ] **Remove branch handler code from `_handle_tool_call`** in server.py (lines 285-296).

- [ ] **Remove `create_experiment_branch` import** from server.py line 10 (`from research_os.project_ops import create_experiment_branch`).

- [ ] **Remove `switch_branch, merge_branches, list_branches` imports** from server.py lines 16-17.

- [ ] **Update `project_ops.py`:**
  - Remove `create_experiment_branch` function (lines 274-297+) and its helper `_ensure_branch_dir` (lines 89-94).
  - Remove `next_experiment_id` function (lines 84-88) — it generates `exp_001_` style IDs, not `0x_` style.
  - Remove branch-related state logic from `default_state()` (lines 60-67) — the `current_branch` and `branches` dict.

- [ ] **Update `state_ledger.yaml` format** — Replace `current_branch` and `branches` with `current_path` and `paths` list.

- [ ] **Fix `EXAMPLE_WALKTHROUGH.md`** (lines 37-50): Replace all references to `sys.branch.create`, `sys.branch.merge`, "branch context" with `sys.path.create`, `sys.path.abandon`, and path-based chronological steps. Fix line 40-41 which shows:
  ```
  sys.branch.create:
  - name: exp_bayesian_model
  - hypothesis: "A Bayesian hierarchical model..."
  ```
  Should show `sys.path.create` with `name: "bayesian_model"` creating `03_bayesian_model/`.

---

## 🔴 CRITICAL: Fix GitHub Repository Settings

### About Section
- [ ] **Change repository description** from *"A self-healing, citation-verified AI research engine using a multi-agent package-to-local workflow with 28+ native MCP tools and automated Context Token Management (CTM)."* to *"An MCP-native research operating system for reproducible, citation-verified academic workflows."*
- [ ] **Remove "multi-agent"** — the system is explicitly NOT multi-agent anymore.

### Topics
- [ ] **Review topics:** `ai-agents-framework` and `agentic-workflows` are misleading since the system is explicitly not agentic. Consider replacing with `mcp-server`, `reproducibility-research`, `research-automation`.
- [ ] **Add `research-os` topic.**

### Website / Link
- [ ] The repository links to `github.com/VibhavSetlur/research-copilot` in the About section — this is the old repository. Update to the current one or remove.

### Enable Community Features
- [ ] **Enable GitHub Discussions** — Settings → General → Features → Discussions. This allows researchers to ask questions, share workflows, and provide feedback.
- [ ] **Enable Issues** (already enabled — issue templates exist).

---

## 🟡 HIGH: Fix CITATION.cff Version

`CITATION.cff` (6 lines) has `version: 1.0.0` but `pyproject.toml` and `__init__.py` both use `0.1.0`.

- [ ] **Change `version: 1.0.0` to `version: 0.1.0`** in CITATION.cff.

---

## 🟡 HIGH: Fix `AI_INTEGRATION.md` — "Autonomous AI Researchers"

`docs/architecture/AI_INTEGRATION.md` (19 lines) opens with: *"Research OS is designed to be the foundational operating system for Autonomous AI Researchers."* This directly contradicts the README's "What This Is NOT" section and the MCP-native philosophy.

- [ ] **Rewrite the opening line** to: *"Research OS is an MCP-native operating system for AI-assisted research. It provides the Hands, Eyes, and Memory — the AI IDE (Cursor, Claude, Antigravity) provides the intelligence."*
- [ ] **Expand the document** — 19 lines is too thin for an integration guide. Add sections: Connection Configuration (JSON snippets for each IDE), Tool Discovery Pattern, Protocol Loading, Error Handling.

---

## 🟡 HIGH: Fix `config.py` — Remove `openai` API Key

`src/research_os/tools/actions/config.py` line 32 includes `"openai": ""` in the default config template. Research OS does not use OpenAI keys — the AI IDE handles the LLM.

- [ ] **Remove `"openai": ""`** from the default config dict.
- [ ] **Add `"semantic_scholar": ""`, `"pubmed": ""`, `"crossref": ""`, `"serpapi": ""`** to the api_keys section.

---

## 🟡 HIGH: Missing `tool.synthesize` Handler

`TOOL_DEFINITIONS` in server.py (lines 190-196) defines `tool.synthesize` but there is **no handler** for it in `_handle_tool_call`. An AI calling this tool would get no response.

- [ ] **Add handler for `tool.synthesize`** in `_handle_tool_call` in server.py. At minimum, gather `workspace/analysis.md`, `workspace/methods.md`, `workspace/citations.md` content and write `synthesis/paper.md`. The handler should call a `synthesize()` function from a new `tools/actions/synthesize.py`.

---

## 🟡 HIGH: Fix `project_ops.py` — Old Data Paths

- [ ] **`compute_input_hashes` function (lines 78-84)** references `workspace/data/raw` and `workspace/data/derived` — these are old paths. Data now lives in `inputs/raw_data/` (immutable) and `workspace/<step>/data/` (derived). Update the function.
- [ ] **`_update_workspace_readme_manifest` function (lines 264-274)** references the same old paths. Fix or delete if unused.
- [ ] **`scaffold_minimal_workspace`** creates `workspace/01_experiment_baseline/` correctly (lines 168-171). Good — no changes needed here.

---

## 🟡 HIGH: Several `TOOL_DEFINITIONS` Missing `category`

Two tools in `TOOL_DEFINITIONS` are missing the `category` field:

- [ ] **`tool.env.restore`** (line 178) — add `"category": "execution"`.
- [ ] **`tool.latex.compile`** (line 180) — add `"category": "execution"`.

---

## 🟢 MEDIUM: `AGENTS.md` References `tool.log.decision`

`AGENTS.md` (line 15) says agents must use `tool.log.decision` to log methodological decisions. This tool exists in `TOOL_DEFINITIONS` (lines 187-190) and has a handler — **but verify the handler is complete**. The handler should write to `workspace/analysis.md` in a structured format.

- [ ] **Check that `tool.log.decision` handler exists** in `_handle_tool_call`. If not, add it.

---

## 🟢 MEDIUM: Example Walkthrough Path Fixes

`EXAMPLE_WALKTHROUGH.md` has additional issues beyond the branch references:

- [ ] **Line 23:** References `workspace/scripts/01_eda.py` — scripts should be inside the experiment step: `workspace/01_experiment_baseline/scripts/01_eda.py`.
- [ ] **Line 31:** References `workspace/data/derived/cleaned_trial_data.csv` — should be `workspace/01_experiment_baseline/data/cleaned_trial_data.csv`.
- [ ] **Line 51:** References `synthesis/report.md` — should be `synthesis/paper.md` or `synthesis/paper.pdf`.

---

## 🟢 MEDIUM: `Dockerfile` Enhancement

The Dockerfile (9 lines) is functional but thin for a research system.

- [ ] **Add `requirements.txt` installation** — currently only installs `pyproject.toml` dependencies.
- [ ] **Add common research libraries** — `numpy`, `scipy`, `pandas`, `matplotlib`, `seaborn`, `scikit-learn`.
- [ ] **Add `mermaid-cli` (mmdc)** for workflow diagram rendering: `RUN npm install -g @mermaid-js/mermaid-cli`.

---

## 🟢 MEDIUM: Add `tool.synthesize` Handler

As identified above, the `tool.synthesize` definition exists but no handler.

- [ ] **Create `src/research_os/tools/actions/synthesize.py`** with a `synthesize()` function.
- [ ] **Function should:**
  1. Read `workspace/analysis.md`, `workspace/methods.md`, `workspace/citations.md`.
  2. Combine into a structured markdown paper in `synthesis/paper.md`.
  3. Optionally compile to LaTeX/PDF via `tool.latex.compile`.

---

## 🔵 LOW: Version Consistency

- [ ] **Verify `src/research_os/__init__.py`** has `__version__ = "0.1.0"` (not `9.0.0`).
- [ ] **Verify `schema_version`** in `default_state()` (project_ops.py line 61) is `"2.0"` or appropriate — currently `"2.0"`.
- [ ] **Verify `schema_version`** in `researcher_config.yaml` template (project_ops.py line 143) is consistent — currently `"10.0.0"` which seems wrong for v0.1.0. Change to `"0.1.0"`.

---

## 🔵 LOW: Pre-Commit Config

`.pre-commit-config.yaml` exists in the repository. If the user doesn't want it:

- [ ] **Either delete `.pre-commit-config.yaml`** or ensure it's documented in CONTRIBUTING.md.

---

## 📋 FINAL VALIDATION CHECKLIST (Before v0.1.0 Release)

- [ ] `.research/` directory deleted
- [ ] `.env.example` has NO LLM provider keys
- [ ] `sys.path.create`, `sys.path.abandon`, `sys.path.list` implemented and functional
- [ ] `sys.branch.*` tools removed from TOOL_DEFINITIONS and handlers
- [ ] `EXAMPLE_WALKTHROUGH.md` references path-based system only
- [ ] GitHub About: no "multi-agent", no "agentic-workflows"
- [ ] CITATION.cff version: `0.1.0`
- [ ] `AI_INTEGRATION.md`: no "Autonomous AI Researchers"
- [ ] `config.py`: no `openai` key in default config
- [ ] `tool.synthesize` handler implemented
- [ ] `tool.env.restore` and `tool.latex.compile` have `category` field
- [ ] `project_ops.py` old data paths updated
- [ ] All tests pass with `pytest`
- [ ] `ruff check .` returns clean
- [ ] Package installs with `pip install research-os`
- [ ] GitHub Discussions enabled
- [ ] Issue templates working (bug_report.md, feature_request.md)

---

## 📊 EFFORT ESTIMATE

| Priority | Area | Tasks | Est. Effort |
|----------|------|-------|-------------|
| 🔴 Critical | Delete .research/ | §1 | 30 min |
| 🔴 Critical | Fix .env.example | §2 | 30 min |
| 🔴 Critical | Implement sys.path.* + remove sys.branch.* | §3 | 5 hours |
| 🔴 Critical | Fix GitHub settings | §4 | 30 min |
| 🟡 High | CITATION.cff version | §5 | 5 min |
| 🟡 High | AI_INTEGRATION.md rewrite | §6 | 1 hour |
| 🟡 High | config.py remove openai | §7 | 30 min |
| 🟡 High | tool.synthesize handler | §8 | 2 hours |
| 🟡 High | project_ops.py old paths | §9 | 1 hour |
| 🟡 High | TOOL_DEFINITIONS categories | §10 | 10 min |
| 🟢 Medium | AGENTS.md tool.log.decision check | §11 | 30 min |
| 🟢 Medium | EXAMPLE_WALKTHROUGH paths | §12 | 1 hour |
| 🟢 Medium | Dockerfile enhancements | §13 | 30 min |
| 🔵 Low | Version consistency | §14 | 15 min |
| 🔵 Low | Pre-commit config | §15 | 5 min |
| | | **Total** | **~14 hours** |

---

*This TODO is the final pre-release checklist. Start with the Critical items — especially §3 (implement sys.path.*) which is the largest gap between what the documentation promises and what the codebase delivers. Once all items are checked, the repository is ready for v0.1.0 public release.*