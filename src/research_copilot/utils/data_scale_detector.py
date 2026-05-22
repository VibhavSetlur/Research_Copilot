#!/usr/bin/env python3
"""Data Scale Detector — analyzes input data files and recommends processing libraries.

Prevents Out-Of-Memory (OOM) errors by:
1. Scanning all files in 00_inputs/raw_data/
2. Classifying each file by size (small/medium/large/massive)
3. Recommending appropriate processing libraries (pandas vs polars vs pyarrow)
4. Generating code templates for large file processing

Usage:
    python .research/scripts/utils/data_scale_detector.py

    # Programmatic usage:
    from data_scale_detector import DataScaleDetector

    detector = DataScaleDetector()
    profile = detector.scan()
    constraint = detector.get_constraint_message()
    template = detector.get_code_template("large")
"""

import hashlib
import json
from pathlib import Path
from typing import Optional

from research_copilot.utils.common import find_project_root


SIZE_THRESHOLDS = {
    "small_max_mb": 100,
    "medium_max_mb": 1024,
    "large_max_gb": 10,
}

LIBRARY_RECOMMENDATIONS = {
    "small": {
        "primary": "pandas",
        "alternative": "polars (eager)",
        "read_func": "pd.read_csv() / pl.read_csv()",
        "notes": "Standard pandas workflow is fine. Memory usage ~5-10x file size.",
    },
    "medium": {
        "primary": "polars (eager)",
        "alternative": "pandas",
        "read_func": "pl.read_csv() / pl.read_parquet()",
        "notes": "Polars recommended for 2-3x memory efficiency. Monitor if >500MB.",
    },
    "large": {
        "primary": "polars (lazy)",
        "alternative": "pyarrow.dataset",
        "read_func": "pl.scan_csv() / pl.scan_parquet()",
        "notes": "MUST use lazy evaluation. Call .collect() only after all transformations.",
    },
    "massive": {
        "primary": "pyarrow.dataset + chunked",
        "alternative": "polars (lazy) + streaming",
        "read_func": "pyarrow.dataset.dataset() / pl.scan_*().collect(streaming=True)",
        "notes": "Process in chunks. Use pyarrow.dataset for filtering before loading.",
    },
}


