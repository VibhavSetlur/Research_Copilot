with open("docs/INSTALLATION.md", "r") as f:
    content = f.read()

content = content.replace('"command": "python",\n  "args": ["start", "--transport", "stdio"]', '"command": "research-os",\n  "args": ["start", "--transport", "stdio"]')
content = content.replace('"command": "python",\n      "args": [\n        "start",', '"command": "research-os",\n      "args": [\n        "start",')
content = content.replace('"command": "python",\n      "args": ["start", "--transport", "stdio"]', '"command": "research-os",\n      "args": ["start", "--transport", "stdio"]')

with open("docs/INSTALLATION.md", "w") as f:
    f.write(content)

with open("src/research_os/cli.py", "r") as f:
    content = f.read()

content = content.replace('"command": _sys.executable,', '"command": "research-os",')

with open("src/research_os/cli.py", "w") as f:
    f.write(content)
