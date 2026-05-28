"""Tests for real-subprocess background tasks."""

import time

from research_os.tools.actions.exec.tasks import (
    task_kill,
    task_list,
    task_run,
    task_status,
)


def test_task_run_starts_subprocess(tmp_path):
    res = task_run("sleep 1", tmp_path, description="quick sleep")
    assert res["status"] == "success"
    assert res["pid"] > 0
    tid = res["task_id"]

    # Listing should show our task.
    listed = task_list(tmp_path)
    assert listed["status"] == "success"
    assert any(t["task_id"] == tid for t in listed["tasks"])


def test_task_status_transitions_to_finished(tmp_path):
    res = task_run("sleep 0.2", tmp_path, description="t")
    tid = res["task_id"]
    time.sleep(0.6)
    s = task_status(tid, tmp_path)
    assert s["status"] == "success"
    assert s["task_status"] == "finished"


def test_task_kill_terminates_process(tmp_path):
    res = task_run("sleep 30", tmp_path, description="long sleep")
    tid = res["task_id"]
    time.sleep(0.1)
    k = task_kill(tid, tmp_path)
    assert k["status"] == "success"
    s = task_status(tid, tmp_path)
    assert s["task_status"] in {"finished", "killed", "kill_requested"}


def test_task_run_unknown_command(tmp_path):
    res = task_run("definitely-not-a-real-binary-xyz123", tmp_path)
    assert res["status"] == "error"


def test_task_status_unknown_id(tmp_path):
    res = task_status("task_nonexistent", tmp_path)
    assert res["status"] == "error"


def test_task_run_refuses_binary_not_on_allowlist(tmp_path):
    # nmap is a real binary that wouldn't be on the default allowlist.
    res = task_run("nmap -sS 192.168.1.0/24", tmp_path)
    assert res["status"] == "error"
    assert "allowlist" in res["message"].lower()


def test_task_run_refuses_shell_metachars(tmp_path):
    # 'sleep' is allowed, but the `;` / `>` chars are flagged.
    res = task_run("sleep 1; rm -rf /tmp/foo", tmp_path)
    assert res["status"] == "error"
    assert "metacharacters" in res["message"].lower()


def test_task_run_audit_log_records_refusal(tmp_path):
    task_run("nmap -sS 192.168.1.0/24", tmp_path)
    audit = tmp_path / "workspace" / "logs" / "task_audit.log"
    assert audit.exists()
    body = audit.read_text()
    assert "accepted" in body
    assert "nmap" in body


def test_task_run_allow_arbitrary_bypasses_allowlist(tmp_path):
    import yaml as _yaml
    # Scaffold a researcher_config first.
    cfg_path = tmp_path / "inputs" / "researcher_config.yaml"
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    cfg_path.write_text(_yaml.dump({"runtime": {"allow_arbitrary": True}}))
    # 'sleep' is allowed regardless; use a less-common binary that
    # exists on most systems.
    res = task_run("printf hi", tmp_path)
    assert res["status"] == "success"
