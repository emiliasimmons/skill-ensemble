---
name: curate
description: Review the project's knowledge state and repair it. Syntheses the literature on hand supports but nobody wrote, gaps between what the project needs and what it holds, upkeep of stale pages and the ledger, and descriptions that no longer match their pages. Conversational, every change needs sign-off. Use to curate, to review part of the canon after material accumulates, or when the canon comes up empty on questions it should answer.
---

**First**, orient with /canon.

Curating reviews the state of the project's knowledge rather than using it to answer
a question. It reads what the canon holds against what the project needs, and comes back
with recommendations for the user to pick from. Much of the work routes elsewhere. Topics
for synthesis are recommended as questions for /query, which does the reading and offers
the page. Gaps in the evidence are recommended as a literature search, or recorded in the
ledger. Stale flags, ledger entries, and descriptions are repaired here, once the user has
signed off on the change.

## Scope

Curation runs over a scope, never the whole project: one tag or a small family of them, a
ledger thread, everything written since the last `curate:` commit, or a decision and the
evidence under it.

When the user names no scope, show the options below with their one-line descriptions, and
ask which to run and over what. Draw the candidates from `index.md`, `glossary.md`, and
`ledger.md` and name them concretely: "`ng`, 11 entries and no synthesis over them", "the
Zimbabwe thread, four open questions and no next step". Each option is independent, so run
the ones the user picks and leave the rest.

Two of the options share their reading. Descriptions and tags opens every page in scope
whose description does not settle its tag, which covers two of the three signals Syntheses
to recommend looks for, so offer that one once the sweep is done and the reading is fresh.
Gaps and Upkeep both work the ledger threads in scope, and over a thread they cost little
more together than apart. Offer the second option and wait for the user to take it.

The `# Curation` thread in `ledger.md` holds what earlier curations proposed and the user
declined. Read it before proposing anything, and raise one of those again only where the
reason it was declined no longer holds.

## Options

### Syntheses to recommend

> Questions relevant to the project that the canon literature can answer.

Three signals, in the tag pages in scope and in the ledger:

- Several entries bearing on the same question with no synthesis over them. Start from a
    tag holding many entries and no synthesis at all.
- Two pages answering the same question differently, neither acknowledging the other. Most
    such pairs are not errors, since different populations, periods, or methods give
    different numbers. Recommend the page that carries both values and the difference in
    design behind them.
- Questions the ledger has re-asked across sessions.

Recommend the topic as the question /query would be asked, where answering it again later
would mean re-reading the same entries. On approval /query runs it, and the user decides
whether to keep the answer as a page.

### Gaps

> Data gaps that a working thread or a model parameter needs.

Judge against the questions the project is trying to answer and the model it runs, since a
list of everything the literature has left unsettled helps nobody.

Read the threads and decisions in scope, ask what each one needs to move, and check
whether the canon supplies it. Parameters, priors, and calibration targets with no entry
behind them are the same case.

Whether the literature has the number is the part curation cannot see. Either nobody has
looked for it, or people have and it does not exist for this setting, and the canon rarely
records which. Put the gap to the user with what the canon does show about coverage: how
many entries the relevant tags hold, whether a synthesis or a /query has already worked
the question, and whether the ledger records a search. Their call decides the
recommendation:

- **Unsearched**: a literature search, and a ledger entry under the thread carrying the
    open question until it returns. Whatever the search finds is cataloged.
- **Searched and absent**: a /query over what the canon does hold, whose synthesis states
    what is known and where it stops, plus the ledger entry naming the analysis or dataset
    that would close the gap.

### Upkeep

> Refreshing pages whose sources changed after they were written, and clearing completed
> or irrelevant ledger entries.

`index.md` flags a synthesis or decision whose body-linked dependency was updated after
it. The flag reports only that a dependency moved. Open both and decide whether the
conclusion moved with it. Rewrite the page when it did. When it holds, say so and, with
sign-off, run `stamp` on the page to clear the flag.

Then `ledger.md`, over the threads in scope:

- Delete entries that have stopped doing work: a next step that completed, a question the
    canon now answers, a dead end that no longer bears on the thread.
- Promote what has settled. Entries that have become general to the project and are backed
    by evidence belong in canon as a decision or a synthesis, and the ledger entry goes
    once that page exists.
- Threads with no next step are finished or blocked. Close the finished ones by deleting
    their sections, and write down what the blocked ones are waiting on.

### Descriptions and tags

> Index, glossary, and page descriptions that no longer match the pages under them.

Sessions pick what to open from one-line descriptions, and nothing else: `index.md`
carries one for every synthesis, decision, and finding, `glossary.md` carries one per tag,
and a tag page shows its members by description alone.

Run `compile`, then `check`, and start from its warnings. None of them block and each is
a judgment the script cannot make: thin tags, tags that read as near-duplicates, tag pages
with no description.

Open each tag page in scope and work down the member list, asking of each page whether its
description explains why it carries the tag. Sometimes the description settles that either
way. Where it leaves the question open, open the page and read it. Settle every member
before proposing anything, since which of these it turns out to be decides what changes:

- The description explains the tag. Nothing to do.
- The page belongs under the tag, and the description does not show why, or would not get
    the page opened for the question it answers. Rewrite the description.
- The page does not belong under the tag. Propose the retag.

With the members settled, judge the tag's own line. Someone reading only that line should
be able to tell whether the pages under it bear on their question, and most of the drift
comes from growth, a line written when the tag held three pages and left in place at
twenty. Propose a line covering what is there now. Where the members fall into two groups
a question would want separately, propose splitting the tag in two instead, with its own
glossary line for each.

The index preamble states the question the project is after, the approach it takes, and
what the canon collects for it. After a stretch of cataloging in a new area it often names
none of the three. Propose the edit, within the two or three paragraphs /canon allows.

Renaming or merging a tag means editing every page that carries it, so argue each change
and get approval first. Tags added after older entries were cataloged never reach those
entries, so sweep them back over the older pages in scope and bring the retag list. For
a split, merge, or rename, edit `## Tags` in `glossary.md` and retag the pages in the same
change, then `compile`.

## Closing

Present what the options turned up and ask which finding to take first, or as a group.
Recommendations the user turns down go to the ledger under a `# Curation` thread, one line
each for what was proposed and the reason it was declined.

Then `compile`, `check`, and commit as `curate: <what>` per `docs/CLAUDE.md`.
