---
name: curate-docs
description: Review the project's knowledge state — find recorded values that are wrong, contradictions, stale claims, missing concepts, taxonomy issues, and data gaps. Conversational; every change needs sign-off. Use when the user asks for a curation pass, a deep review, or wants some part of the project re-examined after accumulating material.
---

**First**, immediately orient with /canon.

## Scope

A pass runs over a scope, not the whole project. Take the scope the user names and map it onto the categories below: "curate the new things" is stale claims and hub rewrites over what landed since the last `curate:` commit; "curate for new concepts" is one category over everything.

When no scope is named, propose two or three from the current state rather than asking an open question. `index.md`'s compiled state block gives the hubs past the staleness nudge and the recent writes; `git log` gives the last `curate:` commit; the tag counts show where growth concentrated. Name each candidate with its size — how many pages it covers — and wait.

## Categories

- **Value errors** — a recorded number that is wrong. See below.
- **Stale claims** — pages whose claims newer sources have superseded.
- **Contradictions** — pages that conflict with each other.
- **Missing concepts** — ideas mentioned across pages but lacking their own concept page.
- **Taxonomy issues** — topics that should be split, merged, or renamed; pages that belong in a different topic.
- **Hub rewrites** — hubs past the staleness threshold whose synthesis no longer reflects their members.
- **Data gaps** — questions the project's evidence doesn't answer but could with a targeted source or analysis.
- **Unreadable pages** — concept or hub pages that fail the readable-on-its-own bar: a technical reader outside the source's field could not follow them without opening the sources or linked pages, or they lean on field- or project-specific terms that are neither in the glossary nor defined at first use.

## Value errors

Work from the pages by default. Read every figure in scope against its stated denominator and population, and against sibling pages measuring the same quantity:

- **Magnitude** — a value an order of magnitude off its siblings is a unit or transcription error until shown otherwise. Check the units the source reported in, not the ones the page states.
- **Internal conflict** — one page quoting two different values for the same quantity.
- **Scope** — a value used more broadly than the page's own bearing section licenses: a regional figure quoted as a constant, a subgroup figure quoted for the general population, a superseded upper bound still quoted as live.
- **Non-independence** — sibling pages drawing on the same survey rounds or the same cohort, treated as separate evidence.

Re-open the extracted content under `sources/` only for what this flags, or for a source the user names. Reading every extraction in scope is not a default pass.

## Working through findings

Present findings grouped by category. Ask which to address first.

- Value errors: propose the correction with the source text behind it. A page that states its own extraction problem is corrected against the published source, not the extraction.
- Stale claims and contradictions: propose concept pages that capture the updated picture, or propose handoffs for substantial re-synthesis.
- Missing concepts: ask whether to run a /query-docs pass or write the concept directly.
- Taxonomy changes: argue each one and get approval before files move. After moves, run a full compile then check — moves invalidate links corpus-wide.
- Hub rewrites: rewriting a hub synthesis updates its `synthesized` stamp. Propose a handoff for complex hubs.
- Unreadable pages: propose the glossary entries or inline glosses the page needs, and the plain-language lead if it opens on notation. A recurring cross-field term becomes a glossary entry; a one-off gets defined in place.
