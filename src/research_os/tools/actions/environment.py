import subprocess
import sys
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger("research.tools.environment")


def package_install(packages: List[str]) -> Dict[str, Any]:
    try:
        res = subprocess.run(
            [sys.executable, "-m", "pip", "install"] + packages,
            capture_output=True,
            text=True,
        )
        return {"stdout": res.stdout, "stderr": res.stderr, "code": res.returncode}
    except Exception as e:
        logger.error(f"Package install failed: {e}")
        return {"error": str(e), "code": 1}


def env_freeze() -> Dict[str, Any]:
    try:
        res = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True
        )
        return {"stdout": res.stdout, "stderr": res.stderr, "code": res.returncode}
    except Exception as e:
        logger.error(f"Env freeze failed: {e}")
        return {"error": str(e), "code": 1}


def env_restore(requirements: str = "", root: Optional[Path] = None) -> Dict[str, Any]:
    try:
        import tempfile

        req_content = requirements
        if not req_content and root:
            req_file = root / "environment" / "requirements.txt"
            if req_file.exists():
                req_content = req_file.read_text()
        if not req_content:
            return {
                "error": "No requirements provided and no environment/requirements.txt found",
                "code": 1,
            }
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write(req_content)
            tmp_name = f.name
        res = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", tmp_name],
            capture_output=True,
            text=True,
        )
        import os

        os.remove(tmp_name)
        return {"stdout": res.stdout, "stderr": res.stderr, "code": res.returncode}
    except Exception as e:
        logger.error(f"Env restore failed: {e}")
        return {"error": str(e), "code": 1}
