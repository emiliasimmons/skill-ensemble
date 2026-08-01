#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pymupdf4llm>=0.0.17",
#     "pymupdf>=1.25",
#     "pypdf>=4.0",
#     "pdfplumber>=0.11",
#     "pandas>=2.0",
# ]
# ///
"""Extract text, tables, metadata, and images from an academic PDF.

Usage:
    uv run extract_pdf.py paper.pdf -o outdir/
    uv run extract_pdf.py paper.pdf -o outdir/ --name smith2022

Output directory will contain:
    paper.pdf / smith2022.pdf   copy of the source PDF (renamed with --name)
    content.md                  full text as markdown
    metadata.json               title, authors, page count, extraction engine
    tables/                     each detected table as a CSV
    images/                     embedded images >5KB (pdfimages, needs poppler-utils)

Text and tables come from pymupdf4llm and pdfplumber. On two-column journal PDFs
that interleaves the columns, drops running headers mid-sentence, and slices table
cells into character fragments; `extract_pdf_docling.py` runs a layout model that
fixes those, for a 1 GB install.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pdfplumber
import pymupdf4llm
from pypdf import PdfReader


def extract_metadata(pdf_path: Path) -> dict:
    reader = PdfReader(pdf_path)
    meta = reader.metadata
    info: dict = {
        "file": pdf_path.name,
        "pages": len(reader.pages),
    }
    if meta is not None:
        info.update({
            "title": meta.get("/Title") or meta.title,
            "author": meta.get("/Author") or meta.author,
            "subject": meta.get("/Subject") or meta.subject,
            "creator": meta.get("/Creator") or meta.creator,
            "producer": meta.get("/Producer"),
            "creation_date": str(meta.get("/CreationDate", "")),
        })
    return {k: v for k, v in info.items() if v is not None}


def docling_available() -> bool:
    return importlib.util.find_spec("docling") is not None


def extract_markdown(pdf_path: Path) -> str:
    return pymupdf4llm.to_markdown(str(pdf_path))


def extract_with_docling(pdf_path: Path, out_dir: Path) -> tuple[str, int]:
    """Return (markdown, table count), writing docling's tables to out_dir/tables."""
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption

    opts = PdfPipelineOptions()
    opts.do_ocr = False
    opts.do_table_structure = True
    opts.table_structure_options.do_cell_matching = True
    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)}
    )
    doc = converter.convert(str(pdf_path)).document

    count = 0
    for table in doc.tables:
        df = table.export_to_dataframe(doc=doc)
        if df.empty:
            continue
        count += 1
        out_dir.mkdir(exist_ok=True)
        df.to_csv(out_dir / f"t{count:02d}.csv", index=False)
    return doc.export_to_markdown(), count


def extract_tables(pdf_path: Path, out_dir: Path) -> int:
    created = not out_dir.exists()
    out_dir.mkdir(exist_ok=True)
    count = 0
    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables()
            for tbl_idx, table in enumerate(tables, 1):
                if not table or len(table) < 2:
                    continue
                flat = [c for row in table for c in row if c]
                if len(flat) < 3:
                    continue
                count += 1
                header = table[0]
                header = [str(h).strip() if h else f"col_{i}" for i, h in enumerate(header)]
                rows = table[1:]
                df = pd.DataFrame(rows, columns=header)
                df.to_csv(out_dir / f"p{page_idx:02d}_t{tbl_idx}.csv", index=False)
    if count == 0 and created:
        out_dir.rmdir()
    return count


def extract_images(pdf_path: Path, out_dir: Path) -> int:
    if not shutil.which("pdfimages"):
        return -1
    created = not out_dir.exists()
    out_dir.mkdir(exist_ok=True)
    result = subprocess.run(
        ["pdfimages", "-all", "-p", str(pdf_path), str(out_dir / "img")],
        capture_output=True,
    )
    if result.returncode != 0:
        msg = result.stderr.decode(errors="replace").strip()
        print(f"pdfimages failed (exit {result.returncode}): {msg}", file=sys.stderr)
        if created and not any(out_dir.iterdir()):
            out_dir.rmdir()
        return -1
    kept = 0
    for f in list(out_dir.iterdir()):
        if f.stat().st_size < 5120:
            f.unlink()
        else:
            kept += 1
    if kept == 0 and created:
        out_dir.rmdir()
    return kept


def process(src: Path, out_dir: Path, name: str | None, engine: str) -> None:
    src = src.resolve()
    if not src.exists() or src.suffix.lower() != ".pdf":
        print(f"not a PDF: {src}", file=sys.stderr)
        sys.exit(1)

    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    dest_name = f"{name}.pdf" if name else src.name
    dest_pdf = out_dir / dest_name
    shutil.copy2(str(src), str(dest_pdf))

    if engine == "docling" and not docling_available():
        print("docling is not installed; run extract_pdf_docling.py instead", file=sys.stderr)
        sys.exit(1)

    if engine == "docling":
        md, n_tables = extract_with_docling(dest_pdf, out_dir / "tables")
    else:
        md = extract_markdown(dest_pdf)
        n_tables = extract_tables(dest_pdf, out_dir / "tables")
    (out_dir / "content.md").write_text(md, encoding="utf-8")

    meta = extract_metadata(dest_pdf)
    meta["engine"] = engine
    (out_dir / "metadata.json").write_text(
        json.dumps(meta, indent=2, default=str, ensure_ascii=False),
        encoding="utf-8",
    )

    n_images = extract_images(dest_pdf, out_dir / "images")

    parts = [f"{dest_pdf.stem}: {meta.get('pages', '?')}pp ({engine})"]
    parts.append(f"{n_tables} tables")
    if n_images == -1:
        parts.append("images skipped (no pdfimages)")
    else:
        parts.append(f"{n_images} images")
    parts.append(f"{len(md)} chars markdown")
    print(", ".join(parts))


def main(doc: str = __doc__, default_engine: str = "pymupdf"):
    parser = argparse.ArgumentParser(
        description=doc,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("pdf", type=Path, help="path to the source PDF")
    parser.add_argument("-o", "--output", type=Path, required=True, help="output directory")
    parser.add_argument("--name", help="rename the PDF copy (without .pdf extension)")
    parser.add_argument(
        "--engine",
        choices=("docling", "pymupdf"),
        default=default_engine,
        help=f"text/table engine (default: {default_engine})",
    )
    args = parser.parse_args()
    process(args.pdf, args.output, args.name, args.engine)


if __name__ == "__main__":
    main()
