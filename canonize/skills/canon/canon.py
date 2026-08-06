#!/usr/bin/env python3
"""canon — the deterministic layer beneath the canonize skills.

Stdlib only. It never decides anything; it compiles what frontmatter already
says, checks conformance, and hands out sequence numbers. Judgement (placement,
synthesis, grilling) stays in skill prose.

Subcommands:
  compile   regenerate compiled blocks from frontmatter
  check     frontmatter conformance + link integrity
  sequence  hand out the next DR number

Invoked by skills; never required by a project. A project is pure data.
"""

from __future__ import annotations

import argparse
import difflib
import os
import posixpath
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
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


# --- corpus model -----------------------------------------------------------

RESERVED = {"index.md", "README.md"}
# canonize config, parsed separately by load_schema; never a knowledge page
CONFIG = {"schema.md"}
# not knowledge pages: raw files, and generated view scaffolding
RAW_DIRS = {"sources", "views"}


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
    def status(self) -> str:
        return str(self.fm.get("status") or "")

    @property
    def timestamp(self) -> str:
        return str(self.fm.get("timestamp") or "")

    @property
    def synthesized(self) -> str:
        return str(self.fm.get("synthesized") or "")

    @property
    def dirname(self) -> str:
        return posixpath.dirname(self.relpath)

    def link_from(self, from_dir: str) -> str:
        return posixpath.relpath(self.relpath, from_dir or ".")


@dataclass
class Schema:
    settings: dict = field(default_factory=dict)
    registry: dict = field(default_factory=dict)   # type -> {zone, mutability, format, surfaces:set}
    tags: dict = field(default_factory=dict)        # tag -> gloss
    sources: list = field(default_factory=list)     # external trees: {name, root, ...}

    def surfaces(self, type_name: str) -> set[str]:
        row = self.registry.get(type_name)
        return row["surfaces"] if row else set()


def _iter_md(root: Path, include_index: bool = False):
    for p in sorted(root.rglob("*.md")):
        if p.name in CONFIG:
            continue
        if p.name in RESERVED and not (include_index and p.name == "index.md"):
            continue
        rel = p.relative_to(root)
        if rel.parts and rel.parts[0] in RAW_DIRS:
            continue
        yield p


def load_pages(root: Path, include_index: bool = False) -> list[Page]:
    """Knowledge pages. `include_index` adds the compiled index files, which are
    not knowledge pages but do carry links worth resolving."""
    pages = []
    for p in _iter_md(root, include_index):
        fm, body, had = parse_frontmatter(p.read_text(encoding="utf-8"))
        pages.append(Page(p.relative_to(root).as_posix(), p, fm, body, had))
    return pages


# --- schema parsing ---------------------------------------------------------

def _read_pipe_table(lines: list[str], start: int) -> tuple[list[dict], int]:
    """Read a markdown pipe table starting at/after `start`; return rows + next index."""
    i = start
    header: list[str] | None = None
    rows: list[dict] = []
    while i < len(lines):
        line = lines[i].strip()
        if not line.startswith("|"):
            if header is not None:
                break
            i += 1
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
        elif set(cells[0]) <= {"-", ":", " "}:
            pass  # separator row
        else:
            rows.append(dict(zip(header, cells)))
        i += 1
    return rows, i


def _read_fenced_mappings(lines: list[str], start: int) -> list[dict]:
    """`- key: value` mappings in this section's fenced block, one level deep."""
    i = start
    while i < len(lines) and not lines[i].startswith("```"):
        if lines[i].startswith("#"):
            return []
        i += 1
    items: list[dict] = []
    i += 1
    while i < len(lines) and not lines[i].startswith("```"):
        line = lines[i].strip()
        if line.startswith("- "):
            items.append({})
            line = line[2:].strip()
        if items and ":" in line:
            key, _, value = line.partition(":")
            items[-1][key.strip()] = _strip_scalar(value)
        i += 1
    return items


