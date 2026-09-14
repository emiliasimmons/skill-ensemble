#!/usr/bin/env python3
"""claims_to_table: turn a markdown file of claims into csv and xlsx.

Input is one `## ` block per row, with `key: value` lines under it. The heading
becomes the first column, the keys become the rest, in the order they first
appear. A line that is neither blank nor `key: value` continues the value above
it, so a long claim can wrap.

    ## smith-2022-tetm
    value: 100% tetM by frequency
    population: 412 isolates, Harare, 2019-2021
    page: pages/smith-2022.md
    source: 10.1000/xyz

    python3 claims_to_table.py claims.md --out-dir .

Writes `<stem>.csv` always. Writes `<stem>.xlsx` when openpyxl is importable,
and says so when it is not. Datasets whose shape does not suit this file write
their own converter into the export directory.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

_HEADING_RE = re.compile(r"^##\s+(?P<name>.+?)\s*$")
_FIELD_RE = re.compile(r"^(?P<key>[A-Za-z][A-Za-z0-9 _-]*):\s*(?P<value>.*)$")


def parse(text: str, id_column: str) -> tuple[list[str], list[dict]]:
    columns: list[str] = [id_column]
    rows: list[dict] = []
    current: dict | None = None
    last_key: str | None = None

    for line in text.splitlines():
        heading = _HEADING_RE.match(line)
        if heading:
            current = {id_column: heading.group("name")}
            rows.append(current)
            last_key = None
            continue
        if current is None or not line.strip():
            last_key = None
            continue
        field = _FIELD_RE.match(line.strip())
        if field:
            key, value = field.group("key").strip(), field.group("value").strip()
            if key not in columns:
                columns.append(key)
            current[key] = value
            last_key = key
        elif last_key:
            current[last_key] = f"{current[last_key]} {line.strip()}".strip()

    return columns, rows


def write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({c: row.get(c, "") for c in columns})


def write_xlsx(path: Path, columns: list[str], rows: list[dict]) -> bool:
    try:
        from openpyxl import Workbook
    except ImportError:
        return False
    book = Workbook()
    sheet = book.active
    sheet.title = "claims"
    sheet.append(columns)
    for row in rows:
        sheet.append([row.get(c, "") for c in columns])
    for i, column in enumerate(columns, start=1):
        width = max([len(column)] + [len(str(r.get(column, ""))) for r in rows])
        sheet.column_dimensions[sheet.cell(row=1, column=i).column_letter].width = \
            min(max(width + 2, 10), 60)
    sheet.freeze_panes = "A2"
    book.save(path)
    return True


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", help="the markdown file of claims")
    ap.add_argument("--out-dir", default="", help="output directory (default: beside input)")
    ap.add_argument("--id-column", default="claim", help="name for the heading column")
    args = ap.parse_args(argv)

    src = Path(args.input)
    if not src.is_file():
        print(f"no such file: {src}", file=sys.stderr)
        return 1

    columns, rows = parse(src.read_text(encoding="utf-8"), args.id_column)
    if not rows:
        print(f"{src}: no `## ` blocks found", file=sys.stderr)
        return 1

    out_dir = Path(args.out_dir) if args.out_dir else src.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / f"{src.stem}.csv"
    write_csv(csv_path, columns, rows)
    print(f"{csv_path}: {len(rows)} rows, {len(columns)} columns")

    xlsx_path = out_dir / f"{src.stem}.xlsx"
    if write_xlsx(xlsx_path, columns, rows):
        print(f"{xlsx_path}: written")
    else:
        print("openpyxl not importable, so no xlsx was written")

    missing = [c for c in columns if sum(1 for r in rows if r.get(c)) < len(rows)]
    if missing:
        print("columns not filled on every row: " + ", ".join(missing), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
