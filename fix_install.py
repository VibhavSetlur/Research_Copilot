with open("docs/INSTALLATION.md", "r") as f:
    content = f.read()

# Replace cursor and claude mcp json configs
content = content.replace('"command": "ros"', '"command": "python"')
content = content.replace('"args": ["start", "--transport", "stdio"]', '"args": ["-m", "research_os.server", "--transport", "stdio"]')
content = content.replace('"start",\n        "--transport",\n        "stdio"', '"-m",\n        "research_os.server",\n        "--transport",\n        "stdio"')
content = content.replace('ros doctor', 'research-os doctor')
content = content.replace('ros start --transport stdio', 'python -m research_os.server --transport stdio')
content = content.replace('ros init', 'research-os init')
content = content.replace('ros: command not found', 'research-os: command not found')

with open("docs/INSTALLATION.md", "w") as f:
    f.write(content)
