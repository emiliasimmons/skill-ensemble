# canon.py usage

## Invoking the script

Resolve `canon.py` relative to this skill's directory and run it against the project's substrate root (default `docs`, set in `schema.md`):

```
python3 <canon-skill-path>/canon.py --root <substrate-root> <subcommand>
```

## Subcommands

### compile — regenerate compiled blocks from frontmatter

Incremental (named blocks) in the routine write path; full-corpus (`all`, the default) as a maintenance repair. Recompiling an unchanged corpus writes nothing.

```
--block members --page <hub> …    one or more hubs a written page joined
--block taxonomy --block state    the root, after any page write
--block registers                 after any decision write or supersession
--block indexes --block zones     the per-zone index files, and the root's
                                   links to them; only after a page lands in
                                   a zone that had none
--block views                     bespoke views under `docs/views/`
                                   (no flag = full recompile of everything)
```

One call carries several `--block`/`--page` flags. The wiki at `docs/index.html` rebuilds on every compile whatever the flags say.

### check — conformance and link integrity

```
--frontmatter    every page has a type; authored core and birth timestamp
                 present; type is registered; every hub-surfacing page lands
                 in some hub
--links          file-relative links resolve; root-anchored .md links flagged;
                 links from registered external sources into the bundle resolve
                 (no flag = both)
```

Non-zero exit on a blocking issue.

### sequence — hand out the next id

```
--kind decision    prints the next DR-NNNN atomically
```

Never pick a DR number by hand.

## What it reads

`schema.md` at the substrate root: the `## Settings` bullets, the `## Type registry` table, the `## Tag vocabulary` table, and the `## External sources` block (trees outside the bundle whose links into it are checked, and which the wiki renders). The registry's `surfaces` column drives which types appear in hub member lists and taxonomy counts, so a new type becomes hub-visible with a registry row and no code change.
