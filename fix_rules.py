import os

files = [
    "templates/AGENTS.md",
    "templates/.cursor/rules/research-os.mdc",
    "templates/.claude/rules/research-os.md",
    "templates/.antigravity/rules/research-os.md"
]

append_text = """

15. **Project Startup**: When the researcher indicates they have placed data or context files in `inputs/`, immediately load the `project_startup` protocol (`guidance/project_startup`) and follow it step by step. Do not wait for further prompts to begin the domain analysis and EDA.

16. **Autonomy Gating**: If the `autonomy_level` in `inputs/researcher_config.yaml` is "supervised", before calling `tool.python.exec`, `tool.synthesize`, or `sys.path.create`, you must call `sys.checkpoint.pending` and wait for the researcher to approve via `sys.checkpoint.approve`.

17. **Next Steps**: After completing any significant task, always end your response with:
    - A one-sentence summary of what was done.
    - "Next steps:" followed by 2-3 concrete options the researcher can choose from.
    - If appropriate, mention which protocol would guide the next step.
"""

for f in files:
    try:
        with open(f, "r") as file:
            content = file.read()
        
        # Prevent double appending
        if "15. **Project Startup**:" not in content:
            with open(f, "a") as file:
                file.write(append_text)
                print(f"Updated {f}")
    except FileNotFoundError:
        print(f"File not found: {f}")
