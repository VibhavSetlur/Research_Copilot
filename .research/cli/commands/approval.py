"""Approval commands: approve, reject."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


def find_project_root():
    p = Path.cwd()
    for _ in range(10):
        if (p / ".research").exists():
            return p
        if p.parent == p:
            break
        p = p.parent
    return None


def load_json(path: Path):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def cmd_approve(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    cache_dir = root / ".research" / "cache"
    pending_path = cache_dir / "pending_approval.json"
    response_path = cache_dir / "approval_response.json"

    if not pending_path.exists():
        print("ERROR: No pending approval request found.")
        sys.exit(1)

    pending = load_json(pending_path)
    pending_phase = pending.get("phase")
    if pending_phase != args.phase:
        print(f"ERROR: Pending approval is for phase '{pending_phase}', not '{args.phase}'.")
        sys.exit(1)

    try:
        sys.path.insert(0, str(root / ".research" / "core"))
        from hooks import hook_engine
        import interceptors  # noqa: F401

        state = {"phase": args.phase, "approval_status": "approved"}
        state = hook_engine.trigger_sync(
            "pre_ledger_commit", state, action="complete_phase", phase=args.phase
        )
    except ImportError:
        pass

    response = {
        "phase": args.phase,
        "status": "approved",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    save_json(response_path, response)

    try:
        pending_path.unlink()
    except Exception as e:
        print(f"WARNING: Could not delete pending approval file: {e}")

    print(f"SUCCESS: Phase '{args.phase}' has been approved.")


def cmd_reject(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    cache_dir = root / ".research" / "cache"
    pending_path = cache_dir / "pending_approval.json"
    response_path = cache_dir / "approval_response.json"

    if not pending_path.exists():
        print("ERROR: No pending approval request found.")
        sys.exit(1)

    pending = load_json(pending_path)
    pending_phase = pending.get("phase")
    if pending_phase != args.phase:
        print(f"ERROR: Pending approval is for phase '{pending_phase}', not '{args.phase}'.")
        sys.exit(1)

    response = {
        "phase": args.phase,
        "status": "rejected",
        "reason": args.reason,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    save_json(response_path, response)

    try:
        pending_path.unlink()
    except Exception as e:
        print(f"WARNING: Could not delete pending approval file: {e}")

    print(f"SUCCESS: Phase '{args.phase}' has been rejected. Reason: {args.reason}")
