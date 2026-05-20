# Skill: High-Performance Interactive Plots with Bokeh

## Purpose
Bokeh is a powerful library for creating interactive, browser-ready visualizations. It excels at handling very large or streaming datasets and supports custom JavaScript callbacks for low-latency client-side interaction.

## Installation
```bash
pip install bokeh
```

## Protocol & Best Practices
1. **Always Use ColumnDataSource:** Bind data to a `ColumnDataSource` to enable seamless hover tooltips, selections, and synchronization.
2. **Explicitly Configure Tools:** Enable specific tools (e.g., pan, box_zoom, wheel_zoom, reset, hover, save) and disable unnecessary ones.
3. **Format Tooltips Nicely:** Use HTML/CSS within `HoverTool` to present high-density, readable hover cards.
4. **Theme Alignment:** Apply a consistent theme (background colors, grid line patterns, fonts) matching the project design system.

## Code Template

```python
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.io import output_file
import pandas as pd

def create_bokeh_scatter(df: pd.DataFrame, x_col: str, y_col: str, label_col: str, output_path: str):
    output_file(output_path)
    
    source = ColumnDataSource(df)
    
    # Setup hover tools
    hover = HoverTool(tooltips="""
        <div style="padding: 5px; font-family: sans-serif;">
            <strong>@{%s}</strong><br>
            %s: @{%s}{0.00}<br>
            %s: @{%s}{0.00}
        </div>
    """ % (label_col, x_col, x_col, y_col, y_col))
    
    p = figure(
        title=f"{y_col.title()} vs {x_col.title()}",
        x_axis_label=x_col.replace("_", " ").title(),
        y_axis_label=y_col.replace("_", " ").title(),
        tools=["pan,box_zoom,wheel_zoom,reset,save", hover],
        width=600,
        height=400
    )
    
    # Styled according to project rules
    p.background_fill_color = "#FAFAFA"
    p.grid.grid_line_color = "#E5E5E5"
    
    p.circle(
        x=x_col, 
        y=y_col, 
        size=10, 
        source=source, 
        color="#0072B2", 
        alpha=0.7, 
        hover_color="#D55E00"
    )
    
    return p
```
