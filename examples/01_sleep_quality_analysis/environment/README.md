# Environment

Reproducible Python environment for Research Copilot.

## Setup

### venv (Recommended)

```bash
bash environment/setup.sh
source environment/venv/bin/activate
```

### Conda

```bash
bash environment/setup_conda.sh
conda activate research-copilot
```

### Verify

```bash
rcp preflight
```

## Dependencies

- **Core**: pyyaml, pydantic, diskcache, SQLAlchemy
- **Data**: pandas, numpy, polars, pyarrow, openpyxl, scipy
- **Statistics**: statsmodels, scikit-learn, pingouin
- **Visualization**: matplotlib, seaborn, plotly, altair, bokeh, panel, networkx, Pillow
- **Literature**: habanero (CrossRef), semanticscholar, metapub (PubMed)
- **Export**: pypandoc

See [requirements.txt](requirements.txt) for pinned versions.

## Install Extras

```bash
# MCP server
pip install -e ".[mcp]"

# Dashboards
pip install -e ".[dashboard]"

# PDF/LaTeX export
pip install -e ".[export]"

# Development
pip install -e ".[dev]"

# Everything
pip install -e ".[all]"
```

## Rebuild

```bash
bash environment/setup.sh --clean
source environment/venv/bin/activate
```

## Add Dependencies

1. Add to `requirements.txt` with pinned version
2. Run `pip install -r environment/requirements.txt`
3. Commit the updated file

## Files

| File | Purpose |
|------|---------|
| `requirements.txt` | Pinned Python dependencies |
| `setup.sh` | venv setup script |
| `setup_conda.sh` | Conda setup script |
| `preflight_check.py` | Environment readiness report |
| `runtime_selector.py` | Container/runtime availability |
| `base/` | Base container definitions |
| `domains/` | Domain container stubs |
