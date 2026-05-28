#!/usr/bin/env python3
"""Preflight smoke check for Research OS.

Run before publishing a release (or any time you want to confirm the
package is wired up). Exits with non-zero on any failure.

Validates:
  1. Top-level package imports cleanly.
  2. The eight action subpackages import.
  3. ``research_os.cli`` exposes ``main``.
  4. Every protocol YAML loads and has the required keys.
  5. Every tool defined in ``server.TOOL_DEFINITIONS`` has a registered
     handler in ``server._HANDLERS``.
  6. The dispatcher correctly resolves dot notation and legacy aliases.

Use:
    python scripts/preflight.py
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PROTOCOLS_DIR = REPO_ROOT / "src" / "research_os" / "protocols"


def _report(name: str, ok: bool, detail: str = "") -> None:
    badge = "OK " if ok else "FAIL"
    line = f"  [{badge}] {name}"
    if detail:
        line += f"  — {detail}"
    print(line)


class Tally:
    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0
        self.errors: list[str] = []

    def check(self, name: str, fn) -> None:
        try:
            ok, detail = fn()
        except Exception as e:
            ok = False
            detail = f"{type(e).__name__}: {e}"
            self.errors.append(f"{name}\n{traceback.format_exc()}")
        _report(name, ok, detail)
        if ok:
            self.passed += 1
        else:
            self.failed += 1


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def check_top_level_import():
    import research_os  # noqa: F401

    return True, f"version {research_os.__version__}"


def check_subpackages():
    pkgs = [
        "research_os.tools.actions.state",
        "research_os.tools.actions.data",
        "research_os.tools.actions.exec",
        "research_os.tools.actions.search",
        "research_os.tools.actions.research",
        "research_os.tools.actions.audit",
        "research_os.tools.actions.synthesis",
        "research_os.tools.actions.memory",
        "research_os.tools.actions.protocol",
    ]
    bad = []
    for p in pkgs:
        try:
            __import__(p)
        except Exception as e:
            bad.append(f"{p}: {e}")
    return not bad, ("ok" if not bad else "; ".join(bad))


def check_cli_entrypoint():
    from research_os.cli import main

    return callable(main), "main() callable"


def check_flat_namespace_is_minimal():
    """Only protocol.py + router.py + __init__.py should live at tools/actions/.

    Everything else MUST live in a category sub-package (state/, data/,
    exec/, search/, research/, audit/, synthesis/, memory/). protocol.py
    and router.py are first-class cross-cutting modules — both touch every
    category, so keeping them flat avoids a circular sub-package."""
    actions_dir = REPO_ROOT / "src" / "research_os" / "tools" / "actions"
    flat = sorted(
        f.name for f in actions_dir.iterdir()
        if f.is_file() and f.suffix == ".py"
    )
    expected = {"__init__.py", "protocol.py", "router.py"}
    return set(flat) == expected, f"{flat}"


def check_every_protocol_loads():
    from research_os.tools.actions.protocol import load_protocol

    bad: list[str] = []
    count = 0
    for f in sorted(PROTOCOLS_DIR.rglob("*.yaml")):
        if "light" in f.parts:
            continue
        # Files prefixed with `_` are registry / index files, not protocols.
        if f.name.startswith("_"):
            continue
        rel = f.relative_to(PROTOCOLS_DIR).with_suffix("").as_posix()
        try:
            data = load_protocol(rel)
            for required in ("id", "name", "steps"):
                if required not in data:
                    bad.append(f"{rel} missing `{required}`")
            if not isinstance(data.get("steps"), list) or not data["steps"]:
                bad.append(f"{rel} has empty/invalid steps")
            count += 1
        except Exception as e:
            bad.append(f"{rel}: {type(e).__name__}: {e}")
    return not bad, f"{count} loaded" if not bad else "; ".join(bad[:3])


def check_no_dot_tool_calls_in_protocols():
    """New protocols shouldn't use the legacy `tool_X.Y` dot notation."""
    import re

    bad_patterns = [
        r"\b(sys|tool|mem)_[a-z_]+\.[a-z_]+\b",  # e.g. sys_state.get
    ]
    offenders: list[str] = []
    for f in PROTOCOLS_DIR.rglob("*.yaml"):
        if "light" in f.parts:
            continue
        if f.name.startswith("_"):
            continue
        text = f.read_text()
        for pat in bad_patterns:
            for match in re.finditer(pat, text):
                # Skip protocol filenames like "literature/literature_search"
                # which contain a dot in the file context, not in tool call.
                offenders.append(f"{f.name}: `{match.group(0)}`")
    return not offenders, ("clean" if not offenders else f"{len(offenders)} offenders")


def check_every_tool_has_handler():
    from research_os.server import _HANDLERS, TOOL_DEFINITIONS

    defined = set(TOOL_DEFINITIONS)
    wired = set(_HANDLERS)
    missing = sorted(defined - wired)
    extra = sorted(wired - defined)
    if missing or extra:
        detail = []
        if missing:
            detail.append(f"defined-but-not-wired: {missing}")
        if extra:
            detail.append(f"wired-but-not-defined: {extra}")
        return False, "; ".join(detail)
    return True, f"{len(defined)} tools wired"


