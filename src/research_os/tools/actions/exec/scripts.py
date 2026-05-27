import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any
from research_os.project_ops import now_iso

def _log_execution(root: Path, step_name: str, cmd: list, res: subprocess.CompletedProcess) -> None:
    log_dir = root / "workspace" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    exec_log_path = log_dir / f"{step_name}_exec.log"
    
    with open(exec_log_path, "a") as f:
        f.write(
            f"--- Executed at {now_iso()} ---\nCommand: {' '.join(cmd)}\nReturn Code: {res.returncode}\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}\n\n"
        )

def execute_r_script(script_path: str, root: Path, timeout: int = 300) -> Dict[str, Any]:
    if not shutil.which("Rscript"):
        return {"status": "error", "message": "Rscript command not found. Ensure R is installed."}
        
    p = root / script_path
    if not p.exists() or not p.is_file():
        return {"status": "error", "message": f"Script not found at {script_path}"}
        
    # Pin R environment via renv if detected
    # env_vars = None
    if (root / "environment" / "renv.lock").exists() or (p.parent / "renv.lock").exists():
        # renv automatically activates if .Rprofile exists, but we can set RENV_PATHS_ROOT if needed
        pass

    cmd = ["Rscript", str(p)]
    try:
        res = subprocess.run(cmd, cwd=str(p.parent), capture_output=True, text=True, timeout=timeout)
        _log_execution(root, p.stem, cmd, res)
        return {
            "status": "success",
            "stdout": res.stdout,
            "stderr": res.stderr,
            "code": res.returncode
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": f"Execution timed out after {timeout} seconds."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def execute_julia_script(script_path: str, root: Path, timeout: int = 300) -> Dict[str, Any]:
    if not shutil.which("julia"):
        return {"status": "error", "message": "julia command not found. Ensure Julia is installed."}
        
    p = root / script_path
    if not p.exists() or not p.is_file():
        return {"status": "error", "message": f"Script not found at {script_path}"}
        
    cmd = ["julia"]
    
    # Check for Project.toml
    if (p.parent / "Project.toml").exists():
        cmd.extend(["--project=" + str(p.parent)])
    elif (root / "environment" / "Project.toml").exists():
        cmd.extend(["--project=" + str(root / "environment")])
        
    cmd.append(str(p))
    
    try:
        res = subprocess.run(cmd, cwd=str(p.parent), capture_output=True, text=True, timeout=timeout)
        _log_execution(root, p.stem, cmd, res)
        return {
            "status": "success",
            "stdout": res.stdout,
            "stderr": res.stderr,
            "code": res.returncode
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": f"Execution timed out after {timeout} seconds."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def execute_bash_script(script_path: str, root: Path, timeout: int = 300) -> Dict[str, Any]:
    p = root / script_path
    if not p.exists() or not p.is_file():
        return {"status": "error", "message": f"Script not found at {script_path}"}
        
    cmd = ["/bin/bash", "-e", str(p)]
    try:
        res = subprocess.run(cmd, cwd=str(p.parent), capture_output=True, text=True, timeout=timeout)
        _log_execution(root, p.stem, cmd, res)
        return {
            "status": "success",
            "stdout": res.stdout,
            "stderr": res.stderr,
            "code": res.returncode
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": f"Execution timed out after {timeout} seconds."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
