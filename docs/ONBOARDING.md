# Researcher Onboarding Guide

Welcome to the Research Copilot Autonomous OS. This guide will help you transition from traditional manual workflows to orchestrating an AI-native lab.

## Step 1: Set Your Profile
In your `.env` file, choose a `RESEARCH_MODE`.
- `lightweight`: For quick data exploration.
- `publication-grade`: Turns on autonomous critique and debate loops.
- `autonomous-lab`: Fully unhinged AI research with auto-recovery.

## Step 2: Establish the Project Brief
Run `copilot init` and provide a clear research question. The system will build an initial `project_brief.md`.

## Step 3: Conversational Steering
Use `copilot chat`. You don't need to specify scripts.
Just say:
> "Run a causal analysis on the cleaned data. Be highly skeptical of any correlations."

The **Supervisor Agent** will parse this, mutate the DAG to include causal analysis nodes and skeptic review nodes, and execute.

## Step 4: Handling Interruptions
When the CLI pauses and asks:
> "Agent requires human approval for branch `causal_test`."
Review the proposed methodology. If it looks good, type `approve`. If not, type `reject and use a different proxy variable`. The system will automatically replan.

## Step 5: Publishing
When you are ready, say:
> "Compile findings for publication."
The system will run the final confidence checks. If any core claim is under the `CONFIDENCE_THRESHOLD`, it will refuse to publish and suggest further experiments.
