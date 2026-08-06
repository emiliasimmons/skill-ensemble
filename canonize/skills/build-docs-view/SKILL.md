---
name: build-docs-view
description: The wiki at docs/index.html — an interactive knowledge graph and file browser over the corpus, rebuilt by every canon compile — and bespoke dashboards built on request. Use when the user wants to change how the wiki looks, register an external source, or design a new view.
---

## The wiki

`docs/index.html` is the bundle's reading surface. `canon compile` rebuilds it every time, so it needs no request and no separate command; `graph.py --root docs` in this skill's directory rebuilds it alone. Data goes to `docs/views/wiki/corpus.js`; the viewer — `view/view.js`, `view/view.css`, `view/vendor/` — stays in this skill's directory and is referenced, not copied. Everything is local; no network at view time.

Three panes, each toggled from the bar and separated by draggable dividers: a file listing grouped by source and folder, the graph, and the rendered markdown of whatever is selected. Links inside a body select the page they point at, so the panel walks the corpus. Missing link targets render struck through in red. The search box takes `tag:` and `type:` facets alongside free words.

Pages become nodes; `.md` links and the typed relations (`derived_from`, `bears_on`, `supersedes`) become edges, each carrying its kind. Links inside a compiled roster become `member` edges.

The graph opens collapsed: one node per topic and per register, plus one per external source, sized by member count and tied to each other by shared membership. Clicking a node reads it. Expanding is a separate act — hovering a group raises a bubble that adds 25 members at a time or collapses, and the reader's header carries the same controls. Members are ranked by how many nodes already on screen they touch. Membership is reference-counted, so collapsing a topic leaves behind whatever another open topic also holds.

Node size carries degree and a border marks distance from whatever is being read. Each group takes its own hue and other nodes are colored by type. Dragging a node pins it there; double-clicking releases it. The open set, the reading position and pinned coordinates live in the URL hash as unreserved characters, so a scene can be pasted anywhere. Structural edges hide from the settings menu.

Arriving nodes grow in and their edges come up from no force at all, so an expansion resolves over about a second rather than in one frame; collapsing runs the same ramp backwards. The viewport is fit once, when the page first has a size, and nothing moves it afterwards except selecting a node that is off screen.

`view/physics.js` holds every layout number: the force defaults, the range and step of each `?debug` slider, the animation durations, damping, and how far a new member is seeded from its group. Change one and reload.

### Sources

The bundle feeds the graph on its own. External trees come from the `External sources` block of `schema.md`, the same list `canon check --links` validates citations against:

```
sources:
  - name: experiments
    root: ../other-repo/experiments
    include: README.md=experiment, SUMMARY.md=summary
```

`root` is relative to the project root. `include` maps a filename to the node type it becomes. A row may also set `collector` (`tree` by default, `canon` for a second conformant bundle) and `prefix` (the node-id namespace, the source name by default).

`canon compile` writes each registered tree a roster page at `docs/<name>.md` and lists it from the index, so the outside files hang off a page in the corpus rather than off the side of the graph. The roster is compiled; the prose above it is not.

Links resolve across sources by filesystem path, so a page and an outside file that link to each other become an edge in both directions. Images referenced from any body render in the panel from wherever they sit on disk.

Add a collector for a source neither handles by writing a function in `collectors.py` that returns `Doc` records and registering it in `COLLECTORS`.

### Changing how it looks

Edit the viewer in this skill's directory; every project picks the change up on its next compile. `physics.js` is the layout's numbers, `model.js` derives groups, adjacency and aggregate ties from the corpus, `scene.js` holds the visible set and the force simulation, `encode.js` draws nodes and edges, `panes.js` owns the file list and reader, `view.js` wires them and the bar. Colors come from CSS variables at the top of `view.css` and are read back in `encode.js`, so a palette change is one place. For a change that should apply to one project only, write `docs/views/wiki/custom.css`, which loads after the stylesheet.

### Portable copy

`graph.py --root docs --bundle` copies the viewer assets and every referenced image under `docs/views/wiki/` and rewrites the paths, making `docs/` self-contained at the cost of its size (roughly 8 MB for a corpus with a few dozen figures). Use it to hand the bundle to someone else; the next `canon compile` reverts to referenced assets.

## Bespoke views

A bespoke view lives under `docs/views/<name>/` and is always generated, never hand-edited.


Write the D3/Leaflet/etc. page each time. Run a /grilling session until these settle:

- **what feeds it** (`applies_to`) — which sources or pages
- **the unit of extraction** — one claim / one parameter / all parameters / …
- **the fields + controlled vocabulary** — the codebook
- **the storage target** (`store`) — pages / csv / json / inline table / …
- **the output** — the file(s)

Record the settled design in a manifest at `docs/views/<name>/manifest.md` (format: `manifest-format.md` in this skill's directory); the manifest's Codebook is the only extraction instruction.

Then build the pipeline. A bespoke view is always a script — or a set of scripts — running extraction → data → visualization, and it must be re-runnable on its own, without an agent. Write the extractor(s) into `docs/views/<name>/`: they read the corpus (frontmatter, or values parsed out of bodies) and emit the data file the page renders.

The one exception is when the extraction itself needs the agent — sentiment analysis, or any judgement an LLM has to make. Do not wire that through chat; recommend an agent SDK for that step.

To change an existing view, load its manifest and scripts and change them directly.

## Refresh

`canon compile` rebuilds the wiki, then runs `docs/views/*/refresh.py`, so every view is current after pages are recorded. A bespoke view joins that by putting a `refresh.py` in its directory calling whatever extractors it needs. The rendered page stays fixed; only the data underneath is regenerated.
