#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Stop hook: keep the compiled surfaces fresh and gate conformance.

No-op unless the cwd holds a canon with uncommitted work under its root, so it costs
nothing in unrelated sessions. A blocking conformance error stops the agent to fix it
once. A second firing (stop_hook_active) falls back to advisory so it cannot loop.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

CANON = Path(__file__).resolve().parent.parent / "skills" / "canon" / "canon.py"


def _is_canon(path: Path) -> bool:
    index = path / "index.md"
    if not (path / "settings.json").is_file() or not index.is_file():
        return False
    try:
        return any(line.startswith(">")
                   for line in index.read_text(encoding="utf-8").splitlines())
    except OSError:
        return False


def _find_root() -> Path | None:
    override = os.environ.get("CANON_ROOT")
    if override:
        root = Path(override)
        return root if _is_canon(root) else None
    cwd = Path.cwd()
    try:
        subdirs = sorted(p for p in cwd.iterdir() if p.is_dir())
    except OSError:
        subdirs = []
    return next((c for c in (cwd / "docs", cwd, *subdirs) if _is_canon(c)), None)


def _has_uncommitted(root: Path) -> bool:
    """A tree git cannot read has nothing to gate on, so it always compiles.

    git is asked from inside the resolved root, so a linked canon (docs/ a gitignored
    symlink into the upstream repo) is inspected in the repo that actually tracks it.
    """
    def git(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(root), *args],
                              capture_output=True, text=True)
    try:
        if git("rev-parse", "--is-inside-work-tree").returncode != 0:
            return True
        return bool(git("status", "--porcelain", "--", ".").stdout.strip())
    except OSError:
        return True


def _canon(root: Path, *args: str) -> tuple[int, str]:
    done = subprocess.run([sys.executable, str(CANON), "--root", str(root), *args],
                          capture_output=True, text=True)
    return done.returncode, (done.stdout + done.stderr).strip()


def main() -> int:
    if not CANON.is_file():
        return 0
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        payload = {}

    root = _find_root()
    if root is None or not _has_uncommitted(root):
        return 0

    compiled = _canon(root, "compile")[1]
    failed, checked = _canon(root, "check")

    if failed and not payload.get("stop_hook_active"):
        print(json.dumps({"decision": "block",
                          "reason": f"canon: fix these before finishing.\n{checked}"}))
        return 0

    advisory = [text for text, quiet in ((compiled, "compiled: no changes"),
                                         (checked, "check: clean"))
                if not text.startswith(quiet)]
    if advisory:
        print(json.dumps({"systemMessage": "canon (uncommitted): " + "\n".join(advisory)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
