#!/usr/bin/env python3
"""
Research Copilot Control Panel — Comprehensive live tracking dashboard.

Features:
- Live state tracking (ledger, token budget, checkpoints)
- File explorer with visual rendering and search/filter
- Data preview (CSV/JSON/Parquet) with column filtering
- Figure/image gallery with validation status
- Methods log and agent activity viewer
- Research map and manifest viewer
- Approval gate system with feedback
- Full-text search across project files
- Abstract/literature viewer

Usage:
    research dashboard
    python .research/scripts/research_dashboard.py
"""

import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import panel as pn

# ── Panel Extension ──────────────────────────────────────────────────────
pn.extension(
    "tabulator",
    "filedownload",
    design="fast",
    template="fast",
    sizing_mode="stretch_width",
)

# ── Project Root Discovery ───────────────────────────────────────────────
def find_project_root() -> Path:
    curr = Path(__file__).resolve().parent
    for parent in [curr] + list(curr.parents):
        if (parent / ".research").exists():
            return parent
    return None

PROJECT_ROOT = find_project_root()
if not PROJECT_ROOT:
    print("ERROR: Could not find project root containing .research/ directory.", file=sys.stderr)
    sys.exit(1)

CACHE_DIR = PROJECT_ROOT / ".research" / "cache"
STATE_PATH = CACHE_DIR / "state.json"
RESEARCH_MAP_PATH = PROJECT_ROOT / ".research" / "cache" / "research_map.json"
RESEARCH_LOG_PATH = PROJECT_ROOT / "docs" / "research_log.md"
METHODS_LOG_PATH = PROJECT_ROOT / "reports" / "logs" / "methods_log.md"
PENDING_APPROVAL_PATH = CACHE_DIR / "pending_approval.json"
APPROVAL_RESPONSE_PATH = CACHE_DIR / "approval_response.json"
CHECKPOINT_DIR = CACHE_DIR / "checkpoints"
SKILL_INDEX_PATH = CACHE_DIR / "skill_index.json"

# ── State Variables ──────────────────────────────────────────────────────
_last_state = None
_last_log_mtime = 0
_last_methods_mtime = 0
_last_checkpoints = []
_current_pending_phase = None
_file_cache = {}

# ── Utility Functions ────────────────────────────────────────────────────
def load_json_safe(path: Path) -> Optional[dict]:
    try:
        if path.exists():
            with open(path) as f:
                return json.load(f)
    except (json.JSONDecodeError, OSError):
        pass
    return None

def load_text_safe(path: Path) -> str:
    try:
        if path.exists():
            return path.read_text()
    except OSError:
        pass
    return ""

def get_file_tree(base_dir: Path, max_depth: int = 4) -> list[dict]:
    """Build a file tree structure."""
    tree = []
    if not base_dir.exists():
        return tree
    for item in sorted(base_dir.iterdir()):
        if item.name.startswith(".") or item.name == "__pycache__":
            continue
        rel = item.relative_to(PROJECT_ROOT)
        node = {"name": item.name, "path": str(rel), "type": "directory" if item.is_dir() else "file"}
        if item.is_file():
            node["size"] = item.stat().st_size
            node["modified"] = datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            node["ext"] = item.suffix.lower()
        else:
            depth = len(rel.parts)
            if depth < max_depth:
                node["children"] = get_file_tree(item, max_depth)
            else:
                node["children"] = []
        tree.append(node)
    return tree

def flatten_tree(tree: list[dict], prefix: str = "") -> list[dict]:
    """Flatten a file tree into a list of files."""
    files = []
    for node in tree:
        full_path = f"{prefix}/{node['name']}" if prefix else node["name"]
        if node["type"] == "file":
            files.append({"name": node["name"], "path": full_path, "size": node.get("size", 0), "ext": node.get("ext", ""), "modified": node.get("modified", "")})
        elif node.get("children"):
            files.extend(flatten_tree(node["children"], full_path))
    return files

def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def get_latest_figures(limit: int = 12) -> list[dict]:
    fig_dir = PROJECT_ROOT / "reports" / "figures"
    if not fig_dir.exists():
        return []
    png_files = sorted(fig_dir.rglob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
    return [{"path": str(f.relative_to(PROJECT_ROOT)), "name": f.name, "size": f.stat().st_size, "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")} for f in png_files]

def get_checkpoints() -> list[dict]:
    if not CHECKPOINT_DIR.exists():
        return []
    cps = []
    for f in sorted(CHECKPOINT_DIR.glob("*.json")):
        data = load_json_safe(f)
        if data:
            cps.append({"phase": data.get("phase", f.stem), "timestamp": data.get("timestamp", ""), "metadata": json.dumps(data.get("metadata", {}))[:100]})
    return cps

def search_files(query: str, max_results: int = 50) -> list[dict]:
    """Search for files by name."""
    results = []
    for ext in ("*.py", "*.md", "*.json", "*.yaml", "*.csv", "*.parquet", "*.png", "*.txt", "*.bib", "*.R"):
        for f in PROJECT_ROOT.rglob(ext):
            if f.name.startswith(".") or "__pycache__" in str(f):
                continue
            if query.lower() in f.name.lower() or query.lower() in str(f.relative_to(PROJECT_ROOT)).lower():
                rel = f.relative_to(PROJECT_ROOT)
                results.append({"name": f.name, "path": str(rel), "size": format_size(f.stat().st_size), "type": "file"})
                if len(results) >= max_results:
                    return results
    return results

def search_content(query: str, max_results: int = 20) -> list[dict]:
    """Search file contents for a query string."""
    results = []
    text_exts = (".py", ".md", ".json", ".yaml", ".txt", ".R", ".bib", ".csv", ".tsv")
    for ext in text_exts:
        for f in PROJECT_ROOT.rglob(f"*{ext}"):
            if f.name.startswith(".") or "__pycache__" in str(f) or f.stat().st_size > 1024 * 1024:
                continue
            try:
                content = f.read_text()
                if query.lower() in content.lower():
                    lines = content.split("\n")
                    matching_lines = []
                    for i, line in enumerate(lines, 1):
                        if query.lower() in line.lower():
                            matching_lines.append({"line": i, "text": line.strip()[:200]})
                            if len(matching_lines) >= 3:
                                break
                    rel = f.relative_to(PROJECT_ROOT)
                    results.append({"name": f.name, "path": str(rel), "matches": len(matching_lines), "snippets": matching_lines})
                    if len(results) >= max_results:
                        return results
            except (OSError, UnicodeDecodeError):
                continue
    return results

