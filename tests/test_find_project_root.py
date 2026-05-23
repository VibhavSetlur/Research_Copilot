from pathlib import Path
from research_os.utils.asset_manager import AssetManager

def test_find_project_root_no_markers_returns_cwd(tmp_path):
    # Temp path has no .os_state
    root = AssetManager.find_project_root(tmp_path)
    # Fallback is Path.cwd()
    assert root == Path.cwd().resolve()

def test_find_project_root_cwd_returns_cwd():
    # Because .os_state does not exist in repo root, it should fallback to cwd
    root = AssetManager.find_project_root()
    assert root == Path.cwd().resolve()

def test_find_project_root_with_marker(tmp_path):
    # Scaffold .os_state
    os_state_dir = tmp_path / ".os_state"
    os_state_dir.mkdir()
    
    # Check from a deep subfolder
    sub_dir = tmp_path / "workspace" / "01_data"
    sub_dir.mkdir(parents=True)
    
    root = AssetManager.find_project_root(sub_dir)
    assert root == tmp_path.resolve()
