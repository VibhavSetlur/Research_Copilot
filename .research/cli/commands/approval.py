"""Approval commands: approve, reject."""
import sys
from pathlib import Path

from core.utils import (
    find_project_root, load_json, save_json, require_project_root, now_iso,
)


def cmd_approve(args):
    root = require_project_root()

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
        __import__("interceptors")

        state = {"phase": args.phase, "approval_status": "approved"}
        state = hook_engine.trigger_sync(
            "pre_ledger_commit", state, action="complete_phase", phase=args.phase
        )
    except ImportError:
        pass

    response = {
        "phase": args.phase,
        "status": "approved",
        "timestamp": now_iso()
    }
    save_json(response_path, response)

    try:
        pending_path.unlink()
    except Exception as e:
        print(f"WARNING: Could not delete pending approval file: {e}")

    print(f"SUCCESS: Phase '{args.phase}' has been approved.")


def cmd_reject(args):
    root = require_project_root()

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
        "timestamp": now_iso()
    }
    save_json(response_path, response)

    try:
        pending_path.unlink()
    except Exception as e:
        print(f"WARNING: Could not delete pending approval file: {e}")

    print(f"SUCCESS: Phase '{args.phase}' has been rejected. Reason: {args.reason}")
