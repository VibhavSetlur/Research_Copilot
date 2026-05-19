---
skill_id: "github_release"
version: "2.0.0"
category: "integration"
domain_compatibility: ["all"]
required_tools: ["python", "requests"]
estimated_tokens: 2500
depends_on: []
produces: ["github_release_url.txt"]
---

# Skill: GitHub Release Creation

## Purpose
Create a GitHub release attaching the final paper, dashboard script, and data manifest.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo` | Str | Yes | Repository name (owner/repo) |
| `tag` | Str | Yes | Release tag (e.g., v1.0.0) |

## Execution Protocol

### Step 1: API Call
- Use GitHub REST API to create a new release object

### Step 2: Asset Upload
- Upload `research_paper_imrad.md`, `reproducibility_audit.json`, and `data_hashes.json` as release assets

## Output Specification
- URL of the created release

## Validation Criteria
- [ ] Release creation must return a 201 Created status code
- [ ] All specified assets must be successfully uploaded
