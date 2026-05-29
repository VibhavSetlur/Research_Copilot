"""Tests for branch-aware path creation (sys_path_create branch_of=...)."""

from pathlib import Path

import pytest

from research_os.project_ops import (
    _extract_path_lineage,
    _max_path_lineage,
    create_numbered_experiment,
    load_state,
    scaffold_minimal_workspace,
)
from research_os.tools.actions.state.path import abandon_path


def _names(workspace: Path) -> set[str]:
    return {p.name for p in workspace.iterdir() if p.is_dir()}


def test_extract_path_lineage_parses_suffix():
    assert _extract_path_lineage("05_glmm") is None
    assert _extract_path_lineage("05_glmm_path_2") == 2
    assert _extract_path_lineage("05_glmm_path_2__DEAD_END") == 2
    assert _extract_path_lineage("05_glmm_alt_path_11") == 11
    assert _extract_path_lineage("not_a_step") is None


def test_main_path_creation_unchanged(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Branch baseline")
    res = create_numbered_experiment(tmp_path, "baseline_eda", hypothesis="H0")
    assert res["path_id"] == "01_baseline_eda"
    assert res["branch_of"] is None
    assert res["path_lineage"] is None
    assert (tmp_path / "workspace" / "01_baseline_eda").is_dir()


def test_branch_off_main_step_gets_path_1_suffix(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Branch fork")
    create_numbered_experiment(tmp_path, "baseline_eda")
    create_numbered_experiment(tmp_path, "logistic")
    # Fork an alternative pipeline off step 02.
    res = create_numbered_experiment(
        tmp_path, "glmm", branch_of="02_logistic"
    )
    assert res["path_id"] == "03_glmm_path_1"
    assert res["path_lineage"] == 1
    assert res["branch_of"] == "02_logistic"
    # data/input of the branch step should symlink to the PARENT's output,
    # not to step 02's output as a sibling. Here those happen to be the
    # same because branch_of=02 IS the parent — verify the symlink target.
    branch_input = tmp_path / "workspace" / "03_glmm_path_1" / "data" / "input"
    parent_output = tmp_path / "workspace" / "02_logistic" / "data" / "output"
    assert branch_input.is_symlink()
    assert branch_input.resolve() == parent_output.resolve()


def test_second_branch_off_same_parent_gets_path_2(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Two branches")
    create_numbered_experiment(tmp_path, "baseline_eda")
    create_numbered_experiment(tmp_path, "logistic")
    create_numbered_experiment(tmp_path, "glmm", branch_of="02_logistic")
    res = create_numbered_experiment(
        tmp_path, "xgboost", branch_of="02_logistic"
    )
    assert res["path_id"] == "04_xgboost_path_2"
    assert res["path_lineage"] == 2


def test_continuation_inherits_branch_lineage(tmp_path):
    """A step branched off a step that already carries a lineage tag
    must INHERIT the lineage, not allocate a new one."""
    scaffold_minimal_workspace(tmp_path, "Lineage flow")
    create_numbered_experiment(tmp_path, "baseline_eda")
    create_numbered_experiment(tmp_path, "logistic")
    create_numbered_experiment(tmp_path, "glmm", branch_of="02_logistic")
    # Now extend the branch — branching off 03_glmm_path_1 should KEEP
    # path_1, because we're walking the same forked path.
    res = create_numbered_experiment(
        tmp_path, "diagnostic", branch_of="03_glmm_path_1"
    )
    assert res["path_id"] == "04_diagnostic_path_1"
    assert res["path_lineage"] == 1
    assert res["branch_of"] == "03_glmm_path_1"


def test_dead_end_suffix_stacks_on_branch_tag(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Dead branch")
    create_numbered_experiment(tmp_path, "baseline_eda")
    create_numbered_experiment(tmp_path, "logistic")
    create_numbered_experiment(tmp_path, "glmm", branch_of="02_logistic")
    res = abandon_path("03_glmm_path_1", "Convergence failed", tmp_path)
    assert res["status"] == "success"
    assert res["renamed_to"] == "03_glmm_path_1__DEAD_END"
    assert (tmp_path / "workspace" / "03_glmm_path_1__DEAD_END").is_dir()
    # Lineage is still recoverable from the new name.
    assert _extract_path_lineage("03_glmm_path_1__DEAD_END") == 1


def test_max_path_lineage_scans_workspace(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Max lineage scan")
    create_numbered_experiment(tmp_path, "baseline_eda")
    create_numbered_experiment(tmp_path, "logistic")
    create_numbered_experiment(tmp_path, "glmm", branch_of="02_logistic")
    create_numbered_experiment(tmp_path, "xgboost", branch_of="02_logistic")
    assert _max_path_lineage(tmp_path / "workspace") == 2


def test_branch_of_unknown_step_raises(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Unknown branch")
    create_numbered_experiment(tmp_path, "baseline_eda")
    with pytest.raises(ValueError, match="branch_of"):
        create_numbered_experiment(
            tmp_path, "glmm", branch_of="99_nonexistent"
        )


def test_state_records_branch_metadata(tmp_path):
    scaffold_minimal_workspace(tmp_path, "State records")
    create_numbered_experiment(tmp_path, "baseline_eda")
    create_numbered_experiment(tmp_path, "logistic")
    create_numbered_experiment(tmp_path, "glmm", branch_of="02_logistic")
    state = load_state(tmp_path)
    branch_entry = state["paths"]["03_glmm_path_1"]
    assert branch_entry["path_lineage"] == 1
    assert branch_entry["branch_of"] == "02_logistic"
    # Main-path entries should NOT have these keys.
    assert "path_lineage" not in state["paths"]["01_baseline_eda"]
    assert "branch_of" not in state["paths"]["01_baseline_eda"]
