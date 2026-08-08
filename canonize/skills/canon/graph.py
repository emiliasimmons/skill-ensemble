#!/usr/bin/env python3
"""Wiki view builder for a canon project.

Writes `index.html` at the substrate root and `views/wiki/canon.js` beside it.
The viewer itself — `view/view.js`, `view/view.css`, `view/vendor/` — is
ordinary source, edited in place and referenced rather than generated.

External trees that feed the graph are registered in the `Sources` block of
`schema.md`, the same list `canon check --links` validates against.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import canon  # noqa: E402
from collectors import COLLECTORS, Doc  # noqa: E402

_ASSETS = Path(__file__).resolve().parent / "view"
_SUPPORT = "views/wiki"

_MD_REF = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
_IMAGE_SUFFIXES = {".png", ".svg", ".jpg", ".jpeg", ".gif", ".webp"}

# a compiled roster is the page asserting membership; prose linking is not
_MEMBER_BLOCKS = ("members", "register", "taxonomy", "zones", "sources")
_BLOCK_RE = re.compile(r"<!--\s*(/?)compiled:([a-z-]+)\s*-->")

# one edge per pair, so a target named in both a roster and prose keeps the
# stronger claim
_KIND_RANK = {"supersedes": 4, "derived_from": 3, "bears_on": 2, "member": 1, "link": 0}


def sources(canon_root: Path) -> list[dict]:
    """The bundle itself, then every external tree registered in schema.md."""
    out = [{"name": canon_root.name, "collector": "canon",
            "root": str(canon_root), "prefix": ""}]
    for row in canon.load_schema(canon_root).sources:
        cfg = dict(row)
        cfg.setdefault("name", Path(cfg["root"]).name)
        cfg.setdefault("collector", "tree")
        cfg.setdefault("prefix", cfg["name"])
        include = cfg.get("include")
        if isinstance(include, str):
            cfg["include"] = dict(
                part.split("=", 1) for part in include.split(",") if "=" in part
            )
            cfg["include"] = {k.strip(): v.strip() for k, v in cfg["include"].items()}
        out.append(cfg)
    return out


def _media_name(abspath: Path) -> str:
    digest = hashlib.sha1(str(abspath).encode()).hexdigest()[:8]
    return f"{_SUPPORT}/media/{digest}_{abspath.name}"


def _member_spans(body: str) -> list[tuple[int, int]]:
    spans, open_at = [], None
    for m in _BLOCK_RE.finditer(body):
        closing, name = m.group(1), m.group(2)
        if name not in _MEMBER_BLOCKS:
            continue
        if closing:
            if open_at is not None:
                spans.append((open_at, m.start()))
                open_at = None
        elif open_at is None:
            open_at = m.end()
    if open_at is not None:
        spans.append((open_at, len(body)))
    return spans


def rewrite(doc: Doc, by_path: dict[Path, str], page_dir: Path,
            media: dict[Path, str], bundle: bool) -> tuple[str, dict[str, str]]:
    """Resolve a body's links to node ids and its images to page-relative paths."""
    edges: dict[str, str] = {}
    spans = _member_spans(doc.body)

    def one(match: re.Match) -> str:
        bang, text, target = match.groups()
        if "://" in target or target.startswith("#"):
            return match.group(0)
        abspath = (doc.abspath.parent / target.split("#")[0]).resolve()

        if bang or abspath.suffix.lower() in _IMAGE_SUFFIXES:
            if not abspath.exists():
                return f"*{text} (image missing)*"
            if abspath not in media:
                media[abspath] = (_media_name(abspath) if bundle
                                  else os.path.relpath(abspath, page_dir))
            return f"![{text}]({media[abspath]})"

        node_id = by_path.get(abspath)
        if node_id:
            at = match.start()
            kind = "member" if any(a <= at < b for a, b in spans) else "link"
            if _KIND_RANK[kind] >= _KIND_RANK.get(edges.get(node_id, "link"), 0):
                edges[node_id] = kind
            return f'<a data-node="{html.escape(node_id, quote=True)}">{text}</a>'
        cls, tip = ("untracked", "not a graph node") if abspath.exists() else ("missing", "missing")
        return f'<a class="{cls}" title="{html.escape(tip + ": " + target, quote=True)}">{text}</a>'

    return _MD_REF.sub(one, doc.body), edges


