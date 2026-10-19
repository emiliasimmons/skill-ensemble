# Migrations

Steps for bringing a canon up to date after canonize updates, by release.

## 0.1.1

### Recommended

Load `/canonize:catalog` and read the entry format it writes to, `canon/formats/entry.md`,
in particular the paragraph after the source profiles that begins "Name each section for
what it holds". Scan the entries in `pages/` for section titles that paragraph rules out,
such as "What it says", "What it contains", and "What the project uses", and rename each
to fit the source the way that paragraph describes. Rename with `sed` through Bash: Edit
and Write restamp `updated`, which flags every synthesis and decision citing the entry as
stale.
