# Contributing to Research Copilot

We welcome contributions to the Research Copilot ecosystem! The platform is designed to be highly extensible via **Skills** and **Domain Profiles**.

## How to Contribute a Skill

Skills are self-contained capabilities. 
1. Copy `.research/skills/SKILL_TEMPLATE.md`.
2. Fill out the YAML frontmatter (ID, tools, dependencies).
3. Clearly define the Execution Protocol and Validation Criteria.
4. Submit a Pull Request.

## How to Contribute a Domain Profile

If your scientific field is not yet supported:
1. Review an existing profile in `.research/domains/` (e.g., `epidemiology.yaml`).
2. Create a new YAML file for your field.
3. Define the reporting standard, preferred visualizations, and default skills.
4. Submit a Pull Request.
