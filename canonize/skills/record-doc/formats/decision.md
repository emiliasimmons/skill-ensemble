# Decision format

A decision record (DR) is a decision about the model, kept as immutable evidence — the modeling analog of an ADR.

File: `decisions/DR-NNNN-kebab-title.md`. The number comes from `sequence --kind decision`; never pick it by hand. Type `decision`.

**Frontmatter:**

```
---
type: decision
title: <the decision as a short noun phrase>
description: <one line: what was decided>
timestamp: <ISO 8601 with time, stamped once at creation>
status: <provisional | accepted | superseded by DR-NNNN>
tags: [<topic names and cross-cutting themes>]
bears_on: [<file-relative links to the provenance or findings it touches>]
supersedes: <DR-NNNN, only when replacing an earlier decision>
---
```

`tags` bind the DR to every hub it belongs in — a DR tagged `seasonality` appears in that hub's member list. The single-parent rule never applies to evidence; a decision appears in every hub it is tagged to. `status` drives the registers: `accepted` compiles into assumptions, `provisional` into open-decisions. `bears_on`/`supersedes` are the typed relations a trace walks without reading the body.

**Status**, one of:

- `provisional` : an expedient choice made to unblock work.
- `accepted` : a considered decision. A plainly stated assumption is an `accepted` DR — the assumptions register compiles from these.
- `superseded by DR-NNNN` : replaced. The replacement carries the real reasoning and names it in `supersedes`.

**When to write one.** Not "is it hard to undo." Write a DR when a reader of the model or its results would be misled without it. That catches a structural choice easy to change in code but shaping how every result is read, and a placeholder, trivial to undo but disastrous to leave unrecorded.

**Body:**

- the decision, in a line or two
- why. For a provisional, why it was the parsimonious thing to unblock work, the open question it stands in for, and the trigger that should make you revisit it
- a `# Citations` section if the decision rests on external sources

Additional sections are fine when the decision warrants them. A DR never points at code; code changes, decisions don't. Code pointers live in provenance pages.
