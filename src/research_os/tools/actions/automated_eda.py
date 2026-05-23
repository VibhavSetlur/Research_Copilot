import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from research_os.project_ops import _resolve_root


class AutomatedEDA:
    """Automated Exploratory Data Analysis trigger.

    Generates standard EDA reports (missingness, distributions, outliers)
    using pandas without the heavy overhead of ydata-profiling.
    """

    def __init__(self, root: Path = None):
        self.root = root or _resolve_root()

    def run_eda(self, dataset_name: str) -> str:
        """Run standard EDA on a dataset and save figures/reports."""
        raw_path = self.root / "workspace" / "data" / "raw" / dataset_name
        derived_path = self.root / "workspace" / "data" / "derived" / dataset_name

        target_path = raw_path if raw_path.exists() else derived_path
        if not target_path.exists():
            return f"Error: Dataset {dataset_name} not found."

        try:
            if target_path.suffix == ".csv":
                df = pd.read_csv(target_path)
            elif target_path.suffix in [".xlsx", ".xls"]:
                df = pd.read_excel(target_path)
            elif target_path.suffix == ".parquet":
                df = pd.read_parquet(target_path)
            else:
                return f"Error: Unsupported format {target_path.suffix}"

            out_dir = (
                self.root / "workspace" / "figures" / f"{Path(dataset_name).stem}_eda"
            )
            out_dir.mkdir(parents=True, exist_ok=True)

            # Use strict style if available
            style_path = self.root / "workspace" / "figures" / "research_style.mplstyle"
            if style_path.exists():
                plt.style.use(str(style_path))

            report_lines = [f"# Automated EDA Report for {dataset_name}", ""]

            # 1. Missingness
            missing = df.isnull().sum()
            if missing.sum() > 0:
                plt.figure(figsize=(10, 6))
                missing[missing > 0].sort_values(ascending=False).plot(kind="bar")
                plt.title("Missing Values per Column")
                plt.ylabel("Count")
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                plt.savefig(out_dir / "missing_values.png")
                plt.close()
                report_lines.append("## Missing Values")
                report_lines.append(
                    f"Found missing values. Chart saved to `figures/{Path(dataset_name).stem}_eda/missing_values.png`\n"
                )

            # 2. Distributions of numeric columns
            numeric_cols = df.select_dtypes(include=["number"]).columns
            if len(numeric_cols) > 0:
                report_lines.append("## Numeric Distributions")
                for col in numeric_cols[:10]:  # Limit to top 10 to avoid bloat
                    plt.figure(figsize=(8, 5))
                    df[col].hist(bins=30)
                    plt.title(f"Distribution of {col}")
                    plt.xlabel(col)
                    plt.ylabel("Frequency")
                    plt.tight_layout()
                    plt.savefig(out_dir / f"dist_{col}.png")
                    plt.close()
                report_lines.append(
                    f"Histograms generated for {len(numeric_cols[:10])} numeric columns.\n"
                )

            # Compile report
            report_path = (
                self.root
                / "workspace"
                / "data"
                / "derived"
                / f"{Path(dataset_name).stem}_eda_report.md"
            )
            report_path.write_text("\n".join(report_lines))

            return f"EDA completed. Report saved to {report_path.relative_to(self.root)} and figures to {out_dir.relative_to(self.root)}"

        except Exception as e:
            return f"Error during EDA: {str(e)}"
