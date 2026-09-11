#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""PostToolUse hook: stamp `updated` on the canon page just written.

`stamp_file` no-ops on any path that is not a canon page, so nothing here decides what a
page is. Always exits 0, so it cannot fail the write it follows.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_CANON = Path(__file__).resolve().parent.parent / "skills" / "canon"
sys.path.insert(0, str(_CANON))


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0
    path = (payload.get("tool_input") or {}).get("file_path") or ""
    if not path:
        return 0
    try:
        # imported here so a missing or broken canon.py is swallowed like any other
        # failure, rather than tracebacking out before this function can catch it
        from canon import stamp_file
        stamp_file(Path(path))
    except Exception:
        pass  # a write must never fail on its bookkeeping
    return 0


if __name__ == "__main__":
    sys.exit(main())
