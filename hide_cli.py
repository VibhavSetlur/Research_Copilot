import re
with open("src/research_copilot/cli.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "sub.add_parser(" in line and "help=" in line:
        if '"init"' not in line and '"chat"' not in line and '"setup"' not in line:
            line = re.sub(r'help="[^"]+"', 'help=argparse.SUPPRESS', line)
    new_lines.append(line)

with open("src/research_copilot/cli.py", "w") as f:
    f.write("".join(new_lines))
