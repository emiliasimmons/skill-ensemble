---
name: canon
description: Project orientation and script usage. Load when writing pages, compiling surfaces, checking conformance, reasoning about the project's structure, or when asked about the docs.
---

# Canon

A canon is the official rules, materials, recognized standards, the most important and
influential, or approved collection of works. This project's canon is a set of files
including: summaries of external references and the evidence behind them, syntheses of
ideas and conclusions over these summaries, and internal findings and decisions from the
project.

The Canon exists as a **reference** for you to find detailed or highly precise information
pertaining to the project. Expect the user to know the knowledge base generally and not to
know the specifics of individual sources, or the content of summaries. It is structured
for progressive disclosure: `index.md` and the tags are the map, and together they
describe what the canon covers. When a question relates to a tag or description in the
index, explore freely: read tag pages to get ideas of the specific pages, and follow links
to sources.

You maintain the pages, and the user decides the core sources of the knowledge.

**Immediately**, read:
- `docs/index.md` for the navigation surface
- `docs/glossary.md` for the shared vocabulary
- `docs/ledger.md` for the working threads and state

## Navigating the canon

Given a request, the first thing to settle is whether the canon holds anything relevant to
that request. To do so, compare the request to the content in `index.md` and the tag
vocabulary in `glossary.md`, as they summarize the canon's content. The index lists every
synthesis, decision, and finding with a one-line description, and every tag with the
number of pages under it. The glossary gives each tag its own one-line description. If
neither describes the subject, the canon does not hold information about the request. If
the user seems to be asking about the canon, say so, otherwise do not.

When a synthesis description matches, read it first. Syntheses are sound on the sources
they drew from, and the open question is whether those sources covered enough: a conclusion
built on a slice of what the canon now holds can be reasonable and still insufficient. If
the index flags that one stale, pages it links have been updated since it was written, which
tells you how much further to look. Go into the tag pages regardless, and stop at a single
synthesis only when it matches the request exactly.

Tag pages cover more ground. They list every page with that tag, grouped by type, each with
its one-line description, so you can match a subject against the list quickly and open only
what fits.

From there, go as wide and as deep as the question needs. Entries hold what a source
reported, the conditions it measured under, and what it is for in this project. Decisions
and findings hold what the project has already settled or measured internally, worth
reading before you re-derive either. Pages link each other file-relative, so following
links inside a subject is usually faster than returning to the tag list.

Occasionally, it will be helpful for you to explore the full content of a cataloged entry.
Open the extracted content under `raw/` when you need an exact figure that isn't in the
summary, its denominator, the population behind it, the full data table, plots, or the
wording of a claim you are about to argue with. Lines that surprise you are reason enough
to open the source. The usual cause is a unit or transcription error in the page, so check
that before you report the surprise.

### Layout

```
docs/
  raw/           raw files (PDFs, datasets)
  pages/         entries, syntheses, decisions
  findings/      analysis results
  tags/          generated one page per tag
  export/        artifacts written for somewhere else
  index.md       root orientation page
  glossary.md    shared vocabulary
  ledger.md      open threads, next steps, and declined ideas
  settings.json  machine config, including: extra types, external trees
  CLAUDE.md      the project's conventions
```

`export/` holds material written for an audience outside the project and is no part of the
canon. Read it when the user asks about an export, and leave it alone otherwise. A bundle
carries copies of pages, so an answer drawn from one is an answer drawn from a stale copy
of a page you could have read directly.

### Page types

`entry`: a cataloged record describing one source the project read: a paper, guideline,
report, code repository, dataset, or a colleague's note. It provides a summary of the
source and its relevance to the project.

`synthesis`: an answer assembled over several entries, providing the conclusion in plain
language and every claim linked to the page or source it came from.

`decision`: any choice about the project the user wants *on the record*. For example:
scope, which sources count for calibration targets, model structure, algorithm,
implementation. It provides the choice and the reasoning behind it.

`finding`: the result of the project. Any page under `findings/` is a finding and has
no `type` field.

### Root pages

`index.md`: the orientation surface, written for someone who has not read the project. You
manage the preamble with the user, containing: the question the project is after, the
approach it takes, and what the canon collects for it. Keep it a slow-changing and concise
(2-3 paragraph) summary of the project's README and the canon's knowledge base. Any topic
you would revise after a cataloging batch or curation pass more likely lives in the
ledger. The layout and the page types are not content for the index, and the status of a
task belongs in the ledger, so the preamble should not contain either. Every link in the
preamble points at a tag or a page, never at the ledger or a bib file. Edit the preamble
whenever the project's aim or scope changes.

Below the preamble, a note anchors the compiled region (`> Compiled from ...`), and
everything from the note down to the first authored `## ` heading belongs to compile: the
tag list with page counts, and the syntheses, decisions, findings, stale, and recent
sections. Leave the compiled region alone, since `compile` overwrites it, and keep the
note, because a surface without it has no anchor and `check` flags it.

`ledger.md`: every open thread and its next steps.

