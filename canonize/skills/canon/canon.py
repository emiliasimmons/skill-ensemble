#!/usr/bin/env python3
"""canon: the deterministic layer beneath the canonize skills.

Stdlib only. Compiles what frontmatter already says, checks conformance, and
stamps time. Judgment (placement, synthesis, grilling) stays in skill prose.

Subcommands:
  compile   regenerate compiled surfaces from frontmatter
  check     frontmatter conformance + link integrity
  stamp     set a page's updated field to now (run by the PostToolUse hook)

Invoked by skills, never required by a project. A project is pure data.
"""

from __future__ import annotations

import argparse
import difflib
import json
import posixpath
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path

# --- frontmatter ------------------------------------------------------------
#
# A deliberately small YAML subset, enough for the frontmatter contract:
# scalars, inline lists ([a, b]), and block lists (- item). Anything richer is
# out of scope by design; the contract stays flat so a context-free reader can
# parse it too.

_DELIM = "---"
_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):(.*)$")


def _strip_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] in "\"'" and value[-1] == value[0]:
        return value[1:-1]
    return value


def _parse_inline_list(value: str) -> list[str]:
    inner = value.strip()[1:-1].strip()
    if not inner:
        return []
    return [_strip_scalar(item) for item in inner.split(",") if item.strip()]


def parse_frontmatter(text: str) -> tuple[dict, str, bool]:
    """Return (frontmatter, body, had_frontmatter)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != _DELIM:
        return {}, text, False
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == _DELIM:
            end = i
            break
    if end is None:
        return {}, text, False

    fm: dict = {}
    current_list_key: str | None = None
    for raw in lines[1:end]:
        line = raw.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue
        stripped = line.lstrip()
        if stripped.startswith("- ") and current_list_key is not None:
            fm[current_list_key].append(_strip_scalar(stripped[2:]))
            continue
        m = _KEY_RE.match(line.strip())
        if not m:
            continue
        key, rest = m.group(1), m.group(2).strip()
        if rest == "":
            fm[key] = []
            current_list_key = key
        elif rest.startswith("[") and rest.endswith("]"):
            fm[key] = _parse_inline_list(rest)
            current_list_key = None
        else:
            fm[key] = _strip_scalar(rest)
            current_list_key = None

    body = "\n".join(lines[end + 1:])
    if body.startswith("\n"):
        body = body[1:]
    return fm, body, True


def set_frontmatter_field(text: str, key: str, value: str) -> str | None:
    """Set `key: value` in a page's frontmatter, replacing an existing line or
    inserting one before the closing delimiter. Returns None when there is no
    frontmatter block. Line-level, so it preserves order, comments, and spacing
    the block parser would drop."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != _DELIM:
        return None
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == _DELIM), None)
    if end is None:
        return None
    key_re = re.compile(rf"^{re.escape(key)}:\s")
    line = f"{key}: {value}\n"
    for i in range(1, end):
        if key_re.match(lines[i]):
            lines[i] = line
            return "".join(lines)
    lines.insert(end, line)
    return "".join(lines)


# --- collection model -------------------------------------------------------

# root-level files that carry links but are not knowledge pages: the compiled
# index and plain prose (README.md, glossary.md)
NONPAGE = {"index.md", "README.md", "glossary.md"}
# excluded whole: raw files, generated tag pages, generated view scaffolding
RAW_DIRS = {"raw", "tags", "views"}


