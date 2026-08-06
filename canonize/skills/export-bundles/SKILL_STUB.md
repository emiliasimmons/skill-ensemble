---
name: export-bundles
description: Materialize a shareable standalone OKF bundle from a topic. Stub — out of scope for now; the design decisions are banked here but nothing is built. Use only when the user explicitly asks to export a bundle, and tell them it is not yet implemented.
---

**Stub. Not implemented.**

## Banked decisions

- Closure walk starts from a topic hub.
- Output is a standalone OKF bundle written **outside** the project.
- Default posture: summaries and citations, not raw files. `sources/` references are rewritten to their canonical `resource`; raw files travel only behind an explicit flag.
- Out-of-closure links are rewritten to a stub list.
- A synthesized log is generated from git history at export time.

## Unresolved (blocking a build)

- Evidence closure depth: how far `derived_from`/`bears_on` edges are followed out of the starting topic.
- Import round-trip semantics: how an exported bundle re-enters a project without duplicating pages.
