import re
with open("src/research_copilot/cli.py", "r") as f:
    content = f.read()

# Replace the subparser creation
content = content.replace('sub = parser.add_subparsers(dest="command")', 
'''sub = parser.add_subparsers(dest="command")
    
    # AI-First commands
    sub.add_parser("init", help="Initialize a clean Research Copilot project")
    sub.add_parser("chat", help="Start the persistent conversational control plane")
    
    # Legacy commands demoted to debug
    p_debug = sub.add_parser("debug", help="Advanced/Debug commands")
    debug_sub = p_debug.add_subparsers(dest="debug_command")
''')

# We need to replace all `sub.add_parser` with `debug_sub.add_parser` after the p_debug definition
lines = content.split('\n')
new_lines = []
in_debug_section = False
for line in lines:
    if "p_debug = sub.add_parser" in line:
        in_debug_section = True
    if in_debug_section and "sub.add_parser" in line and not "p_debug = " in line and "dest=" not in line:
        # Avoid replacing the ones we just explicitly kept for 'sub'
        if '"init"' not in line and '"chat"' not in line:
            line = line.replace('sub.add_parser', 'debug_sub.add_parser')
    new_lines.append(line)

content = '\n'.join(new_lines)

# Also fix the command routing in main()
content = content.replace('handler = commands.get(args.command)', '''if args.command == "debug":
        handler = commands.get(args.debug_command)
    else:
        handler = commands.get(args.command)''')

# Remove the old init and chat definitions since we moved them up
content = re.sub(r'sub\.add_parser\("init",.*?\n', '', content)
# It might be debug_sub now
content = re.sub(r'debug_sub\.add_parser\("init",.*?\n', '', content)
content = re.sub(r'debug_sub\.add_parser\("chat",.*?\n', '', content)

with open("src/research_copilot/cli.py", "w") as f:
    f.write(content)
