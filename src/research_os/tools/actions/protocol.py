import logging
from pathlib import Path
import yaml
from typing import Dict, Any

logger = logging.getLogger("research.tools.protocol")

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
