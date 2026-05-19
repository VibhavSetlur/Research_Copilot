---
skill_id: "notebooklm_import"
version: "2.0.0"
category: "integration"
domain_compatibility: ["all"]
required_tools: ["python", "zipfile"]
estimated_tokens: 2500
depends_on: []
produces: ["notebooklm_source_package.zip"]
---

# Skill: NotebookLM Import

## Purpose
Package and push research artifacts to Google NotebookLM via unofficial APIs or structured zip for manual upload.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `artifacts_dir` | Path | Yes | Directory containing final reports and data dictionaries |

## Execution Protocol

### Step 1: Packaging
- Compile `research_findings.md`, `data_dictionary.md`, and `methods_log.md` into a single Source Document

### Step 2: API/Zip Push
- Zip files if using manual upload, or push via `notebooklm-py`

## Output Specification
- Archive ready for NotebookLM ingestion

## Validation Criteria
- [ ] Archive must not exceed 50MB (NotebookLM limit)
