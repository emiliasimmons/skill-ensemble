# Zotero-managed sources

Requires a connected Zotero MCP server. Reads need Zotero's local API enabled (Settings → Advanced → *Allow other applications on this computer to communicate with Zotero*); on `403 Local API is not enabled`, tell the user and stop. Writes additionally need hybrid mode (`ZOTERO_API_KEY` + `ZOTERO_LIBRARY_ID`); without it, `Cannot perform write operations in local-only mode` is the expected failure and nothing here depends on it.

"From Zotero" is the gate. Any selector the user names is a valid one.

Resolve script paths relative to the skill directory (`$S` = `<skill-dir>/scripts`).

## Selection

| Selector | Resolution |
|---|---|
| a collection | `zotero_search_collections` for the key, then `zotero_get_collection_items` |
| named items | `zotero_search_by_citation_key`, a DOI, or `zotero_semantic_search` |
| a tag | `zotero_get_tags` first: list the matches with counts and confirm which one before `zotero_search_by_tag` |
| the last N added | `zotero_get_recent`, filtering out notes and loose attachments by `itemType` |

Most tags come from publisher metadata rather than the user, so a tag selector usually needs the disambiguation step before it resolves to a set.

## Materializing the selection

Write the resolved items to `docs/sources/zotero-<selector>.bib`, where `<selector>` is the collection or tag name slugified, or `recent`. Re-running a selector overwrites the file; `bib_status.json` persists across rewrites and keys on DOI, so ingestion status survives and the overwrite shows what the selector picked up since last time.

`zotero_export_bibliography` renders through Zotero's web API. Without web credentials, assemble the file from per-item `zotero_get_item_metadata(item_key=..., format='bibtex')`.

From here the `bibtex.md` pipeline runs on that file, with the substitutions below.

## Per item

**Metadata** comes from `zotero_get_item_metadata`, not the bib entry. The bib file only identifies items.

**Retraction.** Run `scite_check_retractions` before writing anything. A retraction changes whether the source belongs in the collection; surface it to the user.

**Content.** `zotero_get_attachment_path` gives the attachment's real path on disk — use it rather than a `file:` field, and never ask the user to resolve a path Zotero can answer. Then extract normally:

```sh
uv run $S/extract_pdf.py <attachment-path> -o docs/sources/<bibtex_key>/
```

With no local attachment, fall back to `zotero_get_item_fulltext` (page-limited, and it returns the whole text into context rather than to disk). Record which path was taken:

```sh
uv run $S/process_bib.py mark docs/sources/zotero-<selector>.bib extracted <key>
uv run $S/process_bib.py mark docs/sources/zotero-<selector>.bib extracted <key> --via zotero
```

**Annotations.** Pull `zotero_get_annotations` and `zotero_get_notes` before discussing the source. The user's own highlights are the best available signal for which points matter to this project; lead the step-2 discussion with them.

For a long source, `zotero_get_pdf_outline` and `zotero_read_pdf_pages` read a named section without pulling the whole text.