def get_data_preview(file_path: Path, max_rows: int = 100) -> Optional[dict]:
    """Preview a data file (CSV, JSON, Parquet)."""
    if not file_path.exists():
        return None
    ext = file_path.suffix.lower()
    try:
        if ext == ".csv":
            import pandas as pd
            df = pd.read_csv(file_path, nrows=max_rows)
            return {"type": "csv", "columns": list(df.columns), "rows": len(df), "data": df.to_dict(orient="records"), "dtypes": {c: str(df[c].dtype) for c in df.columns}}
        elif ext == ".parquet":
            import pandas as pd
            df = pd.read_parquet(file_path)
            df = df.head(max_rows)
            return {"type": "parquet", "columns": list(df.columns), "rows": len(df), "data": df.to_dict(orient="records"), "dtypes": {c: str(df[c].dtype) for c in df.columns}}
        elif ext == ".json":
            with open(file_path) as f:
                data = json.load(f)
            if isinstance(data, list):
                return {"type": "json", "columns": list(data[0].keys()) if data else [], "rows": len(data), "data": data[:max_rows]}
            elif isinstance(data, dict):
                return {"type": "json", "columns": ["key", "value"], "rows": len(data), "data": [{"key": k, "value": str(v)[:200]} for k, v in data.items()]}
    except Exception:
        pass
    return None

def get_literature_abstracts() -> list[dict]:
    """Get literature corpus abstracts."""
    corpus_path = PROJECT_ROOT / "reports" / "literature" / "literature_corpus.json"
    corpus = load_json_safe(corpus_path)
    if not corpus:
        return []
    papers = corpus.get("papers", []) if isinstance(corpus, dict) else corpus
    abstracts = []
    for p in papers[:50]:
        abstracts.append({
            "title": p.get("title", "Untitled"),
            "authors": ", ".join(p.get("authors", p.get("author", [])) if isinstance(p.get("authors", p.get("author", [])), list) else [str(p.get("authors", p.get("author", "")))]),
            "year": p.get("year", ""),
            "doi": p.get("doi", ""),
            "abstract": (p.get("abstract", "") or "")[:500],
            "claims": len(p.get("claims", [])),
        })
    return abstracts

def get_methods_log() -> str:
    return load_text_safe(METHODS_LOG_PATH)

def get_research_log() -> str:
    return load_text_safe(RESEARCH_LOG_PATH)

def get_research_map() -> Optional[dict]:
    return load_json_safe(RESEARCH_MAP_PATH)

def get_manifest() -> Optional[dict]:
    return load_json_safe(PROJECT_ROOT / "docs" / "manifest.json")

def get_iteration_registry() -> Optional[dict]:
    return load_json_safe(PROJECT_ROOT / "docs" / "iterations" / "registry.json")

def get_dead_ends() -> list[dict]:
    dead_dir = PROJECT_ROOT / "docs" / "dead_ends"
    if not dead_dir.exists():
        return []
    entries = []
    for f in sorted(dead_dir.glob("*.md")):
        content = f.read_text()
        title = content.split("\n")[0].replace("# ", "") if content else f.name
        entries.append({"name": f.name, "title": title, "path": str(f.relative_to(PROJECT_ROOT)), "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")})
    return entries

def get_decisions() -> list[dict]:
    dec_dir = PROJECT_ROOT / "docs" / "decisions"
    if not dec_dir.exists():
        return []
    entries = []
    for f in sorted(dec_dir.glob("*.md")):
        content = f.read_text()
        title = content.split("\n")[0].replace("# ", "") if content else f.name
        entries.append({"name": f.name, "title": title, "path": str(f.relative_to(PROJECT_ROOT)), "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")})
    return entries

def get_analysis_plans() -> list[dict]:
    plan_path = PROJECT_ROOT / "reports" / "analysis" / "analysis_plan.md"
    if not plan_path.exists():
        return []
    return [{"name": "analysis_plan.md", "path": str(plan_path.relative_to(PROJECT_ROOT)), "content": load_text_safe(plan_path)}]

def get_scout_reports() -> list[dict]:
    scout_path = PROJECT_ROOT / "reports" / "analysis" / "methodology_scout_report.md"
    if not scout_path.exists():
        return []
    return [{"name": "methodology_scout_report.md", "path": str(scout_path.relative_to(PROJECT_ROOT)), "content": load_text_safe(scout_path)}]

def get_replication_reports() -> list[dict]:
    rep_path = PROJECT_ROOT / "reports" / "analysis" / "replication_validation_report.md"
    if not rep_path.exists():
        return []
    return [{"name": "replication_validation_report.md", "path": str(rep_path.relative_to(PROJECT_ROOT)), "content": load_text_safe(rep_path)}]

def get_citation_report() -> Optional[dict]:
    return load_json_safe(PROJECT_ROOT / "reports" / "literature" / "citation_verification_report.json")

def get_claim_trace_report() -> Optional[dict]:
    return load_json_safe(PROJECT_ROOT / "reports" / "audit" / "claim_trace_report.json")

# ── UI Components ────────────────────────────────────────────────────────

