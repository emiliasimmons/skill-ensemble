"""Document collectors for a graph view.

A collector enumerates `Doc` records from one configured source. Links are
resolved centrally afterwards against the union of every source, so a
collector never has to know what else feeds the same graph — that is what
makes a docs page and an experiment README able to point at each other.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import canon  # noqa: E402

RELATION_KEYS = ("derived_from", "bears_on", "supersedes")
_H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


@dataclass
class Doc:
    id: str
    abspath: Path
    title: str
    type: str
    source: str
    body: str
    description: str = ""
    resource: str = ""
    tags: list[str] = field(default_factory=list)
    group: str = ""
    relations: dict[str, str] = field(default_factory=dict)


def _prefixed(prefix: str, stem: str) -> str:
    return f"{prefix}:{stem}" if prefix else stem


def _canon_group(page: canon.Page) -> str:
    """Files-pane heading only; graph membership comes from edges, not this."""
    parts = page.relpath.split("/")
    if page.relpath.startswith("topics/"):
        return "topics" if len(parts) == 2 else parts[1]
    return parts[0] if len(parts) > 1 else ""


def collect_canon(cfg: dict) -> list[Doc]:
    root = Path(cfg["root"])
    prefix = cfg.get("prefix", "")
    pages = canon.load_pages(root)
    # the corpus front door is not a knowledge page, but it is the thing a
    # reader opens first
    pages += [p for p in canon.load_pages(root, include_index=True)
              if p.relpath == "index.md"]

    docs = []
    for p in pages:
        stem = p.relpath[:-3] if p.relpath.endswith(".md") else p.relpath
        relations: dict[str, str] = {}
        for key in RELATION_KEYS:
            val = p.fm.get(key)
            if not val:
                continue
            for item in (val if isinstance(val, list) else [val]):
                if str(item).endswith(".md"):
                    relations[str(item)] = key
        heading = _H1_RE.search(p.body)
        is_index = p.relpath == "index.md"
        docs.append(Doc(
            id=_prefixed(prefix, stem),
            abspath=p.abspath.resolve(),
            title=(heading.group(1) if is_index and heading else p.title),
            type="index" if is_index else (p.type or "untyped"),
            source=cfg["name"],
            body=p.body,
            description=p.description,
            resource=str(p.fm.get("resource") or ""),
            tags=p.tags,
            group=_canon_group(p),
            relations=relations,
        ))
    return docs


def collect_tree(cfg: dict) -> list[Doc]:
    """Markdown files in a plain directory tree, keyed by filename.

    `include` maps a filename to the node type it becomes, so an experiment's
    README and SUMMARY land as two typed nodes under their folder.
    """
    root = Path(cfg["root"])
    prefix = cfg.get("prefix", "")
    include = cfg.get("include") or {"README.md": "note"}
    if not root.is_dir():
        print(f"graph: source {cfg['name']}: {root} is not a directory", file=sys.stderr)
        return []

    docs = []
    for path in sorted(root.rglob("*.md")):
        type_name = include.get(path.name)
        if type_name is None:
            continue
        rel = path.relative_to(root)
        body = path.read_text(encoding="utf-8", errors="replace")
        heading = _H1_RE.search(body)
        folder = rel.parent.as_posix()
        docs.append(Doc(
            id=_prefixed(prefix, rel.with_suffix("").as_posix()),
            abspath=path.resolve(),
            title=heading.group(1) if heading else f"{folder}/{path.stem}",
            type=type_name,
            source=cfg["name"],
            body=body,
            description=folder,
            group=rel.parent.name if folder != "." else "",
        ))
    return docs


COLLECTORS = {"canon": collect_canon, "tree": collect_tree}
