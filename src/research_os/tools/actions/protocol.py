import json
import logging
from datetime import datetime, timezone
from pathlib import Path
import yaml
from typing import Dict, Any

logger = logging.getLogger("research.tools.protocol")

PROTOCOL_LOG_FILE = "protocol_execution_log.jsonl"


def log_protocol_execution(root: Path, protocol_name: str, status: str, details: str = "") -> dict:
    """Append a structured entry to the protocol execution log."""
    log_path = root / ".os_state" / PROTOCOL_LOG_FILE
    log_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "protocol": protocol_name,
        "status": status,
        "details": details,
    }
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return {"status": "success", "entry": entry}


def get_protocol_history(root: Path, limit: int = 20) -> dict:
    """Return the last N protocol execution log entries."""
    log_path = root / ".os_state" / PROTOCOL_LOG_FILE
    entries = []
    if log_path.exists():
        with open(log_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    return {"entries": entries[-limit:], "total": len(entries)}

PROTOCOLS_DIR = Path(__file__).parent.parent.parent / "protocols"
LIGHT_DIR = PROTOCOLS_DIR / "light"

def _find_protocol_file(name: str, light: bool = False) -> Path | None:
    base = LIGHT_DIR if light else PROTOCOLS_DIR
    if "/" in name:
        rel_path = name + ".yaml"
        candidate = base / rel_path
        return candidate if candidate.exists() else None
    else:
        # search recursively for name.yaml
        for yaml_file in base.rglob("*.yaml"):
            if yaml_file.stem == name:
                return yaml_file
        return None

def load_protocol(name: str, light: bool = False) -> dict:
    file = _find_protocol_file(name, light)
    if not file:
        raise FileNotFoundError(f"Protocol {name} not found")
    with open(file) as f:
        return yaml.safe_load(f)

def list_protocols(light: bool = False) -> list[dict]:
    base = LIGHT_DIR if light else PROTOCOLS_DIR
    protocols = []
    for yaml_file in base.rglob("*.yaml"):
        # We need to correctly relative the file to base
        # But if we use light=False, base=PROTOCOLS_DIR. It will also iterate over PROTOCOLS_DIR / "light"!
        # We should skip the light directory if light=False
        if not light and "light" in yaml_file.parts:
            continue
            
        rel = yaml_file.relative_to(base).with_suffix("")
        name = str(rel).replace("\\", "/")
        try:
            with open(yaml_file) as f:
                data = yaml.safe_load(f)
            summary = data.get("description", "")
        except Exception:
            summary = ""
        protocols.append({"name": name, "summary": summary})
    return protocols

PIPELINE_ORDER = [
    ("guidance/session_boot", []),
    ("guidance/project_startup", ["workspace/01_baseline_eda/conclusions.md"]),
    ("domain/domain_analysis", ["workspace/logs/domain_analysis.log"]),
    ("domain/research_design", ["docs/research_question.md"]),
    ("methodology/methodology_selection", ["workspace/methods.md"]),
    ("literature/literature_search", ["inputs/literature_index.yaml"]),
    ("guidance/analysis_plan", ["workspace/02_data_preparation/README.md"]),
    ("reproducibility/reproducibility", ["workspace/*/environment/requirements.txt"]),
    ("audit/audit_and_validation", ["workspace/logs/audit.log"]),
    ("synthesis/synthesis_paper", ["synthesis/paper.md"]),
]


def get_next_protocol(root: Path) -> dict:
    """Read current workspace state and return the recommended next protocol."""
    for protocol_name, expected_outputs in PIPELINE_ORDER:
        all_present = True
        for output in expected_outputs:
            if "*" in output:
                matches = list(root.glob(output))
                if not matches:
                    all_present = False
                    break
            else:
                if not (root / output).exists():
                    all_present = False
                    break
        if not all_present:
            reason = f"Expected output '{expected_outputs[0] if expected_outputs else 'none'}' not found"
            return {"next_protocol": protocol_name, "reason": reason}
    return {"next_protocol": None, "reason": "All pipeline phases complete — ready for synthesis"}


def validate_protocol(name: str, root: Path = None) -> Dict[str, Any]:
    try:
        data = load_protocol(name)
        expected_outputs = data.get("expected_outputs", [])

        checklist = []
        all_passed = True

        if root:
            for item in expected_outputs:
                if ":" in item:
                    path_str = item.split(":")[0].strip()
                else:
                    path_str = item.strip()
                
                # Simple wildcard matching for workspace/*/
                if "workspace/*/" in path_str:
                    workspace_dir = root / "workspace"
                    if not workspace_dir.exists():
                        checklist.append({"item": path_str, "status": "fail"})
                        all_passed = False
                        continue
                    
                    found = False
                    for child in workspace_dir.iterdir():
                        if child.is_dir() and child.name[:2].isdigit():
                            candidate = child / path_str.split("workspace/*/")[1]
                            if candidate.exists():
                                found = True
                                break
                    if found:
                        checklist.append({"item": path_str, "status": "pass"})
                    else:
                        checklist.append({"item": path_str, "status": "fail"})
                        all_passed = False
                else:
                    p = root / path_str
                    if p.exists():
                        checklist.append({"item": path_str, "status": "pass"})
                    else:
                        checklist.append({"item": path_str, "status": "fail"})
                        all_passed = False

        # Also check required section headers in key files
        if root:
            for fpath, headers in [
                ("workspace/methods.md", ["##", "Method"]),
                ("workspace/analysis.md", ["##", "mermaid"]),
            ]:
                full = root / fpath
                if full.exists():
                    text = full.read_text()
                    for h in headers:
                        if h not in text:
                            checklist.append({"item": f"{fpath} missing header '{h}'", "status": "fail"})
                            all_passed = False
                            break

        return {
            "protocol": name,
            "checklist": checklist,
            "all_passed": all_passed,
            "expected_count": len(expected_outputs),
        }
    except FileNotFoundError:
        return {"error": "Protocol not found"}
    except Exception as e:
        logger.error(f"Validate protocol failed: {e}")
        return {"error": str(e)}
