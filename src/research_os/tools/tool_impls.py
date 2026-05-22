"""Standalone implementations for all §4.2 missing MCP tools.

Each function is self-contained and can be called directly from server.py handlers.
"""

from __future__ import annotations

import base64
import csv
import io
import json
import logging
import os
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("research.tools")


# ---------------------------------------------------------------------------
# tool.latex.compile
# ---------------------------------------------------------------------------

def latex_compile(root: Path) -> dict:
    """Run pdflatex + bibtex on synthesis/paper.tex.

    Runs: pdflatex → bibtex → pdflatex (×2) for proper cross-referencing.
    Returns dict with 'pdf_path', 'log', 'success', and optional 'warning'.
    """
    tex_path = root / "synthesis" / "paper.tex"
    if not tex_path.exists():
        return {"pdf_path": None, "success": False, "log": "", "warning": "synthesis/paper.tex not found"}

    pdflatex = shutil.which("pdflatex")
    bibtex = shutil.which("bibtex")
    if not pdflatex:
        return {"pdf_path": None, "success": False, "log": "", "warning": "pdflatex not found. Install TeX Live."}

    synthesis_dir = tex_path.parent
    log_lines: list[str] = []
    success = True

    def _run_pdflatex() -> bool:
        result = subprocess.run(
            [pdflatex, "-interaction=nonstopmode", "-halt-on-error", tex_path.name],
            cwd=str(synthesis_dir), capture_output=True, text=True, timeout=120,
        )
        log_lines.append(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
        return result.returncode == 0

    def _run_bibtex() -> bool:
        if not bibtex:
            log_lines.append("[WARN] bibtex not found — skipping bibliography compilation")
            return True
        aux = tex_path.with_suffix(".aux")
        if not aux.exists():
            return True
        result = subprocess.run(
            [bibtex, aux.name],
            cwd=str(synthesis_dir), capture_output=True, text=True, timeout=60,
        )
        log_lines.append(result.stdout[-1000:] if len(result.stdout) > 1000 else result.stdout)
        return True

    # Run 1: pdflatex
    if not _run_pdflatex():
        success = False
        log_lines.append("[ERROR] First pdflatex run failed")

    if success:
        _run_bibtex()

    # Run 2: pdflatex
    if success and not _run_pdflatex():
        success = False
        log_lines.append("[ERROR] Second pdflatex run failed")

    # Run 3: pdflatex (resolve all cross-refs)
    if success and not _run_pdflatex():
        success = False
        log_lines.append("[ERROR] Third pdflatex run failed")

    pdf_path = tex_path.with_suffix(".pdf")
    return {
        "pdf_path": str(pdf_path.absolute()) if pdf_path.exists() else None,
        "success": success,
        "log": "\n".join(log_lines[-50:]),
        "warning": None if success else "LaTeX compilation failed — see log for details",
    }


# ---------------------------------------------------------------------------
# tool.pubmed.search
# ---------------------------------------------------------------------------

def pubmed_search(query: str, limit: int = 5) -> dict:
    """Search PubMed via metapub. Returns structured results list."""
    try:
        from research_os.tools.actions.literature_retrieval import search_pubmed
        results = search_pubmed(query, limit)
        return {"query": query, "source": "pubmed", "count": len(results), "results": results}
    except Exception as e:
        logger.warning(f"PubMed search failed: {e}")
        return {"query": query, "source": "pubmed", "count": 0, "results": [], "warning": str(e)}


# ---------------------------------------------------------------------------
# tool.semantic_scholar.search
# ---------------------------------------------------------------------------

def semantic_scholar_search(query: str, limit: int = 5) -> dict:
    """Search Semantic Scholar via REST API. Uses the `semanticscholar` package if available, else direct HTTP."""
    try:
        import requests
        params = {"query": query, "limit": min(limit, 20), "fields": "title,abstract,authors,year,externalIds,url"}
        resp = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            params=params, timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        papers = data.get("data", [])
        results = []
        for p in papers:
            results.append({
                "title": p.get("title", ""),
                "authors": [a.get("name", "") for a in p.get("authors", [])],
                "year": p.get("year"),
                "abstract": (p.get("abstract") or "")[:500],
                "url": p.get("url", ""),
                "externalIds": p.get("externalIds", {}),
            })
        return {"query": query, "source": "semantic_scholar", "count": len(results), "results": results}
    except Exception as e:
        logger.warning(f"Semantic Scholar search failed: {e}")
        return {"query": query, "source": "semantic_scholar", "count": 0, "results": [], "warning": str(e)}


# ---------------------------------------------------------------------------
# tool.google.scholar.search
# ---------------------------------------------------------------------------

def google_scholar_search(query: str, limit: int = 5) -> dict:
    """Search Google Scholar.

    Uses the `scholarly` package if installed. Otherwise tries a lightweight
    requests-based approach with a warning about rate limits.
    """
    try:
        import scholarly
        search_query = scholarly.search_pubs(query)
        results = []
        for _ in range(limit):
            try:
                p = next(search_query)
                results.append({
                    "title": p.get("bib", {}).get("title", ""),
                    "authors": p.get("bib", {}).get("author", ""),
                    "year": p.get("bib", {}).get("year", ""),
                    "abstract": (p.get("bib", {}).get("abstract") or "")[:500],
                    "url": p.get("pub_url", ""),
                    "cites": p.get("num_citations", 0),
                })
            except StopIteration:
                break
        return {"query": query, "source": "google_scholar", "count": len(results), "results": results}
    except ImportError:
        return {
            "query": query, "source": "google_scholar", "count": 0, "results": [],
            "warning": "scholarly package not installed. Install with: pip install scholarly",
        }
    except Exception as e:
        logger.warning(f"Google Scholar search failed: {e}")
        return {"query": query, "source": "google_scholar", "count": 0, "results": [], "warning": str(e)}


# ---------------------------------------------------------------------------
# tool.data.transform
# ---------------------------------------------------------------------------

def data_transform(
    root: Path,
    filepath: str,
    operations: list[dict],
    output: str | None = None,
) -> dict:
    """Apply data transformations using sklearn.

    operations: list of dicts, each with:
      - type: "normalize" | "impute" | "encode" | "drop" | "rename"
      - columns: list of column names (optional, defaults to all applicable)
      - strategy: for impute — "mean"|"median"|"most_frequent"|"constant"
      - value: for constant impute or rename new name

    Returns path to output file and summary.
    """
    import numpy as np
    import pandas as pd
    from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
    from sklearn.impute import SimpleImputer

    data_path = root / filepath
    if not data_path.exists():
        return {"error": f"File not found: {filepath}", "output_path": None}

    df = pd.read_csv(data_path) if data_path.suffix == ".csv" else pd.read_parquet(data_path)
    summaries: list[str] = []

    for op in operations:
        op_type = op.get("type", "")
        cols = op.get("columns")
        if cols:
            available = [c for c in cols if c in df.columns]
            if not available:
                summaries.append(f"[{op_type}] no matching columns — skipped")
                continue
        else:
            available = list(df.columns)

        if op_type == "normalize":
            scaler = StandardScaler()
            numeric_cols = df[available].select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
                summaries.append(f"normalized {len(numeric_cols)} numeric columns (z-score)")
            else:
                summaries.append("[normalize] no numeric columns found")

        elif op_type == "impute":
            strategy = op.get("strategy", "mean")
            imputer = SimpleImputer(strategy=strategy, fill_value=op.get("value"))
            numeric_cols = df[available].select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                df[numeric_cols] = imputer.fit_transform(df[numeric_cols])
                summaries.append(f"imputed {len(numeric_cols)} columns (strategy={strategy})")
            else:
                summaries.append("[impute] no numeric columns found")

        elif op_type == "encode":
            cat_cols = df[available].select_dtypes(include=["object", "category"]).columns.tolist()
            if not cat_cols:
                summaries.append("[encode] no categorical columns found")
                continue
            if op.get("method") == "label":
                for c in cat_cols:
                    le = LabelEncoder()
                    df[c] = le.fit_transform(df[c].astype(str))
                summaries.append(f"label-encoded {len(cat_cols)} columns")
            else:
                df = pd.get_dummies(df, columns=cat_cols, drop_first=True)
                summaries.append(f"one-hot encoded {len(cat_cols)} columns")

        elif op_type == "drop":
            df = df.drop(columns=[c for c in available if c in df.columns], errors="ignore")
            summaries.append(f"dropped {len(available)} columns")

        elif op_type == "rename":
            mapping = {c: op.get("value", f"{c}_renamed") for c in available}
            df = df.rename(columns=mapping)
            summaries.append(f"renamed {len(available)} columns")

        else:
            summaries.append(f"[{op_type}] unknown operation — skipped")

    out_path = root / (output or f"workspace/data/derived/transformed_{Path(filepath).name}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.suffix == ".csv":
        df.to_csv(out_path, index=False)
    else:
        df.to_parquet(out_path, index=False)

    return {
        "output_path": str(out_path.absolute()),
        "original_shape": list(df.shape),
        "columns": list(df.columns),
        "summary": "; ".join(summaries),
    }


# ---------------------------------------------------------------------------
# tool.statistical.test
# ---------------------------------------------------------------------------

def statistical_test(
    filepath: str,
    test_type: str,
    x_column: str,
    y_column: str | None = None,
    group_column: str | None = None,
) -> dict:
    """Run a statistical test with automatic assumption checks.

    test_type: "ttest" | "anova" | "chi_square" | "mann_whitney" | "kruskal"
    """
    import numpy as np
    import pandas as pd
    from scipy import stats as sp_stats

    data_path = Path(filepath)
    if not data_path.exists():
        return {"error": f"File not found: {filepath}"}

    df = pd.read_csv(data_path) if data_path.suffix == ".csv" else pd.read_parquet(data_path)

    result: dict = {"test_type": test_type, "assumptions": {}, "results": {}}

    if test_type == "ttest":
        if not y_column and not group_column:
            return {"error": "ttest requires y_column (paired) or group_column (independent)"}
        if group_column:
            groups = df[group_column].unique()
            if len(groups) != 2:
                return {"error": f"ttest requires exactly 2 groups, got {len(groups)}"}
            a = df[df[group_column] == groups[0]][x_column].dropna()
            b = df[df[group_column] == groups[1]][x_column].dropna()
            # Normality (Shapiro-Wilk) per group
            for g_name, g_data in [(groups[0], a), (groups[1], b)]:
                if len(g_data) >= 3:
                    stat, pv = sp_stats.shapiro(g_data)
                    result["assumptions"][f"normality_{g_name}"] = {
                        "test": "shapiro", "statistic": round(stat, 4), "p_value": round(pv, 4),
                        "passed": pv > 0.05,
                    }
            # Homogeneity of variance (Levene)
            if len(a) >= 2 and len(b) >= 2:
                l_stat, l_pv = sp_stats.levene(a, b)
                result["assumptions"]["homogeneity"] = {
                    "test": "levene", "statistic": round(l_stat, 4), "p_value": round(l_pv, 4),
                    "passed": l_pv > 0.05,
                }
            # Welch t-test (does not assume equal variance)
            t_stat, p_val = sp_stats.ttest_ind(a, b, equal_var=False)
            result["results"] = {
                "test": "Welch t-test", "statistic": round(t_stat, 4), "p_value": round(p_val, 4),
                "significant": p_val < 0.05,
                "group_a": str(groups[0]), "group_b": str(groups[1]),
                "mean_a": round(float(a.mean()), 4), "mean_b": round(float(b.mean()), 4),
            }
        else:
            # Paired t-test
            paired = df[[x_column, y_column]].dropna()
            if len(paired) < 3:
                return {"error": "Need at least 3 paired observations"}
            diff = paired[x_column] - paired[y_column]
            if len(diff) >= 3:
                s_stat, s_pv = sp_stats.shapiro(diff)
                result["assumptions"]["normality_diff"] = {
                    "test": "shapiro", "statistic": round(s_stat, 4), "p_value": round(s_pv, 4),
                    "passed": s_pv > 0.05,
                }
            t_stat, p_val = sp_stats.ttest_rel(paired[x_column], paired[y_column])
            result["results"] = {
                "test": "Paired t-test", "statistic": round(t_stat, 4), "p_value": round(p_val, 4),
                "significant": p_val < 0.05,
                "mean_diff": round(float(paired[x_column].mean() - paired[y_column].mean()), 4),
            }

    elif test_type == "anova":
        if not group_column:
            return {"error": "anova requires group_column"}
        groups = [g[x_column].dropna().values for _, g in df.groupby(group_column)]
        if len(groups) < 2:
            return {"error": "Need at least 2 groups for ANOVA"}
        # Normality per group
        for i, g in enumerate(groups):
            if len(g) >= 3:
                s_stat, s_pv = sp_stats.shapiro(g)
                result["assumptions"][f"normality_group_{i}"] = {
                    "test": "shapiro", "statistic": round(s_stat, 4), "p_value": round(s_pv, 4),
                    "passed": s_pv > 0.05,
                }
        # Homogeneity
        if all(len(g) >= 2 for g in groups):
            l_stat, l_pv = sp_stats.levene(*groups)
            result["assumptions"]["homogeneity"] = {
                "test": "levene", "statistic": round(l_stat, 4), "p_value": round(l_pv, 4),
                "passed": l_pv > 0.05,
            }
        f_stat, p_val = sp_stats.f_oneway(*groups)
        result["results"] = {
            "test": "One-way ANOVA", "statistic": round(f_stat, 4), "p_value": round(p_val, 4),
            "significant": p_val < 0.05, "num_groups": len(groups),
        }

    elif test_type == "chi_square":
        if not y_column:
            return {"error": "chi_square requires x_column and y_column for contingency table"}
        ct = pd.crosstab(df[x_column], df[y_column])
        chi2, p_val, dof, expected = sp_stats.chi2_contingency(ct)
        result["assumptions"]["expected_frequencies"] = {
            "min_expected": round(float(expected.min()), 2),
            "passed": bool((expected >= 5).all()),
        }
        result["results"] = {
            "test": "Chi-square test of independence", "statistic": round(chi2, 4),
            "p_value": round(p_val, 4), "significant": p_val < 0.05,
            "degrees_of_freedom": int(dof),
            "contingency_shape": list(ct.shape),
        }

    elif test_type == "mann_whitney":
        if not group_column:
            return {"error": "mann_whitney requires group_column"}
        groups = df[group_column].unique()
        if len(groups) != 2:
            return {"error": "mann_whitney requires exactly 2 groups"}
        a = df[df[group_column] == groups[0]][x_column].dropna()
        b = df[df[group_column] == groups[1]][x_column].dropna()
        u_stat, p_val = sp_stats.mannwhitneyu(a, b, alternative="two-sided")
        result["results"] = {
            "test": "Mann-Whitney U", "statistic": round(u_stat, 4), "p_value": round(p_val, 4),
            "significant": p_val < 0.05,
            "median_a": round(float(a.median()), 4), "median_b": round(float(b.median()), 4),
        }

    elif test_type == "kruskal":
        if not group_column:
            return {"error": "kruskal requires group_column"}
        groups = [g[x_column].dropna().values for _, g in df.groupby(group_column)]
        if len(groups) < 2:
            return {"error": "Need at least 2 groups for Kruskal-Wallis"}
        h_stat, p_val = sp_stats.kruskal(*groups)
        result["results"] = {
            "test": "Kruskal-Wallis H", "statistic": round(h_stat, 4), "p_value": round(p_val, 4),
            "significant": p_val < 0.05, "num_groups": len(groups),
        }

    else:
        return {"error": f"Unknown test type: {test_type}"}

    return result


# ---------------------------------------------------------------------------
# tool.figure.create
# ---------------------------------------------------------------------------

def figure_create(
    root: Path,
    filepath: str,
    chart_type: str,
    x_column: str,
    y_column: str | None = None,
    group_column: str | None = None,
    title: str = "",
    output: str | None = None,
) -> dict:
    """Create a publication-quality figure from data.

    chart_type: "scatter" | "line" | "bar" | "hist" | "box" | "violin" | "heatmap" | "pairplot"
    Returns path to the saved figure PNG.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns

    data_path = root / filepath
    if not data_path.exists():
        return {"error": f"File not found: {filepath}", "figure_path": None}

    df = pd.read_csv(data_path) if data_path.suffix == ".csv" else pd.read_parquet(data_path)

    sns.set_theme(style="whitegrid", font_scale=1.1)
    fig, ax = plt.subplots(figsize=(8, 5))

    try:
        if chart_type == "scatter":
            if not y_column:
                return {"error": "scatter requires x_column and y_column"}
            hue = group_column if group_column and group_column in df.columns else None
            sns.scatterplot(data=df, x=x_column, y=y_column, hue=hue, ax=ax)

        elif chart_type == "line":
            if not y_column:
                return {"error": "line requires x_column and y_column"}
            sns.lineplot(data=df, x=x_column, y=y_column, ax=ax)

        elif chart_type == "bar":
            if not y_column:
                return {"error": "bar requires x_column and y_column"}
            hue = group_column if group_column and group_column in df.columns else None
            sns.barplot(data=df, x=x_column, y=y_column, hue=hue, ax=ax, errorbar="ci")

        elif chart_type == "hist":
            sns.histplot(data=df, x=x_column, kde=True, ax=ax)

        elif chart_type == "box":
            if y_column:
                hue = group_column if group_column and group_column in df.columns else None
                sns.boxplot(data=df, x=x_column, y=y_column, hue=hue, ax=ax)
            else:
                sns.boxplot(data=df, y=x_column, ax=ax)

        elif chart_type == "violin":
            if y_column:
                sns.violinplot(data=df, x=x_column, y=y_column, ax=ax)
            else:
                sns.violinplot(data=df, y=x_column, ax=ax)

        elif chart_type == "heatmap":
            corr = df.select_dtypes(include="number").corr()
            sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0, ax=ax)
            ax.set_title("Correlation Heatmap" if not title else title)

        elif chart_type == "pairplot":
            plt.close(fig)
            hue = group_column if group_column and group_column in df.columns else None
            numeric = df.select_dtypes(include="number").columns.tolist()
            if len(numeric) > 8:
                numeric = numeric[:8]
            g = sns.pairplot(df[numeric + ([hue] if hue else [])], hue=hue, diag_kind="kde")
            out_path = root / (output or f"workspace/figures/{Path(filepath).stem}_pairplot.png")
            out_path.parent.mkdir(parents=True, exist_ok=True)
            g.savefig(str(out_path), dpi=300, bbox_inches="tight")
            plt.close("all")
            return {"figure_path": str(out_path.absolute()), "chart_type": chart_type}

        else:
            plt.close(fig)
            return {"error": f"Unknown chart type: {chart_type}", "figure_path": None}

        ax.set_title(title if title else f"{chart_type.title()} of {x_column}")
        ax.set_xlabel(x_column)
        if y_column:
            ax.set_ylabel(y_column)
        fig.tight_layout()

        out_path = root / (output or f"workspace/figures/{Path(filepath).stem}_{chart_type}.png")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(str(out_path), dpi=300, bbox_inches="tight")
        plt.close(fig)

        return {"figure_path": str(out_path.absolute()), "chart_type": chart_type}

    except Exception as e:
        plt.close(fig)
        return {"error": f"Figure creation failed: {e}", "figure_path": None}


# ---------------------------------------------------------------------------
# tool.dashboard.create
# ---------------------------------------------------------------------------

def dashboard_create(root: Path, filepath: str, dashboard_type: str = "panel") -> dict:
    """Generate a data dashboard from an experiment output file.

    dashboard_type: "panel" | "html" (panel preferred, html fallback)
    Returns path to the dashboard file.
    """
    import pandas as pd

    data_path = root / filepath
    if not data_path.exists():
        return {"error": f"File not found: {filepath}", "dashboard_path": None}

    df = pd.read_csv(data_path) if data_path.suffix == ".csv" else pd.read_parquet(data_path)
    stem = Path(filepath).stem

    if dashboard_type == "panel":
        try:
            import panel as pn
            pn.extension("vega", "plotly")
            import plotly.express as px

            numeric_cols = df.select_dtypes(include="number").columns.tolist()
            cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

            tabs = []
            if numeric_cols:
                corr_fig = px.imshow(
                    df[numeric_cols].corr(), text_auto=".2f", color_continuous_scale="RdBu_r",
                    title="Correlation Matrix",
                )
                tabs.append(("Correlation", pn.pane.Plotly(corr_fig, sizing_mode="stretch_width")))

                for col in numeric_cols[:4]:
                    fig = px.histogram(df, x=col, title=f"Distribution of {col}", marginal="box")
                    tabs.append((col, pn.pane.Plotly(fig, sizing_mode="stretch_width")))

            if cat_cols:
                for col in cat_cols[:3]:
                    val_counts = df[col].value_counts().reset_index()
                    fig = px.bar(val_counts, x="index", y=col, title=f"Counts by {col}")
                    tabs.append((col, pn.pane.Plotly(fig, sizing_mode="stretch_width")))

            tab_layout = pn.Tabs(*tabs)
            dashboard = pn.Column(
                pn.pane.Markdown(f"# Dashboard: {stem}\n*Auto-generated by Research OS*"),
                pn.pane.DataFrame(df.describe(include="all"), sizing_mode="stretch_width"),
                tab_layout,
                sizing_mode="stretch_width",
            )

            out_path = root / f"workspace/dashboards/{stem}_dashboard.html"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            dashboard.save(str(out_path), embed=True)
            return {"dashboard_path": str(out_path.absolute()), "type": "panel"}
        except ImportError:
            logger.info("panel not installed, falling back to HTML dashboard")

    # Fallback: generate a self-contained HTML dashboard
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    html_parts = [
        "<html><head><meta charset='utf-8'><title>Dashboard</title>",
        "<style>body{font-family:sans-serif;margin:20px}table{border-collapse:collapse}"
        "th,td{border:1px solid #ddd;padding:6px}th{background:#f5f5f5}</style></head><body>",
        f"<h1>Dashboard: {stem}</h1>",
        f"<p><em>Auto-generated by Research OS</em></p>",
        f"<h2>Summary ({df.shape[0]} rows, {df.shape[1]} cols)</h2>",
        df.describe(include="all").to_html(),
    ]
    if numeric_cols:
        html_parts.append(f"<h2>Correlation Matrix</h2>{df[numeric_cols].corr().to_html()}")
    html_parts.append("<h2>Data Preview (first 20 rows)</h2>")
    html_parts.append(df.head(20).to_html())
    html_parts.append("</body></html>")

    out_path = root / f"workspace/dashboards/{stem}_dashboard.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(html_parts))
    return {"dashboard_path": str(out_path.absolute()), "type": "html"}


# ---------------------------------------------------------------------------
# view.workspace.tree
# ---------------------------------------------------------------------------

def workspace_tree(root: Path, max_depth: int = 4) -> dict:
    """Return the full directory tree with file sizes and last-modified timestamps."""
    ws = root / "workspace"
    if not ws.exists():
        return {"tree": "(workspace does not exist)", "entries": [], "total_files": 0, "total_dirs": 0}

    entries: list[dict] = []

    def _walk(dir_path: Path, depth: int = 0):
        if depth > max_depth:
            return
        try:
            for child in sorted(dir_path.iterdir()):
                is_dir = child.is_dir()
                stat = child.stat() if child.exists() else None
                entries.append({
                    "path": str(child.relative_to(root)),
                    "type": "directory" if is_dir else "file",
                    "size_bytes": stat.st_size if stat and not is_dir else None,
                    "size_hr": _human_size(stat.st_size) if stat and not is_dir else None,
                    "modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat() if stat else None,
                    "depth": depth,
                })
                if is_dir:
                    _walk(child, depth + 1)
        except PermissionError:
            pass

    _walk(ws)

    # Build a text tree
    lines: list[str] = ["workspace/"]
    indent_cache: dict[int, str] = {}

    def _format_path(rel: str) -> str:
        parts = rel.split("/")
        result = ""
        for i, p in enumerate(parts):
            if i == 0 and p == "workspace":
                continue
            if i not in indent_cache:
                indent_cache[i] = "  " * i
            result += f"\n{indent_cache[i]}  {p}/" if i < len(parts) - 1 else f"\n{indent_cache[i]}  {p}"
        return result.strip()

    for e in entries:
        if e["type"] == "file":
            size = e["size_hr"] or ""
            lines.append(f"  {e['path'].replace('workspace/', '', 1)}  ({size})")

    return {
        "tree": "\n".join(lines),
        "entries": entries,
        "total_files": sum(1 for e in entries if e["type"] == "file"),
        "total_dirs": sum(1 for e in entries if e["type"] == "directory"),
    }


def _human_size(bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if bytes < 1024:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024
    return f"{bytes:.1f} TB"


# ---------------------------------------------------------------------------
# view.data.head
# ---------------------------------------------------------------------------

def data_head(root: Path, filepath: str, n: int = 5) -> dict:
    """Return first N rows + column types + summary stats for any data file."""
    import pandas as pd

    data_path = root / filepath
    if not data_path.exists():
        return {"error": f"File not found: {filepath}"}

    ext = data_path.suffix.lower()
    try:
        if ext == ".csv":
            df = pd.read_csv(data_path)
        elif ext in (".xlsx", ".xls"):
            df = pd.read_excel(data_path)
        elif ext == ".parquet":
            df = pd.read_parquet(data_path)
        elif ext == ".feather":
            df = pd.read_feather(data_path)
        elif ext == ".json":
            df = pd.read_json(data_path)
        else:
            return {"error": f"Unsupported file format: {ext}"}
    except Exception as e:
        return {"error": f"Failed to read file: {e}"}

    buf = io.StringIO()
    df.info(buf=buf)
    info_str = buf.getvalue()

    return {
        "filepath": filepath,
        "shape": list(df.shape),
        "columns": [
            {"name": c, "dtype": str(df[c].dtype), "non_null": int(df[c].notna().sum()),
             "null_pct": round(float(df[c].isna().mean() * 100), 1)}
            for c in df.columns
        ],
        "info": info_str,
        "head": df.head(n).to_dict(orient="records"),
        "describe": df.describe(include="all").to_dict() if len(df) > 0 else {},
    }


# ---------------------------------------------------------------------------
# view.figure.show
# ---------------------------------------------------------------------------

def figure_show(root: Path, filepath: str) -> dict:
    """Read a figure file and return it as a base64-encoded PNG."""
    fig_path = root / filepath
    if not fig_path.exists():
        return {"error": f"Figure not found: {filepath}", "base64": None}

    ext = fig_path.suffix.lower()
    media_type = "image/png" if ext == ".png" else "image/jpeg" if ext in (".jpg", ".jpeg") else "image/svg+xml" if ext == ".svg" else None
    if not media_type:
        return {"error": f"Unsupported figure format: {ext}", "base64": None}

    b64 = base64.b64encode(fig_path.read_bytes()).decode("utf-8")
    return {
        "filepath": str(fig_path.absolute()),
        "media_type": media_type,
        "base64": b64,
        "size_bytes": fig_path.stat().st_size,
    }
