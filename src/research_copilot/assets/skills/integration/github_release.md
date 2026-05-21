---
skill_id: "github_release"
version: "7.0.0"
category: "integration"
domain_compatibility: ["all"]
required_tools: ["python", "subprocess", "gh-cli"]
depends_on: ["audit_reproducibility"]
produces: ["integration/github_release_log.json"]
complexity: "intermediate"
---

# Skill: GitHub Release Packaging

## Purpose
Package and publish the complete research project (code, data, results, documentation) as a versioned GitHub release for public sharing and archiving.

## When to Use
- Research complete and audited
- Ready for public sharing
- Journal requires code/data availability

## When NOT to Use
- Research not yet complete
- Data contains sensitive information
- Embargo period not expired

## Execution Protocol

### Step 1: Repository Preparation
- Create or update GitHub repository
- Structure:
  ```
  ├── data_raw/          # Raw data (if shareable)
  ├── data_processed/    # Cleaned data
  ├── analysis/          # Analysis scripts
  ├── reports/           # Manuscript, figures, tables
  ├── literature/        # Literature corpus
  ├── requirements.txt   # Dependencies
  ├── README.md          # Project documentation
  └── LICENSE            # Usage license
  ```

### Step 2: Sensitivity Review
- Check: no personal identifiers in data
- Check: no API keys or credentials in code
- Check: no sensitive information in comments
- If sensitive: anonymize or exclude

### Step 3: Documentation
- README must include:
  - Project title and authors
  - Research question
  - How to reproduce (step-by-step)
  - Data availability statement
  - Citation information
  - License

### Step 4: Release Creation
- Tag: semantic version (v1.0.0)
- Commit: all files with descriptive message
- Push: to main branch
- Create GitHub release with:
  - Release notes (summary of findings)
  - Attached manuscript PDF
  - Attached key figures
  - DOI badge (if Zenodo archived)

## Output Specification
- `integration/github_release_log.json`: repository URL, release tag, commit hash, attached files

## Validation Checks
- [ ] No sensitive data in repository
- [ ] README complete
- [ ] Requirements.txt up to date
- [ ] Release accessible via URL
- [ ] License file present
