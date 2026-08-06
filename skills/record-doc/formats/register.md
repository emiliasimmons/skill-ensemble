# Register format

A register is a wiki page whose body is fully compiled from decision frontmatter. Two exist: assumptions (from `accepted` DRs) and open-decisions (from `provisional` DRs). They are never stale — `record-doc` recompiles the affected register in the same commit as every decision write or supersession, so the root state block is always truthful.

Files: `assumptions.md` and `open-decisions.md` at the bundle root, type `register`.

**Frontmatter:**

```
---
type: register
title: <Assumptions | Open decisions>
description: <one line: what the register compiles>
timestamp: <ISO 8601, stamped once at creation>
---
```

**Body:** an authored line of context if useful, then the compiled block owned by `canon`:

```
<!-- compiled:register -->
<!-- /compiled:register -->
```

`canon compile --block registers` fills both from the DRs' `status` field. Never hand-append a register line — it is overwritten on the next compile. Full recompile is `canon fix`; incremental recompile is a `record-doc` side effect of a decision write.
