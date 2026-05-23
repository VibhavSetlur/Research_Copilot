"""Tests for state ledger operations — checkpoints, branches, load/save."""

from pathlib import Path


from research_os.project_ops import (
    default_state,
    load_state,
    save_state,
    scaffold_minimal_workspace,
    create_numbered_experiment,
)
from research_os.state.state_ledger import ResearchLedger
from research_os.tools.actions.checkpoint import (
    create_checkpoint,
    rollback_checkpoint,
    list_checkpoints,
)


# ── Helpers ──────────────────────────────────────────────────────────


def _ensure_findable(tmp_path: Path) -> None:
    """Create a marker directory so find_project_root resolves to tmp_path."""
    (tmp_path / "inputs").mkdir(parents=True, exist_ok=True)


# ── Default state ────────────────────────────────────────────────────


def test_default_state_structure():
    """default_state() returns a dict with all expected keys."""
    state = default_state()
    assert state["schema_version"] == "2.0"
    assert state["current_path"] == "main"
    assert "main" in state["paths"]
    assert "project_id" in state
    assert "created_at" in state
    assert "pipeline_stage" in state
    assert state["pipeline_stage"] == "init"


def test_load_state_returns_default_for_empty_workspace(tmp_path):
    """load_state returns a default state dict when no state file exists.

    This simulates a fresh workspace that has the marker directory
    but no .os_state/state_ledger.json yet.
    """
    _ensure_findable(tmp_path)
    state = load_state(tmp_path)
    # load_state delegates to ResearchLedger._load() which returns
    # ResearchLedger._default_state() — different from project_ops.default_state()
    assert "run_id" in state
    assert "phase" in state
    assert "paths" in state
    assert "main" in state["paths"]
    assert state.get("current_path") == "main"


# ── Load / Save cycle ────────────────────────────────────────────────


def test_save_then_load_preserves_state(tmp_path):
    """State written via save_state is readable via load_state."""
    scaffold_minimal_workspace(tmp_path, "Test Project")
    state = load_state(tmp_path)
    state["step"] = 7
    save_state(tmp_path, state)

    reloaded = load_state(tmp_path)
    assert reloaded["step"] == 7
    assert reloaded["project_name"] == "Test Project"


def test_save_state_sets_updated_at(tmp_path):
    """save_state assigns a new updated_at timestamp."""
    scaffold_minimal_workspace(tmp_path, "Test")
    state = load_state(tmp_path)
    saved = save_state(tmp_path, state)
    assert "updated_at" in saved
    assert saved["updated_at"] is not None


def test_save_state_writes_diff_log(tmp_path):
    """save_state writes a diff entry to workspace/logs/state_changes.log."""
    scaffold_minimal_workspace(tmp_path, "Test")
    state = load_state(tmp_path)
    state["step"] = 99
    save_state(tmp_path, state)

    log = tmp_path / "workspace" / "logs" / "state_changes.log"
    assert log.exists()
    content = log.read_text()
    assert "99" in content


# ── ResearchLedger direct API ────────────────────────────────────────


def test_ledger_returns_default_state_when_no_file(tmp_path):
    """ResearchLedger.get() returns the built-in default when no file exists."""
    ledger = ResearchLedger(tmp_path / ".os_state" / "state_ledger.json")
    state = ledger.get()
    assert "run_id" in state
    assert state["phase"] == "domain_analysis"
    assert state.get("current_path") == "main"


def test_ledger_update_persists_values(tmp_path):
    """ResearchLedger.update saves key-value pairs atomically."""
    ledger = ResearchLedger(tmp_path / ".os_state" / "state_ledger.json")
    ledger.update(phase="data_collection", step=2)
    state = ledger.get()
    assert state["phase"] == "data_collection"
    assert state["step"] == 2
    assert state["updated_at"] is not None


def test_ledger_phase_lifecycle(tmp_path):
    """set_phase → complete_phase round-trips correctly."""
    ledger = ResearchLedger(tmp_path / ".os_state" / "state_ledger.json")
    ledger.set_phase("analysis", step=3)
    assert ledger.get()["phase"] == "analysis"
    assert ledger.get()["checkpoints"]["analysis"] == "in_progress"

    ledger.complete_phase("analysis")
    s = ledger.get()
    assert s["checkpoints"]["analysis"] == "complete"
    assert s["resumable_from"] == "analysis"


# ── Checkpoint operations ────────────────────────────────────────────


def test_checkpoint_create_returns_success(tmp_path):
    """create_checkpoint returns success with a checkpoint_id."""
    scaffold_minimal_workspace(tmp_path, "Test")
    result = create_checkpoint("test checkpoint", root=tmp_path)
    assert result["status"] == "success"
    assert "checkpoint_id" in result
    assert result["checkpoint_id"]


