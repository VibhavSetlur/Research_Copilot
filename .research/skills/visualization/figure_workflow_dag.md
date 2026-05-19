---
skill_id: "figure_workflow_dag"
version: "3.0.0"
category: "visualization"
type: "static_figure"
domain_compatibility: ["all"]
required_tools: ["python"]
estimated_tokens: 2000
depends_on: []
produces: [".research/state/workflow_dag.mermaid"]
---

# Skill: Workflow DAG Figures (Mermaid)

## Purpose
Generate a structured Mermaid.js diagram representing the step-by-step research execution workflow.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_json` | Path | Yes | Path to workflow_dag.json containing node logs |

## Execution Protocol

### Step 1: Format Setup
- Declare flowchart layout: `graph TD` (Top-Down) or `graph LR` (Left-to-Right).

### Step 2: Styling and Node Design
- Generate nodes for each executed skill. Labels must display:
  - Skill name.
  - Duration in seconds.
  - Status (Success, Failed, Skipped).
- Define visual styles using CSS classes:
  - Success nodes: Light green background, solid thin border.
  - Failed nodes: Light red background, double border.
  - Unexecuted nodes: White background, dashed border.

### Step 3: Link Mapping
- Map dependencies matching file input-outputs. Annotate edges with data file names (e.g., `data_raw.csv`).

### Step 4: Export
- Save as `.mermaid` file. Ensure all labels with special characters are enclosed in double quotes.

## Output Specification
Produces:
- `.research/state/workflow_dag.mermaid`

## Validation Criteria
- [ ] Output is a valid Mermaid.js graph string.
- [ ] Nodes represent all executed phases.