"""Tracking commands: dag, data-scale, budget, state, resume, hooks."""
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


def load_yaml(path: Path):
    if yaml is None:
        result = {}
        try:
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and ":" in line:
                        key, _, val = line.partition(":")
                        val = val.strip().strip('"').strip("'")
                        result[key.strip()] = val
        except FileNotFoundError:
            return {}
        return result
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except (FileNotFoundError, Exception):
        return {}


def load_json(path: Path):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def get_config(root: Path):
    config = load_yaml(root / ".research" / "config.yaml")
    defaults = {
        "cache_dir": ".research/cache",
        "state_ledger": ".research/cache/state.json",
        "checkpoint_dir": ".research/cache/checkpoints",
        "core_dir": ".research/core",
        "token_budget_limit": 200000,
    }
    for k, v in defaults.items():
        config.setdefault(k, v)
    return config


def cmd_state(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    try:
        sys.path.insert(0, str(root / ".research" / "core"))
        from state_ledger import ResearchLedger
    except ImportError:
        print("ERROR: state_ledger module not found in .research/core/")
        sys.exit(1)

    ledger = ResearchLedger(root / ".research" / "cache" / "state.json")
    print(ledger.summary())

    if hasattr(args, 'json') and args.json:
        print(json.dumps(ledger.get(), indent=2))


def cmd_resume(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    try:
        sys.path.insert(0, str(root / ".research" / "core"))
        from state_ledger import ResearchLedger
        from checkpoint_manager import CheckpointManager
    except ImportError:
        print("ERROR: core modules not found in .research/core/")
        sys.exit(1)

    ledger = ResearchLedger(root / ".research" / "cache" / "state.json")
    cp_manager = CheckpointManager(root / ".research" / "cache" / "checkpoints")

    phase = args.phase if args.phase else None

    if phase:
        checkpoint = cp_manager.load(phase)
        if checkpoint is None:
            print(f"No checkpoint found for phase: {phase}")
            available = cp_manager.list_all()
            if available:
                print("Available checkpoints:")
                for cp in available:
                    print(f"  - {cp['phase']} [{cp['timestamp'][:19]}]")
            return

        state = ledger.get()
        state["phase"] = phase
        state["resumable_from"] = phase
        state["checkpoints"][phase] = "restored"
        ledger.update(**{"phase": phase, "resumable_from": phase})
        ledger.complete_phase(phase)

        print("=" * 60)
        print("CHECKPOINT RESTORED")
        print("=" * 60)
        print()
        print(f"  Phase: {phase}")
        print(f"  Checkpoint time: {checkpoint.get('timestamp', 'N/A')}")
        print(f"  Run ID: {state.get('run_id', 'N/A')}")
        print()

        metadata = checkpoint.get("metadata", {})
        if metadata:
            print("  Metadata:")
            for k, v in metadata.items():
                print(f"    {k}: {v}")
            print()

        file_hashes = checkpoint.get("file_hashes", {})
        if file_hashes:
            print("  File hashes at checkpoint:")
            for fp, h in file_hashes.items():
                print(f"    {fp}: {h}")
            print()

        print("  State updated. Continue with the next phase in the pipeline.")
        print()
    else:
        print(cp_manager.summary())
        print()
        state = ledger.get()
        print(f"  Current phase: {state.get('phase', 'N/A')}")
        print(f"  Resumable from: {state.get('resumable_from', 'none')}")
        print()
        print("  Usage: research resume --from <phase>")
        print()


def cmd_budget(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    try:
        sys.path.insert(0, str(root / ".research" / "core"))
        from state_ledger import ResearchLedger
    except ImportError:
        print("ERROR: state_ledger module not found in .research/core/")
        sys.exit(1)

    ledger = ResearchLedger(root / ".research" / "cache" / "state.json")
    state = ledger.get()
    budget = state.get("token_budget", {"used": 0, "remaining": 200000, "limit": 200000})

    used = budget.get("used", 0)
    remaining = budget.get("remaining", 0)
    limit = budget.get("limit", 200000)
    pct = round(used / limit * 100, 1) if limit > 0 else 0

    print("=" * 60)
    print("TOKEN BUDGET")
    print("=" * 60)
    print()
    print(f"  Model context limit: {limit:,} tokens")
    print(f"  Used:                {used:,} tokens ({pct}%)")
    print(f"  Remaining:           {remaining:,} tokens")
    print()

    if pct < 60:
        print("  Status: OK — full context available")
    elif pct < 80:
        print("  Status: WARNING — consider summarizing completed phases")
    elif pct < 90:
        print("  Status: CRITICAL — flush non-essential context now")
    else:
        print("  Status: EMERGENCY — force checkpoint and split session")

    print()

    ctms = state.get("context_transfer_memos", [])
    if ctms:
        print("  Context Transfer Memoranda (CTMs):")
        for ctm in ctms:
            print(f"    - {ctm.get('ctm_id', 'unknown')} (phase: {ctm.get('phase', '?')}, "
                  f"usage: {ctm.get('token_usage_pct', 0)*100:.0f}%)")
        print()

    checkpoints = state.get("checkpoints", {})
    if checkpoints:
        print("  Phase checkpoints:")
        for phase, status in checkpoints.items():
            marker = "✓" if status == "complete" else "○"
            print(f"    {marker} {phase}: {status}")
        print()


def cmd_dag(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    try:
        sys.path.insert(0, str(root / ".research" / "scripts" / "utils"))
        from dag_manager import ExecutionDAGManager
    except ImportError:
        print("ERROR: dag_manager module not found in .research/scripts/utils/")
        sys.exit(1)

    dag = ExecutionDAGManager(root)
    print(dag.summary())

    dag_path = root / ".research" / "cache" / "execution_dag.json"
    if dag_path.exists():
        print(f"  DAG file: {dag_path}")
        with open(dag_path) as f:
            data = json.load(f)
        print(f"  Nodes: {len(data.get('nodes', {}))}")
        print(f"  Edges: {len(data.get('edges', []))}")
        print()


def cmd_data_scale(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    try:
        sys.path.insert(0, str(root / ".research" / "scripts" / "utils"))
        from data_scale_detector import DataScaleDetector
    except ImportError:
        print("ERROR: data_scale_detector module not found in .research/scripts/utils/")
        sys.exit(1)

    detector = DataScaleDetector(root)
    profile = detector.scan()

    print("=" * 60)
    print("DATA SCALE ANALYSIS")
    print("=" * 60)

    summary = profile["summary"]
    print(f"\nTotal files: {summary['total_files']}")
    print(f"Total size: {summary['total_size_gb']:.2f} GB")
    print(f"Has large files: {summary['has_large_files']}")

    if summary["by_classification"]:
        print("\nBy classification:")
        for cls, count in sorted(summary["by_classification"].items()):
            print(f"  {cls}: {count} file(s)")

    print("\n" + "-" * 60)
    print("FILE DETAILS")
    print("-" * 60)

    for rel_path, info in sorted(profile["files"].items()):
        marker = "!!!" if info["classification"] in ("large", "massive") else "   "
        print(f"{marker} {info['file_name']}")
        print(f"    Size: {info['size_gb']:.2f} GB | Class: {info['classification']}")
        print(f"    Library: {info['recommended_library']}")
        print(f"    Read: {info['read_function']}")
        print()

    constraint = detector.get_constraint_message()
    if constraint:
        print("=" * 60)
        print("CONSTRAINT MESSAGE")
        print("=" * 60)
        print(constraint)
        print()

    output_path = detector.save_profile()
    print(f"Profile saved to: {output_path}")


def cmd_hooks(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    try:
        sys.path.insert(0, str(root / ".research" / "core"))
        from hooks import hook_engine
        import interceptors  # noqa: F401
    except ImportError:
        print("ERROR: hooks module not found in .research/core/")
        sys.exit(1)

    hooks = hook_engine.list_hooks()
    log = hook_engine.get_execution_log()

    print("=" * 60)
    print("REGISTERED HOOKS")
    print("=" * 60)
    for hook_name, funcs in hooks.items():
        if funcs:
            print(f"  {hook_name}:")
            for fn in funcs:
                print(f"    - {fn}")
        else:
            print(f"  {hook_name}: (none)")
        print()

    if log:
        print(f"  Execution log: {len(log)} entries")
        for entry in log[-10:]:
            status = "+" if entry["status"] == "success" else "x"
            print(f"    {status} {entry['hook']} -> {entry['interceptor']} ({entry['timestamp']})")
        print()
