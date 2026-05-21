---
skill_id: "zotero_sync"
version: "7.0.0"
category: "integration"
domain_compatibility: ["all"]
required_tools: ["python", "pyzotero", "bibtexparser"]
depends_on: ["generate_bibtex"]
produces: ["integration/zotero_sync_log.json"]
complexity: "intermediate"
---

# Skill: Zotero Reference Sync

## Purpose
Sync the research bibliography to a Zotero library for reference management, annotation, and citation insertion.

## When to Use
- Literature corpus built
- BibTeX file generated
- Researcher uses Zotero for reference management

## When NOT to Use
- Researcher uses different reference manager
- Only a few references (manual entry sufficient)

## Execution Protocol

### Step 1: Zotero Connection
- Connect to Zotero API using user ID and API key
- Verify: connection successful, library accessible
- Identify: target collection (create if not exists)

### Step 2: Reference Import
- Parse BibTeX file into individual entries
- For each entry:
  - Check if already in Zotero (by DOI)
  - If new: create Zotero item with all fields
  - If existing: update metadata if changed
- Tag: all imported items with project tag

### Step 3: Attachment Linking
- If PDFs available: attach to Zotero items
- If URLs available: add as linked URLs
- Verify: attachments accessible

### Step 4: Sync Log
- Record: items added, updated, skipped (duplicates)
- Record: any import errors
- Output: sync summary

## Output Specification
- `integration/zotero_sync_log.json`: items added, updated, skipped, errors

## Validation Checks
- [ ] All BibTeX entries processed
- [ ] No duplicate items created
- [ ] Project tag applied to all items
- [ ] Errors logged and reported
