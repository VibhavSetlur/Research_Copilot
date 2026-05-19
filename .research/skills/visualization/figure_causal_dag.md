---
skill_id: "figure_causal_dag"
version: "3.0.0"
category: "visualization"
type: "static_figure"
domain_compatibility: ["all"]
required_tools: ["python", "networkx", "matplotlib", "pygraphviz"]
estimated_tokens: 2500
depends_on: ["causal_inference"]
produces: ["reports/figures/causal_dag/"]
---

# Skill: Static Causal DAG Figures (Manuscript Quality)

## Purpose
Render static Directed Acyclic Graphs (DAGs) representing structural causal models for publication.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `dag_path` | Path | Yes | Path to causal_dag.json containing nodes and edges |

## Execution Protocol

### Step 1: Hierarchical Layout Layout
- Load nodes and edges into NetworkX.
- Enforce strict hierarchical layouts using Graphviz `dot` (left-to-right flow). Avoid spring or circular layouts.

### Step 2: Styling and Node Coloring
- Color nodes based on causal roles using desaturated, print-friendly colors:
  - **Exposure (Treatment)**: Light green (`#a1dab4`).
  - **Outcome**: Light blue (`#41b6c4`).
  - **Adjusted Confounders**: Light gray (`#d9d9d9`).
  - **Unadjusted Confounders**: Light salmon/orange (`#fe9929`).
- Node shapes: Render as rounded boxes or neat circles with a thin border (0.5pt).
- Edge styles: Thin gray lines (`#737373`, 0.5pt) with sharp, small arrowheads.

### Step 3: Typography
- Node labels must use sans-serif typography (Helvetica/Arial) at 8pt.
- Size nodes dynamically to fit label text lengths without clipping.

### Step 4: Exporting
- Save to `reports/figures/causal_dag/` as vector **PDF** and **SVG** files.
- Save a backup **PNG** at 600 DPI.
- Call `plt.savefig(..., bbox_inches='tight', dpi=600)`.

## Output Specification
Produces inside `reports/figures/causal_dag/`:
- `causal_dag.pdf`
- `causal_dag.svg`
- `causal_dag.png`

## Validation Criteria
- [ ] Diagram contains no cycles (is a valid DAG).
- [ ] Nodes are colored distinctively by causal roles.
- [ ] Arrows are clearly visible and do not clip.