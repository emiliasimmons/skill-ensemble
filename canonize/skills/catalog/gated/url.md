# Sources given as a URL

Requires `uv` and network access. Locating open-access fulltext depends on tools outside this skill (an OpenAlex or publisher MCP server, for instance). When none is connected, skip that step.

## Dispatch on the URL

| Shape | Route |
|---|---|
| a git host or a repo URL | `gated/git.md` |
| a `.pdf`, or a URL serving `application/pdf` | download to `docs/raw/<slug>/`, then `extract_pdf.py` |
| a DOI, bare or embedded in the path | resolve metadata, then fulltext |
| anything else | fetch and save the readable content as `docs/raw/<slug>/content.md` |

Publisher URLs usually carry the DOI in the path (`onlinelibrary.wiley.com/doi/10.1111/j.1365-3156.1997.tb00164.x`). Extract it and take the DOI route. It yields citable metadata where scraping the page yields a title.

## Resolving a DOI

```sh
curl -sL "https://api.crossref.org/works/<doi>"
```

Title, creators, container title, year, and type populate the `entry` frontmatter. `resource` takes the DOI, not the URL the user pasted. The `abstract` field, when present, is JATS XML. Strip the tags before showing it to anyone.

## When metadata resolves but the paper does not

The common case for paywalled journals.

1. If a tool that locates open-access copies is connected, try it.
2. Otherwise stop and ask the user for the PDF, either dropped into `docs/raw/` or added to Zotero and cataloged through `gated/zotero.md`. Show the resolved abstract in the ask, so they can judge whether it is enough without a round trip.

Never write an entry from metadata and an abstract on your own initiative. The `entry` format's key points are meant to be paraphrased from a reading. When the user rules that the abstract suffices, catalog it as an abstract-only entry: `basis: abstract` and the note at the top of the body.

## After the page is written

When the URL resolved to a DOI and the Zotero library is writable, offer to file it with `zotero_add_by_doi(doi=..., if_exists='file')`. Ask. Never do it as a side effect of cataloging.
