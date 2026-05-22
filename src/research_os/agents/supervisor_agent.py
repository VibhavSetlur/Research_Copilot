"""Stateless PlanExecutor — validates and runs a plan DAG received from the IDE.

The IDE (the brain) owns all decision-making.  This is a pure executor:
it accepts a concrete, fully-specified plan and returns structured results.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from research_os.state.state_ledger import ResearchLedger

logger = logging.getLogger("research.plan_executor")


class PlanExecutor:
    """Stateless executor that validates and runs a plan DAG received from the IDE.

    No autonomous decision-making.  No LLM calls.  No iteration limits.
    The IDE drives the loop; this merely executes each node in dependency order.
    """

    def __init__(self, root: Path, ledger: ResearchLedger):
        self.root = root
        self.ledger = ledger

    def execute_plan(self, plan_dag: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute a concrete plan DAG and return structured results per node.

        Each node definition:

        .. code-block:: json

            {
                "node_id": "01_load_data",
                "script": "import pandas as pd; df = pd.read_csv(...)",
                "task_name": "data_load",
                "depends_on": [],
                "timeout": 300,
                "input_files": ["inputs/raw_data/survey.csv"],
                "output_files": ["workspace/data/derived/clean.csv"]
            }

        Args:
            plan_dag: Topologically-sorted list of node definitions.

        Returns:
            List of result dicts (one per node) with structure:
                node_id, status, output, paths, checksums, duration_seconds
        """
        self._validate_plan_structure(plan_dag)
        resolved = self._topological_sort(plan_dag)

        results: List[Dict[str, Any]] = []
        node_outputs: Dict[str, Any] = {}

        from research_os.engine import ResearchEngine
        engine = ResearchEngine(self.root)

        for node_id in resolved:
            node = self._find_node(plan_dag, node_id)
            if node is None:
                results.append(self._error(node_id, "Node not found in plan"))
                continue

            upstream_outputs = {
                dep: node_outputs.get(dep, {})
                for dep in node.get("depends_on", [])
            }

            try:
                result = engine.execute_node(
                    node_id=node_id,
                    script=node.get("script"),
                    task_name=node.get("task_name"),
                    timeout=node.get("timeout"),
                    input_files=node.get("input_files"),
                    output_files=node.get("output_files"),
                    **node.get("extra_params", {}),
                )
                result = self._enrich_with_paths_and_checksums(result, node)
                node_outputs[node_id] = result
                results.append(result)
            except Exception as e:
                logger.error("Node %s failed: %s", node_id, e)
                entry = self._error(node_id, str(e))
                node_outputs[node_id] = entry
                results.append(entry)

        return results

    def validate_plan_structure(self, plan_dag: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate plan structure without executing.  Returns validation report."""
        try:
            self._validate_plan_structure(plan_dag)
            self._topological_sort(plan_dag)
            return {"valid": True, "errors": []}
        except ValueError as e:
            return {"valid": False, "errors": [str(e)]}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate_plan_structure(self, plan_dag: List[Dict[str, Any]]) -> None:
        if not isinstance(plan_dag, list):
            raise ValueError("Plan DAG must be a list of node definitions")
        ids: set = set()
        for node in plan_dag:
            nid = node.get("node_id")
            if not nid:
                raise ValueError(f"Node missing 'node_id': {node}")
            if nid in ids:
                raise ValueError(f"Duplicate node_id: {nid}")
            ids.add(nid)

    def _topological_sort(self, plan_dag: List[Dict[str, Any]]) -> List[str]:
        node_map = {n["node_id"]: n for n in plan_dag}
        visited: set = set()
        resolved: list = []

        def visit(nid: str, path: set) -> None:
            if nid in path:
                raise ValueError(f"Circular dependency at node: {nid}")
            if nid in visited:
                return
            path.add(nid)
            node = node_map.get(nid)
            if node is None:
                raise ValueError(f"Node {nid} not found in plan")
            for dep in node.get("depends_on", []):
                visit(dep, path)
            path.remove(nid)
            visited.add(nid)
            resolved.append(nid)

        for nid in node_map:
            visit(nid, set())

        return resolved

    @staticmethod
    def _find_node(plan_dag: List[Dict[str, Any]], node_id: str) -> Optional[Dict[str, Any]]:
        for node in plan_dag:
            if node["node_id"] == node_id:
                return node
        return None

    @staticmethod
    def _enrich_with_paths_and_checksums(result: Dict[str, Any], node: Dict[str, Any]) -> Dict[str, Any]:
        """Add absolute paths and SHA-256 checksums to every result."""
        import hashlib
        from pathlib import Path

        output_files = node.get("output_files", []) or []
        paths = {"created": [], "modified": []}
        checksums = {}

        for rel in output_files:
            abs_path = str(Path(rel).absolute())
            paths["created"].append(abs_path)
            p = Path(rel)
            if p.exists():
                sha = hashlib.sha256(p.read_bytes()).hexdigest()
                checksums[abs_path] = f"sha256:{sha}"

        result["paths"] = paths
        result["checksums"] = checksums
        return result

    @staticmethod
    def _error(node_id: str, message: str) -> Dict[str, Any]:
        return {
            "node_id": node_id,
            "status": "error",
            "error": message,
            "paths": {"created": [], "modified": []},
            "checksums": {},
            "duration_seconds": 0,
        }


# Backward-compatible alias (deprecated)
SupervisorAgent = PlanExecutor