# === TAB 1: OVERVIEW ===
def build_overview_tab():
    state_data = load_json_safe(STATE_PATH) or {}
    budget = state_data.get("token_budget", {"used": 0, "remaining": 200000, "limit": 200000})
    used = budget.get("used", 0)
    limit = budget.get("limit", 200000)
    pct = int((used / limit) * 100) if limit > 0 else 0

    phase = state_data.get("phase", "N/A")
    run_id = state_data.get("run_id", "N/A")
    checkpoints = state_data.get("checkpoints", {})
    completed = sum(1 for v in checkpoints.values() if v == "complete")
    total = len(checkpoints)

    overview_cards = pn.Column(
        pn.pane.Markdown(f"### Phase: `{phase}`", margin=(0, 0, 5, 0)),
        pn.pane.Markdown(f"**Run ID:** `{run_id[:8]}...`", margin=(0, 0, 5, 0)),
        pn.pane.Markdown(f"**Checkpoints:** {completed}/{total} complete", margin=(0, 0, 5, 0)),
        pn.pane.Markdown(f"**Hypotheses:** {len(state_data.get('active_hypotheses', []))}", margin=(0, 0, 5, 0)),
        pn.pane.Markdown(f"**Dead Ends:** {len(state_data.get('dead_ends', []))}", margin=(0, 0, 5, 0)),
        pn.pane.Markdown(f"**Errors:** {len(state_data.get('errors', []))}", margin=(0, 0, 5, 0)),
        sizing_mode="stretch_width",
    )

    token_bar = pn.widgets.Progress(name="Token Budget", value=pct, max=100, bar_color="danger" if pct > 80 else "warning" if pct > 60 else "success")
    token_text = pn.pane.Markdown(f"**{used:,} / {limit:,} tokens** ({pct}%)")

    # Pipeline status
    pipeline_phases = ["research_init", "literature_deep", "method_route", "data_scaffold", "execute_analysis", "compile_outputs", "audit_validate"]
    pipeline_items = []
    for p in pipeline_phases:
        status = checkpoints.get(p, "pending")
        icon = {"complete": "✅", "in_progress": "🔄", "restored": "🔄", "pending": "⬜"}.get(status, "⬜")
        pipeline_items.append(pn.pane.Markdown(f"{icon} **{p}** — {status}", margin=(2, 0, 2, 10)))

    pipeline_status = pn.Column(
        pn.pane.Markdown("### Pipeline Status", margin=(0, 0, 10, 0)),
        *pipeline_items,
        sizing_mode="stretch_width",
    )

    # Recent activity
    log_content = get_research_log()
    recent_lines = log_content.split("\n")[-20:] if log_content else ["No activity log yet."]
    activity_log = pn.widgets.TextAreaInput(value="\n".join(recent_lines), height=300, disabled=True, sizing_mode="stretch_width")

    return pn.Column(
        pn.Row(overview_cards, pn.Column(token_text, token_bar, sizing_mode="stretch_width"), sizing_mode="stretch_width"),
        pn.layout.Divider(),
        pn.Row(pipeline_status, sizing_mode="stretch_width"),
        pn.layout.Divider(),
        pn.pane.Markdown("### Recent Activity", margin=(10, 0, 5, 0)),
        activity_log,
        sizing_mode="stretch_width",
    )

# === TAB 2: FILE EXPLORER ===
def build_file_explorer_tab():
    tree = get_file_tree(PROJECT_ROOT)
    files = flatten_tree(tree)

    file_df = pn.widgets.Tabulator(
        value=files,
        pagination="remote",
        page_size=25,
        sizing_mode="stretch_both",
        configuration={
            "headerFilter": True,
            "initialSort": [{"column": "name", "dir": "asc"}],
        },
        columns=[
            {"field": "name", "title": "Name", "width": 250},
            {"field": "path", "title": "Path", "width": 400},
            {"field": "ext", "title": "Type", "width": 80},
            {"field": "size", "title": "Size", "width": 100, "formatter": "number"},
            {"field": "modified", "title": "Modified", "width": 150},
        ],
    )

    # File content viewer
    file_content = pn.widgets.TextAreaInput(value="Select a file to view its contents...", height=400, disabled=True, sizing_mode="stretch_width")

    def on_file_select(event):
        if event.value and len(event.value) > 0:
            idx = event.value[0]
            if idx < len(files):
                file_path = PROJECT_ROOT / files[idx]["path"]
                if file_path.exists():
                    ext = file_path.suffix.lower()
                    try:
                        if ext in (".png", ".jpg", ".jpeg", ".gif"):
                            file_content.value = f"[Image file: {file_path.name} — use Gallery tab to view]"
                        elif ext in (".csv", ".parquet"):
                            file_content.value = f"[Data file: {file_path.name} — use Data Viewer tab to preview]"
                        elif ext == ".json":
                            data = load_json_safe(file_path)
                            file_content.value = json.dumps(data, indent=2)[:5000] if data else "Empty or invalid JSON"
                        else:
                            file_content.value = file_path.read_text()[:5000]
                    except Exception as e:
                        file_content.value = f"Error reading file: {e}"

    file_df.on_click(on_file_select)

    return pn.Column(
        pn.pane.Markdown("### File Explorer", margin=(0, 0, 10, 0)),
        pn.pane.Markdown("Click a file to preview its contents (text/JSON). For images use Gallery tab, for data use Data Viewer tab.", margin=(0, 0, 10, 0)),
        file_df,
        pn.layout.Divider(),
        pn.pane.Markdown("### File Preview", margin=(10, 0, 5, 0)),
        file_content,
        sizing_mode="stretch_both",
    )

# === TAB 3: DATA VIEWER ===
def build_data_viewer_tab():
    data_dirs = [
        PROJECT_ROOT / "inputs" / "data" / "raw",
        PROJECT_ROOT / "data" / "01_ingested",
        PROJECT_ROOT / "data" / "02_processed",
        PROJECT_ROOT / "data" / "03_analytical",
    ]

    data_files = []
    for d in data_dirs:
        if d.exists():
            for f in d.rglob("*"):
                if f.is_file() and f.suffix.lower() in (".csv", ".parquet", ".json"):
                    data_files.append({"name": f.name, "path": str(f.relative_to(PROJECT_ROOT)), "size": format_size(f.stat().st_size), "dir": f.parent.name})

    file_selector = pn.widgets.Select(name="Select Data File", options=[f["path"] for f in data_files], sizing_mode="stretch_width")
    preview_pane = pn.widgets.Tabulator(value=[], sizing_mode="stretch_both", pagination="remote", page_size=50)
    info_pane = pn.pane.Markdown("Select a file to preview...", sizing_mode="stretch_width")

    def on_file_change(event):
        if event.new:
            file_path = PROJECT_ROOT / event.new
            preview = get_data_preview(file_path)
            if preview:
                info_pane.object = f"**{file_path.name}**\n- Type: {preview['type']}\n- Rows: {preview['rows']}\n- Columns: {', '.join(preview['columns'][:10])}{'...' if len(preview['columns']) > 10 else ''}"
                preview_pane.value = preview["data"]
            else:
                info_pane.object = f"Could not preview {file_path.name}"
                preview_pane.value = []

    file_selector.param.watch(on_file_change, "value")

    return pn.Column(
        pn.pane.Markdown("### Data Viewer", margin=(0, 0, 10, 0)),
        pn.Row(file_selector, sizing_mode="stretch_width"),
        info_pane,
        preview_pane,
        sizing_mode="stretch_both",
    )

