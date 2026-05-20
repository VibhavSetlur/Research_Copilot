# Skill: Declarative Multi-Dimensional Plotting with HoloViews

## Purpose
HoloViews focuses on declaring data structures (e.g., Curves, Scatters, HeatMaps) rather than writing plotting code. It integrates directly with Bokeh, Matplotlib, and Plotly backends to render complex multi-dimensional relationships instantly.

## Installation
```bash
pip install holoviews panel
```

## Protocol & Best Practices
1. **Declare Dimensions Explicitly:** Annotate dimensions as `kdims` (key dimensions, representing independent variables/indices) and `vdims` (value dimensions, representing dependent variables/metrics).
2. **Utilize Containers:** Use container classes like `Layout`, `Overlay` (for layered figures), and `NdOverlay` (for multidimensional comparison across parameters) to organize figures cleanly.
3. **Switch Backends Gracefully:** Use `hv.extension('bokeh')` or `hv.extension('matplotlib')` at the beginning of the script depending on whether static or interactive export is needed.

## Code Template

```python
import holoviews as hv
import pandas as pd
hv.extension('bokeh')

def create_holoviews_layout(df: pd.DataFrame, x_col: str, y_col: str, group_col: str) -> hv.Layout:
    # Key dimensions (independent) and Value dimensions (dependent)
    kdims = [x_col]
    vdims = [y_col, group_col]
    
    # Create dataset
    ds = hv.Dataset(df, kdims=kdims + [group_col], vdims=y_col)
    
    # Generate overlaid curves grouped by group_col
    curves = ds.to(hv.Curve, x_col, y_col).overlay(group_col)
    
    # Generate scatter points overlay
    points = ds.to(hv.Scatter, x_col, y_col).overlay(group_col)
    
    # Combine curves and points, layout horizontally
    layout = (curves * points).opts(
        hv.opts.Curve(width=500, height=350, tools=['hover'], line_width=2),
        hv.opts.Scatter(size=6, alpha=0.8)
    )
    
    return layout
```