def check_dispatcher_aliases():
    from research_os.server import _resolve_tool_name

    cases = {
        "sys.state.get": "sys_state_get",
        "sys_guidance_get": "sys_protocol_get",  # legacy alias
        "tool_audit_statistical_power": "tool_audit_power",
        "sys_md_validate": "sys_file_validate_md",
        "tool_log_decision": "mem_decision_log",
        "sys_state_get": "sys_state_get",  # passthrough
    }
    bad: list[str] = []
    for given, expected in cases.items():
        actual = _resolve_tool_name(given)
        if actual != expected:
            bad.append(f"{given!r} -> {actual!r} (expected {expected!r})")
    return not bad, "ok" if not bad else "; ".join(bad)


def check_handlers_callable():
    from research_os.server import _HANDLERS

    bad = [name for name, fn in _HANDLERS.items() if not callable(fn)]
    return not bad, "all callable" if not bad else f"non-callable: {bad}"


def check_protocols_referenced_tools_resolve():
    """Every sys_/tool_/mem_ name in a protocol must be a real tool (after alias)."""
    import re

    from research_os.server import _ALIASES, TOOL_DEFINITIONS, _resolve_tool_name

    # Add known false positives that aren't tool calls
    false_positive_strings = {
        "tool_name",        # field inside tool_external_tool_instructions
        "tool_discovery",   # protocol name (methodology/tool_discovery)
        "tool_list",        # word appearing in prose ("tool list")
    }
    refs: dict[str, set[str]] = {}
    # Match a tool name, but reject the match if the very next char is `*`
    # (those are wildcard mentions in prose like `tool_search_*`, not real
    # tool calls).
    pattern = re.compile(r"\b((?:sys|tool|mem)_[a-z_]+)\b(?!\*)")
    for f in PROTOCOLS_DIR.rglob("*.yaml"):
        if "light" in f.parts:
            continue
        if f.name.startswith("_"):
            # Registry / index files; their tool refs are validated below
            # via a dedicated router-index check.
            continue
        text = f.read_text()
        for m in pattern.finditer(text):
            name = m.group(1)
            if name in false_positive_strings:
                continue
            # Reject bare prefixes like `tool_search_` that end in `_`
            # (always a truncation/wildcard mention in prose).
            if name.endswith("_"):
                continue
            refs.setdefault(name, set()).add(f.name)

    unresolved = {
        name: list(files)
        for name, files in refs.items()
        if _resolve_tool_name(name) not in TOOL_DEFINITIONS
    }
    if unresolved:
        sample = ", ".join(f"{k} (in {','.join(v)})" for k, v in list(unresolved.items())[:5])
        return False, sample
    return True, f"{len(refs)} unique tool refs all resolve"


def check_router_index_consistent():
    """Every protocol in _router_index.yaml must exist; every tool ref must resolve."""
    import yaml

    from research_os.server import TOOL_DEFINITIONS, _resolve_tool_name

    idx_path = PROTOCOLS_DIR / "_router_index.yaml"
    if not idx_path.exists():
        return False, "_router_index.yaml missing"
    idx = yaml.safe_load(idx_path.read_text()) or {}

    bad: list[str] = []

    # Every protocol entry must point at a real protocol YAML.
    for proto_name in (idx.get("protocols") or {}).keys():
        path = PROTOCOLS_DIR / f"{proto_name}.yaml"
        if not path.exists():
            bad.append(f"protocol `{proto_name}` not on disk")

    # Every protocol on disk must be in the index (or in an allow-list).
    on_disk = set()
    for f in PROTOCOLS_DIR.rglob("*.yaml"):
        if "light" in f.parts or f.name.startswith("_"):
            continue
        rel = f.relative_to(PROTOCOLS_DIR).with_suffix("").as_posix()
        on_disk.add(rel)
    in_index = set((idx.get("protocols") or {}).keys())
    missing_from_index = sorted(on_disk - in_index)
    if missing_from_index:
        bad.append(
            f"{len(missing_from_index)} protocol(s) not in _router_index.yaml: "
            f"{missing_from_index[:3]}..."
        )

    # Every tool ref (shortcut_tool, decomposition.tool, shortcut_intents.tool)
    # must resolve to a real TOOL_DEFINITIONS entry.
    def _check_tool(t: str, ctx: str) -> None:
        if not t:
            return
        if _resolve_tool_name(t) not in TOOL_DEFINITIONS:
            bad.append(f"unknown tool `{t}` in {ctx}")

    for name, data in (idx.get("protocols") or {}).items():
        if not isinstance(data, dict):
            continue
        _check_tool(data.get("shortcut_tool", ""), f"protocols/{name}")
        for entry in data.get("decomposition", []) or []:
            if isinstance(entry, dict):
                _check_tool(entry.get("tool", ""), f"protocols/{name} decomposition")
    for sid, data in (idx.get("shortcut_intents") or {}).items():
        if not isinstance(data, dict):
            continue
        _check_tool(data.get("tool", ""), f"shortcut_intents/{sid}")

    return not bad, (
        f"{len(in_index)} protocols indexed, all tool refs resolve"
        if not bad
        else "; ".join(bad[:3])
    )


