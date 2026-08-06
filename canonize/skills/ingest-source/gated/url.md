# Sources given as a URL

Requires `uv` and network access. Locating open-access fulltext depends on tools outside this skill (an OpenAlex or publisher MCP server, for instance); when none is connected, skip that step rather than reaching for it.

Resolve script paths relative to the skill directory (`$S` = `<skill-dir>/scripts`).

## Dispatch on the URL

| Shape | Route |
|---|---|
| a git host or a repo URL | `gated/git.md` |
| a `.pdf`, or a URL serving `application/pdf` | download to `docs/sources/<slug>/`, then `extract_pdf.py` |
| a DOI, bare or embedded in the path | resolve metadata, then fulltext |
| anything else | fetch and save the readable content as `docs/sources/<slug>/content.md` |

Publisher URLs usually carry the DOI in the path (`onlinelibrary.wiley.com/doi/10.1111/j.1365-3156.1997.tb00164.x`). Extract it and take the DOI route; it yields citable metadata where scraping the page yields a title.

## Resolving a DOI

```sh
curl -sL "https://api.crossref.org/works/<doi>"
```

Title, creators, container title, year, and type populate the `source` frontmatter. `resource` takes the DOI, not the URL the user pasted. The `abstract` field, when present, is JATS XML — strip the tags before showing it to anyone.

## When metadata resolves but the paper does not

The common case for paywalled journals.

1. If a tool that locates open-access copies is connected, try it.
2. Otherwise stop and ask the user for the PDF, either dropped into `docs/sources/` or added to Zotero and ingested through `gated/zotero.md`. Show the resolved abstract in the ask, so they can judge whether it is enough without a round trip.

Never write a source page from metadata and an abstract on your own initiative — the `source` format's key points are meant to be paraphrased from a reading. When the user rules that the abstract suffices, say so plainly in the page's Summary: what was read was the abstract, not the paper.

## After the page is written

When the URL resolved to a DOI and the Zotero library is writable, offer to file it with `zotero_add_by_doi(doi=..., if_exists='file')`. Ask; never do it as a side effect of ingesting.