`glossary.md`: the project's shared terms and the tag vocabulary under `## Tags`. Add
a term when: it recurs, its meaning is not self-evident to technical readers from outside
the field, and it is specific to this project or opaque outside one field. When a term
conflicts with an existing one or is vague, settle the canonical form with the user before
it enters the vocabulary.

Each entry defines its term in one or two sentences and contains only what stays true for
as long as the term is used. Leave values, defaults, counts, renames, and the state of the
literature to the model and the pages that record them. Write the definition alone,
without links or contrasts with neighbouring terms.

`compile` parses the `## Tags` list, one line per tag:
```
- **<tag>**: <one-line description>
```
The `tags/` pages are generated from lines matching that pattern.

`CLAUDE.md`: the project's conventions and the user's standing preferences, including how
commits are made, where sources come from, and how far to navigate before reporting back.
Add to it when the user states a preference that should hold for every later session, and
does not overlap with the ledger.

`settings.json`: machine config, read only by `canon.py`. Never hand-edited to change what
a page says. The keys and what each one does are in `canon_usage.md`.

## Writing

Link like wikipedia, in a markdown file and in a reply alike: the first mention of a page
gets a markdown link to the file, later mentions in the same file or reply do not, and it
gets a link again once a turn has passed. Inside a file the path is relative to the page
carrying the link. In a reply it is relative to the session's working directory. Cite
a decision by its title or file name.

Write for technical readers who lack the background you just absorbed. Cover the
substance and stop: no filler, no closing summary. Where a field's term is the only one
that will do, gloss it at first use. Give numbers their units and what they are relative
to. Internal links give the rest. Pages are one click away, so link them and give only what
they mean for the question. Per sentence: cut it if the user could have written it, or if
a link already gives its information.

### Writing pages

Load the relevant format from `canon/formats/`. It gives the frontmatter, the body shape,
the filename, and the directory. Fill in `type`, `title`, `description`, and the tags,
leave `updated` alone. Write links to other pages relative to the page carrying the link.
Reuse an existing tag before adding one. Introducing a new tag requires writing its line
in the glossary's `## Tags` list. `check` will throw an error if a tag is used in a page
without its description in the glossary.

Findings are concrete results, think of them as a staging area for a results section.
Suggest to record a finding when there are statements you can make that can be summarized
by one or a few figures, with additional support from others (again, consider a results
section that utilizes supplemental information for strength), **or** if a figure or result
answered a well defined question within the project. These are not *requirements*, if
a user wants a finding recorded then record it, these are suggestions for when to
recommend one. Only include a type for a finding if requested by the user.

Never hand-edit a compiled region. On `index.md` the note marks where yours ends and the
script's begins, and `compile` overwrites everything below it. Tag pages are entirely
generated, do not edit them. Recompiling is the hook's job, not yours: it rebuilds the
whole canon at the end of the turn and runs `check`, so pages that do not conform come
back to you before the turn ends.

Recommend a decision when the *rationale* needs to outlive the session and the thread it
came from. Record the rationale, the scope it covers, and any conflict with a decision
already on the record. Revise it as the project moves, narrow or widen its scope, and
delete it when the choice is dropped. Recording a decision does not commit the project to
the choice, it records the reasoning that would otherwise be lost. Decisions require user
approval. Suggest decisions when the rationale fulfills:

- **Non-obvious justification:** a reviewer would need to ask why this path was taken.
- **No precedent:** the choice is not justified by literature, established frameworks, or existing sources.
- **No field consensus:** the approach is not an accepted standard in the relevant community.

When recommending a decision: state the decision, why it qualifies, and the suggested
rationale so the user can approve or edit.

# Ledger

The ledger carries the working state of the project and every thread currently open.
Threads are lines of work with a next step: an experiment, an implementation, an
investigation into a question. Their **purpose** is so the user can open a session and say
"let's work on X", so threads follow how the user divides the project, and threads the
user would not name are ones to leave unopened. The canon carries settled, project-wide
evidence. The ledger carries the questions, provisional choices, and next steps standing
around it.

It is one file, `docs/ledger.md`. Write to it directly, do not check for existence. You
write to it as you work, and the user reads it to see where a thread stands. Split it
across several files only where the project's `CLAUDE.md` says to.

## Sessions and threads

The first time you use the ledger in a session, whether to pick up a thread or to write to
one, say which thread you are on ("Working on thread Calibration > Zimbabwe") so the user
can correct you. If no thread fits the work, ask the user with your recommendation: "Are
we on Calibration?", or, when the work deserves a thread of its own, "Should I add this to
a new thread, Zimbabwe data?". A session that sets out a clear task and completes it has
nothing to do with the ledger.

Write only to the thread you are on. On a sub-thread, that includes the entries directly
under its parent header, and on a top-level thread, every sub-thread beneath it. Ask the
user before writing anywhere else, sibling sub-threads included.

Open a thread only with the user's approval, and write its goal on the line under its
header: what the thread is for and what finishing it looks like.

