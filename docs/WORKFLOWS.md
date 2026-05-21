# Workflows

Research Copilot supports five workflow types. Each defines a different pipeline depth and output format.

## Available Workflows

| Workflow | Steps | When to Use |
|----------|-------|-------------|
| `quick_exploratory` | 4 | Fast analysis, no deep literature review |
| `full_publication` | 10 | Complete pipeline with literature + audit |
| `systematic_review` | 8 | Literature-focused, PRISMA-compliant |
| `causal_investigation` | 12 | Causal inference with refutation tests |
| `predictive_modeling` | 8 | ML pipeline with cross-validation |

## quick_exploratory

**Steps:** intake → profile → method_route → execute_analysis

Fast path for exploratory data analysis. Skips literature search, pre-registration, and adversarial review. Best for:
- Initial data exploration
- Quick sanity checks
- Hypothesis generation

```yaml
default_workflow: quick_exploratory
```

## full_publication

**Steps:** intake → literature_deep → method_route → preregistration → data_scaffold → execute_analysis → replication_validator → compile_outputs → reviewer2_critic → audit_validate

Complete pipeline from raw data to publication-ready manuscript. Includes:
- Literature search and evidence matrix
- OSF-compatible pre-registration
- Three-pass citation verification
- Adversarial Reviewer 2 critique
- Multi-dimensional audit with auto-healing

```yaml
default_workflow: full_publication
```

## systematic_review

**Steps:** intake → literature_deep → extract_claims → synthesize_literature → meta_analysis → compile_outputs → audit_validate

Literature-focused workflow for systematic reviews and meta-analyses. Includes:
- Semantic Scholar, PubMed, arXiv search
- Snowball citation tracking
- Evidence matrix and gap analysis
- Meta-analysis with forest plots
- PRISMA-compliant reporting

```yaml
default_workflow: systematic_review
```

## causal_investigation

**Steps:** intake → literature_deep → method_route → data_scaffold → execute_analysis → confounder_analysis → refutation_tests → sensitivity_analysis → compile_outputs → reviewer2_critic → audit_validate

Causal inference workflow with identification strategy validation. Includes:
- DAG-based confounder identification
- Backdoor path verification
- Refutation tests (placebo, random common cause, subset)
- Sensitivity analysis (E-values, Rosenbaum bounds)
- Causal language audit

```yaml
default_workflow: causal_investigation
```

## predictive_modeling

**Steps:** intake → data_scaffold → feature_engineering → model_selection → cross_validation → hyperparameter_tuning → evaluate → compile_outputs

Machine learning pipeline with model comparison. Includes:
- Feature engineering and selection
- Multiple model comparison
- Cross-validation with stratification
- Hyperparameter tuning
- Model interpretability (SHAP, feature importance)

```yaml
default_workflow: predictive_modeling
```

## Changing Workflow

Edit `.research/config.yaml`:

```yaml
default_workflow: full_publication
```

Or override per-run via intent router:

```bash
rcp intent "run a quick exploratory analysis"
```

## Custom Workflows

Create a new workflow file in `.research/workflows/`:

```yaml
workflow_id: "my_custom_workflow"
name: "My Custom Workflow"
steps:
  - research_init
  - method_route
  - execute_analysis
  - compile_outputs
approval_gates:
  - method_route
  - compile_outputs
```