# === TAB 4: FIGURE GALLERY ===
def build_figure_gallery_tab():
    figures = get_latest_figures()
    gallery = pn.GridBox(ncols=4, sizing_mode="stretch_both")

    for fig in figures:
        img_path = PROJECT_ROOT / fig["path"]
        if img_path.exists():
            img = pn.pane.PNG(str(img_path), height=200, sizing_mode="scale_width")
            info = pn.pane.Markdown(f"**{fig['name']}**\n{fig['modified']}", sizing_mode="stretch_width")
            gallery.append(pn.Column(img, info, sizing_mode="stretch_width"))

    if not figures:
        gallery.append(pn.pane.Markdown("*No figures generated yet.*", sizing_mode="stretch_width"))

    return pn.Column(
        pn.pane.Markdown("### Figure Gallery", margin=(0, 0, 10, 0)),
        pn.pane.Markdown(f"Showing {len(figures)} most recent figures from `reports/figures/`", margin=(0, 0, 10, 0)),
        gallery,
        sizing_mode="stretch_both",
    )

# === TAB 5: METHODS & ACTIVITY LOGS ===
def build_methods_logs_tab():
    methods_log = get_methods_log()
    research_log = get_research_log()

    methods_viewer = pn.widgets.TextAreaInput(value=methods_log if methods_log else "No methods log yet. Methods are logged during analysis phases.", height=400, disabled=True, sizing_mode="stretch_width")
    research_viewer = pn.widgets.TextAreaInput(value=research_log if research_log else "No research log yet. Activity is logged during pipeline execution.", height=400, disabled=True, sizing_mode="stretch_width")

    # Dead ends
    dead_ends = get_dead_ends()
    dead_df = pn.widgets.Tabulator(value=dead_ends, sizing_mode="stretch_width", pagination="remote", page_size=10, columns=[
        {"field": "name", "title": "File", "width": 200},
        {"field": "title", "title": "Title", "width": 400},
        {"field": "modified", "title": "Modified", "width": 150},
    ])

    # Decisions
    decisions = get_decisions()
    decisions_df = pn.widgets.Tabulator(value=decisions, sizing_mode="stretch_width", pagination="remote", page_size=10, columns=[
        {"field": "name", "title": "File", "width": 200},
        {"field": "title", "title": "Title", "width": 400},
        {"field": "modified", "title": "Modified", "width": 150},
    ])

    return pn.Column(
        pn.Tabs(
            ("Methods Log", pn.Column(pn.pane.Markdown("### Methods Log", margin=(0, 0, 5, 0)), methods_viewer, sizing_mode="stretch_both")),
            ("Research Log", pn.Column(pn.pane.Markdown("### Research Activity Log", margin=(0, 0, 5, 0)), research_viewer, sizing_mode="stretch_both")),
            ("Dead Ends", pn.Column(pn.pane.Markdown("### Dead Ends", margin=(0, 0, 5, 0)), dead_df, sizing_mode="stretch_both")),
            ("Decisions", pn.Column(pn.pane.Markdown("### Methodological Decisions", margin=(0, 0, 5, 0)), decisions_df, sizing_mode="stretch_both")),
            dynamic=True,
            sizing_mode="stretch_both",
        ),
        sizing_mode="stretch_both",
    )

# === TAB 6: LITERATURE & ABSTRACTS ===
def build_literature_tab():
    abstracts = get_literature_abstracts()
    abs_df = pn.widgets.Tabulator(
        value=abstracts,
        sizing_mode="stretch_both",
        pagination="remote",
        page_size=15,
        configuration={"headerFilter": True},
        columns=[
            {"field": "title", "title": "Title", "width": 300},
            {"field": "authors", "title": "Authors", "width": 200},
            {"field": "year", "title": "Year", "width": 70},
            {"field": "doi", "title": "DOI", "width": 150},
            {"field": "abstract", "title": "Abstract", "width": 500},
            {"field": "claims", "title": "Claims", "width": 70},
        ],
    )

    # Citation verification
    citation_report = get_citation_report()
    if citation_report:
        citation_df = pn.widgets.Tabulator(
            value=[{"citation": c["citation"], "identifier": c["identifier"], "status": c["overall_status"], "pass_1": c["pass_1"]["status"], "pass_2": c["pass_2"]["status"], "pass_3": c["pass_3"]["status"]} for c in citation_report.get("citations", [])],
            sizing_mode="stretch_width",
            pagination="remote",
            page_size=20,
            columns=[
                {"field": "citation", "title": "Citation", "width": 250},
                {"field": "identifier", "title": "ID", "width": 150},
                {"field": "status", "title": "Overall", "width": 100},
                {"field": "pass_1", "title": "Existence", "width": 100},
                {"field": "pass_2", "title": "Content", "width": 100},
                {"field": "pass_3", "title": "Retraction", "width": 100},
            ],
        )
        citation_summary = pn.pane.Markdown(f"**Verdict:** {citation_report.get('verdict', 'N/A')} | **Total:** {citation_report.get('total_citations', 0)} | **Verified:** {citation_report.get('summary', {}).get('fully_verified', 0)}")
    else:
        citation_df = pn.pane.Markdown("*No citation verification report yet.*")
        citation_summary = pn.pane.Markdown("")

    # Claim trace
    claim_report = get_claim_trace_report()
    if claim_report:
        claim_df = pn.widgets.Tabulator(
            value=[{"id": c["id"], "type": c["type"], "status": c["status"], "location": c["location"], "text": c["text"][:100]} for c in claim_report.get("claims", [])],
            sizing_mode="stretch_width",
            pagination="remote",
            page_size=20,
            columns=[
                {"field": "id", "title": "ID", "width": 80},
                {"field": "type", "title": "Type", "width": 150},
                {"field": "status", "title": "Status", "width": 100},
                {"field": "location", "title": "Location", "width": 150},
                {"field": "text", "title": "Claim", "width": 400},
            ],
        )
        claim_summary = pn.pane.Markdown(f"**Verdict:** {claim_report.get('verdict', 'N/A')} | **Total:** {claim_report.get('total_claims', 0)} | **Traced:** {claim_report.get('summary', {}).get('fully_traced', 0)}")
    else:
        claim_df = pn.pane.Markdown("*No claim trace report yet.*")
        claim_summary = pn.pane.Markdown("")

    return pn.Column(
        pn.Tabs(
            ("Abstracts", pn.Column(pn.pane.Markdown("### Literature Abstracts", margin=(0, 0, 5, 0)), abs_df, sizing_mode="stretch_both")),
            ("Citation Verification", pn.Column(pn.pane.Markdown("### Citation Verification", margin=(0, 0, 5, 0)), citation_summary, citation_df, sizing_mode="stretch_both")),
            ("Claim Traces", pn.Column(pn.pane.Markdown("### Claim Traces", margin=(0, 0, 5, 0)), claim_summary, claim_df, sizing_mode="stretch_both")),
            dynamic=True,
            sizing_mode="stretch_both",
        ),
        sizing_mode="stretch_both",
    )

