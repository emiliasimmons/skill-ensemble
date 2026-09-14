---
name: export
description: Build an artifact from the project for somewhere else. A writeup, a slide schematic, a bundle for a colleague or another repository, a GitHub wiki, a dataset of claims, or a dashboard. Use when the user wants something exported, shared, published, handed over, or an existing export updated.
---

# Export

**First**, orient with /canon.

Exports are artifacts written for readers or systems outside the project. Everything they
produce lands under `docs/export/<slug>/`, and nothing enters the canon: no page, no
finding, no tag, no ledger entry. Where the work turns up a conclusion worth keeping, tell
the user and leave the writing to /query or /curate.

On the first export in a project, create an empty `docs/export/.gitignore` and ask how the
export should be tracked: ignored, untracked, or committed. The user decides per export,
so ask again when a later export differs in kind from the ones before.

## Export steps

1. **Purpose.** Usually arrives with the invocation. Ask only when it is missing, and ask
    nothing else until it is answered.
2. **Target.** One of the sections below, or the general path when none fits.
3. **Kind.** One-off, or a mechanism that can be run again. Targets carry a default:
    dashboards and datasets repeat, slide decks are one-off, writeups depend on what goes
    in them. Judge from the purpose, then confirm.
4. **Content.** The user says what goes in. Resolve it with them, in as many passes as it
    takes. The canon's tag vocabulary does not constrain this: a writeup can draw on model
    code, experiment output, and material the project never cataloged.
5. **Questions.** Every question still live, in one numbered batch, each with a
    recommendation.
6. **Shared understanding.** Before anything is written, summarize what the export will
    be: purpose, audience, what goes in, what the output looks like, and where it lands.
    State every assumption with the reasoning behind it. Wait.
7. **Build.** A single output stays one file. For a few, ask where they go. For many, use
    a directory.
8. **`EXPORT.md`**, always, including for a one-off.
9. **Verify**, for mechanisms only.

## Live questions

Targets below list their questions with the condition that makes each one worth asking.
Check the condition against the resolved content first. Sources with no DOI make the
raw-files question live. When every source carries a DOI, skip it.

Where a condition is unclear, assume the answer and carry it into the shared-understanding
summary with the reasoning behind it.

## EXPORT.md

One file per export directory, holding the record and the instructions together:

- Purpose, audience, and the date of the first run.
- How this export is tracked in git.
- What went in: the pages, the files, the outside material, each linked.
- The answers given, so a later run does not re-ask them.
- The steps a re-run takes, in order. Prose for agent work, commands for mechanical work,
    and both in whatever mixture the export needs.

Write the steps for an agent that has never seen this conversation. Each step names the
script or the reading it needs, the arguments it takes, and what its output looks like
when it succeeded.

Work needed before the mechanical part (building temporary pages out of experiment output,
pulling numbers from a model repository) goes in a pre section. Work needed after
(rewriting a wiki index, checking a rendered document) goes in a post section.

One-offs write the record without the steps.

## Updating exports

Updates arrive as conversation: "update the dashboard", "refresh the brief for Aisha,
I added six papers". Find which export is meant, and ask when more than one matches. Then
read its `EXPORT.md` and run its steps.

Report each step as it finishes. Stop before anything irreversible: a push, or any write
outside the export directory.

## Verifying mechanisms

Mechanisms are only reproducible if they run without this conversation, so prove it. Give
a subagent what the user would give it: "run the ct-dashboard export", plus the path to
the export directory, and nothing else. Anything more, a briefing or a summary of what was
decided, hides the gap you are testing for.

Whatever it had to guess is missing from `EXPORT.md`. Patch the file against its report
and send a second one. If the second run also comes back wrong, stop and bring the user
what is unresolved. Take runs that fail outright, or produce something unrecognizable, to
the user immediately.

Keep the output from the planning run either way.

# Targets

## Writeup

A document for people, in markdown first. Everything else (docx, pdf, html) is derived
from the markdown by the `docx` skill or by pandoc, so a later edit changes one file and
re-derives the rest.

Do the reading yourself. Writeups often need model implementation detail, findings, and
outside material the canon does not hold, and they reorder and rewrite all of it for
readers who have never seen the project.

Live questions:

- Format, when the user named none.
- Citation style, always. Author-year with a references section suits readers outside the
    project, page links suit readers who have the repository, and a plain bibliography at
    the foot suits documents that should carry no links at all. Every form is built from
    entry frontmatter, which holds `author`, `published`, and `resource`.
- Length and depth, when the purpose does not imply them.

## Slide deck

The default output is a schematic: the argument, one block per slide, with the claim each
slide makes and what it shows. Beside the schematic, list the figures and files the deck
needs, ready to hand to a deck-building tool. Confirm this is what the user wants, since
the alternative is building the deck here.

