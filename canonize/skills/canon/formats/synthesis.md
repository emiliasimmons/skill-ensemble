# Synthesis format

Syntheses are answers worth keeping, the ones you would hate to re-derive in six months. /query offers to file one when an answer is expensive.

File: `pages/<short-name>.md`, type `synthesis`.

**Frontmatter:**

```
---
type: synthesis
title: <the idea, as a short phrase>
description: <one line: what the synthesis captures>
tags: [<cross-cutting themes>]
updated: <YYYY-MM-DD HH:MM, set by the hook on every write, never hand-authored>
---
```

**Body:** the synthesis, in structural markdown. Every claim traces to a source or another page by a file-relative body link. Those body links are the synthesis's dependency set: staleness flags the synthesis when one of them is updated more recently. Derivations not linked in the body are invisible to the check. External sources with no page are cited inline at the claim (author-year and DOI), not gathered into a section. Add sections beyond the synthesis when the material warrants (comparison tables, open questions, worked examples).

Lead with the idea in plain language before any notation. Technical readers outside the source's field should be able to follow the argument without opening every link. The links give provenance and depth, the prose gives the argument. Define terms specific to one field at first use.

Syntheses are wiki: revise them as the picture sharpens. If the backing evidence is removed, the claim is invalid. Fix it, or delete it and let git hold the history.
