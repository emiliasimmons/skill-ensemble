# canon.py usage

The invocation is in `SKILL.md`. This file is the subcommand reference.

## compile: regenerate compiled surfaces

Full-canon (`all`, the default) is the normal call. The Stop hook runs it, and recompiling
an unchanged canon writes nothing. Named blocks scope a manual run.

```
--block root      index.md: tags, syntheses, decisions, findings,
                  stale, and recent
--block tags      tags/<tag>.md, one per tag. Prunes pages for retired tags
                  (no flag = both)
```

Staleness and recency read each page's `updated` field, which the PostToolUse hook
maintains on every write.

## check: conformance and link integrity

```
--frontmatter    pages/ pages have a type, registered, with authored core,
                 updated, and at least one tag, every tag declared in the
                 glossary. Findings share the identity floor (title,
                 description, updated, tags) but carry no type. index.md
                 keeps its region note
--links          file-relative links resolve. Root-anchored .md links flagged.
                 Links from registered external trees into the canon resolve
                 (no flag = both)
```

Non-zero exit on a blocking issue (missing type, an undeclared tag, broken or anchored
link). Thin tags, missing descriptions, and near-duplicate tags are warnings and do not
block. `check` is the gate before a commit: compile first so the surfaces match the pages,
then check.

## stamp: set a page's `updated` to now

```
stamp <path>    rewrites the page's `updated` field to the current time
```

The PostToolUse hook runs this after every Write and Edit. It no-ops on any path that is
not a canon page (no frontmatter, or outside `pages/`/`findings/`), so it is safe to fire
on every file the agent touches. Nothing else writes `updated`.

## What it reads

`settings.json` at the substrate root, three keys:

- `tag_aging_days` (default 90): a tag with fewer than two member pages, all of them older than this, draws a `check` warning to retire or grow it. A thin tag on its own does not warn, and neither does an old well-populated one.
- `types`: page types beyond the built-ins. Each row names its `type`, its `zone` (the directory it lives in), and its `format` doc.
- `check`: what the walk covers, in two lists. See below.

The three page types (`entry`, `synthesis`, `decision`, all under `pages/`) are built into
the script, so a project only lists types it adds. The tag vocabulary is not config. It is
read from the `## Tags` list in `glossary.md`, one `- **<tag>**: <description>` per line.
Findings (`findings/`) are located, not typed.

`--root` is a flag on the script, not a key in this file.

## What the walk covers

```json
"check": {
  "ignore": ["export"],
  "add": ["../other-repo/experiments"]
}
```

`ignore` holds paths under the root, files or directories, that neither `compile` nor
`check` walks. `raw/` and `tags/` are skipped without being listed. A project scaffolds
with `export` here: an export bundle copies pages with their frontmatter intact, and
without the entry those copies land in the index's recent list beside the originals.

`add` holds trees outside the root, each path relative to the project root. `check --links`
walks their markdown, finds the links aimed into the canon, and reports the ones that no
longer resolve, so an experiment README citing a page breaks loudly after a rename.