@dataclass
class Page:
    relpath: str          # posix, relative to root
    abspath: Path
    fm: dict
    body: str
    had_fm: bool

    @property
    def type(self) -> str:
        return str(self.fm.get("type") or "")

    @property
    def title(self) -> str:
        return str(self.fm.get("title") or self.relpath)

    @property
    def description(self) -> str:
        return str(self.fm.get("description") or "")

    @property
    def tags(self) -> list[str]:
        t = self.fm.get("tags") or []
        return [str(x) for x in t] if isinstance(t, list) else [str(t)]

    @property
    def updated(self) -> str:
        return str(self.fm.get("updated") or "")

    @property
    def zone(self) -> str:
        return self.relpath.split("/", 1)[0] if "/" in self.relpath else ""

    @property
    def display_type(self) -> str:
        """The type used for grouping. A findings page with no `type` groups
        under its location."""
        if self.type:
            return self.type
        if self.zone == "findings":
            return "finding"
        return ""

    @property
    def dirname(self) -> str:
        return posixpath.dirname(self.relpath)

    def link_from(self, from_dir: str) -> str:
        return posixpath.relpath(self.relpath, from_dir or ".")


@dataclass
class Settings:
    settings: dict = field(default_factory=dict)
    registry: dict = field(default_factory=dict)   # type -> {zone, format}
    sources: list = field(default_factory=list)     # external trees: {name, root, ...}


def _iter_md(root: Path, include_nonpage: bool = False):
    for p in sorted(root.rglob("*.md")):
        if p.name in NONPAGE and not include_nonpage:
            continue
        rel = p.relative_to(root)
        if rel.parts and rel.parts[0] in RAW_DIRS:
            continue
        yield p


def load_pages(root: Path, include_nonpage: bool = False) -> list[Page]:
    """Knowledge pages under pages/ and findings/. `include_nonpage` adds the
    compiled and plain root files, which are not knowledge pages but do carry
    links worth resolving."""
    pages = []
    for p in _iter_md(root, include_nonpage):
        fm, body, had = parse_frontmatter(p.read_text(encoding="utf-8"))
        pages.append(Page(p.relative_to(root).as_posix(), p, fm, body, had))
    return pages


# --- config -----------------------------------------------------------------
#
# Three built-in page types cover the default project. A project adds more
# through settings.json; nothing else advertises it.

BUILTIN_TYPES = {
    "entry": {"zone": "pages", "format": "canon/formats/entry.md"},
    "synthesis": {"zone": "pages", "format": "canon/formats/synthesis.md"},
    "decision": {"zone": "pages", "format": "canon/formats/decision.md"},
}


def load_settings(root: Path) -> Settings:
    """Read settings.json at the substrate root. The registry is the built-ins
    plus any extra types the project registered. Tag glosses are not config;
    they come from the glossary and are filled by `load_tag_vocab`."""
    s = Settings(registry=dict(BUILTIN_TYPES))
    path = root / "settings.json"
    if not path.exists():
        return s
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return s
    s.settings = {k: data[k] for k in ("tag_aging_days", "wiki") if k in data}
    for row in data.get("types", []):
        t = row.get("type")
        if t:
            s.registry[t] = {"zone": row.get("zone", "pages"),
                             "format": row.get("format", "")}
    s.sources = [row for row in data.get("sources", []) if row.get("root")]
    return s


_GLOSS_TAG_RE = re.compile(r"^\s*[-*]\s+\*\*(?P<tag>[^*]+)\*\*\s*:\s*(?P<desc>.*)$")


def load_tag_vocab(root: Path) -> dict[str, str]:
    """tag -> description, read from the `## Tags` list in glossary.md, one
    `- **<tag>**: <description>` per line. Malformed lines declare nothing and
    surface in `check` as undeclared tags."""
    vocab: dict[str, str] = {}
    path = root / "glossary.md"
    if not path.is_file():
        return vocab
    inside = False
    for line in path.read_text(encoding="utf-8").split("\n"):
        if line.startswith("## "):
            inside = line[3:].strip().lower() == "tags"
            continue
        if inside:
            m = _GLOSS_TAG_RE.match(line)
            if m:
                vocab[m.group("tag").strip()] = m.group("desc").strip()
    return vocab


# --- clock ------------------------------------------------------------------
#
# recency and staleness read one field, `updated`, maintained by the PostToolUse
# hook. Never git, never hand-authored.

