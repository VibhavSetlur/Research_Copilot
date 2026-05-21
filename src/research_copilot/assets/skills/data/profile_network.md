---
skill_id: "profile_network"
version: "7.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "networkx", "pandas"]
depends_on: ["profile_tabular"]
produces: ["data/01_ingested/network_profile.json"]
complexity: "advanced"
---

# Skill: Network Data Profiling

## Purpose
Profile graph/network data to understand connectivity, centrality, community structure, and topological properties.

## When to Use
- Data represents relationships between entities (edges between nodes)
- Before network analysis, community detection, or graph ML
- When data has source-target or adjacency structure

## When NOT to Use
- Data is tabular without relational structure
- Network is trivially small (< 5 nodes)

## Execution Protocol

### Step 1: Graph Construction
- Identify node list and edge list
- Determine: directed vs undirected, weighted vs unweighted, bipartite vs monopartite
- Build graph using NetworkX
- Verify: no self-loops (unless expected), no duplicate edges (unless multigraph)

### Step 2: Basic Graph Properties
- Node count (N), edge count (E)
- Density: E / [N(N-1)/2] for undirected
- Average degree, degree distribution
- Connected components: count, size distribution
- Largest connected component: node count, proportion of total

### Step 3: Centrality Analysis
- Degree centrality: most connected nodes
- Betweenness centrality: nodes bridging communities
- Closeness centrality: nodes closest to all others
- Eigenvector centrality: nodes connected to other important nodes
- Report top-10 nodes by each measure

### Step 4: Community Structure
- Detect communities: Louvain or Leiden algorithm
- Number of communities, modularity score (Q)
- Community size distribution
- Inter-community vs intra-community edge ratio

### Step 5: Path Analysis
- Average shortest path length
- Graph diameter (longest shortest path)
- Clustering coefficient (local and global)
- Small-world check: high clustering + short path length

### Step 6: Degree Distribution Fitting
- Fit power law, exponential, log-normal to degree distribution
- Determine best-fitting distribution
- If power law: estimate exponent γ (scale-free if 2 < γ < 3)

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| Graph connected | Single component or giant component | Fragmented network | Analyze components separately |
| Modularity Q > 0.3 | Community structure present | No clear communities | Use alternative clustering |
| Degree distribution | Fits known model | Unknown structure | Use non-parametric methods |
| Density | 0.01 - 0.5 | Too sparse or too dense | Check for missing edges or over-reporting |

### Red Flags
- **Isolated nodes (> 20% of network)**: data collection incomplete; consider removing or treating separately
- **Single hub dominates**: star topology; results driven by one node
- **Disconnected graph**: analyze largest component only, report fragmentation
- **Bipartite treated as monopartite**: project correctly before analysis

## Output Specification
- `data/01_ingested/network_profile.json`: graph properties, centrality rankings, community structure, path metrics, degree distribution fit

## Validation Checks
- [ ] Graph is constructible from edge list
- [ ] Node and edge counts consistent
- [ ] Centrality measures sum to expected totals
- [ ] Modularity score in [-0.5, 1]
