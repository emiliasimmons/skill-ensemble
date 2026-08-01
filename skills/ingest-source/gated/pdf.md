# PDF extraction

Requires `uv`.

Extract text, metadata, tables, and images from a PDF into a source directory. Resolve script paths relative to this skill's directory (`$S` = `<skill-dir>/scripts`).

```sh
uv run $S/extract_pdf.py paper.pdf -o docs/sources/<slug>/
uv run $S/extract_pdf.py paper.pdf -o docs/sources/<slug>/ --name smith2022
```

Output:

| File | Contents |
|---|---|
| `<name>.pdf` | copy of the source PDF (renamed with `--name`) |
| `content.md` | full text as markdown |
| `metadata.json` | title, authors, page count, extraction engine |
| `tables/` | each detected table as a CSV |
| `images/` | embedded images >5KB (pdfimages, needs poppler-utils) |

Text and tables come from pymupdf4llm and pdfplumber. On two-column journal PDFs
that interleaves the columns (reference lists especially), drops running headers
into the middle of sentences, and slices table cells into character fragments.

When those failures matter — a paper whose tables or reference list you need to
read, or an extraction that came out garbled — use the docling variant instead,
which reconstructs reading order and table structure with a layout model:

```sh
uv run $S/extract_pdf_docling.py paper.pdf -o docs/sources/<slug>/
```

Same arguments, same output files. It installs about 1 GB of dependencies and
downloads models on first use, then runs in seconds for short papers and around
half a minute for long ones.

`metadata.json` records which engine ran. To re-extract an older source with
docling, rerun over the same output directory.

When ingesting a PDF, do not read the PDF directly. Extract it first (if not yet extracted), then read the contents from the extraction as needed.
