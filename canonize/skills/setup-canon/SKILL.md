---
name: setup-canon
description: Bootstrap a canon project, or tune how the skills behave. Use when setting canon up for the first time, or when the user wants to change how the skills work (too chatty, asking too often). Do NOT use for ordinary modeling work. Writes only configuration and the directory scaffold.
disable-model-invocation: true
---

Write `settings.json`, `docs/CLAUDE.md`, the root instruction line, and the directory
scaffold, then explain to the user how to work in it. Start from `settings.template.json`,
`docs-claude.template.md`, and `root-claude.template.md` in this skill's directory, and
load /canon for the directory layout, the page formats, and the script.

## Environment

`uv` runs the hooks and every bundled script, and supplies a Python when the machine has
none. Run `uv --version`. If it fails, tell the user the skills' scripts need it, offer to
install it, and wait for their go-ahead:

```
macOS, Linux, WSL   curl -LsSf https://astral.sh/uv/install.sh | sh
Windows             winget install --id=astral-sh.uv -e
```

Confirm it works by running `canon/canon.py --help` through `uv run --script`.

Check that `git` is on PATH and that `pandoc` is installed (catalog uses it to read `.docx`
files). If either is missing, say what won't work without it and offer to install it,
again waiting for the user's go-ahead.

## Scaffold

Look for an existing agent instructions file and any `docs/` directory first. When `docs/`
already has some of the files below, write only the missing ones, list the ones you left
alone, and never overwrite a file the user wrote. Use the template defaults throughout,
including `docs/` as the canon root. Moving the root later is a one-line edit.

- directories: `docs/raw/`, `docs/pages/`, `docs/findings/`, `docs/tags/`
- `docs/index.md`: the preamble /canon specifies (at scaffold time, the project's question
  and approach, with nothing yet to link), then the note
  `> Compiled from frontmatter, overwritten on the next compile.` Compile writes below the
  note, one `## ` section per non-empty block, in this order: `Tags`, `Syntheses`,
  `Decisions`, `Findings`, `Stale`, `Recent`. Empty blocks get no heading, so a new index
  shows only the preamble and the note until the first page is written. Sections the user
  writes go after the compiled ones. No frontmatter.
- `docs/glossary.md`: a `# Glossary` heading for terms the user writes by hand, then
  a `## Tags` section for the tag vocabulary, opening with this note verbatim:

  ```
  > Please note the formatting here is strict and used for tag page compilation
  ```

  The list under the note starts empty and takes one `- **<tag>**: <description>` per
  tag. No frontmatter.
- `docs/ledger.md`: an empty file. Each heading in it is a thread of work, added when that
  work starts.
- `docs/settings.json` from `settings.template.json`, with its default values and
  `canonize_version` set to the `version` in `../../.claude-plugin/plugin.json`, relative
  to this skill's directory. A session-start hook compares the two to tell when the canon
  needs migrating.
- `docs/CLAUDE.md` from `docs-claude.template.md`.
- root `CLAUDE.md` (or `AGENTS.md` if the repo uses that) from `root-claude.template.md`:
  the one line that loads /canon.
- `docs/.gitignore`, which keeps PDFs and Word files out of git:

  ```
  raw/**/*.pdf
  raw/**/*.docx
  ```

Leave `tags/` empty. Compile generates `tags/<tag>.md` from each tag's glossary line and the
pages that use it.

The three page types (`entry`, `synthesis`, `decision`) are built into the script, and
findings are any page under `findings/`. Do not ask which to enable. To add a custom type,
ask the user what it records, then add a `types` row to `settings.json` and a format doc in
`canon/formats/` once they approve.

Finish by running `compile` to fill in the generated files and `check` to confirm they
conform, then commit `setup: scaffold canon project`.

## Sourcing tools

List the tools this session can reach for finding and reading literature: connected MCP
servers (PubMed, Zotero, Semantic Scholar, OpenAlex, bioRxiv, Crossref, a publisher's
server) and installed skills that search for or fetch papers. Read them off the available
tools without calling them. Use the list only in the closing message and write it to no
file, since the user names the source in each request.

## Closing message

After the commit, send one message covering:

1. The files written, as a short list of paths.
2. How to use the skills: catalog brings a source in as an entry under `pages/`, query
   answers questions from what the canon holds and traces values to their sources, curate
   reviews and repairs the canon, and export builds artifacts for use elsewhere.
3. Sourcing. Give one example request per tool on the list, phrased as the user would type
   it, with what happens next:

   ```
   Can you find the Grabowski 2024 study on OpenAlex?   searched on OpenAlex, open-access full text fetched, cataloged
   Catalog doi:<doi> from PubMed                        metadata and PMC full text pulled, then cataloged
   Catalog the "chlamydia" collection from Zotero       every item in the collection, cataloged as one batch
   ```

   Then describe requests that name no tool. A paper named on its own ("catalog Grabowski
   2024") or a bare DOI is looked up with whatever the session can reach, and the agent
   tries to get the full text. When the lookup finds several candidates or no clear match,
   the agent asks which paper is meant. For a paywalled paper, the agent shows the abstract and asks
   for the PDF. PDFs dropped into `docs/raw/` are cataloged on "catalog the new files in
   raw".
4. Customization. `docs/CLAUDE.md` holds the conventions: cataloging commits once per
   batch, every other write commits on its own, the tag rules, and which changes need the
   user's approval. The user can edit it directly or ask for a change in plain words.
   A standing sourcing preference, such as "pull from Zotero first", goes there too.
   `settings.json` holds the tag aging threshold, extra page types, and check exclusions.
5. That the root load line can be made conditional, as `root-claude.template.md` describes.

End by asking whether the user has questions or wants to start work, for instance by
cataloging a first source.

## Tuning

When the user asks to change how the skills behave, find the file the setting lives in,
change it, and say what changed. Commit granularity, standing sourcing preferences, and
project conventions live in `docs/CLAUDE.md`. The tag aging threshold, extra types, and
external source trees live in `settings.json`. The status of each thread lives in
`docs/ledger.md`. Everything else about how the skills behave lives in the skill files.
