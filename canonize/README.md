# canonize

Agent skills that keep a computational modeler thinking rigorously and leave a durable, navigable trail behind the work.

The canon is what is currently true for a project, and what is still live in it. The harness maintains it. You decide direction. It recalls and records better than you do, and it does not pretend to think better than you.

## The problem

In modeling, the gap between "I made a decision" and "I wrote down why" is where reproducibility dies. Structural assumptions and the evidence behind them live in someone's head or an orphan notebook. Six months later nobody, including you, can reconstruct why a piece of the model is the way it is, or which sources a claim rests on. And a summary written once drifts out of date the moment the next paper lands.

## The model

The canon is a **wiki**: settled evidence (entries, syntheses, and decisions) reached through tags. What the project knows.

Sources feed the wiki. Decisions are internal sources. Collaborators, and future you, browse the wiki, not the raw files.

## Two ideas worth holding onto

**Cache-lazy, not cache-forward.** There is no pre-baked synthesis sitting in front of the sources to go stale. Syntheses are written only when an answer is worth keeping, and a recorded claim points you to its source. Navigation surfaces (the tag pages, the index) are compiled from frontmatter and never hand-maintained. A hook-maintained `updated` field drives staleness and recency, so a synthesis whose sources have moved is flagged without anyone tracking it.

**Surfaces stay fresh on their own.** A Stop hook keeps the compiled surfaces fresh and runs the conformance check, so opening the project always reads like a wiki, never a flat pile of files.

## Layout

Storage is zone-first. Navigation is tag-first. Rooted at `docs/` by default:

```
docs/
  raw/         raw files (PDFs, datasets). Storage, not knowledge.
  pages/       flat: entry, synthesis, decision. Cross-linked by relative path.
  findings/    analysis results. Located, not typed.
  tags/        one page per tag: authored description, compiled member list.
  index.md     root orientation page
  glossary.md  terms + the compiled tag vocabulary
  settings.json  machine config: extra types, external sources
  CLAUDE.md    conventions and behavior (commit, sourcing, structural sign-off)
```

`index.md` opens with the tags, syntheses, decisions, findings, a "needs review" list, and recent writes. A page joins a tag by its `tags` frontmatter. `tags/<tag>.md` lists every page carrying it. All links are file-relative, so they open by clicking in any markdown viewer.

## Pages

Every page under `pages/` is markdown with YAML frontmatter and a non-empty `type` (`entry`, `synthesis`, `decision`). Findings are located, not typed. The three types are built into the script and extended through `settings.json`, which is also the integration contract for other skill systems: name the type, provide the content. Pages are wiki: revise or delete them in place, and git holds the history.

## The skills

Seven skills, one script.

- **canon**: orientation, the reading disposition, routing, and the deterministic script (`compile`, `check`, `stamp`). Loaded first by every other skill.
- **setup-canon**: bootstrap or adopt a project. Writes `settings.json`, `docs/CLAUDE.md`, the root instruction line, and the scaffold. Adopting is setup plus a batch catalog and a code scan.
- **catalog**: bring a source in. Write its entry to `pages/` with tags and a relevance-to-project section. Reads the source and the tag vocabulary, nothing else, so cost stays flat as the corpus grows.
- **query**: answer a question by diving into the sources on demand. Trace a value to what it rests on. Keep a wide answer as a synthesis.
- **record**: capture a decision or a finding the user wants to bank.
- **curate**: review the knowledge state on demand: contradictions, stale claims, missing syntheses, tag issues. The one place cross-checking happens.
- **build-view**: bespoke dashboards and charts over the canon, on request.

Nothing here depends on another plugin. Where a skill needs a choice it interviews inline, one question per turn with a recommendation. [inquisitry](../inquisitry) has fuller interview skills that compose by being invoked, not required. A plugin that owns `experiments/<track>/` and its STATUS files composes the same way: canon reads those statuses, never writes them.

## Git is the log

One commit per logical write with a structured message (`catalog: <title>`, `record: <title>`, `curate: <what>`). The clock the script reads for staleness and recency is each page's `updated` field, stamped by a hook on every write, never git and never hand-typed.

## Built on

- [Matt Pocock's engineering skills](https://github.com/mattpocock/skills): decisions written down as they crystallize. Documentation is never its own skill.
- [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): a persistent knowledge base an agent reads and maintains, here made cache-lazy so synthesis happens on demand.