class DataScaleDetector:
    """Detects data file sizes and recommends processing strategies."""

    SUPPORTED_EXTENSIONS = {".csv", ".parquet", ".tsv", ".json", ".feather", ".arrow", ".xlsx"}

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = find_project_root()
        self.root = project_root
        self.data_dir = project_root / "00_inputs" / "raw_data"
        self.thresholds = self._load_thresholds()

    def _load_thresholds(self) -> dict:
        config_path = self.root / ".research" / "config.yaml"
        if not config_path.exists():
            return SIZE_THRESHOLDS

        try:
            import yaml
            with open(config_path) as f:
                config = yaml.safe_load(f)
            ts = config.get("data_scale_thresholds", {})
            return {
                "small_max_mb": ts.get("medium_mb", SIZE_THRESHOLDS["small_max_mb"]),
                "medium_max_mb": ts.get("large_gb", SIZE_THRESHOLDS["large_max_gb"]) * 1024,
                "large_max_gb": ts.get("massive_gb", SIZE_THRESHOLDS["large_max_gb"]),
            }
        except Exception:
            return SIZE_THRESHOLDS

    def _classify(self, size_bytes: int) -> str:
        size_mb = size_bytes / (1024 * 1024)
        size_gb = size_bytes / (1024 * 1024 * 1024)

        if size_gb >= self.thresholds["large_max_gb"]:
            return "massive"
        elif size_gb >= 1.0:
            return "large"
        elif size_mb >= self.thresholds["small_max_mb"]:
            return "medium"
        else:
            return "small"

    @staticmethod
    def _compute_hash(file_path: Path) -> str:
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except (FileNotFoundError, PermissionError):
            return "error"

    def scan(self) -> dict:
        """Scan all data files and return a scale profile.

        Returns:
            Dict with file profiles, summary stats, and constraint message.
        """
        if not self.data_dir.exists():
            return {"files": {}, "summary": {"total_files": 0, "has_large_files": False}}

        files = {}
        total_size = 0
        has_large = False

        for f in sorted(self.data_dir.iterdir()):
            if f.is_file() and f.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                size_bytes = f.stat().st_size
                classification = self._classify(size_bytes)
                rel_path = str(f.relative_to(self.root))

                files[rel_path] = {
                    "file_name": f.name,
                    "size_bytes": size_bytes,
                    "size_mb": round(size_bytes / (1024 * 1024), 2),
                    "size_gb": round(size_bytes / (1024 * 1024 * 1024), 4),
                    "classification": classification,
                    "recommended_library": LIBRARY_RECOMMENDATIONS[classification]["primary"],
                    "read_function": LIBRARY_RECOMMENDATIONS[classification]["read_func"],
                    "sha256": self._compute_hash(f),
                    "extension": f.suffix.lower(),
                }

                total_size += size_bytes
                if classification in ("large", "massive"):
                    has_large = True

        summary = {
            "total_files": len(files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "total_size_gb": round(total_size / (1024 * 1024 * 1024), 4),
            "has_large_files": has_large,
            "by_classification": {},
        }

        for profile in files.values():
            cls = profile["classification"]
            summary["by_classification"].setdefault(cls, 0)
            summary["by_classification"][cls] += 1

        return {"files": files, "summary": summary}

    def get_constraint_message(self) -> Optional[str]:
        """Generate a constraint message for large files."""
        profile = self.scan()
        if not profile["summary"]["has_large_files"]:
            return None

        parts = []
        for rel_path, info in profile["files"].items():
            if info["classification"] in ("large", "massive"):
                parts.append(
                    f"FILE {info['file_name']} ({info['size_gb']:.1f}GB): "
                    f"MUST use {info['recommended_library']}. "
                    f"Use {info['read_function']}."
                )

        if not parts:
            return None

        return (
            "DATA SCALE CONSTRAINT ACTIVE:\n"
            + "\n".join(parts)
            + "\n\nENFORCEMENT: Scripts using pandas or eager loading for these files "
            "will be flagged. Use lazy evaluation or chunked processing."
        )

    def get_library_instruction(self, threshold_mb: int = 500) -> Optional[str]:
        """Return one concise instruction for model prompts based on input size.

        If the largest discovered input file is <= threshold_mb, recommend
        pandas. Otherwise enforce polars or dask to prevent memory overflow.
        """
        profile = self.scan()
        files = profile.get("files", {})
        if not files:
            return None

        max_size_mb = max(info.get("size_mb", 0) for info in files.values())
        if max_size_mb <= threshold_mb:
            return "Data handling instruction: Use Pandas for tabular processing."
        return (
            "Data handling instruction: Input size exceeds 500MB. "
            "Use Polars or Dask to prevent memory overflow; avoid full eager Pandas loads."
        )

    def get_code_template(self, classification: str) -> str:
        """Generate a code template for processing files of a given size class.

        Args:
            classification: 'small', 'medium', 'large', or 'massive'

        Returns:
            Python code template string
        """
        templates = {
            "small": '''# Small file (<100MB) — pandas is fine
import pandas as pd

df = pd.read_csv("00_inputs/raw_data/data.csv")
# ... your analysis ...
''',
            "medium": '''# Medium file (100MB-1GB) — polars recommended
import polars as pl

df = pl.read_csv("00_inputs/raw_data/data.csv")
# ... your analysis ...
# df.collect() not needed for eager mode
''',
            "large": '''# Large file (1GB-10GB) — polars lazy frames REQUIRED
import polars as pl

# Use scan_* for lazy evaluation — NO data loaded yet
lf = pl.scan_csv("00_inputs/raw_data/data.csv")

# Chain all transformations lazily
result = (
    lf
    .filter(pl.col("value") > 0)
    .select(["id", "value", "category"])
    .group_by("category")
    .agg([pl.col("value").mean(), pl.col("value").count()])
)

# Collect ONLY after all transformations
df = result.collect()
''',
            "massive": '''# Massive file (>10GB) — pyarrow.dataset + chunked processing REQUIRED
import pyarrow.dataset as ds
import pyarrow.compute as pc

# Create dataset — NO data loaded yet
dataset = ds.dataset("00_inputs/raw_data/data.csv", format="csv")

# Filter at the dataset level (pushed down to disk)
filtered = dataset.filter(ds.field("value") > 0)

# Process in chunks to avoid OOM
batch_size = 100_000
results = []

for batch in filtered.to_batches(batch_size=batch_size):
    df = batch.to_pandas()
    # Process each chunk
    chunk_result = df.groupby("category")["value"].mean()
    results.append(chunk_result)

# Combine results
import pandas as pd
final = pd.concat(results)
''',
        }
        return templates.get(classification, "# Unknown classification")

    def save_profile(self, output_path: Optional[Path] = None) -> Path:
        """Save the data scale profile to a JSON file.

        Args:
            output_path: Where to save (default: .research/cache/data_scale_profile.json)

        Returns:
            Path to the saved profile
        """
        if output_path is None:
            output_path = self.root / ".research" / "cache" / "data_scale_profile.json"

        profile = self.scan()
        profile["constraint_message"] = self.get_constraint_message()
        profile["code_templates"] = {
            cls: self.get_code_template(cls)
            for cls in LIBRARY_RECOMMENDATIONS
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(profile, f, indent=2, default=str)

        return output_path


def main():
    detector = DataScaleDetector()
    profile = detector.scan()

    print("=" * 60)
    print("DATA SCALE ANALYSIS")
    print("=" * 60)

    summary = profile["summary"]
    print(f"\nTotal files: {summary['total_files']}")
    print(f"Total size: {summary['total_size_gb']:.2f} GB")
    print(f"Has large files: {summary['has_large_files']}")

    if summary["by_classification"]:
        print("\nBy classification:")
        for cls, count in sorted(summary["by_classification"].items()):
            print(f"  {cls}: {count} file(s)")

    print("\n" + "-" * 60)
    print("FILE DETAILS")
    print("-" * 60)

    for rel_path, info in sorted(profile["files"].items()):
        marker = "!!!" if info["classification"] in ("large", "massive") else "   "
        print(f"{marker} {info['file_name']}")
        print(f"    Size: {info['size_gb']:.2f} GB | Class: {info['classification']}")
        print(f"    Library: {info['recommended_library']}")
        print(f"    Read: {info['read_function']}")
        print()

    constraint = detector.get_constraint_message()
    if constraint:
        print("=" * 60)
        print("CONSTRAINT MESSAGE")
        print("=" * 60)
        print(constraint)

    output_path = detector.save_profile()
    print(f"\nProfile saved to: {output_path}")


if __name__ == "__main__":
    main()
