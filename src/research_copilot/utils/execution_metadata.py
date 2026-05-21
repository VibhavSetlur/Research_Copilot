"""Execution metadata aggregator.

Merges data from:
  - execution_log.jsonl (produced by ResearchExecutor)
  - tool_registry.json  (tool definitions)
  - domain_registry.json (domain definitions)

Produces structured analysis-ready metadata consumed by downstream phases.
"""
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional


def _find_project_root() -> Path:
    p = Path.cwd()
    for _ in range(10):
        if (p / ".research").exists():
            return p
        if p.parent == p:
            break
        p = p.parent
    return Path.cwd()


def load_json_safe(path: Path) -> Dict[str, Any]:
    try:
        if path.exists():
            with open(path) as f:
                return json.load(f)
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def load_execution_log(root: Optional[Path] = None) -> List[Dict[str, Any]]:
    root = root or _find_project_root()
    log_path = root / ".research" / "cache" / "execution_log.jsonl"
    entries = []
    if log_path.exists():
        with open(log_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    return entries


def load_tool_registry(root: Optional[Path] = None) -> Dict[str, Any]:
    root = root or _find_project_root()
    return load_json_safe(root / ".research" / "domains" / "tool_registry.json")


def load_domain_registry(root: Optional[Path] = None) -> Dict[str, Any]:
    root = root or _find_project_root()
    return load_json_safe(root / ".research" / "domains" / "domain_registry.json")


def load_assumption_registry(root: Optional[Path] = None) -> Dict[str, Any]:
    root = root or _find_project_root()
    return load_json_safe(root / ".research" / "domains" / "assumption_registry.json")


def get_tool_id_from_entry(entry: Dict[str, Any]) -> Optional[str]:
    tool_ids = entry.get("tool_ids", entry.get("tool_id", []))
    if isinstance(tool_ids, str):
        return tool_ids
    if isinstance(tool_ids, list) and tool_ids:
        return tool_ids[0]
    return None


def enrich_entry_with_tool_metadata(
    entry: Dict[str, Any],
    tools_by_id: Dict[str, Any],
) -> Dict[str, Any]:
    enriched = dict(entry)
    tool_id = get_tool_id_from_entry(entry)
    if tool_id and tool_id in tools_by_id:
        tool = tools_by_id[tool_id]
        enriched["tool_category"] = tool.get("category")
        enriched["tool_language"] = tool.get("language")
        enriched["tool_container"] = tool.get("container")
        enriched["tool_citation"] = tool.get("citation")
        enriched["tool_input_formats"] = tool.get("input_formats", [])
        enriched["tool_output_formats"] = tool.get("output_formats", [])
    return enriched


def build_analysis_metadata(
    root: Optional[Path] = None,
) -> Dict[str, Any]:
    root = root or _find_project_root()
    execution_log = load_execution_log(root)
    tool_registry = load_tool_registry(root)
    domain_registry = load_domain_registry(root)
    assumption_registry = load_assumption_registry(root)

    tools_by_id = {t.get("id"): t for t in tool_registry.get("tools", [])}

    enriched_entries = [
        enrich_entry_with_tool_metadata(e, tools_by_id) for e in execution_log
    ]

    runtime_counts = defaultdict(int)
    container_counts = defaultdict(int)
    tool_ids_used = set()
    domain_hints = defaultdict(int)
    status_counts = defaultdict(int)

    for e in enriched_entries:
        runtime_counts[e.get("runtime", "unknown")] += 1
        container_counts[e.get("container_used") or "none"] += 1
        status_counts[e.get("exit_code", -1)] += 1
        tool_id = get_tool_id_from_entry(e)
        if tool_id:
            tool_ids_used.add(tool_id)
        domain = e.get("domain")
        if domain:
            domain_hints[domain] += 1

    success_count = status_counts.get(0, 0)
    fail_count = sum(v for k, v in status_counts.items() if k != 0)

    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_executions": len(enriched_entries),
            "successful": success_count,
            "failed": fail_count,
            "runtimes_used": dict(runtime_counts),
            "containers_used": dict(container_counts),
            "tools_used": sorted(tool_ids_used),
            "domains_detected": dict(domain_hints),
        },
        "executions": enriched_entries,
        "tool_registry_snapshot": {
            tid: tools_by_id[tid] for tid in tool_ids_used if tid in tools_by_id
        },
        "domain_registry_snapshot": domain_registry,
        "assumption_registry_snapshot": assumption_registry,
    }
    return metadata


def write_analysis_metadata(
    output_path: Optional[str] = None,
    root: Optional[Path] = None,
) -> str:
    root = root or _find_project_root()
    metadata = build_analysis_metadata(root)
    out = Path(output_path) if output_path else (
        root / ".research" / "cache" / "execution_metadata.json"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(metadata, f, indent=2, default=str)
    return str(out)


def get_analysis_pipeline_summary(root: Optional[Path] = None) -> Dict[str, Any]:
    root = root or _find_project_root()
    metadata = build_analysis_metadata(root)
    sm = metadata["summary"]
    return {
        "total_executions": sm["total_executions"],
        "successful": sm["successful"],
        "failed": sm["failed"],
        "success_rate_pct": round(
            sm["successful"] / sm["total_executions"] * 100, 1
        ) if sm["total_executions"] > 0 else 0,
        "runtimes_used": sm["runtimes_used"],
        "containers_used": sm["containers_used"],
        "tools_used": sm["tools_used"],
        "domains_detected": sm["domains_detected"],
    }


if __name__ == "__main__":
    import sys
    if "--summary" in sys.argv:
        sm = get_analysis_pipeline_summary()
        print(json.dumps(sm, indent=2))
    elif "--full" in sys.argv:
        path = write_analysis_metadata()
        print(f"Metadata written to: {path}")
    else:
        path = write_analysis_metadata()
        print(f"Execution metadata written to: {path}")
        sm = get_analysis_pipeline_summary()
        print(f"\nSummary: {sm['total_executions']} executions, "
              f"{sm['successful']} successful, "
              f"{sm['failed']} failed "
              f"({sm['success_rate_pct']}% success rate)")
