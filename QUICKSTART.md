# Quickstart

## Installation

```bash
git clone https://github.com/VibhavSetlur/research-copilot.git
cd research-copilot
pip install -e .
```

## Basic Usage

Boot the MCP server natively:
```bash
rcp start --transport stdio
```

Or run via the CLI:
```bash
rcp init my_project
cd my_project
rcp status
```

For more details, explore the examples in `examples/`.
