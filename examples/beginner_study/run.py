#!/usr/bin/env python3
"""Beginner end-to-end example for Research Copilot."""

from __future__ import annotations

import json
from pathlib import Path

from research_copilot.engine import ResearchEngine
from research_copilot.utils.cache_manager import ingest_file


REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_ROOT = Path(__file__).resolve().parent
INPUT_CSV = EXAMPLE_ROOT / "input" / "sleep_quality.csv"
OUTPUT_DIR = EXAMPLE_ROOT / "outputs"


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    summary_json = OUTPUT_DIR / "summary.json"
    means_csv = OUTPUT_DIR / "group_means.csv"
    figure_png = OUTPUT_DIR / "sleep_score_by_group.png"

    script = f'''
import json
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

input_csv = r"{INPUT_CSV}"
summary_json = r"{summary_json}"
means_csv = r"{means_csv}"
figure_png = r"{figure_png}"

df = pd.read_csv(input_csv)
control = df[df["group"] == "control"]["sleep_score"]
treatment = df[df["group"] == "treatment"]["sleep_score"]

# Welch t-test for unequal variances
t_stat, p_value = stats.ttest_ind(treatment, control, equal_var=False)

mean_control = float(control.mean())
mean_treatment = float(treatment.mean())
mean_diff = mean_treatment - mean_control

pooled_sd = ((control.std(ddof=1) ** 2 + treatment.std(ddof=1) ** 2) / 2) ** 0.5
cohen_d = float(mean_diff / pooled_sd)

summary = {{
    "n_control": int(control.shape[0]),
    "n_treatment": int(treatment.shape[0]),
    "mean_control": mean_control,
    "mean_treatment": mean_treatment,
    "mean_difference": mean_diff,
    "t_statistic": float(t_stat),
    "p_value": float(p_value),
    "cohen_d": cohen_d
}}

with open(summary_json, "w") as f:
    json.dump(summary, f, indent=2)

(
    df.groupby("group", as_index=False)["sleep_score"]
      .mean()
      .rename(columns={{"sleep_score": "mean_sleep_score"}})
      .to_csv(means_csv, index=False)
)

plt.figure(figsize=(6, 4))
(
    df.groupby("group")["sleep_score"]
      .mean()
      .reindex(["control", "treatment"])
      .plot(kind="bar", color=["#7a9e9f", "#2f6f85"])
)
plt.title("Average Sleep Score by Group")
plt.ylabel("Sleep Score")
plt.tight_layout()
plt.savefig(figure_png, dpi=150)

print("BEGINNER_ANALYSIS_COMPLETE")
'''

    engine = ResearchEngine(project_root=REPO_ROOT, hitl_enabled=False)
    result = engine.execute_node(
        node_id="examples_beginner_sleep_analysis",
        script=script,
        timeout=120,
        input_files=[str(INPUT_CSV.relative_to(REPO_ROOT))],
        output_files=[
            str(summary_json.relative_to(REPO_ROOT)),
            str(means_csv.relative_to(REPO_ROOT)),
            str(figure_png.relative_to(REPO_ROOT)),
        ],
    )

    if result.get("status") != "success":
        raise RuntimeError(f"Beginner analysis failed: {result}")

    # Demonstrate CSV profile-only embedding behavior.
    vss_db = OUTPUT_DIR / "vss.sqlite"
    ingest_file(INPUT_CSV, vss_db)

    with open(summary_json) as f:
        summary = json.load(f)

    report_md = OUTPUT_DIR / "report.md"
    report_md.write_text(
        "\n".join(
            [
                "# Beginner Example Report",
                "",
                "## Study Question",
                "Does the sleep intervention improve average sleep score?",
                "",
                "## Key Results",
                f"- Control mean: {summary['mean_control']:.2f}",
                f"- Treatment mean: {summary['mean_treatment']:.2f}",
                f"- Mean difference: {summary['mean_difference']:.2f}",
                f"- Welch t-statistic: {summary['t_statistic']:.3f}",
                f"- p-value: {summary['p_value']:.6f}",
                f"- Cohen's d: {summary['cohen_d']:.3f}",
            ]
        )
        + "\n"
    )

    print("Beginner example complete.")
    print(f"Summary: {summary_json}")
    print(f"Report: {report_md}")
    print(f"Vector DB: {vss_db}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
