---
name: build-view
description: Design and build a bespoke view over the canon. A dashboard, map, or chart driven by an extraction from the pages. Use when the user wants a new view built or an existing one changed. Not for the wiki at docs/index.html, which canon rebuilds on its own.
---

<!--Right now I'm not convinced this skill does anything worth doing. If it does, it should probably work out clearly where to write the script and where it should live, which it half does.-->

Bespoke views live under `docs/views/<name>/` and are always generated, never
hand-edited.

Interview the user until these settle (one question per turn, each with your recommended
answer, and wait for the answer before the next):

- **what feeds it** (`applies_to`): which sources or pages
- **the unit of extraction**: one claim / one parameter / all parameters / …
- **the fields + controlled vocabulary**: the codebook
- **the storage target** (`store`): pages / csv / json / inline table / …
- **the output**: the file(s)

Record the settled design in a manifest at `docs/views/<name>/manifest.md` (format:
`manifest-format.md` in this skill's directory). The manifest's Codebook is the only
extraction instruction.

Then build the pipeline. Bespoke views are always a script (or a set of scripts) running
extraction, data, visualization, and they must be re-runnable on their own, without an
agent.
Write the extractor(s) into `docs/views/<name>/`: they read the canon (frontmatter, or
values parsed out of bodies) and emit the data file the page renders. Write the
D3/Leaflet/etc. page each time.

The one exception is when the extraction itself needs the agent (sentiment analysis, or
any judgement an LLM has to make). Do not wire that through chat. Recommend an agent SDK
for that step.

To change an existing view, load its manifest and scripts and change them directly.

## Refresh

Views join the compile cycle by putting a `refresh.py` in their directory calling whatever
extractors they need. Canon runs `docs/views/*/refresh.py` after every compile, so every
view is current once pages are recorded. The rendered page stays fixed. Only the data
underneath is regenerated.
