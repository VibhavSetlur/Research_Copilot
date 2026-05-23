with open("docs/WALKTHROUGH.md", "r") as f:
    content = f.read()

new_prompts = """### Prompt 1: Project Startup
> "I've put my data, literature PDFs, and research notes into the inputs folder. I want to investigate how air pollution affects respiratory hospital admissions across different cities. Can you start the analysis?"

*Because of Rule 15, the AI will automatically load the `project_startup` protocol. It will scan inputs, conduct a domain analysis, formalise hypotheses, use `sys.path.create` to create `01_baseline_eda`, and execute the EDA script—all autonomously.*

### Prompt 2: Continue to Modelling
> "Continue. Let's move on to the next step suggested by the analysis plan: building a baseline regression model."

*The AI will continue following the `data_analysis` protocol, potentially calling `sys.checkpoint.pending` for approval before executing.*

### Prompt 3: Log Decisions
> "Let's log our decision to use linear regression. Please use `log-decision` (or `tool.log.decision`) to record why we chose this method and why we handled missing values the way we did."

### Prompt 4: Literature & Context
> "Search PubMed for recent papers (from the last 3 years) on PM2.5 and respiratory hospital admissions. Download the top 2 relevant papers to `inputs/literature/` and summarize their findings."

### Prompt 5: Synthesis and Reporting
> "We are ready to synthesize our findings. Use `tool.synthesize` to generate a markdown report of our methodology, results, and literature context into the `synthesis/` directory."
"""

import re
content = re.sub(r"### Prompt 1: Initial Discovery.*### Prompt 6: Synthesis and Reporting\n> \"We are ready to synthesize our findings. Use `tool.synthesize` to generate a markdown report of our methodology, results, and literature context into the `synthesis/` directory.\"\n", new_prompts, content, flags=re.DOTALL)

with open("docs/WALKTHROUGH.md", "w") as f:
    f.write(content)
