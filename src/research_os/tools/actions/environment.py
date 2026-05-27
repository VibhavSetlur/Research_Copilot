"""Environment snapshotting and Docker generation.

Snapshots are written into the *active experiment*'s ``environment/`` so that
each experiment can be reproduced independently. A root-level ``environment/``
is used as a fallback when no experiment is active.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger("research_os.tools.environment")


def package_install(packages: list[str]) -> dict[str, Any]:
    """``pip install`` the requested packages."""
    try:
        res = subprocess.run(
            [sys.executable, "-m", "pip", "install", *packages],
            capture_output=True,
            text=True,
        )
        status = "success" if res.returncode == 0 else "error"
        return {
            "status": status,
            "stdout": res.stdout,
            "stderr": res.stderr,
            "code": res.returncode,
        }
    except Exception as e:
        logger.exception("package_install failed")
        return {"status": "error", "error": str(e), "code": 1}


def _active_experiment_dir(root: Path) -> Path | None:
    ws = root / "workspace"
    if not ws.exists():
        return None
    active = [
        p
        for p in ws.iterdir()
        if p.is_dir()
        and p.name[:2].isdigit()
        and "_" in p.name
        and not p.name.endswith("__DEAD_END")
    ]
    return sorted(active)[-1] if active else None


def env_snapshot(root: Path) -> dict[str, Any]:
    """Snapshot Python (always) and any detected R/Julia/Conda configs."""
    try:
        active = _active_experiment_dir(root)
        env_dir = (active or root) / "environment"
        env_dir.mkdir(parents=True, exist_ok=True)
        session: dict[str, Any] = {"languages": []}

        # Python
        try:
            res = subprocess.run(
                [sys.executable, "-m", "pip", "freeze"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if res.returncode == 0:
                (env_dir / "requirements.txt").write_text(res.stdout)
                session["languages"].append(
                    {
                        "name": "python",
                        "version": sys.version.split()[0],
                        "manager": "pip",
                    }
                )
        except Exception as e:
            logger.warning(f"Python snapshot failed: {e}")

        # R (renv)
        r_lock = root / "renv.lock"
        if r_lock.exists():
            shutil.copy(r_lock, env_dir / "renv.lock")
            session["languages"].append({"name": "R", "manager": "renv"})

        # Julia (Project.toml + Manifest.toml)
        proj = root / "Project.toml"
        if proj.exists():
            shutil.copy(proj, env_dir / "Project.toml")
            man = root / "Manifest.toml"
            if man.exists():
                shutil.copy(man, env_dir / "Manifest.toml")
            session["languages"].append({"name": "julia", "manager": "Pkg"})

        # Conda
        conda_env = root / "environment.yml"
        if conda_env.exists():
            shutil.copy(conda_env, env_dir / "environment.yml")
            session["languages"].append({"name": "conda", "manager": "conda"})

        (env_dir / "session.yaml").write_text(yaml.dump(session, sort_keys=False))
        return {
            "status": "success",
            "session": session,
            "snapshot_dir": str(env_dir.relative_to(root)),
            "message": "Environment snapshotted.",
        }
    except Exception as e:
        logger.exception("env_snapshot failed")
        return {"status": "error", "message": str(e)}


def env_docker_generate(root: Path) -> dict[str, Any]:
    """Generate a Dockerfile from the latest environment snapshot."""
    try:
        env_dir = root / "environment"
        session_file = env_dir / "session.yaml"

        langs: set[str] = set()
        if session_file.exists():
            data = yaml.safe_load(session_file.read_text()) or {}
            langs = {lang.get("name") for lang in data.get("languages", []) if lang.get("name")}

        lines = [
            "FROM python:3.11-slim",
            "ENV DEBIAN_FRONTEND=noninteractive",
            "RUN apt-get update && apt-get install -y --no-install-recommends \\",
            "    git build-essential curl wget ca-certificates && rm -rf /var/lib/apt/lists/*",
        ]

        if "R" in langs:
            lines.extend(
                [
                    "RUN apt-get update && apt-get install -y --no-install-recommends r-base \\",
                    "    && rm -rf /var/lib/apt/lists/*",
                ]
            )
        if "julia" in langs:
            # Pin via $JULIA_VERSION env, easy to bump.
            lines.extend(
                [
                    "ENV JULIA_VERSION=1.10.0",
                    "RUN curl -fsSL https://julialang-s3.julialang.org/bin/linux/x64/${JULIA_VERSION%.*}/julia-${JULIA_VERSION}-linux-x86_64.tar.gz \\",
                    "    | tar -xz -C /opt/ && ln -s /opt/julia-${JULIA_VERSION}/bin/julia /usr/local/bin/julia",
                ]
            )

        lines.extend(
            [
                "WORKDIR /app",
                "COPY . /app",
            ]
        )

        if (env_dir / "requirements.txt").exists():
            lines.append(
                "RUN pip install --no-cache-dir -r environment/requirements.txt"
            )

        if (env_dir / "renv.lock").exists():
            lines.append(
                "RUN R -e 'install.packages(\"renv\", repos=\"https://cloud.r-project.org\"); "
                "renv::restore(lockfile=\"environment/renv.lock\")'"
            )

        if (env_dir / "Project.toml").exists():
            lines.append(
                "RUN julia --project=environment -e 'using Pkg; Pkg.instantiate()'"
            )

        lines.append('CMD ["/bin/bash"]')
        df_path = env_dir / "Dockerfile"
        df_path.parent.mkdir(parents=True, exist_ok=True)
        df_path.write_text("\n".join(lines) + "\n")
        return {
            "status": "success",
            "dockerfile_path": str(df_path.relative_to(root)),
            "message": "Dockerfile generated.",
        }
    except Exception as e:
        logger.exception("env_docker_generate failed")
        return {"status": "error", "message": str(e)}
