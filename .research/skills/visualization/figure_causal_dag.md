---
skill_id: "figure_causal_dag"
version: "8.0.0"
category: "visualization"
domain_compatibility: ["all"]
required_tools: ["python", "networkx", "matplotlib", "graphviz"]
depends_on: ["viz_design_system", "viz_code_standards", "causal_inference"]
produces: ["reports/figures/causal_dag.png", "reports/figures/causal_dag.svg"]
complexity: "intermediate"
---

# Skill: Causal DAG Visualization

## Purpose
Render causal directed acyclic graphs showing hypothesized relationships between treatment, outcome, confounders, mediators, and colliders.

## When to Use
- After causal model specified
- For methods section figure
- Communicating identification strategy

---

## Node Types & Styling

| Node Type | Shape | Color | Description |
|-----------|-------|-------|-------------|
| Treatment | Rectangle | `#0072B2` (blue) | Exposure/intervention |
| Outcome | Rectangle | `#009E73` (green) | Dependent variable |
| Confounder | Ellipse | `#999999` (gray) | Common cause |
| Mediator | Diamond | `#E69F00` (orange) | On causal path |
| Collider | Hexagon | `#D55E00` (vermillion) | Common effect |
| Instrument | Triangle | `#56B4E9` (sky blue) | IV variable |
| Unmeasured | Dashed border | `#CC79A7` (red) | Not observed |

## Edge Types

| Edge Type | Style | Meaning |
|-----------|-------|---------|
| Causal | Solid arrow | Direct causal effect |
| Unmeasured path | Dashed arrow | Hypothesized but unmeasured |
| Backdoor path | Red highlight | Confounding path |
| Blocked path | ⊥ symbol | Adjusted/blocked |

---

## Layout Rules

1. **Hierarchical layout**: Treatment at top, outcome at bottom
2. **Confounders**: Between treatment and outcome
3. **Mediators**: On the causal path between treatment and outcome
4. **Colliders**: Where two arrows meet
5. **Minimize edge crossings**: Use force-directed or Sugiyama layout
6. **Node spacing**: Enough room for labels

---

## Annotation

- Label each node with variable name
- Add legend for node types
- Note identification strategy (backdoor set, frontdoor, IV)
- Include minimal adjustment set
- Highlight backdoor paths in red

---

## Validation Checks
- [ ] Graph is acyclic (no cycles)
- [ ] All variables from causal model included
- [ ] Backdoor paths identified
- [ ] Minimal adjustment set specified
- [ ] Node types correctly styled
- [ ] Design system colors used
