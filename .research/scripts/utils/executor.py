"""ResearchExecutor: multi-language execution kernel scaffold.

Provides safe wrappers to run Python, R, bash, Nextflow, Snakemake, or Julia
jobs. Records stdout/stderr, duration, exit codes, and optional container used.
"""
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
import subprocess
import time
import shutil
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class ExecutionResult:
    runtime: str
    script_path: str
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    container_used: Optional[str]
    artifacts_produced: List[str]
    tool_ids: List[str]
    domain: Optional[str]


def _find_project_root() -> Path:
    p = Path.cwd()
    for _ in range(10):
        if (p / ".research").exists():
            return p
        if p.parent == p:
            break
        p = p.parent
    return Path.cwd()


def _load_config(root: Path) -> Dict[str, Any]:
    if yaml is None:
        return {}
    try:
        with open(root / ".research" / "config.yaml") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


class ResearchExecutor:
    def __init__(self, root: Optional[Path] = None, container_engine: Optional[str] = None, log_path: Optional[Path] = None):
        self.root = root or _find_project_root()
        config = _load_config(self.root)
        exec_cfg = config.get("execution", {}) if isinstance(config, dict) else {}
        self.container_engine = container_engine or exec_cfg.get("container_engine", "docker")
        log_default = exec_cfg.get("executor_log", ".research/cache/execution_log.jsonl")
        self.log_path = Path(log_path) if log_path else (self.root / log_default)

    def _run(self, cmd: List[str], timeout: Optional[int] = None,
             tool_ids: Optional[List[str]] = None, domain: Optional[str] = None) -> ExecutionResult:
        start = time.time()
        try:
            p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
            duration = time.time() - start
            return ExecutionResult(runtime=cmd[0] if cmd else "", script_path=" ", exit_code=p.returncode,
                                   stdout=p.stdout, stderr=p.stderr, duration_seconds=duration,
                                   container_used=None, artifacts_produced=[],
                                   tool_ids=tool_ids or [], domain=domain)
        except subprocess.TimeoutExpired as e:
            duration = time.time() - start
            return ExecutionResult(runtime=cmd[0] if cmd else "", script_path=" ", exit_code=124,
                                   stdout="", stderr=str(e), duration_seconds=duration,
                                   container_used=None, artifacts_produced=[],
                                   tool_ids=tool_ids or [], domain=domain)

    def _wrap_container(self, container: Optional[str], command: List[str]) -> List[str]:
        if not container:
            return command
        if shutil.which(self.container_engine):
            # simple docker run wrapper; users should prefer runtime_selector for complex needs
            return [self.container_engine, "run", "--rm", "-v", f"{Path.cwd()}:/workspace", container] + command
        return command

    def _make_node_id(self, script_path: str, iteration_id: Optional[str]) -> str:
        base = Path(script_path).name.split()[0] if script_path else "command"
        stem = Path(base).stem or "command"
        ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"{stem}_{iteration_id or 'base'}_{ts}"

    def _log_execution(self, result: ExecutionResult, metadata: Dict[str, Any]) -> None:
        entry = asdict(result)
        entry.update(metadata)
        entry["timestamp"] = datetime.now(timezone.utc).isoformat()
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def _update_dag(self, result: ExecutionResult, metadata: Dict[str, Any]) -> None:
        try:
            sys.path.insert(0, str(self.root / ".research" / "scripts" / "utils"))
            from dag_manager import ExecutionDAGManager
        except ImportError:
            return

        node_id = metadata.get("node_id") or self._make_node_id(result.script_path, metadata.get("iteration_id"))
        input_files = metadata.get("input_files") or []
        output_files = metadata.get("output_files") or []
        depends_on = metadata.get("depends_on") or []
        iteration_id = metadata.get("iteration_id")
        status = "complete" if result.exit_code == 0 else "failed"

        dag = ExecutionDAGManager(self.root)
        dag.add_node(node_id, result.script_path, input_files, output_files,
                     depends_on=depends_on, iteration_id=iteration_id, status=status,
                     runtime=result.runtime, container=result.container_used,
                     tool_ids=result.tool_ids, domain=result.domain,
                     exit_code=result.exit_code, duration=result.duration_seconds)
        if output_files:
            dag.update_output_hashes(node_id)

    def _post_process(self, result: ExecutionResult, metadata: Dict[str, Any]) -> ExecutionResult:
        self._log_execution(result, metadata)
        self._update_dag(result, metadata)
        return result

    def run_python(
        self,
        script_path: str,
        args: Optional[List[str]] = None,
        container: Optional[str] = None,
        input_files: Optional[List[str]] = None,
        output_files: Optional[List[str]] = None,
        depends_on: Optional[List[str]] = None,
        iteration_id: Optional[str] = None,
        node_id: Optional[str] = None,
        timeout: Optional[int] = None,
        tool_ids: Optional[List[str]] = None,
        domain: Optional[str] = None,
    ) -> ExecutionResult:
        cmd = [sys.executable, script_path] + (args or [])
        cmd = self._wrap_container(container, cmd)
        res = self._run(cmd, timeout=timeout, tool_ids=tool_ids, domain=domain)
        res.runtime = "python"
        res.script_path = script_path
        res.container_used = container
        return self._post_process(res, {
            "input_files": input_files or [],
            "output_files": output_files or [],
            "depends_on": depends_on or [],
            "iteration_id": iteration_id,
            "node_id": node_id,
        })

    def run_r(
        self,
        script_path: str,
        args: Optional[List[str]] = None,
        container: Optional[str] = None,
        input_files: Optional[List[str]] = None,
        output_files: Optional[List[str]] = None,
        depends_on: Optional[List[str]] = None,
        iteration_id: Optional[str] = None,
        node_id: Optional[str] = None,
        timeout: Optional[int] = None,
        tool_ids: Optional[List[str]] = None,
        domain: Optional[str] = None,
    ) -> ExecutionResult:
        cmd = ["Rscript", script_path] + (args or [])
        cmd = self._wrap_container(container, cmd)
        res = self._run(cmd, timeout=timeout, tool_ids=tool_ids, domain=domain)
        res.runtime = "r"
        res.script_path = script_path
        res.container_used = container
        return self._post_process(res, {
            "input_files": input_files or [],
            "output_files": output_files or [],
            "depends_on": depends_on or [],
            "iteration_id": iteration_id,
            "node_id": node_id,
        })

    def run_bash(
        self,
        command: str,
        container: Optional[str] = None,
        input_files: Optional[List[str]] = None,
        output_files: Optional[List[str]] = None,
        depends_on: Optional[List[str]] = None,
        iteration_id: Optional[str] = None,
        node_id: Optional[str] = None,
        timeout: Optional[int] = None,
        tool_ids: Optional[List[str]] = None,
        domain: Optional[str] = None,
    ) -> ExecutionResult:
        cmd = ["bash", "-c", command]
        cmd = self._wrap_container(container, cmd)
        res = self._run(cmd, timeout=timeout, tool_ids=tool_ids, domain=domain)
        res.runtime = "bash"
        res.script_path = command
        res.container_used = container
        return self._post_process(res, {
            "input_files": input_files or [],
            "output_files": output_files or [],
            "depends_on": depends_on or [],
            "iteration_id": iteration_id,
            "node_id": node_id,
        })

    def run_nextflow(
        self,
        pipeline: str,
        params: Optional[List[str]] = None,
        container: Optional[str] = None,
        input_files: Optional[List[str]] = None,
        output_files: Optional[List[str]] = None,
        depends_on: Optional[List[str]] = None,
        iteration_id: Optional[str] = None,
        node_id: Optional[str] = None,
        timeout: Optional[int] = None,
        tool_ids: Optional[List[str]] = None,
        domain: Optional[str] = None,
    ) -> ExecutionResult:
        cmd = ["nextflow", "run", pipeline] + (params or [])
        cmd = self._wrap_container(container, cmd)
        res = self._run(cmd, timeout=timeout, tool_ids=tool_ids, domain=domain)
        res.runtime = "nextflow"
        res.script_path = pipeline
        res.container_used = container
        return self._post_process(res, {
            "input_files": input_files or [],
            "output_files": output_files or [],
            "depends_on": depends_on or [],
            "iteration_id": iteration_id,
            "node_id": node_id,
        })

    def run_snakemake(
        self,
        snakefile: str,
        config: Optional[List[str]] = None,
        container: Optional[str] = None,
        input_files: Optional[List[str]] = None,
        output_files: Optional[List[str]] = None,
        depends_on: Optional[List[str]] = None,
        iteration_id: Optional[str] = None,
        node_id: Optional[str] = None,
        timeout: Optional[int] = None,
        tool_ids: Optional[List[str]] = None,
        domain: Optional[str] = None,
    ) -> ExecutionResult:
        cmd = ["snakemake", "-s", snakefile] + (config or [])
        cmd = self._wrap_container(container, cmd)
        res = self._run(cmd, timeout=timeout, tool_ids=tool_ids, domain=domain)
        res.runtime = "snakemake"
        res.script_path = snakefile
        res.container_used = container
        return self._post_process(res, {
            "input_files": input_files or [],
            "output_files": output_files or [],
            "depends_on": depends_on or [],
            "iteration_id": iteration_id,
            "node_id": node_id,
        })

    def run_julia(
        self,
        script_path: str,
        args: Optional[List[str]] = None,
        container: Optional[str] = None,
        input_files: Optional[List[str]] = None,
        output_files: Optional[List[str]] = None,
        depends_on: Optional[List[str]] = None,
        iteration_id: Optional[str] = None,
        node_id: Optional[str] = None,
        timeout: Optional[int] = None,
        tool_ids: Optional[List[str]] = None,
        domain: Optional[str] = None,
    ) -> ExecutionResult:
        cmd = ["julia", script_path] + (args or [])
        cmd = self._wrap_container(container, cmd)
        res = self._run(cmd, timeout=timeout, tool_ids=tool_ids, domain=domain)
        res.runtime = "julia"
        res.script_path = script_path
        res.container_used = container
        return self._post_process(res, {
            "input_files": input_files or [],
            "output_files": output_files or [],
            "depends_on": depends_on or [],
            "iteration_id": iteration_id,
            "node_id": node_id,
        })

    def check_runtime(self, runtime: str) -> bool:
        if runtime == "docker":
            return shutil.which("docker") is not None
        if runtime == "singularity":
            return shutil.which("singularity") is not None
        if runtime == "podman":
            return shutil.which("podman") is not None
        if runtime == "r":
            return shutil.which("Rscript") is not None
        if runtime == "python":
            return Path(sys.executable).exists()
        if runtime == "julia":
            return shutil.which("julia") is not None
        if runtime == "nextflow":
            return shutil.which("nextflow") is not None
        if runtime == "snakemake":
            return shutil.which("snakemake") is not None
        if runtime == "bash":
            return shutil.which("bash") is not None
        return False


if __name__ == "__main__":
    ex = ResearchExecutor()
    r = ex.run_python("-c", args=["print('hello')"], node_id="executor_smoke")
    print(json.dumps(asdict(r), indent=2))
