# Quickstart Guide

## 1. Installation

Install via pip:
```bash
pip install git+https://github.com/VibhavSetlur/Research-OS.git

# For additional features:
pip install "research-os[web,literature,viz,poster] @ git+https://github.com/VibhavSetlur/Research-OS.git"
```

## 2. Initialize a Project

```bash
mkdir my-research-project
cd my-research-project
research-os init --name "My Research Project"
```

## 3. Running the MCP Server

Start the Research OS MCP server in your project directory:

```bash
python -m research_os.server --workspace .
```

Connect your AI IDE (like Cursor or Claude Desktop) to this server command.

## 4. Triggering the Guidance Engine

To ensure the AI operates correctly, ask it to load a guidance protocol. For example:

> "Run the `domain_analysis` protocol on the inputs."

The AI will use `sys.guidance.get` to read the YAML decision tree, guiding it to classify the domain, determine reporting standards, and identify pitfalls without you having to explicitly prompt it.

## 5. Experimentation & Chronological Paths

Ask the AI to create a new chronological path when trying a new methodology:
> "Use sys.path.create to create a new chronological path for trying a non-parametric approach."
The AI will invoke `sys.path.create`, isolating the new work while preserving the ledger.
