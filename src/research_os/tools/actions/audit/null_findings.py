"""Null-findings reporter.

Publishable companion document for everything that didn't pan out:
* hypotheses with status `refuted` or `inconclusive`,
* tests that were underpowered (per ``tool_audit_power`` results),
* paths that were `__DEAD_END`'d with rationale.

Why this matters: the file drawer problem is the biggest distortion
in scientific literature. A project that explicitly documents what
DIDN'T work — with honest framing about whether the null is
"no effect" or "no evidence of effect" — is far more useful to the
community than one that only publishes the positives.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("research_os.audit.null_findings")


def _collect_underpowered(root: Path) -> list[dict[str, Any]]:
    """Find every step that ran a power audit and came out underpowered."""
    underpowered: list[dict[str, Any]] = []
    ws = root / "workspace"
    if not ws.exists():
        return []
    for step in sorted(ws.iterdir()):
        if not (step.is_dir() and re.match(r"^\d{2,3}_", step.name)):
            continue
        if step.name.endswith("__DEAD_END"):
            continue
        rep = step / "outputs" / "reports" / "power_report.md"
        if not rep.exists():
            continue
        text = rep.read_text()
        m = re.search(r"Computed power:\s*([\d.]+)", text)
        if m:
            try:
                p = float(m.group(1))
                if p < 0.8:
                    underpowered.append({
                        "step_id": step.name,
                        "power": p,
                        "report": str(rep.relative_to(root)),
                    })
            except ValueError:
                pass
    return underpowered


def _collect_null_hypotheses(state: dict[str, Any]) -> list[dict[str, Any]]:
    hyps = state.get("active_hypotheses") or []
    return [h for h in hyps if h.get("status") in {"refuted", "inconclusive"}]


def _collect_dead_ends(state: dict[str, Any], root: Path) -> list[dict[str, Any]]:
    """Walk dead_ends + each __DEAD_END step's abandon_rationale."""
    out: list[dict[str, Any]] = []
    for dead_path in state.get("dead_ends", []) or []:
        info = (state.get("paths") or {}).get(dead_path, {})
        out.append({
            "path": dead_path,
            "abandoned_at": info.get("abandoned_at"),
            "rationale": info.get("abandon_rationale", "(no rationale recorded)"),
        })
    # Also walk workspace for __DEAD_END dirs whose abandon_rationale wasn't
    # mirrored into state.
    ws = root / "workspace"
    if ws.exists():
        for d in sorted(ws.iterdir()):
            if d.is_dir() and d.name.endswith("__DEAD_END"):
                stem = d.name.replace("__DEAD_END", "")
                if any(o["path"] == stem for o in out):
                    continue
                out.append({
                    "path": stem,
                    "abandoned_at": None,
                    "rationale": "(dead-end on disk, no metadata)",
                })
    return out


def write_null_findings(root: Path) -> dict[str, Any]:
    """Assemble ``synthesis/null_findings.md`` from the project audit chain."""
    from research_os.project_ops import load_state

    state = load_state(root)
    underpowered = _collect_underpowered(root)
    nulls = _collect_null_hypotheses(state)
    deads = _collect_dead_ends(state, root)

    out = root / "synthesis" / "null_findings.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    title = state.get("project_name", "Research Project")

    lines = [
        f"# {title} — Null findings & abandoned paths",
        "",
        f"*Generated {datetime.now(timezone.utc).isoformat()}*",
        "",
        "> **Why this document exists.** Reporting only positive findings "
        "distorts the literature (the file-drawer problem). This file "
        "lists every hypothesis that was tested and did not confirm, "
        "every analysis that turned out underpowered, and every "
        "experimental path that was abandoned — with the reasoning.",
        "",
        "## Refuted or inconclusive hypotheses",
        "",
    ]
    if nulls:
        for h in nulls:
            status = h.get("status", "?")
            hid = h.get("id", "?")
            statement = h.get("statement", "")
            ev = (h.get("evidence") or [{}])[-1]
            note = ev.get("note", "")
            lines.append(f"### {hid} — {statement}")
            lines.append(f"- **Status**: `{status}`")
            if ev.get("step"):
                lines.append(f"- **Step**: `{ev['step']}`")
            if note:
                lines.append(f"- **Evidence**: {note}")
            if status == "inconclusive":
                lines.append(
                    "- **Honest framing**: \"no evidence of effect\" — "
                    "not the same as \"evidence of no effect\". Report "
                    "the observed 95% CI and the minimum-detectable "
                    "effect for the achieved n."
                )
            lines.append("")
    else:
        lines.append("_(no refuted or inconclusive hypotheses tracked)_")
        lines.append("")

    lines.append("## Underpowered tests")
    lines.append("")
    if underpowered:
        lines.append("Tests where the computed power is below the "
                     "conventional 0.80 floor. The minimum detectable "
                     "effect (MDE) at the achieved sample size, not the "
                     "observed p-value, is the honest summary here.")
        lines.append("")
        for up in underpowered:
            lines.append(
                f"- `{up['step_id']}` — computed power = {up['power']:.2f}. "
                f"Power report: `{up['report']}`."
            )
        lines.append("")
    else:
        lines.append("_(no tests flagged as underpowered)_")
        lines.append("")

    lines.append("## Abandoned experimental paths")
    lines.append("")
    if deads:
        for d in deads:
            lines.append(f"### `{d['path']}`")
            if d.get("abandoned_at"):
                lines.append(f"- Abandoned: {d['abandoned_at']}")
            lines.append(f"- Rationale: {d['rationale']}")
            lines.append(
                f"- Preserved at: "
                f"`workspace/{d['path']}__DEAD_END/`"
            )
            lines.append("")
    else:
        lines.append("_(no abandoned paths)_")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("**Submission tip.** Many journals now accept "
                 "[Registered Reports](https://en.wikipedia.org/wiki/Registered_report) "
                 "where in-principle acceptance precedes data — these "
                 "are the strongest defence against publication bias. "
                 "If this project was pre-registered, link the "
                 "pre-registration ID prominently.")

    out.write_text("\n".join(lines) + "\n")

    return {
        "status": "success",
        "report_path": str(out.relative_to(root)),
        "n_null_hypotheses": len(nulls),
        "n_underpowered_tests": len(underpowered),
        "n_abandoned_paths": len(deads),
        "advice": (
            f"Null-findings document written. {len(nulls)} hypotheses, "
            f"{len(underpowered)} underpowered tests, "
            f"{len(deads)} abandoned paths. Submit as a companion paper "
            "or include as an appendix to the main paper."
        ),
    }


__all__ = ["write_null_findings"]
