#!/usr/bin/env python3
"""
Research Copilot Parallel Runner
Executes independent analysis tasks/scripts concurrently using asyncio subprocesses.
Ensures process isolation, logging, and concurrency control.

CLI usage:
  # From tasks JSON file:
  python parallel_runner.py --tasks tasks.json --max-workers 4

  # From question IDs (generates tasks from research map):
  python parallel_runner.py --questions q1,q2,q3 --max-workers 4
"""

import os
import sys
import json
import asyncio
import argparse
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple


class FileLock:
    def __init__(self, lock_path: Path):
        self.lock_path = lock_path
        self.fd = None

    def acquire(self):
        start_time = time.time()
        while True:
            try:
                if sys.platform == 'win32':
                    if self.lock_path.exists():
                        raise OSError("Lock file exists")
                    self.lock_path.write_text(str(os.getpid()))
                else:
                    self.fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                    os.write(self.fd, str(os.getpid()).encode())
                return True
            except (OSError, FileExistsError):
                if time.time() - start_time > 10:
                    raise TimeoutError(f"Could not acquire lock on {self.lock_path}")
                time.sleep(0.1)

    def release(self):
        try:
            if sys.platform == 'win32':
                if self.lock_path.exists():
                    self.lock_path.unlink()
            else:
                if self.fd is not None:
                    os.close(self.fd)
                    self.fd = None
                if self.lock_path.exists():
                    self.lock_path.unlink()
        except OSError:
            pass


from research_copilot.utils.common import find_project_root


def build_tasks_from_questions(questions: List[str], root: Path) -> List[Dict[str, Any]]:
    """Build task list from question IDs by reading the research map."""
    research_map_path = root / ".research" / "cache" / "research_map.json"
    if not research_map_path.exists():
        research_map_path = root / "03_synthesis" / "research_map.json"

    if not research_map_path.exists():
        print(f"ERROR: Research map not found. Run 'research scan' first.")
        sys.exit(1)

    with open(research_map_path) as f:
        research_map = json.load(f)

    questions_data = research_map.get("questions", [])
    tasks = []

    for q_id in questions:
        q_id_clean = q_id.strip().lower()
        # Match q1, q2, etc.
        q_num = q_id_clean.lstrip("q")

        matched = None
        for q in questions_data:
            q_text = q.get("text", "").lower()
            q_idx = questions_data.index(q) + 1
            if q_id_clean == f"q{q_idx}" or q_id_clean == str(q_idx):
                matched = q
                break

        if matched is None and questions_data:
            # Try positional match
            try:
                idx = int(q_num) - 1
                if 0 <= idx < len(questions_data):
                    matched = questions_data[idx]
            except ValueError:
                pass

        if matched:
            q_idx = questions_data.index(matched) + 1
            task = {
                "id": f"q{q_idx}",
                "command": f"{sys.executable} .research/scripts/utils/run_analysis.py --question q{q_idx}",
                "output_dir": str(root / "03_synthesis" / "analysis" / f"q{q_idx}"),
                "log_file": str(root / "03_synthesis" / "analysis" / f"q{q_idx}" / "task.log"),
            }
            tasks.append(task)
        else:
            print(f"WARNING: Question '{q_id}' not found in research map, skipping.")

    return tasks


async def run_single_task(task: Dict[str, Any], semaphore: asyncio.Semaphore) -> Dict[str, Any]:
    """Run a single task subprocess under semaphore control."""
    task_id = task.get("id", "unknown")
    command = task.get("command")
    output_dir = Path(task.get("output_dir", "."))
    log_file = Path(task.get("log_file", output_dir / f"task_{task_id}.log"))

    if not command:
        return {
            "id": task_id,
            "success": False,
            "error": "No command specified",
            "returncode": -1,
            "elapsed": 0.0
        }

    output_dir.mkdir(parents=True, exist_ok=True)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    if isinstance(command, str):
        import shlex
        cmd_args = shlex.split(command)
    else:
        cmd_args = [str(x) for x in command]

    async with semaphore:
        print(f"[RUNNING] Task {task_id}: {' '.join(cmd_args)}")
        start_time = time.time()

        try:
            with open(log_file, "w") as log_fd:
                process = await asyncio.create_subprocess_exec(
                    cmd_args[0],
                    *cmd_args[1:],
                    stdout=log_fd,
                    stderr=log_fd,
                    env=os.environ.copy()
                )
                await process.wait()
                returncode = process.returncode

            elapsed = time.time() - start_time

            if returncode == 0:
                print(f"[SUCCESS] Task {task_id} completed in {elapsed:.2f}s")
                return {
                    "id": task_id,
                    "success": True,
                    "returncode": 0,
                    "elapsed": elapsed,
                    "log_file": str(log_file)
                }
            else:
                print(f"[FAILED] Task {task_id} exited with code {returncode} (see log: {log_file})")
                return {
                    "id": task_id,
                    "success": False,
                    "returncode": returncode,
                    "elapsed": elapsed,
                    "log_file": str(log_file),
                    "error": f"Exit code {returncode}"
                }

        except Exception as e:
            elapsed = time.time() - start_time
            error_msg = str(e)
            print(f"[ERROR] Task {task_id} failed to launch: {error_msg}")

            try:
                with open(log_file, "w") as log_fd:
                    log_fd.write(f"Launch error: {error_msg}\n")
            except Exception:
                pass

            return {
                "id": task_id,
                "success": False,
                "returncode": -2,
                "elapsed": elapsed,
                "log_file": str(log_file),
                "error": error_msg
            }


