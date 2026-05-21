# Quick Start

## Install

```bash
pip install research-copilot
```

## Initialize

```bash
rcp init my-project && cd my-project
```

## Add Data

Place files in `00_inputs/raw_data/`. Supports CSV, Parquet, Excel, Stata, SPSS, SAS.

## Fill Intake

Edit `00_inputs/intake.md` — 3 fields: title, question, outcome variable.

Or start a conversational interview: `rcp intake-interview --start`

## Run

```bash
rcp status    # Check state
rcp scan      # Scan data
```

Then tell your AI: **"analyze my data"**

## Review

Open `03_synthesis/key_findings.md` for results.

## Iterate

Ask in plain English: "try a different method", "what if we control for X?", "check robustness".

---

**Full docs:** [docs/README.md](docs/README.md)
**Getting started:** [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)
**CLI reference:** [docs/CLI_REFERENCE.md](docs/CLI_REFERENCE.md)
**Help:** `/help` or [GitHub Issues](https://github.com/your-org/research-copilot/issues)
