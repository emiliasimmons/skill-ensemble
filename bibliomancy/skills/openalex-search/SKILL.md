---
name: openalex-search
description: Search the OpenAlex catalog of 270M+ scholarly works: find papers by topic, meaning, author, institution, journal, or citation relationship, and export results as BibTeX. Use when the user wants to find literature, look up a paper or DOI, trace who cites a work, survey an author's or institution's output, or gather sources to ingest into a canonize wiki. Also use when another skill needs a DOI or reference metadata resolved from a description or partial citation.
---

# OpenAlex Search

Every request needs an API key. If `check` reports no key, run **Setup** before anything else.

Run the script by the absolute path shown below, verbatim.

```sh
python3 /Users/emilias/.claude/skills/openalex-search/scripts/openalex.py check
```

## Setup

Runs once, when `check` reports no key found.

1. Send the user to https://openalex.org/settings/api to register (free, ~30 seconds) and have them paste the key back.
2. Ask where they want it stored, and offer these three. The script reads them in this order, so the first one present wins:

   | Store | Write it with |
   |---|---|
   | macOS Keychain | `security add-generic-password -s openalex-api-key -a "$USER" -w 'KEY'` |
   | File | `printf '%s' 'KEY' > ~/.claude/.openalex-key && chmod 600 ~/.claude/.openalex-key` |
   | Env var | export `OPENALEX_API_KEY` from their shell config |

   `~/.claude` is a git repository: if they pick the file, confirm `.openalex-key` is gitignored before writing it.
3. Offer to record the location (never the key) in `~/.claude/CLAUDE.md`, so a future session finds it without re-asking.
4. Re-run `check`. It prints the corpus count and the store it read from.

Never echo the key back, never paste it into a file the user didn't choose, and never commit it.

## Searching

Default to keyword. Reach for `--semantic` when the user's need is conceptual and the vocabulary is uncertain: a paragraph-length description of an idea, a grant aim, an abstract to find neighbours of. Keyword wins when they know the terms, need exhaustiveness, or want more than 50 results.

```sh
python3 /Users/emilias/.claude/skills/openalex-search/scripts/openalex.py search "CRISPR off-target effects" --year '>2020' --oa --limit 50
python3 /Users/emilias/.claude/skills/openalex-search/scripts/openalex.py search "$(cat aim.txt)" --semantic --year '>2015'
python3 /Users/emilias/.claude/skills/openalex-search/scripts/openalex.py search "malaria vector control" --sort cited_by_count:desc --limit 10
```

Semantic costs the same per call as keyword ($0.001) and is capped at 50 results, so choose on fit, not price. It is beta: treat a thin or odd result set as a reason to retry with keyword rather than as evidence the literature is thin.

The real cost asymmetry is elsewhere: a filter-only call is $0.0001, ten times cheaper than either search. When the user's constraint is a field rather than a phrase (an author's works, everything in a journal, a year range), filter and pass no query.

```sh
python3 /Users/emilias/.claude/skills/openalex-search/scripts/openalex.py search "" --filter authorships.author.id:A5023888391 --year 2020-2024
```

Every call prints its own cost to stderr. The free allowance is $1.00/day (1,000 searches), and single-work lookups by DOI or ID are free and unmetered.

### Resolve names to IDs first

Filtering on a display name silently returns the wrong thing. Names are ambiguous; IDs are not.

```sh
python3 /Users/emilias/.claude/skills/openalex-search/scripts/openalex.py resolve author "Jennifer Doudna"
python3 /Users/emilias/.claude/skills/openalex-search/scripts/openalex.py resolve institution "Gates Foundation"
```

Take the returned ID into `--filter authorships.author.id:A…`. When several candidates share a name, show the user the works counts and ask rather than guessing.

`get` accepts any entity and infers the type from the identifier, so an ID from `resolve` gives the full record: ORCID and h-index for an author, ROR and country for an institution, ISSN and APC for a journal.

```sh
python3 /Users/emilias/.claude/skills/openalex-search/scripts/openalex.py get A5023888391
python3 /Users/emilias/.claude/skills/openalex-search/scripts/openalex.py get issn:2167-8359
```

### Counting instead of listing

When the question is "how many" or "how has this changed", group. One call returns the whole distribution at filter price, where listing the works to count them yourself costs more and truncates at `--limit`.

```sh
python3 /Users/emilias/.claude/skills/openalex-search/scripts/openalex.py group publication_year --query "doxycycline prophylaxis"
python3 /Users/emilias/.claude/skills/openalex-search/scripts/openalex.py group topics.id --filter authorships.institutions.id:I4210088555
python3 /Users/emilias/.claude/skills/openalex-search/scripts/openalex.py group open_access.oa_status --year 2023
```

Any filterable field groups, so `type`, `authorships.institutions.country_code`, and `primary_location.source.id` all work. Year fields print oldest-first and `--limit` keeps the most recent; everything else ranks by count. Percentages are shares of all groups, not just the shown ones.

Adding `--query` upgrades the call to search price. Omit it when a filter expresses the constraint.

### Looking up many at once

```sh
python3 /Users/emilias/.claude/skills/openalex-search/scripts/openalex.py batch --file docs/sources/refs.txt
```

Fifty IDs per call, mixing DOIs and OpenAlex IDs freely. DOIs that matched nothing are listed on stderr, so `--bibtex` output stays a clean `.bib` while you still learn what is missing. That report is the answer to "which of these references does OpenAlex know about" — the check worth running before trusting a bib export to dedupe.

### Following citations

```sh
python3 /Users/emilias/.claude/skills/openalex-search/scripts/openalex.py get 10.1038/s41586-021-03819-2
python3 /Users/emilias/.claude/skills/openalex-search/scripts/openalex.py cited-by 10.1038/s41586-021-03819-2 --limit 25
```

`get` is free and prints `related_works` IDs, the cheapest way to widen from one known-good paper. `cited-by` is a filter call, not a search, so forward citation chasing is cheap; do it freely.

Full filter and field reference: [`references/api.md`](references/api.md).

## Reporting results

Give the user the compact listing, not raw JSON. Each result carries a `key:` slug (`jumper2021`) that doubles as a BibTeX key and a canonize page filename.

State the result count and what you searched. When a search returns far fewer results than expected, say so and name the constraint you suspect: a `--year` bound and a misresolved ID fail identically from the outside.

Never present a work you have not seen in output. If the user names a paper you cannot find, say it is not in OpenAlex rather than reconstructing plausible metadata; fabricated DOIs propagate into the wiki and are hard to unpick later.

## Handing off to canonize

Stop at metadata. Placement, tagging, and frontmatter belong to `ingest-source`, which delegates writes to `record-doc`. Do not write wiki pages from here.

Emit BibTeX and let the existing bib machinery take it, since that path already dedupes on normalized DOI and tracks status:

```sh
python3 /Users/emilias/.claude/skills/openalex-search/scripts/openalex.py search "doxycycline prophylaxis" --year '>2022' --bibtex > docs/sources/openalex-<topic>.bib
```

Then invoke `ingest-source` on that file. For a single paper, hand over the DOI and let `ingest-source` decide the topic.

DOI is canonize's preferred `resource` value, so prefer results that have one. A work without a DOI needs its OpenAlex URL as the fallback `resource`; flag that to the user, because it means no dedup against a future bib export.
