#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "bibtexparser>=1.4,<2",
# ]
# ///
"""Track extraction and ingestion status for BibTeX-managed sources.

Usage:
    uv run process_bib.py list sources/refs.bib [--json]
    uv run process_bib.py pending sources/refs.bib [--json]
    uv run process_bib.py mark sources/refs.bib extracted key1 [key2 ...]
    uv run process_bib.py mark sources/refs.bib extracted key1 --via zotero
    uv run process_bib.py mark sources/refs.bib --clear ingested key1

Status tracked in bib_status.json alongside the bib file.
Deduplicates entries by DOI when available, bibtex key otherwise.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import bibtexparser

STATUS_FILENAME = "bib_status.json"


def normalize_doi(doi: str) -> str:
    doi = doi.strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if doi.startswith(prefix):
            doi = doi[len(prefix):]
    return doi


def canonical_id(entry: dict) -> str:
    doi = entry.get("doi", "").strip()
    if doi:
        return normalize_doi(doi)
    return entry["ID"]


def parse_file_field(raw: str) -> list[dict]:
    """Parse Zotero file field: description:path:mime_type (semicolon-separated)."""
    results = []
    for part in re.split(r"(?<!\\);", raw):
        part = part.strip()
        if not part:
            continue
        colons = [m.start() for m in re.finditer(r"(?<!\\):", part)]
        if len(colons) < 2:
            continue
        description = part[: colons[0]].strip()
        path_raw = part[colons[0] + 1 : colons[-1]].strip()
        mime_type = part[colons[-1] + 1 :].strip()
        path = (path_raw
                .replace("\\;", ";")
                .replace("\\:", ":")
                .replace("\\\\", "\\"))
        results.append(
            {"description": description, "path": path, "mime_type": mime_type}
        )
    return results


def first_author_etal(author_field: str) -> str:
    authors = [a.strip() for a in author_field.split(" and ") if a.strip()]
    if not authors:
        return ""
    first = authors[0]
    if "," in first:
        last = first.split(",")[0].strip()
    else:
        parts = first.split()
        last = parts[-1] if parts else first
    return f"{last} et al." if len(authors) > 1 else last


def strip_braces(s: str) -> str:
    return s.replace("{", "").replace("}", "")


def load_bib(bib_path: Path) -> list[dict]:
    text = bib_path.read_text(encoding="utf-8")
    bib = bibtexparser.loads(text)
    return bib.entries


def load_status(status_path: Path) -> dict:
    if status_path.exists():
        return json.loads(status_path.read_text(encoding="utf-8"))
    return {}


def save_status(status_path: Path, status: dict) -> None:
    status_path.write_text(
        json.dumps(status, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def sync_status(entries: list[dict], status: dict) -> dict:
    """Register any bib entries not yet in the status file.

    When an entry previously tracked by bibtex key gains a DOI, migrate
    the existing record to the DOI-based canonical id.
    """
    for entry in entries:
        cid = canonical_id(entry)
        key = entry["ID"]
        if cid not in status:
            # migrate: entry was tracked by key, now has a DOI
            if key in status and key != cid:
                status[cid] = status.pop(key)
                if key not in status[cid]["keys"]:
                    status[cid]["keys"].append(key)
            else:
                status[cid] = {"keys": [key], "extracted": False, "ingested": False}
        elif key not in status[cid]["keys"]:
            status[cid]["keys"].append(key)
    return status


def resolve_key(key: str, status: dict) -> str | None:
    if key in status:
        return key
    for cid, rec in status.items():
        if key in rec.get("keys", []):
            return cid
    return None


def entry_to_record(entry: dict, status: dict) -> dict:
    cid = canonical_id(entry)
    file_raw = entry.get("file", "")
    files = parse_file_field(file_raw) if file_raw else []
    primary = files[0] if files else None
    st = status.get(cid, {})

    return {
        "key": entry["ID"],
        "canonical_id": cid,
        "title": strip_braces(entry.get("title", "")),
        "authors": first_author_etal(entry.get("author", "")),
        "year": entry.get("year", ""),
        "doi": entry.get("doi", "").strip() or None,
        "url": entry.get("url", "").strip() or None,
        "abstract": strip_braces(entry.get("abstract", "")) or None,
        "has_file": primary is not None,
        "file_path": primary["path"] if primary else None,
        "file_type": primary["mime_type"] if primary else None,
        "extracted": st.get("extracted", False),
        "ingested": st.get("ingested", False),
    }


def short_type(mime: str | None) -> str:
    if not mime:
        return "-"
    if "/" in mime:
        return mime.split("/")[-1]
    return mime


def show_flag(value) -> str:
    """Flags are true/false, or a string naming how they were satisfied."""
    if isinstance(value, str):
        return value
    return "yes" if value else "no"


def print_table(records: list[dict]) -> None:
    if not records:
        return
    key_w = max(len(r["key"]) for r in records)
    type_w = max(len(short_type(r["file_type"])) for r in records)
    ext_w = max(3, *(len(show_flag(r["extracted"])) for r in records))
    title_max = 52

    fmt = f"{{:<{key_w}}}  {{:<{type_w}}}  {{:>{ext_w}}}  {{:>3}}  {{}}"
    print(fmt.format("KEY", "TYPE", "EXT", "ING", "TITLE"))
    print("-" * (key_w + type_w + ext_w + title_max + 11))
    for r in records:
        title = r["title"]
        if len(title) > title_max:
            title = title[: title_max - 3] + "..."
        print(
            fmt.format(
                r["key"],
                short_type(r["file_type"]),
                show_flag(r["extracted"]),
                show_flag(r["ingested"]),
                title,
            )
        )


def load_all(bibfile: str) -> tuple[list[dict], dict, Path]:
    bib_path = Path(bibfile).resolve()
    if not bib_path.exists():
        print(f"file not found: {bibfile}", file=sys.stderr)
        sys.exit(1)
    status_path = bib_path.parent / STATUS_FILENAME
    entries = load_bib(bib_path)
    status = load_status(status_path)
    status = sync_status(entries, status)
    return entries, status, status_path


def cmd_list(args):
    entries, status, status_path = load_all(args.bibfile)
    save_status(status_path, status)

    records = [entry_to_record(e, status) for e in entries]
    if args.json:
        print(json.dumps(records, indent=2, ensure_ascii=False))
    else:
        print_table(records)


def cmd_pending(args):
    entries, status, status_path = load_all(args.bibfile)
    save_status(status_path, status)

    records = [entry_to_record(e, status) for e in entries]
    records = [r for r in records if not r["ingested"]]

    if args.json:
        print(json.dumps(records, indent=2, ensure_ascii=False))
    else:
        if not records:
            print("all entries ingested")
        else:
            print_table(records)


def cmd_mark(args):
    entries, status, status_path = load_all(args.bibfile)

    # validate all keys before applying any changes
    resolved = []
    for key in args.keys:
        cid = resolve_key(key, status)
        if cid is None:
            print(f"unknown key: {key}", file=sys.stderr)
            sys.exit(1)
        resolved.append((key, cid))

    if args.clear and args.via:
        print("--clear and --via are mutually exclusive", file=sys.stderr)
        sys.exit(1)

    value = False if args.clear else (args.via or True)
    verb = "cleared" if args.clear else "set"
    for key, cid in resolved:
        status[cid][args.flag] = value
        suffix = f" ({args.via})" if args.via else ""
        print(f"{verb} {args.flag} on {key}{suffix}")

    save_status(status_path, status)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="list all entries with status")
    p_list.add_argument("bibfile", help="path to .bib file")
    p_list.add_argument("--json", action="store_true")
    p_list.set_defaults(func=cmd_list)

    p_pending = sub.add_parser("pending", help="entries not yet ingested")
    p_pending.add_argument("bibfile", help="path to .bib file")
    p_pending.add_argument("--json", action="store_true")
    p_pending.set_defaults(func=cmd_pending)

    p_mark = sub.add_parser("mark", help="set or clear status flags")
    p_mark.add_argument("bibfile", help="path to .bib file")
    p_mark.add_argument("flag", choices=["extracted", "ingested"])
    p_mark.add_argument("keys", nargs="+", help="bibtex keys")
    p_mark.add_argument(
        "--clear", action="store_true", help="clear instead of set"
    )
    p_mark.add_argument(
        "--via",
        help="record how the flag was satisfied instead of a bare true "
        "(e.g. --via zotero for fulltext pulled from Zotero)",
    )
    p_mark.set_defaults(func=cmd_mark)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
