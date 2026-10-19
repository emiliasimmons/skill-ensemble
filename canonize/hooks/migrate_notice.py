#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""SessionStart hook: hand the agent the migration steps a canon is behind on.

Compares `canonize_version` in the canon's settings.json with the plugin's version and
passes every step from MIGRATIONS.md for the releases in between. A canon with no recorded
version predates versioning and counts as 0.1.0.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from stop_compile import _find_root  # noqa: E402

BASELINE = "0.1.0"
_RELEASE_RE = re.compile(r"^## (\d+\.\d+\.\d+)\s*$", re.MULTILINE)

INSTRUCTIONS = """\
In your first reply, before other work, tell the user canonize updated from {old} to \
{new}, list each step below with its level in a line or two, and ask whether to dispatch \
a subagent to perform them. With more than two steps, ask with AskUserQuestion, one \
multiSelect option per step. Give the subagent the chosen steps verbatim and the canon \
root `{root}`. Make no writes to the canon until the user has decided on any Required \
step. Once the user has decided and the chosen steps are done, set `canonize_version` in \
`{settings}` to "{new}" and commit `migrate: <what changed>`. If the user declined a \
Required step, leave `canonize_version` as it is, so the steps are offered again next \
session.

{steps}"""

NO_STEPS = """\
canonize updated from {old} to {new}, with no migration steps. Set `canonize_version` in \
`{settings}` to "{new}" and mention the update to the user in one line."""


def _version(text: str) -> tuple[int, ...]:
    return tuple(int(n) for n in text.split("."))


def _steps(guide: str, old: str, new: str) -> str:
    """Release sections with old < version <= new, newest first as the guide lists them."""
    parts = _RELEASE_RE.split(guide)
    sections = []
    for version, body in zip(parts[1::2], parts[2::2]):
        if _version(old) < _version(version) <= _version(new) and body.strip():
            sections.append(f"## {version}\n\n{body.strip()}")
    return "\n\n".join(sections)


def main() -> int:
    root = _find_root()
    if root is None:
        return 0
    settings = root / "settings.json"
    try:
        new = json.loads((PLUGIN / ".claude-plugin" / "plugin.json")
                         .read_text(encoding="utf-8"))["version"]
        old = json.loads(settings.read_text(encoding="utf-8")).get("canonize_version") \
            or BASELINE
        if _version(old) >= _version(new):
            return 0
        guide = (PLUGIN / "MIGRATIONS.md").read_text(encoding="utf-8")
    except (OSError, ValueError, KeyError):
        return 0

    steps = _steps(guide, old, new)
    template = INSTRUCTIONS if steps else NO_STEPS
    context = template.format(old=old, new=new, root=root, settings=settings, steps=steps)
    print(json.dumps({
        "systemMessage": f"canonize updated {old} → {new}"
                         + (": migration steps pending" if steps else ""),
        "hookSpecificOutput": {"hookEventName": "SessionStart",
                               "additionalContext": context},
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
