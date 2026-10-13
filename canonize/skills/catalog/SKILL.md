---
name: catalog
description: Catalog a source into the project. A paper, report, code repo, dataset, or colleague's note you read. Owns placement (which tags) and writes the entry to pages/. Use when the user has read something worth keeping, or dropped in one or many sources.
---

**First**, orient with /canon. Raw sources live in `docs/raw` unless told otherwise.

When it is unclear which source the user means, ask, and never pick one yourself. That
covers a citation matching more than one work (two Grabowski 2024 papers), a search with
no clear match, and a loose pointer such as "that HIV paper". List the candidates in the
question.

## Sources named by citation

A request that names a source with no file or URL ("catalog Grabowski 2024", a title,
a bare DOI) is looked up with the tool the user named, or with whatever literature tools
the session can reach when they named none. A DOI then takes the DOI route in
`gated/url.md`.

## Gated routes

Cataloging a file is gated on the file at hand or on how the user asked. Check every
source against this table before reading. On a match, read the named doc and follow it.
Routes that depend on tools outside this skill state their own requirements.

**.pdf**: `gated/pdf.md`
**.docx**: `gated/docx.md`
**.bib**: `gated/bibtex.md` (a bibliography file, wherever it came from)
**directory containing `.git/`**: `gated/git.md`
**"from Zotero"**: `gated/zotero.md`
**a URL**: `gated/url.md`

Gated docs that write `scripts/<name>` mean `${CLAUDE_SKILL_DIR}/scripts/<name>`. Run them
from that absolute path.

## Source directory names

When extraction gives a source its own directory under `docs/raw/`, name the directory with
a slug, and the copy of the source file inside takes the same stem:
`docs/raw/smith-2022-trachoma/smith-2022-trachoma.pdf`.

The slug is the BibTeX or Zotero citation key when the source came with one. Otherwise
build it in kebab case from the first author's surname, the year, and the first distinctive
word of the title: `smith-2022-trachoma`. Sources with no author or year take a short
descriptive name in the same form, such as `dhs-kenya-2022`.

Never name a directory with a DOI. The slash after the prefix splits it into two
directories.

## Cataloging steps (TODO per source)

1. **Preprocess.** Apply the gated route. Everything downstream reads what the route says
    to read: the PDF copy for a PDF, the extracted content for other formats. **NEVER**
    read a raw file directly when its route sends it through a script.
2. **Read and discuss.** Read the source, then talk the key takeaways over with
    the user before writing. What matters here, what's surprising.
3. **Judge fit.** Read the current tags off `glossary.md` and reuse first. New tags that
    extend an existing family (another STI beside `ct`, `ng`, `syph`; another
    intervention beside its siblings) are added to the vocabulary unilaterally: write their
    lines into the `## Tags` list, and report them. Every other new tag needs the user's
    approval before you add it. Present the tags as a table: tag, description, and whether
    it already exists, is newly added, or needs sign-off.
4. **Write** the entry to `pages/` following `canon/formats/entry.md`: the lead prose, the
    key points, the **relevance to project** section (what the source is for here:
    a target, a prior, a bound, a comparator), limitations, and the tags from step 3.
    **Match the style to the source**, but keep the language to a more general audience
    with the project's glossary in mind.

When cataloging, read only the source and the tag vocabulary, nothing else. Do not
cross-check against other pages, propose syntheses, or hunt for conflicts. Cataloged
sources should have a flat cost as the canon grows.

Cataloging works the `# Catalog` thread in the ledger, whose next steps are extract and
catalog. Bib status stays out of it, since `process_bib.py pending` reports it on demand.

## Abstract only

When the full source cannot be had, cataloging from the abstract and metadata is allowed
once the user agrees to it. Ask before writing, showing the abstract in the ask. Step 2
then discusses the abstract rather than a reading, and the page carries the
`basis: abstract` marking `canon/formats/entry.md` specifies.

## Many sources (batch)

When requested, or above 10 sources, suggest batching them for subagents. One subagent
handles 5 to 20 sources efficiently, so suggest groups of 10. A PDF read directly costs
far more context than extracted text, so suggest groups of about 5 when most of the
sources are PDFs.

The sources run in listed order.

1. **Resolve the list.** `process_bib.py pending` for a bib file, otherwise the files the
    user pointed at. Its order is the batch's order.
2. **Extract** the whole batch with a throwaway script in the scratch directory. It loops
    the resolved list and gives each source its own directory under `docs/raw/`. PDFs are
    copied in. Other files go by suffix to the extractor their gated route names,
    defaulting to 4 jobs at a time.
    Check the machine before raising that. Read the failures, then mark the rest extracted
    through the bib gate where one applies.
3. **Build one project brief** from `index.md` or summarized by an agent, so each
    cataloging agent can write the relevance-to-project section without reading the canon.
4. **Dispatch** one group at a time, one cataloging agent per group: it loads /canon and
    /catalog, takes the brief and the path to read for each source, and runs the Judge fit and Write
    steps on each source. Every source is cataloged on its own, with no cross-reference
    between the sources in a group.

Cataloging agents tag their own pages, and must be instructed not to modify `glossary.md`.
They return every new tag instead: the tag, its description, and the pages it went on, so
you can reconcile them. To do so:

- When two near-identical tags are proposed, settle on one form
- Propose the list of new tags for approval
- Retag where tags were denied or merged
- Write the new tags to `glossary.md`

The flat cost holds for you too. Every agent's return lands in your context, so conflicts
between sources surface for free, and a conflict between two sources moves neither extract
nor catalog. Put the ones you notice in the reply to the user, and write them nowhere.

Then `compile`, `check`, and commit.
