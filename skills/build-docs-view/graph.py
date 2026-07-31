#!/usr/bin/env python3
"""Knowledge-graph viewer for a canon project.

Self-contained, stdlib only. Walks the conformant corpus, resolves
root-anchored links, and writes one interactive HTML page: a Cytoscape graph
with compound clusters for topics, nodes colored by type, plus search and a
type filter. Reuses canon's frontmatter parser (sibling ../canon/canon.py).
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "canon"))
import canon  # noqa: E402

_LINK_RE = re.compile(r"\[[^\]]*\]\((/[^)\s]+\.md)(?:#[^)]*)?\)")
_RELATION_KEYS = ("derived_from", "bears_on", "supersedes")

_PALETTE = {
    "decision": "#f59e0b",
    "finding": "#10b981",
    "source": "#3b82f6",
    "concept": "#8b5cf6",
    "topic": "#ef4444",
    "provenance": "#06b6d4",
    "register": "#94a3b8",
    "glossary": "#94a3b8",
}
_DEFAULT_COLOR = "#cbd5e1"


def _node_id(relpath: str) -> str:
    return relpath[:-3] if relpath.endswith(".md") else relpath


def _cluster_of(page: canon.Page, topics: set[str]) -> tuple[str, str] | None:
    """Return (cluster_id, cluster_label) for compound grouping, or None."""
    parts = page.relpath.split("/")
    if page.relpath.startswith("topics/"):
        # a hub (topics/<t>.md) or a member (topics/<t>/...)
        name = parts[1][:-3] if len(parts) == 2 else parts[1]
        return f"topic:{name}", name
    for tag in page.tags:
        if tag in topics:
            return f"topic:{tag}", tag
    if len(parts) > 1:
        return f"zone:{parts[0]}", parts[0]
    return None


def _link_targets(body: str, fm: dict) -> list[str]:
    out: list[str] = []
    for m in _LINK_RE.finditer(body):
        out.append(_node_id(m.group(1).lstrip("/")))
    for key in _RELATION_KEYS:
        val = fm.get(key)
        if not val:
            continue
        items = val if isinstance(val, list) else [val]
        for item in items:
            item = str(item)
            if item.startswith("/") and item.endswith(".md"):
                out.append(_node_id(item.lstrip("/")))
    return out


def build_graph(root: Path) -> dict:
    pages = canon.load_pages(root)
    topics = {canon._topic_name(p.relpath) for p in pages if p.type == "topic"}
    ids = {_node_id(p.relpath) for p in pages}

    nodes: list[dict] = []
    clusters: dict[str, str] = {}
    bodies: dict[str, str] = {}
    for p in pages:
        nid = _node_id(p.relpath)
        cluster = _cluster_of(p, topics)
        data = {
            "id": nid,
            "label": p.title,
            "type": p.type or "untyped",
            "description": p.description,
            "resource": str(p.fm.get("resource") or ""),
            "tags": p.tags,
            "color": _PALETTE.get(p.type, _DEFAULT_COLOR),
        }
        if cluster:
            clusters[cluster[0]] = cluster[1]
            data["parent"] = cluster[0]
        nodes.append({"data": data})
        bodies[nid] = p.body

    for cid, label in sorted(clusters.items()):
        nodes.append({"data": {"id": cid, "label": label, "isCluster": True}})

    edges: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for p in pages:
        src = _node_id(p.relpath)
        for tgt in _link_targets(p.body, p.fm):
            if tgt == src or tgt not in ids or (src, tgt) in seen:
                continue
            seen.add((src, tgt))
            edges.append({"data": {"id": f"{src}__{tgt}", "source": src, "target": tgt}})

    types = sorted({p.type or "untyped" for p in pages})
    return {"nodes": nodes, "edges": edges, "bodies": bodies,
            "types": types, "palette": _PALETTE}


_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__NAME__ — knowledge graph</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.30.2/cytoscape.min.js"></script>
<style>
  * { box-sizing: border-box; }
  body { margin: 0; font: 14px/1.5 system-ui, sans-serif; color: #0f172a; }
  #bar { padding: 8px 12px; border-bottom: 1px solid #e2e8f0; display: flex;
         gap: 12px; align-items: center; flex-wrap: wrap; }
  #bar h1 { font-size: 15px; margin: 0 12px 0 0; }
  #bar input { padding: 4px 8px; border: 1px solid #cbd5e1; border-radius: 4px; }
  #types label { margin-right: 8px; white-space: nowrap; }
  #main { display: flex; height: calc(100vh - 46px); }
  #cy { flex: 1; height: 100%; }
  #panel { width: 340px; border-left: 1px solid #e2e8f0; padding: 16px;
           overflow-y: auto; }
  #panel .type { font-size: 12px; text-transform: uppercase; letter-spacing: .05em;
                 color: #64748b; }
  #panel pre { white-space: pre-wrap; word-wrap: break-word; background: #f8fafc;
               padding: 10px; border-radius: 4px; font-size: 12px; }
  .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%;
         margin-right: 4px; vertical-align: middle; }
</style>
</head>
<body>
<div id="bar">
  <h1>__NAME__</h1>
  <input id="search" placeholder="search nodes…" size="20">
  <span id="types"></span>
</div>
<div id="main">
  <div id="cy"></div>
  <div id="panel"><em>Click a node to read its page.</em></div>
</div>
<script>
const DATA = __DATA__;
const cy = cytoscape({
  container: document.getElementById('cy'),
  elements: { nodes: DATA.nodes, edges: DATA.edges },
  style: [
    { selector: 'node[!isCluster]', style: {
        'background-color': 'data(color)', 'label': 'data(label)',
        'font-size': 9, 'text-wrap': 'wrap', 'text-max-width': 90,
        'width': 22, 'height': 22 } },
    { selector: 'node[?isCluster]', style: {
        'background-opacity': 0.06, 'background-color': '#475569',
        'border-width': 1, 'border-color': '#cbd5e1', 'label': 'data(label)',
        'font-size': 12, 'color': '#475569', 'text-valign': 'top',
        'shape': 'round-rectangle', 'padding': 12 } },
    { selector: 'edge', style: {
        'width': 1, 'line-color': '#cbd5e1', 'target-arrow-color': '#cbd5e1',
        'target-arrow-shape': 'triangle', 'curve-style': 'bezier',
        'arrow-scale': 0.7 } },
    { selector: '.dim', style: { 'opacity': 0.12 } },
    { selector: '.hl', style: { 'border-width': 3, 'border-color': '#0f172a' } }
  ],
  layout: { name: 'cose', animate: false, nodeRepulsion: 8000, idealEdgeLength: 60,
            nestingFactor: 1.2, padding: 20 }
});

const panel = document.getElementById('panel');
cy.on('tap', 'node[!isCluster]', e => {
  const d = e.target.data();
  const body = DATA.bodies[d.id] || '';
  const res = d.resource ? '<p><a href="'+d.resource+'">'+d.resource+'</a></p>' : '';
  const tags = (d.tags||[]).map(t => '<code>'+t+'</code>').join(' ');
  panel.innerHTML = '<div class="type">'+d.type+'</div><h2>'+d.label+'</h2>'
    + '<p>'+(d.description||'')+'</p>' + res
    + (tags ? '<p>'+tags+'</p>' : '')
    + '<pre>'+body.replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))+'</pre>';
  cy.elements().removeClass('hl');
  e.target.addClass('hl');
});

const typesEl = document.getElementById('types');
const active = new Set(DATA.types);
DATA.types.forEach(t => {
  const color = DATA.palette[t] || '#cbd5e1';
  const lab = document.createElement('label');
  lab.innerHTML = '<input type="checkbox" checked data-t="'+t+'">'
    + '<span class="dot" style="background:'+color+'"></span>'+t;
  typesEl.appendChild(lab);
  lab.querySelector('input').addEventListener('change', ev => {
    ev.target.checked ? active.add(t) : active.delete(t);
    applyTypes();
  });
});
function applyTypes() {
  cy.nodes('[!isCluster]').forEach(n => {
    n.style('display', active.has(n.data('type')) ? 'element' : 'none');
  });
}

document.getElementById('search').addEventListener('input', ev => {
  const q = ev.target.value.trim().toLowerCase();
  cy.elements().removeClass('dim');
  if (!q) return;
  const match = cy.nodes('[!isCluster]').filter(n =>
    (n.data('label')||'').toLowerCase().includes(q));
  if (match.length) {
    cy.elements().addClass('dim');
    match.removeClass('dim');
    match.neighborhood().removeClass('dim');
  }
});
</script>
</body>
</html>
"""


def generate(root: Path, out_path: Path, name: str | None = None) -> dict:
    graph = build_graph(root)
    name = html.escape(name or root.resolve().name)
    page = (_TEMPLATE
            .replace("__NAME__", name)
            .replace("__DATA__", json.dumps(graph)))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page, encoding="utf-8")
    node_count = sum(1 for n in graph["nodes"] if not n["data"].get("isCluster"))
    return {"nodes": node_count, "edges": len(graph["edges"]),
            "bytes": len(page.encode("utf-8"))}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="graph", description=__doc__)
    ap.add_argument("--root", default="docs")
    ap.add_argument("--out", default="docs/views/graph/index.html")
    ap.add_argument("--name", default=None)
    args = ap.parse_args(argv)
    root = Path(args.root)
    if not root.is_dir():
        print(f"graph: root {root} is not a directory", file=sys.stderr)
        return 2
    counts = generate(root, Path(args.out), args.name)
    print(f"graph: {counts['nodes']} nodes, {counts['edges']} edges, "
          f"{counts['bytes']} bytes -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