Live questions:

- Schematic or built deck.
- Audience and duration, which decide how many slides the argument runs to.
- Which figures exist and which need making.

## Share bundle

Markdown for a colleague or for another repository. The first question decides everything
else: is this read standalone, or read inside a canonize project?

Standalone bundles go flat, with an index listing what the bundle holds and what each page
says. Reduce the frontmatter to the fields a reader uses and drop the rest.

Bundles for a canonize project mirror the canon's layout, `pages/` and `findings/` under
the export directory, so the files move into the receiving project without a rewrite. Keep
the frontmatter whole, `updated` included: it tells the recipient how old each page is,
and their own `check` will demand it.

Links are the work in both cases. Rewrite links to pages inside the bundle into the
bundle's layout. Degrade links to pages left behind to the page title and its `resource`
identifier, so the reader can still find the source. Confirm every link in the output
resolves before finishing.

Live questions:

- Standalone or canonize project, always.
- Raw files, when the content holds entries whose `resource` is a local path with no DOI
    or URL. Name those entries in the ask, since they are the ones recipients cannot reach
    any other way. Sources carrying a DOI need no file.
- Which frontmatter fields to keep, when the bundle is standalone.

## GitHub wiki

A flat snapshot for a repository's wiki, produced by
`${CLAUDE_SKILL_DIR}/scripts/to_github_wiki.py`. Default directory
`docs/export/github-wiki/`.

The wiki is often a subset of the canon, so the scope lives in `wiki.json` beside the
output and the script reads it on every run:

```json
{
  "remote": "git@github.com:owner/repo.wiki.git",
  "zones": ["pages", "findings"],
  "tags": [],
  "exclude": ["ledger.md"]
}
```

An empty `tags` list carries every page in the named zones. A populated one carries only
pages holding one of those tags. Links to pages the scope left out degrade to the page
title with its `resource`, so a wiki covering one tag still points at the sources behind
the pages it dropped.

Publishing is a separate act. Write the snapshot, print the clone-and-push commands, and
push nothing unless the user asks for it in that turn.

Live questions:

- Scope, when the wiki is not the whole canon.
- The wiki remote, when the repository has no `<repo>.wiki.git` configured.
- Whether to push, at the end, once the snapshot exists.

## Claims dataset

A table the project's own code reads, built from claims in the entries. Entries hold
prose, so the fields come from the user: what the dataset is for decides the columns.

Three things specific to this target:

- **Reproducibility.** The extraction is a step in `EXPORT.md` specific enough to re-run.
- **Adding literature.** A second run takes the entries cataloged since the first and adds
    their claims to the existing table, leaving the rows already there alone unless their
    page changed.
- **Screening**, when the user wants it. A rule for which papers belong in the dataset at
    all, applied before their claims are extracted, recorded in `EXPORT.md` so the second
    run screens the same way the first did.

Author the extraction into a single intermediate file, in whatever form fits the dataset.
`${CLAUDE_SKILL_DIR}/scripts/claims_to_table.py` converts a file of `## ` blocks with
`key: value` lines into csv and xlsx. For a dataset whose shape does not suit that, write
a converter into the export directory.

Every row carries what it came from: the page, and the source behind the page. Give the
denominator and the population their own columns, so a value means something on its own.

Converted files stay in the export directory.

Live questions:

- What the dataset is for, then the columns, one pass each.
- Screening, and the rule if yes.
- The intermediate form, when the columns do not suit the shipped converter.
- One row per claim or one row per source, when entries hold several claims each.

## Dashboard

One self-contained HTML file: data embedded between `<!-- BEGIN GENERATED DATA -->` and
`<!-- END GENERATED DATA -->` markers, UI written around it. Re-runs replace what lies
between the markers and leave the UI alone. Above a few megabytes of data, move the data
to files the page fetches and keep the markers for the manifest.

Build the extraction first. Show the user the extracted data, as data, before any
interface exists. Then build one tab through to finished, and the rest after they have
seen it work. Extraction is the expensive half and a wrong extraction behind finished tabs
is a rewrite.

The extraction script lives in the export directory, since it is specific to this
dashboard, and `EXPORT.md` names it as the update step.

Live questions:

- What goes on it, and what the tabs are.
- Styling: a stylesheet or design system to copy in, or plain CSS in the file.
- Provenance: whether displayed values link back to their entries, and whether those links
    are repository paths for someone with the project or DOIs for someone without.
- Whether anything outside the canon feeds it, which makes a pre section in `EXPORT.md`.

## Anything else

A format none of the above covers: a poster, a grant appendix, a README for a handover,
a data package. Settle purpose, content, and directory the same way, then produce the
format directly or with whatever tool the user names for it.
