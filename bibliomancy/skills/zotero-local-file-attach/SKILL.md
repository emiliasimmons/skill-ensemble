---
name: zotero-local-file-attach
description: Attach a local file (PDF, supplement, dataset) to Zotero through the desktop app on port 23119, bypassing api.zotero.org and its storage quota. Use instead of the zotero MCP's zotero_attach_file and zotero_add_from_file, which route uploads through the cloud and fail on the free tier. Use when the user wants a file on an existing library item, or wants a new item created from a PDF they already have.
---

# Zotero local file attach

The MCP's attach tools push bytes to api.zotero.org, so a local-storage library without WebDAV hits the free-tier quota and gets a `413` — often swallowed, leaving an empty attachment shell that looks like success. Everything here talks to the running desktop app instead, so the file lands in `~/Zotero/storage/` directly.

Reach for this whenever a file needs to enter Zotero. The MCP's other tools are unaffected: use them for metadata, search, notes, and annotations.

## Pick the route

Zotero listens on port 23119 with two servers, and they differ in one way that decides everything: whether the target item already exists.

**Existing item — `attach`.** The local Web-API mirror at `/api/`. Needs Zotero 10 or newer.

```bash
python3 ~/.claude/skills/zotero-local-file-attach/scripts/zotero_attach.py attach <itemKey> <file>
```

The first write pops an approval dialog in Zotero. Tell the user it is coming and to click **Always Allow**, which mints a key the script keeps in `~/.cache/zotero-attach/local-api-keys.json` and reuses on later runs. Plain Allow mints a single-use key instead, so they get a dialog per write. If a run stalls with no output, a dialog is waiting for them.

`probe` reports whether a remembered key is on hand. Clearing write authorizations in Zotero's Settings → Advanced invalidates it; the next write then shows the dialog once more.

**New item — `save`.** The connector endpoints at `/connector/`, the same ones the browser extension uses. No version floor, no key, no dialog. Write the item metadata to a JSON file first ([building it from OpenAlex](#metadata-from-openalex)), then:

```bash
python3 ~/.claude/skills/zotero-local-file-attach/scripts/zotero_attach.py save <metadata.json> <file>
```

This route cannot reach a pre-existing item — the attachment binds to the session that created the item, and there is no way to point that session at an arbitrary item key. It also renames the file to Zotero's own filename template, where `attach` keeps the name on disk.

So: `save` is the fallback only when the library is on Zotero 9 or older, and only for a new item. On Zotero 9 with an existing item, neither route works; say so rather than substituting a new duplicate item for the one the user meant.

When unsure what the installed Zotero supports:

```bash
python3 ~/.claude/skills/zotero-local-file-attach/scripts/zotero_attach.py probe
```

## Before creating a new item

`save` adds an item unconditionally, so a paper already in the library becomes a duplicate that only shows up later in Zotero's duplicates pane. Search the library for the DOI or title first, and if it is there, use `attach` against that key.

## Metadata from OpenAlex

When the file is a paper and its metadata is not already to hand, resolve it with `openalex-search` rather than reading it off the PDF. Its `get` takes a DOI and is free and unmetered:

```sh
python3 ~/.claude/skills/openalex-search/scripts/openalex.py get 10.1128/msystems.00877-19
```

That prints a compact listing plus a `key:` slug, and `--bibtex` gives a BibTeX entry. Neither is a Zotero item, so translate into the JSON `save` wants:

| BibTeX / listing | Zotero item field |
|---|---|
| `title` | `title` |
| `author`, `and`-separated | `creators`, one `{"creatorType": "author", "firstName", "lastName"}` each |
| `journal` | `publicationTitle` (`itemType` is then `journalArticle`) |
| `year` | `date` |
| `doi` | `DOI`, bare, no `https://doi.org/` prefix |
| `key:` slug | `extra`, as a `Citation Key: <slug>` line |

Set `url` to the publisher page if you have one; `save` derives the attachment's internal match key from it, and Zotero shows it on the item. Keeping the `Citation Key` line matters because the MCP's `zotero_search_by_citation_key` falls back to scanning `Extra` for exactly that.

Resolve the DOI before writing any of it. Never assemble an item from metadata you have not seen in output — a fabricated DOI is worse in a library than a missing one.

## Confirm it landed

Neither route is finished when the script exits zero. Read the attachment back — `zotero_get_item_children` on the parent, or `zotero_get_attachment_path` — and check the file exists at the reported path with the size you expect. An attachment item with no bytes behind it is the exact failure this skill exists to avoid.
