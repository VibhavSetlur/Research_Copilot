# Skill: D3.js Figure Templates & Jinja2 Injection

## Purpose
Some visualizations (such as Sankey/alluvial flow, chord diagrams, and animated timelines) cannot be produced cleanly or with professional quality in Python. This skill describes how to inject Python data structures into standalone D3.js HTML/JS templates using the Jinja2 template engine.

## Installation
Ensure Jinja2 is installed:
```bash
pip install jinja2
```

## Protocol & Best Practices
1. **Separation of Concerns:** Keep D3.js boilerplate and CSS rendering separate in an HTML template file.
2. **Inject Clean JSON:** Use the `to_json()` method or `json.dumps()` in Python to format data into JSON string literals, then output with raw Jinja escaping (`{{ data | safe }}`) inside a `<script>` tag.
3. **Handle Local Resources:** Embed D3.js libraries directly (via CDN or local file links if offline compatibility is required).

## Code Template

### HTML Template (`sankey_template.html`)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sankey Diagram</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://unpkg.com/d3-sankey@0.12.3/dist/d3-sankey.min.js"></script>
    <style>
        .node rect { fill-opacity: 0.9; shape-rendering: crispEdges; }
        .node text { pointer-events: none; text-shadow: 0 1px 0 #fff; font-family: sans-serif; font-size: 10px; }
        .link { fill: none; stroke: #000; stroke-opacity: 0.2; }
        .link:hover { stroke-opacity: 0.5; }
    </style>
</head>
<body>
    <div id="chart"></div>
    <script>
        // Inject Python data structure directly
        const graph = {{ data_json | safe }};
        const width = 800;
        const height = 500;

        const svg = d3.select("#chart").append("svg")
            .attr("width", width)
            .attr("height", height);

        const sankey = d3.sankey()
            .nodeWidth(15)
            .nodePadding(10)
            .extent([[1, 1], [width - 1, height - 6]]);

        const {nodes, links} = sankey(graph);

        // Nodes & Links rendering logic
        svg.append("g")
            .selectAll("rect")
            .data(nodes)
            .join("rect")
            .attr("x", d => d.x0)
            .attr("y", d => d.y0)
            .attr("height", d => d.y1 - d.y0)
            .attr("width", d => d.x1 - d.x0)
            .attr("fill", "steelblue");

        svg.append("g")
            .attr("fill", "none")
            .selectAll("g")
            .data(links)
            .join("path")
            .attr("d", d3.sankeyLinkHorizontal())
            .attr("stroke", "#888")
            .attr("stroke-width", d => Math.max(1, d.width));
    </script>
</body>
</html>
```

### Python Injection Code
```python
import json
from jinja2 import Template

def generate_sankey_diagram(nodes: list, links: list, template_path: str, output_path: str):
    data = {"nodes": nodes, "links": links}
    
    with open(template_path, "r") as f:
        template_str = f.read()
        
    template = Template(template_str)
    rendered_html = template.render(data_json=json.dumps(data))
    
    with open(output_path, "w") as f:
        f.write(rendered_html)
        
    print(f"Successfully generated D3 Sankey: {output_path}")
```
