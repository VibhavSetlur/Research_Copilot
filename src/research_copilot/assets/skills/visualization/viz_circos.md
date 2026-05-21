# Skill: Genomic & Network Circular Layouts (Circos)

## Purpose
Genomic and high-dimensional network datasets are often best represented in circular layouts (Circos style), enabling the depiction of relationships between multiple chromosomes, loci, or network groups in a single dense figure.

## Installation
```bash
pip install pycirclize
```

## Protocol & Best Practices
1. **Define Rings and Tracks:** Structure sectors representing genome chromosomes or network modules, then place concentric track layers containing histograms, scatters, or heatmaps within those sectors.
2. **Establish Chord Links:** Draw links inside the circle to represent structural variations, correlation linkages, or flow between regions.
3. **Limit High Density:** Overly cluttered Circos plots lose informational value. Filter links using statistical significance thresholds (e.g. correlation $|r| > 0.6$ or FDR $p < 0.05$) before drawing chords.

## Code Template

```python
from pycirclize import Circos
import pandas as pd
import matplotlib.pyplot as plt

def create_circular_network_plot(nodes_df: pd.DataFrame, links_df: pd.DataFrame, output_path: str):
    # nodes_df: name, size
    # links_df: source, target, weight
    
    sectors = {row["name"]: row["size"] for _, row in nodes_df.iterrows()}
    circos = Circos(sectors, space=5)
    
    # Style tracks
    for sector in circos.sectors:
        track = sector.add_track((95, 100))
        track.rect(fill_color="#56B4E9", line_color="black")
        track.text(sector.name, color="black", r=108, size=10)
    
    # Plot links between nodes
    for _, link in links_df.iterrows():
        src = link["source"]
        tgt = link["target"]
        w = link["weight"]
        
        # Color chord by weight
        color = "#D55E00" if w > 0 else "#0072B2"
        
        # Draw link chord
        circos.link((src, 0, sectors[src]), (tgt, 0, sectors[tgt]), color=color, alpha=0.6)
        
    fig = circos.plotfig()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
```
