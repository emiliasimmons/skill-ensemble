It is **critically important** to load /canonize:canon immediately, if not yet done.
Never read a file from `./raw/` without either:
- Being explicitly instructed (by a skill or user)
- Determining that reading raw content is relevant **ONLY** if reading its cataloged entry
    in `./pages/` is insufficient.

# Conventions

## Commit

- Cataloging: one commit per batch.
- Every other write: one commit per logical write, structured message (`catalog: <title>`,
  `curate: <what>`).

## Tags

A tag marks a cross-cutting theme with 3 or more expected members. Short and general beats
compound or qualified: `hiv` not `hiv-incidence`, `modeling` not `mathematical-modeling`.
The qualifier belongs in the page's description. Atomic tags intersect to capture what a
compound tag would (`antibiotic` + `resistance` + `modeling`).

## Sign-off

A tag that extends an existing family is added on your own and reported. A tag that opens
a new dimension, a tag split, merge, or rename, and a new page type each need the user's
sign-off first.
