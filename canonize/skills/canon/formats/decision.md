# Decision format

Decisions record choices about code functionality or a mathematical model: structural or algorithmic choices that readers of the model or its results would be misled without. They never record parameter values, since parameter-to-evidence provenance belongs to the experiment that sets it.

File: `pages/<kebab-title>.md`, type `decision`. Cited by title.

**Frontmatter:**

```
---
type: decision
title: <the decision as a short noun phrase>
description: <one line: what was decided>
tags: [<subject and cross-cutting themes>]
updated: <YYYY-MM-DD HH:MM, set by the hook on every write, never hand-authored>
---
```

**Body:**

- the decision, in a line or two
- why: the reasoning, and what it rests on. Where it rests on a source, link that source's entry page inline where it bears on the reasoning. External sources with no page are cited inline (author-year, DOI). No citations section. Where the choice is a stand-in made under uncertainty, state the uncertainty here in the rationale

Decisions are wiki: they change as the model does. Revise them in place. Git holds the history. When a choice is dropped, delete its decision.
