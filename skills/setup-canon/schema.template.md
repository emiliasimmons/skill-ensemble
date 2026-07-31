# project schema

What this bundle's conventions are, for whatever reads it: `canon`, the canonize skills, or a foreign skill system writing pages here. `setup-canon` writes it and fills the bracketed values. To change how the skills behave, tell them what is annoying; they map it to the right setting here.

The project memory is rooted at `<root>/`. Storage is zone-first; navigation is topic-first. Every page is markdown with YAML frontmatter.

## Settings

- substrate_root: [where the memory lives, default docs]
- hub_staleness_nudge: 5
- placeholder_aging_days: 90
- tag_aging_days: 90
- github_wiki_sync: none

`canon` reads these bullets. `hub_staleness_nudge` is how many members a hub may accrue after its `synthesized` date before the state block flags it stale; the aging thresholds bound how long a placeholder DR or an orphan tag may sit before `fixup-docs` surfaces it.

## Structure

```
<root>/
  sources/                       raw source files (PDFs, CSVs). Storage, not knowledge.
  findings/                      analysis results, tagged
  decisions/                     flat, sequential DR-NNNN, tagged
  topics/
    <topic>.md                   the topic hub (type: topic), sibling of its directory
    <topic>/                     member pages: source summaries, concepts
  views/                         compiled HTML, pull-only
  glossary.md
  assumptions.md                 compiled register (accepted decisions)
  open-decisions.md              compiled register (provisional decisions)
  index.md                       root orientation page
  schema.md                      this file
```

Four zones, three postures: `sources/` immutable and human-managed; `findings/` and `decisions/` append-only (append, re-run, or supersede — never quietly rewrite); `topics/` mutable, built incrementally. Topics are coarse — target 8 to 15 for a 150-source project. A topic-zone page has exactly one primary parent (its directory); evidence joins hubs by tag alone, and everything cross-cutting is a tag.

## Frontmatter

Every page carries a YAML frontmatter block:

- **Hard floor: `type`.** A page is conformant with just a non-empty `type`. Never block a page for anything else.
- **Authored core: `type` + `title` + `description`.** `title` is the display label; `description` is the one-line summary that renders in every compiled surface and is the awareness contract — what a reader sees without opening the page.
- **`timestamp`:** stamped once at birth, never hand-maintained. A page without one drops out of the recent-writes block and can never make a hub read as stale.

Format docs name the rest per type. Producers may add any other keys; consumers preserve unknown keys and never reject a page for them.

## Type registry

Adding a type is a registry row plus a format doc, nothing else. The `surfaces` column decides which compiled surfaces a type participates in (`hub` = appears in hub member lists and topic counts; `register` = feeds the registers; `taxonomy` = counts in the taxonomy). A type declaring `hub` becomes hub-visible with no skill or script change. This is the integration contract for foreign skill systems.

| type | zone | mutability | format | surfaces |
|------|------|-----------|--------|----------|
| `decision` | decisions | append-only | record-doc/formats/decision.md | hub, register, taxonomy |
| `finding` | findings | append-only | record-doc/formats/finding.md | hub, taxonomy |
| `source` | topics | mutable | record-doc/formats/source.md | hub, taxonomy |
| `concept` | topics | mutable | record-doc/formats/concept.md | hub, taxonomy |
| `provenance` | topics | mutable | record-doc/formats/provenance.md | hub |
| `topic` | topics | mutable | record-doc/formats/topic.md | |
| `register` | | mutable | record-doc/formats/register.md | |
| `glossary` | | mutable | canon/glossary_format.md | |

Format paths are relative to the canonize skills directory. `mutability` is a default posture, not a law; `record-doc` owns the deliberate-rewrite escape hatch.

## Tag vocabulary

Tags mark cross-cutting themes with 3+ expected members, not keywords. Tags are atomic, composable concepts: `antibiotic`, `resistance`, `modeling` — not `antibiotic-resistance-modeling`. Prefer several narrow tags whose intersection captures the idea over one compound tag that can't recombine. Using an existing tag is free; minting one is unilateral but registered here in the same write, with a gloss. The taxonomy block prints member counts, so a one-member tag is visibly weak. A topic name doubles as the tag that binds evidence to its hub.

| tag | gloss |
|-----|-------|

## Typed relations

Structural links live in frontmatter keys so every compiled surface and `audit-code`'s traversal reads them without parsing bodies: `supersedes`, `bears_on`, `derived_from` (extensible per type via format docs). Prose links remain for reading flow.

## Links and citations

All links are root-anchored from the bundle root (`/decisions/DR-0007.md`), never file-relative. A moved page's outgoing links then survive untouched; only inbound links need repair, which `canon check` finds mechanically. Citations backing a page's claims go under a `# Citations` heading at the bottom, numbered.

## Decision (DR) statuses

provisional, accepted, superseded by DR-NNNN.

## Workspaces

Registered subdirectories under `findings/` where linked repos write their findings, each governed by the same append-only rules. Skills resolve `findings/<name>/` from this list; `setup-canon` registers them in linked mode.

```
workspaces: []
```

When populated:

```
workspaces:
  - name: calib-zim
    description: Zimbabwe calibration
    repo: poc-doxypep-calib
```

## Bundle version

`index.md` frontmatter carries only `okf_version: "0.1"`.
