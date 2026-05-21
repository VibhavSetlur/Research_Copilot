# Skill: Audit Visualizations

> Audit #8: Run figure validation on every figure in `reports/figures/`.

## Purpose
Automated figure validation that checks DPI, colorblind safety, axis labels, font sizes, and file size. Any figure below standard = FAIL.

---

## Protocol

### Step 1: Scan Figures Directory
1. List all figure files in `reports/figures/`
2. Include subdirectories (e.g., `reports/figures/q1/`)
3. Supported formats: PNG, PDF, SVG
4. Skip: `.gitkeep`, `README.md`

### Step 2: Run Figure Validator
Execute `python -m research_copilot.utils.figure_validator --directory reports/figures/`

For each figure, run checks:

| Check | Standard | Method |
|-------|----------|--------|
| DPI | ≥ 300 | Read image metadata |
| Axis labels | Present | OCR-based detection |
| Colorblind safe | Okabe-Ito palette | Color extraction + palette matching |
| No truncated axes | Origin visible | Axis range analysis |
| Font size | ≥ 8pt | OCR-based font size estimation |
| File size | ≤ 5 MB | File system check |
| No rainbow/jet | Perceptually uniform | Colormap detection |
| No pie charts | N/A | Visual pattern detection |
| No 3D charts | N/A | Visual pattern detection |
| Effect size shown | With p-value | Text annotation detection |
| Confidence intervals | Present | Visual element detection |

### Step 3: Generate Validation Report
Create `reports/audit/visualization_audit.json`:

```json
{
  "schema_version": "1.0.0",
  "timestamp": "ISO 8601",
  "total_figures": 12,
  "summary": {
    "pass": 10,
    "fail": 2,
    "warnings": 3
  },
  "figures": [
    {
      "file": "reports/figures/fig_001_q1_scatter.png",
      "checks": {
        "dpi": {"status": "PASS", "value": 300},
        "axis_labels": {"status": "PASS", "x_label": "X variable", "y_label": "Y variable (units)"},
        "colorblind_safe": {"status": "PASS", "palette": "okabe_ito"},
        "no_truncated_axes": {"status": "PASS"},
        "font_size": {"status": "PASS", "minimum": 10},
        "file_size": {"status": "PASS", "size_mb": 1.2},
        "no_rainbow_colormap": {"status": "PASS"},
        "no_pie_chart": {"status": "PASS"},
        "no_3d_chart": {"status": "PASS"},
        "effect_size_shown": {"status": "PASS", "value": "r=0.42"},
        "confidence_intervals": {"status": "PASS"}
      },
      "overall_status": "PASS"
    },
    {
      "file": "reports/figures/fig_002_q2_bar.png",
      "checks": {
        "dpi": {"status": "FAIL", "value": 150, "required": 300},
        "axis_labels": {"status": "PASS"},
        "colorblind_safe": {"status": "FAIL", "palette": "default_matplotlib"},
        "font_size": {"status": "WARNING", "minimum": 7, "required": 8},
        "overall_status": "FAIL"
      },
      "remediation": {
        "dpi": "Re-render at 300 DPI using saved figure parameters",
        "colorblind_safe": "Re-render with Okabe-Ito substitution"
      }
    }
  ]
}
```

### Step 4: Verdict
- **PASS:** All figures meet all standards
- **CONDITIONAL:** Some figures have warnings (minor issues that don't block)
- **FAIL:** Any figure fails a critical check (DPI, colorblind safety, missing axis labels)

### Step 5: Auto-Healing
If FAIL or CONDITIONAL:
1. For DPI failures: Re-render at 300 DPI using saved figure parameters
2. For colorblind palette violations: Re-render with Okabe-Ito substitution
3. For missing axis labels: Add labels with units
4. For font size warnings: Re-render with larger fonts
5. For rainbow/jet colormaps: Re-render with viridis or perceptually uniform palette
6. Re-run validation after fixes

### Step 6: Generate Summary Report
Create `reports/audit/visualization_audit_summary.md`:
- List of all figures with pass/fail status
- Specific remediation steps for failed figures
- Overall verdict

---

## Integration
- Called by: `audit_validate` agent as Audit #8
- Uses: `figure_validator.py` script
- Outputs to: `reports/audit/visualization_audit.json`
- Blocks manuscript if: FAIL verdict
