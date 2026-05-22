# Iterative Research Guide

How to use Research OS's state machine to iterate, branch, checkpoint, and synthesize findings.

---

## Overview

Research OS models research as a **directed acyclic graph (DAG)** of experiments. Each experiment is a numbered folder in `workspace/`. The state ledger tracks progress across all branches.

```
State Machine Flow:

  init → 01_exploration ──→ 02_causal_model ──→ 03_robustness → synthesis
                   \                                  ↑
                    └─→ 02b_alternative_method ────────┘ (merged)
```

---

## Branches (Experiments)

### Creating a Branch

Request a new experiment in your IDE:

> "Branch off and test whether the result holds with demographic controls."

The IDE calls:
```
sys.branch.create(name="demographic_controls", hypothesis="Result holds after controlling for age/sex/income")
```

This creates `workspace/02_demographic_controls/` with:
- `README.md` — goal, methods, expected/actual outcome, decision
- `conclusions.md` — key findings
- Subdirectories: `data/`, `scripts/`, `outputs/`

### Forking from a Previous Step

To copy an existing experiment as a starting point:

```
sys.branch.create(name="robustness_check", from_step="01_exploration")
```

This copies `01_exploration/` → `03_robustness_check/`.

### Abandoning a Branch

If a line of inquiry is a dead end:

```
sys.branch.abandon(branch_id="02b_alternative_method", reason="No significant effect found")
```

The branch is marked as `abandoned` in the state ledger. Files are preserved for reference.

### Merging a Branch

When a branch produces useful findings:

```
sys.branch.merge(source="02_causal_model", target="main", message="Causal effect confirmed: β=0.73, p<0.001")
```

The branch is marked as `merged` in the state ledger.

---

## Checkpoints

### Creating a Checkpoint

Before any destructive operation (data transformation, model training):

```
sys.checkpoint(checkpoint_id="before_model_training", description="Snapshot before fitting random forest")
```

This snapshots the entire `workspace/` into `.os_state/checkpoints/before_model_training/`. Large data files (CSV, Parquet, etc.) are hash-referenced rather than copied.

### Listing Checkpoints

```
sys.checkpoint.list()
```

Returns all checkpoints with timestamps and descriptions.

### Rolling Back

To restore workspace to a previous state:

```
sys.rollback(checkpoint_id="before_model_training")
```

The current state is automatically backed up as `pre_rollback_<checkpoint_id>_<timestamp>` first.

---

## State Ledger

The single source of truth lives at `.os_state/state_ledger.yaml`.

### Viewing State

```
sys.state()
```

Returns:
- Current branch
- All branches and their statuses
- Pipeline stage
- Checkpoint history
- Workspace folder tree

### State Diff Log

Every state change is logged to `workspace/logs/state_changes.log` with before/after diffs:

```
--- 2026-05-22T14:03:00Z
  branch +02_causal_model (active)
  branch switch: main → 02_causal_model
--- 2026-05-22T14:05:00Z
  stage: planned → running
  checkpoint: ckpt_20260522_140500 = 02_causal_model @ 2026-05-22T14:05:00Z
```

---

## Analysis Log

Every significant step should be recorded in `workspace/analysis.md`.

### Logging a Step

The IDE should call after each experiment:

```
sys.analysis.log(
  entry="Welch t-test: income ~ education, t=4.23, p<0.001, d=0.73",
  step="02_causal_model",
  status="complete"
)
```

This:
1. Appends a chronological log entry: `[2026-05-22 14:03] 02_causal_model: ...`
2. Updates the Mermaid workflow diagram at `workspace/workflow.mermaid`
3. Attempts to render `workspace/workflow.png` (if mmdc is installed)

### Workflow Diagram Colors

| Status | Color | Meaning |
|--------|-------|---------|
| `planned` | Grey | Not yet started |
| `running` | Yellow | In progress |
| `complete` | Green | Finished successfully |
| `failed` | Red | Error occurred |
| `dead_end` | Dashed red | Hypothesis disproven |

---

## Methods Log

Every tool that runs a statistical test, data transformation, or literature retrieval **must** append to `workspace/methods.md`.

```
mem.methods.append(
  method="Welch t-test",
  parameters="equal_var=False, alpha=0.05",
  tool="tool.statistical.test",
  citation="student1908"
)
```

---

## Literature & Citations

### Indexing Literature PDFs

Place PDFs in `inputs/literature/`, then:

```
mem.literature.index()
```

This scans the directory and builds/refreshes `inputs/literature_index.yaml`.

### Generating Citations

```
mem.citations.generate()
```

Regenerates `workspace/citations.md` from the literature index. Each entry has a `verified` flag.

### Adding a Manual Citation

```
mem.citation.add(
  bibtex="@article{smith2024, title={...}, ...}",
  citation_key="smith2024",
  source="manual"
)
```

---

## Synthesis

When you're done iterating:

```
sys.synthesize(project_name="My Paper", formats=["pdf"])
```

This:
1. Populates `synthesis/abstract.md`, `paper.tex`, `references.bib`
2. Regenerates `workspace/citations.md`
3. Regenerates `inputs/intake.md`
4. Does NOT compile LaTeX (call `tool.latex.compile` separately)

---

## Full Research Session Example

```
Step  IDE call                                           What happens
────  ─────────────────────────────────────────────────  ─────────────────────
1     (user: "Analyze survey.csv")                       IDE inspects data
2     view.data.head(filepath="inputs/raw_data/survey.csv")  Returns shape, columns, sample rows
3     tool.figure.create(filepath="...", chart_type="hist", ...)  Saves figure to workspace/figures/
4     tool.statistical.test(filepath="...", test_type="ttest", ...)  Returns statistic, p-value, assumptions
5     mem.methods.append(method="Welch t-test", ...)     Appends to workspace/methods.md
6     sys.analysis.log(step="01_exploration", status="complete")  Updates analysis.md + Mermaid diagram
7     (user: "Test education vs income")                 IDE decides to branch
8     sys.branch.create(name="education_income", from_step="01_exploration")  Creates 02_education_income/
9     tool.statistical.test(...)                         Runs in the new branch
10    sys.analysis.log(step="02_education_income", status="complete")  Updates workflow
11    (user: "I'm done. Compile.")
12    sys.synthesize(project_name="Survey Analysis")     Creates synthesis/ templates
13    tool.latex.compile()                               Produces paper.pdf
```