## Writing to the ledger

Record something when its absence would cost the next session on this thread real work:
a choice it would re-decide, a question it would re-ask, a path it would re-explore. Facts
that are merely true or interesting do not qualify, and neither do facts bearing on
another thread, or anything the next session reconstructs at a glance, reads out of canon,
or reads out of any existing files. Raise those in your reply when they are worth the
user's attention.

Every entry ends with *Close when* and the event on this thread that clears it: a step
done, a question answered, a choice the user makes. If you cannot name one, the entry does
not qualify. Provisional choices, made under uncertainty to keep moving, close when the
question behind them is settled. Dead ends (what you tried and why it failed) close with
their thread, or sooner once a decision or finding records them. Choices made on purpose,
which the next session would otherwise undo, close the same way.

Facts about one source belong on that source's page. They reach the ledger only when they
change what this thread does next, in one bullet, linked to the page that records the
fact.

## Built-in threads

The skills manage four threads, each existing only while it holds entries. The first
session to write to one opens it, with the first sentence of its description below as the
goal line, so the user reading the ledger sees the goal too. The skills that work these
threads name them, and running one puts the session on its thread.

- `# Catalog`: sources to get into `pages/`. An entry closes when its source is cataloged.
- `# Queries`: syntheses and questions waiting on /query. An entry closes when the user has
    the answer.
- `# Curate`: literature to search for, and curation recommendations the user declined.
    Gaps go under `## Gaps`, each closing when the search returns and what it found is
    cataloged. When a search finds nothing, rewrite its gap as an absent entry: what was
    searched, when, and that nothing exists for this setting. Absent entries have no
    *Close when* and stay, so the search is not run twice. Declines go under
    `## Declined`, one line each for what was proposed and why, closing when the reason no
    longer holds.
- `# Project`: notes on the project as a whole, such as its current status and threads
    worth starting. Write to it only with the user's approval.

A thread waiting on a gap says so in its own entry, and the gap entry describes only the
literature.

## Removing entries

Delete entries once they close: a next step you completed, a question you answered, a dead
end now recorded in a decision or finding. Prune as you write. Git carries the history.
Close a thread by deleting its section once its goal is met, after asking the user whether
its dead ends are worth recording.

When an entry becomes settled, general to the project, and backed by evidence, it belongs
in canon as a decision or a synthesis (syntheses must be accompanied by a query).
Recommend the move, and delete the ledger entry once the page exists. Many entries close
with nothing to record: a library chosen for familiarity needs no decision.

## Structure

No frontmatter. Headers are threads, sub-headers are sub-threads, and the line under a
top-level header is that thread's goal. Sibling headers advance independently, so two
sections that one action would move are one thread. Entries are bullets of a sentence or
two, nested under the question or step they belong to.

Every page the ledger names gets a link, file-relative, as on a page.

For example:
```markdown
# Catalog
Sources to get into `pages/`.

- `tayimetha_antimicrobial_2018` has a directory but a failed extraction, so re-extract it
    before cataloging. *Close when* the source is cataloged.

# Calibration
Calibrate the model to Zimbabwe and a general-population comparator, done when both pass
re-identification.

## General population
- What HIV incidence prior should we use for a calibration target? Some preliminary
    information gathered from Rakai in [Wright 2025](pages/path2.md), but we need
    a broader view before determining the appropriate range (see the HIV incidence gap
    under Curate). We will move forward with the Rakai prior for experiments while
    gathering data. *Close when* the gap's literature settles the range, or the user picks
    a prior without it.
- Experiment 4 is narrowing the bacterial STI prevalences, see `experiments/path/here`.
    *Close when* experiment 4 is written up.

## Zimbabwe
...

# Curate
Literature to search for, and curation recommendations the user declined.

## Gaps
- HIV incidence in general-population cohorts outside Rakai. *Close when* literature search complete.
- doxycycline use in Zimbabwe from the '90s to present day. **Absent** Searched OpenAlex
    2026-09-20, and nothing covers this setting beyond [Do 2025](pages/file_path.md).
```

# Canon script

```
uv run --script ${CLAUDE_SKILL_DIR}/canon.py --root <substrate-root> <subcommand>

compile [--block root|tags]         regenerate the compiled surfaces from frontmatter
check [--frontmatter|--links]       conformance and link integrity, non-zero on a blocker
stamp <path>                        set a page's `updated` to now
```

Canonize is set up with hooks to call the script for you:
- `stamp` runs after every Write and Edit, manages a page's `updated`.
- `compile` and `check` run together at the end of a turn that leaves uncommitted in the
    canon and a blocking conformance error comes back to you before the turn finishes.

Let the hooks do their job. Call the script yourself only when the hooks are not running,
or when you need the result before the turn would end: the user asking you to make edits
and then commit leaves nothing uncommitted for the hook to check, so run `compile` and
`check` before the commit. Detailed usage of the subcommands and their flags is in
`canon_usage.md`.
