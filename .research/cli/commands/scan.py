"""Scan commands: scan, format-scan."""
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


def find_project_root():
    p = Path.cwd()
    for _ in range(10):
        if (p / ".research").exists():
            return p
        if p.name == ".research" and (p.parent / "inputs").exists():
            return p.parent
        if p.parent == p:
            break
        p = p.parent
    return None


def load_yaml(path: Path):
    if yaml is None:
        result = {}
        try:
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and ":" in line:
                        key, _, val = line.partition(":")
                        val = val.strip().strip('"').strip("'")
                        result[key.strip()] = val
        except FileNotFoundError:
            return {}
        return result
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except (FileNotFoundError, Exception):
        return {}


def load_json(path: Path):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def load_markdown(path: Path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return ""


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def get_config(root: Path):
    config = load_yaml(root / ".research" / "config.yaml")
    defaults = {
        "default_workflow": "quick_exploratory",
        "intake_path": "inputs/intake.md",
        "data_raw": "inputs/data/raw",
        "context_dir": "inputs/context",
        "papers_dir": "inputs/papers",
        "cache_dir": ".research/cache",
        "cache_research_map": ".research/cache/research_map.json",
        "cache_followups": ".research/cache/follow_up_questions.md",
        "docs_dir": "docs",
        "reports_dir": "reports",
        "research_map": "reports/baseline/research_map.json",
        "follow_up_questions": "reports/baseline/follow_up_questions.md",
        "manifest": "docs/manifest.json",
        "iteration_registry": "docs/iterations/registry.json",
        "research_log": "docs/research_log.md",
        "data_ingested": "data/01_ingested",
        "data_processed": "data/02_processed",
        "data_analytical": "data/03_analytical",
        "dag_json": ".research/workflow_dag.json",
    }
    for k, v in defaults.items():
        config.setdefault(k, v)
    return config


def _load_format_router(root):
    import importlib.util
    router_path = root / ".research" / "scripts" / "utils" / "format_router.py"
    if not router_path.exists():
        return None
    spec = importlib.util.spec_from_file_location("format_router", router_path)
    if not spec or not spec.loader:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cmd_scan(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    config = get_config(root)
    intake = load_markdown(root / config["intake_path"])

    data_dir = root / config["data_raw"]
    data_files = []
    schema_cache = {}
    format_router = _load_format_router(root)
    format_manifest = None
    format_meta_by_path = {}
    manifest_path = root / config.get("cache_dir", ".research/cache") / "data_format_manifest.json"
    if format_router and data_dir.exists():
        try:
            format_manifest = format_router.scan_directory(str(data_dir), str(manifest_path))
            for item in format_manifest.get("files", []):
                format_meta_by_path[Path(item.get("path", "")).resolve()] = item
        except Exception:
            format_manifest = None

    if data_dir.exists():
        for f in data_dir.rglob("*"):
            if f.is_file() and not f.name.startswith("."):
                ext = f.suffix.lower()
                fmt_map = {
                    ".csv": "CSV", ".tsv": "TSV", ".parquet": "Parquet",
                    ".xlsx": "Excel", ".xls": "Excel", ".json": "JSON",
                    ".sav": "SPSS", ".dta": "Stata", ".sas7bdat": "SAS",
                    ".feather": "Feather", ".h5": "HDF5", ".hdf5": "HDF5",
                }
                meta = format_meta_by_path.get(f.resolve())
                file_info = {
                    "path": str(f.relative_to(root)),
                    "format": meta.get("format") if meta else fmt_map.get(ext, ext.lstrip(".").upper()),
                    "size_kb": round(f.stat().st_size / 1024, 1),
                }
                if meta:
                    file_info["pandera_applicable"] = bool(meta.get("pandera_applicable"))
                    file_info["domain_hint"] = meta.get("domain_hint")
                    file_info["parser_available"] = bool(meta.get("parser_available"))

                if ext in (".csv", ".tsv", ".xlsx", ".xls"):
                    try:
                        import pandas as pd
                        if ext == ".csv":
                            df = pd.read_csv(f, nrows=100)
                        elif ext == ".tsv":
                            df = pd.read_csv(f, sep="\t", nrows=100)
                        elif ext in (".xlsx", ".xls"):
                            df = pd.read_excel(f, nrows=100)
                        else:
                            df = None

                        if df is not None:
                            schema = {"columns": {}, "total_rows_estimated": None}
                            for col in df.columns:
                                col_info = {
                                    "dtype": str(df[col].dtype),
                                    "non_null_in_sample": int(df[col].notna().sum()),
                                    "null_in_sample": int(df[col].isna().sum()),
                                    "sample_values": [str(v) for v in df[col].dropna().head(3).tolist()],
                                }
                                if df[col].dtype in ("float64", "float32", "int64", "int32"):
                                    col_info["semantic_type"] = "numeric"
                                    col_info["min"] = float(df[col].min()) if df[col].notna().any() else None
                                    col_info["max"] = float(df[col].max()) if df[col].notna().any() else None
                                elif df[col].dtype == "bool":
                                    col_info["semantic_type"] = "boolean"
                                elif df[col].dtype == "object":
                                    nunique = df[col].nunique()
                                    if nunique <= 10:
                                        col_info["semantic_type"] = "categorical"
                                        col_info["unique_values"] = [str(v) for v in df[col].unique()[:10]]
                                    else:
                                        col_info["semantic_type"] = "text"
                                elif "datetime" in str(df[col].dtype):
                                    col_info["semantic_type"] = "datetime"
                                else:
                                    col_info["semantic_type"] = "unknown"
                                schema["columns"][col] = col_info

                            try:
                                full_df = pd.read_csv(f, nrows=1) if ext == ".csv" else None
                                if full_df is not None:
                                    with open(f, "rb") as fh:
                                        total_lines = sum(1 for _ in fh)
                                    schema["total_rows_estimated"] = total_lines - 1
                            except Exception:
                                pass

                            schema_cache[f.name] = schema
                            file_info["columns"] = list(df.columns)
                            file_info["column_count"] = len(df.columns)
                            file_info["sample_row_count"] = len(df)
                    except ImportError:
                        pass
                    except Exception:
                        pass

                data_files.append(file_info)

    context_dir = root / config["context_dir"]
    context_files = []
    if context_dir.exists():
        for f in context_dir.iterdir():
            if f.is_file() and not f.name.startswith("."):
                context_files.append(str(f.relative_to(root)))

    papers_dir = root / config["papers_dir"]
    paper_count = len(list(papers_dir.glob("*.pdf"))) if papers_dir.exists() else 0

    questions = []
    lines = intake.split("\n")
    current_q = None
    for line in lines:
        if line.startswith("### Question ") or line.startswith("## Question "):
            if current_q:
                questions.append(current_q)
            current_q = {"text": "", "type": "unknown", "hypothesis": "", "outcome": "", "predictor": "", "covariates": "", "files": "", "prep": "", "prior": ""}
            parts = line.split(":", 1)
            if len(parts) > 1:
                current_q["text"] = parts[1].strip()
            continue
        if current_q:
            if line.startswith("### ") and "Question" not in line:
                continue
            if line.startswith("## ") and "Question" not in line:
                break
            stripped = line.strip()
            if stripped.startswith("**Question**"):
                current_q["text"] = stripped.split(":", 1)[-1].strip().strip("[]")
            elif stripped.startswith("**Type**"):
                current_q["type"] = stripped.split(":", 1)[-1].strip().strip("[]")
            elif stripped.startswith("**Hypothesis**"):
                current_q["hypothesis"] = stripped.split(":", 1)[-1].strip().strip("[]")
            elif stripped.startswith("**Outcome variable"):
                current_q["outcome"] = stripped.split(":", 1)[-1].strip().strip("[]")
            elif stripped.startswith("**Predictor variable"):
                current_q["predictor"] = stripped.split(":", 1)[-1].strip().strip("[]")
            elif stripped.startswith("**Covariates"):
                current_q["covariates"] = stripped.split(":", 1)[-1].strip().strip("[]")
            elif stripped.startswith("**Data files"):
                current_q["files"] = stripped.split(":", 1)[-1].strip().strip("[]")
            elif stripped.startswith("**Data prep"):
                current_q["prep"] = stripped.split(":", 1)[-1].strip().strip("[]")
            elif stripped.startswith("**Prior research"):
                current_q["prior"] = stripped.split(":", 1)[-1].strip().strip("[]")
    if current_q and current_q["text"]:
        questions.append(current_q)

    project_title = ""
    domain = ""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("**Title**"):
            project_title = stripped.split(":", 1)[-1].strip().strip("[]")
        elif stripped.startswith("**Field**"):
            domain = stripped.split(":", 1)[-1].strip().strip("[]")

    question_summary = f"{len(questions)} question(s)" if questions else "N/A"

    research_map = {
        "schema_version": "7.0.0",
        "project": {"title": project_title},
        "questions": questions,
        "data": {
            "files": data_files,
            "schema_cache": schema_cache,
            "format_manifest": str(manifest_path.relative_to(root)) if format_manifest else "",
            "format_summary": {
                "tabular_count": format_manifest.get("tabular_count") if format_manifest else 0,
                "non_tabular_count": format_manifest.get("non_tabular_count") if format_manifest else 0,
            },
        },
        "domain": {"name": domain, "reporting_standard": ""},
        "literature": {"user_findings": [], "papers_provided": paper_count},
        "constraints": {"target": "", "timeline": "", "ethics_notes": ""},
        "feasibility": {"verdict": "go" if data_files and questions else "caution", "blockers": []},
        "follow_up": [],
    }

    if not data_files:
        research_map["feasibility"]["verdict"] = "caution"
        research_map["follow_up"].append("No data files found in inputs/data/raw/. Add your data files there.")
    if not questions:
        research_map["feasibility"]["verdict"] = "caution"
        research_map["follow_up"].append("No research questions found in intake. Fill in inputs/intake.md.")

    cache_path = root / config["cache_research_map"]
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w") as f:
        json.dump(research_map, f, indent=2)

    if schema_cache:
        schema_path = root / config.get("cache_dir", ".research/cache") / "schema_cache.json"
        schema_path.parent.mkdir(parents=True, exist_ok=True)
        with open(schema_path, "w") as f:
            json.dump(schema_cache, f, indent=2)

    print("=" * 60)
    print("SCAN COMPLETE")
    print("=" * 60)
    print()
    print(f"  Project: {project_title or 'Untitled'}")
    print(f"  Research questions: {question_summary}")
    for i, q in enumerate(questions[:3]):
        marker = "(Primary)" if "Primary" in q.get("text", "") or i == 0 else ""
        print(f"    Q{i+1}: {q['text'][:80]}{'...' if len(q['text']) > 80 else ''} {marker}")
    if len(questions) > 3:
        print(f"    ... and {len(questions) - 3} more")
    print()
    print(f"  Data files found: {len(data_files)}")
    for df in data_files:
        cols_info = f", {df['column_count']} cols" if "column_count" in df else ""
        print(f"    - {df['path']} ({df['format']}, {df['size_kb']} KB{cols_info})")
        if "columns" in df:
            print(f"      Columns: {', '.join(df['columns'][:10])}{'...' if len(df['columns']) > 10 else ''}")
    print(f"  Context files: {len(context_files)}")
    for cf in context_files:
        print(f"    - {cf}")
    print(f"  Papers (PDF): {paper_count}")
    print()
    if domain:
        print(f"  Domain: {domain}")
        print()
    print(f"  Feasibility: {research_map['feasibility']['verdict']}")
    print()
    print(f"  Research map saved to: {cache_path}")
    if schema_cache:
        print(f"  Schema cache saved: {len(schema_cache)} file(s) sniffed")
    if format_manifest:
        print(f"  Format manifest saved: {manifest_path}")
    print(f"  NOTE: Output directories (docs/, reports/, data/, scripts/) are NOT created.")
    print(f"  The AI agent (research_init) will create them when you run it.")
    print()

    if research_map["follow_up"]:
        print("  Follow-up:")
        for q in research_map["follow_up"]:
            print(f"    - {q}")
        print()


def cmd_format_scan(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    config = get_config(root)
    data_dir = root / config["data_raw"]
    router = _load_format_router(root)
    if not router:
        print("ERROR: format_router not available in .research/scripts/utils.")
        sys.exit(1)

    manifest_path = root / config.get("cache_dir", ".research/cache") / "data_format_manifest.json"
    manifest = router.scan_directory(str(data_dir), str(manifest_path))

    counts = {}
    for item in manifest.get("files", []):
        fmt = item.get("format", "UNKNOWN")
        counts[fmt] = counts.get(fmt, 0) + 1

    print("=" * 60)
    print("FORMAT SCAN")
    print("=" * 60)
    print()
    print(f"  Files scanned: {len(manifest.get('files', []))}")
    print(f"  Tabular: {manifest.get('tabular_count', 0)}")
    print(f"  Non-tabular: {manifest.get('non_tabular_count', 0)}")
    print()
    for fmt, count in sorted(counts.items(), key=lambda x: x[0]):
        print(f"  - {fmt}: {count}")
    print()
    print(f"  Manifest: {manifest_path}")
