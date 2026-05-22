# Researcher Guide

Welcome to Research OS v3.0. As a human researcher, your role is to provide the high-level intent, raw data, and scientific oversight, while the AI acts as your execution engine.

## Step 1: Initialization
Create a fresh folder for your project and run the MCP server:
`python -m research_os.server --workspace .`

Attach your AI (e.g., Claude via Desktop app or an IDE like Cursor) and ask it to scaffold the workspace.

## Step 2: Providing Context
Drop your data files into `inputs/raw_data/` and any background PDFs into `inputs/context/`.

## Step 3: Guiding the AI
You don't need to tell the AI how to write a t-test. Instead, tell the AI to follow the system protocols.
- "Run the domain analysis."
- "Execute the literature search protocol."
- "Based on the methodology selection, create an experiment branch and run the analysis."

## Step 4: Branching and Iteration
If a statistical assumption fails, simply tell the AI: "Branch off this experiment and try a non-parametric test instead." The AI will use `sys.branch.create` to isolate the state, ensuring your primary branch remains clean.

## Step 5: Reviewing Outputs
All generated code will be in `workspace/scripts/`. Review it for correctness. The AI will output figures to `workspace/figures/`.
Once you are satisfied, tell the AI to "Run the writing standards protocol" to generate the manuscript in `synthesis/`.
