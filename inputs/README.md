# inputs/ — User-Provided Research Materials

This folder contains everything you provide to the system. The AI **never modifies** files here — it only reads them.

## Structure

```
inputs/
├── intake.md              # Primary intake form (fill this in, or use the interview)
├── intake.yaml            # Alternative: YAML format for complex projects
├── intake.json            # Alternative: JSON format for programmatic use
├── data/
│   ├── raw/               # ← Drop your data files here
│   └── README.md          # Describe your data files
├── papers/                # PDFs of relevant papers (optional)
└── context/               # Abstracts, notes, links, background docs (optional)
```

## Quick Start

### 1. Drop Your Data

Place data files in `data/raw/`. Supported formats:

| Format | Extension | Notes |
|--------|-----------|-------|
| CSV | `.csv` | Auto-detects delimiter and encoding |
| TSV | `.tsv` | Tab-separated |
| Parquet | `.parquet` | Fast, columnar |
| Excel | `.xlsx`, `.xls` | First sheet by default |
| Stata | `.dta` | Versions 10-17 |
| SPSS | `.sav` | IBM SPSS |
| SAS | `.sas7bdat` | SAS datasets |

### 2. Fill the Intake

**Option A: Conversational Interview** (recommended for beginners)
```bash
rcp intake-interview --start
```
The AI asks 5 questions in plain English and generates `intake.md` automatically.

**Option B: Manual** — Edit `intake.md` directly. Only 3 fields are required:
- **Title**: Your project name
- **Primary research question**: What do you want to find out?
- **Outcome variable**: What is the main thing you're measuring?

**Option C: YAML** — Use `intake.yaml` for complex multi-question projects.

**Option D: JSON** — Use `intake.json` for programmatic/API workflows.

### 3. Add Context (Optional)

- **papers/**: Drop PDFs of relevant papers. The system will extract claims and build an evidence matrix.
- **context/**: Add abstracts, notes, links, background documents, or theoretical frameworks.

## File Naming Conventions

- Use descriptive names: `survey_2024_wave1.csv`, not `data1.csv`
- Use underscores, not spaces
- Include version or date if applicable: `clinical_data_v2.parquet`
- Never overwrite raw files — create new versions instead

## Data Scale Guidelines

| File Size | System Behavior |
|-----------|----------------|
| < 100MB | Full profiling with pandas |
| 100MB - 1GB | Sampled profiling (10k rows), polars recommended |
| 1GB - 10GB | Polars lazy frames required |
| > 10GB | Polars lazy + chunked processing required |

## What Happens Next

After you add data and fill the intake:

1. The system scans all files and profiles them automatically
2. It cross-references your intake with actual data columns
3. It assesses feasibility (go / caution / stop)
4. It creates the full project structure under `01_workspace/`, `02_experiments/`, `03_synthesis/`
5. It generates follow-up questions only if critical information is missing

## Rules

1. **Never modify raw data files** — only create new processed versions
2. **The AI never writes to this folder** — it only reads
3. **All raw data files get SHA-256 hashes** recorded before use
4. **Large files are sampled** for profiling to prevent OOM errors
5. **Keep this folder clean** — only include files relevant to your research