def load_schema(root: Path) -> Schema:
    schema = Schema()
    schema_path = root / "schema.md"
    if not schema_path.exists():
        return schema
    text = schema_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    section = None
    for i, line in enumerate(lines):
        h = line.strip().lower()
        if h.startswith("#"):
            title = h.lstrip("#").strip()
            if "type registry" in title:
                rows, _ = _read_pipe_table(lines, i + 1)
                for r in rows:
                    t = _demark(r.get("type", ""))
                    if not t:
                        continue
                    schema.registry[t] = {
                        "zone": _demark(r.get("zone", "")),
                        "mutability": _demark(r.get("mutability", "")),
                        "format": _demark(r.get("format", "")),
                        "surfaces": {
                            s.strip() for s in _demark(r.get("surfaces", "")).replace(",", " ").split()
                        },
                    }
            elif "tag vocabulary" in title:
                rows, _ = _read_pipe_table(lines, i + 1)
                for r in rows:
                    tag = _demark(r.get("tag", ""))
                    if tag:
                        schema.tags[tag] = r.get("gloss", "").strip()
            elif title.startswith("external sources"):
                schema.sources = [s for s in _read_fenced_mappings(lines, i + 1) if s.get("root")]
            section = title
            continue
        if section and "setting" in section:
            m = re.match(r"^\s*-\s*([A-Za-z_][A-Za-z0-9_]*):\s*(.+)$", line)
            if m:
                schema.settings[m.group(1)] = m.group(2).strip()
    return schema


def _demark(cell: str) -> str:
    # strip backticks / code spans a table cell may wrap a value in
    return cell.strip().strip("`").strip()


# --- compiled blocks --------------------------------------------------------

def _block_markers(name: str) -> tuple[str, str]:
    return f"<!-- compiled:{name} -->", f"<!-- /compiled:{name} -->"


def replace_block(text: str, name: str, content: str) -> str:
    """Replace the inner content of a compiled block, preserving authored prose.

    If the block is absent, append it at the end of the file.
    """
    open_m, close_m = _block_markers(name)
    pattern = re.compile(
        re.escape(open_m) + r".*?" + re.escape(close_m), re.DOTALL
    )
    replacement = f"{open_m}\n{content.rstrip()}\n{close_m}"
    if pattern.search(text):
        return pattern.sub(lambda _: replacement, text)
    sep = "" if text.endswith("\n\n") else ("\n" if text.endswith("\n") else "\n\n")
    return text + sep + replacement + "\n"


def _line(page: Page, from_dir: str, show_status: bool = False) -> str:
    desc = f" — {page.description}" if page.description else ""
    status = f" `{page.status}`" if show_status and page.status else ""
    return f"- [{page.title}]({page.link_from(from_dir)}){desc}{status}"


def _is_superseded(page: Page) -> bool:
    return page.status.startswith("superseded")


def _members_of(topic: str, topic_dir: str, pages: list[Page], schema: Schema) -> list[Page]:
    members = []
    for p in pages:
        if "hub" not in schema.surfaces(p.type):
            continue
        physical = p.relpath.startswith(topic_dir + "/")
        tagged = topic in p.tags
        if physical or tagged:
            members.append(p)
    return members


def _group_by_type(pages: list[Page]) -> dict[str, list[Page]]:
    groups: dict[str, list[Page]] = {}
    for p in pages:
        groups.setdefault(p.type, []).append(p)
    return groups


def compile_members(hub: Page, pages: list[Page], schema: Schema) -> str:
    topic = _topic_name(hub.relpath)
    topic_dir = f"topics/{topic}"
    members = _members_of(topic, topic_dir, pages, schema)
    if not members:
        return "_No members yet._"
    out = []
    for type_name in sorted(_group_by_type(members)):
        # superseded members sort last so the live set reads as an uninterrupted block
        rows = sorted(
            _group_by_type(members)[type_name],
            key=lambda p: (_is_superseded(p), p.relpath),
        )
        out.append(f"### {type_name.capitalize()}s ({len(rows)})")
        out.extend(_line(p, hub.dirname, show_status=True) for p in rows)
        out.append("")
    return "\n".join(out).rstrip()


def _topic_name(relpath: str) -> str:
    # topics/<name>.md -> <name>
    return Path(relpath).stem


def compile_taxonomy(pages: list[Page], schema: Schema) -> str:
    hubs = sorted((p for p in pages if p.type == "topic"), key=lambda p: p.relpath)
    out = ["### Topics", ""]
    if not hubs:
        out.append("_No topics yet._")
    for hub in hubs:
        topic = _topic_name(hub.relpath)
        count = len(_members_of(topic, f"topics/{topic}", pages, schema))
        desc = f" — {hub.description}" if hub.description else ""
        out.append(f"- [{hub.title}]({hub.link_from('')}){desc} · {count} members")
    out += ["", "### Tags", ""]
    counts = _tag_counts(pages)
    vocab = dict(schema.tags)
    all_tags = sorted(set(vocab) | set(counts))
    if not all_tags:
        out.append("_No tags yet._")
    for tag in all_tags:
        gloss = vocab.get(tag, "")
        gloss_str = f" — {gloss}" if gloss else ""
        out.append(f"- `{tag}`{gloss_str} · {counts.get(tag, 0)} pages")
    return "\n".join(out).rstrip()


