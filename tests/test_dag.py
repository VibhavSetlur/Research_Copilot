import pytest
from pathlib import Path
from research_os.utils.dag_manager import ExecutionDAGManager

def test_dag_manager_initialization(tmp_path):
    """Test that the DAG manager initializes correctly."""
    dag_manager = ExecutionDAGManager(tmp_path)
    assert dag_manager.dag_path.exists()
    dag = dag_manager.get_dag() if hasattr(dag_manager, "get_dag") else dag_manager._load()
    assert "nodes" in dag
    assert "edges" in dag

def test_add_node(tmp_path):
    """Test adding a node to the DAG."""
    dag_manager = ExecutionDAGManager(tmp_path)
    node_id = dag_manager.add_node(
        node_id="test_node_01",
        script_path="test_script.py",
        input_files=[],
        output_files=[],
        status="pending",
        depends_on=["parent_node"]
    )
    assert node_id["node_id"] == "test_node_01"
    
    dag = dag_manager.get_dag() if hasattr(dag_manager, "get_dag") else dag_manager._load()
    assert "test_node_01" in dag["nodes"]
    assert dag["nodes"]["test_node_01"]["status"] == "pending"
    assert "parent_node" in dag["nodes"]["test_node_01"]["depends_on"]

def test_update_node_status(tmp_path):
    """Test updating the status of an existing node."""
    dag_manager = ExecutionDAGManager(tmp_path)
    dag_manager.add_node(
        node_id="test_node",
        script_path="test.py",
        input_files=[],
        output_files=[],
        status="pending"
    )
    
    # We update status directly by modifying dag since there's no update_node_status method natively
    dag = dag_manager._load()
    dag["nodes"]["test_node"]["status"] = "success"
    dag["nodes"]["test_node"]["result"] = {"key": "value"}
    dag_manager._save(dag)
    
    dag = dag_manager._load()
    assert dag["nodes"]["test_node"]["status"] == "success"
    assert dag["nodes"]["test_node"]["result"] == {"key": "value"}