# === TAB 7: RESEARCH MAP & MANIFEST ===
def build_research_map_tab():
    research_map = get_research_map()
    manifest = get_manifest()
    iterations = get_iteration_registry()

    if research_map:
        map_json = pn.pane.JSON(object=research_map, depth=3, sizing_mode="stretch_both")
    else:
        map_json = pn.pane.Markdown("*No research map yet.*")

    if manifest:
        manifest_json = pn.pane.JSON(object=manifest, depth=3, sizing_mode="stretch_both")
    else:
        manifest_json = pn.pane.Markdown("*No manifest yet.*")

    if iterations:
        iter_df = pn.widgets.Tabulator(
            value=iterations.get("iterations", []),
            sizing_mode="stretch_width",
            pagination="remote",
            page_size=10,
            columns=[
                {"field": "id", "title": "ID", "width": 60},
                {"field": "type", "title": "Type", "width": 150},
                {"field": "trigger", "title": "Trigger", "width": 200},
                {"field": "date", "title": "Date", "width": 120},
                {"field": "status", "title": "Status", "width": 100},
                {"field": "summary", "title": "Summary", "width": 400},
            ],
        )
    else:
        iter_df = pn.pane.Markdown("*No iterations yet.*")

    return pn.Column(
        pn.Tabs(
            ("Research Map", pn.Column(pn.pane.Markdown("### Research Map", margin=(0, 0, 5, 0)), map_json, sizing_mode="stretch_both")),
            ("Manifest", pn.Column(pn.pane.Markdown("### Project Manifest", margin=(0, 0, 5, 0)), manifest_json, sizing_mode="stretch_both")),
            ("Iterations", pn.Column(pn.pane.Markdown("### Iteration Registry", margin=(0, 0, 5, 0)), iter_df, sizing_mode="stretch_both")),
            dynamic=True,
            sizing_mode="stretch_both",
        ),
        sizing_mode="stretch_both",
    )

# === TAB 8: ANALYSIS REPORTS ===
def build_analysis_reports_tab():
    # Analysis plan
    plans = get_analysis_plans()
    plan_content = plans[0]["content"] if plans else "*No analysis plan yet.*"

    # Methodology scout
    scouts = get_scout_reports()
    scout_content = scouts[0]["content"] if scouts else "*No methodology scout report yet.*"

    # Replication validation
    reps = get_replication_reports()
    rep_content = reps[0]["content"] if reps else "*No replication validation report yet.*"

    return pn.Column(
        pn.Tabs(
            ("Analysis Plan", pn.Column(pn.pane.Markdown("### Analysis Plan", margin=(0, 0, 5, 0)), pn.widgets.TextAreaInput(value=plan_content, height=500, disabled=True, sizing_mode="stretch_width"), sizing_mode="stretch_both")),
            ("Methodology Scout", pn.Column(pn.pane.Markdown("### Methodology Scout Report", margin=(0, 0, 5, 0)), pn.widgets.TextAreaInput(value=scout_content, height=500, disabled=True, sizing_mode="stretch_width"), sizing_mode="stretch_both")),
            ("Replication Validation", pn.Column(pn.pane.Markdown("### Replication Validation Report", margin=(0, 0, 5, 0)), pn.widgets.TextAreaInput(value=rep_content, height=500, disabled=True, sizing_mode="stretch_width"), sizing_mode="stretch_both")),
            dynamic=True,
            sizing_mode="stretch_both",
        ),
        sizing_mode="stretch_both",
    )

# === TAB 9: APPROVAL GATES ===
def build_approval_gates_tab():
    gate_info = pn.pane.Markdown("No pending approval gates.", sizing_mode="stretch_width")
    reason_input = pn.widgets.TextAreaInput(name="Feedback / Revision Instructions", placeholder="Enter feedback...", height=80, visible=False, sizing_mode="stretch_width")
    error_alert = pn.pane.Alert("", alert_type="danger", visible=False, sizing_mode="stretch_width")

    approve_btn = pn.widgets.Button(name="Approve & Continue", button_type="success", visible=False, sizing_mode="stretch_width")
    edit_btn = pn.widgets.Button(name="Edit Before Continue", button_type="warning", visible=False, sizing_mode="stretch_width")
    reject_btn = pn.widgets.Button(name="Reject & Retry", button_type="danger", visible=False, sizing_mode="stretch_width")

    def submit_response(status):
        global _current_pending_phase
        if not _current_pending_phase:
            error_alert.value = "No active pending phase."
            error_alert.visible = True
            return
        reason = reason_input.value.strip()
        if status in ("rejected", "edit") and not reason:
            error_alert.value = "Feedback required for Reject/Edit."
            error_alert.visible = True
            return
        response = {"phase": _current_pending_phase, "status": status, "reason": reason, "timestamp": datetime.now(timezone.utc).isoformat()}
        try:
            temp = APPROVAL_RESPONSE_PATH.with_suffix(".tmp")
            with open(temp, "w") as f:
                json.dump(response, f, indent=2)
            temp.replace(APPROVAL_RESPONSE_PATH)
            if PENDING_APPROVAL_PATH.exists():
                PENDING_APPROVAL_PATH.unlink()
            error_alert.visible = False
            reason_input.value = ""
            _current_pending_phase = None
            update_gate_ui(None)
            gate_info.object = f"Response '{status}' submitted for phase '{_current_pending_phase or 'unknown'}'."
        except Exception as e:
            error_alert.value = f"Error: {e}"
            error_alert.visible = True

    def update_gate_ui(pending_data):
        global _current_pending_phase
        if pending_data:
            _current_pending_phase = pending_data.get("phase")
            msg = pending_data.get("message", "No description.")
            ts = pending_data.get("timestamp", "Unknown")
            gate_info.object = f"### Pending: `{_current_pending_phase}`\n**Requested:** {ts}\n\n{msg}"
            reason_input.visible = True
            approve_btn.visible = True
            edit_btn.visible = True
            reject_btn.visible = True
        else:
            _current_pending_phase = None
            gate_info.object = "No pending approval gates."
            reason_input.visible = False
            approve_btn.visible = False
            edit_btn.visible = False
            reject_btn.visible = False
            error_alert.visible = False

    approve_btn.on_click(lambda e: submit_response("approved"))
    edit_btn.on_click(lambda e: submit_response("edit"))
    reject_btn.on_click(lambda e: submit_response("rejected"))

    # Store update function for polling
    global _update_gate_ui
    _update_gate_ui = update_gate_ui

    return pn.Column(
        pn.pane.Markdown("### Human Interception Gates", margin=(0, 0, 10, 0)),
        pn.pane.Markdown("Approve, request edits, or reject phase outputs before the pipeline continues.", margin=(0, 0, 10, 0)),
        gate_info,
        reason_input,
        error_alert,
        pn.Row(approve_btn, edit_btn, reject_btn, sizing_mode="stretch_width"),
        sizing_mode="stretch_width",
    )

