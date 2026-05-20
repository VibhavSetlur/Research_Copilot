# Research Environment

Reproducible Python environment for the Research Copilot system.

## Quick Setup

### Using venv (recommended)
```bash
bash environment/setup.sh
source environment/venv/bin/activate
```

### Using Conda
```bash
bash environment/setup_conda.sh
conda activate research-copilot
```

### Optional: Preflight Check
```bash
python .research/research.py preflight
```

## Recreating Environment

If you need to rebuild from scratch:
```bash
# venv
bash environment/setup.sh --clean
source environment/venv/bin/activate

# conda
bash environment/setup_conda.sh --clean
conda activate research-copilot
```

## Updating Dependencies

```bash
source environment/venv/bin/activate  # or conda activate research-copilot
pip install -r environment/requirements.txt
```

## Adding New Dependencies

1. Add to `environment/requirements.txt` with pinned version
2. Run `pip install -r environment/requirements.txt`
3. Commit the updated `requirements.txt`

## Reproducibility

The `requirements.txt` pins all package versions for reproducibility.
When the AI agent runs `research_init`, it verifies the environment is active
and all dependencies are installed before proceeding.

## Files

| File | Purpose |
|------|---------|
| `requirements.txt` | Pinned Python dependencies |
| `setup.sh` | venv setup script |
| `setup_conda.sh` | Conda setup script |
| `preflight_check.py` | Environment readiness report |
| `runtime_selector.py` | Container/runtime availability report |
| `base/` | Base container definitions and compose file |
| `domains/` | Domain container stubs |
