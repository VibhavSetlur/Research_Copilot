---
skill_id: "snowball_citations"
version: "2.0.0"
category: "literature"
domain_compatibility: ["all"]
required_tools: ["python", "requests", "networkx"]
estimated_tokens: 2500
depends_on: ["search_semantic_scholar"]
produces: ["citation_graph.json", "snowball_corpus.json"]
---

# Skill: Recursive Citation Snowballing

## Purpose
Perform forward and backward citation chaining to build a comprehensive literature network.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `seed_dois` | List[Str] | Yes | List of starting DOIs |
| `depth` | Int | No | Recursion depth (default: 2) |

## Execution Protocol

### Step 1: Backward Chaining (References)
- For each seed DOI, fetch its bibliography (references) via Semantic Scholar or CrossRef

### Step 2: Forward Chaining (Citations)
- For each seed DOI, fetch papers that cite it

### Step 3: Recursion & Filtering
- Repeat up to `depth` times
- Filter out papers with < 5 citations to avoid explosion
- Deduplicate by DOI

### Step 4: Graph Construction
- Build a Directed Graph where nodes are papers and edges are citations

## Output Specification
- `citation_graph.json`: Nodes and edges of citation network
- `snowball_corpus.json`: Flattened metadata of all discovered papers

## Validation Criteria
- [ ] Graph must be a DAG (Directed Acyclic Graph) - remove cycles if any
- [ ] Deduplication must yield unique DOIs across the corpus
