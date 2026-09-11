---
name: setup-canon
description: Bootstrap a canon project, or tune how the skills behave. Use when setting canon up for the first time, or when the user wants to change how the skills work (too chatty, asking too often). Do NOT use for ordinary modeling work. This skill only writes the config layer and scaffold.
disable-model-invocation: true
---

Write `settings.json`, `docs/CLAUDE.md`, the root instruction line, and the directory
scaffold. Start from `settings.template.json`, `docs-claude.template.md`, and
`root-claude.template.md` in this skill's directory, and load /canon for the layout and
function, the formats, and the script.

## Environment

`uv` launches the hooks and every bundled script, and supplies a Python when the machine
has none. Run `uv --version`. On failure, explain what it unblocks, offer the install, and
wait for approval:

```
macOS, Linux, WSL   curl -LsSf https://astral.sh/uv/install.sh | sh
Windows             winget install --id=astral-sh.uv -e
```

Confirm it by running `canon/canon.py --help` through `uv run --script`.

Check `git` on PATH, `pandoc` for docx extraction, and whether `docling` imports. Carry
the docling result into the PDF extraction question below. Report closed routes and offer
the install. Install nothing unasked.

## Questions

Before asking, look for an existing agent instructions file and any `docs/` directory. When
`docs/` already carries canon surfaces, write only the ones missing and report the rest,
never overwriting an authored file. Then put these three in one message and wait. Each
answer is recorded in `docs/CLAUDE.md`.

- **PDF extraction.** Basic extraction (pymupdf) interleaves two-column papers, drops
  running headers into sentences, and fragments tables. Docling reconstructs reading order
  and table structure with a layout model, at the cost of a ~1 GB install and a model
  download on first use. Approve docling now, or start basic and switch per-source when an
  extraction comes out garbled. Recorded under `## Sourcing`.
- **Commits.** Cataloging commits once per batch by default, or per source as each is
  written. Batch recommended. Every other write (curate, query, a decision or finding)
  commits per logical write. Or name a custom behavior, such as staging everything for
  review. Recorded under `## Commit`.
- **Academic sourcing.** Whether the user has a preferred way to bring in academic works
  (a Zotero library, OpenAlex, a reference-manager export, dropping PDFs into `raw/`), so
  catalog reaches for it first. Recorded under `## Sourcing`.

Everything else takes template defaults: root `docs`, `wiki: false`. The wiki or a
non-default root is a one-line edit the user can ask for later.

## Scaffold

- directories: `docs/raw/`, `docs/pages/`, `docs/findings/`, `docs/tags/`
- `docs/index.md`: the preamble /canon specifies (at scaffold time, the project's question
  and approach, with nothing yet to link), then the region note
  (`> Compiled from frontmatter, overwritten on the next compile.`). Compile fills the run
  below it, one `## ` section per non-empty block, in reading order: `Tags`, `Syntheses`,
  `Decisions`, `Findings`, `Stale`, `Recent`. An empty block gets no heading, so a fresh
  scaffold reads as the preamble and the note alone until the first page lands. Any
  authored section goes after the run. No frontmatter.
- `docs/glossary.md`: a `# Glossary` heading, hand-edited terms, then a `## Tags` section
  for the tag vocabulary, opening with this note verbatim:

  ```
  > Please note the formatting here is strict and used for tag page compilation
  ```

  The list under the note starts empty and takes one `- **<tag>**: <description>` per
  tag. No frontmatter.
- `docs/ledger.md`: an empty file. Each header is a thread, added as work starts.
- `docs/settings.json` from `settings.template.json`, values filled.
- `docs/CLAUDE.md` from `docs-claude.template.md`, with the three answers recorded.
- root `CLAUDE.md` (or `AGENTS.md` if the repo uses that) from `root-claude.template.md`:
  the one line that loads /canon.
- `docs/.gitignore`: the HTML wiki is generated, so it stays out of history:

  ```
  raw/**/*.pdf
  raw/**/*.docx
  index.html
  views/wiki/*
  !views/wiki/custom.css
  ```

Leave `tags/` empty. Compile generates `tags/<tag>.md` from each tag's glossary line and the
pages that use it.

The three types (`entry`, `synthesis`, `decision`) are built into the script, and findings
are any page under `findings/`. Do not ask which to enable. Custom types are a short
interview on what they record, then a `types` row in `settings.json` plus a format doc in
`canon/formats/`, with sign-off.

Finish by running `compile` to populate the compiled surfaces and `check` to confirm
conformance, then commit `setup: scaffold canon project`.

## Tuning

Take the complaint in plain words, map it to its home, change it, and say what changed.
Commit granularity, sourcing route, and project conventions live in `docs/CLAUDE.md`. The
tag aging threshold, the wiki toggle, extra types, and external source trees live in
`settings.json`. Where a thread stands lives in `docs/ledger.md`. How the skills behave
lives in the skill files.