# === TAB 10: SEARCH ===
def build_search_tab():
    search_input = pn.widgets.TextInput(name="Search", placeholder="Search files or content...", sizing_mode="stretch_width")
    search_mode = pn.widgets.RadioButtonGroup(name="Mode", options=["Files", "Content"], value="Files", sizing_mode="stretch_width")
    search_btn = pn.widgets.Button(name="Search", button_type="primary", sizing_mode="stretch_width")
    results_pane = pn.widgets.Tabulator(value=[], sizing_mode="stretch_both", pagination="remote", page_size=25)

    def on_search(event):
        query = search_input.value.strip()
        if not query:
            return
        if search_mode.value == "Files":
            results = search_files(query)
            results_pane.value = results
            results_pane.columns = [
                {"field": "name", "title": "Name", "width": 250},
                {"field": "path", "title": "Path", "width": 400},
                {"field": "size", "title": "Size", "width": 100},
                {"field": "type", "title": "Type", "width": 80},
            ]
        else:
            results = search_content(query)
            flat_results = []
            for r in results:
                for s in r.get("snippets", []):
                    flat_results.append({"file": r["name"], "path": r["path"], "line": s["line"], "snippet": s["text"]})
            results_pane.value = flat_results
            results_pane.columns = [
                {"field": "file", "title": "File", "width": 200},
                {"field": "path", "title": "Path", "width": 300},
                {"field": "line", "title": "Line", "width": 60},
                {"field": "snippet", "title": "Snippet", "width": 500},
            ]

    search_btn.on_click(on_search)
    search_input.param.watch(lambda e: on_search(None), "enter")

    return pn.Column(
        pn.pane.Markdown("### Search", margin=(0, 0, 10, 0)),
        pn.Row(search_input, search_mode, search_btn, sizing_mode="stretch_width"),
        results_pane,
        sizing_mode="stretch_both",
    )

# === TAB 11: CHECKPOINTS ===
def build_checkpoints_tab():
    cps = get_checkpoints()
    cp_df = pn.widgets.Tabulator(
        value=cps,
        sizing_mode="stretch_both",
        pagination="remote",
        page_size=20,
        columns=[
            {"field": "phase", "title": "Phase", "width": 200},
            {"field": "timestamp", "title": "Timestamp", "width": 200},
            {"field": "metadata", "title": "Metadata", "width": 500},
        ],
    )

    return pn.Column(
        pn.pane.Markdown("### Checkpoints", margin=(0, 0, 10, 0)),
        pn.pane.Markdown(f"{len(cps)} checkpoints saved. Resume from any checkpoint with: `research resume --from <phase>`", margin=(0, 0, 10, 0)),
        cp_df,
        sizing_mode="stretch_both",
    )

# ── Domain-Specific Tabs ─────────────────────────────────────────────────

def _get_domain_context() -> Optional[dict]:
    research_map = get_research_map()
    if not research_map:
        return None
    domain = research_map.get("domain", {})
    format_manifest = load_json_safe(CACHE_DIR / "data_format_manifest.json")
    return {
        "name": domain.get("name", "general"),
        "reporting_standard": domain.get("reporting_standard", ""),
        "format_manifest": format_manifest,
        "questions": research_map.get("questions", []),
    }

def _load_domain_registry() -> Optional[dict]:
    domain_reg_path = PROJECT_ROOT / ".research" / "domains" / "domain_registry.json"
    return load_json_safe(domain_reg_path)

def _load_tool_registry() -> Optional[dict]:
    tool_reg_path = PROJECT_ROOT / ".research" / "domains" / "tool_registry.json"
    return load_json_safe(tool_reg_path)

def _find_leaf_node(domain_name: str) -> Optional[dict]:
    reg = _load_domain_registry()
    if not reg:
        return None
    name_lower = domain_name.lower()
    for cat in reg.get("categories", []):
        for leaf in cat.get("leaf_nodes", []):
            if leaf["id"].lower() in name_lower or name_lower in leaf["id"].lower():
                return leaf
    return None

