# Skill: Figure Quality Enforcement

## Purpose
Ensures all generated research figures meet publication-quality standards. Running this validation prior to committing outputs prevents cut-off axes, low resolutions, massive file sizes, and non-inclusive color palettes from entering the final manuscript.

## Protocol & Quality Checklist

Before any generated figure is accepted:
1. **DPI Minimum (300 DPI):** Ensure the output image contains metadata specifying at least 300 DPI, or is of equivalent resolution (width $\ge 1200\text{px}$).
2. **Margin Axis Labels:** Verify left and bottom margins contain variance in pixels indicating ticks and labels are present and not missing.
3. **No Axis Truncation:** Ensure non-background pixels do not touch the image edge (preventing layout clipping).
4. **Colorblind Safe Check:** Avoid pure saturated red-green pairings. Restrict categorical elements to the Okabe-Ito palette.
5. **File Size Bounds:** Constrain individual figures to $\le 5\text{MB}$.

## Integration

Run the validator script automatically at the end of visualization steps:
```bash
python -m research_copilot.utils.figure_validator path/to/figure.png
```
If the script returns a `FAIL` (exit code 1), the visual output is rejected, and the pipeline blocks until the plotting code is adjusted (e.g. adding `plt.tight_layout()` or setting correct DPI parameters).
