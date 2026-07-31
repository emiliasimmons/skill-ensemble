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
| `content.md` | full text as markdown (pymupdf4llm, handles multi-column) |
| `metadata.json` | title, authors, page count, etc. |
| `tables/` | each detected table as a CSV (pdfplumber) |
| `images/` | embedded images >5KB (pdfimages, needs poppler-utils) |

When ingesting a PDF, do not read the PDF directly. Extract it first (if not yet extracted), then read the contents from the extraction as needed.
