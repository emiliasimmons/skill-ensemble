# bibliomancy

Find the paper, then get it into the library — with the metadata right.

Two skills covering the two halves of reference work that agents usually do badly: searching a real catalog instead of recalling citations from memory, and putting files into Zotero without going through the cloud.

## The skills

**openalex-search** — search over OpenAlex's 270M+ works. Keyword or semantic search, filters on any field (author, institution, journal, year, open access), grouped counts for "how many" and "how has this changed" questions, single-work lookup by DOI or OpenAlex ID, and BibTeX export.

Three things the skill exists to enforce:

- Resolve a name to an ID before filtering on it. `authorships.author.display_name` matches the wrong people silently; `authorships.author.id` does not.
- Group instead of listing when the question is a count. One filter-priced call returns the whole distribution; listing works to count them costs more and truncates at `--limit`.
- Never assemble a citation you have not seen in output. A fabricated DOI is worse than a missing one.

Calls are metered ($0.0001 for a filter-only call, $0.001 for keyword or semantic, free for single-work lookup) against a $1.00/day free allowance, and each call prints its own cost. Needs a free API key from https://openalex.org/settings/api; the skill walks through storing it in the Keychain, a file, or an env var, and never echoes or commits it.

**zotero-local-file-attach** — attach a PDF, supplement, or dataset to Zotero through the desktop app on port 23119.

The Zotero MCP's attach tools push bytes to api.zotero.org, so a local-storage library without WebDAV hits the free-tier quota and gets a `413` that is often swallowed, leaving an empty attachment shell that looks like success. This skill talks to the running app instead, so the file lands in `~/Zotero/storage/`.

Two routes, and which one applies depends only on whether the target item already exists:

| Situation | Route | Notes |
|---|---|---|
| Item is already in the library | `attach`, via the local Web-API mirror | Zotero 10+. First write pops an approval dialog; **Always Allow** mints a reusable key. Keeps the filename on disk. |
| Item does not exist yet | `save`, via the connector endpoints | No version floor, no dialog. Creates the item from a metadata JSON file, then attaches. Renames to Zotero's filename template. |

`save` cannot reach a pre-existing item, so on Zotero 9 with an existing item neither route works — the skill says so rather than creating a duplicate.

## How they compose

`save` needs item metadata, and the skill resolves it through `openalex-search`'s free DOI lookup rather than reading it off the PDF, then translates the fields into the JSON Zotero wants (including a `Citation Key:` line in `extra`, which is what the MCP's `zotero_search_by_citation_key` scans for).

`openalex-search` is also the front end for [canonize](../canonize): search, export BibTeX, ingest the result as a source page.

The Zotero MCP's other tools are unaffected — use them for metadata, search, notes, and annotations.
