"""Info commands: agents, agent, skills, skill, skill-search, workflow, iterations, followups."""
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


def find_project_root():
    p = Path.cwd()
    for _ in range(10):
        if (p / ".research").exists():
            return p
        if p.parent == p:
            break
        p = p.parent
    return None


def load_yaml(path: Path):
    if yaml is None:
        result = {}
        try:
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and ":" in line:
                        key, _, val = line.partition(":")
                        val = val.strip().strip('"').strip("'")
                        result[key.strip()] = val
        except FileNotFoundError:
            return {}
        return result
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except (FileNotFoundError, Exception):
        return {}


def load_json(path: Path):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def load_markdown(path: Path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return ""


def get_config(root: Path):
    config = load_yaml(root / ".research" / "config.yaml")
    defaults = {
        "default_workflow": "quick_exploratory",
        "intake_path": "inputs/intake.md",
        "data_raw": "inputs/data/raw",
        "cache_dir": ".research/cache",
        "cache_research_map": ".research/cache/research_map.json",
        "cache_followups": ".research/cache/follow_up_questions.md",
        "research_map": "reports/baseline/research_map.json",
        "follow_up_questions": "reports/baseline/follow_up_questions.md",
        "iteration_registry": "docs/iterations/registry.json",
    }
    for k, v in defaults.items():
        config.setdefault(k, v)
    return config


def get_research_map(root: Path, config: dict):
    ai_map = load_json(root / config["research_map"])
    if ai_map:
        return ai_map
    return load_json(root / config["cache_research_map"])


def cmd_agents(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    agents_dir = root / ".research" / "agents"

    if args.name:
        agent_file = agents_dir / f"{args.name}.md"
        if not agent_file.exists():
            matches = list(agents_dir.glob(f"*_{args.name}.md"))
            if matches:
                agent_file = matches[0]
            else:
                print(f"Agent '{args.name}' not found.")
                return
        print(f"--- {agent_file} ---")
        print(load_markdown(agent_file))
    else:
        print("=" * 60)
        print("AGENTS")
        print("=" * 60)
        print()
        for f in sorted(agents_dir.glob("*.md")):
            if f.name.startswith("00_"):
                continue
            content = load_markdown(f)
            desc = ""
            for line in content.split("\n")[:10]:
                if line.startswith("description:"):
                    desc = line.split(":", 1)[1].strip().strip('"')
                    break
            name = f.stem.split("_", 1)[1] if "_" in f.stem else f.stem
            print(f"  {name}")
            if desc:
                print(f"    {desc}")
            print()
        print("  Use: research agent <name> to view an agent")


def cmd_skills(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    skills_dir = root / ".research" / "skills"

    if args.name:
        found = None
        for f in skills_dir.rglob("*.md"):
            if f.stem == args.name:
                found = f
                break
        if not found:
            print(f"Skill '{args.name}' not found.")
            print("Available skills:")
            for f in sorted(skills_dir.rglob("*.md")):
                if f.name != "SKILL_TEMPLATE.md":
                    print(f"  {f.parent.name}/{f.stem}")
            return
        print(f"--- {found} ---")
        print(load_markdown(found))
    else:
        print("=" * 60)
        print("SKILLS")
        print("=" * 60)
        print()
        for cat_dir in sorted(skills_dir.iterdir()):
            if cat_dir.is_dir() and cat_dir.name != "__pycache__":
                skills = [f.stem for f in cat_dir.glob("*.md") if f.name != "SKILL_TEMPLATE.md"]
                if skills:
                    print(f"  {cat_dir.name}/")
                    for s in sorted(skills):
                        print(f"    - {s}")
                    print()
        print("  Use: research skill <name> to view a skill")


def cmd_skill_search(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    index_path = root / ".research" / "cache" / "skill_index.json"
    if not index_path.exists():
        sys.path.append(str(root))
        try:
            from scripts.utils.build_skill_index import build_index
            build_index(root)
        except Exception as e:
            print(f"Index not found, and auto-build failed: {e}")
            sys.exit(1)

    try:
        with open(index_path, "r") as f:
            index_data = json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to load skill index: {e}")
        sys.exit(1)

    query_text = args.query.lower()
    query_words = re.findall(r'[a-zA-Z0-9\-]+', query_text)
    if not query_words:
        print("Please enter a valid search query.")
        return

    results = []
    for skill in index_data.get("skills", []):
        score = 0
        skill_id = skill.get("id", "").lower()
        title = skill.get("title", "").lower()
        category = skill.get("category", "").lower()
        description = skill.get("description", "").lower()
        keywords = [k.lower() for k in skill.get("keywords", [])]

        for word in query_words:
            if word in title:
                score += 10
            if word in skill_id:
                score += 5
            if word in category:
                score += 3
            if word in keywords:
                score += 3
            if word in description:
                score += 1

        if score > 0:
            results.append((score, skill))

    results.sort(key=lambda x: x[0], reverse=True)

    print("=" * 60)
    print(f"SKILL SEARCH RESULTS FOR: '{args.query}'")
    print("=" * 60)
    print()

    if not results:
        print("  No matching skills found.")
        print()
        return

    top_n = results[:3]
    for idx, (score, skill) in enumerate(top_n, 1):
        print(f"  {idx}. {skill['category']}/{skill['title']} (Score: {score})")
        print(f"     ID:   {skill['id']}")
        print(f"     Path: {skill['path']}")
        desc = skill.get("description", "")
        if len(desc) > 120:
            desc = desc[:117] + "..."
        print(f"     Desc: {desc}")
        print()


def cmd_workflow(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    config = get_config(root)
    workflow_id = config["default_workflow"]
    workflow_file = root / ".research" / "workflows" / f"{workflow_id}.yaml"
    workflow = load_yaml(workflow_file)

    print("=" * 60)
    print(f"WORKFLOW: {workflow.get('name', workflow_id)}")
    print("=" * 60)
    print()
    print(f"  {workflow.get('description', '')}")
    print()

    agents = workflow.get("agents", [])
    print("  Pipeline:")
    for i, agent in enumerate(agents):
        print(f"    {i+1}. {agent}")
    print()

    iter_support = workflow.get("iteration_support", {})
    if iter_support.get("enabled"):
        print("  Iteration Support:")
        print(f"    Agent: {iter_support.get('agent', 'research_iterate')}")
        loop_points = iter_support.get("loop_points", [])
        for lp in loop_points:
            print(f"    After {lp.get('after', '?')}:")
            for opt in lp.get("options", []):
                if isinstance(opt, dict):
                    for k, v in opt.items():
                        print(f"      - {k}: {v}")
                else:
                    print(f"      - {opt}")
        print()

    branching = workflow.get("branching", [])
    if branching:
        print("  Branching rules:")
        for b in branching:
            print(f"    - after {b.get('after', '?')}: if {b.get('if', '?')} → {b.get('then', '?')}")
        print()

    feedback = workflow.get("feedback", [])
    if feedback:
        print("  Feedback loops:")
        for fb in feedback:
            print(f"    - {fb.get('from', '?')} → {fb.get('to', '?')} when {fb.get('when', '?')}")
        print()


def cmd_iterations(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    config = get_config(root)
    registry = load_json(root / config.get("iteration_registry", "docs/iterations/registry.json"))

    print("=" * 60)
    print("RESEARCH ITERATIONS")
    print("=" * 60)
    print()

    if not registry:
        print("  No iterations yet. Run research_init first.")
        print()
        return

    project = registry.get("project", "Unknown")
    total = registry.get("total", 0)
    current = registry.get("current_iteration", "000")

    print(f"  Project: {project}")
    print(f"  Total iterations: {total}")
    print(f"  Current: {current}")
    print()

    iterations = registry.get("iterations", [])
    for it in iterations:
        status_marker = "✓" if it.get("status") == "complete" else "○"
        print(f"  {status_marker} #{it['id']}: {it['type']}")
        print(f"     Trigger: {it.get('trigger', 'N/A')}")
        print(f"     Date: {it.get('date', 'N/A')}")
        if it.get("summary"):
            print(f"     Summary: {it['summary']}")
        if it.get("decision"):
            print(f"     Decision: {it['decision']}")
        print()


def cmd_followups(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    config = get_config(root)
    research_map = get_research_map(root, config)
    map_followups = research_map.get("follow_up", [])

    followup_file = root / config["follow_up_questions"]
    followup = load_markdown(followup_file)
    if not followup:
        followup_file = root / config.get("cache_followups", ".research/cache/follow_up_questions.md")
        followup = load_markdown(followup_file)

    print("=" * 60)
    print("FOLLOW-UP QUESTIONS")
    print("=" * 60)
    print()

    if map_followups:
        for q in map_followups:
            print(f"  - {q}")
        print()

    if followup and "[Your answer]" not in followup:
        print("--- follow_up_questions.md ---")
        print(followup)
    elif not map_followups:
        print("  No follow-up questions. Intake is complete.")
    print()
