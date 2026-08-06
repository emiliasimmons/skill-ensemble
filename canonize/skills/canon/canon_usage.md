# canon.py usage

The invocation is in `SKILL.md`. This file is the subcommand reference.

## compile — regenerate compiled blocks from frontmatter

Incremental (named blocks) in the routine write path; full-corpus (`all`, the default) after bulk changes.
Recompiling an unchanged corpus writes nothing.

```
--block members --page <hub> …    one or more hubs a written page joined
--block taxonomy --block state    the root, after any page write
--block registers                 after any decision write or supersession
--block indexes --block zones     the per-zone index files, and the root's
                                   links to them; only after a page lands in
                                   a zone that had none
--block sources                   the roster pages for registered external
                                   trees, after one gains or loses files
--block views                     bespoke views under `docs/views/`
                                   (no flag = full recompile of everything)
```

One call carries several `--block`/`--page` flags. The wiki at `docs/index.html` rebuilds on every compile whatever the flags say, then `docs/views/*/refresh.py` runs so bespoke views follow the pages that just landed.

## check — conformance and link integrity

```
--frontmatter    every page has a type; authored core and birth timestamp
                 present; type is registered; every hub-surfacing page lands
                 in some hub; tag vocabulary is clean and placeholders have
                 not aged out
--links          file-relative links resolve; root-anchored .md links flagged;
                 links from registered external sources into the bundle resolve
                 (no flag = both)
```

Non-zero exit on a blocking issue; tag and placeholder problems warn without blocking.

`check` is the gate before a commit. Compile first so the surfaces match the pages, then check, then commit.

## sequence — hand out the next id

```
--kind decision    prints the next DR-NNNN atomically
```

Never pick a DR number by hand.

## What it reads

`schema.md` at the substrate root: the `## Settings` bullets, the `## Type registry` table, the `## Tag vocabulary` table, and the `## External sources` block. The registry's `surfaces` column drives which types appear in hub member lists and taxonomy counts, so a new type becomes hub-visible with a registry row and no code change.

## External sources

Trees outside the bundle whose links into it are checked, and which the wiki renders as nodes:

```
sources:
  - name: experiments
    root: ../other-repo/experiments
    include: README.md=experiment, SUMMARY.md=summary
```

`root` is relative to the project root. `include` maps a filename to the node type it becomes. A row may also set `collector` (`tree` by default, `canon` for a second conformant bundle) and `prefix` (the node-id namespace, the source name by default).

`compile` writes each registered tree a roster page at `docs/<name>.md` and lists it from the index, so the outside files hang off a page in the corpus rather than off the side of the graph. The roster is compiled; the prose above it is not. Links resolve across sources by filesystem path, so a page and an outside file that link to each other become an edge in both directions.

For a source neither collector handles, write a function in `collectors.py` returning `Doc` records and register it in `COLLECTORS`.

## The wiki

`docs/index.html` is the bundle's reading surface: a knowledge graph and file browser over the corpus, rebuilt by every compile. `graph.py --root <substrate-root>` rebuilds it alone. Data goes to `docs/views/wiki/corpus.js`; the viewer under `view/` is referenced, not copied, and nothing reaches the network at view time.

A project overrides its styling with `docs/views/wiki/custom.css`, which loads after the stylesheet.

`graph.py --root <substrate-root> --bundle` copies the viewer assets and every referenced image under `docs/views/wiki/` and rewrites the paths, making `docs/` self-contained at the cost of its size (roughly 8 MB for a corpus with a few dozen figures). Use it to hand the bundle to someone else; the next compile reverts to referenced assets.
