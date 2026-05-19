---
skill_id: "prisma_flow_diagram"
version: "1.0.0"
category: "visualization"
domain_compatibility: ["all"]
required_tools: ["python", "matplotlib", "graphviz"]
depends_on: ["viz_design_system", "viz_code_standards"]
produces: ["reports/figures/prisma_diagram.png", "reports/figures/prisma_diagram.svg"]
complexity: "intermediate"
---

# Skill: PRISMA Flow Diagram

## Purpose
Generate a PRISMA 2020-compliant flow diagram showing the study selection process from identification through inclusion. Required for systematic reviews and meta-analyses.

## When to Use
- After literature pipeline completes
- For systematic review manuscripts
- When reporting study selection process

## When NOT to Use
- Not a systematic review
- Literature search not yet complete

---

## PRISMA 2020 Flow Structure

```
┌─────────────────────────────────┐
│         IDENTIFICATION          │
│                                 │
│ Records identified from:        │
│   Databases (n = XXX)           │
│   Registers (n = XXX)           │
│                                 │
│ Total records: n = XXX          │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│         SCREENING               │
│                                 │
│ Records screened: n = XXX       │
│ Records excluded: n = XXX       │
│   (reasons listed)              │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│        SOUGHT FOR RETRIEVAL     │
│                                 │
│ Reports sought for retrieval:   │
│   n = XXX                       │
│ Reports not retrieved: n = XXX  │
│   (reasons)                     │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│         ASSESSED                │
│                                 │
│ Reports assessed for            │
│   eligibility: n = XXX          │
│ Reports excluded: n = XXX       │
│   Reason 1 (n = XX)             │
│   Reason 2 (n = XX)             │
│   Reason 3 (n = XX)             │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│         INCLUDED                │
│                                 │
│ Studies included in review:     │
│   n = XXX                       │
│ Studies included in meta-       │
│   analysis: n = XXX             │
└─────────────────────────────────┘
```

---

## Implementation

### Data Input
Read from `reports/literature/prisma_flow.json`:
```json
{
  "identification": {
    "databases": 234,
    "registers": 45,
    "other_sources": 23,
    "total": 302
  },
  "deduplication": {
    "duplicates_removed": 81,
    "after_dedup": 221
  },
  "screening": {
    "screened": 221,
    "excluded": 145,
    "exclusion_reasons": {
      "not relevant topic": 78,
      "wrong study design": 34,
      "wrong population": 23,
      "not peer reviewed": 10
    }
  },
  "retrieval": {
    "sought": 76,
    "not_retrieved": 4,
    "not_retrieved_reasons": {
      "full text unavailable": 3,
      "language barrier": 1
    }
  },
  "assessment": {
    "assessed": 72,
    "excluded": 26,
    "exclusion_reasons": {
      "insufficient data": 12,
      "wrong outcome measure": 8,
      "duplicate publication": 4,
      "methodological flaws": 2
    }
  },
  "inclusion": {
    "included_in_review": 46,
    "included_in_meta_analysis": 28
  }
}
```

### Figure Generation
```python
def create_prisma_flow(prisma_data, output_path, format="png"):
    """Create PRISMA 2020 flow diagram.
    
    Features:
    - 5-phase layout (Identification → Screening → Retrieval → Assessment → Included)
    - Numbers at each stage
    - Exclusion reasons listed
    - Clean, publication-ready styling
    - Design system colors and fonts
    """
```

---

## Styling

- **Box style**: Rounded rectangle, white fill, dark border
- **Arrow style**: Solid, dark gray, 1.5pt
- **Font**: Inter/sans-serif, 10pt body, 12pt section headers
- **Colors**: 
  - Box background: `#FFFFFF`
  - Box border: `#333333`
  - Section header: `#0072B2` (blue)
  - Numbers: bold
  - Exclusion reasons: `#666666` (gray)
- **Size**: Double column (17.5cm wide)
- **DPI**: 300 for print

---

## Validation Checks
- [ ] Numbers are internally consistent
- [ ] All PRISMA 2020 phases present
- [ ] Exclusion reasons sum to total excluded
- [ ] Design system theme applied
- [ ] Font sizes meet publication standard
- [ ] Output in both PNG and SVG formats
