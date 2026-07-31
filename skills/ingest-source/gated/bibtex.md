# BibTeX-managed sources

Requires `uv`.

Never read `.bib` files directly. All interaction with bib data goes through the `process_bib.py` scripts below.

The user manages references in Zotero or Mendeley and exports `.bib` files into `docs/sources/`. `process_bib.py` tracks extraction and ingestion status across exports, deduplicating on DOI.

Resolve script paths relative to this skill's directory. All examples below use `$S` as shorthand for `<skill-dir>/scripts`.

## Status tracking

```sh
uv run $S/process_bib.py list docs/sources/refs.bib          # all entries
uv run $S/process_bib.py pending docs/sources/refs.bib       # not yet ingested
```

Both accept `--json` for machine-readable output. Each call syncs new bib entries into `docs/sources/bib_status.json`.

## Extraction

For each pending entry with a file, determine the file path from the listing. If the path is unclear (cross-platform, WSL, etc.), ask the user.

- **PDF**: `uv run $S/extract_pdf.py <file> -o docs/sources/<bibtex_key>/`
- **Other formats**: suggest a method to the user and wait for approval.

After extraction, compare the bibtex metadata (title, authors) against extracted metadata as a sanity check. Then mark:

```sh
uv run $S/process_bib.py mark docs/sources/refs.bib extracted <key>
```

## Ingestion

Read the extracted content and follow the standard source flow in SKILL.md. After the source page is written via /record-doc, mark:

```sh
uv run $S/process_bib.py mark docs/sources/refs.bib ingested <key>
```

## Clearing flags

```sh
uv run $S/process_bib.py mark docs/sources/refs.bib --clear extracted <key>
```

## Entries without files

Some bib entries have no attached file. The listing shows `has_file: false` for these. The agent can attempt to locate the source via DOI or URL, or work from the abstract alone. Ask the user.
