# Quickstart Guide

## 1. Installation

Clone the repository and install the dependencies:
```bash
git clone https://github.com/VibhavSetlur/Research-OS.git
cd Research-OS
pip install -e .
```

## 2. Running the MCP Server

Start the Research OS MCP server. The server uses stdio by default for seamless integration with IDEs like Cursor, Claude Desktop, or custom MCP clients.

```bash
python -m research_os.server --workspace /path/to/my/new/project
```

## 3. Scaffolding a Project

Once the server is running and your AI is attached, simply ask your AI:

> "Initialize a new research project called 'Alzheimers RCT Analysis'."

The AI will invoke `sys.workspace.scaffold`, which instantly builds the directory structure:
- `.os_state/`
- `docs/`
- `inputs/`
- `workspace/`
- `synthesis/`
- `environment/`

## 4. Triggering the Guidance Engine

To ensure the AI operates correctly, ask it to load a guidance protocol. For example:

> "Run the `domain_analysis` protocol on the inputs."

The AI will use `sys.guidance.get` to read the YAML decision tree, guiding it to classify the domain, determine reporting standards, and identify pitfalls without you having to explicitly prompt it.

## 5. Experimentation & Chronological Paths

Ask the AI to create a new chronological path when trying a new methodology:
> "Use sys.path.create to create a new chronological path for trying a non-parametric approach."
The AI will invoke `sys.path.create`, isolating the new work while preserving the ledger.
