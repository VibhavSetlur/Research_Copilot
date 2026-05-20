#!/usr/bin/env python3
"""DAG Visualizer — Web viewer for execution_dag.json.

Creates a local web application that visualizes the research data pipeline
as an interactive flowchart. Failing nodes are highlighted in red.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def _load_dag() -> dict:
    """Load the execution DAG."""
    dag_path = Path(".research/cache/execution_dag.json")
    if dag_path.exists():
        with open(dag_path) as f:
            return json.load(f)
    return {"nodes": {}, "edges": []}


def generate_dag_html(output_path: str = "reports/dashboards/dag_viewer.html") -> str:
    """Generate an interactive DAG visualization as a standalone HTML file.

    Args:
        output_path: Path to write the HTML file

    Returns:
        Path to generated HTML file
    """
    dag = _load_dag()
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    # Build node data for visualization
    nodes = []
    for node_id, node_data in dag.get("nodes", {}).items():
        status = node_data.get("status", "pending")
        status_color = {
            "complete": "#22c55e",
            "running": "#3b82f6",
            "failed": "#ef4444",
            "pending": "#6b7280",
        }.get(status, "#6b7280")

        script_name = Path(node_data.get("script_path", "")).name
        inputs = node_data.get("input_files", [])
        outputs = node_data.get("output_files", [])
        iteration = node_data.get("iteration_id", "")

        nodes.append({
            "id": node_id,
            "label": script_name or node_id,
            "status": status,
            "color": status_color,
            "script_path": node_data.get("script_path", ""),
            "iteration_id": iteration,
            "timestamp": node_data.get("timestamp", ""),
            "inputs": inputs,
            "outputs": outputs,
            "depends_on": node_data.get("depends_on", []),
        })

    edges = []
    for edge in dag.get("edges", []):
        edges.append({
            "from": edge["from"],
            "to": edge["to"],
        })

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Copilot — Execution DAG</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }}
        .header {{ background: #1e293b; padding: 1rem 2rem; border-bottom: 1px solid #334155; display: flex; justify-content: space-between; align-items: center; }}
        .header h1 {{ font-size: 1.25rem; font-weight: 600; }}
        .header .stats {{ display: flex; gap: 1.5rem; font-size: 0.875rem; }}
        .stat {{ display: flex; align-items: center; gap: 0.5rem; }}
        .stat-dot {{ width: 8px; height: 8px; border-radius: 50%; }}
        .container {{ padding: 2rem; display: flex; gap: 2rem; }}
        .dag-container {{ flex: 1; background: #1e293b; border-radius: 0.5rem; padding: 1.5rem; overflow: auto; min-height: 600px; }}
        .sidebar {{ width: 320px; background: #1e293b; border-radius: 0.5rem; padding: 1.5rem; }}
        .node {{ display: inline-flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; margin: 0.5rem; background: #334155; border-radius: 0.5rem; border-left: 4px solid; cursor: pointer; transition: all 0.2s; }}
        .node:hover {{ background: #475569; transform: translateY(-2px); }}
        .node.selected {{ background: #475569; box-shadow: 0 0 0 2px #3b82f6; }}
        .node-label {{ font-size: 0.875rem; font-weight: 500; }}
        .node-status {{ font-size: 0.75rem; padding: 0.125rem 0.5rem; border-radius: 9999px; background: rgba(255,255,255,0.1); }}
        .edge {{ stroke: #475569; stroke-width: 2; fill: none; }}
        .edge.failed {{ stroke: #ef4444; }}
        svg {{ width: 100%; height: 100%; }}
        .detail-section {{ margin-bottom: 1rem; }}
        .detail-section h3 {{ font-size: 0.75rem; text-transform: uppercase; color: #94a3b8; margin-bottom: 0.5rem; letter-spacing: 0.05em; }}
        .detail-section p {{ font-size: 0.875rem; color: #cbd5e1; }}
        .detail-section ul {{ list-style: none; }}
        .detail-section li {{ font-size: 0.875rem; color: #cbd5e1; padding: 0.25rem 0; }}
        .legend {{ display: flex; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap; }}
        .legend-item {{ display: flex; align-items: center; gap: 0.5rem; font-size: 0.75rem; }}
        .empty-state {{ text-align: center; padding: 4rem 2rem; color: #64748b; }}
        .empty-state svg {{ width: 64px; height: 64px; margin-bottom: 1rem; opacity: 0.5; }}
        .refresh-btn {{ background: #3b82f6; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.375rem; cursor: pointer; font-size: 0.875rem; }}
        .refresh-btn:hover {{ background: #2563eb; }}
        .flow-row {{ display: flex; align-items: center; margin: 0.5rem 0; flex-wrap: wrap; }}
        .flow-arrow {{ color: #64748b; margin: 0 0.25rem; font-size: 1.25rem; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Research Copilot — Execution DAG</h1>
        <div class="stats">
            <div class="stat">
                <span class="stat-dot" style="background: #22c55e;"></span>
                <span>{len([n for n in nodes if n['status'] == 'complete'])} Complete</span>
            </div>
            <div class="stat">
                <span class="stat-dot" style="background: #ef4444;"></span>
                <span>{len([n for n in nodes if n['status'] == 'failed'])} Failed</span>
            </div>
            <div class="stat">
                <span class="stat-dot" style="background: #6b7280;"></span>
                <span>{len([n for n in nodes if n['status'] == 'pending'])} Pending</span>
            </div>
            <button class="refresh-btn" onclick="location.reload()">Refresh</button>
        </div>
    </div>

    <div class="container">
        <div class="dag-container">
            <div class="legend">
                <div class="legend-item"><span class="stat-dot" style="background: #22c55e;"></span> Complete</div>
                <div class="legend-item"><span class="stat-dot" style="background: #3b82f6;"></span> Running</div>
                <div class="legend-item"><span class="stat-dot" style="background: #ef4444;"></span> Failed</div>
                <div class="legend-item"><span class="stat-dot" style="background: #6b7280;"></span> Pending</div>
            </div>

            {generate_flow_html(nodes, edges)}
        </div>

        <div class="sidebar">
            <div id="node-detail">
                <div class="empty-state">
                    <p>Click a node to view details</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        const nodes = {json.dumps(nodes)};
        const edges = {json.dumps(edges)};

        function showNodeDetail(nodeId) {{
            const node = nodes.find(n => n.id === nodeId);
            if (!node) return;

            document.querySelectorAll('.node').forEach(el => el.classList.remove('selected'));
            document.querySelector(`[data-node-id="${{nodeId}}"]`)?.classList.add('selected');

            const detail = document.getElementById('node-detail');
            detail.innerHTML = `
                <div class="detail-section">
                    <h3>Node</h3>
                    <p><strong>${{node.label}}</strong></p>
                </div>
                <div class="detail-section">
                    <h3>Status</h3>
                    <p style="color: ${{node.color}}">● ${{node.status.toUpperCase()}}</p>
                </div>
                <div class="detail-section">
                    <h3>Script</h3>
                    <p style="font-family: monospace; font-size: 0.75rem;">${{node.script_path || 'N/A'}}</p>
                </div>
                <div class="detail-section">
                    <h3>Timestamp</h3>
                    <p>${{node.timestamp || 'N/A'}}</p>
                </div>
                ${{node.iteration_id ? `
                <div class="detail-section">
                    <h3>Iteration</h3>
                    <p>${{node.iteration_id}}</p>
                </div>` : ''}}
                <div class="detail-section">
                    <h3>Input Files (${{node.inputs.length}})</h3>
                    <ul>${{node.inputs.map(f => `<li>📄 ${{f}}</li>`).join('') || '<li>None</li>'}}</ul>
                </div>
                <div class="detail-section">
                    <h3>Output Files (${{node.outputs.length}})</h3>
                    <ul>${{node.outputs.map(f => `<li>📊 ${{f}}</li>`).join('') || '<li>None</li>'}}</ul>
                </div>
                <div class="detail-section">
                    <h3>Dependencies</h3>
                    <ul>${{node.depends_on.map(d => `<li>→ ${{d}}</li>`).join('') || '<li>None (root node)</li>'}}</ul>
                </div>
            `;
        }}

        // Attach click handlers
        document.querySelectorAll('.node').forEach(el => {{
            el.addEventListener('click', () => showNodeDetail(el.dataset.nodeId));
        }});
    </script>
</body>
</html>"""

    output.write_text(html)
    return str(output)