def _stamp_epoch(stamp: str) -> int | None:
    s = (stamp or "").strip()
    if not s:
        return None
    for candidate in (s, s[:10]):
        try:
            return int(datetime.fromisoformat(candidate).timestamp())
        except ValueError:
            continue
    return None


def page_time(page: Page) -> int | None:
    return _stamp_epoch(page.updated)


def _body_link_targets(page: Page) -> set[str]:
    """Root-relative relpaths this page links in its body (its dependency set)."""
    targets: set[str] = set()
    for m in _MD_LINK_RE.finditer(page.body):
        t = m.group(1).split("#")[0]
        if not t or "://" in t or not t.endswith(".md"):
            continue
        targets.add(t.lstrip("/") if t.startswith("/") else resolve_link(t, page.relpath))
    return targets


def stale_pages(pages: list[Page]) -> list[tuple[Page, int]]:
    """Syntheses and decisions with a body dependency updated more recently than
    the page itself."""
    by_relpath = {p.relpath: p for p in pages}
    out = []
    for p in pages:
        if p.display_type not in ("synthesis", "decision"):
            continue
        pt = page_time(p)
        if pt is None:
            continue
        newer = 0
        for target in _body_link_targets(p):
            dep = by_relpath.get(target)
            if not dep:
                continue
            dt = page_time(dep)
            if dt and dt > pt:
                newer += 1
        if newer:
            out.append((p, newer))
    return out


# --- compiled surfaces ------------------------------------------------------
#
# A compiled surface carries a blockquote note ("> Compiled from ...") that
# anchors the machine-owned region: from the note to the first authored h2 (a
# `## ` whose slug is not a block name here) or end of file. Compile owns the
# span between, rendering the non-empty blocks as `## ` sections in order and
# dropping the empty ones, so a block with nothing to list has no heading.
# Authored prose lives above the note or past the boundary.

_H2_RE = re.compile(r"^##\s+(.+?)\s*$")


def _slug(text: str) -> str:
    return text.strip().lower().replace(" ", "-")


def _heading(name: str) -> str:
    return name[:1].upper() + name[1:]


def _find_note(lines: list[str]) -> int | None:
    """Index of the region note: the last blockquote line whose next non-blank
    line is a heading or the end of the file. A blockquote inside authored prose
    (followed by more prose) does not qualify, so it is never mistaken for it."""
    note = None
    for i, line in enumerate(lines):
        if not line.startswith(">"):
            continue
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j >= len(lines) or lines[j].startswith("#"):
            note = i
    return note


def render_sections(ordered: list[tuple[str, str]]) -> str:
    """The non-empty blocks as `## ` sections in order; empties omitted."""
    out = []
    for name, body in ordered:
        if body.strip():
            out.append(f"## {_heading(name)}\n\n{body.rstrip()}")
    return "\n\n".join(out)


def replace_region(text: str, registry: set[str], ordered: list[tuple[str, str]]) -> str:
    """Rewrite the compiled region in place. Without the note there is no anchor,
    so the text is returned unchanged and `check` flags the surface."""
    lines = text.split("\n")
    note = _find_note(lines)
    if note is None:
        return text
    start = note + 1
    while start < len(lines) and not lines[start].strip():
        start += 1
    end = len(lines)
    for j in range(start, len(lines)):
        m = _H2_RE.match(lines[j])
        if m and _slug(m.group(1)) not in registry:
            end = j
            break
    rendered = render_sections(ordered)
    middle = ["", rendered, ""] if rendered else [""]
    rebuilt = "\n".join(lines[: note + 1] + middle + lines[end:])
    return re.sub(r"\n{3,}", "\n\n", rebuilt).rstrip() + "\n"


def _line(page: Page, from_dir: str) -> str:
    desc = f" -- {page.description}" if page.description else ""
    return f"- [{page.title}]({page.link_from(from_dir)}){desc}"


