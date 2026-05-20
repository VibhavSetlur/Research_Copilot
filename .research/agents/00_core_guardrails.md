# Core Guardrails

> Injected into every agent. Non-negotiable.

---

## 1. Cite Everything

Every methodological choice, interpretation, and claim needs a source. Hierarchy:
1. Domain standards (STROBE, APA, etc.)
2. Peer-reviewed methodology papers
3. Empirical literature in the domain
4. Statistical textbooks
5. Software docs

Format: `Decision: [what] | Source: [Author, Year, DOI] | Confidence: HIGH|MEDIUM|LOW`

## 2. Compare to Literature

After every finding, compare to what prior research found. If results differ, explain why.

## 3. Try to Disprove Yourself

After reaching a conclusion, ask: what would change my mind? Run at least one sensitivity check.

## 4. Iterate Only When Needed

Don't loop 3 times by default. Only iterate when:
- An assumption test fails
- A result contradicts well-established literature
- The finding is fragile (depends on arbitrary choices)
- Something is ambiguous

## 5. Methods Log

Every decision, pivot, or failure appends to `reports/logs/methods_log.md`:

```
---
Timestamp: {ISO 8601}
Agent: {agent}
Phase: {observe|test|validate|pivot}
Decision: {what was chosen}
Source: {Author, Year, DOI}
If PIVOT:
  Trigger: {what caused it}
  Alternative: {new approach}
---
```

## 6. Code Standards

- Python 3.10+, type hints, docstrings with methodological Notes
- Comments explain WHY (scientific reasoning), never WHAT
- Set random seeds before stochastic operations
- pip-installable packages preferred

## 7. Reporting

- No colloquial language
- Exact p-values with test stat, df, test name
- Effect sizes mandatory
- Confidence intervals for every estimate
- Non-significant results reported with same detail

## 8. Data Provenance

- `inputs/data/` is immutable
- Every output file: YAML frontmatter with producing_skill, agent, timestamp, input hashes

## 9. Figures

- 300 DPI, colorblind-safe palettes
- Diagnostic sub-panels per analysis type
- On-image statistical annotations

## 10. Tables

- Publication-ready, no vertical lines
- Significance in footnotes only
- Save as .md and .tex (booktabs)

## 11. Dead End Enforcement (MANDATORY)

BEFORE writing any new code, trying any new method, or choosing any new approach:

1. **Read ALL files in `docs/dead_ends/`** — understand what has already failed
2. **Check your planned approach against dead ends** — if it matches, DO NOT try it
3. **Choose a different approach** — document why the dead end was rejected
4. **If ALL approaches are dead ends** — report to user, do not loop infinitely

This prevents the agent from getting stuck in infinite loops, repeatedly trying the same
failed technique (e.g., Multiple Imputation, a specific model, a data cleaning method).

Dead ends are created when:
- An approach produces invalid results
- A method's assumptions are violated and cannot be fixed
- A technique fails to converge
- A result is contradicted by robustness checks
- The user explicitly rejects an approach

Format dead end entries as:
```
Approach: [what was tried]
Reason: [why it failed]
Date: [when]
Alternatives to try: [what to try instead]
```

## 12. State Ledger & Checkpoint System

The global research ledger (`.research/cache/state.json`) is the single source of truth.

- **Read state** before starting any phase: `research state`
- **Update state** after completing any phase using `ResearchLedger.complete_phase()`
- **Save checkpoints** at phase boundaries using `CheckpointManager.save()`
- **Resume** from failures: `research resume --from <phase>`
- **Never** skip state updates — every phase transition must be recorded

## 13. Token Budget Management

Monitor context window usage via the token budget in state.json.

- At 60%: summarize completed phases into 3-sentence abstracts
- At 80%: flush non-essential skill docs, keep only active skill
- At 90%: force checkpoint, split into new conversation with state transfer
- Check budget: `research budget`

## 14. Atomic Instruction Format

Every agent instruction must follow this format so any LLM can execute it without ambiguity:

1. EXACTLY ONE action per numbered step
2. Each step specifies: what to DO, what FILE to read, what FILE to write
3. No compound instructions ("do X and also Y and then Z")
4. Decision branches are IF/ELIF/ELSE, never ambiguous prose
5. Every output file has exact path and schema specified
6. Every input file has exact path specified
7. Verification: every step ends with a checkable condition

## 15. Anti-Hallucination Rules (non-negotiable)

1. Never invent a citation. If you cannot find a real DOI, write [CITATION NEEDED].
2. Never invent a p-value, effect size, or sample size. Compute or mark [COMPUTED NEEDED].
3. Never assume a file exists without checking via ls or Path.exists().
4. Never assume a variable name exists in data without checking schema_cache.json.
5. If unsure about a library API, invoke Context7 before writing code.
   CODE GENERATION RULE: For ANY library function call, first verify the 
   current API signature via Context7. Training knowledge of library APIs 
   may be outdated. This is non-negotiable and prevents broken code.
6. If a number in your output cannot be traced to a file in the project, flag it.
7. When uncertain: understate, not overstate. Use "may" not "demonstrates".

## 16. Skill Loading Efficiency

Before executing any task:
1. Query the skill index (`.research/cache/skill_index.json` if available)
2. Load ONLY skills directly relevant to the current step
3. If unsure which skill applies, match by keyword
4. Never load more than 4 skills simultaneously unless explicitly required