def test_checkpoint_list_after_create(tmp_path):
    """list_checkpoints includes newly created checkpoints."""
    scaffold_minimal_workspace(tmp_path, "Test")
    create_checkpoint("first", root=tmp_path)
    result = list_checkpoints(root=tmp_path)
    assert result["status"] == "success"
    assert len(result["checkpoints"]) >= 1


def test_checkpoint_rollback_restores_workspace(tmp_path):
    """rollback_checkpoint restores files from the workspace snapshot."""
    scaffold_minimal_workspace(tmp_path, "Test")
    note = tmp_path / "workspace" / "note.md"
    note.write_text("original")

    cp = create_checkpoint("snapshot", root=tmp_path)
    cp_id = cp["checkpoint_id"]

    note.write_text("modified")
    assert note.read_text() == "modified"

    rb = rollback_checkpoint(cp_id, root=tmp_path)
    assert rb["status"] == "success"
    assert note.read_text() == "original"


def test_checkpoint_rollback_nonexistent(tmp_path):
    """Rolling back to a non-existent checkpoint returns an error."""
    scaffold_minimal_workspace(tmp_path, "Test")
    result = rollback_checkpoint("ghost", root=tmp_path)
    assert result["status"] == "error"


# ── Branch operations (via create_numbered_experiment) ────────────────


def test_path_create_adds_to_state(tmp_path):
    """create_numbered_experiment creates a new path and updates state."""
    scaffold_minimal_workspace(tmp_path, "Test")
    res = create_numbered_experiment(tmp_path, "data_prep", hypothesis="Clean data")
    state = load_state(tmp_path)
    assert res["path_id"] in state["paths"]
    assert state["current_path"] == res["path_id"]



# ── Nested state operations ──────────────────────────────────────────


def test_ledger_add_hypothesis(tmp_path):
    """add_hypothesis appends to active_hypotheses and can update status."""
    ledger = ResearchLedger(tmp_path / ".os_state" / "state_ledger.json")
    ledger.add_hypothesis("H1", status="testing", effect=0.5)
    state = ledger.get()
    assert any(
        h["id"] == "H1" and h["status"] == "testing" for h in state["active_hypotheses"]
    )

    ledger.add_hypothesis("H1", status="confirmed")
    state = ledger.get()
    h1 = next(h for h in state["active_hypotheses"] if h["id"] == "H1")
    assert h1["status"] == "confirmed"


def test_ledger_add_dead_end_deduplicates(tmp_path):
    """add_dead_end prevents duplicate entries in the dead_ends list."""
    ledger = ResearchLedger(tmp_path / ".os_state" / "state_ledger.json")
    ledger.add_dead_end("approach_A")
    ledger.add_dead_end("approach_A")
    state = ledger.get()
    assert state["dead_ends"] == ["approach_A"]


def test_ledger_track_tokens(tmp_path):
    """track_tokens updates the token budget correctly."""
    ledger = ResearchLedger(tmp_path / ".os_state" / "state_ledger.json")
    ledger.track_tokens(used=5000, limit=100000)
    state = ledger.get()
    assert state["token_budget"]["used"] == 5000
    assert state["token_budget"]["remaining"] == 95000
    assert state["token_budget"]["limit"] == 100000


def test_ledger_add_loaded_data(tmp_path):
    """add_loaded_data appends paths to loaded_data."""
    ledger = ResearchLedger(tmp_path / ".os_state" / "state_ledger.json")
    ledger.add_loaded_data("inputs/raw_data/dataset.csv")
    state = ledger.get()
    assert "inputs/raw_data/dataset.csv" in state["loaded_data"]


def test_ledger_get_latest_ctm_returns_none_when_empty(tmp_path):
    """get_latest_ctm returns None when no CTMs exist."""
    ledger = ResearchLedger(tmp_path / ".os_state" / "state_ledger.json")
    assert ledger.get_latest_ctm() is None


def test_ledger_save_and_get_ctm(tmp_path):
    """save_ctm stores a CTM and get_latest_ctm retrieves it."""
    ledger = ResearchLedger(tmp_path / ".os_state" / "state_ledger.json")
    ctm_data = {
        "phase": "analysis",
        "token_usage_pct": 0.92,
        "abandoned_paths": ["approach_A"],
        "micro_decisions": ["Used Mann-Whitney U"],
        "immediate_goals": ["Complete report"],
        "partial_results": ["p-value computed"],
        "open_questions": ["Why outlier?"],
        "handoff_notes": "Check residuals.",
    }
    ledger.save_ctm(ctm_data)
    ctm = ledger.get_latest_ctm()
    assert ctm is not None
    assert ctm["phase"] == "analysis"
    assert ctm["token_usage_pct"] == 0.92
    assert "ctm_id" in ctm
    assert ctm["generated_at"] is not None
