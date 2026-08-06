# Glossary format

The glossary pins down terms so the project speaks one language, kept inline as terms come up.

File: `glossary.md` at the bundle root, type `glossary`. A single conformant page.

**Frontmatter:**

```
---
type: glossary
title: Glossary
description: Canonical terms for the project.
timestamp: <ISO 8601, stamped once at creation>
---
```

**Body:** for each term, the canonical word and a one-line meaning precise enough that two people could not read it two ways.

When a new term collides with one already there, flag it and pick a single canonical form rather than letting both run. When a term is vague or overloaded, propose the precise word ("you are saying account — the customer or the user?"). Keep it short; a glossary earns its keep by being read.
