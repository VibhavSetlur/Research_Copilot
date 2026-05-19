---
skill_id: "profile_genomic"
version: "7.0.0"
category: "data"
domain_compatibility: ["genomics", "bioinformatics"]
required_tools: ["python", "pandas", "numpy", "scipy"]
depends_on: ["profile_tabular"]
produces: ["data/01_ingested/genomic_profile.json"]
complexity: "advanced"
---

# Skill: Genomic Data Profiling

## Purpose
Profile genomic data (gene expression, variant calls, sequencing data) to understand data quality, batch effects, normalization status, and biological signal.

## When to Use
- Data contains gene-level measurements (expression, methylation, variants)
- Before differential expression, enrichment, or genomic modeling
- When merging genomic datasets from multiple sources

## When NOT to Use
- Data is clinical/phenotypic only (no molecular measurements)
- Data is already processed through standard QC pipeline

## Execution Protocol

### Step 1: Data Structure Identification
- Identify data type: RNA-seq counts, microarray intensity, variant calls, methylation beta values
- Determine: genes (rows) × samples (columns) or vice versa
- Verify gene identifiers: Ensembl IDs, gene symbols, RefSeq
- Check for duplicate gene entries

### Step 2: Quality Metrics (RNA-seq)
- Library size per sample: total reads, distribution
- Gene detection rate: genes with count > 0 per sample
- Mitochondrial gene proportion: high % indicates poor quality
- Ribosomal RNA proportion: high % indicates poor depletion
- GC content bias: correlation between GC% and expression

### Step 3: Normalization Assessment
- Detect if data is normalized: check for non-integer values, log-transformed range
- If raw counts: recommend TMM (edgeR) or DESeq2 median-of-ratios
- If log-transformed: verify base (log2 vs natural log)
- Check for zero-inflation: proportion of zero counts per gene and per sample

### Step 4: Batch Effect Detection
- If batch information available: compare distributions across batches
- PCA: color by batch vs biological condition
- If batch clusters separately from biology: batch effect present
- Quantify: proportion of variance explained by batch

### Step 5: Biological Signal Assessment
- Sample clustering: do biological replicates cluster together?
- Differential expression pilot: top variable genes separate conditions?
- Outlier samples: samples that don't cluster with any group

### Step 6: Multiple Testing Context
- Count of genes/features: determines multiple testing burden
- Expected proportion of true positives (π₀ estimation)
- Recommend FDR method: Benjamini-Hochberg (default), Storey's q-value

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| Library size CV < 0.3 | Consistent sequencing depth | Variable depth | Normalize for library size |
| Batch PCA | Biological clustering | Batch-driven clustering | Apply ComBat or removeBatchEffect |
| Replicate correlation | r > 0.9 | Poor reproducibility | Investigate sample quality |
| Zero proportion | < 80% for RNA-seq | Excessive zeros | Consider zero-inflated models |

### Red Flags
- **Gene symbols confused with dates** (SEPT2, MARCH1): common Excel conversion error; use Ensembl IDs
- **Negative expression values**: already log-transformed with offset; verify transformation
- **All samples identical**: technical replicate or data copy error
- **Chromosome identifiers missing**: cannot perform genomic context analysis

## Output Specification
- `data/01_ingested/genomic_profile.json`: data type, quality metrics, normalization status, batch effect assessment, biological signal indicators

## Validation Checks
- [ ] Gene identifiers are valid and non-duplicate
- [ ] Sample count matches metadata
- [ ] Normalization status determined
- [ ] Batch effect assessed (if batch info available)
