import re

with open("src/research_os/server.py", "r") as f:
    content = f.read()

# Find the imports block
imports_start = content.find("from research_os.tools.actions.web_search")
imports_end = content.find("try:\n    from mcp.server import Server")

if imports_start != -1 and imports_end != -1:
    old_imports = content[imports_start:imports_end]
    
    # We will replace these with dynamic imports inside the _handle_* functions?
    # No, we will just use a MagicMock-like pattern or try/except
    
    new_imports = """
class _MissingDependency:
    def __init__(self, name):
        self.name = name
    def __call__(self, *args, **kwargs):
        raise RuntimeError(f"Optional dependency missing for {self.name}. Please install required extras.")

def _lazy_import(module_name, names):
    try:
        mod = __import__(module_name, fromlist=names)
        return [getattr(mod, name) for name in names]
    except ImportError:
        return [_MissingDependency(name) for name in names]

search_web, scrape_web = _lazy_import("research_os.tools.actions.web_search", ["search_web", "scrape_web"])
package_install, = _lazy_import("research_os.tools.actions.environment", ["package_install"])
create_checkpoint, rollback_checkpoint, list_checkpoints = _lazy_import("research_os.tools.actions.checkpoint", ["create_checkpoint", "rollback_checkpoint", "list_checkpoints"])
create_path, abandon_path, list_paths = _lazy_import("research_os.tools.actions.path", ["create_path", "abandon_path", "list_paths"])
download_literature, = _lazy_import("research_os.tools.actions.literature", ["download_literature"])
get_config, set_config, init_config, validate_config = _lazy_import("research_os.tools.actions.config", ["get_config", "set_config", "init_config", "validate_config"])
notify_researcher, checkpoint_pending, checkpoint_approve, session_handoff = _lazy_import("research_os.tools.actions.interaction", ["notify_researcher", "checkpoint_pending", "checkpoint_approve", "session_handoff"])
discover_mcp, = _lazy_import("research_os.tools.actions.external_mcp", ["discover_mcp"])
task_monitor, task_kill = _lazy_import("research_os.tools.actions.task", ["task_monitor", "task_kill"])
search_semantic_scholar, search_pubmed, search_crossref = _lazy_import("research_os.tools.actions.search", ["search_semantic_scholar", "search_pubmed", "search_crossref"])
load_protocol, list_protocols, validate_protocol = _lazy_import("research_os.tools.actions.protocol", ["load_protocol", "list_protocols", "validate_protocol"])
_profile_inputs, = _lazy_import("research_os.tools.actions.profiling", ["_profile_inputs"])

"""
    new_content = content[:imports_start] + new_imports + content[imports_end:]
    with open("src/research_os/server.py", "w") as f:
        f.write(new_content)
    print("Fixed server imports")
else:
    print("Could not find imports block")
