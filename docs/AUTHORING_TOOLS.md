# Authoring Custom Tools

Agentic Research OS exposes its capabilities to Claude, Cursor, and Windsurf via the Model Context Protocol (MCP). If you want to give the AI new abilities (e.g., querying your internal database, running a specific simulation engine), you can easily author custom tools.

## Step 1: Create the Python Logic
Create your tool logic in `src/research_copilot/tools/actions/`.

For example, `my_custom_tool.py`:
```python
def analyze_molecule(smiles: str) -> dict:
    """Analyzes a molecule given its SMILES string."""
    # Your custom domain logic here
    return {"status": "success", "smiles": smiles, "molecular_weight": 123.45}
```

## Step 2: Define the Pydantic Schema
Tools in MCP require a rigid JSON-schema definition so the LLM knows exactly what arguments to pass.
Add your schema to `src/research_copilot/schemas/action_schemas.py`:

```python
from pydantic import BaseModel, Field

class AnalyzeMoleculeInput(BaseModel):
    smiles: str = Field(..., description="The SMILES string of the molecule to analyze.")
```

## Step 3: Register the Tool
Open `src/research_copilot/server.py` and register your tool in the MCP server setup block:

```python
from research_copilot.schemas.action_schemas import AnalyzeMoleculeInput
from research_copilot.tools.actions.my_custom_tool import analyze_molecule

@mcp.tool()
def run_analyze_molecule(smiles: str) -> str:
    """Run molecular analysis."""
    result = analyze_molecule(smiles)
    return json.dumps(result)
```

## Step 4: Restart the MCP Server
If you are connected via Cursor or Claude Desktop, you will need to restart the MCP server or restart your IDE so it can fetch the updated `tools/list` registry. The AI will now be able to call `run_analyze_molecule`.
