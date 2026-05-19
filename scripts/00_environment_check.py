#!/usr/bin/env python3
"""Environment check — verify all dependencies are installed and versions are compatible.

Run this BEFORE any analysis to ensure reproducibility.
Usage: python scripts/00_environment_check.py
"""

import sys
import importlib
from pathlib import Path


REQUIRED_PACKAGES = {
    "yaml": {"import": "yaml", "min": "6.0", "label": "PyYAML"},
    "pandas": {"import": "pandas", "min": "2.2", "label": "pandas"},
    "numpy": {"import": "numpy", "min": "1.26", "label": "NumPy"},
    "scipy": {"import": "scipy", "min": "1.12", "label": "SciPy"},
    "matplotlib": {"import": "matplotlib", "min": "3.8", "label": "Matplotlib"},
    "seaborn": {"import": "seaborn", "min": "0.13", "label": "Seaborn"},
    "plotly": {"import": "plotly", "min": "5.20", "label": "Plotly"},
    "sklearn": {"import": "sklearn", "min": "1.4", "label": "scikit-learn"},
    "statsmodels": {"import": "statsmodels", "min": "0.14", "label": "statsmodels"},
}

OPTIONAL_PACKAGES = {
    "dash": {"import": "dash", "label": "Dash (dashboards)"},
    "dash_bootstrap_components": {"import": "dash_bootstrap_components", "label": "Dash Bootstrap (dashboards)"},
    "missingno": {"import": "missingno", "label": "missingno (missingness viz)"},
    "networkx": {"import": "networkx", "label": "NetworkX (DAGs)"},
    "openpyxl": {"import": "openpyxl", "label": "openpyxl (Excel)"},
    "polars": {"import": "polars", "label": "Polars (fast data)"},
    "pingouin": {"import": "pingouin", "label": "Pingouin (stats)"},
}


def check_package(pkg_name, pkg_info):
    """Check if a package is installed and meets minimum version."""
    import_name = pkg_info.get("import", pkg_name)
    label = pkg_info.get("label", pkg_name)
    min_version = pkg_info.get("min")

    try:
        mod = importlib.import_module(import_name)
        version = getattr(mod, "__version__", "unknown")

        if min_version and version != "unknown":
            ver_parts = [int(x) for x in version.split(".")[:2]]
            min_parts = [int(x) for x in min_version.split(".")[:2]]
            if ver_parts < min_parts:
                return False, f"{label} {version} installed (need >= {min_version})"

        return True, f"{label} {version}"
    except ImportError:
        return False, f"{label} NOT installed"


def main():
    print("=" * 60)
    print("ENVIRONMENT CHECK")
    print("=" * 60)
    print()

    print(f"  Python: {sys.version}")
    print(f"  Path: {sys.executable}")
    print()

    print("  Required packages:")
    all_required_ok = True
    for pkg_name, pkg_info in REQUIRED_PACKAGES.items():
        ok, msg = check_package(pkg_name, pkg_info)
        marker = "✓" if ok else "✗"
        print(f"    {marker} {msg}")
        if not ok:
            all_required_ok = False
    print()

    print("  Optional packages:")
    for pkg_name, pkg_info in OPTIONAL_PACKAGES.items():
        ok, msg = check_package(pkg_name, pkg_info)
        marker = "✓" if ok else "○"
        print(f"    {marker} {msg}")
    print()

    print("  Project structure:")
    root = Path(__file__).parent.parent
    checks = [
        (".research/", (root / ".research").exists()),
        ("inputs/", (root / "inputs").exists()),
        ("inputs/intake.md", (root / "inputs/intake.md").exists()),
        ("inputs/data/raw/", (root / "inputs/data/raw").exists()),
        ("requirements.txt", (root / "requirements.txt").exists()),
    ]
    for name, exists in checks:
        marker = "✓" if exists else "✗"
        print(f"    {marker} {name}")
    print()

    if all_required_ok:
        print("  Status: PASS — All required packages installed")
        print("  Next: Run 'python .research/research.py scan'")
    else:
        print("  Status: FAIL — Missing required packages")
        print("  Fix: pip install -r requirements.txt")

    print()

    return 0 if all_required_ok else 1


if __name__ == "__main__":
    sys.exit(main())
