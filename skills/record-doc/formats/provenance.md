# Provenance format

A provenance page records why a parameter has the value it does. The why lives here in the wiki; the value itself, the what, lives in the model's code.

File: `topics/<topic>/<name>.md`, type `provenance`.

**Frontmatter:**

```
---
type: provenance
title: <the parameter>
description: <one line: the value and how it was obtained>
timestamp: <ISO 8601, stamped once at creation>
tags: [<topic names and cross-cutting themes>]
derived_from: [<root-anchored links to the finding, source, or DR the value rests on>]
code_site: <path and symbol where the value lives in code>
---
```

`derived_from` is the evidence beneath the value, the typed relation a trace and `audit-code` walk. `code_site` names where the value lives in code, so `audit-code` can check the two against each other.

**Body:**

- the parameter and what it represents
- how the value was obtained, one of: `measured` (literature reports it directly), `derived` (built from proxy evidence through an inference step), `calibrated` (fit to model output against targets), `assumed` (expert judgment, no data — flag loudly)
- the basis, by root-anchored link

Additional sections are fine when the parameter's provenance warrants them. Do not record a lifecycle stage by hand. The stage (prior, calibrated) is read off the evidence: sources only reads as a prior; a calibration finding existing reads as calibrated. There is no step that advances it.
