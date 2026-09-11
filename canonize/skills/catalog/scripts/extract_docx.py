#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Convert a .docx to markdown, keeping tracked changes and extracted media.

Usage:

    uv run extract_docx.py document.docx docs/raw/<slug>/

A document with embedded images becomes `<outdir>/<name>/contents.md` beside a `media/`
directory. One without becomes `<outdir>/<name>.md`.

Requires pandoc on PATH.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def convert(docx: Path, outdir: Path) -> str:
    name = docx.stem
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        # pandoc resolves --extract-media relative to the working directory, so it runs
        # in the temp dir and the results move into place once the shape is known.
        subprocess.run(
            ["pandoc", str(docx), "-t", "markdown", "--wrap=none",
             "--track-changes=all", "--extract-media=media", "-o", "contents.md"],
            cwd=work, check=True,
        )
        outdir.mkdir(parents=True, exist_ok=True)
        media = work / "media"
        if media.is_dir() and any(media.iterdir()):
            dest = outdir / name
            dest.mkdir(parents=True, exist_ok=True)
            shutil.move(str(work / "contents.md"), str(dest / "contents.md"))
            shutil.move(str(media), str(dest / "media"))
            return f"{name}: folder output (contents.md + media/)"
        shutil.move(str(work / "contents.md"), str(outdir / f"{name}.md"))
        return f"{name}: single file output"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="extract_docx", description=__doc__)
    parser.add_argument("docx", type=Path)
    parser.add_argument("outdir", type=Path)
    args = parser.parse_args(argv)

    if not shutil.which("pandoc"):
        print("pandoc not found", file=sys.stderr)
        return 1
    if not args.docx.is_file():
        print(f"{args.docx} is not a file", file=sys.stderr)
        return 1

    try:
        print(convert(args.docx.resolve(), args.outdir))
    except subprocess.CalledProcessError as exc:
        print(f"pandoc failed ({exc.returncode})", file=sys.stderr)
        return exc.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
