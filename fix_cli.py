import re

with open("src/research_copilot/cli.py", "r") as f:
    text = f.read()

# Isolate the build_parser function body to safely replace sub.add_parser
start_idx = text.find('sub = parser.add_subparsers(dest="command")')
end_idx = text.find('return parser', start_idx)

body = text[start_idx:end_idx]

# Replace `sub.add_parser` with `debug_sub.add_parser`
body = body.replace('sub.add_parser(', 'debug_sub.add_parser(')

# Now, put back the `sub = parser.add_subparsers(...)` and add the new `sub` commands
new_setup = """sub = parser.add_subparsers(dest="command")

    sub.add_parser("init", help="Initialize a clean Research Copilot project")
    sub.add_parser("chat", help="Start the persistent conversational control plane")
    
    p_debug = sub.add_parser("debug", help="Advanced/Debug commands")
    debug_sub = p_debug.add_subparsers(dest="debug_command")
"""

body = body.replace('debug_sub = parser.add_subparsers(dest="command")', new_setup)

# Remove the old init and chat
body = re.sub(r'\s*debug_sub\.add_parser\("init", help="Initialize a clean Research Copilot project"\)\n', '', body)
body = re.sub(r'\s*debug_sub\.add_parser\("chat", help="Start the persistent conversational control plane"\)\n', '', body)

# Stitch back together
text = text[:start_idx] + body + text[end_idx:]

# Update the main() command routing
main_replacement = """if args.command == "debug":
        handler = commands.get(args.debug_command)
    else:
        handler = commands.get(args.command)"""
        
text = text.replace('handler = commands.get(args.command)', main_replacement)

# Also fix the `if not args.command:` to default to chat if no command
text = text.replace('if not args.command:\\n        parser.print_help()\\n        return', 
'''if not args.command:
        args.command = "chat"''')

with open("src/research_copilot/cli.py", "w") as f:
    f.write(text)

