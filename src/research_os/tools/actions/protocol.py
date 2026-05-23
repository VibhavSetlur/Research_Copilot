from typing import Dict, Any
from pathlib import Path
import yaml
import logging

logger = logging.getLogger("research.tools.protocol")

_PROTOCOL_CACHE: Dict[str, Dict[str, Any]] = {}


def get_protocol(name: str, root: Path) -> Dict[str, Any]:
    try:
        if name in _PROTOCOL_CACHE:
            return {"content": yaml.dump(_PROTOCOL_CACHE[name])}

        p_dir = root / "src" / "research_os" / "protocols"
        if not p_dir.exists():
            p_dir = Path(__file__).parent.parent.parent / "protocols"
            
        if not p_dir.exists():
            return {"error": "Protocol directory not found"}

        # Search recursively
        found_file = None
        for file in p_dir.rglob(f"{name}.yaml"):
            # If name doesn't specify light/, avoid matching light/ versions if there are duplicates
            # but if name starts with light/, let it match.
            if "light/" not in name and "/light/" in file.as_posix():
                continue
            found_file = file
            break
            
        if not found_file:
            return {"error": "Protocol not found"}

        data = yaml.safe_load(found_file.read_text())
        _PROTOCOL_CACHE[name] = data
        return {"content": yaml.dump(data)}
    except Exception as e:
        logger.error(f"Get protocol failed: {e}")
        return {"error": str(e)}


def list_protocols(root: Path) -> Dict[str, Any]:
    try:
        p_dir = root / "src" / "research_os" / "protocols"
        if not p_dir.exists():
            p_dir = Path(__file__).parent.parent.parent / "protocols"
        if not p_dir.exists():
            return {"error": "Protocols directory not found"}
        protocols = []
        for p in p_dir.rglob("*.yaml"):
            # skip light directory for list
            if "light" in p.parts:
                continue
            try:
                name = p.stem
                if name in _PROTOCOL_CACHE:
                    data = _PROTOCOL_CACHE[name]
                else:
                    data = yaml.safe_load(p.read_text())
                    _PROTOCOL_CACHE[name] = data

                protocols.append(
                    {
                        "name": name,
                        "description": data.get("description", ""),
                        "version": data.get("version", "1.0.0"),
                    }
                )
            except Exception:
                pass
        return {"protocols": protocols}
    except Exception as e:
        logger.error(f"List protocols failed: {e}")
        return {"error": str(e)}


def validate_protocol(name: str, root: Path) -> Dict[str, Any]:
    try:
        p_dir = root / "src" / "research_os" / "protocols"
        if not p_dir.exists():
            p_dir = Path(__file__).parent.parent.parent / "protocols"
            
        found_file = None
        for file in p_dir.rglob(f"{name}.yaml"):
            if "light/" not in name and "/light/" in file.as_posix():
                continue
            found_file = file
            break
            
        if not found_file:
            return {"error": "Protocol not found"}

        data = yaml.safe_load(found_file.read_text())
        expected_outputs = data.get("expected_outputs", [])

        checklist = []
        all_passed = True

        for output in expected_outputs:
            path_str = output.split(":")[0].strip()
            item_path = root / path_str
            passed = item_path.exists()
            if not passed:
                all_passed = False
            checklist.append({"item": output, "passed": passed})

        return {
            "status": "success",
            "protocol": name,
            "all_passed": all_passed,
            "checklist": checklist,
        }
    except Exception as e:
        logger.error(f"Validate protocol failed: {e}")
        return {"error": str(e)}
