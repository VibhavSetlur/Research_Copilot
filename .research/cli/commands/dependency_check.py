#!/usr/bin/env python3
"""Dynamic Package Management — Dependency Hell Solver CLI command.

Detects uninstalled imports in scripts and auto-resolves dependencies
using uv (preferred) or pip as fallback.
"""

import ast
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone


# Mapping of import names to pip package names
IMPORT_TO_PACKAGE = {
    "pandas": "pandas",
    "numpy": "numpy",
    "scipy": "scipy",
    "sklearn": "scikit-learn",
    "statsmodels": "statsmodels",
    "matplotlib": "matplotlib",
    "seaborn": "seaborn",
    "plotly": "plotly",
    "altair": "altair",
    "bokeh": "bokeh",
    "panel": "panel",
    "holoviews": "holoviews",
    "polars": "polars",
    "pyarrow": "pyarrow",
    "pingouin": "pingouin",
    "lifelines": "lifelines",
    "pymc": "pymc",
    "networkx": "networkx",
    "geopandas": "geopandas",
    "xgboost": "xgboost",
    "lightgbm": "lightgbm",
    "catboost": "catboost",
    "torch": "torch",
    "tensorflow": "tensorflow",
    "transformers": "transformers",
    "habanero": "habanero",
    "semanticscholar": "semanticscholar",
    "metapub": "metapub",
    "diskcache": "diskcache",
    "sqlalchemy": "SQLAlchemy",
    "pydantic": "pydantic",
    "pypandoc": "pypandoc",
    "openpyxl": "openpyxl",
    "xlrd": "xlrd",
    "fastparquet": "fastparquet",
    "zstandard": "zstandard",
    "nest_asyncio": "nest-asyncio",
    "yaml": "PyYAML",
    "dateutil": "python-dateutil",
    "sklearn": "scikit-learn",
    "cv2": "opencv-python",
    "PIL": "Pillow",
    "tqdm": "tqdm",
    "requests": "requests",
    "beautifulsoup4": "beautifulsoup4",
    "bs4": "beautifulsoup4",
    "mcp": "mcp",
}


def _extract_imports(script_path: str) -> list:
    """Extract all import names from a Python script using AST parsing."""
    path = Path(script_path)
    if not path.exists():
        return []

    try:
        source = path.read_text()
        tree = ast.parse(source)
    except SyntaxError:
        return []

    imports = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split(".")[0])

    return sorted(imports)


def _get_installed_packages() -> set:
    """Get set of installed package names."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            packages = json.loads(result.stdout)
            return {p["name"].lower().replace("-", "_") for p in packages}
    except Exception:
        pass

    return set()


def _get_requirements_packages() -> set:
    """Get packages listed in requirements.txt."""
    req_path = Path("environment/requirements.txt")
    if not req_path.exists():
        return set()

    packages = set()
    for line in req_path.read_text().split("\n"):
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("-"):
            # Extract package name (before any version specifier)
            pkg = line.split(">=")[0].split("==")[0].split("<")[0].split(">")[0].split("!")[0].strip()
            if pkg:
                packages.add(pkg.lower().replace("-", "_"))

    return packages


def check_dependencies(script: str, auto_install: bool = False) -> str:
    """Check for uninstalled imports in a script and optionally resolve them.

    Args:
        script: Path to the Python script to check
        auto_install: Whether to automatically install missing dependencies

    Returns:
        Status report
    """
    imports = _extract_imports(script)
    if not imports:
        return f"No imports found in {script}"

    installed = _get_installed_packages()
    requirements = _get_requirements_packages()

    missing = []
    for imp in imports:
        # Skip standard library modules
        if imp in sys.stdlib_module_names:
            continue

        # Check if installed
        imp_normalized = imp.lower().replace("-", "_")
        if imp_normalized not in installed:
            pkg_name = IMPORT_TO_PACKAGE.get(imp, imp)
            missing.append({
                "import_name": imp,
                "package_name": pkg_name,
                "in_requirements": pkg_name.lower().replace("-", "_") in requirements,
            })

    if not missing:
        return f"✅ All imports in {script} are satisfied."

    # Build report
    output = [
        f"🔍 **Dependency Check for {script}**",
        f"",
        f"Found {len(missing)} missing package(s):",
        f"",
    ]

    for m in missing:
        status = "in requirements.txt" if m["in_requirements"] else "NOT in requirements.txt"
        output.append(f"  - `{m['import_name']}` → `{m['package_name']}` ({status})")

    output.append("")

    if auto_install:
        output.append("⚙️ **Installing missing packages...**")
        output.append("")

        # Try uv first, fall back to pip
        packages_to_install = [m["package_name"] for m in missing]

        # Try uv
        try:
            result = subprocess.run(
                ["uv", "pip", "install"] + packages_to_install,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                output.append(f"✅ Installed {len(packages_to_install)} package(s) using `uv`:")
                for pkg in packages_to_install:
                    output.append(f"  - {pkg}")
            else:
                raise Exception(result.stderr)
        except (FileNotFoundError, Exception):
            # Fall back to pip
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install"] + packages_to_install,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                if result.returncode == 0:
                    output.append(f"✅ Installed {len(packages_to_install)} package(s) using `pip`:")
                    for pkg in packages_to_install:
                        output.append(f"  - {pkg}")
                else:
                    output.append(f"❌ Installation failed: {result.stderr}")
            except Exception as e:
                output.append(f"❌ Installation failed: {str(e)}")

        # Update requirements.txt with missing packages
        req_path = Path("environment/requirements.txt")
        packages_not_in_req = [m["package_name"] for m in missing if not m["in_requirements"]]

        if packages_not_in_req:
            output.append("")
            output.append("📝 **Updating requirements.txt...**")
            with open(req_path, "a") as f:
                f.write(f"\n# Auto-added by dependency checker ({datetime.now(timezone.utc).strftime('%Y-%m-%d')})\n")
                for pkg in packages_not_in_req:
                    f.write(f"{pkg}\n")
            output.append(f"Added {len(packages_not_in_req)} package(s) to requirements.txt:")
            for pkg in packages_not_in_req:
                output.append(f"  - {pkg}")

        # Re-run environment check
        env_check = Path(".research/scripts/00_environment_check.py")
        if env_check.exists():
            output.append("")
            output.append("🔄 **Re-running environment check...**")
            try:
                result = subprocess.run(
                    [sys.executable, str(env_check)],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if result.returncode == 0:
                    output.append("✅ Environment check passed")
                else:
                    output.append(f"⚠️ Environment check warnings: {result.stderr[:200]}")
            except Exception as e:
                output.append(f"⚠️ Environment check failed: {str(e)}")
    else:
        output.append("Run with --auto-install to automatically install missing packages.")

    return "\n".join(output)
