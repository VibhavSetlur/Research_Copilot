#!/usr/bin/env python3
"""Execution DAG Manager — tracks script execution lineage across iterations.

Maintains a Directed Acyclic Graph (DAG) of all script executions, recording:
- Which scripts ran and in what order
- Input/output files with SHA-256 hashes
- Iteration branching (e.g., 02_analysis_ITER001.py vs 02_analysis_ITER002.py)
- Dependencies between script runs

Location: .research/cache/execution_dag.json

Usage:
    from dag_manager import ExecutionDAGManager

    dag = ExecutionDAGManager()
    dag.add_node("02_analysis_ITER001_01", "scripts/02_analysis_ITER001.py",
                 input_files=["data/01_ingested/clean.csv"],
                 output_files=["data/02_processed/analysis.csv"],
                 depends_on=["01_data_prep_01"],
                 iteration_id="001")
    dag.update_output_hashes("02_analysis_ITER001_01")
    dag.get_lineage("data/02_processed/analysis.csv")
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from research_copilot.utils.common import find_project_root


class ExecutionDAGManager:
    """Manages the execution DAG for script lineage tracking."""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = find_project_root()
        self.root = project_root
        self.dag_path = project_root / ".research" / "cache" / "execution_dag.json"
        self._ensure_dag_exists()

    def _ensure_dag_exists(self) -> None:
        if not self.dag_path.exists():
            self._init_dag()

    def _init_dag(self) -> None:
        dag = {
            "schema_version": "7.0.0",
            "project": "",
            "nodes": {},
            "edges": [],
            "branches": {},
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
        self._save(dag)

    def _load(self) -> dict:
        if self.dag_path.exists():
            with open(self.dag_path) as f:
                return json.load(f)
        self._init_dag()
        with open(self.dag_path) as f:
            return json.load(f)

    def _save(self, dag: dict) -> None:
        self.dag_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.dag_path.with_suffix(".tmp")
        with open(tmp, "w") as f:
            json.dump(dag, f, indent=2, default=str)
        tmp.replace(self.dag_path)

    @staticmethod
    def _compute_hash(file_path: Path) -> str:
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except (FileNotFoundError, PermissionError):
            return "error"

    def _current_branch(self) -> str:
        state_path = self.root / ".research" / "cache" / "state.json"
        try:
            with open(state_path) as f:
                state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return "main"
        return state.get("current_branch", state.get("active_branch", "main"))

    def add_node(
        self,
        node_id: str,
        script_path: str,
        input_files: list,
        output_files: list,
        depends_on: list = None,
        iteration_id: str = None,
        status: str = "complete",
        runtime: str = None,
        container: str = None,
        tool_ids: list = None,
        domain: str = None,
        branch_id: str = None,
        exit_code: int = None,
        duration: float = None,
    ) -> dict:
        """Add an execution node to the DAG.

        Args:
            node_id: Unique ID (format: <script_base>_<ITERATION_ID>_<run_index>)
            script_path: Relative path to the script
            input_files: List of input file paths
            output_files: List of output file paths
            depends_on: List of node_ids this depends on
            iteration_id: Iteration ID (e.g., "001", "002")
            status: Execution status
            runtime: Runtime used (python, r, bash, nextflow, snakemake, julia)
            container: Container image used
            tool_ids: Tool IDs from the tool registry
            domain: Domain context (genomics, neuroimaging, etc.)
            branch_id: Experiment branch that owns this execution
            exit_code: Process exit code
            duration: Execution duration in seconds

        Returns:
            The created node dict
        """
        dag = self._load()
        now = datetime.now(timezone.utc).isoformat()
        branch_id = branch_id or self._current_branch()

        input_hashes = {}
        for fp in input_files:
            p = self.root / fp if not Path(fp).is_absolute() else Path(fp)
            if p.exists():
                input_hashes[fp] = self._compute_hash(p)

        node = {
            "node_id": node_id,
            "script_path": script_path,
            "iteration_id": iteration_id,
            "branch_id": branch_id,
            "depends_on": depends_on or [],
            "input_files": input_files,
            "output_files": output_files,
            "status": status,
            "timestamp": now,
            "data_hash_in": input_hashes,
            "data_hash_out": {},
            "runtime": runtime,
            "container": container,
            "tool_ids": tool_ids or [],
            "domain": domain,
            "exit_code": exit_code,
            "duration_seconds": duration,
        }

        dag["nodes"][node_id] = node
        dag.setdefault("branches", {}).setdefault(branch_id, {"nodes": []})
        if node_id not in dag["branches"][branch_id]["nodes"]:
            dag["branches"][branch_id]["nodes"].append(node_id)

        for dep in (depends_on or []):
            if dep in dag["nodes"]:
                dag["edges"].append({"from": dep, "to": node_id})

        dag["last_updated"] = now
        self._save(dag)
        return node

    def update_output_hashes(self, node_id: str) -> dict:
        """Compute and store SHA-256 hashes for a node's output files."""
        dag = self._load()
        if node_id not in dag["nodes"]:
            return {}

        node = dag["nodes"][node_id]
        output_hashes = {}
        for fp in node.get("output_files", []):
            p = self.root / fp if not Path(fp).is_absolute() else Path(fp)
            if p.exists():
                output_hashes[fp] = self._compute_hash(p)

        node["data_hash_out"] = output_hashes
        dag["last_updated"] = datetime.now(timezone.utc).isoformat()
        self._save(dag)
        return output_hashes

    def get_node(self, node_id: str) -> Optional[dict]:
        """Get a specific node by ID."""
        dag = self._load()
        return dag["nodes"].get(node_id)

    def get_lineage(self, file_path: str) -> list:
        """Get the full lineage (all nodes that produced or consumed a file)."""
        dag = self._load()
        lineage = []

        for node_id, node in dag["nodes"].items():
            if file_path in node.get("input_files", []) or file_path in node.get("output_files", []):
                lineage.append(node)

        return sorted(lineage, key=lambda n: n["timestamp"])

    def get_upstream(self, node_id: str) -> list:
        """Get all upstream dependencies of a node (recursive)."""
        dag = self._load()
        visited = set()
        result = []

        def _traverse(nid: str):
            if nid in visited:
                return
            visited.add(nid)
            node = dag["nodes"].get(nid)
            if node:
                for dep in node.get("depends_on", []):
                    _traverse(dep)
                result.append(node)

        _traverse(node_id)
        return result

    def get_downstream(self, node_id: str) -> list:
        """Get all nodes that depend on a given node (recursive)."""
        dag = self._load()
        visited = set()
        result = []

        def _traverse(nid: str):
            if nid in visited:
                return
            visited.add(nid)
            for edge in dag["edges"]:
                if edge["from"] == nid:
                    child_id = edge["to"]
                    child = dag["nodes"].get(child_id)
                    if child:
                        _traverse(child_id)
                        result.append(child)

        _traverse(node_id)
        return result

    def get_iteration_branches(self, base_script: str) -> dict:
        """Get all iteration branches for a base script.

        Args:
            base_script: Base script name without iteration suffix
                         (e.g., "02_analysis" to find "02_analysis_ITER001", etc.)

        Returns:
            Dict mapping iteration_id to list of nodes
        """
        dag = self._load()
        branches = {}

        for node_id, node in dag["nodes"].items():
            if base_script in node.get("script_path", ""):
                iter_id = node.get("iteration_id", "base")
                branches.setdefault(iter_id, []).append(node)

        return branches

    def validate_reproducibility(self, node_id: str) -> dict:
        """Check if a node's outputs can be reproduced from its inputs.

        Compares current input hashes against recorded hashes.
        If inputs haven't changed, outputs should be reproducible.

        Returns:
            Dict with reproducibility status and details
        """
        dag = self._load()
        node = dag["nodes"].get(node_id)
        if not node:
            return {"status": "error", "message": f"Node {node_id} not found"}

        input_changed = False
        changes = []

        for fp, recorded_hash in node.get("data_hash_in", {}).items():
            p = self.root / fp if not Path(fp).is_absolute() else Path(fp)
            if not p.exists():
                changes.append({"file": fp, "status": "missing"})
                input_changed = True
            else:
                current_hash = self._compute_hash(p)
                if current_hash != recorded_hash:
                    changes.append({
                        "file": fp,
                        "status": "changed",
                        "recorded_hash": recorded_hash[:8],
                        "current_hash": current_hash[:8],
                    })
                    input_changed = True

        return {
            "node_id": node_id,
            "reproducible": not input_changed,
            "input_changed": input_changed,
            "changes": changes,
            "script": node["script_path"],
            "timestamp": node["timestamp"],
        }

    def summary(self) -> str:
        """Print a human-readable summary of the DAG."""
        dag = self._load()
        nodes = dag.get("nodes", {})
        edges = dag.get("edges", [])

        lines = [
            "=" * 60,
            "EXECUTION DAG SUMMARY",
            "=" * 60,
            f"  Project: {dag.get('project', 'N/A')}",
            f"  Nodes: {len(nodes)}",
            f"  Edges: {len(edges)}",
            f"  Last Updated: {dag.get('last_updated', 'N/A')}",
            "",
        ]

        iterations = {}
        runtimes = {}
        containers = {}
        tools_used = set()
        for node_id, node in nodes.items():
            iter_id = node.get("iteration_id", "base")
            iterations.setdefault(iter_id, []).append(node)
            rt = node.get("runtime", "unknown")
            runtimes[rt] = runtimes.get(rt, 0) + 1
            ct = node.get("container") or "none"
            containers[ct] = containers.get(ct, 0) + 1
            for tid in node.get("tool_ids", []):
                tools_used.add(tid)

        if iterations:
            lines.append("  Iterations:")
            for iter_id, iter_nodes in sorted(iterations.items()):
                lines.append(f"    Iteration {iter_id}: {len(iter_nodes)} node(s)")
                for n in iter_nodes:
                    status_marker = "+" if n["status"] == "complete" else "x"
                    rt = n.get("runtime", "?")
                    ct = n.get("container") or "local"
                    tools = ", ".join(n.get("tool_ids", [])) or "-"
                    lines.append(f"      {status_marker} {n['script_path']}")
                    lines.append(f"         runtime={rt} container={ct} tools=[{tools}]")
                lines.append("")

        branches = {}
        for node in nodes.values():
            branches.setdefault(node.get("branch_id", "main"), 0)
            branches[node.get("branch_id", "main")] += 1
        if branches:
            lines.append("  Branches:")
            for branch_id, count in sorted(branches.items()):
                lines.append(f"    {branch_id}: {count} node(s)")
            lines.append("")

        if runtimes:
            lines.append("  Runtimes:")
            for rt, count in sorted(runtimes.items()):
                lines.append(f"    {rt}: {count}")
            lines.append("")

        if containers:
            lines.append("  Containers:")
            for ct, count in sorted(containers.items()):
                lines.append(f"    {ct}: {count}")
            lines.append("")

        if tools_used:
            lines.append(f"  Tools used: {', '.join(sorted(tools_used))}")
            lines.append("")

        return "\n".join(lines)

    def merge_branch_lineage(self, branch_id: str, target_branch: str = "main") -> None:
        """Merge a branch's nodes into another branch (typically main trunk)."""
        dag = self._load()
        if branch_id not in dag.get("branches", {}):
            return

        branch_nodes = dag["branches"][branch_id].get("nodes", [])
        dag.setdefault("branches", {}).setdefault(target_branch, {"nodes": []})
        
        for nid in branch_nodes:
            if nid not in dag["branches"][target_branch]["nodes"]:
                dag["branches"][target_branch]["nodes"].append(nid)
                if nid in dag["nodes"]:
                    dag["nodes"][nid]["branch_id"] = target_branch

        dag["last_updated"] = datetime.now(timezone.utc).isoformat()
        self._save(dag)


if __name__ == "__main__":
    dag = ExecutionDAGManager()
    print(dag.summary())
