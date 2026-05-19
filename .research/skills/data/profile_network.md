---
skill_id: "profile_network"
version: "3.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "networkx", "pandas"]
estimated_tokens: 3000
depends_on: []
produces: ["data/01_ingested/profile_network.json"]
---

# Skill: Network Graph Profiling

## Purpose
Profile network and relational datasets to extract topological properties and connectivity metrics.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `edges_path` | Path | Yes | Edge list file path |
| `directed` | Bool | No | Flag indicating directed edges (default: False) |

## Execution Protocol

### Step 1: Graph Ingestion
- Load edges using NetworkX. Add weights if present in input files.

### Step 2: Global Topology Analysis
- Count total Nodes (N) and Edges (E).
- Calculate Network Density.
- Identify connected components (strongly and weakly for directed graphs).
- Compute transitivity (clustering coefficient) and reciprocity.

### Step 3: Centrality Metrics Distributions
- Compute degree distribution parameters.
- Calculate Betweenness and Eigenvector centrality summaries (Mean, Max, Variance).

### Step 4: Small-world & Scale-free Screening
- Calculate the average clustering coefficient and average path length.
- Test fit of degree distribution to a power-law distribution.

## Output Specification
Produces:
- `data/01_ingested/profile_network.json` containing network matrices and degree distributions.

## Validation Criteria
- [ ] Density is bounded between 0 and 1.
- [ ] Node count equals total unique values in edges list.