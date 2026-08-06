#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pymupdf4llm>=0.0.17",
#     "pymupdf>=1.25",
#     "pypdf>=4.0",
#     "pdfplumber>=0.11",
#     "pandas>=2.0",
#     "docling>=2.15",
# ]
# ///
"""Extract an academic PDF with the docling layout model.

Usage:
    uv run extract_pdf_docling.py paper.pdf -o outdir/
    uv run extract_pdf_docling.py paper.pdf -o outdir/ --name smith2022

Same output as extract_pdf.py, but content.md and tables/ come from a layout model
instead of pymupdf4llm and pdfplumber. That recovers two-column reading order
(reference lists in particular), keeps running headers out of the body text, and
holds table cells together instead of slicing them into character fragments.

Costs about 1 GB of dependencies, a model download on first run, and roughly 30
seconds of inference on a long PDF.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True  # keep __pycache__ out of the installed skill
sys.path.insert(0, str(Path(__file__).parent))

from extract_pdf import main  # noqa: E402

if __name__ == "__main__":
    main(doc=__doc__, default_engine="docling")
