# Source format

A source is something external you read: a paper, a guideline, a code repository, a dataset. The raw file lives in `sources/`; the summary — the knowledge object — lives under the topic it belongs to. Nobody browses PDFs; the summary is what the project knows.

File: `topics/<topic>/<short-name>.md`, type `source`.

**Frontmatter:**

```
---
type: source
title: <the source's name>
description: <one line: what it is and what it bears on>
resource: <DOI or stable URL preferred; else the local sources/ path>
timestamp: <ISO 8601 with time, stamped once at creation>
tags: [<cross-cutting themes beyond its home topic>]
---
```

`resource` follows the ordering rule: a web-accessible canonical identifier first (DOI for academic works, else a stable URL), then the local `sources/...` path only when nothing web-accessible exists. The home topic is the directory the summary sits in; `tags` add any other hub it should surface in.

## Body

Open with unheaded lead prose: what the source is, and where the raw file sits (`/sources/...`). Then two sections every source carries, whatever its kind:

- **Bearing on this project** — what the source can be used for here, and what it cannot. Name the specific use: a calibration target, a prior, a bound, a comparator. Where it conflicts with or duplicates another page, say so and link it.
- **Citations** — numbered, where external sources or sibling pages back the summary.

Everything between them follows the kind of source. Take the matching profile; add or drop sections as the material warrants.

**Academic article**

- **Key points** — what matters to this project, in your own words. Paraphrase; do not paste long passages.
- **Limitations** — the source's own, and any bearing on the use named above.
- **Methodology** — where the design decides how far the numbers travel.
- **Extraction notes** — where the extracted text or tables came out wrong: what is corrupt, and what to read instead.

Every figure carries its denominator and population — sex, age band, year, and the sampling frame it was measured in. A number without its denominator is not usable and is not recorded as if it were.

**Guideline or report**

- **What it recommends** — the operative recommendation, and the population it applies to.
- **Strength and basis** — the evidence grade, and what it rests on.
- **Key points** and **Limitations** as above.

**Code repository**

- **What the project uses** — the modules, classes, or parameters this project draws on.
- **Architecture** — the structure a reader needs to follow the above.
- **Not used** — capabilities present but deliberately unused, and why.
- **Extension points** — where this project hooks in.

**Dataset**

- **What it contains** — variables, units, coverage in time and place.
- **Denominator and population** — who is counted, and who is not.
- **Provenance** — how it was collected, and by whom.
- **Limitations** as above.

A source summary is wiki: update it as understanding improves. The raw file does not change.
