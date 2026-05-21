---
skill_id: "network_analysis"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "networkx", "scipy"]
depends_on: ["profile_network", "descriptive_stats"]
produces: ["analysis/03_analytical/network_results.json"]
complexity: "advanced"
---

# Skill: Network Statistical Analysis

## Purpose
Perform statistical analysis on network data including community detection, centrality-based inference, and network comparison.

## When to Use
- Research question involves relationships, influence, or connectivity
- Need to identify key nodes, communities, or structural patterns
- Comparing networks across conditions or time

## When NOT to Use
- Network is trivially small (< 10 nodes)
- Only descriptive network stats needed (use profile_network)
- Edges are not meaningful (random associations)

## Execution Protocol

### Step 1: Network Construction Validation
- Verify edge list: no self-loops (unless intentional), no duplicate edges
- Confirm: directed vs undirected, weighted vs unweighted
- Check: largest connected component includes ≥ 80% of nodes

### Step 2: Centrality-Based Analysis
- Compute centrality measures: degree, betweenness, closeness, eigenvector
- Identify top-k nodes by each measure
- Test: do central nodes differ on outcome variables?
- Correlate centrality with node attributes (point-biserial or Spearman)

### Step 3: Community Detection & Validation
- Detect communities: Louvain (modularity optimization) or Leiden (improved)
- Report: number of communities, modularity Q, community sizes
- Validate: conductance (ratio of external to internal edges per community)
- Characterize communities: what attributes define each community?

### Step 4: Network Comparison
- If comparing two or more networks:
  - Global: density, average clustering, diameter, assortativity
  - Degree distribution: Kolmogorov-Smirnov test
  - Community structure: compare modularity, number of communities
  - Node-level: compare centrality distributions

### Step 5: Statistical Network Modeling
- ERGM (Exponential Random Graph Model): model probability of edge formation
- Terms: edges (density), nodematch (homophily), gwesp (transitivity)
- Check: MCMC convergence, goodness-of-fit
- SAOM (Stochastic Actor-Oriented Model): for longitudinal networks

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| Giant component | > 80% of nodes | Fragmented network | Analyze components separately |
| Modularity Q | > 0.3 | No clear communities | Use alternative clustering |
| ERGM GOF | Model reproduces observed stats | Model misspecified | Add/change terms |
| Centrality correlation | Significant | Central nodes differ | Report attribute-centrality relationship |

### Red Flags
- **Degree distribution has extreme outliers**: few nodes dominate; results driven by hubs
- **Modularity Q < 0.1**: no meaningful community structure
- **ERGM degenerate**: model produces unrealistic networks; simplify terms
- **Network density > 0.80**: nearly complete graph; little structure to analyze

## Reporting Template
> "The network comprised N = [value] nodes and E = [value] edges (density = [value]). Community detection identified [count] communities (modularity Q = [value]). [Node attribute] was significantly associated with degree centrality (r = [value], p = [value])."

## Output Specification
- `analysis/03_analytical/network_results.json`: centrality rankings, community structure, network comparison results, ERGM coefficients

## Validation Checks
- [ ] Network is constructible and connected
- [ ] Centrality measures sum to expected totals
- [ ] Modularity in [-0.5, 1]
- [ ] ERGM converges and passes GOF
