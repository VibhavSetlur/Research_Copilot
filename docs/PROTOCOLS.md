# Protocol Reference

Research OS ships 34 YAML protocols organised into 9 categories. Each
protocol is a sequence of steps the AI should follow, with explicit
`expected_outputs`, a `next_protocol` pointer, and quality minimums.

For the format of a protocol file, see
[CONTRIBUTING.md § Adding or modifying a protocol](../CONTRIBUTING.md).

---

## The main pipeline (10 stages, in order)

| # | Protocol | What it does | Done when |
|---|---|---|---|
| 1 | `guidance/session_boot` | Read config + state, apply blank-field defaults, choose next protocol | first entry in execution log |
| 2 | `guidance/project_startup` | Run intake autofill, profile data, lock research question | intake.md filled + research_question.md confirmed |
| 3 | `domain/domain_analysis` | Classify domain, pick reporting standard, list biases | docs/domain_summary.md exists |
| 4 | `domain/research_design` | Choose study design + sample size justification | docs/research_design.md exists |
| 5 | `methodology/methodology_selection` | Pick statistical / computational methods (literature-grounded) | workspace/methods.md substantive |
| 6 | `literature/literature_search` | Multi-database search + dedup + PRISMA accounting | literature_index.yaml + citations.md exist |
| 7 | `guidance/analysis_plan` | Per-step loop: scope → ground → execute → document → snapshot | ≥1 experiment with non-empty conclusions.md |
| 8 | `reproducibility/reproducibility` | Lock environments, verify seeds, generate Dockerfile | per-experiment requirements.txt exist |
| 9 | `audit/audit_and_validation` | Citation / power / assumption / figure / code audits | workspace/logs/audit_report.md exists |
| 10 | `synthesis/synthesis_paper` | Compile paper (venue-tailored, verified citations) | synthesis/paper.md exists |

`sys_protocol_next` returns the first stage whose outputs (or execution log)
say "not done yet". The pipeline is robust to migrating projects — it works
off both the execution log AND on-disk artifacts.

---

## On-demand protocols

### Guidance

* `guidance/iterative_planning` — for "what should I do next?" workflows.
  Surveys state, pulls fresh literature + tools, proposes 2-3 options.
* `guidance/dead_end_routing` — abandon a failed experiment cleanly:
  document, rename to `__DEAD_END`, choose where to resume.
* `guidance/hypothesis_tracking` — register or update a hypothesis with
  evidence + status (testing / supported / refuted / inconclusive).
* `guidance/glossary_update` — add or refine domain terms.
* `guidance/writing_standards` — universal writing rules (loaded implicitly
  by every writing/ and synthesis/ protocol).

### Domain

* `domain/domain_analysis` — classify the field + reporting standard.
* `domain/research_design` — pick design + justify sample size.

### Methodology

* `methodology/methodology_selection` — top-level method picker.
* `methodology/research_methods` — deep dive when uncertain which method fits.
* `methodology/tool_discovery` — find + evaluate libraries / CLIs.
* `methodology/clinical_trials` — CONSORT-compliant RCT analysis.
* `methodology/machine_learning` — TRIPOD-AI ML workflow.
* `methodology/meta_analysis` — random/fixed effects, heterogeneity, forest plots.
* `methodology/causal_inference_deep` — DAG, identification, refutation, E-values.
* `methodology/survey_psychometrics` — α/ω, EFA/CFA, sampling weights.

### Literature

* `literature/literature_search` — multi-database systematic search.
* `literature/systematic_review` — full PRISMA workflow.
* `literature/evidence_synthesis` — evidence table, GRADE, contradiction detection.

### Writing

* `writing/writing_core` — banned phrases, tense, number formatting (loaded by all writers).
* `writing/writing_methods` — append a structured method entry.
* `writing/writing_citations` — maintain workspace/citations.md.
* `writing/writing_conclusions` — per-step conclusions.md.
* `writing/writing_analysis_log` — append structured entry to analysis.md.
* `writing/writing_readme` — project + per-step README.

### Synthesis (the final-output protocols)

Each is venue/audience-tailored and enforces quality minimums:

* `synthesis/synthesis_paper` — IMRAD, venue profiles:
  journal / conference / preprint / dissertation / report.
  Word-count bands, figure DPI ≥300, citation cap 40, verified online.
* `synthesis/synthesis_abstract` — structured (journal/preprint) vs
  unstructured (conference) vs grant style. Cap 3 citations.
* `synthesis/synthesis_poster` — tikzposter, audience profiles:
  academic_conference / symposium / industry / teaching. ≥2 figures
  ≥300 DPI, ≤6 citations.
* `synthesis/synthesis_dashboard` — single-file HTML, audience profiles:
  academic / executive / technical / teaching. Sortable tables, lightbox,
  light/dark, print stylesheet.
* `synthesis/synthesis_grant` — funder profiles: nih_r01 / nsf / wellcome /
  erc / doe / industry. Specific Aims first, every aim has milestones +
  pitfalls + alternatives.
* `synthesis/synthesis_report` — audience profiles: internal_team / client /
  technical_audit / policy_brief. Every recommendation evidence-linked.

### Audit

* `audit/audit_and_validation` — citations, assumptions, figures, causal
  language, code lint. Aggregates to workspace/logs/audit_report.md.

### Reproducibility

* `reproducibility/reproducibility` — per-experiment env snapshot, seed
  verification, output hashing, Dockerfile generation.

### Visualization

* `visualization/figure_guidelines` — chart-chooser + formatting standards
  (palettes, fonts, DPI, error indicators).

---

## Quality minimums

Every protocol declares its own minimums in a `quality_bar` block (some
synthesis protocols are especially strict). Examples:

* `synthesis_paper`: abstract 200-300 words, methods ≥400 words, ≥1 figure,
  ≥8 citations, every claim grounded, no causal language for observational
  designs.
* `synthesis_poster`: ≥2 figures ≥300 DPI, ≤6 citations, font ≥24pt,
  one headline message.
* `synthesis_dashboard`: single-file offline HTML, semantic landmarks,
  print-friendly, ≤12 citations, ≥3 sections.
* `synthesis_grant`: Specific Aims ≤500 words (1 page), Approach ≥1500 words,
  every Aim has milestones + pitfalls + alternatives, ≥15 citations.

The AI is instructed to refuse to mark a synthesis complete until the
quality bar passes.

---

## How `model_profile` affects protocols

When the protocol loader reads a YAML, it applies the researcher's
`model_profile` setting:

* `small` — drops verbose keys (`model_adaptations`, `examples`, `templates`)
  to keep tokens minimal. AI tool descriptions are also trimmed to first
  sentence only.
* `medium` — standard.
* `large` — full detail; protocols may suggest multi-step planning.

This means a researcher on DeepSeek-7B local gets a leaner experience than
one on Claude Opus, without protocol authors needing to maintain two files.

---

## Adding a new protocol

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the schema. Briefly:

```yaml
id: my_protocol
name: My Protocol
version: '1.0.0'
schema_version: '2.0'
description: One-line summary.
trigger: When the AI should run this.
prerequisites: [list of files/states required]

steps:
  - id: step_id
    name: Step Name
    description: |
      Concrete tool calls (underscore form), one numbered action per step.

expected_outputs:
  - path/to/file

next_protocol: category/next_one     # null if terminal
on_failure: guidance/dead_end_routing
```

The loader auto-injects a `protocol_completion` step — don't add one yourself.