def build_canon(cfg: list[dict], page_dir: Path, name: str,
                 bundle: bool) -> tuple[dict, dict]:
    docs: list[Doc] = []
    for source in cfg:
        collector = COLLECTORS.get(source["collector"])
        if collector is None:
            print(f"graph: unknown collector {source['collector']!r}", file=sys.stderr)
            continue
        docs.extend(collector(source))

    by_path = {d.abspath: d.id for d in docs}
    media: dict[Path, str] = {}

    nodes, bodies = [], {}
    edges: list[dict] = []
    seen: set[tuple[str, str]] = set()

    for doc in docs:
        body, targets = rewrite(doc, by_path, page_dir, media, bundle)
        bodies[doc.id] = body
        for target, kind in doc.relations.items():
            abspath = (doc.abspath.parent / target.split("#")[0]).resolve()
            node_id = by_path.get(abspath)
            if node_id and _KIND_RANK[kind] >= _KIND_RANK.get(targets.get(node_id, "link"), 0):
                targets[node_id] = kind
        for target in sorted(targets):
            if target == doc.id or (doc.id, target) in seen:
                continue
            seen.add((doc.id, target))
            edges.append({"data": {"id": f"{doc.id}__{target}", "source": doc.id,
                                   "target": target, "kind": targets[target]}})

        nodes.append({"data": {
            "id": doc.id, "label": doc.title, "type": doc.type,
            "source": doc.source, "description": doc.description,
            "resource": doc.resource, "tags": doc.tags, "group": doc.group}})

    canon = {"name": name, "nodes": nodes, "edges": edges, "bodies": bodies,
              "types": sorted({d.type for d in docs}),
              "sources": [s["name"] for s in cfg]}
    return canon, media


def write_view(canon: dict, media: dict[Path, str], page_dir: Path,
               name: str, bundle: bool) -> None:
    support = page_dir / _SUPPORT
    support.mkdir(parents=True, exist_ok=True)
    (support / "canon.js").write_text(
        "window.CANON = " + json.dumps(canon) + ";\n", encoding="utf-8")

    if bundle:
        assets = support / "assets"
        if assets.exists():
            shutil.rmtree(assets)
        shutil.copytree(_ASSETS, assets, ignore=shutil.ignore_patterns("index.html"))
        for abspath, rel in media.items():
            dest = page_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(abspath, dest)
        prefix = f"{_SUPPORT}/assets/"
    else:
        prefix = os.path.relpath(_ASSETS, page_dir) + "/"

    custom = (f'<link rel="stylesheet" href="{_SUPPORT}/custom.css">'
              if (support / "custom.css").exists() else "")
    page = ((_ASSETS / "index.html").read_text(encoding="utf-8")
            .replace("__NAME__", html.escape(name))
            .replace("__ASSETS__", prefix)
            .replace("__SUPPORT__", _SUPPORT + "/")
            .replace("__CUSTOM__", custom))
    (page_dir / "index.html").write_text(page, encoding="utf-8")


def generate(canon_root: Path, name: str | None = None, bundle: bool = False) -> dict:
    name = name or canon_root.resolve().parent.name
    cfg = sources(canon_root)
    canon, media = build_canon(cfg, canon_root, name, bundle)
    write_view(canon, media, canon_root, name, bundle)
    return {"nodes": len(canon["nodes"]), "edges": len(canon["edges"]),
            "images": len(media), "sources": len(cfg),
            "bytes": (canon_root / _SUPPORT / "canon.js").stat().st_size}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="graph", description=__doc__)
    ap.add_argument("--root", default="docs", help="substrate root")
    ap.add_argument("--name", default=None)
    ap.add_argument("--bundle", action="store_true",
                    help="copy viewer assets and referenced images in, for a portable folder")
    args = ap.parse_args(argv)
    root = Path(args.root)
    if not root.is_dir():
        print(f"graph: root {root} is not a directory", file=sys.stderr)
        return 2
    counts = generate(root, args.name, args.bundle)
    print(f"graph: {counts['nodes']} nodes, {counts['edges']} edges, "
          f"{counts['images']} images, {counts['sources']} sources, "
          f"{counts['bytes']} bytes -> {root}/index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
