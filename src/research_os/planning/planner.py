"""DAGValidator — validates plan DAG structure without making decisions.

The IDE (the brain) owns all planning.  This class provides structural
validation only: circular dependency detection, missing node checks,
type consistency, and dependency satisfaction.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("research.dag_validator")


class DAGValidator:
    """Structural validator for plan DAGs.

    No LLM calls.  No autonomous decisions.  Pure structural validation
    that the IDE can use to check its plan before submission.
    """

    def __init__(self, root: Path):
        self.root = root

    def validate_plan(self, plan_dag: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a plan DAG structure and return a report.

        Args:
            plan_dag: List of node definitions, each with at minimum:
                node_id, tool, params, depends_on

        Returns:
            Dict with:
                valid: bool
                errors: List[str]
                warnings: List[str]
                node_count: int
                dependency_count: int
                topological_order: Optional[List[str]] (only if valid)
        """
        errors: List[str] = []
        warnings: List[str] = []

        if not isinstance(plan_dag, list):
            return {"valid": False, "errors": ["Plan DAG must be a list"], "warnings": [], "node_count": 0, "dependency_count": 0}

        if len(plan_dag) == 0:
            return {"valid": False, "errors": ["Plan DAG is empty"], "warnings": [], "node_count": 0, "dependency_count": 0}

        node_map: Dict[str, Dict] = {}
        ids: Set[str] = set()

        for i, node in enumerate(plan_dag):
            nid = node.get("node_id")
            if not nid:
                errors.append(f"Node at index {i} missing 'node_id'")
                continue
            if nid in ids:
                errors.append(f"Duplicate node_id: {nid}")
            ids.add(nid)
            node_map[nid] = node

            if "tool" not in node:
                errors.append(f"Node '{nid}' missing 'tool'")
            if "params" not in node:
                warnings.append(f"Node '{nid}' has no 'params' (will use empty dict)")

        if errors:
            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings,
                "node_count": len(plan_dag),
                "dependency_count": self._count_deps(plan_dag),
            }

        dep_count = 0
        for node in plan_dag:
            for dep in node.get("depends_on", []):
                dep_count += 1
                if dep not in node_map:
                    errors.append(f"Node '{node['node_id']}' depends on unknown node '{dep}'")
                if dep == node["node_id"]:
                    errors.append(f"Node '{node['node_id']}' depends on itself")

        if errors:
            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings,
                "node_count": len(plan_dag),
                "dependency_count": dep_count,
            }

        try:
            topo_order = self._topological_sort(plan_dag)
            return {
                "valid": True,
                "errors": [],
                "warnings": warnings,
                "node_count": len(plan_dag),
                "dependency_count": dep_count,
                "topological_order": topo_order,
            }
        except ValueError as e:
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": warnings,
                "node_count": len(plan_dag),
                "dependency_count": dep_count,
            }

    def check_integrity(self, plan_dag: List[Dict[str, Any]]) -> List[str]:
        """Deep integrity check.  Returns list of any issues found."""
        issues: List[str] = []
        node_map = {n["node_id"]: n for n in plan_dag}

        for node in plan_dag:
            nid = node["node_id"]
            tool = node.get("tool", "")
            params = node.get("params", {})

            if tool.startswith("tool.") and "script" not in params and "code" not in params:
                issues.append(f"Node '{nid}': tool '{tool}' expects script/code param")
            if tool.startswith("view.") and "path" not in params:
                issues.append(f"Node '{nid}': view tool '{tool}' expects 'path' param")

        return issues

    @staticmethod
    def _count_deps(plan_dag: List[Dict]) -> int:
        return sum(len(n.get("depends_on", [])) for n in plan_dag)

    @staticmethod
    def _topological_sort(plan_dag: List[Dict[str, Any]]) -> List[str]:
        node_map = {n["node_id"]: n for n in plan_dag}
        visited: Set[str] = set()
        resolved: List[str] = []

        def visit(nid: str, path: Set[str]) -> None:
            if nid in path:
                raise ValueError(f"Circular dependency at node: {nid}")
            if nid in visited:
                return
            path.add(nid)
            node = node_map.get(nid)
            if node is None:
                raise ValueError(f"Node '{nid}' not found in plan")
            for dep in node.get("depends_on", []):
                visit(dep, path)
            path.remove(nid)
            visited.add(nid)
            resolved.append(nid)

        for nid in node_map:
            visit(nid, set())

        return resolved


# Backward-compatible alias (deprecated)
PlannerAgent = DAGValidator
