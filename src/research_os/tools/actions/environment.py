import subprocess
import sys
import logging
import os
import shutil
import tempfile
import yaml
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


def _get_active_experiment_dir(root: Path) -> Optional[Path]:
    workspace_dir = root / "workspace"
    if not workspace_dir.exists():
        return None
    active_paths = [
        p for p in workspace_dir.iterdir()
        if p.is_dir() and not p.name.endswith("__DEAD_END") and p.name[:2].isdigit() and p.name[2:3] == "_"
    ]
    return sorted(active_paths)[-1] if active_paths else None


def env_snapshot(root: Path) -> Dict[str, Any]:
    # Determine active experiment path
    active_path = _get_active_experiment_dir(root)
    if active_path:
        env_dir = active_path / "environment"
    else:
        env_dir = root / "environment"
    env_dir.mkdir(parents=True, exist_ok=True)
    
    session_data = {"languages": []}
    
    # Python
    try:
        res = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True)
        if res.returncode == 0:
            (env_dir / "requirements.txt").write_text(res.stdout)
            session_data["languages"].append({"name": "python", "version": sys.version.split()[0], "manager": "pip"})
    except Exception as e:
        logger.error(f"Failed to snapshot python env: {e}")

    # R
    r_lock = root / "renv.lock"
    if r_lock.exists():
        shutil.copy(r_lock, env_dir / "renv.lock")
        session_data["languages"].append({"name": "R", "manager": "renv"})
        
    # Julia
    j_proj = root / "Project.toml"
    j_man = root / "Manifest.toml"
    if j_proj.exists():
        shutil.copy(j_proj, env_dir / "Project.toml")
        if j_man.exists():
            shutil.copy(j_man, env_dir / "Manifest.toml")
        session_data["languages"].append({"name": "julia", "manager": "Pkg"})
        
    # Conda
    c_env = root / "environment.yml"
    if c_env.exists():
        shutil.copy(c_env, env_dir / "environment.yml")
        session_data["languages"].append({"name": "conda", "manager": "conda"})
        
    (env_dir / "session.yaml").write_text(yaml.dump(session_data))
    
    return {"status": "success", "session": session_data, "message": "Environment snapshotted."}


def env_restore(requirements: str = "", root: Optional[Path] = None) -> Dict[str, Any]:
    if not root:
        return {"error": "Root path is required for multi-lang restore", "code": 1}
        
    active_path = _get_active_experiment_dir(root)
    if active_path:
        env_dir = active_path / "environment"
        if not (env_dir / "session.yaml").exists() and not (env_dir / "requirements.txt").exists():
            env_dir = root / "environment"
    else:
        env_dir = root / "environment"
    session_file = env_dir / "session.yaml"
    
    if not session_file.exists():
        # Fallback to old behavior
        req_file = env_dir / "requirements.txt"
        if req_file.exists():
            res = subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file)], capture_output=True, text=True)
            return {"stdout": res.stdout, "stderr": res.stderr, "code": res.returncode}
        return {"error": "No session.yaml or requirements.txt found", "code": 1}
        
    session_data = yaml.safe_load(session_file.read_text())
    logs = []
    has_error = False
    
    for lang in session_data.get("languages", []):
        if lang["name"] == "python" and lang["manager"] == "pip":
            req_file = env_dir / "requirements.txt"
            if req_file.exists():
                res = subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file)], capture_output=True, text=True)
                logs.append(res.stdout)
                if res.returncode != 0:
                    has_error = True
        elif lang["name"] == "R" and lang["manager"] == "renv":
            res = subprocess.run(["Rscript", "-e", "renv::restore()"], cwd=str(root), capture_output=True, text=True)
            logs.append(res.stdout)
            if res.returncode != 0:
                has_error = True
        elif lang["name"] == "julia" and lang["manager"] == "Pkg":
            res = subprocess.run(["julia", "--project=" + str(env_dir), "-e", "using Pkg; Pkg.instantiate()"], capture_output=True, text=True)
            logs.append(res.stdout)
            if res.returncode != 0:
                has_error = True
                
    return {
        "status": "error" if has_error else "success",
        "stdout": "\n".join(logs),
        "code": 1 if has_error else 0
    }


def env_docker_generate(root: Path) -> Dict[str, Any]:
    env_dir = root / "environment"
    session_file = env_dir / "session.yaml"
    
    dockerfile_lines = [
        "FROM ubuntu:22.04",
        "ENV DEBIAN_FRONTEND=noninteractive",
        "RUN apt-get update && apt-get install -y python3-pip python3-dev \\",
        "    wget curl git build-essential software-properties-common"
    ]
    
    if session_file.exists():
        session_data = yaml.safe_load(session_file.read_text())
        langs = [l["name"] for l in session_data.get("languages", [])]
        
        if "R" in langs:
            dockerfile_lines.extend([
                "RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9",
                "RUN add-apt-repository 'deb https://cloud.r-project.org/bin/linux/ubuntu jammy-cran40/'",
                "RUN apt-get install -y r-base"
            ])
            
        if "julia" in langs:
            dockerfile_lines.extend([
                "RUN wget https://julialang-s3.julialang.org/bin/linux/x64/1.9/julia-1.9.3-linux-x86_64.tar.gz",
                "RUN tar zxvf julia-1.9.3-linux-x86_64.tar.gz -C /opt/",
                "RUN ln -s /opt/julia-1.9.3/bin/julia /usr/local/bin/julia"
            ])
            
    dockerfile_lines.extend([
        "WORKDIR /app",
        "COPY . /app",
    ])
    
    if (env_dir / "requirements.txt").exists():
        dockerfile_lines.append("RUN pip3 install -r environment/requirements.txt")
        
    if (env_dir / "renv.lock").exists():
        dockerfile_lines.append("RUN Rscript -e 'if (!requireNamespace(\"renv\", quietly = TRUE)) install.packages(\"renv\", repos=\"https://cloud.r-project.org\"); renv::restore(lockfile=\"environment/renv.lock\")'")
        
    if (env_dir / "Project.toml").exists():
        dockerfile_lines.append("RUN julia --project=environment -e 'using Pkg; Pkg.instantiate()'")
        
    dockerfile_lines.append("CMD [\"/bin/bash\"]")
    
    df_path = env_dir / "Dockerfile"
    df_path.write_text("\n".join(dockerfile_lines) + "\n")
    
    return {"status": "success", "message": "Dockerfile generated successfully."}

