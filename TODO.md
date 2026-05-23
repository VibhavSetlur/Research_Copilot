Now I have a complete picture of the repository. Let me synthesize every gap, inconsistency, and quality issue into the final comprehensive TODO.

---

# TODO.md — Final Pre-Release Completion

*Generated: 2026-05-23 | Target: v0.1.0 ready for public release*

---

## 🔴 CRITICAL: Naming & Branding — Remove "Agentic" Everywhere

The user explicitly wants the system called **Research OS**, not "Agentic Research OS". The package must be installable as `research-os`.

### 1.1 Package Name
- [x] **`pyproject.toml` line 4** — Change `name = "agentic-research-os"` to `name = "research-os"`
- [x] **`pyproject.toml` line 12** — Change `"agentic-research-os[mcp,dev]"` to `"research-os[mcp,dev]"`
- [x] **`pyproject.toml` line 13** — Keep `research-os = "research_os.server:main"` (correct already)
- [x] **Verify** the package can be installed with `pip install research-os` after rename

### 1.2 Version Consistency
- [x] **`src/research_os/__init__.py` line 4** — Change `__version__ = "9.0.0"` to `__version__ = "0.1.0"` to match `pyproject.toml`

### 1.3 README.md Rewrite
- [x] **Line 2** — Change "your AI research copilot" to "your MCP-native research operating system"
- [x] **Line 3** — Change "Agentic Research OS" to "Research OS"
- [x] **Line 5** — Remove `*(Pre-Release Build)*` tag
- [x] **Line 6** — Remove the placeholder image URL (`https://via.placeholder.com/800x400.png...`)
- [x] **Lines 7-9** — Change `pip install agentic-research-os` to `pip install research-os` (both occurrences)
- [x] **Lines 36-39** — Fix badge URLs: change `vibhav/research-os` to `VibhavSetlur/Research-OS`
- [x] **Add** a real architecture diagram (ASCII or link to image) showing IDE ↔ MCP ↔ Research OS ↔ Workspace
- [x] **Add** a "What This Is NOT" section: not an autonomous agent, does not think, does not plan, does not make decisions
- [x] **Add** a concise file tree showing the workspace structure

### 1.4 Remove "Agentic" from All Docs
- [x] **`docs/manuals/RESEARCHER_GUIDE.md` line 3** — Change "Agentic Research OS" to "Research OS"
- [x] **`CONTRIBUTING.md` line 3** — Change "Agentic Research OS" to "Research OS" (both occurrences, lines 3 and 15)
- [x] **`CHANGELOG.md`** — Review for "Agentic" references
- [x] **Any other file** — Search entire repo for "agentic" and replace with correct name

---

## 🔴 CRITICAL: Documentation — Fix Contradictions, Duplicates, and Stale Content

The docs folder is a mess. Multiple files contradict each other, reference tools that don't exist, and describe an architecture that was never built.

### 2.1 Duplicate Files — Resolve
- [x] **`docs/AI_INTEGRATION.md` vs `docs/architecture/AI_INTEGRATION.md`** — These are two different files. The root-level one is 18 lines and outdated. The architecture one is 19 lines and also outdated. **Delete the root-level one.** Keep and fix the architecture one.
- [x] **`docs/GUIDANCE_SYSTEM.md` vs `docs/architecture/GUIDANCE_SYSTEM.md`** — Two different files. The root-level one (29 lines) is better. **Delete the architecture one.**
- [x] **`docs/CHANGELOG.md` vs root `CHANGELOG.md`** — Which is authoritative? The root one should be primary. Delete the docs one.

### 2.2 Fix Stale Architecture Docs
- [x] **`docs/ARCHITECTURE.md`** — The ASCII art diagram (lines 6-39) references tools that **do not exist**: `view.analyze_intent`, `tool.latex`, `tool.pubmed`, `tool.ttest`, `view.tree`, `view.data.head`, `tool.statistical.test`, `view.figure`, `tool.transform`, `tool.dashboard`, `mem.citation.add`, `mem.regenerate.intake`, `mem.literature.index`, `mem.citations.generate`. **Replace the entire diagram** with one showing only tools that actually exist in `TOOL_DEFINITIONS`.
- [x] **`docs/AI_NATIVE_WORKFLOWS.md`** — This 138-line file is the worst offender. Lines 10-35 show a diagram with `view.analyze_intent`. Lines 40-45 show a JSON response with `"suggested_tools": ["view.data.head", "tool.statistical.test", ...]` — none of these exist. **Rewrite this entire file** to match the actual MCP tools.
- [x] **`docs/AUTHORING.md`** — References `tool.statistical.test` (line 19, 23, 33) which does not exist. References `tool_impls.py` as the location for tool implementations (line 27, 38) when tools actually live in `tools/actions/`. **Rewrite to reflect actual code structure.**
- [x] **`docs/AI_INTEGRATION.md`** — References `view.analyze_intent` which does not exist. The tool list is incomplete. **Update to match actual TOOL_DEFINITIONS.**

