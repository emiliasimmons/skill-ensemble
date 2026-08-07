---
name: record-doc
description: Records one conformant page into the project (a decision, finding, source, concept, or any registered type) and regenerates the surfaces that depend on it. Use when the user says "record-doc", wants a decision/finding/source/note filed, or when another skill needs to write a page.
---

**First**, immediately orient with /canon.

## Steps

1. **Resolve the type.** Read the type registry in `docs/schema.md`. The type must already be registered — record-doc never mints one. If the type is unregistered, stop and say so, and suggest a tag if the content is only "kind of its own thing." Load **only** that type's format doc (recording a finding never pays the token cost of the decision format).

2. **Place and name.** The registry `zone` gives the directory. For a `decision`, take the next id from `sequence --kind decision` — never pick a number by hand. For a `source`, `concept`, or `provenance`, the home topic gives `topics/<topic>/`; if its hub does not exist yet, that is a new-topic proposal — stop and get sign-off before scaffolding.

3. **Compose.** Stamp the authored core (`type`, `title`, `description`) and a birth `timestamp` once (ISO 8601 with time, so same-day writes stay ordered), add the type-specific keys and typed relations the format doc names, and write every cross-link file-relative to the page being written (`../decisions/...`, `../findings/...`). Any tag not already in the schema's `## Tag vocabulary` is a mint: add it there with a one-line gloss in this same write — unilateral, but never invisible. For a concept or hub synthesis, meet the format doc's readable-on-its-own bar before writing: reread the draft as a technical reader outside the source's field, and gloss inline or promote to the glossary any term they would stall on.

4. **Write the page.**

5. **Regenerate the affected blocks** with `compile` — never hand-edit compiled content. Recompile the member block of each hub the page joined, the root taxonomy and state, and, on a decision write or supersession, the registers. Authored prose around the blocks is never touched.

6. **Commit** per the `## docs` steering block: commit each write with a structured message (`record: DR-0021 <title>`, `ingest: <title>`, `curate: <what>`), or stage for review. Default to commit when no steering block exists.

## Two calling positions

- **Conversational**, with no grill loaded: "record-doc: DR, we fix beta at 0.3 because the Smith fit landed there." You supply the missing conformance; ask only what the type genuinely requires.
- **Subroutine**, from a workflow skill or a foreign skill system: the external contract is *name the type, provide the content*.

## Mutability

Prefer append and supersede. A deliberate rewrite is legitimate when the commit logs it and any surface reading the page is recompiled afterward.

A hub synthesis rewrite additionally sets that hub's `synthesized` to the current time and recompiles the root taxonomy and state blocks in the same commit.
