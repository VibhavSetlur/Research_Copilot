# Changelog

All notable changes to Research Copilot.

## [9.0.0] — 2026-05-20

### Added
- Semantic clustering of papers in literature_deep (TF-IDF + agglomerative clustering)
- Related Work Writer skill for auto-generating literature review sections
- Smart Imputer skill (MCAR/MAR/MNAR strategies with MICE and Rubin's rules)
- Data Validator skill (Pandera schema auto-generation from profile)
- Meta-Analysis skill (inverse-variance weighting, forest plots, funnel plots)
- Longitudinal Analysis skill (RM ANOVA, LME, LGC models)
- Survey Research domain profile (AAPOR reporting standard)
- Methods Checklist skill (STROBE/CONSORT/PRISMA/APA pre-submission checklists)
- Peer Review Prep agent (anticipated reviewer comments with pre-drafted responses)
- Progress Reporter skill (machine-parseable progress lines)
- Onboarding Guide skill (5-step first analysis)
- Predatory journal detection in audit_validate
- Quick start path for intake interviewer (5 questions, under 3 minutes)
- Profile tabular quick mode for files >100MB (10k row sampling)

### Fixed
- YAML parse error in econometrics.yaml (missing space in list item)
- Dashboard smoke test documentation (app._layout_value() instead of app.layout)
- Added Pillow to requirements.txt (required by figure_validator.py)
- Executor DAG update try/except indentation

### Changed
- README.md restructured as clean landing page with documentation links
- Created full documentation suite: Getting Started, Architecture, CLI Reference, MCP Integration, Workflows, Domains, Iteration, Contributing, Changelog
- QUICKSTART.md streamlined to 30-second reference card
- All skill files trimmed to <120 lines (code replaced with AI-readable protocols)

### Removed
- Duplicate find_project_root implementations (consolidated into common.py)

## [8.0.0] — 2026-03-15

### Added
- MCP server with 28+ native tools
- Multi-agent LLM delegation
- Token budget management with CTM handoff
- Knowledge graph for context management
- Semantic file system taxonomy
- Interpretative coupling for figures
- Execution DAG tracking
- Branching engine for divergent hypotheses

## [7.0.0] — 2026-01-20

### Added
- Lifecycle hook system (pre_routing, pre_execution, post_execution, pre_ledger_commit, on_failure)
- State ledger with checkpoint/restore
- Three-pass citation verification
- Claim-to-evidence graph tracing
- Adversarial Reviewer 2 with auto-remediation
- Conversational intake interviewer
- OSF pre-registration generation

## [6.0.0] — 2025-11-10

### Added
- 19 domain profiles with reporting standards
- 5 workflow types
- 8 iteration types
- Auto-debugging for failing scripts
- Dynamic dependency management
- Context7 API integration for code generation

## [5.0.0] — 2025-09-01

### Added
- Initial release of Research Copilot
- Core pipeline: intake → init → literature → method → analysis → compile → audit
- Pydantic schema validation
- Approval gates
- Cache system
