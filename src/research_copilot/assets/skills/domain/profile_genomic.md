---
skill_id: "profile_genomic"
version: "1.0.0"
category: "data"
domain_compatibility: ["genomics"]
required_tools: ["fastqc", "multiqc"]
depends_on: []
produces: ["02_experiments/main/qc_report.html"]
complexity: "basic"
---

# Skill: Genomic Data Profiling

<objective>
Runs FastQC/MultiQC on raw FASTQ files to determine sequencing quality.
</objective>

<protocol>
### Step 1: Pre-checks
- Validate inputs are FASTQ format.

### Step 2: Core Procedure
- Run FastQC on all files.
- Aggregate with MultiQC.
</protocol>
