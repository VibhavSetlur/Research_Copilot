"""Iterative planning — the AI repeatedly proposes the BEST next step.

Some researchers don't want to dictate every move ("now run X, now run Y").
They want the AI to assess the current state, search literature + tools, and
propose what's most worth doing next. This module supports that workflow.

Public functions
----------------
* ``plan_next_step``       — propose the best next step given current state.
* ``branch_recommendation`` — when to fork a parallel experiment vs continue.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("research_os.tools.research.planning")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_plan(root: Path, body: str) -> str:
    """Write a planning document into the active step (or workspace/logs)."""
    from research_os.tools.actions.audit.audit import get_current_path

    current = get_current_path(root)
    target_dir = (
        root / "workspace" / current / "outputs" / "reports"
        if current
        else root / "workspace" / "logs"
    )
    target_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = target_dir / f"next_step_plan_{ts}.md"
    out.write_text(body)
    return str(out.relative_to(root))


def plan_next_step(root: Path, *, goal: str | None = None,
                   search_literature: bool = True,
                   search_tools: bool = True) -> dict[str, Any]:
    """Survey current state + search the world + propose the best next step.

    Pulls together:
      - active hypotheses (from state)
      - completed and active experiment paths
      - latest conclusions
      - audit warnings (if audit_report.md exists)
      - fresh literature on the open questions
      - tool candidates if a methodological question is open
    Returns a structured plan and writes it as a markdown into the active step.
    """
    try:
        from research_os.project_ops import load_state
        from research_os.tools.actions.search.search import search_semantic_scholar, search_web
        from research_os.tools.actions.state.path import list_paths

        state = load_state(root)
        paths_info = list_paths(root).get("paths", []) or []
        active = [p for p in paths_info if p.get("status") == "active"]
        completed = [p for p in paths_info if p.get("status") == "completed"]
        dead = [p for p in paths_info if p.get("status") == "dead_end"]
        hypotheses = state.get("active_hypotheses", []) or []

        # ── Pull recent conclusions ─────────────────────────────────────
        recent_conclusions: list[dict[str, str]] = []
        for p in (active + completed)[-3:]:
            conc_path = Path(p["experiment_dir"]) / "conclusions.md"
            if conc_path.exists():
                recent_conclusions.append(
                    {"path": p["path_id"], "text": conc_path.read_text()[:2000]}
                )

        # ── Pull audit warnings ────────────────────────────────────────
        audit_report = root / "workspace" / "logs" / "audit_report.md"
        audit_text = audit_report.read_text()[:2000] if audit_report.exists() else ""

        # ── Decide what to search ──────────────────────────────────────
        question = (
            goal
            or (
                state.get("research_question")
                or (hypotheses[0].get("statement") if hypotheses else "")
                or "next analytical step"
            )
        )

        lit_hits: list[dict[str, Any]] = []
        if search_literature:
            try:
                lit_hits = search_semantic_scholar(question, limit=5)
            except Exception as e:
                logger.warning(f"plan literature search failed: {e}")

        tool_hits: list[dict[str, Any]] = []
        if search_tools and goal:
            try:
                web = search_web(f"{goal} library tool", limit=5)
                tool_hits = web.get("results", [])
            except Exception as e:
                logger.warning(f"plan tool search failed: {e}")

        # ── Build the recommendation ───────────────────────────────────
        # Heuristics for what to do next:
        recommendations: list[str] = []
        untested = [h for h in hypotheses if h.get("status") == "testing"]
        refuted = [h for h in hypotheses if h.get("status") == "refuted"]

        if not hypotheses:
            recommendations.append(
                "No hypotheses tracked. Run `tool_intake_autofill` or register "
                "hypotheses with `mem_hypothesis_add` before more experiments."
            )
        elif untested:
            recommendations.append(
                f"Open hypotheses without conclusive evidence: "
                f"{', '.join(h['id'] for h in untested)}. Design a new experiment "
                "targeting one of them via `guidance/analysis_plan`."
            )
        elif refuted and not completed:
            recommendations.append(
                "All current hypotheses refuted. Either revise the research "
                "question (`docs/research_question.md`) or branch to a different "
                "methodological angle via `guidance/dead_end_routing`."
            )
        if dead:
            recommendations.append(
                f"{len(dead)} dead-end path(s) on record. Review their "
                "`conclusions.md` before re-trying similar approaches."
            )
        if audit_text and "BLOCKER" in audit_text:
            recommendations.append(
                "Audit has BLOCKER warnings. Resolve those before any synthesis."
            )
        if state.get("pipeline_stage") in {"execution", "analysis"} and not active:
            recommendations.append(
                "No active experiment path. Create one via `sys_path_create` "
                "before writing scripts."
            )

        # ── Write the plan markdown ────────────────────────────────────
        lines = [
            f"# Next-step plan — {_now()}",
            "",
            f"## Project state",
            f"- Stage: `{state.get('pipeline_stage', 'init')}`",
            f"- Active paths: {len(active)} · completed: {len(completed)} · dead: {len(dead)}",
            f"- Hypotheses tracked: {len(hypotheses)} "
            f"(testing: {len(untested)}, refuted: {len(refuted)})",
            "",
            "## Recent conclusions",
        ]
        if not recent_conclusions:
            lines.append("- (none yet)")
        for c in recent_conclusions:
            lines.append(f"### `{c['path']}`")
            lines.append("```")
            lines.append(c["text"])
            lines.append("```")

        if audit_text:
            lines.extend(["", "## Latest audit (head)", "```", audit_text, "```"])

        lines.extend(["", "## Fresh literature on the open question", ""])
        if not lit_hits:
            lines.append("- (no literature retrieved — provider may be down)")
        for paper in lit_hits[:5]:
            title = (paper.get("title") or "")[:140]
            year = paper.get("year") or ""
            url = paper.get("url") or ""
            lines.append(f"- **{title}** ({year}) {url}")

        if tool_hits:
            lines.extend(["", "## Tool / library candidates", ""])
            for t in tool_hits[:5]:
                lines.append(f"- **{t.get('title', '')[:120]}** — {t.get('url', '')}")

        lines.extend(["", "## Recommended next steps", ""])
        if not recommendations:
            recommendations.append(
                "Pipeline looks healthy. Suggested next: continue "
                "`guidance/analysis_plan` for the next hypothesis, OR move to "
                "`reproducibility/reproducibility` if all experiments are done."
            )
        for r in recommendations:
            lines.append(f"- {r}")

        lines.extend(
            [
                "",
                "## How to act",
                "1. Read the recommendations above + the fresh literature.",
                "2. Pick ONE next step. Tell the researcher what you chose and why.",
                "3. Log the decision: `mem_decision_log context='next-step plan' "
                "selected=<your-pick> rationale=<short>`",
                "4. Load the matching protocol (analysis_plan, dead_end_routing,",
                "   reproducibility, synthesis_paper, …) and proceed.",
            ]
        )

        plan_path = _write_plan(root, "\n".join(lines) + "\n")

        return {
            "status": "success",
            "plan_path": plan_path,
            "recommendations": recommendations,
            "open_hypotheses": [h["id"] for h in untested],
            "literature_hits": len(lit_hits),
            "tool_hits": len(tool_hits),
        }
    except Exception as e:
        logger.exception("plan_next_step failed")
        return {"status": "error", "message": str(e)}


def branch_recommendation(root: Path, *, reason: str) -> dict[str, Any]:
    """Decide: branch into a new parallel experiment, or extend the current one.

    Use when you have a working pipeline but want to try an alternative
    methodology / model / preprocessing without abandoning the current path.
    """
    try:
        from research_os.tools.actions.state.path import list_paths

        paths = list_paths(root).get("paths", []) or []
        active = [p for p in paths if p.get("status") == "active"]
        recommendation = (
            "branch"
            if len(active) <= 2
            else "extend_current"
        )
        guidance = {
            "branch": (
                "Create a parallel experiment via `sys_path_create` with a NEW "
                "slug describing the alternative approach. The branched path "
                "becomes current_path; you can switch back later by referencing "
                "the old folder."
            ),
            "extend_current": (
                "You already have multiple active paths. Finish the current line "
                "of analysis (write conclusions.md, snapshot env) BEFORE forking "
                "again. Branching too aggressively makes synthesis harder."
            ),
        }[recommendation]
        return {
            "status": "success",
            "recommendation": recommendation,
            "reason": reason,
            "active_paths": [p["path_id"] for p in active],
            "guidance": guidance,
        }
    except Exception as e:
        logger.exception("branch_recommendation failed")
        return {"status": "error", "message": str(e)}
