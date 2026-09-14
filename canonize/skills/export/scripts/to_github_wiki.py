#!/usr/bin/env python3
"""to_github_wiki: flatten a canon into a GitHub Wiki snapshot.

GitHub Wiki has one flat page namespace, so `pages/x.md` becomes `x.md`,
inter-page links are rewritten to the flat slugs, frontmatter is stripped, and
tag pages plus a `_Sidebar.md` are generated. The output is disposable: it is
rebuilt from the canon and pushed by hand to the repo's wiki remote.

Scope and remote come from `wiki.json` in the output directory, so a wiki that
carries part of the canon carries the same part on every run.

    python3 to_github_wiki.py --root docs --out docs/export/github-wiki

Stdlib only. Reuses canon.py's frontmatter parser and page model.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

_CANON = Path(__file__).resolve().parents[2] / "canon" / "canon.py"
_spec = importlib.util.spec_from_file_location("canon", _CANON)
canon = importlib.util.module_from_spec(_spec)
sys.modules["canon"] = canon  # @dataclass resolves its own module while executing
_spec.loader.exec_module(canon)

DEFAULT_ZONES = ["pages", "findings"]
DEFAULT_EXCLUDE = ["ledger.md"]
# tags/ is regenerated here from the included pages, raw/ holds binaries
NEVER = {"raw", "tags"}


def load_scope(out_dir: Path) -> dict:
    path = out_dir / "wiki.json"
    if not path.exists():
        return {"zones": DEFAULT_ZONES, "tags": [], "exclude": DEFAULT_EXCLUDE,
                "remote": ""}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "zones": data.get("zones") or DEFAULT_ZONES,
        "tags": data.get("tags") or [],
        "exclude": data.get("exclude", DEFAULT_EXCLUDE),
        "remote": data.get("remote", ""),
    }


def collect(root: Path, out_dir: Path, scope: dict) -> list:
    """Pages the wiki carries: the index, the glossary, and every page in an
    included zone that also matches the tag filter."""
    out_res = out_dir.resolve()
    keep_tags = set(scope["tags"])
    exclude = set(scope["exclude"])
    pages = []
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        zone = rel.split("/")[0] if "/" in rel else ""
        if zone in NEVER or rel in exclude:
            continue
        resolved = path.resolve()
        if resolved == out_res or out_res in resolved.parents:
            continue
        if zone and zone not in scope["zones"]:
            continue
        fm, body, had = canon.parse_frontmatter(path.read_text(encoding="utf-8"))
        page = canon.Page(rel, path, fm, body, had)
        if zone and keep_tags and not keep_tags.intersection(page.tags):
            continue
        pages.append(page)
    return pages


class NameAllocator:
    """Unique flat filenames, case-insensitively, `.N` on collision."""

    def __init__(self) -> None:
        self._used: dict[str, str] = {}

    def take(self, name: str) -> str:
        stem = name[:-3] if name.endswith(".md") else name
        candidate = f"{stem}.md"
        n = 0
        while candidate.lower() in self._used:
            n += 1
            candidate = f"{stem}.{n}.md"
        self._used[candidate.lower()] = candidate
        return candidate


def flat_name(relpath: str) -> str:
    if relpath == "index.md":
        return "Home.md"
    return relpath.split("/")[-1]


def slug(flatname: str) -> str:
    return flatname[:-3] if flatname.endswith(".md") else flatname


_LINK_RE = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)\)")


def rewrite_links(body: str, relpath: str, link_map: dict[str, str],
                  resources: dict[str, str]) -> str:
    """Point inter-page links at flat slugs. A link to a page the wiki left out
    degrades to its title plus the source identifier, so the reader can still
    reach what it cited."""

    def repl(m: re.Match) -> str:
        bang, text, target = m.group(1), m.group(2), m.group(3)
        if bang or target.startswith("#") or "://" in target or target.startswith("mailto:"):
            return m.group(0)
        base, _, frag = target.partition("#")
        frag = f"#{frag}" if frag else ""
        if not base.endswith(".md"):
            return text
        resolved = canon.resolve_link(base, relpath)
        dest = link_map.get(resolved)
        if dest:
            return f"[{text}]({dest}{frag})"
        resource = resources.get(resolved)
        return f"{text} ({resource})" if resource else text

    return _LINK_RE.sub(repl, body)


def _starts_with_h1(body: str) -> bool:
    for line in body.splitlines():
        if line.strip():
            return line.lstrip().startswith("# ")
    return False


def transform_body(page, link_map: dict[str, str], resources: dict[str, str]) -> str:
    body = page.body
    head = ""
    if page.title and not _starts_with_h1(body):
        head = f"# {page.title}\n\n"
        if page.description:
            head += f"_{page.description}_\n\n"
    byline = []
    for key in ("author", "published", "resource"):
        value = page.fm.get(key)
        if value:
            byline.append(str(value))
    if byline:
        head += " · ".join(byline) + "\n\n"
    return (head + rewrite_links(body, page.relpath, link_map, resources)).rstrip() + "\n"


_TAG_SANITIZE_RE = re.compile(r"[^A-Za-z0-9._-]+")


def build_tag_pages(pages, vocab: dict[str, str], link_map: dict[str, str],
                    alloc: NameAllocator):
    by_tag: dict[str, list] = {}
    for p in pages:
        for tag in p.tags:
            by_tag.setdefault(tag, []).append(p)

    contents: dict[str, str] = {}
    slugs: dict[str, str] = {}
    for tag in sorted(by_tag):
        flat = alloc.take(f"tag-{_TAG_SANITIZE_RE.sub('-', tag)}.md")
        slugs[tag] = slug(flat)
        lines = [f"# Tag: {tag}", ""]
        if vocab.get(tag):
            lines += [f"_{vocab[tag]}_", ""]
        for member in sorted(by_tag[tag], key=lambda p: p.title.lower()):
            dest = link_map.get(member.relpath)
            if dest:
                line = f"- [{member.title}]({dest})"
                if member.description:
                    line += f" -- {member.description}"
                lines.append(line)
        contents[flat] = "\n".join(lines).rstrip() + "\n"
    return contents, slugs


def build_sidebar(pages, link_map: dict[str, str], tag_slugs: dict[str, str]) -> str:
    lines = ["## Navigation", "", "- [Home](Home)"]
    if "glossary.md" in link_map:
        lines.append(f"- [Glossary]({link_map['glossary.md']})")
    lines.append("")
    if tag_slugs:
        lines += ["### Tags", ""]
        lines += [f"- [{tag}]({dest})" for tag, dest in sorted(tag_slugs.items())]
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default="docs", help="canon root (default: docs)")
    ap.add_argument("--out", default="docs/export/github-wiki",
                    help="output directory (default: docs/export/github-wiki)")
    args = ap.parse_args(argv)

    root, out_dir = Path(args.root), Path(args.out)
    if not root.is_dir():
        print(f"no such root: {root}", file=sys.stderr)
        return 1

    scope = load_scope(out_dir)
    pages = collect(root, out_dir, scope)
    if not pages:
        print("nothing in scope", file=sys.stderr)
        return 1

    alloc = NameAllocator()
    link_map, contents = {}, {}
    for page in sorted(pages, key=lambda p: p.relpath):
        flat = alloc.take(flat_name(page.relpath))
        link_map[page.relpath] = slug(flat)
        contents[flat] = page

    # every page in the canon, so a link out of scope can still name its source
    resources = {}
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        if rel in link_map:
            continue
        fm, _, _ = canon.parse_frontmatter(path.read_text(encoding="utf-8"))
        if fm.get("resource"):
            resources[rel] = str(fm["resource"])

    tagged = [p for p in pages if p.tags]
    tag_contents, tag_slugs = build_tag_pages(
        tagged, canon.load_tag_vocab(root), link_map, alloc)

    out_dir.mkdir(parents=True, exist_ok=True)
    for existing in out_dir.glob("*.md"):
        existing.unlink()

    written = 0
    for flat, page in contents.items():
        (out_dir / flat).write_text(
            transform_body(page, link_map, resources), encoding="utf-8")
        written += 1
    for flat, text in tag_contents.items():
        (out_dir / flat).write_text(text, encoding="utf-8")
        written += 1
    (out_dir / "_Sidebar.md").write_text(
        build_sidebar(pages, link_map, tag_slugs), encoding="utf-8")
    written += 1

    print(f"wiki: {written} pages in {out_dir}")
    remote = scope["remote"]
    if remote:
        print(f"push with:\n  git -C {out_dir} init -q && git -C {out_dir} add -A")
        print(f"  git -C {out_dir} commit -qm 'wiki snapshot'")
        print(f"  git -C {out_dir} push -f {remote} HEAD:master")
    else:
        print("no `remote` in wiki.json; add one to get the push commands")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
