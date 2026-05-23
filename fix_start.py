import glob

files = [
    "README.md",
    "docs/INSTALLATION.md",
    "docs/QUICKSTART.md",
    "docs/RESEARCHER_GUIDE.md",
    "docs/WALKTHROUGH.md",
    "docs/tutorials/EXAMPLE_WALKTHROUGH.md",
    "src/research_os/cli.py"
]

for file in files:
    try:
        with open(file, "r") as f:
            content = f.read()
            
        content = content.replace("python -m research_os.server --workspace .", "research-os start --workspace .")
        content = content.replace("python -m research_os.server --transport stdio", "research-os start --transport stdio")
        content = content.replace('"args": ["-m", "research_os.server", "--transport", "stdio"]', '"args": ["start", "--transport", "stdio"]')
        content = content.replace('"args": [\n        "-m",\n        "research_os.server",\n        "--transport",\n        "stdio"\n      ]', '"args": [\n        "start",\n        "--transport",\n        "stdio"\n      ]')
        content = content.replace('"-m",\n        "research_os.server",', '"start",')
        
        with open(file, "w") as f:
            f.write(content)
    except FileNotFoundError:
        pass
