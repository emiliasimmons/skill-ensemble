#!/usr/bin/env python3
"""OpenAlex CLI: keyword and semantic search, entity resolution, citation chasing, BibTeX export."""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://api.openalex.org"
KEYCHAIN_SERVICE = "openalex-api-key"
KEY_FILE = os.path.expanduser("~/.claude/.openalex-key")

WORK_FIELDS = (
    "id,doi,display_name,publication_year,publication_date,type,cited_by_count,"
    "open_access,primary_location,authorships,abstract_inverted_index,"
    "relevance_score,topics,referenced_works_count,related_works"
)

ENTITIES = {
    "author": "authors",
    "institution": "institutions",
    "source": "sources",
    "topic": "topics",
    "funder": "funders",
    "publisher": "publishers",
}

ID_PREFIX = {
    "W": "works", "A": "authors", "I": "institutions", "S": "sources",
    "T": "topics", "F": "funders", "P": "publishers", "K": "keywords",
}

# Salient fields per entity type: (label, dotted path into the record).
ENTITY_SUMMARY = {
    "authors": [
        ("orcid", "orcid"), ("works", "works_count"), ("cited by", "cited_by_count"),
        ("h-index", "summary_stats.h_index"), ("i10", "summary_stats.i10_index"),
        ("affiliation", "last_known_institutions.0.display_name"),
    ],
    "institutions": [
        ("ror", "ror"), ("country", "country_code"), ("type", "type"),
        ("works", "works_count"), ("cited by", "cited_by_count"), ("homepage", "homepage_url"),
    ],
    "sources": [
        ("issn-l", "issn_l"), ("publisher", "host_organization_name"),
        ("is oa", "is_oa"), ("in doaj", "is_in_doaj"),
        ("apc usd", "apc_usd"), ("works", "works_count"),
    ],
    "topics": [
        ("field", "field.display_name"), ("domain", "domain.display_name"),
        ("works", "works_count"), ("description", "description"),
    ],
    "funders": [
        ("country", "country_code"), ("works", "works_count"),
        ("grants", "grants_count"), ("homepage", "homepage_url"),
    ],
    "publishers": [
        ("level", "hierarchy_level"), ("works", "works_count"),
    ],
}


def dig(obj, path):
    """Follow a dotted path, treating integer segments as list indices."""
    for part in path.split("."):
        if obj is None:
            return None
        if part.isdigit():
            obj = obj[int(part)] if len(obj) > int(part) else None
        else:
            obj = obj.get(part) if isinstance(obj, dict) else None
    return obj


def normalize_ident(raw):
    """Map an identifier to (endpoint, ident). Endpoint is None if undetectable."""
    s = raw.strip()
    low = s.lower()
    if low.startswith("https://doi.org/"):
        return "works", "doi:" + s[len("https://doi.org/"):]
    if low.startswith("10."):
        return "works", f"doi:{s}"
    if low.startswith("doi:") or low.startswith("pmid:") or low.startswith("pmcid:"):
        return "works", s
    if "orcid.org/" in low:
        return "authors", s
    if "ror.org/" in low:
        return "institutions", s
    if low.startswith("issn:"):
        return "sources", s
    m = re.match(r"^([WAISTFPK])\d+$", s, re.I)
    if m:
        return ID_PREFIX[m.group(1).upper()], s.upper()
    return None, s


def die(msg, code=1):
    print(msg, file=sys.stderr)
    sys.exit(code)


