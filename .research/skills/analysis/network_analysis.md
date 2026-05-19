---
skill_id: "network_analysis"
version: "5.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "networkx", "pandas"]
estimated_tokens: 3000
depends_on: ["profile_network"]
produces: ["analysis/03_analytical/network_results.json"]
---

# Skill: Advanced Network Graph Analysis

## Purpose
Partition graphs using Louvain modularity and compute centrality metrics.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `edges_path` | Path | Yes | Edge list path |

## Methodological Framework
- **Louvain Modularity (Q)**:
  $$Q = \frac{1}{2m} \sum_{i,j} \left[ A_{ij} - \frac{k_i k_j}{2m} \right] \delta(c_i, c_j)$$
  Measures the density of links inside communities compared to links between communities.

## Step-by-Step Analytical Protocol
1. Load edges. Calculate modularity communities.
2. Calculate Betweenness, Degree, and Closeness centralities.

## Diagnostics & Interpretation Guide (What to Look For)
- **Modularity Q < 0.3**:
  - *Interpret*: The network does not have strong community partitioning. Group divisions may be arbitrary.
  - *Action*: Avoid describing communities as structural modules; report flat centrality metrics instead.

## Writing & Reporting Standards
> "The network was partitioned using the Louvain modularity algorithm, yielding a modularity score of $Q = .48$, indicating strong community separation. Node centralities identified node X as the primary broker (Betweenness $= .24$)."

## Reference Python Implementation
```python
import networkx as nx
from community import community_louvain
import pandas as pd

def run_network(edges_path):
    df = pd.read_csv(edges_path)
    G = nx.from_pandas_edgelist(df, source=df.columns[0], target=df.columns[1])
    partition = community_louvain.best_partition(G)
    mod = community_louvain.modularity(partition, G)
    return mod, partition
```

## Validation Criteria
- [ ] Modularity partitions are mapped.