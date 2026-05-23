"""Global test fixtures — ensures tests never touch the real filesystem."""
import pytest
from pathlib import Path

@pytest.fixture(autouse=True)
def _isolate_find_project_root(request, monkeypatch, tmp_path):
    """Force find_project_root to return a temp directory, never the real cwd."""
    if "test_find_project_root.py" in str(request.node.fspath):
        return

    from research_os.utils import asset_manager

    def _fake_find_project_root(start=None):
        if start is not None:
            return Path(start)
        return tmp_path

    monkeypatch.setattr(
        asset_manager.AssetManager, "find_project_root",
        staticmethod(_fake_find_project_root),
    )
    monkeypatch.setattr(
        "research_os.utils.common.find_project_root",
        _fake_find_project_root,
    )
    monkeypatch.setattr(
        "research_os.state.state_ledger.find_project_root",
        _fake_find_project_root,
    )
    monkeypatch.setattr(
        "research_os.state.checkpoint_manager.find_project_root",
        _fake_find_project_root,
    )