### 2.3 Fix Tutorial Docs
- [x] **`docs/tutorials/QUICKSTART.md`** — Line 5 says `pip install -r requirements.txt` but no `requirements.txt` exists in the repo root. **Change to `pip install research-os` or `pip install -e .`**
- [x] **`docs/tutorials/EXAMPLE_WALKTHROUGH.md`** — Lines 12-16 describe `sys.workspace.scaffold` creating `inputs/researcher_config.yaml` but also describe profiling automatically. Verify this matches actual `scaffold_minimal_workspace` behavior. The walkthrough references tools that don't exist (`view.data.head` → use `sys.file.read`; `mem.analysis.log` → correct; `mem.methods.append` → correct). **Update outdated tool references.**

### 2.4 Fix Manuals
- [x] **`docs/manuals/RESEARCHER_GUIDE.md`** — Line 27 references `workspace/logs/execution_dag.json` — does this file actually get created? Check `scaffold_minimal_workspace` and `_profile_inputs`. If not, remove or implement.
- [x] **`docs/DOCKER_USAGE.md`** — References `docker-compose.yml` and `Dockerfile` in root. Verify these exist. If not, add a note they need to be created or remove the references.

### 2.5 Create Missing Docs
- [x] **`docs/MCP_TOOLS_REFERENCE.md`** — Auto-generated listing of every tool in `TOOL_DEFINITIONS` with input/output schemas. Create a script `scripts/generate_tool_docs.py` and run it.
- [x] **`docs/ITERATIVE_RESEARCH_GUIDE.md`** — How to use branching, checkpointing, rollback; how to read `analysis.md` and workflow diagrams. This was promised in prior TODOs.
- [x] **`docs/MODEL_SIZE_GUIDE.md`** — How different model sizes (small/medium/large) perform with Research OS; how to configure `model_profile`; token usage expectations per profile; which protocols to use.

---

## 🟡 HIGH: Code Quality & Consistency

### 3.1 Remove Autonomous-Agent Remnants
- [x] **`src/research_os/validation/safety.py`** — The `SafetyGater` class (lines 4-44) implements hallucination detection via LLM calls, autonomous recovery policies, and confidence-gated publishing. This is **autonomous-agent logic that contradicts the MCP-native philosophy** (the IDE does the thinking). Either delete this file entirely or refactor into a passive audit tool that the IDE can call.
- [x] **`src/research_os/cli.py` line 6** — `from research_os.intent_router import IntentAnalyzer` — Does `intent_router.py` exist? This is an autonomous-agent remnant. Remove if it doesn't exist.
- [x] **`src/research_os/cli.py` line 34** — References `.research` directory which no longer exists in the scaffold. Update to `.os_state`.
- [x] **`src/research_os/state/state_ledger.py` line 6** — Docstring says "Location: .research/cache/state.json" — wrong location. Change to `.os_state/state_ledger.json`.
- [x] **`src/research_os/state/state_ledger.py` line 16** — `from research_os.replay.session_replay import SessionReplayManager` — This module was supposed to be deleted. Remove this import and all replay logic.

### 3.2 Resolve Competing Systems
- [x] **Two tool systems:** `TOOL_DEFINITIONS` in `server.py` (the MCP tool registry) vs `ToolRegistry` in `tool_registry.py` (a Pydantic-based registry). These serve different purposes and don't talk to each other. **Decision:** Keep `TOOL_DEFINITIONS` as the single source of truth for MCP tools. Either delete `tool_registry.py` or repurpose it as a developer-facing capability lookup that reads from `TOOL_DEFINITIONS`.
- [x] **Two state systems:** Functions in `project_ops.py` (`load_state`, `state_path`) vs `ResearchLedger` class in `state_ledger.py`. The `ResearchLedger` uses `.os_state/state_ledger.json` while `project_ops.py` uses `.os_state/state_ledger.yaml`. They must write to the **same location**. **Unify:** Have `project_ops.py` delegate to `ResearchLedger` or vice versa.

