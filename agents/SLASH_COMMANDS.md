# Research Co-Pilot: Slash Commands

Slash command definitions for **OpenCode**, **Antigravity**, **Cursor**, and **GitHub Copilot Chat**. Every command is a complete, self-sufficient execution prompt — copy and invoke directly.

---

## Quick Reference

| Command | Phase | What It Does |
|---------|-------|-------------|
| `/research-init` | 1 | Profile data, classify domain & type, write epistemic baseline with causal map |
| `/research-route` | 2 | Select methods, fetch live literature, build dependency manifest |
| `/research-scaffold` | 3 | Build directories, ingest & validate data, write data dictionary |
| `/research-analyze [rq=all]` | 4 | Run assumption checks, pivot engine, execute tests, generate figures |
| `/research-compile` | 5 | Synthesize IMRAD report, tables, 5-tab publication dashboard |
| `/research-audit` | 6 | Cold-start reproducibility + causal coherence + compliance sweep |
| `/research-status` | — | Show current state and recommended next command |
| `/research-pivot` | — | Manually log assumption failure and re-execute RQ |
| `/research-brief` | — | Print the research brief template for manual completion |

Do not skip phases. Each phase depends on the outputs of all prior phases.

---

## Command Definitions

### `/research-init`

```
Load agents/00_core_guardrails.md. Execute agents/01_initialize.md against all files in data_raw/ and docs_input/research_brief.md. Perform deep structural profiling of every file (MIME detection, missingness mechanism hypothesis using Little's MCAR test or pattern correlation matrices, outlier detection, relational integrity, temporal/spatial irregularity checks). Classify the data into a primary type code and any secondary codes from the full taxonomy (TABULAR-CROSS, TABULAR-PANEL, TABULAR-SURVEY, TEXT-CORPUS, TIME-SERIES, SPATIAL, NETWORK, BIOMEDICAL, MIXED). Parse all research questions into a causal variable taxonomy (Y, T, W, M, E, Z). Produce a power analysis per RQ citing domain-specific effect size literature. Write docs_input/initial_epistemic_baseline.md with: data inventory, structural profiles, causal map, variable-to-hypothesis matrix, power analysis, and detailed risk register. Halt and log ERROR if any required input is missing or malformed.
```

---

### `/research-route`

```
Load agents/00_core_guardrails.md. Execute agents/02_route_and_discover.md using docs_input/initial_epistemic_baseline.md as context. Consult the full extended internal routing table first (covering causal inference, Bayesian, ML, NLP, survival, spatial, network, and biomedical analysis goals). Flag any RQ not matched by the registry. For flagged gaps, perform live web searches on Google Scholar, PubMed, arXiv, and PyPI to identify state-of-the-art methods (post-2018, peer-reviewed, DOI required, package with ≥1,000 GitHub stars). For ALL RQs, search for 3–5 highly-cited comparable studies using similar methods on similar data. Write docs/papers_and_tools_cited.md with: method selection rationale, mathematical basis, key reference with DOI, failure alternative, supporting literature, and full dependency manifest.
```

---

### `/research-scaffold`

```
Load agents/00_core_guardrails.md. Execute agents/03_ingest_and_scaffold.md using docs_input/initial_epistemic_baseline.md and docs/papers_and_tools_cited.md as context. Build only the directories required for the classified data type (including type-specific subdirectories for text embeddings, spatial vectors, rasters, graph files, or normalized genomics data). Write scripts/01_validation.py implementing strict pandera schema validation with bounds derived from the epistemic baseline; use polars or dask if file size > 1 GB. Execute scripts/01_validation.py. Verify SHA-256 hashes of all ingested files before proceeding. Write docs/data_dictionary.md with full causal role metadata, missingness mechanism flags, and Table 1 (sample characteristics). Generate reports/figures/missingness_heatmap.png. Write environment/requirements.txt, environment/setup_env.sh, and per-directory READMEs.
```

---

### `/research-analyze [rq=all]`

```
Load agents/00_core_guardrails.md. Execute agents/04_execute_analysis.md for Phase {rq}. For each research question in scope: (1) load and hash-verify data from data/02_processed/; (2) apply domain-specific transformations (text embeddings, spatial projections, network centrality features, time-series differencing, biomedical normalization, train/test split for predictive models); (3) run all required assumption and causal diagnostic checks (normality, homoscedasticity, independence, multicollinearity VIF, covariate balance SMD, stationarity, SEM fit indices, PH assumption for survival — all per the estimator-specific check table); (4) log every result to docs/methods_log.md; (5) pivot to the pre-specified robust alternative if any assumption fails, citing literature in the PIVOT block; (6) apply Benjamini-Hochberg FDR correction if >3 hypotheses; (7) compute effect sizes for all tests; (8) execute domain-specific additional outputs (KM curves, LISA maps, topic coherence, factor loadings, centrality distributions); (9) generate publication-quality multi-panel figures (.pdf, .png, .html) with domain-appropriate figure type, on-image annotations, plain-English interpretation, and three-part companion captions; (10) save all results to data/03_analytical/. Replace {rq} with a specific RQ number or "all".
```

---

### `/research-compile`

