---
name: build-view
description: Design and build a bespoke view over the corpus — a dashboard, map, or chart driven by an extraction from the pages. Use when the user wants a new view built or an existing one changed. Not for the wiki at docs/index.html, which canon rebuilds on its own.
---

A bespoke view lives under `docs/views/<name>/` and is always generated, never hand-edited.

Interview the user until these settle — one question per turn, each with your recommended answer, and wait for the answer before the next:

- **what feeds it** (`applies_to`) — which sources or pages
- **the unit of extraction** — one claim / one parameter / all parameters / …
- **the fields + controlled vocabulary** — the codebook
- **the storage target** (`store`) — pages / csv / json / inline table / …
- **the output** — the file(s)

Record the settled design in a manifest at `docs/views/<name>/manifest.md` (format: `manifest-format.md` in this skill's directory); the manifest's Codebook is the only extraction instruction.

Then build the pipeline. A bespoke view is always a script — or a set of scripts — running extraction → data → visualization, and it must be re-runnable on its own, without an agent. Write the extractor(s) into `docs/views/<name>/`: they read the corpus (frontmatter, or values parsed out of bodies) and emit the data file the page renders. Write the D3/Leaflet/etc. page each time.

The one exception is when the extraction itself needs the agent — sentiment analysis, or any judgement an LLM has to make. Do not wire that through chat; recommend an agent SDK for that step.

To change an existing view, load its manifest and scripts and change them directly.

## Refresh

A view joins the compile cycle by putting a `refresh.py` in its directory calling whatever extractors it needs; canon runs `docs/views/*/refresh.py` after every compile, so every view is current once pages are recorded. The rendered page stays fixed; only the data underneath is regenerated.
