---
name: query
description: Answer a question from the project's evidence, or trace a value back to what it rests on. The answer is written as the synthesis page would read, and recorded to pages/ on request. Use when the user asks why something is the way it is, where a number came from, or wants an answer grounded in what the project holds.
---

**First**, orient with /canon.

The reply is the page. Write the answer in the form a synthesis takes on disk without
frontmatter, but with headings and links and all, so recording it afterward is a copy. The
user reads it and says whether it stays.

## Navigating

/canon gives the route in. Answering a query takes that route further: your answer should
comprehensively address the query, so navigation ends once every page that could bear on
it has been seen or ruled out.

That set runs wider than the tags a question obviously maps to. Take the union of every
tag page the question touches, since entries often carry only one of those tags, add
whatever the index names on the subject, and count the pages linked from anything you read
as part of the same set. Descriptions rule candidates out. They cannot ground a claim, so
nothing in the reply rests on one alone.

Read every synthesis, decision, and finding the question touches, whatever the entries
turn out to say. Syntheses already on the subject either feed the answer or get replaced
by it, and ignoring one leaves the canon holding two pages that answer the same question
differently. Decisions may have settled the question already, and the answer says so.
Findings are the project's own measurements and bear wherever they touch the question.

Entries carry the conditions their source measured under, which decide whether a number
answers this question: the population, the denominator, the year, the setting. When two
entries disagree, both belong in the answer along with the conditions that separate them,
so hold the disagreement open.

How far to read is settled by the question and by what the canon turns out to hold, and
both look different a few pages in. Go back over the tag lists as the answer takes shape,
since descriptions dismissed early read differently once the terms of the answer are
known, and those early dismissals are the usual hole in a wide answer.

Open the extracted content under `raw/` only when the answer turns on an exact figure, its
denominator, a full table, or the source's own wording. Numbers that surprise you (seem to
disagree with another entry without reason) are reason enough. The usual cause is
a transcription error on the page, so check that before building on it.

The reading is done when every candidate has been seen and every claim in the answer
stands on a page, a source behind an entry, or a finding.

## The reply

The reply comes in two parts: the answer, and a note on the read. Only the answer is the
page.

Follow the body shape in `canon/formats/synthesis.md`: the idea in plain language before
any notation, each claim carrying a file-relative link at the point it bears, terms from
one field glossed at first use, and no citations section. Sources with no page are cited
inline at the claim, author-year and DOI. Add the sections the material warrants, such as
a comparison table or the open questions the evidence leaves.

Open with the page's title as an `#` heading, so what follows is the body as it would be
filed. Links in the reply are relative to the session's working directory, so they open
from the conversation.

Questions two or three pages answer get a paragraph or two with the links at the claims
and no headings. The shape scales with the question.

Where the reply needs background the canon does not hold, mark that sentence as unsourced.

Then a horizontal rule, and the note on the read below it. A few lines: the tags swept and
how many pages each holds, what was opened and what the descriptions ruled out, and every
place the evidence ran thin. Claims resting on one entry, entries whose population or
period sits off the question, stale pages drawn on, entries written from an abstract
alone. The note never goes to disk.

## Tracing a value

Start at the page stating the value and follow its body link to the entry beneath, then
the entry's `resource` or `local` to the source itself, and read the value where it was
published. Report the chain, each hop as a link, so the user can walk it.

When the page and the source disagree, say so and propose the correction against the
published source. When the index flags the page stale, a dependency was updated after it:
report the value as it stands, and say the evidence underneath has moved.

## Recording it

Ask whether to keep the answer. On yes, write it to `pages/<short-name>.md` with the
frontmatter `canon/formats/synthesis.md` specifies. The body is the answer, and three
things change on the way to disk: the note on the read is dropped, the `#` title line
becomes the frontmatter `title`, and the links are re-rooted from the session's directory
to the page's. Tags come from `glossary.md`, reused before invented, and genuinely new
ones need their glossary lines and the user's approval.

Where the answer refreshes a synthesis the canon already holds, rewrite that page instead
of adding a second one. Rewriting it also clears its stale flag.

Then `compile`, `check`, and commit per `docs/CLAUDE.md`. Answers the user takes without
filing them are a normal outcome.

## Conflicts and gaps

Where the answer contradicts a recorded decision or a value on another page, put the
contradiction in the reply and leave it standing for the user.

Where syntheses you drew on are flagged stale, say so and offer to refresh them against
their current dependencies.

Where the canon holds too little to answer, say what is missing and what would close it: a
source to find, an analysis to run, a dataset to acquire. Offer the ledger entry under the
thread that wants it.
