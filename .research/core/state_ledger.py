#!/usr/bin/env python3
"""Global Research Ledger — atomic state management for the research pipeline.

Single source of truth for every pipeline run. Replaces fragmented
manifest/registry/log files with one authoritative object.

Location: .research/cache/state.json
"""

import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


class ResearchLedger:
    """Thread-safe, atomic research state ledger."""

    def __init__(self, state_path: Optional[Path] = None):
        if state_path is None:
            root = self._find_project_root()
            state_path = root / ".research" / "cache" / "state.json"
        self._path = Path(state_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _find_project_root() -> Path:
        p = Path.cwd()
        for _ in range(10):
            if (p / ".research").exists():
                return p
            if p.parent == p:
                break
            p = p.parent
        return Path.cwd()

    def _load(self) -> dict:
        if self._path.exists():
            with open(self._path) as f:
                return json.load(f)
        return self._default_state()

    def _save(self, data: dict) -> None:
        """Atomic write: write to temp file, then rename to avoid corruption."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(
            dir=str(self._path.parent), suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(data, f, indent=2, default=str)
            os.replace(tmp_path, str(self._path))
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    @staticmethod
    def _default_state() -> dict:
        return {
            "run_id": str(uuid.uuid4()),
            "project": "",
            "phase": "research_init",
            "step": 0,
            "checkpoints": {},
            "active_hypotheses": [],
            "dead_ends": [],
            "loaded_data": [],
            "token_budget": {"used": 0, "remaining": 200000, "limit": 200000},
            "last_checkpoint": datetime.now(timezone.utc).isoformat(),
            "errors": [],
            "resumable_from": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _run_pre_commit_hooks(self, state: dict, action: str, **kwargs) -> dict:
        """Run pre_ledger_commit hooks synchronously via trigger_sync().

        No nest_asyncio needed — hooks.py handles async/sync normalization.
        """
        try:
            from hooks import hook_engine
            import interceptors  # noqa: F401 — registers interceptors
        except ImportError:
            try:
                from .hooks import hook_engine
                from . import interceptors  # noqa: F401
            except ImportError:
                return state

        return hook_engine.trigger_sync(
            "pre_ledger_commit", state, action=action, **kwargs
        )

    def get(self) -> dict:
        return self._load()

    def update(self, **kwargs) -> dict:
        state = self._load()
        state.update(kwargs)
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        state = self._run_pre_commit_hooks(state, "update", **kwargs)
        self._save(state)
        return state

    def set_phase(self, phase: str, step: int = 0) -> dict:
        state = self._load()
        state["phase"] = phase
        state["step"] = step
        state["checkpoints"][phase] = "in_progress"
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save(state)
        return state

    def complete_phase(self, phase: str) -> dict:
        state = self._load()
        state["checkpoints"][phase] = "complete"
        state["resumable_from"] = phase
        state["last_checkpoint"] = datetime.now(timezone.utc).isoformat()
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        state = self._run_pre_commit_hooks(state, "complete_phase", phase=phase)
        self._save(state)
        return state

    def add_hypothesis(self, hypothesis_id: str, status: str = "testing", effect: Optional[float] = None) -> dict:
        state = self._load()
        hypotheses = state.get("active_hypotheses", [])
        for h in hypotheses:
            if h["id"] == hypothesis_id:
                h["status"] = status
                if effect is not None:
                    h["effect"] = effect
                state["updated_at"] = datetime.now(timezone.utc).isoformat()
                self._save(state)
                return state
        hypotheses.append({"id": hypothesis_id, "status": status, "effect": effect})
        state["active_hypotheses"] = hypotheses
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save(state)
        return state

    def add_dead_end(self, approach: str) -> dict:
        state = self._load()
        if approach not in state.get("dead_ends", []):
            state.setdefault("dead_ends", []).append(approach)
            state["updated_at"] = datetime.now(timezone.utc).isoformat()
            self._save(state)
        return state

    def add_error(self, error: str) -> dict:
        state = self._load()
        state.setdefault("errors", []).append({
            "message": error,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save(state)
        return state

    def track_tokens(self, used: int, limit: Optional[int] = None) -> dict:
        state = self._load()
        budget = state.get("token_budget", {"used": 0, "remaining": 200000, "limit": 200000})
        if limit is not None:
            budget["limit"] = limit
        budget["used"] = used
        budget["remaining"] = max(0, budget["limit"] - used)
        state["token_budget"] = budget
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save(state)
        return state

    def add_loaded_data(self, data_path: str) -> dict:
        state = self._load()
        if data_path not in state.get("loaded_data", []):
            state.setdefault("loaded_data", []).append(data_path)
            state["updated_at"] = datetime.now(timezone.utc).isoformat()
            self._save(state)
        return state

    def summary(self) -> str:
        state = self._load()
        lines = [
            "=" * 60,
            "GLOBAL RESEARCH LEDGER",
            "=" * 60,
            "",
            f"  Run ID:      {state.get('run_id', 'N/A')}",
            f"  Project:     {state.get('project', 'N/A')}",
            f"  Phase:       {state.get('phase', 'N/A')} (step {state.get('step', 0)})",
            f"  Created:     {state.get('created_at', 'N/A')}",
            f"  Updated:     {state.get('updated_at', 'N/A')}",
            "",
            "  Checkpoints:",
        ]
        for phase, status in state.get("checkpoints", {}).items():
            marker = "✓" if status == "complete" else "○"
            lines.append(f"    {marker} {phase}: {status}")
        if not state.get("checkpoints"):
            lines.append("    (none yet)")

        lines.append("")
        lines.append(f"  Hypotheses: {len(state.get('active_hypotheses', []))}")
        for h in state.get("active_hypotheses", []):
            eff = f", effect={h['effect']}" if h.get("effect") is not None else ""
            lines.append(f"    - {h['id']}: {h['status']}{eff}")

        lines.append("")
        lines.append(f"  Dead ends: {len(state.get('dead_ends', []))}")
        for d in state.get("dead_ends", []):
            lines.append(f"    - {d}")

        lines.append("")
        lines.append(f"  Loaded data: {len(state.get('loaded_data', []))} file(s)")
        for d in state.get("loaded_data", []):
            lines.append(f"    - {d}")

        budget = state.get("token_budget", {})
        lines.append("")
        lines.append("  Token Budget:")
        lines.append(f"    Used:      {budget.get('used', 0):,}")
        lines.append(f"    Remaining: {budget.get('remaining', 0):,}")
        lines.append(f"    Limit:     {budget.get('limit', 0):,}")

        errors = state.get("errors", [])
        lines.append("")
        lines.append(f"  Errors: {len(errors)}")
        for e in errors[-5:]:
            lines.append(f"    - [{e.get('timestamp', '')}] {e.get('message', '')}")
        if len(errors) > 5:
            lines.append(f"    ... and {len(errors) - 5} more")

        lines.append("")
        lines.append(f"  Resumable from: {state.get('resumable_from', 'none')}")
        lines.append("")
        return "\n".join(lines)
