# canonize

Agent skills that keep a computational modeler thinking rigorously and leave a durable, navigable trail behind every choice.

The project's memory is the authoritative record of what was decided and why: examined, defended, and kept. It grows as you work, appended to but never quietly rewritten.

## The problem

In modeling, the gap between "I made a decision" and "I wrote down why" is where reproducibility dies. Parameter choices, structural assumptions, and the evidence behind them live in someone's head or an orphan notebook. Six months later nobody, including you, can reconstruct why a value is what it is, whether a piece of the model is a considered position or a placeholder, or which parameter set produced a given figure.

The fix is to make capture a cheap, non-optional side effect of the verbs you already want to run, and to keep the reading surfaces current automatically so opening the project always feels like a wiki, never a flat pile of files.

## The one-sentence model

Sources feed the wiki. Decisions are internal sources. Collaborators browse the wiki, not the sources.

## Two ideas worth holding onto

**Improve progressive disclosure; penalize maintenance over reading.** Anything derivable from frontmatter is *compiled* by the `canon` script, never hand-maintained; anything authored is prose a human or agent deliberately wrote. A routine write costs a bounded handful of cheap operations and never re-reads the corpus into context.

**The parameter lifecycle is read, not set.** There is no freeze button. A value with only sources behind it reads as a prior; once a calibration finding exists, it reads as calibrated. The stage is a property the wiki compiles, not a state you advance.

## Layout

Storage is zone-first; navigation is topic-first. Rooted at `docs/` (by default):

```
docs/
  sources/                    raw files (PDFs, CSVs). Flat. Storage, not knowledge.
  findings/                   analysis results, tagged
  decisions/                  model design records (DR-NNNN), flat, tagged
  topics/
    <topic>.md                the topic hub (authored synthesis + compiled member list)
    <topic>/                  member source summaries and concepts
  views/                      compiled interactive views, pull-only
  glossary.md
  assumptions.md              compiled register (accepted decisions)
  open-decisions.md           compiled register (provisional decisions)
  index.md                    root orientation page
  schema.md                   central config + type registry
```

## The disclosure spine

Three navigation surfaces, kept current automatically so a reader never confronts a flat 150-item list:

1. **Root orientation page** (`index.md`) — authored preamble like a wiki landing page, then a compiled taxonomy (every topic and tag with counts), a compiled project-state block (open decisions, stale hubs, recent writes), and compiled links to the per-zone indexes at the bottom.
2. **Topic hubs** (`topics/<name>.md`) — the primary browsing surface: an authored synthesis on top, a compiled member list below cutting across zones.
3. **Leaf pages** — source summaries, findings, decisions, concepts.

Everything cross-cutting is a tag; a page tagged with a topic's name appears in that hub. All links are file-relative (`../decisions/...`, `../findings/...`) so they open by clicking in any markdown viewer.

## Page format

Every page is markdown with YAML frontmatter and a non-empty `type`. Readable without tooling, diffable in git. Types are a **registry** in `schema.md`, not a fixed table — adding a type is a registry row plus a format doc, which is also the integration contract for other skill systems: name the type, provide the content, `record-doc` handles conformance.

## The skills

Seven skills, one pull tool, and one script.

- **setup-canon** — bootstrap, adopt, or link a project; writes the schema, type registry, and root scaffold. Adopting is setup plus one batch ingest.
- **ingest-source** — bring sources and findings in; owns placement (topic + tags); batch mode skims all before placing any. Delegates every write.
- **query-docs** — answer questions and trace values live through the typed relations; read-only; offers to keep an expensive synthesis.
- **record-doc** — the single writing primitive and the integration point; the only skill that writes pages.
- **curate-docs** — review the project's knowledge state: contradictions, stale claims, missing concepts, taxonomy issues, hub rewrites. Conversational.
- **handoff** — compact the current session into a disposable note for a fresh agent to pick up. Save location comes from the `Handoffs` steering setting; defaults to the OS temp dir.
- **build-docs-view** — the wiki at `docs/index.html`, and bespoke dashboards on request.
- **canon** — the deterministic layer (compile, check, fix, sequence). Stdlib only, ships with the skills; a project never needs it.

Nothing here depends on another plugin. Where a skill needs a choice from the user it interviews inline, one question per turn with a recommendation attached; [inquisitry](../inquisitry) has fuller interview and triage skills if you want them, and they compose by being invoked, not by being required.

## Git is the log

One commit per logical write with a structured message (`ingest: <title>`, `record: DR-0021 <title>`, `curate: <what>`)

## Linked repos

A project's `docs/` can be shared across repositories via symlink: the upstream repo owns it in git, linked repos symlink and gitignore it. Each linked repo writes findings to its own registered workspace under `findings/`. Run `setup-canon` in linked mode to set this up.

## Built on

- [Matt Pocock's engineering skills](https://github.com/mattpocock/skills) — decisions written down as they crystallize; documentation is never its own skill.
- [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — a persistent knowledge base that pre-compiles synthesis instead of re-deriving it every time.
- [OKF (Open Knowledge Format)](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) — the page format: markdown with YAML frontmatter, a non-empty `type` on every page.

