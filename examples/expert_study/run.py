#!/usr/bin/env python3
"""Expert branching and synthesis example for Research Copilot."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from research_copilot.core.state_ledger import ResearchLedger
from research_copilot.engine import ResearchEngine


REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_ROOT = Path(__file__).resolve().parent
INPUT_DIR = EXAMPLE_ROOT / "input"
OUTPUT_DIR = EXAMPLE_ROOT / "outputs"
DATA_CSV = INPUT_DIR / "policy_panel.csv"

BRANCH_SPECS = {
    "branch_linear": "outcome ~ treatment + baseline + age",
    "branch_interaction": "outcome ~ treatment * baseline + age",
    "branch_site_adjusted": "outcome ~ treatment + baseline + age + C(site)",
}


def _write_dataset() -> None:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(42)
    n = 80
    treatment = rng.integers(0, 2, size=n)
    baseline = rng.normal(0.0, 1.0, size=n)
    age = rng.integers(20, 60, size=n)
    site = rng.choice(["north", "south", "east", "west"], size=n)
    noise = rng.normal(0.0, 0.8, size=n)

    outcome = 5.0 + 1.2 * treatment + 0.8 * baseline + 0.03 * age + noise

    df = pd.DataFrame(
        {
            "treatment": treatment,
            "baseline": baseline,
            "age": age,
            "site": site,
            "outcome": outcome,
        }
    )
    df.to_csv(DATA_CSV, index=False)


def _branch_script(formula: str, output_json: Path, output_csv: Path) -> str:
    return f'''
import json
import pandas as pd
import statsmodels.formula.api as smf

input_csv = r"{DATA_CSV}"
output_json = r"{output_json}"
output_csv = r"{output_csv}"
formula = r"{formula}"

df = pd.read_csv(input_csv)
model = smf.ols(formula=formula, data=df).fit()
coef = float(model.params.get("treatment", 0.0))
pval = float(model.pvalues.get("treatment", 1.0))

pred = df.copy()
pred["prediction"] = model.predict(df)
pred.to_csv(output_csv, index=False)

result = {{
    "model_formula": formula,
    "r_squared": float(model.rsquared),
    "aic": float(model.aic),
    "findings": [
        {{
            "variable": "treatment",
            "outcome": "outcome",
            "effect_size": coef,
            "p_value": pval
        }}
    ],
    "winning_artifacts_data_path": output_csv
}}

with open(output_json, "w") as f:
    json.dump(result, f, indent=2)

print("EXPERT_BRANCH_COMPLETE")
'''


def _run_branches() -> list[dict]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    engine = ResearchEngine(project_root=REPO_ROOT, hitl_enabled=False)

    worker_results = []
    for branch, formula in BRANCH_SPECS.items():
        branch_dir = OUTPUT_DIR / branch
        branch_dir.mkdir(parents=True, exist_ok=True)
        result_json = branch_dir / f"{branch}_results.json"
        artifact_csv = branch_dir / f"{branch}_artifact.csv"

        result = engine.execute_node(
            node_id=f"examples_expert_{branch}",
            script=_branch_script(formula, result_json, artifact_csv),
            timeout=180,
            input_files=[str(DATA_CSV.relative_to(REPO_ROOT))],
            output_files=[
                str(result_json.relative_to(REPO_ROOT)),
                str(artifact_csv.relative_to(REPO_ROOT)),
            ],
        )

        worker_results.append(
            {
                "id": branch,
                "success": result.get("status") == "success",
                "log_file": "",
            }
        )

    return worker_results


def _run_synthesis(worker_results: list[dict]) -> Path:
    parallel_results = OUTPUT_DIR / "parallel_results.json"
    parallel_results.write_text(json.dumps({"results": worker_results}, indent=2))

    cmd = [
        str(REPO_ROOT / ".venv" / "bin" / "python"),
        str(REPO_ROOT / "src" / "research_copilot" / "utils" / "synthesize_results.py"),
        "--results-file",
        str(parallel_results),
        "--output-dir",
        str(OUTPUT_DIR),
        "--manifest",
        str(OUTPUT_DIR / "manifest.json"),
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
    (OUTPUT_DIR / "synthesis_stdout.log").write_text(completed.stdout)
    (OUTPUT_DIR / "synthesis_stderr.log").write_text(completed.stderr)

    if completed.returncode != 0:
        raise RuntimeError(
            "Synthesis script failed. See logs in outputs/synthesis_stdout.log and outputs/synthesis_stderr.log"
        )

    return parallel_results


def _offline_winner_fallback() -> dict:
    branch_payloads = {}
    for branch in BRANCH_SPECS:
        result_json = OUTPUT_DIR / branch / f"{branch}_results.json"
        with open(result_json) as f:
            branch_payloads[branch] = json.load(f)

    ranked = sorted(
        branch_payloads.items(),
        key=lambda item: (
            item[1]["findings"][0].get("p_value", 1.0),
            -item[1].get("r_squared", 0.0),
        ),
    )
    winner_name, winner_payload = ranked[0]
    winner_path = winner_payload.get("winning_artifacts_data_path", "")

    ledger = ResearchLedger(REPO_ROOT / "03_synthesis" / "state_ledger.json")
    ledger.update(
        winning_branch_name=winner_name,
        winning_artifacts_data_path=str(winner_path),
        main_trunk_artifacts_data_path=str(winner_path),
    )

    return {
        "winning_branch_name": winner_name,
        "winning_artifacts_data_path": str(winner_path),
        "selection_mode": "offline_fallback",
    }


def main() -> int:
    _write_dataset()
    workers = _run_branches()
    _run_synthesis(workers)

    decision = _offline_winner_fallback()
    report = OUTPUT_DIR / "expert_report.md"
    report.write_text(
        "\n".join(
            [
                "# Expert Example Report",
                "",
                "## Workflow",
                "- Generated synthetic policy panel dataset",
                "- Ran three branch models through ResearchEngine",
                "- Synthesized branch outputs",
                "- Updated state ledger trunk data path",
                "",
                "## Winner",
                f"- Branch: {decision['winning_branch_name']}",
                f"- Data path: {decision['winning_artifacts_data_path']}",
                f"- Selection mode: {decision['selection_mode']}",
            ]
        )
        + "\n"
    )

    print("Expert example complete.")
    print(f"Decision: {decision}")
    print(f"Report: {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
