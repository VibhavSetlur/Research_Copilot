# Skill: 3D Response Surface Plots with Plotly

## Purpose
3D response surfaces are designed to visualize statistical response models, optimization spaces, or parameter sweeps where the output depends on two continuous variables. 

## Protocol & Best Practices
1. **Never Decorative:** Do not use 3D plots for simple multi-category distributions or basic tables where a 2D heatmap or faceted layout would convey the same information. Only use 3D when modeling a continuous response function $z = f(x, y)$.
2. **Include 2D Projection Contours:** Always project contour lines onto the bottom plane of the 3D box so the quantitative values can be read without perspective distortion.
3. **Use Perceptually Uniform Colormaps:** Apply uniform continuous colormaps like `viridis`, `magma`, or `plasma`. Never use `rainbow` or `jet`.

## Code Template

```python
import plotly.graph_objects as go
import numpy as np
import pandas as pd

def create_response_surface(x_grid: np.ndarray, y_grid: np.ndarray, z_matrix: np.ndarray, 
                            x_label: str, y_label: str, z_label: str, output_path: str):
    fig = go.Figure(data=[go.Surface(
        z=z_matrix, 
        x=x_grid, 
        y=y_grid,
        colorscale='Viridis',
        contours = {
            # Project contours onto z-axis (bottom plane)
            "z": {"show": True, "start": float(z_matrix.min()), "end": float(z_matrix.max()), "size": (z_matrix.max()-z_matrix.min())/10, "project": {"z": True}}
        }
    )])
    
    fig.update_layout(
        title=f"Response Surface for {z_label}",
        scene = {
            "xaxis_title": x_label,
            "yaxis_title": y_label,
            "zaxis_title": z_label,
        },
        autosize=False,
        width=800,
        height=600,
        margin=dict(l=65, r=50, b=65, t=90)
    )
    
    fig.write_html(output_path)
    print(f"Generated 3D Response Surface: {output_path}")
```