def build_genomics_tab():
    ctx = _get_domain_context()
    leaf = _find_leaf_node(ctx["name"] if ctx else "")
    tools = _load_tool_registry()
    tool_list = [t for t in tools.get("tools", []) if t.get("container") == "genomics"] if tools else []

    header = f"### Genomics Dashboard"
    if leaf:
        header += f"\n- **Leaf node**: {leaf.get('name', 'N/A')}"
        header += f"\n- **Reporting standard**: {leaf.get('reporting_standard', 'N/A')}"
        header += f"\n- **Primary tools**: {', '.join(leaf.get('primary_tools', []))}"
        header += f"\n- **File formats**: {', '.join(leaf.get('file_formats', []))}"

    # Variant summary table
    variant_files = []
    for d in [PROJECT_ROOT / "data" / "03_analytical", PROJECT_ROOT / "reports" / "analysis"]:
        if d.exists():
            for f in d.rglob("*"):
                if f.is_file() and f.suffix.lower() in (".vcf", ".csv", ".parquet"):
                    if any(kw in f.name.lower() for kw in ["variant", "snp", "vcf", "de", "expression"]):
                        variant_files.append({"name": f.name, "path": str(f.relative_to(PROJECT_ROOT)), "size": format_size(f.stat().st_size)})

    variant_df = pn.widgets.Tabulator(
        value=variant_files,
        sizing_mode="stretch_width",
        pagination="remote",
        page_size=10,
        columns=[
            {"field": "name", "title": "File", "width": 300},
            {"field": "path", "title": "Path", "width": 400},
            {"field": "size", "title": "Size", "width": 100},
        ],
    )

    # Tool availability
    tool_rows = [{"id": t.get("id"), "category": t.get("category"), "language": t.get("language")} for t in tool_list]
    tool_df = pn.widgets.Tabulator(
        value=tool_rows,
        sizing_mode="stretch_width",
        pagination="remote",
        page_size=10,
        columns=[
            {"field": "id", "title": "Tool", "width": 150},
            {"field": "category", "title": "Category", "width": 200},
            {"field": "language", "title": "Language", "width": 100},
        ],
    )

    return pn.Column(
        pn.Tabs(
            ("Overview", pn.Column(pn.pane.Markdown(header, margin=(0, 0, 10, 0)), sizing_mode="stretch_both")),
            ("Variant/DE Files", pn.Column(pn.pane.Markdown("### Variant & Differential Expression Files", margin=(0, 0, 5, 0)), variant_df, sizing_mode="stretch_both")),
            ("Tool Registry", pn.Column(pn.pane.Markdown(f"### Genomics Tools ({len(tool_list)} registered)", margin=(0, 0, 5, 0)), tool_df, sizing_mode="stretch_both")),
            dynamic=True,
            sizing_mode="stretch_both",
        ),
        sizing_mode="stretch_both",
    )

def build_chemistry_tab():
    ctx = _get_domain_context()
    leaf = _find_leaf_node(ctx["name"] if ctx else "")
    tools = _load_tool_registry()
    tool_list = [t for t in tools.get("tools", []) if t.get("container") in ("cheminformatics", "materials")] if tools else []

    header = f"### Chemistry / Cheminformatics Dashboard"
    if leaf:
        header += f"\n- **Leaf node**: {leaf.get('name', 'N/A')}"
        header += f"\n- **Primary tools**: {', '.join(leaf.get('primary_tools', []))}"
        header += f"\n- **File formats**: {', '.join(leaf.get('file_formats', []))}"

    mol_files = []
    for d in [PROJECT_ROOT / "inputs" / "data" / "raw", PROJECT_ROOT / "data" / "01_ingested"]:
        if d.exists():
            for f in d.rglob("*"):
                if f.is_file() and f.suffix.lower() in (".sdf", ".mol", ".mol2", ".pdb", ".cif", ".xyz"):
                    mol_files.append({"name": f.name, "path": str(f.relative_to(PROJECT_ROOT)), "format": f.suffix.upper(), "size": format_size(f.stat().st_size)})

    mol_df = pn.widgets.Tabulator(
        value=mol_files,
        sizing_mode="stretch_width",
        pagination="remote",
        page_size=10,
        columns=[
            {"field": "name", "title": "File", "width": 250},
            {"field": "path", "title": "Path", "width": 350},
            {"field": "format", "title": "Format", "width": 100},
            {"field": "size", "title": "Size", "width": 100},
        ],
    )

    tool_rows = [{"id": t.get("id"), "category": t.get("category"), "language": t.get("language")} for t in tool_list]
    tool_df = pn.widgets.Tabulator(
        value=tool_rows,
        sizing_mode="stretch_width",
        pagination="remote",
        page_size=10,
        columns=[
            {"field": "id", "title": "Tool", "width": 150},
            {"field": "category", "title": "Category", "width": 200},
            {"field": "language", "title": "Language", "width": 100},
        ],
    )

    return pn.Column(
        pn.Tabs(
            ("Overview", pn.Column(pn.pane.Markdown(header, margin=(0, 0, 10, 0)), sizing_mode="stretch_both")),
            ("Molecule Files", pn.Column(pn.pane.Markdown("### Molecule / Structure Files", margin=(0, 0, 5, 0)), mol_df, sizing_mode="stretch_both")),
            ("Tool Registry", pn.Column(pn.pane.Markdown(f"### Chemistry Tools ({len(tool_list)} registered)", margin=(0, 0, 5, 0)), tool_df, sizing_mode="stretch_both")),
            dynamic=True,
            sizing_mode="stretch_both",
        ),
        sizing_mode="stretch_both",
    )