def resolve_key():
    """Env var, then macOS Keychain, then key file. Returns (key, origin)."""
    key = os.environ.get("OPENALEX_API_KEY")
    if key:
        return key.strip(), "env:OPENALEX_API_KEY"

    try:
        out = subprocess.run(
            ["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"],
            capture_output=True, text=True, timeout=10,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip(), f"keychain:{KEYCHAIN_SERVICE}"
    except (FileNotFoundError, subprocess.SubprocessError):
        pass

    if os.path.exists(KEY_FILE):
        with open(KEY_FILE) as f:
            key = f.read().strip()
        if key:
            return key, KEY_FILE

    die(
        "No OpenAlex API key found. Looked in:\n"
        f"  1. $OPENALEX_API_KEY\n"
        f"  2. macOS Keychain service '{KEYCHAIN_SERVICE}'\n"
        f"  3. {KEY_FILE}\n\n"
        "Get a free key at https://openalex.org/settings/api, then run the setup "
        "step in the openalex-search skill."
    )


def fetch(path, params, key):
    params = {k: v for k, v in params.items() if v is not None}
    params["api_key"] = key
    url = f"{BASE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "openalex-search-skill"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode()), dict(r.headers)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:600]
        if e.code in (401, 403):
            die(f"HTTP {e.code} — key rejected. Verify it at https://openalex.org/settings/api\n{body}")
        if e.code == 429:
            die(
                "HTTP 429 — daily usage allowance exhausted.\n"
                "Check https://openalex.org/settings/usage — it resets daily.\n" + body
            )
        die(f"HTTP {e.code}: {body}")
    except urllib.error.URLError as e:
        die(f"Network error: {e.reason}")


def build_filter(args):
    parts = list(args.filter or [])
    if args.year:
        parts.append(f"publication_year:{args.year}")
    if args.oa:
        parts.append("is_oa:true")
    if args.type:
        parts.append(f"type:{args.type}")
    if args.min_citations:
        parts.append(f"cited_by_count:>{args.min_citations}")
    return ",".join(parts) or None


def abstract_text(work):
    idx = work.get("abstract_inverted_index")
    if not idx:
        return ""
    positions = [(p, w) for w, ps in idx.items() for p in ps]
    positions.sort()
    return " ".join(w for _, w in positions)


def authors(work, limit=3):
    names = [
        a.get("author", {}).get("display_name", "")
        for a in work.get("authorships", [])
    ]
    names = [n for n in names if n]
    if not names:
        return "—"
    shown = ", ".join(names[:limit])
    extra = len(names) - limit
    return f"{shown} +{extra} more" if extra > 0 else shown


def surname(work):
    for a in work.get("authorships", []):
        name = a.get("author", {}).get("display_name", "").strip()
        if name:
            return name.split()[-1]
    return "anon"


def slug(work):
    """BibTeX-style key, also usable as a canonize page filename: doudna2021."""
    base = re.sub(r"[^a-z]", "", surname(work).lower()) or "anon"
    return f"{base}{work.get('publication_year') or 'nd'}"


def venue(work):
    loc = work.get("primary_location") or {}
    src = loc.get("source") or {}
    return src.get("display_name") or "—"


def short_doi(work):
    doi = work.get("doi") or ""
    return doi.replace("https://doi.org/", "") or "—"


def oa_tag(work):
    oa = work.get("open_access") or {}
    if not oa.get("is_oa"):
        return "closed"
    return oa.get("oa_status") or "oa"


def openalex_id(work):
    return (work.get("id") or "").rsplit("/", 1)[-1]


def print_works(works, semantic=False):
    if not works:
        print("No results.")
        return
    for i, w in enumerate(works, 1):
        bits = [str(w.get("publication_year") or "n.d."),
                f"{w.get('cited_by_count', 0)} cites",
                oa_tag(w)]
        if semantic and w.get("relevance_score") is not None:
            bits.append(f"score {w['relevance_score']:.3f}")
        print(f"[{i}] " + " · ".join(bits))
        print(f"    {w.get('display_name') or 'Untitled'}")
        print(f"    {authors(w)} · {venue(w)}")
        print(f"    doi:{short_doi(w)}  {openalex_id(w)}  key:{slug(w)}")
        print()


def escape_bibtex(s):
    return s.replace("{", "").replace("}", "").replace("\\", "")


def print_bibtex(works, with_abstract=False):
    for w in works:
        names = [
            a.get("author", {}).get("display_name", "")
            for a in w.get("authorships", [])
        ]
        entry_type = "article" if w.get("type") == "article" else "misc"
        fields = [
            ("author", " and ".join(n for n in names if n)),
            ("title", w.get("display_name") or ""),
            ("journal", venue(w) if venue(w) != "—" else ""),
            ("year", str(w.get("publication_year") or "")),
            ("doi", short_doi(w) if short_doi(w) != "—" else ""),
            ("url", w.get("doi") or ""),
            ("note", f"OpenAlex {openalex_id(w)}"),
        ]
        if with_abstract:
            fields.append(("abstract", abstract_text(w)))
        print(f"@{entry_type}{{{slug(w)},")
        for k, v in fields:
            if v:
                print(f"  {k} = {{{escape_bibtex(v)}}},")
        print("}\n")


def emit(works, args, semantic=False):
    if args.json:
        print(json.dumps(works, indent=2))
    elif args.bibtex:
        print_bibtex(works, with_abstract=args.abstract)
    else:
        print_works(works, semantic=semantic)
        if args.abstract:
            for w in works:
                text = abstract_text(w)
                if text:
                    print(f"--- {slug(w)} ---\n{text}\n")


def cmd_check(args, key, origin):
    data, headers = fetch("/works", {"per_page": 1, "select": "id"}, key)
    print(f"Key OK (from {origin}).")
    print(f"Corpus: {data['meta']['count']:,} works.")
    for h in ("X-RateLimit-Limit", "X-RateLimit-Remaining",
              "X-RateLimit-Credits-Used", "X-RateLimit-Reset"):
        if h in headers:
            print(f"{h}: {headers[h]}")
    print("Usage detail: https://openalex.org/settings/usage")


def cmd_search(args, key, origin):
    filt = build_filter(args)

    if args.semantic:
        limit = min(args.limit, 50)
        params = {
            "search.semantic": args.query,
            "filter": filt,
            "per_page": limit,
            "select": WORK_FIELDS,
        }
        data, _ = fetch("/works", params, key)
        results = data.get("results", [])[:limit]
        cost = data.get("meta", {}).get("cost_usd")
        print(f"# semantic · {len(results)} results (max 50) · ${cost}\n", file=sys.stderr)
        emit(results, args, semantic=True)
        return

    results = []
    cursor = "*"
    spent = 0.0
    while len(results) < args.limit:
        params = {
            "search": args.query or None,
            "filter": filt,
            "per_page": min(200, args.limit - len(results)),
            "cursor": cursor,
            "select": WORK_FIELDS,
            "sort": args.sort,
        }
        data, _ = fetch("/works", params, key)
        batch = data.get("results", [])
        results.extend(batch)
        spent += data.get("meta", {}).get("cost_usd") or 0.0
        cursor = data.get("meta", {}).get("next_cursor")
        if not batch or not cursor:
            break
    total = data.get("meta", {}).get("count", len(results))
    print(f"# keyword · {len(results)} shown of {total:,} matches · ${spent:.4f}\n",
          file=sys.stderr)
    emit(results[: args.limit], args)


def print_entity(endpoint, rec):
    print(rec.get("display_name") or "Untitled")
    print(f"  id: {(rec.get('id') or '').rsplit('/', 1)[-1]}")
    for label, path in ENTITY_SUMMARY.get(endpoint, []):
        val = dig(rec, path)
        if val not in (None, "", []):
            print(f"  {label}: {val}")


def cmd_get(args, key, origin):
    endpoint, ident = normalize_ident(args.id)
    if args.entity:
        endpoint = ENTITIES.get(args.entity, args.entity)
    if endpoint is None:
        die(f"Cannot tell what kind of entity '{args.id}' is. Pass --entity.")

    path = f"/{endpoint}/{urllib.parse.quote(ident, safe=':/.')}"
    select = WORK_FIELDS if endpoint == "works" else None
    data, _ = fetch(path, {"select": select}, key)

    if endpoint == "works":
        emit([data], args)
        if not (args.json or args.bibtex):
            related = data.get("related_works") or []
            if related:
                print(f"related_works ({len(related)}): "
                      + " ".join(r.rsplit('/', 1)[-1] for r in related[:10]))
        return

    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print_entity(endpoint, data)


def cmd_group(args, key, origin):
    params = {
        "group_by": args.field,
        "filter": build_filter(args),
        "search": args.query or None,
    }
    data, _ = fetch(f"/{args.entity}", params, key)
    groups = data.get("group_by", [])
    if not groups:
        print("No groups returned.")
        return

    if args.json:
        print(json.dumps(groups, indent=2))
        return

    grand_total = sum(g["count"] for g in groups)

    if args.field.endswith("year") and args.sort != "count":
        # Most recent years are the interesting ones, but read best oldest-first.
        groups.sort(key=lambda g: str(g.get("key")), reverse=True)
        shown = groups[: args.limit][::-1]
    else:
        shown = groups[: args.limit]

    def label(g):
        name = str(g.get("key_display_name") or g.get("key"))
        return name.rsplit("/", 1)[-1] if name.startswith("https://openalex.org/") else name

    width = min(max(len(label(g)) for g in shown), 60)
    for g in shown:
        share = g["count"] / grand_total * 100 if grand_total else 0
        print(f"{label(g)[:width]:<{width}}  {g['count']:>8,}  {share:5.1f}%")

    shown_total = sum(g["count"] for g in shown)
    print(f"\n{len(shown)} of {len(groups)} groups, "
          f"{shown_total:,} of {grand_total:,} works.")


def cmd_batch(args, key, origin):
    raw_ids = list(args.ids or [])
    if args.file:
        with open(args.file) as f:
            raw_ids += [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
    if not raw_ids:
        die("No IDs given. Pass them as arguments or with --file.")

    dois, oa_ids, singles = [], [], []
    for raw in raw_ids:
        s = raw.strip()
        for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
            if s.lower().startswith(prefix):
                s = s[len(prefix):]
                break
        if re.match(r"^[WAISTFPK]\d+$", s, re.I):
            oa_ids.append(s.upper())
        elif s.startswith("10."):
            # A comma or pipe inside a DOI would break the filter; fetch those alone.
            (singles if ("," in s or "|" in s) else dois).append(s.lower())
        else:
            singles.append(s)

    found, seen_dois = [], set()

    def run_batches(field, values):
        for i in range(0, len(values), 50):
            chunk = values[i:i + 50]
            params = {
                "filter": f"{field}:{'|'.join(chunk)}",
                "per_page": len(chunk),
                "select": WORK_FIELDS,
            }
            data, _ = fetch(f"/{args.entity}", params, key)
            found.extend(data.get("results", []))

    if dois:
        run_batches("doi", dois)
    if oa_ids:
        run_batches("openalex", oa_ids)
    for ident in singles:
        endpoint, norm = normalize_ident(ident)
        try:
            rec, _ = fetch(f"/{endpoint or args.entity}/"
                           f"{urllib.parse.quote(norm, safe=':/.')}",
                           {"select": WORK_FIELDS}, key)
            found.append(rec)
        except SystemExit:
            pass

    for w in found:
        d = (w.get("doi") or "").replace("https://doi.org/", "").lower()
        if d:
            seen_dois.add(d)

    emit(found, args)

    missing = [d for d in dois if d not in seen_dois]
    if missing:
        sys.stdout.flush()  # keeps the report below the results, and out of --bibtex
        print(f"\nNot in OpenAlex ({len(missing)} of {len(raw_ids)} requested):",
              file=sys.stderr)
        for d in missing:
            print(f"  {d}", file=sys.stderr)


def cmd_cited_by(args, key, origin):
    ident = args.id
    if ident.startswith("10."):
        ident = f"doi:{ident}"
    work, _ = fetch(f"/works/{urllib.parse.quote(ident, safe=':/.')}",
                    {"select": "id,display_name,cited_by_count"}, key)
    wid = openalex_id(work)
    print(f"# citing '{work.get('display_name')}' ({work.get('cited_by_count', 0)} total)\n",
          file=sys.stderr)
    params = {
        "filter": f"cites:{wid}",
        "per_page": min(200, args.limit),
        "select": WORK_FIELDS,
        "sort": args.sort or "cited_by_count:desc",
    }
    data, _ = fetch("/works", params, key)
    # OpenAlex sometimes lists a work in its own referenced_works; drop the seed.
    citing = [w for w in data.get("results", []) if openalex_id(w) != wid]
    emit(citing[: args.limit], args)


def cmd_resolve(args, key, origin):
    endpoint = ENTITIES[args.entity]
    data, _ = fetch(
        f"/{endpoint}",
        {"search": args.name, "per_page": args.limit,
         "select": "id,display_name,works_count,cited_by_count"},
        key,
    )
    results = data.get("results", [])
    if not results:
        print("No match.")
        return
    if args.json:
        print(json.dumps(results, indent=2))
        return
    for r in results:
        rid = (r.get("id") or "").rsplit("/", 1)[-1]
        print(f"{rid:<14} {r.get('works_count', 0):>8} works  {r.get('display_name')}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_output(sp):
        sp.add_argument("--json", action="store_true", help="raw JSON")
        sp.add_argument("--bibtex", action="store_true", help="BibTeX for canonize ingest")
        sp.add_argument("--abstract", action="store_true", help="include abstracts")

    def add_filters(sp):
        sp.add_argument("--filter", action="append", metavar="FIELD:VALUE",
                        help="raw OpenAlex filter, repeatable")
        sp.add_argument("--year", metavar="Y", help="2023, >2020, or 2020-2024")
        sp.add_argument("--oa", action="store_true", help="open access only")
        sp.add_argument("--type", help="article, book, dataset, review, preprint")
        sp.add_argument("--min-citations", type=int, metavar="N")

    sp = sub.add_parser("check", help="verify key and show remaining allowance")
    add_output(sp)

    sp = sub.add_parser("search", help="keyword (default) or semantic search")
    sp.add_argument("query")
    sp.add_argument("--semantic", action="store_true",
                    help="vector search; ~100x the cost of a list call, max 50 results")
    sp.add_argument("--limit", type=int, default=25)
    sp.add_argument("--sort", help="e.g. cited_by_count:desc, publication_date:desc")
    add_filters(sp)
    add_output(sp)

    sp = sub.add_parser("get", help="fetch one entity by DOI, ORCID, ROR, ISSN, or OpenAlex ID")
    sp.add_argument("id")
    sp.add_argument("--entity", help="override type detection (author, institution, ...)")
    add_output(sp)

    sp = sub.add_parser("group", help="counts grouped by a field, one cheap call")
    sp.add_argument("field", help="publication_year, type, open_access.oa_status, topics.id, ...")
    sp.add_argument("--query", help="restrict to a search first (costs search rate)")
    sp.add_argument("--entity", default="works")
    sp.add_argument("--limit", type=int, default=25)
    sp.add_argument("--sort", choices=["count", "key"], help="default: chronological for years, else count")
    add_filters(sp)
    sp.add_argument("--json", action="store_true")

    sp = sub.add_parser("batch", help="look up many DOIs or IDs, 50 per call")
    sp.add_argument("ids", nargs="*")
    sp.add_argument("--file", help="file of IDs, one per line, # comments allowed")
    sp.add_argument("--entity", default="works")
    add_output(sp)

    sp = sub.add_parser("cited-by", help="works citing a given work")
    sp.add_argument("id")
    sp.add_argument("--limit", type=int, default=25)
    sp.add_argument("--sort")
    add_output(sp)

    sp = sub.add_parser("resolve", help="name -> OpenAlex ID (always do this before filtering)")
    sp.add_argument("entity", choices=sorted(ENTITIES))
    sp.add_argument("name")
    sp.add_argument("--limit", type=int, default=5)
    sp.add_argument("--json", action="store_true")

    args = p.parse_args()
    key, origin = resolve_key()
    handlers = {
        "check": cmd_check, "search": cmd_search, "get": cmd_get,
        "cited-by": cmd_cited_by, "resolve": cmd_resolve,
        "group": cmd_group, "batch": cmd_batch,
    }
    handlers[args.cmd](args, key, origin)


if __name__ == "__main__":
    main()