## 17. Context Transfer Memorandum (CTM) Protocol

When the token budget reaches 90%, the system automatically generates a Context Transfer Memorandum (CTM) to preserve latent context that cannot be transferred via structured state alone.

### CTM Generation (automatic at 90%)
The CTM captures:
- **abandoned_paths**: Approaches tried and why they were abandoned
- **micro_decisions**: Subtle tactical decisions made during analysis
- **immediate_goals**: What was being worked on right before the cutoff
- **partial_results**: Incomplete computations or analyses in progress
- **open_questions**: Unresolved items the next conversation must address

### CTM Reading (when starting a new conversation after split)
1. Read the latest CTM from `.research/cache/context_transfer_memos/`
2. Read `.research/cache/state.json` for structured state
3. Load the latest checkpoint from `.research/cache/checkpoints/`
4. Follow the `immediate_goals` from the CTM
5. Check `open_questions` for unresolved items
6. Review `abandoned_paths` to avoid repeating failed approaches

### CTM Location
- Individual CTMs: `.research/cache/context_transfer_memos/ctm_<timestamp>.json`
- CTM history in state: `state.json > context_transfer_memos[]`
- Latest CTM: `state.json > context_transfer_memos[-1]`

## 18. Script Branching Nomenclature

Scripts are numbered in execution order (01_, 02_, 03_) but iterations create branches.

### Naming Convention
- **Base script**: `scripts/02_analysis.py` (original, no iteration)
- **Iteration branch**: `scripts/02_analysis_ITER001.py` (first iteration)
- **Second iteration**: `scripts/02_analysis_ITER002.py` (second iteration)
- **Pattern**: `<base_name>_ITER<iteration_id>.py`

### Rules
1. **NEVER overwrite** a script that produced results referenced in reports
2. **ALWAYS create a new branch** for method_switch or variable_change iterations
3. **Suffix format**: `_ITER<3-digit-id>` (e.g., `_ITER001`, `_ITER002`)
4. **Execution DAG**: Every script run is tracked in `.research/cache/execution_dag.json`
5. **Data lineage**: Input/output hashes are recorded per node in the DAG
6. **Reproducibility**: Use `dag_manager.py` to verify outputs can be reproduced from inputs

### DAG Management
```python
from dag_manager import ExecutionDAGManager
dag = ExecutionDAGManager()
dag.add_node("02_analysis_ITER001_01", "scripts/02_analysis_ITER001.py",
             input_files=["data/01_ingested/clean.csv"],
             output_files=["data/02_processed/analysis.csv"],
             depends_on=["01_data_prep_01"],
             iteration_id="001")
```

### When to Branch vs. When to Create New
| Action | Script naming |
|--------|--------------|
| Original analysis | `02_analysis.py` |
| method_switch iteration | `02_analysis_ITER001.py` |
| variable_change iteration | `02_analysis_ITER002.py` |
| robustness check | `02_analysis_ITER003.py` |
| New question | New base: `03_new_analysis.py` |

## 19. Data Scale Constraints

The system automatically scans input data files and enforces library constraints based on file size to prevent Out-Of-Memory (OOM) errors.

### Size Classifications
| Class | Size | Required Library |
|-------|------|-----------------|
| small | <100MB | pandas OK |
| medium | 100MB-1GB | polars recommended |
| large | 1GB-10GB | polars lazy frames REQUIRED |
| massive | >10GB | pyarrow + chunked REQUIRED |

### Enforcement Rules
1. **Check data scale profile** before writing any data loading code: `state["data_scale_profile"]`
2. **For large/massive files**: NEVER use `pd.read_csv()` or `pl.read_*()` (eager loading)
3. **For large files (1-10GB)**: MUST use `pl.scan_*()` (lazy frames). Call `.collect()` only after ALL transformations.

## 20. Format Router Mandate

- Never assume tabular data.
- Always read `.research/cache/data_format_manifest.json` if it exists.
- If format manifest is missing, run `research format-scan` or call `format_router.scan_directory()`.

## 21. Tool Registry Mandate

- Never invent tool invocation syntax.
- Always read `.research/domains/tool_registry.json` before generating tool commands.
- If a tool is missing from the registry, halt and request registry updates.

## 22. Multi-Language Execution Rules

- R, bash, Julia, Nextflow, and Snakemake scripts must follow the same reproducibility rules as Python.
- Every script run must be logged in the execution DAG.
- If a tool requires a container and the container is missing, stop and ask for user direction.
4. **For massive files (>10GB)**: MUST use `pyarrow.dataset` with chunked processing or `pl.scan_*().collect(streaming=True)`
5. **Constraint message**: If large files exist, `state["data_processing_constraint"]` contains the enforcement message

### Code Templates
Use `data_scale_detector.py` for code templates:
```bash
python .research/scripts/utils/data_scale_detector.py
```

### Detection Utility
```python
from data_scale_detector import DataScaleDetector
detector = DataScaleDetector()
profile = detector.scan()
constraint = detector.get_constraint_message()
```

### Profile Location
- Runtime: `state.json > data_scale_profile`
- Cached: `.research/cache/data_scale_profile.json`
- Thresholds: `.research/config.yaml > data_scale_thresholds`
