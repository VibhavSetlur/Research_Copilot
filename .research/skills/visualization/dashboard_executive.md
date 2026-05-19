---
skill_id: "dashboard_executive"
version: "8.0.0"
category: "visualization"
domain_compatibility: ["all"]
required_tools: ["python", "dash", "plotly", "dash-bootstrap-components"]
depends_on: ["viz_design_system", "viz_code_standards", "dashboard_overview"]
produces:
  - "reports/dashboards/executive_dashboard.py"
  - "reports/dashboards/executive_summary.pdf"
complexity: "advanced"
---

# Skill: Executive Summary Dashboard

## Purpose
Generate a high-level dashboard for non-technical stakeholders: key findings, implications, and actionable insights WITHOUT statistical jargon. Plain language. Clear visuals. Actionable takeaways.

## When to Use
- Results need to be communicated to non-researchers
- Policy or business decision support
- Quick overview before deep dive
- Grant reports, stakeholder updates

## When NOT Use
- Only technical audience
- Results not yet finalized
- Findings are preliminary or inconclusive

---

## Design Philosophy

1. **No statistical jargon** — No p-values, CIs, test statistics in labels
2. **Plain language** — Write for a 10th-grade reading level
3. **Action-oriented** — Every finding leads to a recommendation
4. **Visual first** — Numbers support visuals, not the reverse
5. **Honest about uncertainty** — Caveats visible, not hidden

---

## Layout

```
┌─────────────────────────────────────────────────┐
│  [Project Title]                                 │
│  Executive Summary — [Date]                      │
│  "One-sentence summary of the main finding"      │
├─────────────────────────────────────────────────┤
│  KEY FINDINGS                                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │ Finding  │ │ Finding  │ │ Finding  │        │
│  │ 1        │ │ 2        │ │ 3        │        │
│  │ [Big #]  │ │ [Big #]  │ │ [Big #]  │        │
│  │ ↑ or ↓   │ │ ↑ or ↓   │ │ →        │        │
│  └──────────┘ └──────────┘ └──────────┘        │
├─────────────────────────────────────────────────┤
│  WHAT THIS MEANS                                 │
│  ┌───────────────────────────────────────────┐  │
│  │  Visual: Simplified comparison/trend      │  │
│  │  (bar chart, line, or icon-based)         │  │
│  └───────────────────────────────────────────┘  │
│                                                  │
│  Plain language explanation of the main result   │
│  (2-3 sentences, no statistics)                  │
├─────────────────────────────────────────────────┤
│  RECOMMENDATIONS                                 │
│  ┌───────────────────────────────────────────┐  │
│  │ 🔴 HIGH: [Action] — [Why]                 │  │
│  │ 🟡 MEDIUM: [Action] — [Why]               │  │
│  │ 🟢 LOW: [Action] — [Why]                  │  │
│  └───────────────────────────────────────────┘  │
├─────────────────────────────────────────────────┤
│  CAVEATS & LIMITATIONS                           │
│  • [Limitation 1 — plain language]              │
│  • [Limitation 2 — plain language]              │
│  • [What we don't know yet]                     │
├─────────────────────────────────────────────────┤
│  EVIDENCE STRENGTH                               │
│  Finding 1: ████████░░ Strong (80%)             │
│  Finding 2: ██████░░░░ Moderate (60%)           │
│  Finding 3: ████░░░░░░ Preliminary (40%)        │
└─────────────────────────────────────────────────┘
```

---

## Component Specifications

### Finding Card
```python
def create_finding_card(
    finding_number,
    statement,        # Plain language: "Treatment improved outcomes"
    key_number,       # "12%" or "3.2 points"
    direction,        # "up", "down", "no_change"
    evidence_strength, # "strong", "moderate", "preliminary"
    context,          # "Compared to control group"
):
    """Create a finding card for non-technical audience."""
```

