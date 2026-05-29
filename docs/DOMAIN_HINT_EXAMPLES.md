# Domain hint examples (illustrative — do NOT copy)

Research OS used to ship ten preset `researcher_config.yaml` files —
one per modality (RCT, genomics, geospatial, time-series, etc.). Each
hardcoded `expected_columns`, `expected_file_extensions`, biases, and a
chosen reporting standard. They acted as ready-made answers — exactly
the prescription we now reject.

There is now ONE template: `templates/researcher_config.yaml`. Every
field is blank. The AI fills it per-project by reasoning over what's
actually in `inputs/`, grounded in literature.

This file is a small catalogue of **reasoning patterns** the AI can
draw on — to recognise the *shape* of a project, not to copy its
content. Treat every example as illustrative. Three patterns. Read for
the shape, write your own answers.

---

## Pattern 1 — Hypothesis-driven experimental science
*(any field where the unit is a controlled experiment + outcome
measurement: a wet-lab RCT, an A/B test, a randomised user study, a
controlled fMRI task design.)*

Signals to look for:
- a registry / pre-registration in `inputs/context/`
- a randomisation table or assignment vector in `inputs/raw_data/`
- outcomes recorded once or repeatedly per unit

Questions the AI must answer per project:
- What's the unit of randomisation, and what's the unit of analysis?
  (Mismatch is the most common bug.)
- Is the primary outcome continuous / binary / count / time-to-event /
  ordinal? What's its distributional shape on this sample?
- What's the missingness mechanism, and on which outcomes?
- Which population is the primary analysis on — everyone-assigned, or
  per-protocol? The literature for *this specific field* will tell
  you which is the convention.
- What community reporting standard applies (CONSORT 2010 for clinical
  RCTs, but other communities have their own — let `domain_analysis`
  surface it from a literature search, never from this file).

Biases the AI must reason about (these recur across experimental
fields; the specifics vary):
- Allocation concealment / blinding integrity
- Differential attrition by arm
- Selective outcome reporting
- Underpowered subgroup splits surviving as "results"

What the AI should NOT do:
- Pick MICE for missing data because "that's what the protocol says".
  Pick it because the missingness mechanism + literature for this
  field support it.

---

## Pattern 2 — Observational / population-level inference
*(any field where the data was collected without the researcher
controlling assignment: epidemiological cohorts, panel economics,
population genomics, web telemetry, claims data, social-survey waves,
ecological observational data.)*

Signals to look for:
- denominators that aren't under researcher control (registry
  populations, scraped corpora, claims databases)
- time + identifier columns (`subject_id`, `firm_id`, `census_tract`,
  `cohort_year`)
- treatment / exposure variables that vary across units but weren't
  assigned

Questions the AI must answer per project:
- What is the causal question, if any? (Description vs. association vs.
  causal effect — be explicit; the analysis follows.)
- What's the identification strategy if causal? (Backdoor, IV,
  difference-in-differences, regression-discontinuity, synthetic
  control — the field's literature dictates which is defensible here.)
- What's the unit of clustering / repeated measurement? Standard
  errors must respect it.
- Which confounders are observable? Which aren't, and how would the
  result move under an unmeasured-confounder counterfactual?

Biases the AI must reason about:
- Selection into the dataset (survivorship, healthy-worker,
  registration bias, sampling frame mismatch)
- Reverse causation (especially with cross-sectional data)
- Measurement error that varies systematically with the exposure
- Population shift between training-era and target-era data

What the AI should NOT do:
- Run propensity-score matching because "that's what observational
  papers do". Justify it from the DAG + the field's current best
  practice.

---

## Pattern 3 — Computational / model-centric work
*(any field where the deliverable is a fitted model or learned
representation: ML benchmarks, NLP system papers, computational
linguistics, protein-language-model embeddings, climate simulation,
agent-based modelling, scientific machine-learning surrogates.)*

Signals to look for:
- a model artefact in `inputs/` or `environment/` (checkpoint, config,
  recipe)
- a held-out evaluation set OR a need to construct one
- a baseline that's expected for comparison

Questions the AI must answer per project:
- What does the field count as a fair baseline here? (This is field-
  specific; surface it from a recent benchmark paper, not memory.)
- What's the evaluation regime — single split, k-fold, leave-one-group-
  out, temporal split, distribution-shift split? The right answer
  depends on the deployment story.
- How sensitive is the headline to (a) random seed, (b) hyperparameter
  choice, (c) data subset? An ablation or sensitivity sweep is rarely
  optional.
- What does the field require in the model card / methods card —
  intended use, training-data provenance, known failure modes?

Biases the AI must reason about:
- Train-test contamination (literal or via shared upstream corpora)
- Benchmark gaming (over-tuned on a single metric the field uses)
- Compute imbalance making the "winning" comparison unfair
- Representational bias from the training data masquerading as
  generalisable performance

What the AI should NOT do:
- Pick SHAP because "that's the interpretation tool". Pick the
  interpretation method appropriate to the model family + the field's
  current literature.

---

## What to do with these

When `domain_analysis` runs, the AI should:
1. Read `inputs/` and the researcher's intake.
2. Recognise which of these patterns (or none, or two combined) the
   project resembles.
3. Use the *questions* in that pattern to drive a literature pass.
4. Write the answers — specific to THIS project — into
   `docs/domain_summary.md`.
5. NEVER paste from this file into `researcher_config.yaml`.

If none of these patterns fits, that's expected. They aren't a
taxonomy. They're three reminders that good methodology comes from
asking the right questions, not from picking the right preset.
