# Topic format

A topic hub is the level-2 browsing surface: the primary reading path into everything the project knows about one theme. It is a sibling page of its member directory (`topics/seasonality.md` describes `topics/seasonality/`), so it carries frontmatter where an index file could not.

File: `topics/<topic>.md`, type `topic`. Its directory `topics/<topic>/` holds the member source summaries and concepts.

**Frontmatter:**

```
---
type: topic
title: <the topic, title case>
description: <one line: what this topic covers — this is the taxonomy entry>
timestamp: <ISO 8601 with time, stamped once at creation>
synthesized: <ISO 8601 with time, when the synthesis was last written>
tags: [<cross-cutting themes the hub itself belongs to>]
---
```

`description` is the line the root taxonomy block prints, so it earns its brevity. `synthesized` is set when the hub is scaffolded and rewritten only when the synthesis is; `canon` counts members newer than it to decide whether the hub reads as stale. It carries a time because a batch ingested the same day would otherwise be uncountable. A hub missing the field counts every member.

**Body:** two parts.

1. An **authored synthesis** on top: a genuine several-paragraph account of what the project knows about this topic — not a link list. This is the reading payload. Nothing regenerates it mechanically.
2. A **compiled member block** below, owned by `canon`:

```
<!-- compiled:members -->
<!-- /compiled:members -->
```

`canon compile --block members --page topics/<topic>.md` fills it: the topic's source summaries and concepts (physically in its directory) plus every finding and decision tagged to it, listed by file-relative link, grouped by type. Never hand-edit inside the markers.

New topics are always a proposal, never unilateral — minting one is a structural change requiring sign-off. Target 8 to 15 topics for a 150-source project.
