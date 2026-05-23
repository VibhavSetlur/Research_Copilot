import pandas as pd
from pathlib import Path
from typing import Dict, Any
from research_os.project_ops import _resolve_root


class DataPeekProtocol:
    """The Peek Protocol for Data Exploration.

    Forces the agent to look at the shape, columns, missingness, and a few
    rows of the data before blindly writing analysis code.
    """

    def __init__(self, root: Path = None):
        self.root = root or _resolve_root()

    def peek(self, dataset_name: str) -> Dict[str, Any]:
        """Runs df.info, df.describe, and df.head to give a context injection.

        Args:
            dataset_name: Name of the dataset file (assumed to be in workspace/data/raw or derived)

        Returns:
            Dictionary containing schema, shape, describe, and head representations.
        """
        # Look in both raw and derived
        raw_path = self.root / "workspace" / "data" / "raw" / dataset_name
        derived_path = self.root / "workspace" / "data" / "derived" / dataset_name

        target_path = raw_path if raw_path.exists() else derived_path
        if not target_path.exists():
            return {"error": f"Dataset {dataset_name} not found in data directories."}

        try:
            if target_path.suffix == ".csv":
                df = pd.read_csv(target_path)
            elif target_path.suffix in [".xlsx", ".xls"]:
                df = pd.read_excel(target_path)
            elif target_path.suffix == ".parquet":
                df = pd.read_parquet(target_path)
            else:
                return {"error": f"Unsupported format for Peek: {target_path.suffix}"}

            # Buffer info to string
            import io

            buf = io.StringIO()
            df.info(buf=buf)
            info_str = buf.getvalue()

            return {
                "dataset_name": dataset_name,
                "shape": df.shape,
                "columns": list(df.columns),
                "info": info_str,
                "describe": df.describe(include="all").to_string(),
                "head": df.head(3).to_string(),
                "missing_values": df.isnull().sum().to_dict(),
            }
        except Exception as e:
            return {"error": f"Failed to peek at dataset: {str(e)}"}
