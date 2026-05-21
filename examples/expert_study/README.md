# Expert Example: Multi-Branch Policy Evaluation

This expert example demonstrates a branch-and-synthesize workflow:

1. Generate a synthetic policy dataset.
2. Execute three branch analyses through `ResearchEngine` with different model formulas.
3. Materialize branch artifacts into a synthesis directory structure.
4. Run `synthesize_results.py` over branch outputs.
5. Apply deterministic fallback winner selection if remote LLM synthesis is unavailable.
6. Update the main trunk path in `03_synthesis/state_ledger.json`.

## Run

From repository root:

```bash
./.venv/bin/python examples/expert_study/run.py
```

## Outputs

- `examples/expert_study/outputs/branches/<branch>/<branch>_results.json`
- `examples/expert_study/outputs/combined_results.json`
- `examples/expert_study/outputs/parallel_results.json`
- `examples/expert_study/outputs/expert_report.md`
