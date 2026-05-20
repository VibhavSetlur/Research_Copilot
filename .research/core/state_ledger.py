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
            "context_transfer_memos": [],
            "execution_dag_path": None,
            "data_scale_profile": None,
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

    def save_ctm(self, ctm_data: dict) -> dict:
        """Save a Context Transfer Memorandum to state and write to disk.

        CTMs are generated at 90% token budget to preserve latent context
        that cannot be transferred via structured state alone.

        Args:
            ctm_data: Dict with keys: phase, token_usage_pct, abandoned_paths,
                      micro_decisions, immediate_goals, partial_results,
                      open_questions, state_file_refs, handoff_notes

        Returns:
            Updated state dict
        """
        state = self._load()
        now = datetime.now(timezone.utc)

        ctm = {
            "ctm_id": f"ctm_{now.strftime('%Y%m%d_%H%M%S')}",
            "phase": ctm_data.get("phase", state.get("phase", "unknown")),
            "token_usage_pct": ctm_data.get("token_usage_pct", 0.9),
            "generated_at": now.isoformat(),
            "abandoned_paths": ctm_data.get("abandoned_paths", []),
            "micro_decisions": ctm_data.get("micro_decisions", []),
            "immediate_goals": ctm_data.get("immediate_goals", []),
            "partial_results": ctm_data.get("partial_results", []),
            "open_questions": ctm_data.get("open_questions", []),
            "state_file_refs": ctm_data.get("state_file_refs", []),
            "handoff_notes": ctm_data.get("handoff_notes", ""),
        }

        state.setdefault("context_transfer_memos", []).append(ctm)
        state["updated_at"] = now.isoformat()
        self._save(state)

        ctm_dir = self._path.parent / "context_transfer_memos"
        ctm_dir.mkdir(parents=True, exist_ok=True)
        ctm_path = ctm_dir / f"{ctm['ctm_id']}.json"
        self._save_to_path(ctm_path, ctm)

        return state

    def get_latest_ctm(self) -> Optional[dict]:
        """Retrieve the most recent Context Transfer Memorandum."""
        state = self._load()
        memos = state.get("context_transfer_memos", [])
        if memos:
            return memos[-1]
        return None

    def get_all_ctms(self) -> list:
        """Retrieve all Context Transfer Memoranda."""
        state = self._load()
        return state.get("context_transfer_memos", [])

    def get_dag_path(self) -> Path:
        """Get or create the execution DAG file path."""
        state = self._load()
        dag_path_str = state.get("execution_dag_path")
        if dag_path_str:
            return Path(dag_path_str)

        dag_path = self._path.parent / "execution_dag.json"
        state["execution_dag_path"] = str(dag_path)
        self._save(state)

        if not dag_path.exists():
            self._init_dag(dag_path)

        return dag_path

    def _init_dag(self, dag_path: Path) -> None:
        """Initialize a new execution DAG file."""
        state = self._load()
        dag = {
            "schema_version": "7.0.0",
            "project": state.get("project", ""),
            "nodes": {},
            "edges": [],
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
        self._save_to_path(dag_path, dag)

    def _save_to_path(self, path: Path, data: dict) -> None:
        """Save data to a specific path atomically."""
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(data, f, indent=2, default=str)
            os.replace(tmp_path, str(path))
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    def add_dag_node(self, node_id: str, script_path: str, input_files: list,
                     output_files: list, depends_on: list = None,
                     iteration_id: str = None, status: str = "complete") -> dict:
        """Add a node to the execution DAG.

        Args:
            node_id: Unique node ID (format: <script_name>_<iteration_id>_<run_index>)
            script_path: Path to the executed script
            input_files: List of input data files consumed
            output_files: List of output files produced
            depends_on: List of node_ids this execution depends on
            iteration_id: Iteration ID if part of an iteration
            status: Execution status (pending, running, complete, failed)

        Returns:
            Updated state dict
        """
        dag_path = self.get_dag_path()

        if not dag_path.exists():
            self._init_dag(dag_path)

        with open(dag_path) as f:
            dag = json.load(f)

        now = datetime.now(timezone.utc).isoformat()

        input_hashes = {}
        for fp in input_files:
            p = Path(fp)
            if p.exists():
                input_hashes[fp] = self._compute_file_hash(p)

        node = {
            "node_id": node_id,
            "script_path": script_path,
            "iteration_id": iteration_id,
            "depends_on": depends_on or [],
            "input_files": input_files,
            "output_files": output_files,
            "status": status,
            "timestamp": now,
            "data_hash_in": input_hashes,
            "data_hash_out": {},
        }

        dag["nodes"][node_id] = node

        for dep in (depends_on or []):
            if dep in dag["nodes"]:
                dag["edges"].append({"from": dep, "to": node_id})

        dag["last_updated"] = now
        self._save_to_path(dag_path, dag)

        state = self._load()
        state["execution_dag_path"] = str(dag_path)
        state["updated_at"] = now
        self._save(state)

        return state

    def update_dag_node_output_hashes(self, node_id: str) -> dict:
        """Compute and store SHA-256 hashes for a node's output files."""
        dag_path = self.get_dag_path()
        if not dag_path.exists():
            return self._load()

        with open(dag_path) as f:
            dag = json.load(f)

        if node_id not in dag["nodes"]:
            return self._load()

        node = dag["nodes"][node_id]
        output_hashes = {}
        for fp in node.get("output_files", []):
            p = Path(fp)
            if p.exists():
                output_hashes[fp] = self._compute_file_hash(p)

        node["data_hash_out"] = output_hashes
        dag["last_updated"] = datetime.now(timezone.utc).isoformat()
        self._save_to_path(dag_path, dag)

        return self._load()

    def get_dag(self) -> dict:
        """Load and return the full execution DAG."""
        dag_path = self.get_dag_path()
        if not dag_path.exists():
            self._init_dag(dag_path)
        with open(dag_path) as f:
            return json.load(f)

    @staticmethod
    def _compute_file_hash(file_path: Path) -> str:
        """Compute SHA-256 hash of a file."""
        import hashlib
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except (FileNotFoundError, PermissionError):
            return "error"

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
