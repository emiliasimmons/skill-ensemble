# PDF sources

Copy the PDF into its source directory, then read the copy with the Read tool:

```sh
mkdir -p docs/raw/smith-2022-trachoma
cp paper.pdf docs/raw/smith-2022-trachoma/smith-2022-trachoma.pdf
```

Read takes at most 20 pages per call and needs a `pages` range for PDFs over 10 pages, so
read a long paper in consecutive ranges (`1-20`, `21-40`).

## Scripted extraction

Requires `uv`. Run the extraction scripts only when the user asks for them, or when Read
cannot open the PDF.

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

The docling variant reconstructs reading order and table structure with a layout model:

```sh
uv run scripts/extract_pdf_docling.py paper.pdf -o docs/raw/smith-2022-trachoma/
```

Same arguments, same output files. It installs about 1 GB of dependencies and
downloads models on first use, then runs in seconds for short papers and around
half a minute for long ones.

Ask before the first docling run in a project, naming the install size. Once the user
agrees, record it as `docling approved` under `## PDF extraction` in `docs/CLAUDE.md`,
adding the heading if it is missing, and stop asking. Treat that line as the record of
consent: when it reads approved, run docling without a prompt. When it does not, ask again
even if a source directory already shows `"engine": "docling"`.

`metadata.json` records which engine ran. To re-extract a source with the other engine,
rerun over the same output directory.
