# Beginner Example: Sleep Intervention Study

This beginner example demonstrates a complete small analysis:

1. Load a small CSV.
2. Run a treatment vs control comparison (Welch t-test).
3. Export summary metrics and a publication-style figure.
4. Ingest the CSV into the local vector cache using CSV profile embedding.
5. Produce a human-readable markdown report.

## Run

From repository root:

```bash
./.venv/bin/python examples/beginner_study/run.py
```

## Outputs

- `examples/beginner_study/outputs/summary.json`
- `examples/beginner_study/outputs/group_means.csv`
- `examples/beginner_study/outputs/sleep_score_by_group.png`
- `examples/beginner_study/outputs/vss.sqlite`
- `examples/beginner_study/outputs/report.md`
