# OpenAlex API reference

Base URL `https://api.openalex.org`.

## Auth and cost

`api_key` is a URL parameter, required. Free key at https://openalex.org/settings/api.

Allowance is dollar-denominated, not request-denominated: $1.00/day with a key, $0.10/day without. Every list response carries its own price in `meta.cost_usd`.

| Operation | Cost | Daily free ceiling |
|---|---|---|
| Single lookup (`/works/W…`, `/works/doi:…`) | free | unlimited |
| List / filter (`?filter=`) | $0.0001 | 10,000 calls, 1M results |
| Search (`?search=` or `?search.semantic=`) | $0.001 | 1,000 calls, 100K results |
| PDF or XML download | $0.01 | 100 files |

Exhausting the allowance returns 429; it resets daily. Usage detail at https://openalex.org/settings/usage.

The `mailto` parameter and the polite pool were removed in February 2026.

## Query parameters

| Parameter | Notes |
|---|---|
| `search` | Full text across title, abstract, and fulltext |
| `search.semantic` | Vector search, GTE Large EN 1,024-dim, max 50 results, first 2,000 chars matched |
| `search.exact` | Every word must appear, ANDed across the fulltext, not a phrase match |
| `filter` | `field:value`, comma-separated |
| `sort` | `cited_by_count:desc`, `publication_date:desc`, `relevance_score:desc` |
| `per_page` | Max 200, default 25. `per-page` also accepted |
| `page` | Basic paging stops at 10,000 results |
| `cursor` | `cursor=*` to start, then `meta.next_cursor`; required past 10,000 |
| `sample` | Max 10,000; pair with `seed` for reproducibility; excludes `sort` and `page` |
| `select` | Comma-separated fields, shrinks the response |
| `group_by` | Returns counts in `group_by` instead of results |

Only one of `search`, `search.exact`, `search.semantic` per request.

## Filter syntax

| Form | Example |
|---|---|
| Single | `publication_year:2024` |
| AND | `publication_year:2024,is_oa:true` |
| OR | `type:article\|book` (max 100 values) |
| NOT | `type:!paratext` |
| Range | `publication_year:2020-2024` |
| Comparison | `cited_by_count:>100` |
| AND within one attribute | `authorships.institutions.id:I136199984+I27837315` |

## Useful work filters

| Filter | Use |
|---|---|
| `authorships.author.id` | One researcher's output |
| `authorships.institutions.id` | One organization's output |
| `primary_location.source.id` | One journal or repository |
| `topics.id` | Subject classification |
| `cites:W…` | Works citing that work: forward citations, who built on it |
| `cited_by:W…` | Works that work cites: its own reference list, backward |
| `doi`, `openalex`, `orcid` | Bulk lookup, up to 50 piped values |
| `publication_year`, `cited_by_count`, `is_oa`, `type`, `has_fulltext` | |

Field-scoped search filters (`title.search`, `abstract.search`, `title_and_abstract.search`, `fulltext.search`, `default.search`, `keyword.search`, `raw_affiliation_strings.search`, and their `.no_stem` variants) are **deprecated**. Use the `search` parameter.

## Entity endpoints

`/works` `/authors` `/sources` `/institutions` `/topics` `/keywords` `/publishers` `/funders`, each with `/{id}` for single lookups, plus `/autocomplete/{entity}` for typeahead.

Removed or superseded: `/concepts` (use `/topics`), the `/text` endpoint (gone), `host_venue` (use `primary_location`), `grants` (use `funders` and `awards`).

## External identifiers

```
/works/doi:10.1234/example        /works/pmid:29456894
/authors/https://orcid.org/0000-0001-6187-6610
/institutions/https://ror.org/0161xgx34
/sources/issn:2167-8359
```

## Response shape

```json
{ "meta": { "count": 286750097, "page": 1, "per_page": 25,
            "next_cursor": "…", "cost_usd": 0.001 },
  "results": [],
  "group_by": [] }
```

Abstracts arrive as `abstract_inverted_index`, a word→positions map, not a string. Sort the `(position, word)` pairs to rebuild the text; `openalex.py --abstract` does this.

Singleton lookups return the entity object with no `meta` block.
