# PDF extraction

Requires `uv`.

Extract text, metadata, tables, and images from a PDF into a source directory.

```sh
uv run scripts/extract_pdf.py paper.pdf -o docs/raw/smith-2022-trachoma/
```

Output:

| File | Contents |
|---|---|
| `<slug>.pdf` | copy of the source PDF, renamed to the directory's slug |
| `content.md` | full text as markdown |
| `metadata.json` | title, authors, page count, extraction engine |
| `tables/` | each detected table as a CSV |
| `images/` | embedded images >5KB (pdfimages, needs poppler-utils) |

Text and tables come from pymupdf4llm and pdfplumber. On two-column journal PDFs
that interleaves the columns (reference lists especially), drops running headers
into the middle of sentences, and slices table cells into character fragments.

When those failures matter (a paper whose tables or reference list you need to
read, or an extraction that came out garbled) use the docling variant instead,
which reconstructs reading order and table structure with a layout model:

```sh
uv run scripts/extract_pdf_docling.py paper.pdf -o docs/raw/smith-2022-trachoma/
```

Same arguments, same output files. It installs about 1 GB of dependencies and
downloads models on first use, then runs in seconds for short papers and around
half a minute for long ones.

Ask before the first docling run in a project, naming the install size (unless
`docs/CLAUDE.md` `## Sourcing` already reads docling approved, set at setup). Once
the user agrees, record it under `## Sourcing` in `docs/CLAUDE.md` and stop asking.
Treat that line as the record of consent: when it reads approved, run docling
without a prompt. When it does not, ask again even if a source directory already
shows `"engine": "docling"`.

`metadata.json` records which engine ran. To re-extract an older source with
docling, rerun over the same output directory.

For more than a handful of PDFs at once, drive this script from a throwaway loop rather
than one call per file. See the batch section of `SKILL.md`.

When cataloging a PDF, do not read the PDF directly. Extract it first (if not yet extracted), then read the contents from the extraction as needed.
