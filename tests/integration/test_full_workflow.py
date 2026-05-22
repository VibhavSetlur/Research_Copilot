import os
import json
import pytest
from pathlib import Path
from research_os.server import _handle_tool_call

@pytest.fixture
def workspace_root(tmp_path):
    root = tmp_path / "test_workspace"
    root.mkdir()
    # Write a dummy config
    inputs_dir = root / "inputs"
    inputs_dir.mkdir()
    config = 'researcher: {name: "Test"}\nmodel_profile: "large"'
    (inputs_dir / "researcher_config.yaml").write_text(config)
    
    # Write dummy CSV
    raw_dir = inputs_dir / "raw_data"
    raw_dir.mkdir()
    (raw_dir / "dummy.csv").write_text("x,y\n1,2\n3,4\n5,6")
    
    # Write dummy protocol
    proto_dir = root / "src" / "research_os" / "protocols"
    proto_dir.mkdir(parents=True, exist_ok=True)
    proto_content = "name: domain_analysis\ndescription: test\nsteps: []\n"
    (proto_dir / "domain_analysis.yaml").write_text(proto_content)
    
    return root

def test_full_workflow(workspace_root):
    root = workspace_root
    
    # 1. Initialize project
    res = _handle_tool_call("sys.workspace.scaffold", {"project_name": "Test Project"}, root)
    assert "success" in res[0].text
    
    # 2. Get guidance
    res = _handle_tool_call("sys.guidance.get", {"protocol_name": "domain_analysis"}, root)
    assert "success" in res[0].text
    
    # 3. Create branch
    res = _handle_tool_call("sys.branch.create", {"name": "test_branch", "hypothesis": "Test H"}, root)
    assert "success" in res[0].text
    
    # 4. Write script
    script_content = """import csv
import os
with open('../inputs/raw_data/dummy.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)
    total = sum(int(row[0]) + int(row[1]) for row in reader)
os.makedirs('data/derived', exist_ok=True)
with open('data/derived/result.txt', 'w') as f:
    f.write(str(total))
"""
    # Need to create the script file
    res = _handle_tool_call("sys.file.write", {"filepath": "workspace/analysis.py", "content": script_content}, root)
    assert "success" in res[0].text
    
    # 5. Run script
    res = _handle_tool_call("tool.python.exec", {"script_path": "workspace/analysis.py"}, root)
    assert "success" in res[0].text
    
    # Check derived data
    derived_path = root / "workspace" / "data" / "derived" / "result.txt"
    assert derived_path.exists()
    
    # 6. Log findings
    res = _handle_tool_call("mem.analysis.log", {"entry": "The sum is 21."}, root)
    assert "success" in res[0].text
    
    # 7. Synthesize paper
    paper_content = """# Title
Abstract
This is a test abstract.

Methods
Data was summed.

Results
The sum is 21.

Discussion
This proves our hypothesis. (Oops causal language)

References
[1] Smith et al.
"""
    res = _handle_tool_call("sys.file.write", {"filepath": "synthesis/paper.md", "content": paper_content}, root)
    assert "success" in res[0].text
    
    # 8. Audit synthesis
    res = _handle_tool_call("tool.audit.synthesis", {"paper_path": "synthesis/paper.md"}, root)
    assert "warning" in res[0].text or "success" in res[0].text
    
    audit_data = json.loads(res[0].text)
    assert len(audit_data.get("data", {}).get("report", {}).get("causal_language_found", [])) > 0
