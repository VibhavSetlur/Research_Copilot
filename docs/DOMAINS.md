# Domains

Research Copilot includes 19 domain profiles, each with reporting standards, effect size conventions, preferred methods, and domain-specific confounders.

## Available Domains

| Domain | Reporting Standard | Effect Size | Preferred Visualizations |
|--------|-------------------|-------------|-------------------------|
| Psychology & Social Sciences | APA 7th | Cohen's d | Violin, forest plot |
| Epidemiology | STROBE | Risk ratio / OR | Kaplan-Meier, forest plot |
| Econometrics | AEA | AME / IV | Coefficient plot, event study |
| Finance | Journal of Finance | Alpha / Beta | Time series, factor model |
| Education | APA | Cohen's d / Hedges' g | Bar, growth curve |
| Genomics | Nature Genetics | log2FC | Volcano, heatmap |
| NLP/Computational | ACL | F1 / BLEU | Confusion matrix, learning curve |
| Ecology | Ecology | Effect ratio | Ordination, species accumulation |
| Climate Science | AGU | Anomaly magnitude | Time series, spatial map |
| Materials Science | ACS | Property change % | XRD, stress-strain |
| Neuroscience | APA + SfN | Cohen's d + BOLD % | Brain map, ERP waveform |
| Computational Biology | PLOS | log2FC | Pathway enrichment |
| Political Science | APSR | AME | Coefficient plot, marginal effects |
| Anthropology | AAA | Thematic / Cohen's d | Network, ethnographic map |
| Sociology | ASA | Standardized coefficient | Path diagram, mosaic plot |
| Empirical Legal Studies | Bluebook | Odds ratio | Coefficient plot |
| Public Policy | Policy brief | Impact magnitude | Dashboard, map |
| Survey Research | AAPOR | Odds ratio | Likert bar, diverging bar |
| Bayesian-First (any) | HDI not CI | Posterior mean + HDI | Posterior density, trace plot |

## Domain Configuration

Each domain is defined in `src/research_copilot/assets/domains/<domain>.yaml`:

```yaml
domain_id: "epidemiology"
name: "Epidemiology & Public Health"
reporting_standard: "STROBE"
significance_threshold: 0.05
default_effect_size_metric: "risk_ratio"
preferred_visualizations:
  - kaplan_meier
  - forest_plot
  - directed_acyclic_graph
quality_gates:
  - confounding_assessed
  - selection_bias_addressed
  - missingness_reported
confounders:
  - age
  - sex
  - socioeconomic_status
  - comorbidities
```

## How Domains Are Used

1. **Auto-detection**: The system detects domain from data characteristics (ICD codes → epidemiology, Likert items → survey research, panel data → econometrics)
2. **Method routing**: Domain profiles influence method selection (e.g., epidemiology → survival analysis, econometrics → instrumental variables)
3. **Quality gates**: Each domain has specific quality checks that must pass before manuscript compilation
4. **Reporting standards**: Output format matches domain conventions (APA tables, STROBE checklist, CONSORT flow diagram)

## Adding a Custom Domain

Create a new YAML file in `src/research_copilot/assets/domains/`:

```yaml
domain_id: "my_domain"
name: "My Custom Domain"
reporting_standard: "Custom"
significance_threshold: 0.05
default_effect_size_metric: "cohens_d"
preferred_visualizations:
  - scatter
  - boxplot
quality_gates:
  - assumption_checks
  - robustness_verified
confounders:
  - confounder_1
  - confounder_2
```

The domain is automatically available for routing after the next `rcp scan`.
