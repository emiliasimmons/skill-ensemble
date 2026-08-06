#!/usr/bin/env bash
set -euo pipefail

if ! command -v pandoc &>/dev/null; then
  echo "pandoc not found" >&2
  exit 1
fi

if [ $# -lt 2 ]; then
  echo "usage: extract_docx.sh <file.docx> <outdir>" >&2
  exit 1
fi

DOCX="$(realpath "$1")"
OUTDIR="$2"
NAME="$(basename "${DOCX%.docx}")"

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

( cd "$TMPDIR" && pandoc "$DOCX" \
  -t markdown \
  --wrap=none \
  --track-changes=all \
  --extract-media=media \
  -o contents.md )

mkdir -p "$OUTDIR"

if [ -n "$(ls -A "$TMPDIR/media" 2>/dev/null)" ]; then
  DEST="$OUTDIR/$NAME"
  mkdir -p "$DEST"
  mv "$TMPDIR/contents.md" "$DEST/contents.md"
  mv "$TMPDIR/media" "$DEST/media"
  echo "$NAME: folder output (contents.md + media/)"
else
  mv "$TMPDIR/contents.md" "$OUTDIR/$NAME.md"
  echo "$NAME: single file output"
fi