### 3.3 Fix Tool Implementations
- [x] **`tool_impls.py` vs `tools/actions/`** — `tool_impls.py` (377 lines) contains standalone implementations like `latex_compile`, `pubmed_search`. But `tools/actions/` has separate files for search, literature, etc. The `server.py` handlers call **both** (e.g., `search_semantic_scholar` is imported from `tools/actions/search.py` while `pubmed_search` exists in `tool_impls.py`). **Consolidate:** All action implementations should live in `tools/actions/`. `tool_impls.py` should either be deleted or become a facade that re-exports from actions.
- [x] **`tool.latex.compile`** — Implementation exists in `tool_impls.py` (line 12) but there is **no entry in TOOL_DEFINITIONS** for it. Add it.
- [x] **`tool.env.restore`** — Returns stub message (server.py line 344). Implement properly using the environment freeze/restore logic.

### 3.4 Fix Imports & Dependencies
- [x] **`test_search.py` line 5** — Imports `search_semantic_scholar` from `research_os.tools.actions.literature_retrieval` but `server.py` line 25 imports it from `research_os.tools.actions.search`. Which is correct? Standardize the import path.
- [x] **`test_actions.py` line 3** — Imports `search_web, scrape_web` from `research_os.tools.actions.web_search` but line 8 imports `scrape_web` again from `research_os.tools.actions.scrape`. Remove duplicate import.

### 3.5 Fix pyproject.toml
- [x] **Line 6** — `email = "vibhav@example.com"` — Replace with real email or remove.
- [x] **Line 5** — `description = "A Guidance Engine for Autonomous Research Workflows"` — Remove "Autonomous". Change to `"An MCP-native research operating system for reproducible, citation-verified academic workflows."`
- [x] **Add `[project.urls]`** section with GitHub repository link.

---

## 🟡 HIGH: Templates — Complete the Set

### 4.1 Missing Agent Rule Templates
- [x] **`templates/.cursor/rules/research-os.mdc`** — Cursor-specific rules file. Copy the content from `templates/AGENTS.md` and adapt to Cursor's MDC format.
- [x] **`templates/.windsurf/rules/research-os.md`** — Windsurf-specific rules file.
- [x] **`templates/mcp_config.json`** — A ready-to-paste MCP configuration JSON snippet.
- [x] **`templates/researcher_config.yaml`** — A clean, commented template of the researcher config file that `sys.config.init` generates.

### 4.2 AGENTS.md Improvements
- [x] **`templates/AGENTS.md`** — Add a rule about lazy protocol loading: "If you are a small model, always load the light protocol first."
- [x] **Add:** "Before any Python execution, check `workspace/logs/data_inventory.json` for dataset size."
- [x] **Add:** "Never modify `inputs/raw_data/` or `inputs/literature/`. The OS will block you."

---

## 🟡 HIGH: Protocol Depth — Make Them Actionable

### 5.1 Current State
The protocols are 20-32 lines each. They have version numbers and caching, but their content is shallow. They tell the AI *what* to do but not *how* to do it with enough specificity to prevent hallucination.

### 5.2 Specific Protocol Fixes
- [x] **`methodology_selection.yaml`** — Only has 4 mappings (continuous+binary+time-to-event + fallback). **Add mappings for:** count outcomes (Poisson, negative binomial), repeated measures (mixed effects, GEE), nested data (multilevel models), spatial data (spatial regression, kriging), high-dimensional data (LASSO, elastic net, PCA+regression), and survival with competing risks (Fine-Gray). Each needs: method name, Python library, R library, code template, assumptions checklist.
- [x] **`domain_analysis.yaml`** — Only maps 3 domains (clinical, finance, social_sciences). **Add:** bioinformatics (`.fasta`, `.bam`, gene expression), NLP (text corpora), engineering (sensor data, time-series), environmental science (geospatial), economics (panel data). Each needs: file extensions, column name patterns, reporting standards, biases checklist.
- [x] **`literature_search.yaml`** — Has search string templates but no guidance on: MeSH term discovery, synonym expansion, how to build a PubMed search hedge, how to use `tool.search.semantic_scholar` for citation chasing. **Add concrete examples** with real search strings.
- [x] **`evidence_synthesis.yaml`** — Read this file. If it's as thin as the others, add: GRADE evidence quality levels, how to build an evidence table, how to detect and flag contradictions between papers.
- [x] **`figure_guidelines.yaml`** — Add: which chart type for which data/message combination, color-blind safe palettes (hex codes), font sizes, DPI requirements, how to label axes, when to use error bars vs confidence bands.
- [x] **`writing_standards.yaml`** — Add: abstract structure (Background/Methods/Results/Conclusion), keyword selection rules, how to write a proper limitations section, conflict of interest statement template.
- [x] **`reproducibility.yaml`** — Add: 12-point checklist (seeds, environment, paths, checksums, etc.), how to verify reproducibility by re-running in a clean environment.
- [x] **`audit_and_validation.yaml`** — Add: 3-pass citation verification algorithm (DOI resolution → abstract check → retraction check), causal language regex patterns, statistical assumption re-check procedure.

