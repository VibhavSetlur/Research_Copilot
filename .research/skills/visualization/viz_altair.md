# Skill: Declarative Charts with Altair

## Purpose
Altair is a declarative statistical visualization library for Python, based on the Vega and Vega-Lite visualization grammars. It allows creating interactive, layered charts where the chart specification matches the statistical properties of the data.

## Installation
```bash
pip install altair vega_datasets
```

## Protocol & Best Practices
1. **Use Declarative Mappings:** Define charts by mapping data columns to visual encoding channels (e.g., `x`, `y`, `color`, `size`) rather than drawing shapes manually.
2. **Handle Large Datasets Wisely:** By default, Altair limits dataset size to 5000 rows to prevent bloated HTML. For larger datasets, use `.pre_transform_data()` or enable the JSON data transformer:
   ```python
   import altair as alt
   alt.data_transformers.enable('json')
   ```
3. **Always Set Explicit Data Types:** Append type shorthand to column names to avoid parsing errors:
   - `:Q` for Quantitative (numerical)
   - `:O` for Ordinal (ordered categorical)
   - `:N` for Nominal (unordered categorical)
   - `:T` for Temporal (dates/times)
4. **Color Safe Palettes:** Bind categorical colors to the Okabe-Ito palette.

## Code Template

```python
import altair as alt
import pandas as pd

def create_interactive_scatter(df: pd.DataFrame, x_col: str, y_col: str, color_col: str) -> alt.Chart:
    # Okabe-Ito color palette
    okabe_ito = ["#000000", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7"]
    
    # Selection interval for panning and zooming
    brush = alt.selection_interval(resolve='global')
    
    chart = alt.Chart(df).mark_circle(size=60).encode(
        x=alt.X(f"{x_col}:Q", scale=alt.Scale(zero=False), title=x_col.replace("_", " ").title()),
        y=alt.Y(f"{y_col}:Q", scale=alt.Scale(zero=False), title=y_col.replace("_", " ").title()),
        color=alt.condition(
            brush, 
            alt.Color(f"{color_col}:N", scale=alt.Scale(range=okabe_ito), title=color_col.title()), 
            alt.value('lightgray')
        ),
        tooltip=[x_col, y_col, color_col]
    ).add_params(
        brush
    ).properties(
        width=500,
        height=350,
        title=f"{y_col.title()} vs {x_col.title()}"
    )
    
    return chart
```
