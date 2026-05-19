---
skill_id: "compute_hashes"
version: "7.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "hashlib"]
depends_on: []
produces: ["data/01_ingested/hash_manifest.json"]
complexity: "basic"
---

# Skill: Data Integrity Hashing

## Purpose
Compute and record cryptographic hashes for all data files to enable integrity verification, provenance tracking, and reproducibility auditing.

## When to Use
- Immediately after data ingestion
- After any data transformation
- Before and after analysis runs
- When sharing data between systems

## When NOT to Use
- Files are ephemeral/temporary
- Data is streaming (use checkpoint hashing instead)

## Execution Protocol

### Step 1: File Discovery
- Scan `data_raw/` and `data/` directories recursively
- Identify all data files: CSV, Parquet, Excel, JSON, SAS, SPSS, Stata, Feather
- Exclude: code files, documentation, hidden files

### Step 2: Hash Computation
- Compute SHA-256 for each file
- For files > 1GB: read in 8192-byte chunks to avoid memory overflow
- Record: file path, hash, file size, modification timestamp

### Step 3: Manifest Generation
- Create JSON manifest with all file entries
- Include metadata: computation timestamp, tool version, OS
- Sort entries by file path for deterministic output

### Step 4: Verification (if previous manifest exists)
- Compare current hashes to previous manifest
- Identify: new files, modified files, deleted files, unchanged files
- Report delta summary

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| Hash matches previous | File unchanged | Investigate modification source |
| File size consistent | Size matches expectation | Check for truncation or corruption |
| All files accounted | No unexpected changes | Verify intentional vs accidental |

## Output Specification
- `data/01_ingested/hash_manifest.json`: file paths, SHA-256 hashes, sizes, timestamps, delta from previous manifest

## Validation Checks
- [ ] All data files hashed
- [ ] Hashes are reproducible (recompute matches)
- [ ] Manifest is valid JSON
- [ ] Delta correctly identifies changes
