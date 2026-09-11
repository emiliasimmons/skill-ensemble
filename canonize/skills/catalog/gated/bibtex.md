# BibTeX-managed sources

Requires `uv`.

Never read `.bib` files directly. All interaction with bib data goes through the `process_bib.py` scripts below.

A `.bib` in `docs/raw/` is a reference-manager export, a collaborator's bibliography, or a file `gated/zotero.md` materialized from a Zotero selector. `process_bib.py` tracks extraction and cataloging status across files, deduplicating on DOI.


## Status tracking

```sh
uv run scripts/process_bib.py list docs/raw/refs.bib     # all entries
uv run scripts/process_bib.py pending docs/raw/refs.bib  # not yet cataloged
```

Both accept `--json` for machine-readable output. Each call syncs new bib entries into `docs/raw/bib_status.json`.

## Extraction

For more than a handful of entries, drive the extractors from a throwaway script instead of
one call per entry. See the batch section of `SKILL.md`.

For a single entry, determine the file path from the listing. Zotero writes those paths for
the machine that exported the bib, so ask the user when one is cross-platform or WSL.

- **PDF**: `uv run scripts/extract_pdf.py <file> -o docs/raw/<bibtex_key>/`
- **Other formats**: suggest a method to the user and wait for approval.

After extraction, compare the bibtex metadata (title, authors) against extracted metadata as a sanity check. Then mark:

```sh
uv run scripts/process_bib.py mark docs/raw/refs.bib extracted <key>
```

## Cataloging

Read the extracted content and follow the standard entry flow in SKILL.md. After the entry is written to `pages/`, mark:

```sh
uv run scripts/process_bib.py mark docs/raw/refs.bib cataloged <key>
```

## Clearing flags

```sh
uv run scripts/process_bib.py mark docs/raw/refs.bib --clear extracted <key>
```

## Entries without files

Some bib entries have no attached file. The listing shows `has_file: false` for these. The agent can attempt to locate the source via DOI or URL, or work from the abstract in the bib entry. Ask the user. An entry written from the abstract is marked `basis: abstract`, per the abstract-only section of SKILL.md, and still gets marked `cataloged`.
