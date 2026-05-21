# Skill: Zero-Code Exploratory Analysis with PyGWalker

## Purpose
PyGWalker (Python binding of Graphic Walker) embeds a Tableau-like drag-and-drop explorer interface directly into your Jupyter notebook or exported HTML. It allows researchers to perform high-fidelity exploratory data analysis (EDA) without writing code.

## Installation
```bash
pip install pygwalker
```

## Protocol & Best Practices
1. **Prepare Data First:** Clean datasets, set proper data types, and rename columns to human-readable names prior to initializing PyGWalker.
2. **Export Spec Files:** To save your visualization setup across sessions, always specify a config path using the `spec` parameter so it writes your visual settings to a JSON file.
3. **Use HTML Export for Dashboards:** Generate a standalone HTML report containing the interactive explorer layout for non-technical stakeholders.

## Code Template

```python
import pygwalker as pyg
import pandas as pd
from pathlib import Path

def launch_explorer(df: pd.DataFrame, spec_name: str = "dw_spec.json"):
    """
    Launch interactive Graphic Walker explorer.
    Writes/reads visual specifications to/from a spec JSON file.
    """
    spec_path = Path(".research/cache") / spec_name
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    
    walker = pyg.walk(
        df,
        spec=str(spec_path),
        use_kernel_calc=True,
        show_cloud_tool=False
    )
    return walker

def export_explorer_html(df: pd.DataFrame, output_path: str):
    """
    Exports a standalone HTML page with the full drag-and-drop explorer app.
    """
    pyg.to_html(df, output_path)
    print(f"Explorer exported to standalone HTML: {output_path}")
```