def generate_flow_html(nodes: list, edges: list) -> str:
    """Generate a simple flow visualization."""
    if not nodes:
        return """
        <div class="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
            </svg>
            <h2>No executions recorded yet</h2>
            <p>Run your first analysis script to see the DAG visualization.</p>
        </div>
        """

    # Group nodes by their depth (longest path from root)
    depth_map = {}
    node_ids = {n["id"] for n in nodes}

    def get_depth(node_id, visited=None):
        if visited is None:
            visited = set()
        if node_id in visited:
            return 0
        visited.add(node_id)

        node = next((n for n in nodes if n["id"] == node_id), None)
        if not node:
            return 0

        deps = [d for d in node.get("depends_on", []) if d in node_ids]
        if not deps:
            return 0
        return 1 + max(get_depth(d, visited) for d in deps)

    for node in nodes:
        depth_map[node["id"]] = get_depth(node["id"])

    # Group by depth
    depth_groups = {}
    for node_id, depth in depth_map.items():
        depth_groups.setdefault(depth, []).append(node_id)

    html_parts = []

    for depth in sorted(depth_groups.keys()):
        group_nodes = depth_groups[depth]
        html_parts.append('<div class="flow-row">')

        for i, node_id in enumerate(group_nodes):
            node = next(n for n in nodes if n["id"] == node_id)
            html_parts.append(
                f'<div class="node" data-node-id="{node_id}" '
                f'style="border-left-color: {node["color"]};">'
                f'<span class="node-label">{node["label"]}</span>'
                f'<span class="node-status" style="color: {node["color"]}">{node["status"]}</span>'
                f'</div>'
            )

            if i < len(group_nodes) - 1:
                html_parts.append('<span class="flow-arrow">│</span>')

        html_parts.append('</div>')

        # Add arrows to next level
        if depth + 1 in depth_groups:
            html_parts.append('<div class="flow-row" style="color: #475569; font-size: 1.5rem; padding: 0 1rem;">↓</div>')

    return "\n".join(html_parts)


def cmd_dag_viewer(args):
    """CLI command handler for DAG viewer."""
    output_path = getattr(args, "output", "reports/dashboards/dag_viewer.html")
    path = generate_dag_html(output_path)
    print(f"DAG viewer generated: {path}")
    print(f"Open in browser: file://{Path(path).absolute()}")


if __name__ == "__main__":
    path = generate_dag_html()
    print(f"DAG viewer generated: {path}")
    print(f"Open in browser: file://{Path(path).absolute()}")
