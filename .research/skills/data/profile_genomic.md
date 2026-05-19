---
skill_id: "profile_genomic"
version: "3.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "pysam", "biopython"]
estimated_tokens: 2500
depends_on: []
produces: ["data/01_ingested/profile_genomic.json"]
---

# Skill: Genomic Data Profiling

## Purpose
Evaluate quality scores and baseline statistics of FASTQ, BAM, or VCF genomic file formats.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `genomic_path` | Path | Yes | Path to genomic file |

## Execution Protocol

### Step 1: FASTQ Quality Control
- Calculate GC content percentage per read.
- Compute average Phred quality score profile along the read length.
- Identify overrepresented sequences and PCR duplicates.

### Step 2: BAM/SAM Alignment Stats
- Calculate total mapped reads, unmapped reads, and secondary alignments.
- Estimate mean coverage depth and coverage uniformity.

### Step 3: VCF Variant Diagnostics
- Count total SNPs and Indels.
- Compute Transition/Transversion (Ti/Tv) ratio.
- Calculate missing genotype rates per sample.

## Output Specification
Produces:
- `data/01_ingested/profile_genomic.json` containing quality metrics.

## Validation Criteria
- [ ] GC percentage is bounded between 0 and 100.
- [ ] Phred scores are positive.