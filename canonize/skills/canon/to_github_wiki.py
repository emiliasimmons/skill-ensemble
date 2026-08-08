#!/usr/bin/env python3
"""to_github_wiki — flatten the wiki into a GitHub Wiki snapshot.

A one-way publish. GitHub Wiki has a single flat page namespace, so the nested
wiki (`topics/<name>/<page>.md`) is flattened by path (`A/B.md -> A-B.md`),
inter-page links are rewritten to the flat slugs, frontmatter is stripped,
and tag pages plus a `_Sidebar.md` are generated. The output is a disposable
snapshot pushed to the repo's `<repo>.wiki.git` remote by hand.

Convention: run `canon compile` first so the compiled surfaces (taxonomy, state,
registers, per-zone indexes) are current before the snapshot is taken.

Stdlib only. Reuses canon.py's frontmatter parser and collection model.

    python3 to_github_wiki.py --root docs --out docs/views/github-wiki

TODO(images): findings may reference images; copy the binary assets and rewrite
  image links. For now image links are left untouched and may 404.
TODO(assets): non-markdown links (e.g. ../sources/paper.pdf) are
  unwrapped to plain text; rewrite them to source-repo blob URLs instead.
TODO(frontmatter): optionally emit GitHub-Docs-style YAML frontmatter
  (title/intro/children) rather than stripping — see
  https://docs.github.com/en/contributing/writing-for-github-docs/using-yaml-frontmatter
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from canon import Page, load_schema, parse_frontmatter, resolve_link

# whole zones that never become wiki pages: raw storage and compiled HTML
EXCLUDED_TOP = {"sources", "views"}


# --- file collection --------------------------------------------------------

def collect_files(root: Path, out_dir: Path):
    """Relpaths (posix) of every markdown page that becomes a wiki page.

    Includes reserved index.md files (they are the compiled listings the
    sidebar links to); excludes schema.md, the raw/views zones, and the output
    directory itself so a re-run never re-flattens its own output.
    """
    out_res = out_dir.resolve()
    for p in sorted(root.rglob("*.md")):
        if p.name == "schema.md":
            continue
        rel = p.relative_to(root)
        if rel.parts and rel.parts[0] in EXCLUDED_TOP:
            continue
        resolved = p.resolve()
        if resolved == out_res or out_res in resolved.parents:
            continue
        yield rel.as_posix()


def load_included(root: Path, out_dir: Path) -> list[Page]:
    pages = []
    for rel in collect_files(root, out_dir):
        abspath = root / rel
        fm, body, had = parse_frontmatter(abspath.read_text(encoding="utf-8"))
        pages.append(Page(rel, abspath, fm, body, had))
    return pages


# --- flat naming ------------------------------------------------------------

class NameAllocator:
    """Hands out unique flat filenames, case-insensitively, `.N` on collision."""

    def __init__(self) -> None:
        self._used: dict[str, str] = {}  # lower(name) -> name

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
    return relpath.replace("/", "-")


def slug(flatname: str) -> str:
    return flatname[:-3] if flatname.endswith(".md") else flatname


# --- link rewriting ---------------------------------------------------------

_LINK_RE = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)\)")


def rewrite_links(body: str, relpath: str, link_map: dict[str, str]) -> str:
    """Rewrite inter-page .md links to flat slugs; unwrap the unresolvable.

    link_map keys are root-relative source paths ("topics/x.md"); values
    are destination slugs ("topics-x", no extension). `relpath` is the page
    carrying the link, which its file-relative targets resolve against.
    """

    def repl(m: re.Match) -> str:
        bang, text, target = m.group(1), m.group(2), m.group(3)
        if bang:  # image — TODO(images); leave untouched
            return m.group(0)
        if target.startswith("#") or "://" in target or target.startswith("mailto:"):
            return m.group(0)
        base, _, frag = target.partition("#")
        frag = f"#{frag}" if frag else ""
        resolved = resolve_link(base, relpath)
        if base.endswith(".md"):
            dest = link_map.get(resolved)
            return f"[{text}]({dest}{frag})" if dest else text
        return text  # non-md asset in an excluded zone — TODO(assets)

    return _LINK_RE.sub(repl, body)


# --- page body transform ----------------------------------------------------

def _starts_with_h1(body: str) -> bool:
    for line in body.splitlines():
        if line.strip():
            return line.lstrip().startswith("# ")
    return False


def transform_body(page: Page, link_map: dict[str, str]) -> str:
    """Strip frontmatter, synthesize a heading if needed, rewrite links."""
    body = page.body
    title = page.fm.get("title")
    desc = page.fm.get("description")
    if title and not _starts_with_h1(body):
        head = f"# {title}\n\n"
        if desc:
            head += f"_{desc}_\n\n"
        body = head + body
    return rewrite_links(body, page.relpath, link_map).rstrip() + "\n"


# --- tag pages --------------------------------------------------------------

_TAG_SANITIZE_RE = re.compile(r"[^A-Za-z0-9._-]+")


def build_tag_pages(pages, schema, link_map, alloc):
    """Return (tag -> flatname content, tag -> slug) for a page per tag."""
    by_tag: dict[str, list[Page]] = {}
    for p in pages:
        for tag in p.tags:
            by_tag.setdefault(tag, []).append(p)

    contents: dict[str, str] = {}
    slugs: dict[str, str] = {}
    for tag in sorted(by_tag):
        safe = _TAG_SANITIZE_RE.sub("-", tag)
        flat = alloc.take(f"tag-{safe}.md")
        slugs[tag] = slug(flat)
        gloss = schema.tags.get(tag, "")
        lines = [f"# Tag: {tag}", ""]
        if gloss:
            lines += [f"_{gloss}_", ""]
        lines.append(f"Pages tagged `{tag}`:")
        lines.append("")
        for member in sorted(by_tag[tag], key=lambda p: p.title.lower()):
            dest = link_map.get(member.relpath)
            if dest:
                lines.append(f"- [{member.title}]({dest})")
        contents[flat] = "\n".join(lines).rstrip() + "\n"
    return contents, slugs


# --- sidebar ----------------------------------------------------------------

def build_sidebar(pages, link_map, tag_slugs) -> str:
    lines = ["## Navigation", "", "- [Home](Home)", ""]

    hubs = sorted(
        (p for p in pages if p.type == "topic"), key=lambda p: p.title.lower()
    )
    if hubs:
        lines += ["### Topics", ""]
        for h in hubs:
            dest = link_map.get(h.relpath)
            if dest:
                lines.append(f"- [{h.title}]({dest})")
        lines.append("")

    registers = [
        ("Assumptions", "assumptions.md"),
        ("Open decisions", "open-decisions.md"),
        ("Glossary", "glossary.md"),
    ]
    reg = [f"- [{label}]({link_map[key]})" for label, key in registers if key in link_map]
    if reg:
        lines += ["### Registers", ""] + reg + [""]

    evidence = [
        ("Findings", "findings/index.md"),
        ("Decisions", "decisions/index.md"),
    ]
    ev = [f"- [{label}]({link_map[key]})" for label, key in evidence if key in link_map]
    if ev:
        lines += ["### Evidence", ""] + ev + [""]

    if tag_slugs:
        lines += ["### Tags", ""]
        for tag in sorted(tag_slugs):
            lines.append(f"- [{tag}]({tag_slugs[tag]})")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


# --- orchestration ----------------------------------------------------------

def build(root: Path, out_dir: Path) -> int:
    pages = load_included(root, out_dir)
    schema = load_schema(root)

    alloc = NameAllocator()
    flatnames: dict[str, str] = {}   # relpath -> flatname
    link_map: dict[str, str] = {}    # relpath -> dest slug
    for page in pages:
        flat = alloc.take(flat_name(page.relpath))
        flatnames[page.relpath] = flat
        link_map[page.relpath] = slug(flat)

    tag_contents, tag_slugs = build_tag_pages(pages, schema, link_map, alloc)

    out_dir.mkdir(parents=True, exist_ok=True)
    for existing in out_dir.glob("*.md"):  # clean snapshot; leaves .git untouched
        existing.unlink()

    for page in pages:
        content = transform_body(page, link_map)
        (out_dir / flatnames[page.relpath]).write_text(content, encoding="utf-8")

    for flat, content in tag_contents.items():
        (out_dir / flat).write_text(content, encoding="utf-8")

    (out_dir / "_Sidebar.md").write_text(
        build_sidebar(pages, link_map, tag_slugs), encoding="utf-8"
    )

    print(
        f"github-wiki: {len(pages)} pages, {len(tag_contents)} tag pages, "
        f"1 sidebar -> {out_dir}"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="to_github_wiki", description=__doc__)
    parser.add_argument("--root", default="docs", help="substrate root (default: docs)")
    parser.add_argument(
        "--out",
        default=None,
        help="output directory (default: docs/views/github-wiki)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root)
    if not root.is_dir():
        print(f"to_github_wiki: root {root} is not a directory", file=sys.stderr)
        return 2
    out_dir = Path(args.out) if args.out else root / "views" / "github-wiki"
    return build(root, out_dir)


if __name__ == "__main__":
    sys.exit(main())
