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
    """Only protocol.py + __init__.py should live at tools/actions/."""
    actions_dir = REPO_ROOT / "src" / "research_os" / "tools" / "actions"
    flat = sorted(
        f.name for f in actions_dir.iterdir()
        if f.is_file() and f.suffix == ".py"
    )
    expected = {"__init__.py", "protocol.py"}
    return set(flat) == expected, f"{flat}"


def check_every_protocol_loads():
    import yaml

    from research_os.tools.actions.protocol import load_protocol

    bad: list[str] = []
    count = 0
    for f in sorted(PROTOCOLS_DIR.rglob("*.yaml")):
        if "light" in f.parts:
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

    known = set(TOOL_DEFINITIONS) | set(_ALIASES)
    # Add known false positives that aren't tool calls
    false_positive_strings = {
        "tool_name",        # field inside tool_external_tool_instructions
        "tool_discovery",   # protocol name (methodology/tool_discovery)
        "tool_list",        # word appearing in prose ("tool list")
    }
    refs: dict[str, set[str]] = {}
    pattern = re.compile(r"\b((?:sys|tool|mem)_[a-z_]+)\b")
    for f in PROTOCOLS_DIR.rglob("*.yaml"):
        if "light" in f.parts:
            continue
        text = f.read_text()
        for m in pattern.finditer(text):
            name = m.group(1)
            if name in false_positive_strings:
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
