# Example Walkthrough: From CSV to paper.pdf

A complete mock research session showing every step from data ingestion to publication-ready PDF.

---

## Scenario

You have a CSV file (`housing.csv`) with housing prices and features (sqft, bedrooms, location, year_built). You want to:
1. Explore the data
2. Test whether location predicts price
3. Visualize the relationship
4. Compile a paper

---

## Step 1: Initialize Project

```bash
ros init ~/housing-analysis/
```

Output:
```
RESEARCH OS — WORKSPACE CREATED
  Project: housing-analysis
  Location: /home/you/housing-analysis

inputs/
├── raw_data/
├── literature/
├── context/
├── literature_index.yaml
└── intake.md
workspace/
├── methods.md
├── analysis.md
├── citations.md
├── logs/
├── data/
├── figures/
├── reports/
├── dashboards/
└── scripts/
synthesis/
docs/
├── research_question.md
├── hypotheses.md
└── glossary.md
environment/
.os_state/
```

---

## Step 2: Add Data

```bash
cp ~/Downloads/housing.csv ~/housing-analysis/inputs/raw_data/
```

Research OS automatically computes the SHA-256 hash and updates `inputs/intake.md`.

---

## Step 3: Connect IDE (One-Time Setup)

Configure your IDE's MCP server as described in `docs/IDE_INTEGRATION.md`.

---

## Step 4: Explore the Data

**User:** *"I have a CSV at `inputs/raw_data/housing.csv`. What does the data look like?"*

**IDE calls:**

```
view.data.head(filepath="inputs/raw_data/housing.csv", n=5)
```

**Response:**
```json
{
  "shape": [500, 8],
  "columns": [
    {"name": "price", "dtype": "float64", "non_null": 500, "null_pct": 0.0},
    {"name": "sqft", "dtype": "float64", "non_null": 500, "null_pct": 0.0},
    {"name": "bedrooms", "dtype": "int64", "non_null": 498, "null_pct": 0.4},
    {"name": "location", "dtype": "object", "non_null": 500, "null_pct": 0.0},
    {"name": "year_built", "dtype": "int64", "non_null": 500, "null_pct": 0.0}
  ],
  "head": [
    {"price": 450000, "sqft": 1800, "bedrooms": 3, "location": "urban", "year_built": 2005},
    {"price": 285000, "sqft": 1200, "bedrooms": 2, "location": "suburb", "year_built": 1998}
  ],
  "describe": { ... }
}
```

---

## Step 5: Create a Figure

**User:** *"Show me the distribution of prices by location."*

**IDE calls:**

```
tool.figure.create(
  filepath="inputs/raw_data/housing.csv",
  chart_type="box",
  x_column="location",
  y_column="price",
  title="Housing Prices by Location"
)
```

**Response:**
```json
{
  "figure_path": "/home/you/housing-analysis/workspace/figures/housing_box.png",
  "chart_type": "box"
}
```

**IDE then updates the workflow:**

```
sys.analysis.log(
  entry="Price distribution by location visualized — urban median $520K, suburb $310K, rural $180K",
  step="01_exploration",
  status="running"
)
```

---

## Step 6: Run a Statistical Test

**User:** *"Is the price difference between urban and suburban homes statistically significant?"*

**IDE calls:**

```
tool.statistical.test(
  filepath="/home/you/housing-analysis/inputs/raw_data/housing.csv",
  test_type="ttest",
  x_column="price",
  group_column="location"
)
```

**Response:**
```json
{
  "test_type": "ttest",
  "assumptions": {
    "normality_urban": {"test": "shapiro", "p_value": 0.082, "passed": true},
    "normality_suburb": {"test": "shapiro", "p_value": 0.064, "passed": true},
    "homogeneity": {"test": "levene", "p_value": 0.231, "passed": true}
  },
  "results": {
    "test": "Welch t-test",
    "statistic": 7.824,
    "p_value": 0.0000012,
    "significant": true,
    "mean_urban": 520000,
    "mean_suburb": 310000
  }
}
```

---

## Step 7: Log Methods

**IDE automatically calls:**

```
mem.methods.append(
  method="Welch t-test",
  parameters="price ~ location (urban vs suburb), equal_var=False",
  tool="tool.statistical.test"
)
```

---

## Step 8: Complete the First Experiment

**IDE calls:**

```
sys.analysis.log(
  entry="01_exploration complete: significant price difference between urban and suburban homes (t=7.82, p<0.001)",
  step="01_exploration",
  status="complete"
)
```

---

## Step 9: Branch for Deeper Analysis

**User:** *"Does the price difference hold after controlling for square footage?"*

**IDE calls:**

```
sys.branch.create(
  name="price_per_sqft",
  hypothesis="Urban premium persists after controlling for size",
  from_step="01_exploration"
)
```

Creates `workspace/02_price_per_sqft/` with a copy of the first experiment's data.

---

## Step 10: Advanced Analysis

**IDE calls:** (in the new branch)

```
tool.statistical.test(
  filepath=".../02_price_per_sqft/data/housing.csv",
  test_type="anova",
  x_column="price_per_sqft",
  group_column="location"
)
```

---

## Step 11: Merge Findings

**User:** *"The price-per-sqft analysis confirms the finding. Add it to the main branch."*

**IDE calls:**

```
sys.branch.merge(
  source="02_price_per_sqft",
  target="main",
  message="Urban premium confirmed per sqft: F(2,497)=12.4, p<0.001"
)
```

---

## Step 12: Synthesize Paper

**User:** *"I'm done. Compile the paper."*

**IDE calls:**

```
sys.synthesize(
  project_name="Housing Price Analysis",
  formats=["pdf"]
)
```

Creates `synthesis/abstract.md`, `synthesis/paper.tex`, `synthesis/references.bib`.

---

## Step 13: Compile LaTeX

**IDE calls:**

```
tool.latex.compile()
```

**Response:**
```json
{
  "pdf_path": "/home/you/housing-analysis/synthesis/paper.pdf",
  "success": true
}
```

---

## Final Workspace State

```
housing-analysis/
├── inputs/raw_data/housing.csv
├── workspace/
│   ├── 01_exploration/
│   │   ├── README.md
│   │   └── conclusions.md
│   ├── 02_price_per_sqft/
│   │   ├── README.md
│   │   └── conclusions.md
│   ├── analysis.md          # Full chronological log + Mermaid diagram
│   ├── methods.md           # Every statistical test recorded
│   ├── citations.md
│   ├── figures/housing_box.png
│   └── workflow.mermaid     # Diagram with 2 complete nodes, 1 merged branch
├── synthesis/
│   ├── abstract.md
│   ├── paper.tex
│   ├── references.bib
│   └── paper.pdf            # ← Final output
└── .os_state/
    ├── state_ledger.yaml
    └── checkpoints/
```

---

## Total Time: ~15 minutes of IDE chat interaction.
