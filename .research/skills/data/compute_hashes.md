---
skill_id: "compute_hashes"
version: "3.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "hashlib"]
estimated_tokens: 2000
depends_on: []
produces: ["data/data_hashes.json"]
---

# Skill: Data Cryptographic Hashing

## Purpose
Compute SHA-256 hashes of input files to document dataset versions and ensure data integrity.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_paths` | List[Path]| Yes | List of target file paths to hash |

## Execution Protocol

### Step 1: File Processing
- Iterate over file paths. Verify files exist.
- Read files in binary mode in 4MB chunks to prevent memory leaks on large datasets.

### Step 2: Digest Compilation
- Generate SHA-256 hexadecimal digests.
- Retrieve file size and last modified date.

### Step 3: Export Manifest
- Write parameters to `data_hashes.json`.

## Output Specification
Produces:
- `data/data_hashes.json` mapping paths to digests.

## Validation Criteria
- [ ] Hex digests are exactly 64 characters long.
- [ ] File sizes match local system records.