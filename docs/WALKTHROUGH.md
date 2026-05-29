# Research OS — End-to-End Walkthrough

A long, opinionated, deliberately messy simulation of how a real research
project unfolds inside Research OS. Mixes **shell commands you run
yourself** (lines starting with `$`) with **chat messages you type at
your AI IDE** (lines starting with `you ▸`). The chat messages are
intentionally imperfect — comma splices, half-finished sentences,
mid-turn pivots, retroactive constraints — because that's how
researchers actually talk and the system has to handle it.

Everything here is reachable with the install you already have. If a
section uses an optional dependency (literature providers, LaTeX) that
isn't installed, the AI will tell you and either degrade gracefully or
suggest the install — both behaviours are exercised below.

> Conventions
> * `$` = shell command (you run it)
> * `you ▸ ...` = you type into the AI IDE chat
> * `AI ⤺ ...` = a paraphrase of what the AI tends to say back (not a
>   verbatim transcript — your IDE's wording will differ)
> * `tool: name` = MCP tool the AI calls under the hood

---

## Table of contents

1. [Day 1 — setup, intake, first day of real work](#day-1)
2. [Day 2 — pivots, dead-ends, branches, casual mode](#day-2)
3. [Day 3 — long-running jobs, handoff, autopilot](#day-3)
4. [Day 4 — methodology variety (ablation, replication, pilot, simulation)](#day-4)
5. [Day 5 — a totally different project (qualitative interviews + mixed methods)](#day-5)
6. [Day 6 — a quick paper review (orthogonal task, doesn't touch the main project)](#day-6)
7. [Day 7 — synthesis (paper + abstract + poster + dashboard + grant)](#day-7)
8. [Day 8 — audit + reproducibility + verified citations](#day-8)
9. [Day 9 — resume from a different chat / different AI model](#day-9)
10. [Day 10 — wrap up and ship](#day-10)
11. [Cheat sheet — the 15 phrases that cover 90% of usage](#cheat-sheet)
12. [Token-budget notes (so the AI doesn't burn your money)](#token-budget)

---

<a name="day-1"></a>
## Day 1 — Setup, intake, first day of real work

### 1.1 Install Research OS

```
$ conda create -n research-os python=3.11 -y
$ conda activate research-os
$ pip install "research-os[ci] @ git+https://github.com/VibhavSetlur/Research-OS.git"
```

`[ci]` is the lean install — fine for everything in this walkthrough.
For shap/xgboost/jupyter heavy ML or full search providers, use
`[all]` instead. R / Julia / Docker need their own runtimes installed
separately.

```
$ research-os --help
$ python -c "import research_os; print(research_os.__version__)"
```

If you cloned the repo:

```
$ cd Research-OS
$ pip install -e ".[ci,dev]"
$ python scripts/preflight.py
```

Preflight runs 12 checks in ~2 seconds. If anything fails, fix that
before going further — the AI relies on a clean wire-up.

### 1.2 Scaffold a project

```
$ mkdir -p ~/projects/penguin-bills && cd ~/projects/penguin-bills
$ research-os init --name "Penguin Bill Dimorphism"
```

What that did, in one paragraph: created `inputs/raw_data/`,
`inputs/literature/`, `inputs/context/`, `workspace/`, `synthesis/`,
`docs/`, `environment/`, `.os_state/`; dropped MCP configs for every
supported IDE (`.cursor/mcp.json`, `.claude/mcp.json`, `.antigravity/`,
`.vscode/`, plus `opencode.json`, `.windsurfrules`, `.continuerules`,
`.aider.conf.yml`, `AGENTS.md`, `CLAUDE.md`, `GETTING_STARTED.md`,
`.gitignore`); initialised `inputs/researcher_config.yaml` with sane
defaults; wrote a minimal `state_ledger.json` + `manifest.json` under
`.os_state/`.

### 1.3 Pull some data + drop a PDF + add notes

```
$ curl -L -o inputs/raw_data/penguins.csv \
    https://raw.githubusercontent.com/allisonhorst/palmerpenguins/main/inst/extdata/penguins.csv

$ mkdir dropbox
$ curl -L -o dropbox/horst2020penguins.pdf \
    https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0090081&type=printable \
    || echo "%PDF-1.4 placeholder" > dropbox/horst2020penguins.pdf

$ cat > inputs/context/pi_briefing.md <<'EOF'
# PI briefing — penguin bill dimorphism

Research question: Do bill dimensions differ between Adelie and Chinstrap
penguins after controlling for body mass, and does the pattern hold across
the three islands?

H1: Chinstraps have longer bills than Adelies even after mass adjustment.
H2: The Adelie/Chinstrap contrast is consistent across islands.
H3: Sex modifies the species effect.

Deadline: draft figures for Friday's lab meeting; full short paper by end
of month.
EOF

$ cat > inputs/context/prior_attempt.md <<'EOF'
# Notes from previous attempt

Tried a simple two-sample t-test on bill_length_mm by species last quarter.
Found a difference but did not control for body mass. Reviewer said the
effect could just be allometry. Need a model that conditions on body mass
and probably allows island-level random effects.
EOF
```

### 1.4 Open the project in your AI IDE

Whichever IDE you use should auto-detect the MCP config and connect to
the `research-os` server. If it doesn't (sometimes IDEs cache MCP
configs):

```
$ research-os start --workspace .
```

Leave that running in a second terminal. The IDE will pick it up on
restart.

### 1.5 First chat — let the AI orient itself

```
you ▸ hey start the session
```

**What the AI should do** (this is the new, cheap routing path):

1. `tool: sys_boot` — single call, ~800 tokens back. Returns
   `pause_classification: fresh_session`, `pipeline_stage: init`,
   autonomy `supervised`, model_profile `medium`, no active plan,
   `next_protocol: guidance/project_startup`, and `advice: "Fresh
   project. After the researcher's first message, call tool_route with
   their prompt to pick the right protocol."`
2. The AI greets you with one line.

```
AI ⤺ Penguin Bill Dimorphism · stage `init` · supervised mode ·
     model_profile medium. Pipeline suggests `guidance/project_startup`
     next, but go ahead — what do you want to do?
```

Notice the AI did NOT load any protocol YAML, did NOT call
`sys_state_get` separately, did NOT call `sys_protocol_history`. All in
one `sys_boot` call.

### 1.6 The first real ask — messy version

```
you ▸ ok so I dropped a bunch of stuff, theres a pdf in the dropbox folder
      that came in over slack, the csv is the penguins data and theres
      a couple of context notes from my PI, can you like figure out
      whats going on and start the project, also dont assume the domain
      is generic this is actually biology specifically penguin morphology
```

**Behind the scenes:**

1. `tool: tool_route(prompt="ok so I dropped a bunch of stuff...")` — returns:
   - `primary_protocol: guidance/project_startup`
   - `shortcut_tool: tool_intake_autofill`
   - `complexity: high` (>25 words + multiple verbs)
   - `active_plan_path: .os_state/active_plan.json` (persisted; AI must walk it)
   - `decomposition`:
     1. `tool_context_intake` — route loose files into inputs/
     2. `tool_intake_autofill` — infer domain + question + hypotheses
     3. `sys_state_get` — confirm registered hypotheses + new docs
2. The AI **walks the plan** step-by-step, calling `tool_plan_advance`
   between each.

```
AI ⤺ Plan persisted (3 steps). Executing #1 — moving dropbox files
     into inputs/...
        tool: tool_context_intake → 1 PDF routed to inputs/literature/
     Executing #2 — autofill from inputs/...
        tool: tool_intake_autofill → domain inferred as "biology",
        research question pulled from PI briefing, 3 hypotheses
        registered (H1, H2, H3), researcher_config blanks filled.
     Executing #3 — confirm state...
        tool: sys_state_get → 3 active hypotheses, intake.md fresh,
        research_question.md no longer placeholder.

     One thing: you said "biology specifically penguin morphology" but
     the autofill landed on "biology" only. Want me to set the domain
     to "biology_ecology_morphology" via sys_config_set?
```

```
you ▸ yeah biology_ecology is fine, dont need to be specific
you ▸ also my expertise is advanced not intermediate, ive done lots of mixed models
```

**Behind the scenes:**

- `tool: sys_config_set key="domain" value="biology_ecology"`
- `tool: sys_config_set key="researcher.expertise_level" value="advanced"`

From here the AI skips beginner-level explanations. It will also assume
you know what a random intercept is.

### 1.7 What to do next?

```
you ▸ so whats next
```

`tool: tool_route(prompt="so whats next")` →
`shortcut_tool: tool_plan_next_step`, complexity low.

```
AI ⤺ tool: tool_plan_next_step(goal="bill dimensions by species controlled for mass")
     -> 5 literature hits, 3 tool candidates, 2 recommendations:

     1. Start with `guidance/analysis_plan` for a baseline EDA on
        penguins.csv (distribution scan + missingness + island/sex tally).
     2. Skip directly to a mixed-effects model targeting H1 (since the
        prior_attempt notes call out the missing mass adjustment).

     I lean toward #1 — your figures-for-Friday deadline benefits from
     a quick EDA pass. Go?
```

```
you ▸ yeah go with 1
```

`tool: sys_protocol_get name="guidance/analysis_plan" format="summary"` —
~300 tokens, returns step headings. The AI then picks the step it needs
and loads it with `format="step" step_id="..."` when ready.

```
AI ⤺ Loaded analysis_plan summary (11 steps). Walking step 1
     (`scope_step`) next.
        tool: sys_path_create name="baseline_eda"
              hypothesis="(EDA — no specific hypothesis tested)"
        -> created workspace/01_baseline_eda/ with subfolders.

        tool: sys_protocol_get name="analysis_plan"
              format="step" step_id="ground_methods"
        tool: tool_research_method query="exploratory data analysis
              of penguin morphometric data" limit=5
        -> 6 papers found, top 2 saved to
           workspace/01_baseline_eda/literature/.

        tool: sys_file_write filepath="workspace/01_baseline_eda/scripts/01_baseline_eda_v1.py"
              content=<...>
        tool: tool_python_exec script_path="workspace/01_baseline_eda/scripts/01_baseline_eda_v1.py"
        -> exit_code 0; figures saved to outputs/figures/.

        tool: mem_methods_append method="descriptive EDA"
              step_number="01" step_name="baseline_eda" ...
        tool: mem_decision_log context="EDA approach"
              selected="quartile summaries + paired plots by species"
              rationale="quick, matches prior_attempt's framing"

        tool: sys_file_write filepath="workspace/01_baseline_eda/conclusions.md"
              content="...Adelies and Chinstraps clearly differ in bill_length_mm;
              sex looks important; sample per island/species is small (~40-50)."

     Step done. Want me to advance the active plan or stop here?
```

### 1.8 End of Day 1

```
you ▸ stop here Im done for today
```

No formal handoff yet — the work-in-progress is in state and on disk.
Close the tab.

---

<a name="day-2"></a>
## Day 2 — Pivots, dead-ends, branches, casual mode

### 2.1 Pick back up

```
you ▸ pick up where we left off
```

`tool: tool_route(prompt="pick up where we left off")` →
`shortcut_tool: tool_session_resume`, complexity low.

```
AI ⤺ tool: tool_session_resume
     -> pause_reason: completed_step. Last action: analysis_plan step
        `document_conclusions` completed. 3 hypotheses still testing.
        1 active path: 01_baseline_eda. No running tasks.
        Recommended next: continue analysis_plan or pivot.

     Continue, switch tracks, or start something new?
```

### 2.2 A mid-stream pivot ("actually no, redo it differently")

```
you ▸ wait actually I want to redo the EDA but group by island and year
      too, and also DROP missing rows for this pass I dont want to impute
      yet. Also can you skip the t-test idea entirely, my reviewer last
      time flagged that as a dead end so dont even start it
```

Two distinct asks in one message:
- Modify the existing step (re-do EDA with extra grouping + listwise deletion)
- Record an avoidance constraint ("don't try t-tests")

```
AI ⤺ Two things:

     (1) Bumping the EDA to v2:
         tool: sys_file_write filepath="workspace/01_baseline_eda/scripts/01_baseline_eda_v2.py"
               -> new version, NOT overwriting v1 (atomic versioning).
         tool: tool_python_exec script_path="..._v2.py" -> ok.
         tool: mem_methods_append method="EDA v2 — added island×year grouping; listwise deletion"
               justification="researcher pivot, exploratory only"
         tool: sys_file_write filepath="workspace/01_baseline_eda/conclusions.md"
               -> appended a v2 note + updated decision.

     (2) Logging the t-test avoidance as a project decision:
         tool: mem_decision_log context="method exclusion"
               selected="exclude unadjusted t-tests"
               rationale="reviewer-flagged in prior attempt; need mass-adjusted model"

     Done. The exclusion is now in the audit trail — future steps can
     point at it. Next?
```

### 2.3 Deliberate dead-end demo

A naive baseline path the AI will then abandon:

```
you ▸ actually one sec, lets fit a logistic regression of species ~
      bill_length_mm just to see what we get, fast and dirty
```

```
AI ⤺ tool: tool_route → analysis_plan (high complexity due to chained verbs)
     tool: sys_path_create name="logistic_species_bill_naive"
     -> workspace/02_logistic_species_bill_naive/
     ...fits via statsmodels...
     conclusions.md: "AUROC 0.88. BUT body mass is uncontrolled — same
     issue prior_attempt called out. Recommend abandon."
```

```
you ▸ yeah thats the same problem from before, abandon it. and capture
      the lesson so we dont try it again
```

```
AI ⤺ tool: tool_route → guidance/dead_end_routing
     tool: sys_path_abandon path_name="02_logistic_species_bill_naive"
           rationale="ignores body-mass confound; reviewer-flagged in prior attempt"
     -> folder renamed to 02_logistic_species_bill_naive__DEAD_END
     tool: tool_dead_end_lessons -> wrote workspace/logs/dead_end_lessons.md
     tool: tool_plan_next_step goal="mass-adjusted species effect"
     -> recommendation: branch to a mixed-effects model.

     Branch now?
```

### 2.4 The real model — a proper branch

```
you ▸ yes branch into a proper mixed model. linear, bill_length_mm as
      outcome, body_mass_g as covariate, species + sex + island as fixed
      effects, and island as a random intercept just in case theres
      between-island heterogeneity
```

`tool: tool_route` → analysis_plan, high complexity, plan persisted.

```
AI ⤺ Plan persisted (6 steps). Walking:
     tool: tool_branch_recommendation reason="alternative model approach"
     -> recommendation: branch.
     tool: sys_path_create name="lmm_bill_length_mass_adjusted"
     tool: tool_research_method query="linear mixed effects allometric
           penguin morphology"
     tool: tool_literature_search_and_save query="random intercept
           island morphometric study" source="semantic_scholar"
           step_id="03_lmm_bill_length_mass_adjusted" limit=5 download_top=2
     -> 2 PDFs saved to workspace/03_lmm_.../literature/ with .meta.yaml sidecars
     tool: sys_file_write filepath="workspace/03_lmm_.../scripts/03_lmm_..._v1.py"
     tool: tool_python_exec ...
     tool: tool_audit_assumptions filepath="workspace/03_lmm_.../outputs/data/residuals.csv"
     -> normality + homoscedasticity check, mild deviation, logged.
     tool: mem_hypothesis_update hypothesis_id="H1" status="supported"
           evidence="species_chinstrap β=2.3mm (95% CI 1.4-3.2), p<0.001 after mass adjustment"
     tool: sys_file_write filepath="workspace/03_lmm_.../conclusions.md"
           content="<...>"
     tool: tool_plan_advance -> plan complete, archived.

     H1 supported, H2 and H3 still testing.
```

### 2.5 Casual exploration tangent

```
you ▸ ok totally side thing, no formal write up just exploratory, I
      noticed in v2 the gentoo bill_depth_mm distribution looks weird,
      can you poke at that real quick? scratch sandbox is fine
```

```
AI ⤺ tool: tool_route → guidance/casual_exploration (matched "totally side
     thing", "exploratory")
     Casual mode confirmed — skipping the reproducibility paperwork.
     tool: tool_scratch_write filename="gentoo_depth_quick.py"
           content="...quick groupby + plot..."
     tool: tool_scratch_run filename="gentoo_depth_quick.py"
     -> stdout: "gentoo bill_depth_mm bimodal — clusters at ~15 and ~18mm,
        could be sex-linked dimorphism stronger than in Adelie or Chinstrap"

     Three bullets:
     - Tried: group gentoo by sex, plot histogram.
     - Saw: clear bimodality, gap around 16.5mm.
     - Worth a real experiment? Yes — could be H4 candidate.

     Want me to promote this into a proper step?
```

```
you ▸ yeah promote it, and add H4 chinstrap sex effect is stronger in gentoo
```

```
AI ⤺ tool: mem_hypothesis_add statement="Sex × species interaction is
           stronger in gentoo than in Adelie/Chinstrap"
           status="testing"
     -> H4 registered.
     tool: sys_path_create name="gentoo_sex_dimorphism"
     -> workspace/04_gentoo_sex_dimorphism/ created with scratch file
        promoted into scripts/04_gentoo_sex_dimorphism_v1.py
     tool: mem_methods_append ... (back-filled retroactively)
```

### 2.6 Mid-flow context drop

Your PI emails you another paper at 4pm. You drop it in the dropbox:

```
$ cp ~/Downloads/lewis2023_gentoo_dimorphism.pdf dropbox/
```

```
you ▸ new paper just landed in dropbox, please integrate it
```

```
AI ⤺ tool: tool_context_intake also_autofill=true
     -> 1 PDF routed to inputs/literature/, autofill re-run, no new
        hypotheses inferred (paper already aligns with H4).

     Want me to also save it scoped to step 04 as a canonical reference?
     (It would go under workspace/04_gentoo_sex_dimorphism/literature/.)
```

```
you ▸ yes good idea
```

### 2.7 End of day 2 (hard close, no handoff doc this time)

```
you ▸ ok done for the day
```

The state ledger captures everything. The active plan is empty (last
one auto-archived). Tomorrow's resume will work.

---

<a name="day-3"></a>
## Day 3 — Long-running jobs, handoff, autopilot

### 3.1 Resume

```
you ▸ ok where were we, also Im a little fuzzy on what was happening
      with hypothesis H2
```

`tool: tool_route` → `tool_session_resume`. Then the AI also calls
`mem_hypothesis_list` to give a per-hypothesis breakdown.

```
AI ⤺ Resume brief: stage analysis, 3 active paths (01, 03, 04), 1 dead-end
     (02). Hypotheses: H1=supported, H2=testing, H3=testing, H4=testing.
     For H2 specifically: it's "the Adelie/Chinstrap contrast is consistent
     across islands". Step 03's mixed model HAS island as a random
     intercept but you haven't yet pulled out the island×species
     interaction term — that's what would test H2 directly.

     Continue with H2-specific extension, or pivot?
```

### 3.2 Long-running bootstrap

```
you ▸ ok lets bootstrap the LMM coefficients for the discussion section,
      do 5000 reps. background it, Im going to lunch
```

```
AI ⤺ tool: tool_route → background_task shortcut.
     tool: sys_file_write filepath="workspace/03_lmm_.../scripts/03_lmm_..._bootstrap_v1.py"
     tool: tool_task_run command="python workspace/03_lmm_.../scripts/03_lmm_..._bootstrap_v1.py"
           description="LMM bootstrap 5000 reps"
     -> task_id task_20260527_133241_a3b7c1, pid 482211.

     Backgrounded. Poll with tool_task_status when you're back.
```

### 3.3 Handoff midway

You realise you need to hop to a meeting:

```
you ▸ shoot I have a thing, wrap up the session, the bootstrap can keep
      running. Make sure tomorrows session knows everything thats going
      on including that ablation idea I mentioned offhand last week
      about dropping flipper_length
```

```
AI ⤺ tool: tool_route → guidance/chat_handoff
     tool: sys_checkpoint_create description="handoff <iso>"
     tool: sys_session_handoff
     -> wrote .os_state/handoffs/handoff_<iso>.md with:
        - State + active hypotheses
        - Running task (the bootstrap, with PID)
        - Open thread: H2 island×species interaction not yet tested
        - Open thread: ablation idea about dropping flipper_length
          (captured from your message just now)
        - Dead-end lessons (no unadjusted t-tests)
        - Notes for the next AI

     tool: sys_notify level="info" message="Session handed off. Bootstrap
           running as task_20260527_133241_a3b7c1."

     Done. Tomorrow's first prompt should be `pick up where we left off`
     and the resume tool will read this handoff.
```

### 3.4 Try autopilot for tomorrow

```
you ▸ also you know what, switch to autopilot for tomorrow, I trust the
      pipeline, just dont write the final paper without me and dont run
      anything that needs more than 1 GPU hour without asking
```

```
AI ⤺ tool: sys_config_set key="interaction.autonomy_level" value="autopilot"
     tool: sys_protocol_get name="guidance/autopilot" format="summary"
     -> Loaded. The mandatory gates are:
        1. tool_synthesize for the final paper
        2. tool_audit_reproducibility (slow)
        3. tool_research_tool paid_or_licensed candidates
        4. sys_path_abandon
        5. sys_file_write to synthesis/ with force=true
        6. tool_package_install for new packages
        7. tool_task_run > 1 GPU-hour / >10 GB RAM / >50 GB I/O

     I'll auto-checkpoint after every step and notify you every 60 min
     during long runs. To halt mid-run say "halt and show me".
```

---

<a name="day-4"></a>
## Day 4 — Methodology variety

This day exercises four methodology protocols that come with v1.x:
**ablation**, **replication**, **pilot**, and **simulation**.

### 4.1 Ablation study

```
you ▸ ok lets do that ablation on the LMM, drop flipper_length, drop sex,
      drop the random intercept one at a time, want to see which
      component is really doing the work
```

```
AI ⤺ tool: tool_route → methodology/ablation_study
     tool: sys_protocol_get name="methodology/ablation_study" format="summary"
     -> 7 steps. Walking step `enumerate_components` then `baseline_lock`...

     tool: sys_path_create name="ablation_lmm"
     tool: sys_file_write outputs/reports/ablation_plan.md content="<...>"
     tool: sys_file_write scripts/05_ablation_lmm_baseline_v1.py
     tool: tool_python_exec ... (baseline freeze with frozen seeds)
     tool: sys_file_write scripts/05_ablation_lmm_v1.py
     tool: tool_python_exec ... (3 ablations, same seeds, same splits)
     tool: sys_file_write outputs/reports/ablation_table.md content="<...>"

     Result: flipper_length is essential (Δ AIC +12), sex is helpful
     (Δ AIC +4), random intercept is neutral (Δ AIC -0.5). Recommendation:
     keep flipper, keep sex, can drop random intercept for parsimony.
```

### 4.2 Replication of an earlier paper

A reviewer asked: does your finding replicate Horst 2014?

```
you ▸ reviewer wants us to show this replicates horst 2014 specifically.
      direct replication on their fig 3 — same model, our data
```

```
AI ⤺ tool: tool_route → methodology/replication_study (matched "replicate"
     plus "horst 2014")
     tool: sys_path_create name="replicate_horst2014_fig3"
     tool: sys_file_read inputs/literature/horst2020penguins.pdf
     -> extracted original spec: ANCOVA bill_length ~ species + body_mass,
        N=344, F-statistic, R²=0.78.
     tool: sys_file_write outputs/reports/replication_design.md content="<...>"
     tool: sys_file_write outputs/reports/original_spec.md content="<...>"
     tool: sys_file_write scripts/06_replicate_horst2014_fig3_v1.py
     tool: tool_python_exec ... (re-runs ANCOVA on our data)
     tool: sys_file_write outputs/reports/comparison.md
     -> verdict: replicated. CI overlaps; β within 8% of original.

     Conclusions.md says replicated; recommend including this as
     supplementary figure S1.
```

### 4.3 Pilot study for a new measurement protocol

You're thinking about adding GPS tracking to the next field season:

```
you ▸ totally different topic, were thinking about adding GPS tracking
      for the next fieldwork. before we commit can you set up a pilot
      study protocol that we can hand to the field team? n=15, just
      checking feasibility, recruitment, instrument breakage
```

```
AI ⤺ tool: tool_route → methodology/pilot_study
     tool: sys_path_create name="pilot_gps_tracking"
     tool: sys_file_write outputs/reports/pilot_aim.md
     -> Aim: instrument feasibility + recruitment rate; NOT effect estimation.
     tool: sys_file_write outputs/reports/feasibility_template.md
     -> the form the field team fills in as they go.

     The protocol's quality_bar says pilots must NOT report confirmatory
     effect estimates — the template enforces that. Hand pilot_aim.md
     and feasibility_template.md to the field team.
```

### 4.4 Simulation to support a Monte Carlo claim

You want to justify why N=300 is enough for the main analysis:

```
you ▸ I need to show that our N=300 is enough to detect a 2mm bill effect
      at alpha 0.05 and 80 percent power, can you run a simulation, ADEMP
      style
```

```
AI ⤺ tool: tool_route → methodology/simulation_studies
     tool: sys_path_create name="sim_power_lmm_n300"
     tool: sys_file_write outputs/reports/ademp.md
        Aim: confirm N=300 yields ≥80% power for a 2mm species effect under LMM.
        DGM: simulated penguins with known parameters from our pilot estimates.
        Estimands: power = P(reject H0: β=0 | β=2).
        Methods: lme4-style LMM.
        Performance: power, type-I rate, bias, MSE, MC SE.
     tool: sys_file_write outputs/reports/seed_plan.md
     tool: sys_file_write scripts/07_sim_power_lmm_n300_pilot_v1.py
     tool: tool_python_exec ... (10 reps × 5 scenarios for the pilot)
     tool: tool_task_run command="python .../07_sim_power_lmm_n300_full_v1.py"
           description="ADEMP full simulation 5000 reps"
     -> backgrounded. Poll later.
```

---

<a name="day-5"></a>
## Day 5 — A totally different project (qualitative interviews + mixed methods)

You start a second project in a new folder. This is to demo the
**qualitative_research** and **mixed_methods** protocols. There are no
modality-specific config presets — `research-os init` writes the one
neutral `researcher_config.yaml`, and `domain_analysis` infers the
qualitative shape from the transcripts.

```
$ mkdir -p ~/projects/penguin-keepers-interviews && cd ~/projects/penguin-keepers-interviews
$ research-os init --name "Penguin Keeper Practices"

# The init wrote inputs/researcher_config.yaml as a neutral template.
$ chmod 600 inputs/researcher_config.yaml

# Add the transcripts (whatever you have — even just plain text)
$ cp ~/fieldnotes/transcripts/*.docx inputs/raw_data/
```

```
you ▸ start session
you ▸ this is a qualitative interview study, 12 transcripts of zoo
      keepers about their penguin husbandry practices, were doing thematic
      analysis using grounded theory style coding, also want this to be
      mixed methods eventually because well also have keeper survey data
      coming later in the year
```

```
AI ⤺ tool: sys_boot -> fresh_session, domain "qualitative", reporting
     standard "COREQ".
     tool: tool_route -> primary methodology/qualitative_research,
     alternative methodology/mixed_methods. complexity: high. plan
     persisted (5 steps).

     Walking the qualitative_research plan:
     tool: sys_path_create name="qual_keeper_practices"
     tool: sys_file_write outputs/reports/interview_protocol.md
     -> Documented: purposive sample, semi-structured topic guide,
        reflexivity statement template, member-checking plan, COREQ
        items addressed.
     tool: tool_context_intake -> 12 .docx files routed to inputs/raw_data/
        and symlinked into workspace/01_qual_keeper_practices/data/input/.

     Next step is open coding (first pass). I can stage that as a
     scratch script, or use an external coding tool — your preference?
```

```
you ▸ scratch script is fine, we want LLM assisted coding for the first
      pass then I review manually
```

```
AI ⤺ tool: mem_methods_append method="LLM-assisted open coding (first pass)"
           implementation="custom"
           justification="speed; human review on second pass for trustworthiness"
     tool: tool_scratch_write filename="open_code_v1.py"
     tool: tool_scratch_run filename="open_code_v1.py"
     -> 87 open codes extracted, saved to outputs/reports/open_codes.md.

     Per the protocol's quality_bar, every theme MUST be supported by
     ≥2 quotes from ≥2 participants and at least one disconfirming case
     must be reported. Continue to axial coding, or pause for your review?
```

```
you ▸ pause, I need to review the open codes before clustering
you ▸ also remind me when survey data comes in, we wanna switch to
      mixed_methods protocol and integrate
```

```
AI ⤺ tool: sys_notify level="info" message="Open coding paused for
           researcher review. Mixed-methods integration deferred until
           survey data arrives."
     -> Logged. Resume any time with "continue open coding" or
        "load mixed methods" once the survey is in.
```

---

<a name="day-6"></a>
## Day 6 — A quick paper review (orthogonal task)

A colleague pings you about reviewing their draft. This shouldn't touch
the penguin project at all.

```
$ cd ~/projects/penguin-bills
$ cp ~/Downloads/colleague_draft_v3.pdf inputs/literature/
```

```
you ▸ hey can you tear apart colleague_draft_v3 in inputs/literature,
      quick review only, focus on the statistical inference, sample size
      and confidence intervals especially. also be tough my friend
      asked for a brutal review
```

```
AI ⤺ tool: tool_route(prompt="hey can you tear apart...")
     -> shortcut_tool: tool_quick_review, primary guidance/quick_paper_review.
        complexity: low.
     tool: tool_quick_review paper_path="inputs/literature/colleague_draft_v3.pdf"
           lens="statistical_inference"
     -> stages a skeleton at workspace/reviews/colleague_draft_v3.md
        with sections for verdict, 3 strengths, 5 concerns, citations.
     tool: sys_protocol_get name="guidance/quick_paper_review" format="step"
           step_id="ground_method"
     tool: sys_file_read inputs/literature/colleague_draft_v3.pdf
     tool: tool_research_method query="<their headline method> + statistical
           inference common critiques" limit=5
     tool: sys_file_write filepath="workspace/reviews/colleague_draft_v3.md"
           content="<filled-in review>"

     Verdict: MAJOR REVISE. Three strengths, five concerns (most→least
     severe), 8 grounding citations. Total length 740 words. Want me to
     also add it to inputs/literature_index.yaml? (Default: no — quick
     reviews don't pollute the main project's literature.)
```

```
you ▸ no dont add it
```

The main project remains untouched. The review is just under
`workspace/reviews/`.

---

<a name="day-7"></a>
## Day 7 — Synthesis: paper + abstract + poster + dashboard + grant

The big day. You have results, you want every deliverable variant.

### 7.1 Progress check first

```
you ▸ progress check, where are we
```

```
AI ⤺ tool: tool_route -> progress_check shortcut.
     tool: tool_progress_digest
     -> writes workspace/logs/progress_digest.md and returns the markdown.

     Penguin Bill Dimorphism:
     - 6 experiments active, 1 dead-end
     - H1 supported, H4 supported, H2/H3 inconclusive
     - 18 figures, 7 tables, 11 reports
     - 14 citations in workspace/citations.md
     - Next, per pipeline: synthesis/synthesis_paper
```

### 7.2 The paper

```
you ▸ alright write the paper for an ecology journal, target Functional
      Ecology, use APA citations, structured abstract, 4500 words ish
```

```
AI ⤺ tool: tool_route -> primary synthesis/synthesis_paper, shortcut tool_synthesize.
     complexity: high. plan persisted: synthesize_plan -> audit_synthesis ->
     audit_citations -> synthesize.

     tool: tool_synthesize_plan
     -> proposes section order: Intro / Methods (5 sub) / Results (8 sub)
        / Discussion / Limitations / Conclusion. Estimates 4200-4800 words.
     tool: tool_audit_synthesis paper_path="(staged)" (dry-run)
     -> 3 minor flags: 2 unsupported claims in discussion draft, 1 figure
        missing caption.
     tool: tool_audit_citations
     -> 12 of 14 citations verified via Crossref; 2 unverified (will be
        DROPPED from the final paper, not silently kept).

     Proceed with the build?
```

```
you ▸ yes go, the two unverified are probably from my old notes go ahead
      and drop them
```

```
AI ⤺ tool: tool_synthesize output_type="paper" output_format="both"
           citation_style="apa"
     -> wrote:
        synthesis/paper.md (4400 words)
        synthesis/paper.tex
        synthesis/references.bib (12 verified entries)
        synthesis/figures/fig01_...png through fig07_...png (renumbered + copied)
        synthesis/tables/tab01_...md through tab03_...md

     Tip: tool_latex_compile to get the PDF.
```

### 7.3 Abstract, poster, dashboard, grant — same workspace, different audiences

```
you ▸ also need a structured abstract under 250 words
you ▸ and a tikzposter for the conference next month
you ▸ and a dashboard for the lab meeting, executive tier please, no
      methods detail
you ▸ and an R01 narrative draft, focus on the bill dimorphism aim
```

These are independent so the AI can batch them — but it should
checkpoint between because each is a synthesis call:

```
AI ⤺ Four asks. I'll do them in sequence and notify after each.
     tool: tool_synthesize output_type="abstract" citation_style="apa"
     -> synthesis/abstract.md, 245 words, structured.
     tool: tool_poster_create
     -> synthesis/poster.tex with tikzposter template + numbered figs.
     tool: tool_dashboard_create audience="executive"
     -> synthesis/dashboard.html (single file, sortable, light/dark).
     tool: tool_synthesize output_type="grant"
     -> synthesis/grant.md with R01 structure (Specific Aims,
        Significance, Innovation, Approach). Cited literature only.

     Done. Five synthesis files plus the original paper.
```

### 7.4 LaTeX compile

```
you ▸ compile the paper PDF
```

```
AI ⤺ tool: tool_latex_compile
     -> pdflatex + bibtex run twice; synthesis/paper.pdf created.
```

If pdflatex isn't installed, the tool returns an error and the AI
suggests `apt install texlive-full` (or whatever your OS needs).

---

<a name="day-8"></a>
## Day 8 — Audit + reproducibility + verified citations

```
you ▸ audit everything before I send this, paper, citations, figures
      one by one, the works
```

```
AI ⤺ tool: tool_route -> audit/audit_and_validation, high complexity, plan
     persisted (4 steps).

     tool: tool_audit_synthesis paper_path="synthesis/paper.md"
     -> 1 WARN: discussion contains "causes" — observational data; suggest
        "is associated with" instead.
     tool: tool_audit_citations
     -> all 12 references verified against Crossref. 0 unverified.
     tool: tool_audit_figure filepath="synthesis/figures/fig01_..."
     -> DPI 300 ✓, colorblind palette ✓, axis labels ✓, error bars ✓.
     [repeats for fig02..fig07]
     tool: tool_audit_assumptions filepath="workspace/03_lmm_.../outputs/data/residuals.csv"
     -> minor non-normality, already documented in conclusions.md.

     One fix needed: causal language in discussion paragraph 3. Want me
     to rewrite that paragraph?
```

```
you ▸ yes fix it
```

```
AI ⤺ tool: sys_file_write filepath="synthesis/paper.md" force=true
           content="<...rewritten...>"
     -> done. Re-audit?
```

```
you ▸ yes
```

Re-run audit — all green.

### 8.2 Reproducibility — the slow one

```
you ▸ confirm everything reruns from scratch
```

`tool: tool_route` → reproducibility/reproducibility, shortcut
`tool_audit_reproducibility`. Because autopilot is on AND
`tool_audit_reproducibility` is on the mandatory-gate list:

```
AI ⤺ Autopilot gate hit: tool_audit_reproducibility is slow. Proceed?
```

```
you ▸ yes go
```

```
AI ⤺ tool: tool_audit_reproducibility
     -> walks every numbered step, re-runs scripts in a clean env, hashes
        outputs, compares to recorded hashes.
        6 steps reproduced ✓
        1 step mismatch: 04_gentoo_sex_dimorphism — figure DPI differs
        slightly (interactive matplotlib backend drift). Logged.

     Recommendation: pin matplotlib backend in the step's
     environment/requirements.txt and re-run.
```

```
you ▸ yeah do that
```

---

<a name="day-9"></a>
## Day 9 — Resume from a different chat / different AI model

Maybe you switched IDEs, maybe you swapped models, maybe a co-author
forked the repo. Same procedure:

```
you ▸ ok Im back, the handoff doc should be in os_state somewhere
```

```
AI ⤺ tool: sys_boot
     -> pause_classification: ctx_exhaustion (recent handoff doc found).
     tool: tool_session_resume
     -> reads .os_state/handoffs/handoff_<latest>.md AND state ledger,
        returns: project, hypotheses, dead-end lessons, running tasks
        (none — the bootstrap from day 3 finished), critical assumptions
        list, "Notes for the next AI" addendum.

     I see I'm a different model than before. The previous AI's notes
     say:
       - "Always check tool_dead_end_lessons before retrying methods."
       - "Pilot for GPS tracking is staged — don't run any analysis on
          inputs/raw_data/penguins.csv that assumes GPS."
       - "Reviewer in prior attempt specifically flagged unadjusted
          t-tests."

     Where do you want to pick up?
```

### 9.1 Hand the project to a colleague

You're going on leave; your postdoc takes over.

```
you ▸ Im handing this to my postdoc Maya next week, she needs to be able
      to walk in cold. Write a fresh handoff specifically for her with
      everything important and link the dashboard
```

```
AI ⤺ tool: sys_session_handoff
     -> wrote .os_state/handoffs/handoff_<iso>.md including:
        - Project status + active hypotheses
        - All decisions logged (mem_decision_log entries)
        - All dead-end lessons (workspace/logs/dead_end_lessons.md)
        - Critical assumptions still untested
        - Pointer to synthesis/dashboard.html for overview
        - "Notes for the next AI" addendum tailored to a fresh model
        - Rollback checkpoint id

     Maya should run:
        $ research-os init      # only if she's in a fresh clone
        $ research-os start
        you ▸ pick up where Maya is starting

     The resume tool will read this handoff doc verbatim.
```

---

<a name="day-10"></a>
## Day 10 — Wrap up and ship

### 10.1 One last check

```
you ▸ progress digest one more time, then make sure the dep inventory is
      clean, then a final handoff. Also tell me how many tokens we burned
      this session (rough guess is fine)
```

```
AI ⤺ tool: tool_progress_digest
     -> [reads back digest]
     tool: sys_dep_inventory
     -> all optional deps present; no degraded tools.
     tool: sys_session_handoff
     -> handoff written.

     Token-budget estimate (rough): boot was ~1K tokens (sys_boot + tool_route),
     synthesis pass was the biggest single call (~3K for tool_synthesize,
     ~800 for the paper-audit). Total session: ~12K tokens vs ~40K for
     an equivalent session pre-routing.
```

### 10.2 Commit + push

```
$ git add -A
$ git commit -m "Final paper draft + audit pass + reproducibility check"
$ git push origin main
```

Done. The project is publishable, reproducible, audited, handoff-ready.

---

<a name="cheat-sheet"></a>
## Cheat sheet — the 15 phrases that cover 90% of usage

| Say | Behind the scenes |
|---|---|
| `start session` | `sys_boot` (one call) — greets you |
| `pick up where we left off` | `tool_route` → `tool_session_resume` |
| `fill the intake` | `tool_route` → `tool_intake_autofill` shortcut |
| `what should I do next?` | `tool_plan_next_step` |
| `run a baseline X` | `tool_route` → `analysis_plan` (plan persisted if complex) |
| `branch into Y` | `tool_branch_recommendation` + new numbered step |
| `that's a dead end, move on` | `sys_path_abandon` + `tool_dead_end_lessons` |
| `casual mode, just poke at it` | `guidance/casual_exploration`, scratch-first |
| `quick review of this paper` | `tool_quick_review` shortcut |
| `autopilot until X` | `guidance/autopilot` with explicit gates |
| `wrap up / handoff` | `sys_session_handoff` with checkpoint |
| `progress check` | `tool_progress_digest` |
| `audit the paper` | every applicable `tool_audit_*` in parallel |
| `write the paper for journal Z` | `tool_synthesize` with verified citations only |
| `replicate / ablation / pilot / simulation X` | the matching methodology protocol |

Anything else you say still works — `tool_route` will pick the
best-match protocol and decompose it. The cheat sheet is just the
common case.

---

<a name="token-budget"></a>
## Token-budget notes (so the AI doesn't burn your money)

Routing was redesigned for cost. The rules of thumb:

| Pattern | Token cost | Use when |
|---|---|---|
| `sys_boot` (single call) | ~800 | EVERY session start. Never call sys_state_get/sys_config_get/sys_protocol_history/sys_dep_inventory separately. |
| `tool_route(prompt)` | ~250 | Before loading any protocol. |
| `sys_protocol_get format="summary"` | ~300 | When you need step headings + quality_bar but not the bodies. |
| `sys_protocol_get format="step" step_id="..."` | ~150-500 | When you're actually executing one step. |
| `sys_protocol_get format="full"` | ~1.5-3K | Only when you genuinely need the whole protocol at once. |
| `sys_tool_describe(name)` | ~200 | When you need full description for one tool (the default `list_tools` is already short). |
| `tool_synthesize output_type="paper"` | ~2-5K | One-shot — this is the actual paper draft. |

The router persists an `active_plan` to `.os_state/active_plan.json`
for any `complexity: high` prompt. Walking the plan with
`tool_plan_advance` after each step prevents one-shot failures on deep
asks. If you (or the researcher) pivot mid-plan, call
`tool_plan_clear` and re-route.

If a session feels like it's burning tokens fast, check:
- Is the AI calling `sys_state_get` + `sys_config_get` separately
  instead of `sys_boot`? Tell it to use `sys_boot`.
- Is it loading protocols at `format="full"` to discover step names?
  Tell it to use `format="summary"`.
- Is it one-shotting a complex prompt instead of walking the active
  plan? Tell it to call `tool_plan_advance`.

These three habits add up to a ~70-80% reduction in tokens per turn
compared to the pre-routing version.

---

## Custom-instruction prompts (when you want to break the default flow)

The system handles custom asks too. Examples that exercise less-trodden
paths:

```
you ▸ ignore the autopilot gates for this one call, I need
      tool_audit_reproducibility right now
you ▸ load the analysis_plan protocol in full this time, I want to read
      every step
you ▸ what does tool_external_tool_instructions do? give me the full
      description
you ▸ list every protocol related to literature
you ▸ I want a custom synthesis output, neither paper nor poster, just
      a 2-page memo for stakeholders — pick the closest output_type and
      let me edit afterwards
you ▸ pretend to be a tough reviewer, audit my paper as if you were
      rejecting it
you ▸ apply a custom step name "baseline_with_outlier_robust" and skip
      the auto-prefix this time
you ▸ rollback to checkpoint <id>, I broke something
you ▸ show me the manifest, I want to see every file
you ▸ install statsmodels then redo step 03's diagnostics
you ▸ generate a Dockerfile so my collaborator can rerun this on their
      machine
you ▸ snapshot the current Python environment to step 04
you ▸ what dependencies are missing for me to use ML tools?
you ▸ I made a typo in hypothesis H2, can you fix it without losing the
      history? (mem_hypothesis_update preserves the change in the log)
you ▸ delete that one scratch file I made yesterday, it's polluting
      tool_scratch_list
you ▸ append a glossary entry for "allometry"
you ▸ add a new figure caption to fig03 — I forgot to credit the data source
you ▸ profile the parquet file I just dropped into raw_data
you ▸ sample 20 random rows from the 1.2GB csv, dont load the whole thing
you ▸ render the rmarkdown report I have in step 04
you ▸ run my Julia script for the eigendecomposition step
you ▸ verify the citations in the paper one more time, the AI from
      yesterday might have hallucinated
you ▸ summarise the last 24 hours of activity for me
you ▸ what did we learn from the dead ends so far?
you ▸ workspace looks broken, run the repair tool
you ▸ I want to inspect the protocol_execution_log directly, where is it?
you ▸ add a step literature pdf scoped to step 03 from this arxiv link:
      https://arxiv.org/abs/2401.12345
you ▸ what's the difference between methodology_selection and
      research_methods? when does each fire?
```

Each of these maps to one or more existing MCP tools. If `tool_route`
can't match an explicit trigger phrase, it falls back to keyword-based
intent classification, then to `sys_protocol_list` so the AI can
browse. Nothing in the system silently fails on a weird prompt — at
worst you get a "no match, here are 3 alternatives" response.

---

That's the full system. It's a lot of surface area but the routing
keeps it cheap. If you find yourself burning tokens, the answer is
almost always "the AI skipped sys_boot or tool_route" — point it back
at AGENTS.md and the cheat sheet above.