def _tag_counts(pages: list[Page]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for p in pages:
        for tag in p.tags:
            counts[tag] = counts.get(tag, 0) + 1
    return counts


def _as_instant(stamp: str, *, end_of_day: bool) -> str:
    """Widen a date-only stamp to a comparable instant.

    Stamps written before the formats carried a time cannot say whether a
    same-day member landed before or after the synthesis. Bias each side so the
    pair resolves stale: a hub to the start of its day, a member to the end.
    """
    if len(stamp) == 10:
        return stamp + ("T23:59:59" if end_of_day else "T00:00:00")
    return stamp


def _unsynthesized(hub: Page, pages: list[Page], schema: Schema) -> int:
    """Members added since the hub's synthesis was last rewritten.

    A hub that has never recorded a `synthesized` stamp counts every member.
    """
    topic = _topic_name(hub.relpath)
    members = _members_of(topic, f"topics/{topic}", pages, schema)
    if not hub.synthesized:
        return len(members)
    since = _as_instant(hub.synthesized, end_of_day=False)
    return sum(
        1 for m in members
        if m.timestamp and _as_instant(m.timestamp, end_of_day=True) > since
    )


def _stale_hubs(pages: list[Page], schema: Schema) -> list[tuple[Page, int]]:
    threshold = int(schema.settings.get("hub_staleness_nudge", "5") or "5")
    out = []
    for hub in pages:
        if hub.type != "topic":
            continue
        n = _unsynthesized(hub, pages, schema)
        if n >= threshold:
            out.append((hub, n))
    return out


def compile_state(pages: list[Page], schema: Schema) -> str:
    open_decisions = [p for p in pages if p.type == "decision" and p.status == "provisional"]
    stale = _stale_hubs(pages, schema)
    recent = sorted(
        (p for p in pages if p.timestamp),
        key=lambda p: p.timestamp, reverse=True,
    )[:5]

    out = []
    out.append(f"- Open decisions: {len(open_decisions)}")
    if stale:
        names = ", ".join(f"{p.title} ({n})" for p, n in stale)
        out.append(f"- Stale hubs: {names}")
    else:
        out.append("- Stale hubs: none")
    out.append("- Recent writes:")
    if recent:
        for p in recent:
            out.append(f"  - {p.timestamp[:10]} [{p.title}]({p.link_from('')})")
    else:
        out.append("  - none yet")
    return "\n".join(out)


def compile_register(pages: list[Page], status: str) -> str:
    rows = sorted(
        (p for p in pages if p.type == "decision" and p.status == status),
        key=lambda p: p.relpath,
    )
    if not rows:
        return "_None._"
    return "\n".join(_line(p, "") for p in rows)


# --- index files (fully compiled, reserved, no frontmatter) -----------------

def _index_zones(root: Path, pages: list[Page], schema: Schema) -> list[str]:
    """Zones that get an index file. `topics` always does; the rest only once
    they hold a page, so the root never links to an index that isn't there."""
    zones = {row["zone"] for row in schema.registry.values() if row["zone"]}
    out = []
    for zone in sorted(zones):
        if not (root / zone).is_dir():
            continue
        direct = [p for p in pages if str(Path(p.relpath).parent) == zone]
        if direct or zone == "topics":
            out.append(zone)
    return out


def compile_zones(root: Path, pages: list[Page], schema: Schema) -> str:
    zones = _index_zones(root, pages, schema)
    if not zones:
        return "_No zones yet._"
    return "\n".join(f"- [{zone}]({zone}/index.md)" for zone in zones)


def _source_include(row: dict) -> dict:
    include = row.get("include")
    if isinstance(include, str):
        parts = (p.split("=", 1) for p in include.split(",") if "=" in p)
        return {k.strip(): v.strip() for k, v in parts}
    return include or {"README.md": "note"}


def _source_files(root: Path, row: dict) -> tuple[Path, dict, list[Path]]:
    tree = (root.parent / row["root"]).resolve()
    if not tree.is_dir():
        return tree, {}, []
    include = _source_include(row)
    return tree, include, sorted(p for p in tree.rglob("*.md") if p.name in include)


def _source_page(row: dict) -> str:
    return f"{row['name']}.md"


def compile_sources(root: Path, schema: Schema) -> str:
    """One line per external tree, pointing at that tree's own roster page.

    The rosters stay off the index on purpose: an index that lists every
    outside file grows without bound as the trees do.
    """
    out = []
    for row in schema.sources:
        _, _, files = _source_files(root, row)
        if not files:
            continue
        out.append(f"- [{row['name']}]({_source_page(row)}) — {len(files)} files")
    return "\n".join(out) if out else "_No external sources._"


def compile_source_roster(root: Path, row: dict) -> str:
    tree, include, files = _source_files(root, row)
    lines = []
    for path in files:
        rel = path.relative_to(tree)
        label = rel.parent.as_posix()
        label = f"{label}/{path.stem}" if label != "." else path.stem
        lines.append(f"- [{label}]({os.path.relpath(path, root)}) — {include[path.name]}")
    return "\n".join(lines)


def compile_index(directory_pages: list[Page], heading: str, from_dir: str) -> str:
    out = [f"# {heading}", ""]
    groups = _group_by_type(directory_pages)
    if not groups:
        out.append("_Empty._")
    for type_name in sorted(groups):
        out.append(f"## {type_name.capitalize()}s")
        out.append("")
        for p in sorted(groups[type_name], key=lambda p: p.relpath):
            out.append(_line(p, from_dir))
        out.append("")
    return "\n".join(out).rstrip() + "\n"


# --- link + frontmatter checking --------------------------------------------

_MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
_DECISION_STATUS_RE = re.compile(r"^(provisional|accepted|superseded by DR-\d{4,})$")


def resolve_link(target: str, from_relpath: str) -> str:
    """A link target as a path relative to the root, from the page carrying it."""
    if target.startswith("/"):
        return target.lstrip("/")
    return posixpath.normpath(posixpath.join(posixpath.dirname(from_relpath), target))


def check_frontmatter(pages: list[Page], schema: Schema) -> list[str]:
    problems = []
    core = ("title", "description")
    for p in pages:
        if not p.had_fm:
            problems.append(f"ERROR {p.relpath}: no frontmatter block")
            continue
        if not p.type:
            problems.append(f"ERROR {p.relpath}: missing `type` (the hard floor)")
            continue
        if schema.registry and p.type not in schema.registry:
            problems.append(f"WARN  {p.relpath}: type `{p.type}` not in registry")
        missing = [k for k in core if not p.fm.get(k)]
        if missing:
            problems.append(f"WARN  {p.relpath}: missing authored core {missing}")
        if not p.timestamp:
            problems.append(f"WARN  {p.relpath}: missing timestamp")
        if p.type == "decision" and p.status and not _DECISION_STATUS_RE.match(p.status):
            problems.append(f"WARN  {p.relpath}: invalid decision status `{p.status}`")
    return problems + check_orphans(pages, schema)


def check_orphans(pages: list[Page], schema: Schema) -> list[str]:
    """A hub-surfacing page that lands in no hub is reachable only from its zone
    index, outside the topic-first path."""
    hubs = {_topic_name(p.relpath) for p in pages if p.type == "topic"}
    problems = []
    for p in pages:
        if "hub" not in schema.surfaces(p.type):
            continue
        parts = Path(p.relpath).parts
        physical = len(parts) > 2 and parts[0] == "topics" and parts[1] in hubs
        if physical or any(tag in hubs for tag in p.tags):
            continue
        problems.append(f"WARN  {p.relpath}: in no hub (add a topic tag)")
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


def check_source_links(root: Path, schema: Schema) -> list[str]:
    """Links from registered external trees into the bundle.

    `check_links` walks pages under the root only, so a rename would break an
    outside citation silently.
    """
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


def _aged_out(stamp: str, days: int) -> bool:
    """True when `stamp` is older than `days` ago. An unparseable stamp is young."""
    try:
        return date.fromisoformat(stamp[:10]) < date.today() - timedelta(days=days)
    except ValueError:
        return False


def check_tags(pages: list[Page], schema: Schema) -> list[str]:
    """Registered tags that never took, and pairs that read as the same tag."""
    if not schema.tags:
        return []
    days = int(schema.settings.get("tag_aging_days", "90") or "90")
    counts = _tag_counts(pages)
    oldest: dict[str, str] = {}
    for p in pages:
        for tag in p.tags:
            if p.timestamp and (tag not in oldest or p.timestamp < oldest[tag]):
                oldest[tag] = p.timestamp

    problems = []
    for tag in sorted(schema.tags):
        n = counts.get(tag, 0)
        if n < 2 and _aged_out(oldest.get(tag, ""), days):
            problems.append(f"WARN  tag `{tag}`: {n} member(s) after {days} days (retire or grow it)")
    for a, b in _near_duplicate_tags(sorted(schema.tags)):
        problems.append(f"WARN  tags `{a}` and `{b}` read as one tag (merge into a canonical form)")
    return problems


def _near_duplicate_tags(tags: list[str]) -> list[tuple[str, str]]:
    out = []
    for i, a in enumerate(tags):
        for b in tags[i + 1:]:
            if difflib.SequenceMatcher(None, a, b).ratio() >= 0.85:
                out.append((a, b))
    return out


def check_placeholders(pages: list[Page], schema: Schema) -> list[str]:
    """Provisional decisions are legitimate, but not indefinitely."""
    days = int(schema.settings.get("placeholder_aging_days", "90") or "90")
    return [
        f"WARN  {p.relpath}: provisional for over {days} days (revisit or settle it)"
        for p in pages
        if p.type == "decision" and p.status == "provisional" and _aged_out(p.timestamp, days)
    ]


_RELATION_KEYS = ("derived_from", "bears_on", "supersedes")


def check_frontmatter_links(root: Path, pages: list[Page]) -> list[str]:
    """Validate .md links in typed-relation frontmatter keys."""
    problems = []
    for p in pages:
        for key in _RELATION_KEYS:
            val = p.fm.get(key)
            if not val:
                continue
            items = val if isinstance(val, list) else [val]
            for item in items:
                item = str(item)
                if not item.endswith(".md"):
                    continue
                if item.startswith("/"):
                    problems.append(f"ANCHORED {p.relpath}: {key} -> {item} (use a file-relative link)")
                elif not (root / resolve_link(item, p.relpath)).exists():
                    problems.append(f"BROKEN {p.relpath}: {key} -> {item}")
    return problems


# --- sequence ---------------------------------------------------------------

_DR_RE = re.compile(r"DR-(\d+)")


def next_sequence(root: Path) -> str:
    highest = 0
    decisions = root / "decisions"
    if decisions.is_dir():
        for p in decisions.glob("DR-*.md"):
            m = _DR_RE.match(p.name)
            if m:
                highest = max(highest, int(m.group(1)))
    return f"DR-{highest + 1:04d}"


# --- command wiring ---------------------------------------------------------

def _write_if_changed(path: Path, content: str) -> bool:
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


_WIKI = Path(__file__).resolve().parent / "graph.py"


def cmd_compile(root: Path, blocks: set[str], page_args: list[str]) -> int:
    pages = load_pages(root)
    schema = load_schema(root)
    changed: list[str] = []
    want = lambda name: "all" in blocks or name in blocks

    def do_root_blocks():
        idx = root / "index.md"
        if not idx.exists():
            print(f"skip: {idx} does not exist (run setup-canon first)", file=sys.stderr)
            return
        text = idx.read_text(encoding="utf-8")
        if want("taxonomy"):
            text = replace_block(text, "taxonomy", compile_taxonomy(pages, schema))
        if want("state"):
            text = replace_block(text, "state", compile_state(pages, schema))
        if want("zones"):
            text = replace_block(text, "zones", compile_zones(root, pages, schema))
        if want("sources") and schema.sources:
            do_source_pages()
            text = replace_block(text, "sources", compile_sources(root, schema))
        if _write_if_changed(idx, text):
            changed.append("index.md")

    def do_members():
        targets = [p for p in pages if p.type == "topic"]
        if page_args:
            wanted = {a.lstrip("/") for a in page_args}
            targets = [h for h in targets if h.relpath in wanted]
        for hub in targets:
            text = hub.abspath.read_text(encoding="utf-8")
            text = replace_block(text, "members", compile_members(hub, pages, schema))
            if _write_if_changed(hub.abspath, text):
                changed.append(hub.relpath)

    def do_registers():
        specs = [
            ("assumptions.md", "accepted", "Assumptions"),
            ("open-decisions.md", "provisional", "Open decisions"),
        ]
        for fname, status, _label in specs:
            path = root / fname
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            text = replace_block(text, "register", compile_register(pages, status))
            if _write_if_changed(path, text):
                changed.append(fname)

    def do_source_pages():
        for row in schema.sources:
            name = row.get("name")
            _, _, files = _source_files(root, row)
            if not name or not files or f"{name}.md" in RESERVED:
                continue
            path = root / _source_page(row)
            if path.exists():
                text = path.read_text(encoding="utf-8")
            else:
                text = (f"---\ntype: register\ntitle: {name}\n"
                        f"description: External tree at `{row['root']}`, "
                        f"cited by this bundle.\n"
                        f"timestamp: {date.today().isoformat()}\n---\n\n")
            text = replace_block(text, "members", compile_source_roster(root, row))
            if _write_if_changed(path, text):
                changed.append(_source_page(row))

    def do_indexes():
        # every zone dir that holds markdown pages gets a demoted, type-grouped index
        for zone in _index_zones(root, pages, schema):
            direct = [p for p in pages if str(Path(p.relpath).parent) == zone]
            heading = zone.replace("/", " / ")
            idx = root / zone / "index.md"
            if _write_if_changed(idx, compile_index(direct, heading, zone)):
                changed.append(f"{zone}/index.md")

    def do_wiki():
        result = subprocess.run([sys.executable, str(_WIKI), "--root", str(root)],
                                capture_output=True, text=True)
        if result.returncode:
            print(f"wiki: {result.stderr.strip()}", file=sys.stderr)
        else:
            changed.append("index.html")

    def do_views():
        for script in sorted(root.glob("views/*/refresh.py")):
            result = subprocess.run([sys.executable, str(script)],
                                    capture_output=True, text=True)
            if result.returncode:
                print(f"view {script.parent.name}: {result.stderr.strip()}", file=sys.stderr)
            else:
                changed.append(f"views/{script.parent.name}")

    if want("indexes"):
        do_indexes()
    if want("taxonomy") or want("state") or want("zones") or want("sources"):
        do_root_blocks()
    if want("members"):
        do_members()
    if want("registers"):
        do_registers()
    if want("views"):
        do_views()
    # the wiki reads whatever the corpus now says, so it follows every compile
    if _WIKI.exists():
        do_wiki()

    if changed:
        print("compiled: " + ", ".join(changed))
    else:
        print("compiled: no changes")
    return 0


def cmd_check(root: Path, do_fm: bool, do_links: bool) -> int:
    pages = load_pages(root)
    schema = load_schema(root)
    problems: list[str] = []
    if do_fm:
        problems += check_frontmatter(pages, schema)
    if do_links:
        linkable = load_pages(root, include_index=True)
        problems += check_links(root, linkable)
        problems += check_frontmatter_links(root, linkable)
        problems += check_source_links(root, schema)
    if do_fm:
        problems += check_tags(pages, schema)
        problems += check_placeholders(pages, schema)
    if not problems:
        print(f"check: clean ({len(pages)} pages)")
        return 0
    for line in problems:
        print(line)
    errors = sum(1 for p in problems if p.startswith(("ERROR", "BROKEN", "ANCHORED")))
    print(f"check: {len(problems)} issue(s), {errors} blocking", file=sys.stderr)
    return 1 if errors else 0


def cmd_sequence(root: Path, kind: str) -> int:
    if kind != "decision":
        print(f"sequence: unknown kind {kind!r} (only 'decision')", file=sys.stderr)
        return 2
    print(next_sequence(root))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="canon", description=__doc__)
    parser.add_argument("--root", default="docs", help="substrate root (default: docs)")
    sub = parser.add_subparsers(dest="command", required=True)

    c = sub.add_parser("compile", help="regenerate compiled blocks from frontmatter")
    c.add_argument("--block", action="append", default=[],
                   choices=["taxonomy", "state", "zones", "sources", "members",
                            "registers", "indexes", "views", "all"],
                   help="repeatable; default is all blocks")
    c.add_argument("--page", action="append", default=[],
                   help="limit --block members to named hub page(s)")

    k = sub.add_parser("check", help="frontmatter conformance + link integrity")
    k.add_argument("--frontmatter", action="store_true")
    k.add_argument("--links", action="store_true")

    s = sub.add_parser("sequence", help="hand out the next DR number")
    s.add_argument("--kind", default="decision")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root)
    if not root.is_dir():
        print(f"canon: root {root} is not a directory", file=sys.stderr)
        return 2
    if args.command == "compile":
        blocks = set(args.block) or {"all"}
        return cmd_compile(root, blocks, args.page)
    if args.command == "check":
        both = not (args.frontmatter or args.links)
        return cmd_check(root, do_fm=args.frontmatter or both, do_links=args.links or both)
    if args.command == "sequence":
        return cmd_sequence(root, args.kind)
    return 2


if __name__ == "__main__":
    sys.exit(main())
