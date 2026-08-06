---
name: query-docs
description: Answer a question over the project's evidence, or trace a value back to what it rests on. Use when the user asks why something is the way it is, asks where a number came from, or wants an answer grounded in what the project already holds. Read-only; an answer that crosses more than a page or two is drafted as a concept page.
---

**First**, immediately orient with /canon. Every claim traces to sources or evidence.

## Answering

Find the relevant hubs from the taxonomy, read their syntheses and members, and follow references between pages until the answer is grounded. Walk the typed relations in frontmatter — `derived_from`, `bears_on`, `supersedes` — where the question is where a value came from. Traces compute live and recompute on the next asking; for an old result, report the values as they stood when it ran and flag where the evidence beneath them has since moved.

A question one or two pages answer gets a plain answer in the conversation.

## Drafting

Anything wider is answered by writing the concept page: the frontmatter `formats/concept.md` specifies, `derived_from` naming every page the answer rests on, and the synthesis with each claim carrying its file-relative link. Write it inline in the conversation, not to disk.

The draft is what gets discussed. Amend it in place as the user pushes back, and file it through /record-doc on acceptance. An answer the user takes without keeping the page is a normal outcome.

Where the answer contradicts an accepted decision or a calibrated value, put the contradiction in the draft rather than resolving it silently.

Route register-recompile requests to `canon fix`.