def build_neuroimaging_tab():
    ctx = _get_domain_context()
    leaf = _find_leaf_node(ctx["name"] if ctx else "")
    tools = _load_tool_registry()
    tool_list = [t for t in tools.get("tools", []) if t.get("container") == "neuroimaging"] if tools else []

    header = f"### Neuroimaging Dashboard"
    if leaf:
        header += f"\n- **Leaf node**: {leaf.get('name', 'N/A')}"
        header += f"\n- **Reporting standard**: {leaf.get('reporting_standard', 'N/A')}"
        header += f"\n- **Primary tools**: {', '.join(leaf.get('primary_tools', []))}"
        header += f"\n- **File formats**: {', '.join(leaf.get('file_formats', []))}"

    nifti_files = []
    for d in [PROJECT_ROOT / "inputs" / "data" / "raw", PROJECT_ROOT / "data" / "01_ingested"]:
        if d.exists():
            for f in d.rglob("*"):
                if f.is_file() and f.suffix.lower() in (".nii", ".nii.gz", ".edf", ".fif", ".bdf"):
                    nifti_files.append({"name": f.name, "path": str(f.relative_to(PROJECT_ROOT)), "format": f.suffix.upper(), "size": format_size(f.stat().st_size)})

    nifti_df = pn.widgets.Tabulator(
        value=nifti_files,
        sizing_mode="stretch_width",
        pagination="remote",
        page_size=10,
        columns=[
            {"field": "name", "title": "File", "width": 250},
            {"field": "path", "title": "Path", "width": 350},
            {"field": "format", "title": "Format", "width": 100},
            {"field": "size", "title": "Size", "width": 100},
        ],
    )

    tool_rows = [{"id": t.get("id"), "category": t.get("category"), "language": t.get("language")} for t in tool_list]
    tool_df = pn.widgets.Tabulator(
        value=tool_rows,
        sizing_mode="stretch_width",
        pagination="remote",
        page_size=10,
        columns=[
            {"field": "id", "title": "Tool", "width": 150},
            {"field": "category", "title": "Category", "width": 200},
            {"field": "language", "title": "Language", "width": 100},
        ],
    )

    return pn.Column(
        pn.Tabs(
            ("Overview", pn.Column(pn.pane.Markdown(header, margin=(0, 0, 10, 0)), sizing_mode="stretch_both")),
            ("Imaging Files", pn.Column(pn.pane.Markdown("### Neuroimaging Files", margin=(0, 0, 5, 0)), nifti_df, sizing_mode="stretch_both")),
            ("Tool Registry", pn.Column(pn.pane.Markdown(f"### Neuroimaging Tools ({len(tool_list)} registered)", margin=(0, 0, 5, 0)), tool_df, sizing_mode="stretch_both")),
            dynamic=True,
            sizing_mode="stretch_both",
        ),
        sizing_mode="stretch_both",
    )

def build_finance_tab():
    ctx = _get_domain_context()
    leaf = _find_leaf_node(ctx["name"] if ctx else "")

    header = f"### Quantitative Finance Dashboard"
    if leaf:
        header += f"\n- **Leaf node**: {leaf.get('name', 'N/A')}"
        header += f"\n- **Reporting standard**: {leaf.get('reporting_standard', 'N/A')}"
        header += f"\n- **Primary tools**: {', '.join(leaf.get('primary_tools', []))}"

    # Look for execution metadata with finance tools
    exec_meta = load_json_safe(CACHE_DIR / "execution_metadata.json")
    sm = exec_meta.get("summary", {}) if exec_meta else {}

    summary_items = [
        f"- **Total executions**: {sm.get('total_executions', 0)}",
        f"- **Successful**: {sm.get('successful', 0)}",
        f"- **Failed**: {sm.get('failed', 0)}",
        f"- **Runtimes**: {', '.join(f'{k}: {v}' for k, v in sm.get('runtimes_used', {}).items())}",
    ]

    return pn.Column(
        pn.Tabs(
            ("Overview", pn.Column(pn.pane.Markdown(header, margin=(0, 0, 10, 0)), sizing_mode="stretch_both")),
            ("Execution Summary", pn.Column(pn.pane.Markdown("### Execution Summary\n" + "\n".join(summary_items), margin=(0, 0, 5, 0)), sizing_mode="stretch_both")),
            dynamic=True,
            sizing_mode="stretch_both",
        ),
        sizing_mode="stretch_both",
    )

def build_domain_tabs():
    """Build domain-specific tabs based on detected domain from research map."""
    ctx = _get_domain_context()
    if not ctx:
        return []

    domain_lower = ctx["name"].lower()
    tabs = []

    if any(kw in domain_lower for kw in ["genom", "rna", "transcript", "proteom", "metagenom", "single cell"]):
        tabs.append(("Genomics", build_genomics_tab()))

    if any(kw in domain_lower for kw in ["chem", "molecular", "qsar", "drug", "dock"]):
        tabs.append(("Chemistry", build_chemistry_tab()))

    if any(kw in domain_lower for kw in ["neuro", "fmri", "eeg", "meg", "imaging"]):
        tabs.append(("Neuroimaging", build_neuroimaging_tab()))

    if any(kw in domain_lower for kw in ["finance", "quant", "econ", "trading", "portfolio"]):
        tabs.append(("Finance", build_finance_tab()))

    return tabs

# ── Build Dashboard ──────────────────────────────────────────────────────
def build_dashboard():
    overview_tab = build_overview_tab()
    file_explorer_tab = build_file_explorer_tab()
    data_viewer_tab = build_data_viewer_tab()
    figure_gallery_tab = build_figure_gallery_tab()
    methods_logs_tab = build_methods_logs_tab()
    literature_tab = build_literature_tab()
    research_map_tab = build_research_map_tab()
    analysis_reports_tab = build_analysis_reports_tab()
    approval_gates_tab = build_approval_gates_tab()
    search_tab = build_search_tab()
    checkpoints_tab = build_checkpoints_tab()

    tab_list = [
        ("Overview", overview_tab),
        ("File Explorer", file_explorer_tab),
        ("Data Viewer", data_viewer_tab),
        ("Figure Gallery", figure_gallery_tab),
        ("Methods & Logs", methods_logs_tab),
        ("Literature & Abstracts", literature_tab),
        ("Research Map", research_map_tab),
        ("Analysis Reports", analysis_reports_tab),
        ("Approval Gates", approval_gates_tab),
        ("Search", search_tab),
        ("Checkpoints", checkpoints_tab),
    ]

    domain_tabs = build_domain_tabs()
    tab_list.extend(domain_tabs)

    tabs = pn.Tabs(*tab_list, dynamic=True, sizing_mode="stretch_both")

    return tabs

# ── Polling Callback ─────────────────────────────────────────────────────
def poll_updates():
    global _last_state, _last_log_mtime, _last_methods_mtime, _last_checkpoints
    global _update_gate_ui

    # Update approval gates
    if PENDING_APPROVAL_PATH.exists():
        try:
            with open(PENDING_APPROVAL_PATH) as f:
                pending_data = json.load(f)
            if hasattr(_update_gate_ui, "__call__"):
                _update_gate_ui(pending_data)
        except Exception:
            pass
    else:
        if hasattr(_update_gate_ui, "__call__"):
            _update_gate_ui(None)

# ── Launch ───────────────────────────────────────────────────────────────
dashboard = build_dashboard()
pn.state.add_periodic_callback(poll_updates, period=2000)

template = pn.template.FastListTemplate(
    title="Research Copilot — Control Panel",
    main=[dashboard],
    header_background="#1e293b",
    accent_base_color="#10b981",
    sidebar=[],
)

template.servable()
