---
name: setup-canon
description: Bootstrap a canon project, adopt an existing one, link a repo to a shared evidence trail, or tune how the skills behave. Use when setting canon up for the first time, adopting a project that already has sources or code, linking to another project's docs, or when the user wants to change how the skills work (too chatty, asking too often). Do NOT use for ordinary modeling work; this skill only writes the config layer and scaffold.
disable-model-invocation: true
---

Writes `schema.md`, the root orientation page, the directory scaffold, and the `## docs` steering block. Start from `schema.template.md` and `steering.template.md` in this skill's directory, and load /canon for the layout and the script. Load /record-doc for the register and other format specs.

Three modes: **new project**, **adopt**, **linked**.

## New project

Explore first. Look before asking: existing agent instructions file, git remote, any `docs/` directory. Present what you found, then ask only what you could not work out, one question at a time:

- Where in this repo the memory lives (sets `substrate_root`, default `docs`).
- Whether to enable GitHub wiki sync, if the repo has a GitHub remote (optional).
- Commits: commit each write automatically, or stage for review.
- Handoffs: save to a local directory or the OS temp dir. If local, whether to gitignore handoff files.

Use `schema.template.md` defaults for everything else.

Scaffold the tree up front:

- directories: `docs/sources/`, `docs/findings/`, `docs/decisions/`, `docs/topics/`, `docs/views/`
- `docs/index.md`: `okf_version: "0.1"` frontmatter (its only frontmatter), a short authored preamble written like a wiki landing page, then the compiled markers `<!-- compiled:taxonomy -->…<!-- /compiled:taxonomy -->` and `<!-- compiled:state -->…<!-- /compiled:state -->`, then links to the registers and glossary, then `<!-- compiled:zones -->…<!-- /compiled:zones -->` at the bottom under a "Browse by zone" heading
- `docs/assumptions.md`, `docs/open-decisions.md` — registers scaffolded with a `<!-- compiled:register -->` block each (format: `record-doc/formats/register.md`)
- `docs/glossary.md` — scaffolded per `canon/glossary_format.md`
- `docs/schema.md` from the template, with the chosen values filled and an empty `## Tag vocabulary` table
- `docs/.gitignore` — the wiki is generated on every compile, so it stays out of history:

  ```
  index.html
  views/wiki/*
  !views/wiki/custom.css
  ```

The template's type registry ships whole; do not ask the user which types to enable. Custom types are not minted here unless asked — that is a brief /grilling session on what the type captures, then a registry row plus a format doc, with sign-off.

Finish: run /canon compile to populate the empty spine, /canon check to confirm conformance, write the steering block, and commit `setup: scaffold canon project`.

If the project already has sources, code, or undocumented decisions, go to adopt.

## Adopt

The new-project scaffold followed by a structured ingest and (when code exists) a decision extraction. All commits follow the preference set during scaffold (auto or confirm).

1. **Scaffold.** Run the new-project flow above.
2. **Commit** `setup: scaffold canon project`.
3. **Gather materials.** If `sources/` is empty, prompt the user to add materials (academic article PDFs, a BibTeX bibliography export, datasets, code pointers) and wait.
4. **Preprocess.** Run gated preprocessing on all sources per /ingest-source (PDF extraction, BibTeX parsing). Everything downstream works from the extracted content.
5. **Propose taxonomy.** With no topics yet, scan extracted content and cluster by subject. The placement plan's clusters *are* the proposed topic set. Present each proposed topic with the sources that would land in it. Get approval before proceeding.
6. **Commit** taxonomy and extracted materials.
7. **Ingest.** Ask the user's preference: one-by-one in chat, subagent dispatch across topic areas, or silent draft with review at the end. Suggest based on the number and type mix of sources. If the session is long or taxonomy negotiation was involved, offer a /handoff before starting; it captures the approved taxonomy, commit preference, and the source list with proposed placements.
8. **Commit** ingestion.
9. **Scan code** (skip if the project has no code). Read the codebase for unrecorded decisions and findings: hardcoded values, structural choices, algorithm selections, boundary conditions, calibration outputs, validation results. Read relevant topic pages to compare code values and citations against ingested evidence. Output a table:

   | # | Type | Item | Location | Confidence | Why it matters |
   |---|------|------|----------|------------|----------------|

   Type is any registered type from the project's schema (commonly `decision`, `finding`, `provenance`). Suggest the best-fit type per item. Confidence is one of: `clear` (obviously deliberate), `likely` (probably intentional but alternatives exist), `unclear` (could be accidental or a default). After the table, suggest any tags the code reveals that the taxonomy doesn't yet cover. Flag conflicts between code behavior and just-ingested sources separately.

   If ingestion was substantial, offer a /handoff before this step. If 3+ items are `unclear` or have plausible competing alternatives, suggest a /grilling session to settle them.
10. **Triage.** The user approves, merges, defers, or drops items from the table. Deferred items land in open-decisions.
11. **Record** approved items through /record-doc, each under its type. **Commit.**
12. **Curate** (optional). Offer a /curate-docs pass focused on missing concepts: sources and code-extracted items are now side by side for the first time, but the concept layer connecting them is empty. Curate-docs will propose concepts that bridge code decisions to literature, shared abstractions across sources, and terms the project uses without defining. Skip if the corpus is small (under ~5 pages) and no cross-cutting themes emerged. This is the tail of a long flow; offer a /handoff rather than running curation inline if the session warrants it.

## Linked

Use when this repo should share another project's evidence trail ("link to ../poc-doxypep", "set this up as a calibration repo for …"). Do not assume the purpose; the workspace might be calibration, sensitivity analysis, presentations, or anything.

Explore first: does the upstream `docs/` exist with a `schema.md`; does this repo already have a `docs/` or symlink; what other skill systems or plugins are loaded. Then ask, one at a time:

1. **Upstream project** — the upstream root (e.g. `../poc-doxypep`); the symlink targets `<upstream>/docs/`.
2. **Workspace name** — a short slug from the repo name; becomes `findings/<name>/`.
3. **Workspace description** — one line.

Then:

1. Symlink `docs/ -> <upstream>/docs/`.
2. Add `docs` to `.gitignore` (the upstream tracks it).
3. Create `docs/findings/<workspace>/`.
4. Register the workspace in the shared `schema.md` `workspaces` list (name, description, repo).
5. Write the steering block noting the shared path, the workspace, and any other loaded skill systems.
6. Commit `setup: link workspace <workspace>`.

Do not scaffold zones or write a new schema — the upstream owns them.

## Tuning (any mode)

Take the complaint in plain words, map it to its setting (commit and handoff behavior live in the steering block; thresholds and types live in `schema.md`; skill behavior lives in the skill file), change it, and say what changed.
