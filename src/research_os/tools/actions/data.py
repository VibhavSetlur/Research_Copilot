import logging
from typing import Dict, Any
from pathlib import Path
import pandas as pd

logger = logging.getLogger("research.tools.data")


def data_sample(
    filepath: str, n_rows: int, strategy: str, root: Path
) -> Dict[str, Any]:
    try:
        data_path = root / filepath
        if not data_path.exists():
            return {"error": f"File not found: {filepath}"}

        ext = data_path.suffix.lower()
        if ext == ".csv":
            df = pd.read_csv(data_path)
        elif ext == ".parquet":
            df = pd.read_parquet(data_path)
        else:
            return {"error": f"Unsupported file format: {ext}"}

        if strategy == "head":
            sampled = df.head(n_rows)
        elif strategy == "random":
            sampled = df.sample(n=min(n_rows, len(df)), random_state=42)
        else:
            return {"error": f"Unknown strategy: {strategy}"}

        out_path = root / f"workspace/data/derived/sampled_{data_path.name}"
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if ext == ".csv":
            sampled.to_csv(out_path, index=False)
        else:
            sampled.to_parquet(out_path, index=False)

        return {
            "status": "success",
            "filepath": str(out_path.absolute()),
            "rows": len(sampled),
        }
    except Exception as e:
        logger.error(f"Data sample failed: {e}")
        return {"status": "error", "message": str(e)}

def data_convert(filepath: str, output_format: str, root: Path) -> Dict[str, Any]:
    try:
        p = root / filepath
        if not p.exists() or not p.is_file():
            return {"status": "error", "message": f"File not found: {filepath}"}
            
        ext = p.suffix.lower()
        output_format = output_format.lower()
        if output_format.startswith("."):
            output_format = output_format[1:]
            
        out_path = p.with_suffix(f".{output_format}")
        
        # Load data
        if ext == ".csv":
            df = pd.read_csv(p)
        elif ext == ".parquet":
            df = pd.read_parquet(p)
        elif ext == ".feather":
            df = pd.read_feather(p)
        elif ext == ".rds":
            try:
                import pyreadr
                result = pyreadr.read_r(str(p))
                df = next(iter(result.values())) # get first dataframe
            except ImportError:
                return {"status": "error", "message": "pyreadr package is required to read .rds files."}
        else:
            return {"status": "error", "message": f"Unsupported input format: {ext}"}
            
        # Save data
        if output_format == "csv":
            df.to_csv(out_path, index=False)
        elif output_format == "parquet":
            df.to_parquet(out_path, index=False)
        elif output_format == "feather":
            df.to_feather(out_path)
        elif output_format == "rds":
            try:
                import pyreadr
                pyreadr.write_rds(str(out_path), df)
            except ImportError:
                return {"status": "error", "message": "pyreadr package is required to write .rds files."}
        else:
            return {"status": "error", "message": f"Unsupported output format: {output_format}"}
            
        return {
            "status": "success",
            "message": f"Converted to {output_format}",
            "filepath": str(out_path.relative_to(root))
        }
    except Exception as e:
        logger.error(f"Data conversion failed: {e}")
        return {"status": "error", "message": str(e)}
