import os
import shutil

src_dir = "src/research_copilot"

# 1. Create directories
dirs = [
    "agents", "cognition", "memory", "planning", "execution", "graph", 
    "replay", "state", "research_objects", "collaboration", "validation", 
    "provenance", "prompts", "tools", "runtime", "interfaces"
]

for d in dirs:
    os.makedirs(os.path.join(src_dir, d), exist_ok=True)
    init_path = os.path.join(src_dir, d, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w") as f:
            pass

# 2. File mappings
moves = {
    "control_plane/supervisor.py": "agents/supervisor.py",
    "control_plane/specialized_agents.py": "agents/specialized_agents.py",
    "control_plane/critic.py": "agents/critic.py",
    "core/cognitive_tracker.py": "cognition/cognitive_tracker.py",
    "core/assumption_graph.py": "cognition/assumption_graph.py",
    "core/memory_synthesizer.py": "memory/memory_synthesizer.py",
    "core/synthesis_watcher.py": "memory/synthesis_watcher.py",
    "control_plane/planner.py": "planning/planner.py",
    "core/capability_planner.py": "planning/capability_planner.py",
    "control_plane/mutation_engine.py": "graph/mutation_engine.py",
    "control_plane/scheduler.py": "execution/scheduler.py",
    "core/session_replay.py": "replay/session_replay.py",
    "core/state_ledger.py": "state/state_ledger.py",
    "core/checkpoint_manager.py": "state/checkpoint_manager.py",
    "control_plane/diff_engine.py": "collaboration/diff_engine.py",
    "control_plane/prompt_builder.py": "prompts/prompt_builder.py",
    "core/tool_registry.py": "tools/tool_registry.py",
    "core/hooks.py": "runtime/hooks.py",
    "core/interceptors.py": "runtime/interceptors.py",
    "core/model_resolver.py": "runtime/model_resolver.py",
    "core/token_budget.py": "runtime/token_budget.py",
}

for src, dst in moves.items():
    src_path = os.path.join(src_dir, src)
    dst_path = os.path.join(src_dir, dst)
    if os.path.exists(src_path):
        shutil.move(src_path, dst_path)
        print(f"Moved {src} -> {dst}")
    else:
        print(f"Warning: {src} not found")

# 3. Update imports globally
import_map = {
    "research_copilot.agents.supervisor": "research_copilot.agents.supervisor",
    "research_copilot.agents.specialized_agents": "research_copilot.agents.specialized_agents",
    "research_copilot.agents.critic": "research_copilot.agents.critic",
    "research_copilot.cognition.cognitive_tracker": "research_copilot.cognition.cognitive_tracker",
    "research_copilot.cognition.assumption_graph": "research_copilot.cognition.assumption_graph",
    "research_copilot.memory.memory_synthesizer": "research_copilot.memory.memory_synthesizer",
    "research_copilot.memory.synthesis_watcher": "research_copilot.memory.synthesis_watcher",
    "research_copilot.planning.planner": "research_copilot.planning.planner",
    "research_copilot.planning.capability_planner": "research_copilot.planning.capability_planner",
    "research_copilot.graph.mutation_engine": "research_copilot.graph.mutation_engine",
    "research_copilot.execution.scheduler": "research_copilot.execution.scheduler",
    "research_copilot.replay.session_replay": "research_copilot.replay.session_replay",
    "research_copilot.state.state_ledger": "research_copilot.state.state_ledger",
    "research_copilot.state.checkpoint_manager": "research_copilot.state.checkpoint_manager",
    "research_copilot.collaboration.diff_engine": "research_copilot.collaboration.diff_engine",
    "research_copilot.prompts.prompt_builder": "research_copilot.prompts.prompt_builder",
    "research_copilot.tools.tool_registry": "research_copilot.tools.tool_registry",
    "research_copilot.runtime.hooks": "research_copilot.runtime.hooks",
    "research_copilot.runtime.interceptors": "research_copilot.runtime.interceptors",
    "research_copilot.runtime.model_resolver": "research_copilot.runtime.model_resolver",
    "research_copilot.runtime.token_budget": "research_copilot.runtime.token_budget",
}

def update_file(path):
    with open(path, "r") as f:
        content = f.read()
    
    new_content = content
    for old, new in import_map.items():
        new_content = new_content.replace(old, new)
        
    if new_content != content:
        with open(path, "w") as f:
            f.write(new_content)
        print(f"Updated imports in {path}")

for root, _, files in os.walk("."):
    if ".venv" in root or "__pycache__" in root or ".git" in root or ".pytest_cache" in root:
        continue
    for file in files:
        if file.endswith(".py"):
            update_file(os.path.join(root, file))

print("Done.")
