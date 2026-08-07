---
name: canon
description: Project orientation and script usage. Load when writing pages, compiling surfaces, checking conformance, reasoning about the project's structure, or when asked about the docs.
---

# Canon

**First**, always read `docs/index.md` and `docs/glossary.md`.
`docs/index.md` is the navigation entry point: the authored preamble, compiled taxonomy, and state blocks.
`docs/glossary.md` defines project vocabulary.
Read `docs/schema.md` when writing a page, minting a tag, or resolving a workspace.

Index descriptions are awareness contracts, not evidence. When your task reasons about what the docs say (comparing code to literature, flagging gaps, detecting conflicts, grounding a decision in prior work), read the relevant pages under `docs/topics/`. Start from the taxonomy: hub names and tags map to subjects, member lists point to pages. Read the pages, and follow references between them until you have enough context to ground the work.

## Docs layout

Four zones, three postures:

- `docs/sources/` — raw files (PDFs, documents, spreadsheets, slide decks, etc). Immutable, human-managed.
- `docs/findings/` — analysis results, tagged. Append-only. Optionally subdivided by workspace.
- `docs/decisions/` — design records (`DR-NNNN`), flat, tagged. Append-only.
- `docs/topics/` — topic hubs and their member pages, built incrementally.

Storage is zone-first; navigation is topic-first. `topics/<name>.md` is the hub; `topics/<name>/` holds its members. A page joins a hub **by tag**: its home topic (the directory it lives in) is always also a tag, and every other topic it is tagged with lists it in that hub too. Evidence has no single-parent constraint — a decision appears in every hub it is tagged to.

Never edit or create files under `docs/sources/`. Report problems to the user.

## Rewriting a page

A request to rewrite or revise any recorded page routes through /record-doc with that page's format doc loaded, never a direct edit from here. The format doc carries the conformance the rewrite must still meet (frontmatter, typed relations, and for a concept or hub the readable-on-its-own bar); editing the prose without it drops those silently. Load record-doc and the format for the page's type before touching it.

## Compiled blocks

Every navigation surface is compiled from frontmatter and never hand-edited: the taxonomy and state blocks on `index.md`, the member list on each hub, the assumptions and open-decisions registers, the per-zone indexes. Compiled blocks are delimited by `<!-- compiled:NAME -->` … `<!-- /compiled:NAME -->`; only the inner content is regenerated, never the authored prose around it. All links are file-relative to the page carrying them (`../decisions/...`, `../findings/...`).

Evidence is append-only: append, supersede, or re-run — never quietly rewrite.

## The script

```
python3 ${CLAUDE_SKILL_DIR}/canon.py --root <substrate-root> <subcommand>
```

That path resolves here and nowhere else, so a skill that runs the script orients with canon first and carries the resolved path from this block. For the subcommands (compile, check, sequence), read `canon_usage.md` in this skill's directory.

## Naming pages in conversation

The first mention of any page or source from the docs in a reply **must** be formatted as a markdown link to the file (DRs, hubs, summaries, custom sources, etc), with the path relative to the project root. Re-link after a long stretch without mentioning it.

## Explaining what you read

Write for a technical reader who does not have the background you just absorbed from the pages. Cover the substance and stop: no filler sections, no closing summary of what was just said, no boilerplate. Answer what was asked at the scope it was asked, and keep it brief. Prefer ordinary words wherever an ordinary word carries the meaning. Where the field's term is the only one that will do, give it a clause of explanation at first use, in the glossary's wording if it has an entry. Same for a number: its units, and what it is relative to.

Internal links carry the rest. A page in the docs is one click away, so link it and give only what it means for the question at hand. Nothing outside the docs can be relied on that way.

Per sentence: cut it if the user could have written it themselves, or if a link already carries it. Keep what they would otherwise have to go find.

## Glossary

The glossary is the project's shared vocabulary: the terms its pages, code, data, and results are written in. It is what makes a concept or hub readable on its own by a technical reader who does not share the field a source came from.

### When to flag

A term qualifies when all three hold:

- It recurs across the project's pages, code, parameters, or results, not a one-off mention. A cross-field term used once gets defined inline where it appears, not an entry.
- Its meaning is not self-evident to a technical reader who may not work in the field the term comes from.
- It is specific to this project, or standard within one field but opaque outside it. A term general to every technical reader needs no entry.

### Conflicts and ambiguity

When a term conflicts with an existing glossary entry, call it out: "The glossary defines X as Y, but here you seem to mean Z — which is it?"

When a term is vague or overloaded, propose a precise canonical form before it enters the vocabulary: "You're saying 'rate' — the transmission rate or the recovery rate?"

### Writing

On resolution, edit `docs/glossary.md` directly. One or two sentences defining what the term IS in this project. Write the entry when it settles, don't batch.

## When to recommend recording a decision

Never record a decision autonomously. When a choice meets any of the criteria below, pause and recommend recording it, then wait for the user's go-ahead.

- **Non-obvious justification:** An independent reviewer would need to ask *why* this path was taken. It is not self-evident or forced.
- **No precedent:** The choice cannot be justified by literature, established frameworks, or existing project sources.
- **No field consensus:** The approach is not an accepted standard in the relevant scientific or computational community.

When recommending, state the decision, why it qualifies, and a suggested one-line rationale, so the user can approve or edit rather than compose from scratch.

> **Rule of thumb:** If a peer would need an explicit justification to replicate or validate the logic, recommend recording it.

A provisional decision is legitimate when the choice is forced and the rationale is thin.
