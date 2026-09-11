# Finding format

Findings are the results of analyses you ran, written in enough detail to understand the claim, cite the numbers, and re-run the analysis without opening the full record. They are user-driven: recorded when a result is worth keeping, not spawned automatically.

Findings are location-based: any page under `findings/` is one, so they need no registered `type`. They are still pages, written per /canon, meeting this format, and checked like any page (title, description, tags all required). Tools that produce findings write through the same path. Nothing drops an unchecked file into the tree.

File: `findings/<kebab-title>.md`.

**Frontmatter:**

```
---
title: <the question the analysis answered, as a short phrase>
description: <one-line result>
tags: [<themes>]
updated: <YYYY-MM-DD HH:MM, set by the hook on every write, never hand-authored>
resource: <path to the full record, e.g. experiments/02_syph/SUMMARY.md>
---
```

`resource` points at the full record (a SUMMARY, notebook, or script output), one click away for figures and detail.

**Body:**

```markdown
## Question
<what the analysis asked, one paragraph>

## Method
<pointer to the re-runnable artifact: committed script or notebook path. Never paste the code.>

## Inputs
<data, settings, parameter values as run, enough for a re-run>

## Result
<headline result with key numbers, one to three sentences>

## Key observations
<the 2-3 observations that bear on downstream work>
```

Enough to brief a colleague from the finding alone. For simple findings, Inputs and Key observations may drop if Result stands on its own. Validation results (whether the model reproduces a real-world target) are findings like any other. Findings are wiki: rewrite them when you re-run them, or delete one when it turns out to rest on a bug. Git holds the history.