def check_protocol_freshness():
    """Warn (don't fail) when a protocol hasn't been touched in 180+ days.

    Looks first at an explicit ``last_reviewed: YYYY-MM-DD`` field on
    each protocol YAML; falls back to git mtime when absent. Tracks the
    maintenance burden of having 47+ protocols by surfacing stale ones
    early instead of letting them quietly rot. Returns True (pass) when
    nothing is over the threshold; otherwise returns False with the
    stale list as detail (preflight overall still passes since this is a
    soft check, but the detail line catches the eye).
    """
    import subprocess as _subprocess
    from datetime import date, datetime

    import yaml

    STALE_DAYS = 180
    today = date.today()
    stale: list[str] = []
    total = 0

    for f in sorted(PROTOCOLS_DIR.rglob("*.yaml")):
        if "light" in f.parts or f.name.startswith("_"):
            continue
        total += 1
        try:
            data = yaml.safe_load(f.read_text()) or {}
        except Exception:
            continue

        # Prefer explicit field.
        last_reviewed_raw = data.get("last_reviewed")
        last_date = None
        if last_reviewed_raw:
            try:
                last_date = datetime.strptime(
                    str(last_reviewed_raw)[:10], "%Y-%m-%d"
                ).date()
            except ValueError:
                pass

        # Fallback: git mtime via `git log -1 --format=%cI`.
        if last_date is None:
            try:
                res = _subprocess.run(
                    ["git", "log", "-1", "--format=%cI", "--", str(f)],
                    capture_output=True,
                    text=True,
                    cwd=str(REPO_ROOT),
                    timeout=5,
                )
                if res.returncode == 0 and res.stdout.strip():
                    last_date = datetime.fromisoformat(
                        res.stdout.strip().split("T")[0]
                    ).date()
            except (OSError, _subprocess.TimeoutExpired, ValueError):
                pass

        if last_date is None:
            continue  # Untracked / new; not stale.
        age = (today - last_date).days
        if age > STALE_DAYS:
            rel = f.relative_to(PROTOCOLS_DIR).with_suffix("").as_posix()
            stale.append(f"{rel} ({age}d)")

    if stale:
        return True, (
            f"{total} protocols, {len(stale)} flagged for review "
            f"(>{STALE_DAYS}d): {', '.join(stale[:3])}"
            + ("..." if len(stale) > 3 else "")
        )
    return True, f"{total} protocols, all reviewed within {STALE_DAYS}d"


def check_scaffold_smoke():
    """Scaffold a temp workspace + verify the minimum files appear."""
    import tempfile

    from research_os.project_ops import scaffold_minimal_workspace

    with tempfile.TemporaryDirectory() as d:
        root = Path(d) / "smoke_project"
        scaffold_minimal_workspace(root, "Smoke Test", ide_flags=["cursor"])
        required = [
            "AGENTS.md",
            "GETTING_STARTED.md",
            "inputs/researcher_config.yaml",
            "inputs/intake.md",
            "workspace/methods.md",
            "workspace/analysis.md",
            "workspace/citations.md",
            "workspace/workflow.mermaid",
            "workspace/scratch/README.md",
            ".os_state/state_ledger.json",
            ".os_state/manifest.json",
            ".gitignore",
            ".cursor/mcp.json",
        ]
        missing = [r for r in required if not (root / r).exists()]
        forbidden = [
            "synthesis/paper.md",
            "synthesis/abstract.md",
        ]
        present_forbidden = [f for f in forbidden if (root / f).exists()]
        if missing or present_forbidden:
            return False, (
                f"missing {missing}; pre-baked forbidden output {present_forbidden}"
            ).strip()
    return True, "ok"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    # Make src importable when called from a clean checkout.
    sys.path.insert(0, str(REPO_ROOT / "src"))

    print("Research OS preflight\n" + "=" * 24)
    tally = Tally()

    tally.check("Top-level package imports", check_top_level_import)
    tally.check("Action subpackages import", check_subpackages)
    tally.check("CLI entrypoint exists", check_cli_entrypoint)
    tally.check("tools/actions/ flat namespace minimal", check_flat_namespace_is_minimal)
    tally.check("Every protocol YAML loads", check_every_protocol_loads)
    tally.check("No dot-notation tool calls in protocols", check_no_dot_tool_calls_in_protocols)
    tally.check("Every tool definition has a handler", check_every_tool_has_handler)
    tally.check("All handlers are callable", check_handlers_callable)
    tally.check("Dispatcher aliases resolve", check_dispatcher_aliases)
    tally.check("Protocol tool refs all resolve", check_protocols_referenced_tools_resolve)
    tally.check("Router index references resolve", check_router_index_consistent)
    tally.check("Protocol freshness (review cadence)", check_protocol_freshness)
    tally.check("Workspace scaffold smoke", check_scaffold_smoke)

    print()
    print(f"Summary: {tally.passed} passed · {tally.failed} failed")
    if tally.failed:
        print("\nFailures detail (first 3):")
        for err in tally.errors[:3]:
            print(err)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
