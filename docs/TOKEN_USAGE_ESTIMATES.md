# Token Usage Estimates

## Per-Task Estimates (single session)

| Task | Protocols Loaded | Tool Calls | Est. Tokens (small) | Est. Tokens (medium) | Est. Tokens (large) |
|------|-----------------|------------|---------------------|----------------------|---------------------|
| Scaffold project | analysis_plan | 1 | 800-1,200 | 800-1,200 | 800-1,200 |
| Domain analysis | domain_analysis | 1-2 | 1,000-1,500 | 1,200-1,800 | 1,200-1,800 |
| EDA (1 step) | methodology_selection | 3-5 | 2,000-3,000 | 2,500-3,500 | 2,500-3,500 |
| Literature search | literature_search | 3-5 | 2,000-4,000 | 2,500-5,000 | 3,000-5,000 |
| Write methods entry | writing_core + writing_methods | 2-3 | 1,500-2,500 | 1,500-2,500 | 1,500-2,500 |
| Write citations | writing_core + writing_citations | 2-3 | 1,500-2,500 | 1,500-2,500 | 1,500-2,500 |
| Write analysis log | writing_core + writing_analysis_log | 1-2 | 800-1,200 | 800-1,200 | 800-1,200 |
| Write conclusions | writing_core + writing_conclusions | 1-2 | 1,000-1,500 | 1,000-1,500 | 1,000-1,500 |
| Synthesis (one section) | writing_core + writing_synthesis | 2-3 | 2,000-3,500 | 2,500-4,000 | 2,500-4,000 |
| Full paper synthesis | writing_core + writing_synthesis | 5-8 | 10,000-15,000 | 12,000-18,000 | 12,000-18,000 |
| Audit | audit_and_validation | 2-4 | 1,500-2,500 | 1,500-2,500 | 1,500-2,500 |
| Poster creation | writing_synthesis | 1-2 | 2,000-4,000 | 3,000-5,000 | 3,000-5,000 |

## Full Workflow Estimates (total across all sessions)

| Workflow | Sessions Needed | Total Est. Tokens |
|----------|----------------|-------------------|
| Quick exploratory (2 steps) | 2-3 | 8,000-15,000 |
| Standard analysis (4 steps) | 4-6 | 20,000-40,000 |
| Full paper (6+ steps) | 8-12 | 50,000-100,000 |
| Systematic review | 12-20 | 100,000-200,000 |

## Token-Saving Strategies
1. **Lazy loading:** Protocols load on-demand via sys.guidance.get. Tool schemas via sys.tool.info.
2. **Light protocols:** Use protocols/light/ for small models — saves 60% per protocol load.
3. **Session handoffs:** Break long workflows into sessions. Each handoff costs ~200 tokens but saves 5,000+ in context refresh.
4. **Minimal context:** Use sys.state.minimal_context for small models (<500 tokens).
