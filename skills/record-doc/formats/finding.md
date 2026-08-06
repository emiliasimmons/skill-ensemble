# Finding format

A finding is the result of an analysis you ran. It carries enough detail to understand the claim, cite the key numbers, and re-run it without opening the full analysis record.

This is the shared contract between canonize and any external tool that produces findings (e.g. a calibration plugin's experiment-close step): name the type, provide the content, `record-doc` handles conformance.

File: `findings/<short-name>.md`, or `findings/<workspace>/<short-name>.md` when the project uses workspaces (the current repo's workspace is named in the `## docs` steering block). The filename mirrors the analysis artifact it came from. Type `finding`.

**Frontmatter:**

```yaml
---
type: finding
title: <the question the analysis answered, as a short phrase>
description: <one-line result>
timestamp: <ISO 8601 with time, stamped once at creation>
tags: [<topic names and cross-cutting themes, e.g. calibration, zimbabwe>]
resource: <path to the full analysis record, e.g. experiments/02_syph/SUMMARY.md>
derived_from: [<file-relative links to the sources or findings it builds on>]
---
```

`tags` place the finding into every hub it bears on. `resource` (optional) points to the full record — a SUMMARY, notebook, or script output — one click away for figures and full detail. `derived_from` is the typed relation a trace walks.

**Body:**

```markdown
## Question
<what the analysis asked, one paragraph>

## Method
<pointer to the re-runnable artifact — committed script or notebook path. Never paste the code.>

## Inputs
<data sources, settings, parameter values as they were run — enough for a trace to rebuild the result>

## Result
<headline result with key numbers, one to three sentences>

## Key observations
<the 2-3 observations that bear on downstream decisions>
```

Content level: enough to brief a colleague from the finding alone. For simple findings, Inputs and Key observations may be omitted if Result is self-contained. Additional sections are fine when the analysis warrants them. A finding is immutable unless you re-run it. A validation result — whether the model reproduces a real-world target — is a finding like any other.