def _group_by_type(pages: list[Page]) -> dict[str, list[Page]]:
    groups: dict[str, list[Page]] = {}
    for p in pages:
        groups.setdefault(p.display_type, []).append(p)
    return groups


def _plural(word: str) -> str:
    if word.endswith("sis"):
        return word[:-3] + "ses"            # synthesis -> syntheses
    if word.endswith("y") and word[-2:-1] not in "aeiou":
        return word[:-1] + "ies"            # entry -> entries
    return word + ("es" if word.endswith(("s", "x", "z", "ch", "sh")) else "s")


def _tag_counts(pages: list[Page]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for p in pages:
        for tag in p.tags:
            counts[tag] = counts.get(tag, 0) + 1
    return counts


def _tagged(pages: list[Page]) -> list[Page]:
    """Pages that surface on tag pages: everything in pages/ and findings/."""
    return [p for p in pages if p.zone in ("pages", "findings")]


def compile_members_block(members: list[Page]) -> str:
    """The type-grouped member list that fills a tag page's `members` block."""
    groups = _group_by_type(members)
    if not groups:
        return ""
    out = []
    for type_name in sorted(groups):
        rows = sorted(groups[type_name], key=lambda p: p.relpath)
        label = _plural(type_name or "page").capitalize()
        out.append(f"### {label} ({len(rows)})")
        out += [_line(p, "tags") for p in rows]
        out.append("")
    return "\n".join(out).rstrip()


def render_tag_page(tag: str, description: str, members: list[Page]) -> str:
    """Tag pages are generated from the tag's glossary line and the pages that
    declare it. Every part is derived, so compile rewrites the file whole."""
    gloss = f" {description}" if description else ""
    return (f"---\ntag: {tag}\ndescription:{gloss}\n---\n\n"
            f"# {tag}\n\n"
            f"> Compiled from the glossary and the pages carrying this tag,"
            f" overwritten on the next compile.\n\n"
            f"## Members\n\n{compile_members_block(members)}\n")


def compile_tags_block(pages: list[Page], from_dir: str = "") -> str:
    counts = _tag_counts(_tagged(pages))
    if not counts:
        return ""
    out = []
    for tag in sorted(counts):
        link = posixpath.relpath(f"tags/{tag}.md", from_dir or ".")
        out.append(f"- [{tag}]({link}) · {counts[tag]} pages")
    return "\n".join(out)


def compile_type_block(pages: list[Page], type_name: str, from_dir: str = "") -> str:
    rows = sorted(
        (p for p in pages if p.zone == "pages" and p.display_type == type_name),
        key=lambda p: p.relpath,
    )
    if not rows:
        return ""
    return "\n".join(_line(p, from_dir) for p in rows)


def compile_findings_block(pages: list[Page], from_dir: str = "") -> str:
    findings = [p for p in pages if p.zone == "findings"]
    if not findings:
        return ""
    groups: dict[str, list[Page]] = {}
    for p in findings:
        parts = p.relpath.split("/")
        workspace = parts[1] if len(parts) > 2 else ""
        groups.setdefault(workspace, []).append(p)
    out = []
    for workspace in sorted(groups):
        if workspace:
            out.append(f"### {workspace}")
        out += [_line(p, from_dir) for p in sorted(groups[workspace], key=lambda p: p.relpath)]
        out.append("")
    return "\n".join(out).rstrip()


def compile_stale_block(pages: list[Page], from_dir: str = "") -> str:
    stale = stale_pages(pages)
    if not stale:
        return ""
    out = []
    for p, n in sorted(stale, key=lambda t: (-t[1], t[0].relpath)):
        noun = "dependency" if n == 1 else "dependencies"
        out.append(f"- [{p.title}]({p.link_from(from_dir)}) -- {n} newer {noun}")
    return "\n".join(out)


def compile_recent_block(pages: list[Page], from_dir: str = "", limit: int = 5) -> str:
    dated = [(page_time(p), p) for p in pages]
    dated = [(t, p) for t, p in dated if t]
    dated.sort(key=lambda x: x[0], reverse=True)
    if not dated:
        return ""
    out = []
    for t, p in dated[:limit]:
        stamp = datetime.fromtimestamp(t).date().isoformat()
        out.append(f"- {stamp} [{p.title}]({p.link_from(from_dir)})")
    return "\n".join(out)


# --- link + frontmatter checking --------------------------------------------

_MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
_MD_LINK_FULL = re.compile(r"(\[[^\]]*\])\(([^)\s]+)\)")


def resolve_link(target: str, from_relpath: str) -> str:
    """A link target as a path relative to the root, from the page carrying it."""
    if target.startswith("/"):
        return target.lstrip("/")
    return posixpath.normpath(posixpath.join(posixpath.dirname(from_relpath), target))


def _rewrite_links(body: str, from_relpath: str, to_dir: str) -> str:
    """Rewrite relative .md link targets so a body lifted out of `from_relpath`
    resolves from `to_dir`."""
    def repl(m: re.Match) -> str:
        label, target = m.group(1), m.group(2)
        base, _, frag = target.partition("#")
        if "://" in target or target.startswith("mailto:") or not base.endswith(".md"):
            return m.group(0)
        resolved = resolve_link(base, from_relpath)
        newt = posixpath.relpath(resolved, to_dir or ".")
        return f"{label}({newt}{'#' + frag if frag else ''})"
    return _MD_LINK_FULL.sub(repl, body)


def check_frontmatter(pages: list[Page], schema: Settings) -> list[str]:
    """Pages and findings share the identity floor (title, description, updated,
    tags), all errors. Only pages/ carry a registered `type`."""
    problems = []
    for p in pages:
        if p.zone not in ("pages", "findings"):
            continue
        if not p.had_fm:
            problems.append(f"ERROR {p.relpath}: no frontmatter block")
            continue
        if p.zone == "pages":
            if not p.type:
                problems.append(f"ERROR {p.relpath}: missing `type` (the hard floor)")
                continue
            if p.type not in schema.registry:
                problems.append(f"ERROR {p.relpath}: type `{p.type}` not registered")
        for key in ("title", "description"):
            if not p.fm.get(key):
                problems.append(f"ERROR {p.relpath}: missing `{key}`")
        if not p.updated:
            problems.append(f"ERROR {p.relpath}: missing `updated` (the hook should set it)")
        if not p.tags:
            problems.append(f"ERROR {p.relpath}: no tags (reachable from no tag page)")
    return problems


def check_links(root: Path, pages: list[Page]) -> list[str]:
    problems = []
    for p in pages:
        for m in _MD_LINK_RE.finditer(p.body):
            target = m.group(1).split("#")[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            if not target.endswith(".md"):
                continue
            if target.startswith("/"):
                problems.append(f"ANCHORED {p.relpath} -> {target} (use a file-relative link)")
            elif not (root / resolve_link(target, p.relpath)).exists():
                problems.append(f"BROKEN {p.relpath} -> {target}")
    return problems


def check_source_links(root: Path, schema: Settings) -> list[str]:
    """Links from registered external trees into the bundle. `check_links` walks
    pages under the root only, so a rename would break an outside citation silently."""
    problems = []
    inside = root.resolve()
    for source in schema.sources:
        name = source.get("name") or source["root"]
        src_root = Path(source["root"])
        if not src_root.is_dir():
            problems.append(f"WARN  source `{name}`: {src_root} is not a directory")
            continue
        for path in sorted(src_root.rglob("*.md")):
            text = path.read_text(encoding="utf-8", errors="replace")
            for m in _MD_LINK_RE.finditer(text):
                target = m.group(1).split("#")[0]
                if not target or "://" in target or not target.endswith(".md"):
                    continue
                dest = (path.parent / target).resolve()
                if inside not in dest.parents or dest.exists():
                    continue
                problems.append(
                    f"BROKEN {name}/{path.relative_to(src_root).as_posix()} -> {target}")
    return problems


def check_compiled(root: Path) -> list[str]:
    """The index alone mixes authored prose with a compiled region, so it alone
    needs the note that says where the region goes."""
    path = root / "index.md"
    if path.is_file() and _find_note(path.read_text(encoding="utf-8").split("\n")) is None:
        return ["WARN  index.md: no region note; compile cannot place the compiled block"]
    return []


def _aged_out(stamp: str, days: int) -> bool:
    """True when `stamp` is older than `days` ago. An unparseable stamp is young."""
    try:
        return date.fromisoformat(stamp[:10]) < date.today() - timedelta(days=days)
    except ValueError:
        return False


def check_tags(pages: list[Page], schema: Settings, root: Path) -> list[str]:
    """Tags carried by pages but not declared in the glossary, thin tags, and
    pairs that read as the same tag."""
    vocab = load_tag_vocab(root)
    try:
        days = int(schema.settings.get("tag_aging_days", 90))
    except (TypeError, ValueError):
        days = 90
    counts = _tag_counts(_tagged(pages))
    oldest: dict[str, str] = {}
    for p in _tagged(pages):
        for tag in p.tags:
            if p.updated and (tag not in oldest or p.updated < oldest[tag]):
                oldest[tag] = p.updated

    problems = []
    for tag in sorted(counts):
        if tag not in vocab:
            problems.append(
                f"ERROR tag `{tag}`: not declared in the glossary "
                f"(add `- **{tag}**: <description>` under `## Tags`)")
    for tag in sorted(vocab):
        n = counts.get(tag, 0)
        if n < 2 and _aged_out(oldest.get(tag, ""), days):
            problems.append(f"WARN  tag `{tag}`: {n} member(s) after {days} days (retire or grow it)")
        if not vocab[tag]:
            problems.append(f"WARN  tag `{tag}`: no description on its glossary line")
    for a, b in _near_duplicate_tags(sorted(vocab)):
        problems.append(f"WARN  tags `{a}` and `{b}` read as one tag (merge into a canonical form)")
    return problems


def _near_duplicate_tags(tags: list[str]) -> list[tuple[str, str]]:
    out = []
    for i, a in enumerate(tags):
        for b in tags[i + 1:]:
            if difflib.SequenceMatcher(None, a, b).ratio() >= 0.85:
                out.append((a, b))
    return out


# --- stamp ------------------------------------------------------------------

def stamp_file(path: Path) -> bool:
    """Set `updated` to now on a canon page. No-op unless the file has a
    frontmatter block and sits under a pages/ or findings/ directory, so the
    hook can fire it on every write without discriminating."""
    if path.suffix != ".md" or not path.is_file():
        return False
    if not ({"pages", "findings"} & set(path.parts)):
        return False
    text = path.read_text(encoding="utf-8")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    updated = set_frontmatter_field(text, "updated", now)
    if updated is None or updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


# --- command wiring ---------------------------------------------------------

def _write_if_changed(path: Path, content: str) -> bool:
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


_WIKI = Path(__file__).resolve().parent / "graph.py"


def cmd_compile(root: Path, blocks: set[str]) -> int:
    pages = load_pages(root)
    schema = load_settings(root)
    changed: list[str] = []
    want = lambda name: "all" in blocks or name in blocks

    def do_root_blocks():
        idx = root / "index.md"
        if not idx.exists():
            print(f"skip: {idx} does not exist (run setup-canon first)", file=sys.stderr)
            return
        ordered = [
            ("tags", compile_tags_block(pages)),
            ("syntheses", compile_type_block(pages, "synthesis")),
            ("decisions", compile_type_block(pages, "decision")),
            ("findings", compile_findings_block(pages)),
            ("stale", compile_stale_block(pages)),
            ("recent", compile_recent_block(pages)),
        ]
        registry = {name for name, _ in ordered}
        text = replace_region(idx.read_text(encoding="utf-8"), registry, ordered)
        if _write_if_changed(idx, text):
            changed.append("index.md")

    def do_tags():
        tags_dir = root / "tags"
        vocab = load_tag_vocab(root)
        all_tags = set(_tag_counts(_tagged(pages)))  # observed; orphans get pruned
        for tag in sorted(all_tags):
            members = [p for p in _tagged(pages) if tag in p.tags]
            path = tags_dir / f"{tag}.md"
            if _write_if_changed(path, render_tag_page(tag, vocab.get(tag, ""), members)):
                changed.append(f"tags/{tag}.md")
        if tags_dir.is_dir():
            for path in tags_dir.glob("*.md"):
                if path.stem not in all_tags:
                    path.unlink()
                    changed.append(f"tags/{path.name} (removed)")

    # views and the wiki are generated, gitignored artifacts; a refresh is not a
    # change worth reporting, so neither appends to `changed`.
    def do_views():
        for script in sorted(root.glob("views/*/refresh.py")):
            result = subprocess.run([sys.executable, str(script)],
                                    capture_output=True, text=True)
            if result.returncode:
                print(f"view {script.parent.name}: {result.stderr.strip()}", file=sys.stderr)

    def do_wiki():
        result = subprocess.run([sys.executable, str(_WIKI), "--root", str(root)],
                                capture_output=True, text=True)
        if result.returncode:
            print(f"wiki: {result.stderr.strip()}", file=sys.stderr)

    if want("root"):
        do_root_blocks()
    if want("tags"):
        do_tags()
    if want("views"):
        do_views()
    if schema.settings.get("wiki") and _WIKI.exists():
        do_wiki()

    print("compiled: " + (", ".join(changed) if changed else "no changes"))
    return 0


def cmd_check(root: Path, do_fm: bool, do_links: bool) -> int:
    pages = load_pages(root)
    schema = load_settings(root)
    problems: list[str] = []
    if do_fm:
        problems += check_frontmatter(pages, schema)
        problems += check_tags(pages, schema, root)
        problems += check_compiled(root)
    if do_links:
        linkable = load_pages(root, include_nonpage=True)
        problems += check_links(root, linkable)
        problems += check_source_links(root, schema)
    if not problems:
        print(f"check: clean ({len(pages)} pages)")
        return 0
    for line in problems:
        print(line)
    errors = sum(1 for p in problems if p.startswith(("ERROR", "BROKEN", "ANCHORED")))
    print(f"check: {len(problems)} issue(s), {errors} blocking", file=sys.stderr)
    return 1 if errors else 0


def cmd_stamp(path: Path) -> int:
    stamp_file(path)  # never fails the write it follows
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="canon", description=__doc__)
    parser.add_argument("--root", default="docs", help="substrate root (default: docs)")
    sub = parser.add_subparsers(dest="command", required=True)

    c = sub.add_parser("compile", help="regenerate compiled surfaces")
    c.add_argument("--block", action="append", default=[],
                   choices=["root", "tags", "views", "all"],
                   help="repeatable; default is all blocks")

    k = sub.add_parser("check", help="frontmatter conformance + link integrity")
    k.add_argument("--frontmatter", action="store_true")
    k.add_argument("--links", action="store_true")

    s = sub.add_parser("stamp", help="set a page's `updated` field to now")
    s.add_argument("path", help="the page to stamp")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "stamp":
        return cmd_stamp(Path(args.path))
    root = Path(args.root)
    if not root.is_dir():
        print(f"canon: root {root} is not a directory", file=sys.stderr)
        return 2
    if args.command == "compile":
        return cmd_compile(root, set(args.block) or {"all"})
    if args.command == "check":
        both = not (args.frontmatter or args.links)
        return cmd_check(root, do_fm=args.frontmatter or both, do_links=args.links or both)
    return 2


if __name__ == "__main__":
    sys.exit(main())
