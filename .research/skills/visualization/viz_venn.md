# Skill: Venn Diagram Set Overlap Plotting

## Purpose
Set overlap visualization displays relationships, intersections, and exclusive counts across multiple categorical lists or cohorts. It provides structured insights into sample similarities, gene enrichment overlap, or feature overlap.

## Installation
```bash
pip install matplotlib-venn
```

## Protocol & Best Practices
1. **Limit Sets to Three:** Venn diagrams become unreadable and lose proportional geometric meaning when representing more than 3 sets. For 4 or more sets, use UpSet plots (`upsetplot`) instead.
2. **Always Use Proportional Layouts:** Use `venn2` and `venn3` to construct layouts where circle areas correspond proportionally to subset sizes.
3. **Okabe-Ito Colors:** Style overlapping areas using transparency and colors from the project palette.

## Code Template

```python
import matplotlib.pyplot as plt
from matplotlib_venn import venn3
from typing import Set

def plot_cohort_overlap(set_a: Set[Any], set_b: Set[Any], set_c: Set[Any], 
                        label_a: str, label_b: str, label_c: str, output_path: str):
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Custom palette
    color_a = "#E69F00"
    color_b = "#56B4E9"
    color_c = "#009E73"
    
    v = venn3(
        [set_a, set_b, set_c],
        set_labels=(label_a, label_b, label_c),
        ax=ax
    )
    
    # Apply theme styling
    if v.get_patch_by_id('100'): v.get_patch_by_id('100').set_color(color_a)
    if v.get_patch_by_id('010'): v.get_patch_by_id('010').set_color(color_b)
    if v.get_patch_by_id('001'): v.get_patch_by_id('001').set_color(color_c)
    
    # Add titles and labels
    ax.set_title("Cohort Sample Overlap Analysis", fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
```
