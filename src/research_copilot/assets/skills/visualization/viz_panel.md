# Skill: Dashboard App Development with Panel

## Purpose
Panel provides a Pythonic way to build interactive dashboards and web applications that connect widgets to plots, tables, and computations. It supports any plotting backend and can run both in Jupyter Notebooks and standalone web servers.

## Installation
```bash
pip install panel
```

## Protocol & Best Practices
1. **Component-Based Architecture:** Write dashboards as modular component groups. Avoid single-file monolithic layouts.
2. **Use Reactive Classes:** Leverage `param.Parameterized` or `pn.depends` to bind widget states to rendering functions automatically.
3. **Use Markdown/HTML Templates:** Use native layout features like `pn.Row`, `pn.Column`, and custom HTML templates to make dashboards look premium and clean.

## Code Template

```python
import panel as pn
import pandas as pd
import param
import plotly.express as px

pn.extension()

class ResearchExplorer(param.Parameterized):
    # Setup interactive parameters
    x_metric = param.Selector(objects=[])
    y_metric = param.Selector(objects=[])
    color_by = param.Selector(objects=[])
    
    def __init__(self, df: pd.DataFrame, **params):
        super().__init__(**params)
        self.df = df
        
        # Populate selector parameters dynamically
        cols = list(df.select_dtypes(include='number').columns)
        cat_cols = list(df.select_dtypes(exclude='number').columns)
        
        self.param.x_metric.objects = cols
        self.param.y_metric.objects = cols
        self.param.color_by.objects = cat_cols
        
        # Set default values
        if cols:
            self.x_metric = cols[0]
            self.y_metric = cols[-1] if len(cols) > 1 else cols[0]
        if cat_cols:
            self.color_by = cat_cols[0]

    @pn.depends('x_metric', 'y_metric', 'color_by')
    def view_plot(self):
        fig = px.scatter(
            self.df, 
            x=self.x_metric, 
            y=self.y_metric, 
            color=self.color_by,
            title=f"Plot of {self.y_metric} vs {self.x_metric} color-coded by {self.color_by}"
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig

def build_dashboard(df: pd.DataFrame) -> pn.layout.Column:
    explorer = ResearchExplorer(df)
    
    dashboard = pn.Column(
        pn.pane.Markdown("# Research Explorer Dashboard"),
        pn.Row(
            pn.Column(
                pn.Param(explorer.param, widgets={
                    'x_metric': pn.widgets.Select,
                    'y_metric': pn.widgets.Select,
                    'color_by': pn.widgets.Select
                }),
                width=250
            ),
            explorer.view_plot,
        )
    )
    return dashboard
```
