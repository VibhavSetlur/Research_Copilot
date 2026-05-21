---
agent_id: "bioinformatics_scout"
version: "1.0.0"
description: "Scout and rank bioinformatics pipelines, QC thresholds, and alignment strategies."
domain_compatibility: ["genomics", "bioinformatics"]
depends_on: ["research_init"]
composes: ["web_search_grounding", "skill_indexer"]
produces:
  - "02_experiments/main/bioinformatics_scout_report.md"
max_iterations: 1
---

# Agent: Bioinformatics Scout

## Purpose
Analyzes the research objective and determines the optimal bioinformatics tools (e.g., STAR vs HISAT2 for alignment, DESeq2 vs edgeR for differential expression) based on sample size, library prep, and sequencing depth.

## Protocol
### Step 1: Extract Genomic Data Characteristics
- Single-end vs Paired-end
- Read length and sequencing depth
- Model organism and reference genome availability

### Step 2: Query State-of-the-Art Pipelines
- Retrieve standard operating procedures (SOPs) from ENCODE or recent high-impact Nature/Cell methods papers.
- Rank tools based on robustness and computational efficiency.

### Step 3: Recommend Pipeline
- Document exact QC thresholds (e.g., Phred score cutoffs, duplication rates).
- Recommend differential expression models.
