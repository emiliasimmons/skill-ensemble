---
name: ingest-source
description: Bring sources and findings into the project — a paper or dataset you read, or the result of an analysis you ran. Owns placement (which topic, which tags). Use when the user has read something worth keeping, dropped in one or many sources, or wants an analysis result recorded, including a validation result. Delegates every write to record-doc.
---

Orient with /canon.

## Gated filetypes

Some source types are gated. Check every source against this table before reading; on a match, read the named doc and follow its instructions:

**.pdf**: `gated/pdf.md`
**.docx**: `gated/docx.md`
**.bib**: `gated/bibtex.md` (Zotero/Mendeley exports)
**directory containing `.git/`**: `gated/git.md`

## A source you read

Per source — the batch flow below runs this once per source.

1. **Preprocess.** Apply any gated preprocessing (above). Everything downstream works on the extracted content, never the raw file. **This must be done first** - **NEVER** read a matching raw file
2. **Read and discuss.** Read the source, then discuss key takeaways with the user before writing anything. What matters to this project? What's surprising?
3. **Judge fit.** Pick the one primary topic the summary belongs under (its home directory) and the cross-cutting tags. The primary topic is always also a tag. When a source contributes meaningfully to a second topic, add that topic name as a secondary tag; the page will appear in both hubs but live in one directory. The summary is the knowledge object, not the raw file.
4. **Cross-check** against what the project already holds. Look for existing concepts, findings, and decisions the source bears on. Surface what you find:
   - Propose concept pages for strong new connections.
   - For conflicts with accepted decisions or calibrated values, propose concept pages that capture the contradiction.
   - When a concept's synthesis would substantially change, propose a handoff for re-derivation in a fresh context rather than rewriting inline.
5. **When nothing fits,** say so. Explore just enough to confirm novelty, then propose a new topic — never place unilaterally, never force a bad fit. A new topic is a structural change: on approval, /record-doc scaffolds the hub and files the summary.
6. **Write** the summary through /record-doc (type `source`).

## Many sources (batch)

Ask the user's preference before starting:

**One-by-one in chat** (smaller batches): run the per-source flow above on each, discussing each before writing.

**Subagent drafts** (larger batches):

1. Run per-source preprocessing yourself before dispatch, then send subagents to read sources and produce draft summaries with proposed topics and tags. Subagents get extracted content, never raw gated files.
2. Present the drafts to the user for review. Include a placement plan: each source with its proposed topic and tags, flagged misfits, and aggregated new-topic proposals. During adoption with no topics yet, this plan is the proposed taxonomy.
3. Discuss the drafts and placement together. Amend as needed.
4. File approved summaries through /record-doc.
5. Run a single /canon compile at the end rather than per source.

## A finding you ran

Write it through /record-doc (type `finding`): the question, the method as a pointer to the re-runnable artifact (never paste the script), the inputs that mattered, and the result with its diagnostic. When the project has registered workspaces (in `schema.md`), the current repo's workspace routes it to `findings/<workspace>/`.

## Staleness

Past the schema's nudge threshold you may say so once — one line — but never offer to rewrite a synthesis. Rewrites are /curate-docs curation the user schedules.
