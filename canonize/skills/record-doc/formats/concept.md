# Concept format

A concept is a synthesis worth keeping — an answer you would hate to re-derive in six months. `query-docs` offers to file one when an answer is expensive.

File: `topics/<topic>/<short-name>.md`, type `concept`.

**Frontmatter:**

```
---
type: concept
title: <the idea, as a short phrase>
description: <one line: what the concept captures>
timestamp: <ISO 8601 with time, stamped once at creation>
tags: [<cross-cutting themes beyond its home topic>]
derived_from: [<file-relative links to the evidence it synthesizes>]
---
```

The home topic is the directory it sits in. `derived_from` names the sources, findings, or decisions the synthesis rests on, as the typed relation a trace walks.

**Body:** the synthesis itself, in structural markdown. Every claim traces to something in sources or evidence, by file-relative link. Add sections beyond the synthesis when the material warrants it: comparison tables, open questions, worked examples, or whatever structure fits. A `# Citations` section where external sources back it.

**Readable on its own.** A technical reader, not necessarily in the field a given source comes from, must follow the page end to end without opening the sources or the linked pages; the links carry provenance and depth, not the argument. Lead with the idea in plain language before any notation or derivation. Every term whose meaning is specific to one field or to this project is used in its glossary form or defined at first use; an unglossed one is the defect. A term that recurs and has no glossary entry is promoted rather than reglossed on each page.

A concept is wiki: revise it as the picture sharpens. If backing evidence is removed, the concept's claim is invalid — fix or supersede it.
