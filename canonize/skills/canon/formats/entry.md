# Entry format

Entries record a summary or description or the content of the source you read: papers,
guidelines, reports, code repositories, datasets, colleague's notes. Raw files
live in `raw/`. Summaries live in `pages/`. Nobody browses the raw files: the summaries
are what the project knows.

File: `pages/<short-name>.md`, type `entry`.

**Frontmatter:**

```
---
type: entry
title: <the source's name>
description: <one line: what it is and what it bears on>
author: <first author, or "Last et al." / the maintainer / the colleague>
published: <publication date, when there is one>
resource: <DOI or stable URL, else the raw/ path>
local: <raw/<file>, when a raw file exists>
basis: abstract <only when the entry rests on the abstract alone>
tags: [<cross-cutting themes>]
updated: <YYYY-MM-DD HH:MM, set by the hook on every write, never hand-authored>
---
```

`type`, `title`, `description`, and `tags` are the floor. `updated` is stamped by the
hook. `author`, `published`, `resource`, and `local` are filled per kind. Repos have no
`published`, colleague notes have no DOI. `resource` prefers a web-accessible identifier
(DOI for academic works, else a stable URL). `local` names the raw file when one exists.
`basis` is absent on entries written from the source itself, and set to `abstract` on
entries written from the abstract and metadata alone.

## Body

Open with a short paragraph under no heading: what the source is and what it set out to do.
Paths and identifiers stay in the frontmatter.

Every entry then has a **Relevance to project** section: what this source can be used for
here, and what it cannot. Name the use, such as a target, a prior, a bound, a comparator,
or a design reference. Write about the project, not about other pages.

Link another page inline where the text depends on it, with a file-relative path. The
identifier lives in `resource`. No citations section.

Give every number the context it needs to mean anything: what it is a fraction of, who was
counted (sex, age band, year, sampling frame), and how it was measured. "Resistance 100%"
is not usable. "100% tetM by frequency, at the tetM locus" is. Without that context,
a number reads as settled fact when it is not.

After that, pick the profile below for the kind of source, and add or drop sections as the
material warrants.

**Article** (a paper):
- **Key points**: what matters here, paraphrased. No long passages.
- **Limitations**: the source's own, and any bearing on the use named above.
- **Methodology**: the design choices that limit how widely the results apply.

**Longform** (a book, guideline, or report):
- **What it says**: the operative content or recommendation, and the population it applies to.
- **Strength and basis**: the evidence grade, and what it rests on.
- **Key points** and **Limitations** as above.

**Git repo** (a code repository. `author` = maintainer, `resource` = repo URL, no `published`):
- **What the project uses**: the modules, classes, or parameters drawn on.
- **Architecture**: the structure a reader needs to follow the above.
- **Extension points**: where this project hooks in.

**Dataset** (`resource` = the download or DOI, `local` = the file if held):
- **What it contains**: variables, units, coverage in time and place.
- **Denominator and population**: who is counted, and who is not.
- **Provenance**: how it was collected, and by whom.

**Note** (a colleague's message or handwritten note. `author` = them, `published` = date received, `local` = the file):
- **What it says**: the claim or instruction, in their words where it matters.
- **Standing**: how much weight it carries, and what would confirm it.

## Abstract-only entries

Entries marked `basis: abstract` open above the lead prose with:

```
> Note: summary derived from the abstract only, not the full source.
```

Key points stay inside what the abstract states, and limitations records that the methods,
figures, and numbers were not read. Relevance to project holds to the use the abstract can
support. When the full source later arrives, rewrite the page from it, drop the note, and
drop `basis`.

Entries are wiki: update them as understanding improves. Raw files do not change.