### Recommendation Row
```python
def create_recommendation(
    action,           # What to do
    rationale,        # Why (linked to finding)
    priority,         # "high", "medium", "low"
    evidence,         # "strong", "moderate", "preliminary"
):
    """Create a recommendation with priority badge."""
```

### Evidence Bar
```python
def create_evidence_bar(label, strength_pct, strength_label):
    """Create a visual evidence strength indicator."""
```

---

## Visual Standards

### Colors for Executive Dashboard
- **Positive finding**: `#009E73` (green) with ↑ arrow
- **Negative finding**: `#D55E00` (vermillion) with ↓ arrow
- **No change**: `#999999` (gray) with → arrow
- **High priority**: `#D55E00` (vermillion)
- **Medium priority**: `#E69F00` (orange)
- **Low priority**: `#009E73` (green)

### Chart Types (Executive-Friendly)
- **Comparison**: Horizontal bar chart (sorted by value)
- **Trend**: Line chart with clear direction
- **Proportion**: Stacked bar (not pie chart)
- **Distribution**: Simplified histogram with mean line

### Chart Rules
- NO error bars (explain uncertainty in text instead)
- NO statistical annotations
- NO axis truncation for bar charts
- ALWAYS include clear title explaining what the chart shows
- ALWAYS use plain language labels (not variable names)

---

## Plain Language Translation

| Statistical Term | Executive Translation |
|-----------------|----------------------|
| "p < 0.05" | "This finding is statistically reliable" |
| "p > 0.05" | "We cannot confidently say there is a difference" |
| "95% CI [0.2, 0.8]" | "The true effect is likely between 0.2 and 0.8" |
| "R² = 0.45" | "This explains about 45% of the variation" |
| "β = 0.32" | "For each unit increase, the outcome increases by 0.32" |
| "OR = 2.1" | "The odds are about 2 times higher" |
| "Not significant" | "The data does not show a clear effect" |
| "Effect size d = 0.5" | "A moderate difference between groups" |

---

## Evidence Strength Classification

| Strength | Criteria | Visual |
|----------|---------|--------|
| **Strong** | p < 0.01, large effect, robust to sensitivity | ████████░░ (80%) |
| **Moderate** | p < 0.05, medium effect, some sensitivity | ██████░░░░ (60%) |
| **Preliminary** | p < 0.10, small effect, sensitive to specs | ████░░░░░░ (40%) |
| **Inconclusive** | p > 0.10 or conflicting results | ██░░░░░░░░ (20%) |

---

## Export Formats

### PDF Summary
- One-page layout
- Print-ready (300 DPI)
- Includes: findings, recommendations, caveats
- Generated via WeasyPrint or ReportLab

### Presentation Slides
- 3-5 slides maximum
- One finding per slide
- Visual-first, text-minimal
- Export-ready for PowerPoint/Google Slides

---

## Implementation Steps

1. **Extract findings** — From analysis results, identify 3-5 key findings
2. **Translate to plain language** — Remove all statistical jargon
3. **Classify evidence strength** — Based on p-values, effect sizes, robustness
4. **Generate recommendations** — Link each finding to an action
5. **Build dashboard** — Using component architecture from overview dashboard
6. **Create PDF** — One-page executive summary
7. **Validate** — No statistical terms in labels, all findings supported by data

---

## Output Specification
- `reports/dashboards/executive_dashboard.py`: Runnable Dash app
- `reports/dashboards/executive_summary.pdf`: One-page PDF summary

## Validation Checks
- [ ] Zero statistical jargon in visible labels
- [ ] All findings supported by analysis results
- [ ] Evidence strength correctly classified
- [ ] Caveats and limitations prominently displayed
- [ ] Recommendations are actionable and specific
- [ ] Plain language translation accurate
- [ ] PDF renders correctly at print resolution
- [ ] Color choices follow design system
- [ ] Charts are executive-appropriate (no error bars, no annotations)
- [ ] Runs on port 8050 without errors