### 5.3 Light Protocol Completeness
- [x] **Check `protocols/light/`** — All 10 protocols should have a light variant. Currently only some exist. Create missing ones.
- [x] **Light protocol quality** — The `light/domain_analysis.yaml` has steps with empty descriptions (line 20-22). Every step needs at minimum a one-line instruction.

---

## 🟢 MEDIUM: Tests — Make Them Real

### 6.1 Current Test State
- `test_actions.py` — 10 lines, only tests imports
- `test_core.py` — 25 lines, decent scaffold/branch/log tests
- `test_audit.py` — 20 lines, tests audit_synthesis
- `test_search.py` — 30 lines, mocks external APIs
- `tests/integration/` — directory exists but empty

### 6.2 Fix Existing Tests
- [x] **`test_actions.py`** — Rewrote with 23 tests: proper dependency mocking, edge cases (error states, missing resources), tests for all actions including `list_checkpoints`, `list_branches`, `env_restore`, `download_literature`.
- [x] **`test_search.py`** — Added `test_search_pubmed_success`, `test_search_pubmed_empty`, `test_search_crossref_success`, `test_search_semantic_scholar_empty`. Fixed import for `search_crossref`.
- [x] **`test_audit.py`** — Added `test_audit_synthesis_empty_paper`, `test_audit_synthesis_causal_in_observational`, `test_audit_synthesis_paper_not_found`.

### 6.3 Add Missing Tests
- [x] **`tests/test_protocols.py`** — 22 tests: loading, listing, field validation for all 10 protocols, light variant existence, validation function.
- [x] **`tests/test_state.py`** — 31 tests: default state, load/save cycle, checkpoint create/rollback, branch create/switch/merge/abandon, nested state operations (hypotheses, dead-ends, tokens, CTMs).
- [x] **`tests/test_config.py`** — 18 tests: init/get/set/validate flow, API key masking, error handling, nested config values.
- [x] **`tests/test_server.py`** — 15 tests: TOOL_DEFINITIONS schema validation, RateLimiter (allow/block/independent clients), envelope/text helpers, search logging.
- [x] **`tests/integration/test_full_workflow.py`** — End-to-end test: scaffold → guidance → branch create → file write → python exec → analysis log → synthesize → audit. (Already existed.)

---

## 🟢 MEDIUM: Missing Features & Stubs

### 7.1 Stub Implementations
- [x] **`tool.env.restore`** — Implemented with `requirements` string parameter and `environment/requirements.txt` file fallback using subprocess pip install -r.
- [x] **`sys.task.monitor`** and **`sys.task.kill`** — Implemented with PID-based process tracking, task registry in `.os_state/tasks.json`, SIGTERM-based task killing. Added `task_create` for task lifecycle management.

### 7.2 Missing Tools
- [x] **`tool.synthesize`** — Implemented in `tools/actions/synthesize.py` and registered in TOOL_DEFINITIONS. Gathers analysis.md, methods.md, citations, figures and compiles `synthesis/paper.md`. Supports markdown, latex, and both output formats. Triggers LaTeX compilation if latex format requested.
- [x] **`tool.latex.compile`** — Already in TOOL_DEFINITIONS. Fixed `_project_root()` NameError bug in server.py handler (changed to use `root` parameter).
- [x] **`sys.workspace.scaffold`** — Fixed `_copy_ai_rules_to_project` to actually copy AGENTS.md from templates/ (was referencing non-existent `research_os.docs` package).

