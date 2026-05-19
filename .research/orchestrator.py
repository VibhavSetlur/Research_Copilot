#!/usr/bin/env python3
"""Skills-first Research Copilot (v2) orchestrator.

This script is the v2 replacement for the legacy phase runner.

Responsibilities:
- Discover `.research/skills/**` and `.research/agents/**` (skills-first registry)
- Hydrate prompts (provider-adapted) for agents, skills, and workflows
- Persist a provenance DAG (`.research/workflow_dag.json` + `.mermaid`)
- Track data versions (`.research/data_versions.yaml`, multi-document YAML)
- Maintain minimal run history (`.research/state/run_log.jsonl`)

This orchestrator intentionally does NOT execute analysis code; it produces structured prompts
and provenance artifacts that any LLM or agent runtime can follow.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESEARCH_DIR = PROJECT_ROOT / ".research"

CONFIG_FILE = RESEARCH_DIR / "config.yaml"

SKILLS_DIR = RESEARCH_DIR / "skills"
AGENTS_DIR = RESEARCH_DIR / "agents"
DOMAINS_DIR = RESEARCH_DIR / "domains"
WORKFLOWS_DIR = RESEARCH_DIR / "workflows"
STATE_DIR = RESEARCH_DIR / "state"

DAG_JSON_DEFAULT = RESEARCH_DIR / "workflow_dag.json"
DAG_MERMAID_DEFAULT = RESEARCH_DIR / "workflow_dag.mermaid"
DATA_VERSIONS_DEFAULT = RESEARCH_DIR / "data_versions.yaml"
RUN_LOG_DEFAULT = STATE_DIR / "run_log.jsonl"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_stamp_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def append_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(content)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if value.startswith('"') and value.endswith('"') and len(value) >= 2:
        return value[1:-1]
    if value.startswith("'") and value.endswith("'") and len(value) >= 2:
        return value[1:-1]

    lowered = value.lower()
    if lowered in {"true", "yes"}:
        return True
    if lowered in {"false", "no"}:
        return False

    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        items = [item.strip() for item in inner.split(",")]
        return [_parse_scalar(item) for item in items]

    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        pass

    return value


def parse_simple_yaml(yaml_text: str) -> Dict[str, Any]:
    """Parse a minimal YAML subset.

    Supports:
    - `key: value` scalars
    - `key: [a, b]` inline lists
    - `key:` followed by `- item` block lists
    """

    data: Dict[str, Any] = {}
    current_list_key: Optional[str] = None

    for raw_line in yaml_text.splitlines():
        line = raw_line.rstrip("\n")
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("- "):
            if current_list_key is None:
                continue
            item = stripped[2:].strip()
            if not isinstance(data.get(current_list_key), list):
                data[current_list_key] = []
            data[current_list_key].append(_parse_scalar(item))
            continue

        if ":" not in line:
            continue

        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()

        if not value:
            data[key] = []
            current_list_key = key
        else:
            data[key] = _parse_scalar(value)
            current_list_key = None

    return data


def dump_simple_yaml(data: Dict[str, Any]) -> str:
    """Dump a simple mapping to the YAML subset this repo supports."""

    lines: List[str] = []
    for key in sorted(data.keys()):
        value = data[key]
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                if isinstance(item, str):
                    lines.append(f"  - \"{item}\"")
                else:
                    lines.append(f"  - {item}")
            continue

        if isinstance(value, str):
            lines.append(f"{key}: \"{value}\"")
        elif value is True:
            lines.append(f"{key}: true")
        elif value is False:
            lines.append(f"{key}: false")
        else:
            lines.append(f"{key}: {value}")

    return "\n".join(lines) + "\n"


def parse_frontmatter_markdown(markdown_text: str) -> Tuple[Dict[str, Any], str]:
    lines = markdown_text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, markdown_text

    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fm_text = "\n".join(lines[1:i])
            body = "\n".join(lines[i + 1 :]).lstrip("\n")
            return parse_simple_yaml(fm_text), body

    return {}, markdown_text


def load_yaml_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return parse_simple_yaml(read_text(path))


def load_yaml_documents_file(path: Path) -> List[Dict[str, Any]]:
    """Load multi-document YAML consisting of repeated `---` mapping documents."""

    if not path.exists():
        return []

    docs: List[Dict[str, Any]] = []
    in_doc = False
    buffer: List[str] = []

    for line in read_text(path).splitlines():
        if line.strip() == "---":
            if in_doc and buffer:
                docs.append(parse_simple_yaml("\n".join(buffer)))
                buffer = []
            in_doc = True
            continue
        if not in_doc:
            continue
        buffer.append(line)

    if in_doc and buffer:
        docs.append(parse_simple_yaml("\n".join(buffer)))

    return docs


def append_yaml_document(path: Path, doc: Dict[str, Any]) -> None:
    content = "---\n" + dump_simple_yaml(doc)
    if path.exists():
        existing = read_text(path)
        if existing and not existing.endswith("\n"):
            content = "\n" + content
    append_text(path, content)


def config_or_default(config: Dict[str, Any], key: str, default: Any) -> Any:
    value = config.get(key)
    return default if value is None or value == "" else value


def config_path(config: Dict[str, Any], key: str, default: Path) -> Path:
    raw = config.get(key)
    if raw:
        return PROJECT_ROOT / str(raw)
    return default


@dataclass(frozen=True)
class SkillDefinition:
    skill_id: str
    version: str
    category: str
    required_tools: List[str]
    depends_on: List[str]
    produces: List[str]
    path: Path
    estimated_tokens: Optional[int] = None
    domain_compatibility: Optional[List[str]] = None


@dataclass(frozen=True)
class AgentDefinition:
    agent_id: str
    version: str
    description: str
    composes: List[str]
    produces: List[str]
    path: Path
    depends_on: Optional[List[str]] = None
    domain_compatibility: Optional[List[str]] = None


class Registry:
    def __init__(self, skills_dir: Path, agents_dir: Path) -> None:
        self._skills_dir = skills_dir
        self._agents_dir = agents_dir
        self.skills: Dict[str, SkillDefinition] = {}
        self.agents: Dict[str, AgentDefinition] = {}

    def load(self) -> None:
        self.skills = self._discover_skills()
        self.agents = self._discover_agents()

    def _discover_skills(self) -> Dict[str, SkillDefinition]:
        skills: Dict[str, SkillDefinition] = {}
        if not self._skills_dir.exists():
            return skills

        for path in sorted(self._skills_dir.glob("**/*.md")):
            if path.name == "SKILL_TEMPLATE.md":
                continue
            meta, _ = parse_frontmatter_markdown(read_text(path))
            skill_id = str(meta.get("skill_id") or "").strip()
            if not skill_id:
                continue
            skills[skill_id] = SkillDefinition(
                skill_id=skill_id,
                version=str(meta.get("version") or "0.0.0"),
                category=str(meta.get("category") or ""),
                required_tools=list(meta.get("required_tools") or []),
                depends_on=list(meta.get("depends_on") or []),
                produces=list(meta.get("produces") or []),
                estimated_tokens=(
                    int(meta["estimated_tokens"]) if "estimated_tokens" in meta else None
                ),
                domain_compatibility=list(meta.get("domain_compatibility") or []),
                path=path,
            )

        return skills

    def _discover_agents(self) -> Dict[str, AgentDefinition]:
        agents: Dict[str, AgentDefinition] = {}
        if not self._agents_dir.exists():
            return agents

        for path in sorted(self._agents_dir.glob("*.md")):
            if path.name == "00_core_guardrails.md":
                continue
            meta, _ = parse_frontmatter_markdown(read_text(path))
            agent_id = str(meta.get("agent_id") or "").strip()
            if not agent_id:
                continue
            agents[agent_id] = AgentDefinition(
                agent_id=agent_id,
                version=str(meta.get("version") or "0.0.0"),
                description=str(meta.get("description") or ""),
                composes=list(meta.get("composes") or []),
                produces=list(meta.get("produces") or []),
                depends_on=list(meta.get("depends_on") or []) or None,
                domain_compatibility=list(meta.get("domain_compatibility") or []) or None,
                path=path,
            )

        return agents


def ensure_scaffold() -> None:
    for path in [RESEARCH_DIR, SKILLS_DIR, AGENTS_DIR, DOMAINS_DIR, WORKFLOWS_DIR, STATE_DIR]:
        path.mkdir(parents=True, exist_ok=True)

    if not CONFIG_FILE.exists():
        logging.warning("Missing .research/config.yaml; creating default.")
        write_text(
            CONFIG_FILE,
            (
                'project_id: "research-copilot"\n'
                'project_name: "Research Copilot Project"\n'
                'schema_version: "2.0.0"\n'
                '\n'
                'default_domain: "custom"\n'
                'default_workflow: "quick_exploratory"\n'
                'default_provider: "generic"\n'
                '\n'
                'literature_recursion_depth: 3\n'
                'literature_top_k_per_seed: 25\n'
                'literature_max_results_total: 300\n'
                '\n'
                'max_prompt_tokens: 12000\n'
                '\n'
                'data_raw_dir: "data_raw"\n'
                'docs_input_dir: "docs_input"\n'
                'reports_dir: "reports"\n'
                'analysis_dir: "analysis"\n'
                'logs_dir: "reports/logs"\n'
                'baseline_dir: "reports/baseline"\n'
                'literature_dir: "reports/literature"\n'
                'data_quality_dir: "reports/data_quality"\n'
                'audit_dir: "reports/audit"\n'
                'manuscript_dir: "reports/manuscript"\n'
                'tables_dir: "reports/tables"\n'
                'figures_dir: "reports/figures"\n'
                'dashboards_dir: "reports/dashboards"\n'
                '\n'
                'methods_log_path: "reports/logs/methods_log.md"\n'
                'data_dictionary_path: "reports/data_dictionary.md"\n'
                'citations_path: "reports/papers_and_tools_cited.md"\n'
                'question_evolution_path: "reports/question_evolution.md"\n'
                '\n'
                'dag_json_path: ".research/workflow_dag.json"\n'
                'dag_mermaid_path: ".research/workflow_dag.mermaid"\n'
                'state_dir: ".research/state"\n'
                'data_versions_path: ".research/data_versions.yaml"\n'
            ),
        )


def load_config() -> Dict[str, Any]:
    ensure_scaffold()
    return load_yaml_file(CONFIG_FILE)


def dag_paths(config: Dict[str, Any]) -> Tuple[Path, Path]:
    dag_json = config_path(config, "dag_json_path", DAG_JSON_DEFAULT)
    dag_mermaid = config_path(config, "dag_mermaid_path", DAG_MERMAID_DEFAULT)
    return dag_json, dag_mermaid


def state_paths(config: Dict[str, Any]) -> Tuple[Path, Path]:
    state_dir = config_path(config, "state_dir", STATE_DIR)
    run_log = state_dir / "run_log.jsonl"
    return state_dir, run_log


def data_versions_path(config: Dict[str, Any]) -> Path:
    return config_path(config, "data_versions_path", DATA_VERSIONS_DEFAULT)


def load_guardrails() -> str:
    path = AGENTS_DIR / "00_core_guardrails.md"
    return read_text(path) if path.exists() else ""


def load_domain_profile(domain_id: str) -> Dict[str, Any]:
    candidate = DOMAINS_DIR / f"{domain_id}.yaml"
    if candidate.exists():
        return load_yaml_file(candidate)
    # fall back to template/custom
    template = DOMAINS_DIR / "custom_template.yaml"
    return load_yaml_file(template) if template.exists() else {"domain_id": domain_id}


def load_workflow(workflow_id: str) -> Dict[str, Any]:
    candidate = WORKFLOWS_DIR / f"{workflow_id}.yaml"
    if candidate.exists():
        return load_yaml_file(candidate)
    return {}


def format_prompt(system_text: str, user_text: str, provider: str) -> str:
    provider_norm = (provider or "generic").strip().lower()

    if provider_norm in {"gpt", "openai", "chatgpt"}:
        payload = [
            {"role": "system", "content": system_text.strip()},
            {"role": "user", "content": user_text.strip()},
        ]
        return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"

    if provider_norm in {"claude", "anthropic"}:
        combined = "<SYSTEM>\n" + system_text.strip() + "\n\n<USER>\n" + user_text.strip()
        return "Human:\n" + combined + "\n\nAssistant:\n"

    # generic / copilot / gemini / cursor
    return "# SYSTEM\n" + system_text.strip() + "\n\n# USER\n" + user_text.strip() + "\n"


def build_agent_user_text(
    agent: AgentDefinition,
    registry: Registry,
    config: Dict[str, Any],
    domain_profile: Dict[str, Any],
) -> str:
    provider = str(config_or_default(config, "default_provider", "generic"))
    domain_id = str(domain_profile.get("domain_id") or config_or_default(config, "default_domain", "custom"))

    lines: List[str] = []
    lines.append("EXECUTION TASK INSTRUCTION")
    lines.append(f"Provider: {provider}")
    lines.append(f"Domain: {domain_id}")
    lines.append(f"Execute agent: {agent.path.relative_to(PROJECT_ROOT)}")
    lines.append("")

    if domain_profile:
        lines.append("Domain profile (active):")
        for k in ["reporting_standard", "significance_threshold", "citation_style", "default_effect_size_metric"]:
            if k in domain_profile:
                lines.append(f"- {k}: {domain_profile[k]}")
        lines.append("")

    if agent.composes:
        lines.append("Skills composed by this agent (resolved paths):")
        for skill_id in agent.composes:
            skill = registry.skills.get(skill_id)
            if skill is None:
                lines.append(f"- {skill_id} (MISSING DEFINITION)")
            else:
                lines.append(f"- {skill_id}: {skill.path.relative_to(PROJECT_ROOT)}")
        lines.append("")

    lines.append("Required outputs (agent contract):")
    for out_path in agent.produces:
        lines.append(f"- {out_path}")
    lines.append("")
    lines.append("Execution note:")
    lines.append("- Follow each referenced skill file verbatim.")
    lines.append("- Halt on any missing required input.")
    lines.append("- Emit outputs exactly at the contracted paths.")
    return "\n".join(lines)


def build_skill_user_text(
    skill: SkillDefinition,
    config: Dict[str, Any],
    domain_profile: Dict[str, Any],
) -> str:
    provider = str(config_or_default(config, "default_provider", "generic"))
    domain_id = str(domain_profile.get("domain_id") or config_or_default(config, "default_domain", "custom"))

    lines: List[str] = []
    lines.append("EXECUTION TASK INSTRUCTION")
    lines.append(f"Provider: {provider}")
    lines.append(f"Domain: {domain_id}")
    lines.append(f"Execute skill: {skill.path.relative_to(PROJECT_ROOT)}")
    lines.append("")
    lines.append("Required outputs (skill contract):")
    for out_path in skill.produces:
        lines.append(f"- {out_path}")
    lines.append("")
    lines.append("Execution note:")
    lines.append("- Follow the skill file verbatim.")
    lines.append("- Halt on any missing required input.")
    lines.append("- Emit outputs exactly at the contracted paths.")
    return "\n".join(lines)


def render_agent_prompt(
    agent: AgentDefinition,
    registry: Registry,
    config: Dict[str, Any],
    domain_profile: Dict[str, Any],
    provider: str,
    inline: bool,
) -> str:
    system_text = load_guardrails()
    user_text = build_agent_user_text(agent, registry, config, domain_profile)

    if inline:
        user_text += "\n\n---\n\nAGENT FILE (INLINE)\n\n" + read_text(agent.path) + "\n"
        for skill_id in agent.composes:
            skill = registry.skills.get(skill_id)
            if skill is None:
                continue
            user_text += "\n---\n\nSKILL FILE (INLINE)\n\n" + read_text(skill.path) + "\n"

    return format_prompt(system_text, user_text, provider)


def render_skill_prompt(
    skill: SkillDefinition,
    config: Dict[str, Any],
    domain_profile: Dict[str, Any],
    provider: str,
    inline: bool,
) -> str:
    system_text = load_guardrails()
    user_text = build_skill_user_text(skill, config, domain_profile)

    if inline:
        user_text += "\n\n---\n\nSKILL FILE (INLINE)\n\n" + read_text(skill.path) + "\n"

    return format_prompt(system_text, user_text, provider)


def render_workflow_prompt(
    workflow: Dict[str, Any],
    registry: Registry,
    config: Dict[str, Any],
    domain_profile: Dict[str, Any],
    provider: str,
    inline: bool,
) -> str:
    system_text = load_guardrails()

    workflow_id = str(workflow.get("workflow_id") or "")
    name = str(workflow.get("name") or workflow_id)
    description = str(workflow.get("description") or "")
    agent_ids = list(workflow.get("agents") or [])

    domain_id = str(domain_profile.get("domain_id") or config_or_default(config, "default_domain", "custom"))

    lines: List[str] = []
    lines.append("WORKFLOW EXECUTION INSTRUCTION")
    lines.append(f"Provider: {provider}")
    lines.append(f"Domain: {domain_id}")
    lines.append(f"Workflow: {workflow_id} — {name}")
    if description:
        lines.append(f"Description: {description}")
    lines.append("")
    lines.append("Run agents in the listed order unless an explicit dependency requires otherwise:")
    for idx, agent_id in enumerate(agent_ids, start=1):
        agent = registry.agents.get(str(agent_id))
        if agent is None:
            lines.append(f"{idx}. {agent_id} (MISSING DEFINITION)")
        else:
            lines.append(f"{idx}. {agent.agent_id}: {agent.path.relative_to(PROJECT_ROOT)}")
    lines.append("")
    lines.append("Execution note:")
    lines.append("- For each agent, follow its composed skills and output contracts.")
    lines.append("- Update provenance artifacts (DAG) after each agent completion.")

    user_text = "\n".join(lines)

    if inline:
        seen_skill_ids: set[str] = set()
        for agent_id in agent_ids:
            agent = registry.agents.get(str(agent_id))
            if agent is None:
                continue
            user_text += "\n\n---\n\nAGENT FILE (INLINE)\n\n" + read_text(agent.path) + "\n"
            for skill_id in agent.composes:
                if skill_id in seen_skill_ids:
                    continue
                seen_skill_ids.add(skill_id)
                skill = registry.skills.get(skill_id)
                if skill is None:
                    continue
                user_text += "\n---\n\nSKILL FILE (INLINE)\n\n" + read_text(skill.path) + "\n"

    return format_prompt(system_text, user_text, provider)


def load_dag(dag_json_path: Path) -> Dict[str, Any]:
    if not dag_json_path.exists():
        return {
            "schema_version": "1.1.0",
            "generated": utc_now_iso(),
            "nodes": [],
            "edges": [],
        }

    try:
        return json.loads(read_text(dag_json_path))
    except Exception:
        return {
            "schema_version": "1.1.0",
            "generated": utc_now_iso(),
            "nodes": [],
            "edges": [],
        }


def _mermaid_escape(label: str) -> str:
    return label.replace("\\", "\\\\").replace('"', "\\\"")


def dag_to_mermaid(dag: Dict[str, Any]) -> str:
    nodes: List[Dict[str, Any]] = list(dag.get("nodes") or [])
    edges: List[Dict[str, Any]] = list(dag.get("edges") or [])

    id_map: Dict[str, str] = {}
    for idx, node in enumerate(nodes, start=1):
        node_id = str(node.get("id") or f"node_{idx}")
        id_map[node_id] = f"N{idx}"  # Mermaid-safe

    lines: List[str] = ["flowchart TD"]
    for node in nodes:
        node_id = str(node.get("id") or "")
        mermaid_id = id_map.get(node_id, node_id)
        label = str(node.get("label") or node_id)
        lines.append(f"    {mermaid_id}[\"{_mermaid_escape(label)}\"]")

    for edge in edges:
        src = id_map.get(str(edge.get("from") or ""), "")
        dst = id_map.get(str(edge.get("to") or ""), "")
        if src and dst:
            lines.append(f"    {src} --> {dst}")

    return "\n".join(lines) + "\n"


def save_dag(dag_json_path: Path, dag_mermaid_path: Path, dag: Dict[str, Any]) -> None:
    dag["generated"] = utc_now_iso()
    write_text(dag_json_path, json.dumps(dag, indent=2))
    write_text(dag_mermaid_path, dag_to_mermaid(dag))


def append_run_log(run_log_path: Path, event: Dict[str, Any]) -> None:
    append_text(run_log_path, json.dumps(event, ensure_ascii=False) + "\n")


def latest_data_version(records: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not records:
        return None
    return records[-1]


def next_version_id(records: List[Dict[str, Any]]) -> str:
    last = latest_data_version(records)
    if not last:
        return "v1"
    last_id = str(last.get("version_id") or "")
    if last_id.startswith("v") and last_id[1:].isdigit():
        return f"v{int(last_id[1:]) + 1}"
    return f"v{len(records) + 1}"


def record_data_version_node(dag: Dict[str, Any], record: Dict[str, Any]) -> str:
    version_id = str(record.get("version_id") or "")
    node_id = f"data_version::{version_id}" if version_id else f"data_version::{run_stamp_utc()}"

    # Upsert node
    existing_ids = {str(n.get("id")) for n in (dag.get("nodes") or [])}
    if node_id not in existing_ids:
        dag["nodes"].append(
            {
                "id": node_id,
                "type": "data_version",
                "label": f"data:{record.get('action', 'version')}:{version_id}",
                "timestamp": str(record.get("timestamp_utc") or utc_now_iso()),
                "status": "RECORDED",
                "meta": record,
            }
        )
    return node_id


def record_agent_execution(
    dag: Dict[str, Any],
    agent: AgentDefinition,
    registry: Registry,
    stamp: str,
    parent_node_id: Optional[str] = None,
    data_version_node_id: Optional[str] = None,
) -> str:
    agent_node_id = f"agent::{agent.agent_id}::{stamp}"
    dag["nodes"].append(
        {
            "id": agent_node_id,
            "type": "agent",
            "label": f"agent:{agent.agent_id}",
            "timestamp": utc_now_iso(),
            "status": "REQUESTED",
        }
    )

    if parent_node_id:
        dag["edges"].append({"from": parent_node_id, "to": agent_node_id})

    if data_version_node_id:
        dag["edges"].append({"from": data_version_node_id, "to": agent_node_id})

    skill_node_ids: Dict[str, str] = {}
    for skill_id in agent.composes:
        skill_def = registry.skills.get(skill_id)
        skill_node_id = f"skill::{skill_id}::{agent.agent_id}::{stamp}"
        skill_node_ids[skill_id] = skill_node_id
        dag["nodes"].append(
            {
                "id": skill_node_id,
                "type": "skill",
                "label": f"skill:{skill_id}",
                "timestamp": utc_now_iso(),
                "status": "REQUESTED" if skill_def is not None else "MISSING_DEFINITION",
            }
        )
        dag["edges"].append({"from": agent_node_id, "to": skill_node_id})

    for skill_id in agent.composes:
        skill_def = registry.skills.get(skill_id)
        if skill_def is None:
            continue
        for dep in skill_def.depends_on:
            dep_node_id = skill_node_ids.get(dep)
            this_node_id = skill_node_ids.get(skill_id)
            if dep_node_id and this_node_id:
                dag["edges"].append({"from": dep_node_id, "to": this_node_id})

    return agent_node_id


def record_skill_execution(
    dag: Dict[str, Any],
    skill: SkillDefinition,
    stamp: str,
    data_version_node_id: Optional[str] = None,
) -> str:
    node_id = f"skill::{skill.skill_id}::standalone::{stamp}"
    dag["nodes"].append(
        {
            "id": node_id,
            "type": "skill",
            "label": f"skill:{skill.skill_id}",
            "timestamp": utc_now_iso(),
            "status": "REQUESTED",
        }
    )
    if data_version_node_id:
        dag["edges"].append({"from": data_version_node_id, "to": node_id})
    return node_id


def cmd_init(domain: Optional[str], workflow: Optional[str]) -> None:
    config = load_config()

    # Create standard project directories.
    analysis_dir = PROJECT_ROOT / str(config_or_default(config, "analysis_dir", "analysis"))
    reports_dir = PROJECT_ROOT / str(config_or_default(config, "reports_dir", "reports"))
    for sub in [
        analysis_dir,
        PROJECT_ROOT / "data" / "01_ingested",
        PROJECT_ROOT / "data" / "02_processed",
        PROJECT_ROOT / "data" / "03_analytical",
        reports_dir / "logs",
        reports_dir / "baseline",
        reports_dir / "literature",
        reports_dir / "data_quality",
        reports_dir / "audit",
        reports_dir / "manuscript",
        reports_dir / "tables",
        reports_dir / "figures",
        reports_dir / "dashboards",
    ]:
        sub.mkdir(parents=True, exist_ok=True)

    # Update config defaults if requested (line-edit to preserve user formatting).
    if domain:
        _replace_yaml_scalar_line(CONFIG_FILE, "default_domain", domain)
    if workflow:
        _replace_yaml_scalar_line(CONFIG_FILE, "default_workflow", workflow)

    print("Initialized v2 research workspace scaffold.")
    print(f"- Config: {CONFIG_FILE.relative_to(PROJECT_ROOT)}")
    if domain:
        print(f"- Default domain set: {domain}")
    if workflow:
        print(f"- Default workflow set: {workflow}")


def _replace_yaml_scalar_line(path: Path, key: str, value: str) -> None:
    if not path.exists():
        return
    lines = read_text(path).splitlines()
    out: List[str] = []
    replaced = False
    for line in lines:
        if line.strip().startswith(f"{key}:"):
            out.append(f"{key}: \"{value}\"")
            replaced = True
        else:
            out.append(line)
    if not replaced:
        out.append(f"{key}: \"{value}\"")
    write_text(path, "\n".join(out) + "\n")


def cmd_status() -> None:
    config = load_config()
    registry = Registry(SKILLS_DIR, AGENTS_DIR)
    registry.load()

    dag_json, dag_mermaid = dag_paths(config)
    dag = load_dag(dag_json)

    domain_id = str(config_or_default(config, "default_domain", "custom"))
    workflow_id = str(config_or_default(config, "default_workflow", "quick_exploratory"))
    provider = str(config_or_default(config, "default_provider", "generic"))

    data_records = load_yaml_documents_file(data_versions_path(config))
    last_data = latest_data_version(data_records)

    print("=====================================================================")
    print("               RESEARCH COPILOT (V2) — STATUS                        ")
    print("=====================================================================")
    print(f"Project Workspace: {PROJECT_ROOT.name}")
    print(f"Config:            {CONFIG_FILE.relative_to(PROJECT_ROOT)}")
    print(f"Default Provider:  {provider}")
    print(f"Default Domain:    {domain_id}")
    print(f"Default Workflow:  {workflow_id}")
    print(f"Discovered Skills: {len(registry.skills)}")
    print(f"Discovered Agents: {len(registry.agents)}")
    print(f"DAG JSON:          {dag_json.relative_to(PROJECT_ROOT)}")
    print(f"DAG Mermaid:       {dag_mermaid.relative_to(PROJECT_ROOT)}")
    print(f"DAG Nodes:         {len(dag.get('nodes') or [])}")
    print(f"DAG Edges:         {len(dag.get('edges') or [])}")
    if last_data:
        print(f"Latest Data:       {last_data.get('version_id')} ({last_data.get('action')})")
    else:
        print("Latest Data:       (none recorded)")
    print("---------------------------------------------------------------------")
    if registry.agents:
        print("Agents:")
        for agent_id in sorted(registry.agents.keys()):
            agent = registry.agents[agent_id]
            print(f"- {agent_id}: {agent.description}")
    else:
        print("Agents: (none found yet)")
    print("=====================================================================")


def cmd_list(kind: str) -> None:
    config = load_config()
    registry = Registry(SKILLS_DIR, AGENTS_DIR)
    registry.load()

    if kind == "skills":
        for skill_id in sorted(registry.skills.keys()):
            skill = registry.skills[skill_id]
            print(f"{skill_id}\t{skill.category}\t{skill.path.relative_to(PROJECT_ROOT)}")
        return

    if kind == "agents":
        for agent_id in sorted(registry.agents.keys()):
            agent = registry.agents[agent_id]
            print(f"{agent_id}\t{agent.version}\t{agent.path.relative_to(PROJECT_ROOT)}")
        return

    if kind == "domains":
        for path in sorted(DOMAINS_DIR.glob("*.yaml")):
            meta = load_yaml_file(path)
            domain_id = meta.get("domain_id") or path.stem
            print(f"{domain_id}\t{path.relative_to(PROJECT_ROOT)}")
        return

    if kind == "workflows":
        for path in sorted(WORKFLOWS_DIR.glob("*.yaml")):
            meta = load_yaml_file(path)
            workflow_id = meta.get("workflow_id") or path.stem
            print(f"{workflow_id}\t{path.relative_to(PROJECT_ROOT)}")
        return

    if kind == "history":
        _, run_log = state_paths(config)
        if not run_log.exists():
            return
        print(read_text(run_log), end="")
        return

    raise ValueError(f"Unknown list kind: {kind}")


def cmd_prompt_agent(agent_id: str, inline: bool, provider: Optional[str], domain: Optional[str]) -> None:
    config = load_config()
    registry = Registry(SKILLS_DIR, AGENTS_DIR)
    registry.load()

    agent = registry.agents.get(agent_id)
    if agent is None:
        print(f"Error: Unknown agent_id '{agent_id}'.", file=sys.stderr)
        sys.exit(1)

    provider_eff = str(provider or config_or_default(config, "default_provider", "generic"))
    domain_eff = str(domain or config_or_default(config, "default_domain", "custom"))
    domain_profile = load_domain_profile(domain_eff)
    config_with_provider = dict(config)
    config_with_provider["default_provider"] = provider_eff

    print(render_agent_prompt(agent, registry, config_with_provider, domain_profile, provider_eff, inline))


def cmd_prompt_skill(skill_id: str, inline: bool, provider: Optional[str], domain: Optional[str]) -> None:
    config = load_config()
    registry = Registry(SKILLS_DIR, AGENTS_DIR)
    registry.load()

    skill = registry.skills.get(skill_id)
    if skill is None:
        print(f"Error: Unknown skill_id '{skill_id}'.", file=sys.stderr)
        sys.exit(1)

    provider_eff = str(provider or config_or_default(config, "default_provider", "generic"))
    domain_eff = str(domain or config_or_default(config, "default_domain", "custom"))
    domain_profile = load_domain_profile(domain_eff)
    config_with_provider = dict(config)
    config_with_provider["default_provider"] = provider_eff

    print(render_skill_prompt(skill, config_with_provider, domain_profile, provider_eff, inline))


def cmd_prompt_workflow(workflow_id: str, inline: bool, provider: Optional[str], domain: Optional[str]) -> None:
    config = load_config()
    registry = Registry(SKILLS_DIR, AGENTS_DIR)
    registry.load()

    workflow = load_workflow(workflow_id)
    if not workflow:
        print(f"Error: Unknown workflow_id '{workflow_id}'.", file=sys.stderr)
        sys.exit(1)

    provider_eff = str(provider or config_or_default(config, "default_provider", "generic"))
    domain_eff = str(domain or config_or_default(config, "default_domain", "custom"))
    domain_profile = load_domain_profile(domain_eff)
    config_with_provider = dict(config)
    config_with_provider["default_provider"] = provider_eff

    print(render_workflow_prompt(workflow, registry, config_with_provider, domain_profile, provider_eff, inline))


def cmd_run_agent(agent_id: str, provider: Optional[str], domain: Optional[str]) -> None:
    config = load_config()
    registry = Registry(SKILLS_DIR, AGENTS_DIR)
    registry.load()

    agent = registry.agents.get(agent_id)
    if agent is None:
        print(f"Error: Unknown agent_id '{agent_id}'.", file=sys.stderr)
        sys.exit(1)

    provider_eff = str(provider or config_or_default(config, "default_provider", "generic"))
    domain_eff = str(domain or config_or_default(config, "default_domain", "custom"))
    domain_profile = load_domain_profile(domain_eff)

    stamp = run_stamp_utc()
    dag_json, dag_mermaid = dag_paths(config)
    dag = load_dag(dag_json)

    records = load_yaml_documents_file(data_versions_path(config))
    last_data = latest_data_version(records)
    data_node_id = None
    if last_data and last_data.get("version_id"):
        data_node_id = f"data_version::{last_data.get('version_id')}"

    record_agent_execution(dag, agent, registry, stamp, parent_node_id=None, data_version_node_id=data_node_id)
    save_dag(dag_json, dag_mermaid, dag)

    _, run_log = state_paths(config)
    append_run_log(
        run_log,
        {
            "timestamp_utc": utc_now_iso(),
            "command": "run agent",
            "agent_id": agent_id,
            "provider": provider_eff,
            "domain": domain_eff,
            "run_stamp": stamp,
        },
    )

    config_with_provider = dict(config)
    config_with_provider["default_provider"] = provider_eff
    print(render_agent_prompt(agent, registry, config_with_provider, domain_profile, provider_eff, inline=False))


def cmd_run_skill(skill_id: str, provider: Optional[str], domain: Optional[str]) -> None:
    config = load_config()
    registry = Registry(SKILLS_DIR, AGENTS_DIR)
    registry.load()

    skill = registry.skills.get(skill_id)
    if skill is None:
        print(f"Error: Unknown skill_id '{skill_id}'.", file=sys.stderr)
        sys.exit(1)

    provider_eff = str(provider or config_or_default(config, "default_provider", "generic"))
    domain_eff = str(domain or config_or_default(config, "default_domain", "custom"))
    domain_profile = load_domain_profile(domain_eff)

    stamp = run_stamp_utc()
    dag_json, dag_mermaid = dag_paths(config)
    dag = load_dag(dag_json)

    records = load_yaml_documents_file(data_versions_path(config))
    last_data = latest_data_version(records)
    data_node_id = None
    if last_data and last_data.get("version_id"):
        data_node_id = f"data_version::{last_data.get('version_id')}"

    record_skill_execution(dag, skill, stamp, data_version_node_id=data_node_id)
    save_dag(dag_json, dag_mermaid, dag)

    _, run_log = state_paths(config)
    append_run_log(
        run_log,
        {
            "timestamp_utc": utc_now_iso(),
            "command": "run skill",
            "skill_id": skill_id,
            "provider": provider_eff,
            "domain": domain_eff,
            "run_stamp": stamp,
        },
    )

    config_with_provider = dict(config)
    config_with_provider["default_provider"] = provider_eff
    print(render_skill_prompt(skill, config_with_provider, domain_profile, provider_eff, inline=False))


def cmd_run_workflow(workflow_id: str, provider: Optional[str], domain: Optional[str]) -> None:
    config = load_config()
    registry = Registry(SKILLS_DIR, AGENTS_DIR)
    registry.load()

    workflow = load_workflow(workflow_id)
    if not workflow:
        print(f"Error: Unknown workflow_id '{workflow_id}'.", file=sys.stderr)
        sys.exit(1)

    provider_eff = str(provider or config_or_default(config, "default_provider", "generic"))
    domain_eff = str(domain or config_or_default(config, "default_domain", "custom"))
    domain_profile = load_domain_profile(domain_eff)

    stamp = run_stamp_utc()
    dag_json, dag_mermaid = dag_paths(config)
    dag = load_dag(dag_json)

    workflow_node_id = f"workflow::{workflow_id}::{stamp}"
    dag["nodes"].append(
        {
            "id": workflow_node_id,
            "type": "workflow",
            "label": f"workflow:{workflow_id}",
            "timestamp": utc_now_iso(),
            "status": "REQUESTED",
        }
    )

    records = load_yaml_documents_file(data_versions_path(config))
    last_data = latest_data_version(records)
    data_node_id = None
    if last_data and last_data.get("version_id"):
        data_node_id = f"data_version::{last_data.get('version_id')}"

    agent_ids = list(workflow.get("agents") or [])
    previous_agent_node_id: Optional[str] = None
    for agent_id in agent_ids:
        agent = registry.agents.get(str(agent_id))
        if agent is None:
            dag["nodes"].append(
                {
                    "id": f"agent::{agent_id}::{stamp}",
                    "type": "agent",
                    "label": f"agent:{agent_id} (MISSING)",
                    "timestamp": utc_now_iso(),
                    "status": "MISSING_DEFINITION",
                }
            )
            dag["edges"].append({"from": workflow_node_id, "to": f"agent::{agent_id}::{stamp}"})
            continue

        node_id = record_agent_execution(
            dag,
            agent,
            registry,
            stamp,
            parent_node_id=workflow_node_id,
            data_version_node_id=data_node_id,
        )
        if previous_agent_node_id:
            dag["edges"].append({"from": previous_agent_node_id, "to": node_id})
        previous_agent_node_id = node_id

    save_dag(dag_json, dag_mermaid, dag)

    _, run_log = state_paths(config)
    append_run_log(
        run_log,
        {
            "timestamp_utc": utc_now_iso(),
            "command": "run workflow",
            "workflow_id": workflow_id,
            "provider": provider_eff,
            "domain": domain_eff,
            "run_stamp": stamp,
        },
    )

    config_with_provider = dict(config)
    config_with_provider["default_provider"] = provider_eff
    print(render_workflow_prompt(workflow, registry, config_with_provider, domain_profile, provider_eff, inline=False))


def cmd_data_add(path: str, rationale: str) -> None:
    config = load_config()
    target = (PROJECT_ROOT / path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
    if not target.exists() or not target.is_file():
        print(f"Error: data path not found or not a file: {target}", file=sys.stderr)
        sys.exit(1)

    records_path = data_versions_path(config)
    records = load_yaml_documents_file(records_path)
    version_id = next_version_id(records)

    rel = str(target.relative_to(PROJECT_ROOT)) if str(target).startswith(str(PROJECT_ROOT)) else str(target)
    record = {
        "version_id": version_id,
        "action": "add",
        "timestamp_utc": utc_now_iso(),
        "path": rel,
        "sha256": sha256_file(target),
        "size_bytes": target.stat().st_size,
        "rationale": rationale or "",
    }
    append_yaml_document(records_path, record)

    dag_json, dag_mermaid = dag_paths(config)
    dag = load_dag(dag_json)
    record_data_version_node(dag, record)
    save_dag(dag_json, dag_mermaid, dag)

    print(f"Recorded data version {version_id} (add): {rel}")


def cmd_data_remove(criteria: str, rationale: str) -> None:
    config = load_config()
    records_path = data_versions_path(config)
    records = load_yaml_documents_file(records_path)
    version_id = next_version_id(records)

    record = {
        "version_id": version_id,
        "action": "remove",
        "timestamp_utc": utc_now_iso(),
        "criteria": criteria,
        "rationale": rationale or "",
    }
    append_yaml_document(records_path, record)

    dag_json, dag_mermaid = dag_paths(config)
    dag = load_dag(dag_json)
    record_data_version_node(dag, record)
    save_dag(dag_json, dag_mermaid, dag)

    print(f"Recorded data version {version_id} (remove): {criteria}")


def cmd_data_status() -> None:
    config = load_config()
    records = load_yaml_documents_file(data_versions_path(config))
    last = latest_data_version(records)
    if not last:
        print("No data versions recorded.")
        return
    print(json.dumps(last, indent=2, ensure_ascii=False))


def cmd_data_diff(v1: str, v2: str) -> None:
    config = load_config()
    records = load_yaml_documents_file(data_versions_path(config))
    by_id = {str(r.get("version_id")): r for r in records}
    r1 = by_id.get(v1)
    r2 = by_id.get(v2)
    if not r1 or not r2:
        print("Error: version_id not found.", file=sys.stderr)
        sys.exit(1)
    print("=== " + v1 + " ===")
    print(json.dumps(r1, indent=2, ensure_ascii=False))
    print("=== " + v2 + " ===")
    print(json.dumps(r2, indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Skills-first Research Copilot orchestrator (v2).")
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="Initialize standard v2 directories and defaults")
    init_parser.add_argument("--domain", help="Set default domain")
    init_parser.add_argument("--workflow", help="Set default workflow")

    subparsers.add_parser("status", help="Show v2 registry + DAG status")

    list_parser = subparsers.add_parser("list", help="List skills/agents/domains/workflows/history")
    list_parser.add_argument("kind", choices=["skills", "agents", "domains", "workflows", "history"])

    prompt_parser = subparsers.add_parser("prompt", help="Print a provider-adapted prompt")
    prompt_parser.add_argument("--provider", help="Override provider formatting (generic|claude|gpt|gemini|copilot)")
    prompt_parser.add_argument("--domain", help="Override active domain")
    prompt_sub = prompt_parser.add_subparsers(dest="kind")
    prompt_agent = prompt_sub.add_parser("agent", help="Prompt for an agent")
    prompt_agent.add_argument("agent_id")
    prompt_agent.add_argument("--inline", action="store_true", help="Inline agent + skill files")
    prompt_skill = prompt_sub.add_parser("skill", help="Prompt for a skill")
    prompt_skill.add_argument("skill_id")
    prompt_skill.add_argument("--inline", action="store_true", help="Inline the skill file")
    prompt_workflow = prompt_sub.add_parser("workflow", help="Prompt for a workflow")
    prompt_workflow.add_argument("workflow_id")
    prompt_workflow.add_argument("--inline", action="store_true", help="Inline referenced agent + skill files")

    run_parser = subparsers.add_parser("run", help="Record provenance nodes and print prompt")
    run_parser.add_argument("--provider", help="Override provider formatting (generic|claude|gpt|gemini|copilot)")
    run_parser.add_argument("--domain", help="Override active domain")
    run_sub = run_parser.add_subparsers(dest="kind")
    run_agent = run_sub.add_parser("agent", help="Record agent + skills in DAG and emit prompt")
    run_agent.add_argument("agent_id")
    run_skill = run_sub.add_parser("skill", help="Record skill in DAG and emit prompt")
    run_skill.add_argument("skill_id")
    run_workflow = run_sub.add_parser("workflow", help="Record workflow + agents + skills in DAG and emit prompt")
    run_workflow.add_argument("workflow_id")

    data_parser = subparsers.add_parser("data", help="Data version tracking")
    data_sub = data_parser.add_subparsers(dest="kind")
    data_add = data_sub.add_parser("add", help="Add a data file and record a version")
    data_add.add_argument("path")
    data_add.add_argument("--rationale", default="", help="Rationale for addition")
    data_remove = data_sub.add_parser("remove", help="Record a logical removal (criteria-only)")
    data_remove.add_argument("criteria")
    data_remove.add_argument("--rationale", default="", help="Rationale for removal")
    data_sub.add_parser("status", help="Show latest data version record")
    data_diff = data_sub.add_parser("diff", help="Show metadata for two data versions")
    data_diff.add_argument("v1")
    data_diff.add_argument("v2")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(domain=args.domain, workflow=args.workflow)
        return

    if args.command == "status":
        cmd_status()
        return

    if args.command == "list":
        cmd_list(args.kind)
        return

    if args.command == "prompt":
        if args.kind == "agent":
            cmd_prompt_agent(args.agent_id, inline=bool(args.inline), provider=args.provider, domain=args.domain)
            return
        if args.kind == "skill":
            cmd_prompt_skill(args.skill_id, inline=bool(args.inline), provider=args.provider, domain=args.domain)
            return
        if args.kind == "workflow":
            cmd_prompt_workflow(args.workflow_id, inline=bool(args.inline), provider=args.provider, domain=args.domain)
            return

    if args.command == "run":
        if args.kind == "agent":
            cmd_run_agent(args.agent_id, provider=args.provider, domain=args.domain)
            return
        if args.kind == "skill":
            cmd_run_skill(args.skill_id, provider=args.provider, domain=args.domain)
            return
        if args.kind == "workflow":
            cmd_run_workflow(args.workflow_id, provider=args.provider, domain=args.domain)
            return

    if args.command == "data":
        if args.kind == "add":
            cmd_data_add(args.path, rationale=str(args.rationale or ""))
            return
        if args.kind == "remove":
            cmd_data_remove(args.criteria, rationale=str(args.rationale or ""))
            return
        if args.kind == "status":
            cmd_data_status()
            return
        if args.kind == "diff":
            cmd_data_diff(args.v1, args.v2)
            return

    parser.print_help()


if __name__ == "__main__":
    main()