async def run_parallel_tasks_async(tasks: List[Dict[str, Any]], max_workers: int) -> List[Dict[str, Any]]:
    """Run all tasks in parallel using asyncio Semaphores."""
    semaphore = asyncio.Semaphore(max_workers)
    tasks_to_run = [run_single_task(task, semaphore) for task in tasks]
    return await asyncio.gather(*tasks_to_run)


def run_parallel_tasks(tasks: List[Dict[str, Any]], max_workers: int = 4) -> List[Dict[str, Any]]:
    """Python API to run independent tasks concurrently."""
    return asyncio.run(run_parallel_tasks_async(tasks, max_workers))


def main():
    parser = argparse.ArgumentParser(description="Research Copilot Parallel Subprocess Runner")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--tasks", help="Path to JSON file containing tasks list")
    group.add_argument("--questions", help="Comma-separated question IDs (q1,q2,q3)")

    parser.add_argument("--max-workers", type=int, default=4, help="Maximum number of parallel workers")
    parser.add_argument("--state-ledger", help="Optional path to state.json ledger to update atomically")

    args = parser.parse_args()

    root = find_project_root()

    # Build task list
    if args.tasks:
        tasks_path = Path(args.tasks)
        if not tasks_path.exists():
            print(f"ERROR: Tasks file not found: {tasks_path}")
            sys.exit(1)

        try:
            with open(tasks_path) as f:
                tasks = json.load(f)
        except Exception as e:
            print(f"ERROR: Failed to parse tasks JSON: {e}")
            sys.exit(1)

        if not isinstance(tasks, list):
            print("ERROR: Tasks JSON must be a list of task objects")
            sys.exit(1)
    else:
        question_list = [q.strip() for q in args.questions.split(",") if q.strip()]
        tasks = build_tasks_from_questions(question_list, root)

    if not tasks:
        print("ERROR: No tasks to run.")
        sys.exit(1)

    print("=" * 60)
    print(f"PARALLEL WORKER ENGINE STARTING")
    print(f"  Total tasks: {len(tasks)}")
    print(f"  Max workers: {args.max_workers}")
    print("=" * 60)

    start_time = time.time()
    results = run_parallel_tasks(tasks, args.max_workers)
    total_elapsed = time.time() - start_time

    success_count = sum(1 for r in results if r["success"])
    fail_count = len(results) - success_count

    print("=" * 60)
    print("PARALLEL WORKER ENGINE COMPLETE")
    print(f"  Completed: {success_count} succeeded, {fail_count} failed")
    print(f"  Total time: {total_elapsed:.2f}s")
    print("=" * 60)

    # Optional state.json ledger update with locking
    if args.state_ledger:
        ledger_path = Path(args.state_ledger)
        if ledger_path.exists():
            lock_path = ledger_path.with_suffix(".lock")
            lock = FileLock(lock_path)
            try:
                lock.acquire()
                with open(ledger_path) as lf:
                    ledger_data = json.load(lf)

                if "parallel_runs" not in ledger_data:
                    ledger_data["parallel_runs"] = []

                ledger_data["parallel_runs"].append({
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "total_tasks": len(tasks),
                    "success": fail_count == 0,
                    "results": results
                })

                with open(ledger_path, "w") as lf:
                    json.dump(ledger_data, lf, indent=2)
            except Exception as le:
                print(f"WARNING: Failed to update state ledger: {le}")
            finally:
                lock.release()

    # Save results for synthesizer pick up
    results_path = root / "03_synthesis" / "analysis" / "parallel_results.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(results_path, "w") as f:
            json.dump({
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "total_tasks": len(tasks),
                "success": fail_count == 0,
                "elapsed": total_elapsed,
                "results": results
            }, f, indent=2)
        print(f"Results log saved to: {results_path}")
    except Exception as e:
        print(f"WARNING: Could not save results file: {e}")

    if fail_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
