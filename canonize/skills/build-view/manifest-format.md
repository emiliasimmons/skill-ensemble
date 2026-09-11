# View manifest format

A manifest is the contract for one bespoke view. It lives at `docs/views/<name>/manifest.md` and is read by `build-view` to know how to compile and refresh the view.

Nothing in the frontmatter is domain-specific. Every field is settled in the interview.

```yaml
---
type: view
title: <view name>
description: <one line: what the view shows>
updated: <YYYY-MM-DD HH:MM, set when the manifest is written>
status: registered            # one-shot | registered
unit: <what one extraction represents, omit if none>
store: <pages | csv | json | table | ...>
applies_to: <which sources feed it, e.g. { tags: [nutrition, tb] }>
refresh: <the procedure to re-run, e.g. graph.py | ./extract.py | manual>
output: <file(s), or none>
---
# Codebook

<the dimensions + controlled vocabulary the extraction must fill. This body is the only extraction instruction>
```

Notes:

- `type: view` is a meta-type for view configuration, distinct from the knowledge types. `docs/views/` sits outside the canon, so a manifest is neither checked for conformance nor drawn in the graph.
- `status: registered` means the view is living and refreshed on request. `one-shot` means it was compiled once and is not maintained. Refresh is always pull, never triggered by cataloging.
- `applies_to` is declarative (tags, a path glob, a list of ids) so a refresh decision is cheap.
- `refresh` names the procedure that rebuilds the view's data and leaves the rendered page fixed. Do not regenerate the page on refresh.
