# Contributing

Guide for developers contributing to Research Copilot.

## Development Setup

```bash
git clone https://github.com/your-org/research-copilot.git
cd research-copilot
pip install -e ".[dev,all]"
```

## Code Style

- **Line length**: 120 characters
- **Imports**: Sorted (isort-compatible)
- **Type hints**: Required for all public functions
- **Docstrings**: Google style for public APIs

Run linters:

```bash
ruff check src/
ruff format --check src/
mypy src/
```

## Testing

```bash
pytest tests/ -v
pytest tests/ --cov=src/research_copilot
```

### Test Categories

| Directory | Purpose |
|-----------|---------|
| `tests/unit/` | Unit tests for individual functions |
| `tests/integration/` | Integration tests for pipeline stages |
| `tests/e2e/` | End-to-end tests (full pipeline) |
| `tests/fixtures/` | Test data and mock responses |

## Adding a New Skill

1. Create `src/research_copilot/assets/skills/<category>/<skill_name>.md`
2. Follow the skill template:
   - Frontmatter: `skill_id`, `version`, `category`, `depends_on`, `produces`, `complexity`
   - Purpose: 1-sentence description
   - When to Use / When NOT to Use
   - Execution Protocol (numbered steps)
   - Diagnostics & Interpretation table
   - Validation checklist
3. Keep under 120 lines — skills are AI instruction sheets, not code
4. Replace code implementations with plain-text protocols and decision rules
5. Add keywords to `.research/cache/skill_index.json` for routing

## Adding a New Agent

1. Create `src/research_copilot/assets/agents/<NN>_<agent_name>.md`
2. Follow the agent template:
   - Frontmatter: `agent_id`, `version`, `description`, `depends_on`, `composes`, `produces`
   - Purpose: 1-sentence description
   - Protocol (numbered steps)
   - Validation checklist
3. Agents orchestrate skills — they don't implement methodology directly

## Adding a New Domain

1. Create `src/research_copilot/assets/domains/<domain_name>.yaml`
2. Include: `domain_id`, `name`, `reporting_standard`, `preferred_visualizations`, `quality_gates`, `confounders`
3. Run `rcp scan` to register the domain

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make changes, run tests: `pytest tests/ -v`
3. Run linters: `ruff check src/ && ruff format src/ && mypy src/`
4. Commit with a descriptive message
5. Push and create a PR

### Commit Message Convention

```
type(scope): description

Examples:
feat(skills): add meta-analysis skill
fix(executor): correct DAG update indentation
docs(cli): add export commands to reference
test(integration): add pipeline e2e test
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Architecture Decisions

Major changes should include an Architecture Decision Record (ADR) in `docs/adr/`:

```markdown
# ADR-NNN: Title

## Context
What is the issue that we're seeing that is motivating this decision?

## Decision
What is the change that we're proposing and/or doing?

## Consequences
What becomes easier or more difficult to do because of this change?
```

## Release Process

1. Update version in `pyproject.toml`
2. Update `docs/CHANGELOG.md`
3. Tag the release: `git tag v9.0.0`
4. Push: `git push origin main --tags`
5. Build and publish: `python -m build && python -m twine upload dist/*`