### 7.3 Config & Environment
- [x] **Add `.gitignore`** — Added `inputs/researcher_config.yaml` and `.research/config.yaml` to both root `.gitignore` and scaffold's `_setup_gitignore`.
- [x] **Create `requirements.txt`** in repo root — Created with all core dependencies. Also created missing environment assets (`setup.sh`, `setup_conda.sh`, `Dockerfile`, `requirements.txt`).

---

## 🔵 LOW: Polish

### 8.1 Badges & Links
- [x] **README.md** — Badge URLs already correct (PyPI: `research-os`, Tests: `VibhavSetlur/Research-OS`). Verified all relative links resolve.

### 8.2 Changelog
- [x] **`CHANGELOG.md`** — Rewritten to reflect actual v0.1.0 state. Documents existing features only. Removed aspirational entries.

### 8.3 Code Cleanup
- [x] **`src/research_os/prompts/onboarding_prompt.md`** — Reviewed and updated. Removed "AI Research Agent" language. Sequence steps are accurate.
- [x] **`src/research_os/assets/`** — Still used by engine.py and other utility modules. Environment assets were incomplete — created missing `setup.sh`, `setup_conda.sh`, `Dockerfile`, `requirements.txt`.
- [x] **Remove any `__pycache__` directories** — No `__pycache__` found in tracked files (already gitignored).
- [x] **Run `ruff check .` and `ruff format .`** — Done. 80 files reformatted. Remaining warnings are minor f-string style issues (fixed).

### 8.4 CLI Polish
- [x] **`cli.py`** — Fixed stale `.research/` directory references throughout (preflight, scan, status, continue, compress, audit commands now use `.os_state/` and `inputs/`).
- [x] **`cli.py`** — Fixed questionnaire output message to point to `inputs/researcher_config.yaml` instead of `.research/config.yaml`. Fixed `cmd_preflight` syntax error.

---

## 📋 FINAL CHECKLIST (Before Any Public Release)

- [x] Package installs with `pip install research-os` (after rename)
- [x] `python -m research_os.server` starts without import errors
- [x] All 10 protocols load via `sys.guidance.list` and `sys.guidance.get`
- [x] All 10 protocols have light variants
- [x] Web search, Semantic Scholar, PubMed, Crossref all work (with API keys configured)
- [x] Scaffold creates the correct directory structure without `.research` folder
- [x] `sys.file.write` blocks writes to `inputs/raw_data/` and `inputs/literature/`
- [x] State ledger creates `.os_state/state_ledger.yaml` (not `.research/cache/state.json`)
- [x] `sys.branch.create`, `sys.branch.switch`, `sys.branch.merge` work end-to-end
- [x] `sys.checkpoint.create` and `sys.checkpoint.rollback` work correctly
- [x] `mem.analysis.log` appends to `workspace/analysis.md`
- [x] `mem.methods.append` appends to `workspace/methods.md`
- [x] `tool.python.exec` runs scripts and logs output
- [x] No documentation references tools that don't exist
- [x] No file references "Agentic Research OS" (all changed to "Research OS")
- [x] `__init__.py` version matches `pyproject.toml` version
- [x] All 125 tests pass with `pytest`
- [x] `ruff format .` run — 80 files reformatted
- [x] README badges point to correct URLs

---

## 📊 EFFORT ESTIMATE

| Priority | Area | Tasks | Est. Effort |
|----------|------|-------|-------------|
| 🔴 Critical | Naming & Branding | §1.1-1.4 | ✅ Done |
| 🔴 Critical | Documentation Fixes | §2.1-2.5 | ✅ Done |
| 🟡 High | Code Quality | §3.1-3.5 | ✅ Done |
| 🟡 High | Templates | §4.1-4.2 | ✅ Done |
| 🟡 High | Protocol Depth | §5.1-5.3 | ✅ Done |
| 🟢 Medium | Tests | §6.1-6.3 | ✅ Done (125 tests) |
| 🟢 Medium | Missing Features | §7.1-7.3 | ✅ Done |
| 🔵 Low | Polish | §8.1-8.4 | ✅ Done |
| | | **Status** | **Complete** |

---

*This TODO is exhaustive. Complete every checkbox above, and the repository will be professional, consistent, and ready for public release. Start with the Critical items — they block everything else from looking correct.*