```
Load agents/00_core_guardrails.md. Execute agents/05_compile_outputs.md using data/03_analytical/, reports/figures/, docs/methods_log.md, and docs/papers_and_tools_cited.md as context. Write reports/research_findings.md as a complete IMRAD-structured academic paper with: structured 250-word abstract; Introduction citing supporting literature; Data and Measures with Table 1; Analytical Strategy with pivot narrative; Results with full APA-format statistics (test statistic, df, p, FDR-p, effect size, 95% CI) and figure/table references; Discussion with hypothesis verdicts and literature comparison; complete APA 7th reference list. Generate domain-appropriate publication-grade tables in reports/tables/ as .md and booktabs .tex. Build the self-contained 5-tab interactive publication dashboard in reports/dashboards/analysis_app.py (Tab 1: Study Overview with hypothesis status badges; Tab 2: Interactive Data Explorer with correlation heatmap and distribution panels; Tab 3: Methodology with pipeline flowchart and assumption audit table; Tab 4: Results with per-RQ visual + diagnostic panels + statistical tables + effect size context cards; Tab 5: Literature and full APA bibliography) — runnable with a single command, fully styled, custom Plotly hover templates, download buttons, and responsive layout.
```

---

### `/research-audit`

```
Load agents/00_core_guardrails.md. Execute agents/06_audit_and_validate.md. (1) Reset environment: delete all __pycache__, intermediate outputs in data/02_processed/, data/03_analytical/, reports/figures/, reports/tables/, reports/dashboards/analysis_app.py; re-run environment/setup_env.sh; verify all package hashes against requirements.txt. (2) Execute the full pipeline cold: scripts/01_validation.py → scripts/02_transformation.py → scripts/03_modeling.py; capture exit codes and wall-clock durations. (3) Recompute and verify all SHA-256 hashes in data/01_ingested/, data/02_processed/, data/03_analytical/ against docs/data_dictionary.md. (4) Check every PIVOT entry in methods_log.md has a code implementation, an output file, and a citation. (5) Scan scripts/02_transformation.py and scripts/03_modeling.py for target leakage (Outcome Y or Mediator M appearing in feature matrices). (6) Scan reports/research_findings.md for causal language without causal estimators. (7) Scan all markdown for unformatted p-values, missing effect sizes, missing CIs, and colloquial phrases. (8) Verify all figures (.png, .html) and captions (_caption.txt) exist per RQ. (9) Verify docstring and type-hint coverage on all .py files. (10) Execute dashboard in headless mode. Write docs/validation_audit_report.md with all 9 audit dimension tables and a Final Verdict of PASS or FAIL.
```

---

### `/research-status`

```
Survey the current research project directory. Report:
1. Which phases are complete — determined by presence of: docs_input/initial_epistemic_baseline.md (Phase 1), docs/papers_and_tools_cited.md (Phase 2), data/01_ingested/ with ≥1 .parquet file (Phase 3), data/03_analytical/ with ≥1 result JSON (Phase 4), reports/research_findings.md (Phase 5), docs/validation_audit_report.md with "Final Verdict: PASS" (Phase 6).
2. The classified data type(s) and research domain from the epistemic baseline.
3. The total number of research questions and their current verdict status (SUPPORTED / PARTIALLY SUPPORTED / NOT SUPPORTED / PENDING).
4. Any open FAIL, HIGH, or PIVOT entries in docs/methods_log.md.
5. Any outstanding remediation steps in docs/validation_audit_report.md.
6. The single recommended next command to run.
Format as a status table followed by a concise recommendation.
```

---

### `/research-pivot [rq=1] [assumption=normality] [alternative=mannwhitneyu]`

```
Load agents/00_core_guardrails.md. Manually record a methodological pivot for Research Question {rq}. The assumption that failed: {assumption}. The alternative method selected: {alternative}. Append a structured PIVOT entry to docs/methods_log.md with the current ISO 8601 timestamp, the full test statistic for the failed assumption, the selected robust alternative with exact package==version, an explicit causal or statistical justification citing academic literature (Author, Year, DOI), and whether causal validity is maintained. Update scripts/03_modeling.py to implement {alternative} for RQ {rq}. Re-execute that research question only. Regenerate all figures (.pdf, .png, .html) and the three-part caption file for this RQ. Save updated outputs to data/03_analytical/.
```

---

### `/research-brief`

```
Print the complete research_brief.md template from docs_input/research_brief.md. Do not fill it in. Present it to the researcher for manual completion. Remind the researcher that this is the only document they write — all other documentation, scripts, figures, tables, and the dashboard are generated by the agent pipeline.
```

---

## Tool-Specific Usage Notes

### OpenCode / Antigravity
Place this file at `.opencode/commands/research.md`. Commands are registered as slash commands from `.opencode/commands/*.md` files. Invoke with `/research-init` etc.

### Cursor
Add the Phase Prompts from `.cursor/CURSOR_INSTRUCTIONS.md` to Cursor Settings → AI → Custom Instructions. Paste individual command blocks into Cursor Chat when needed.

### GitHub Copilot Chat
Prefix any command with `@workspace`. The `.github/copilot-instructions.md` file is auto-loaded. Example: `@workspace /research-init`.

### Generic LLM Interface
Copy any command block directly into the chat window. The prompt is fully self-contained.
