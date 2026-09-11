# root instruction line

One line into the repo-root agent instructions file (`AGENTS.md`, or `CLAUDE.md` if the
repo uses that). It steers the session into the canon, and nothing more: the conventions
and settings live in `docs/CLAUDE.md`, which loads on its own under `docs/`. If the file
already exists, add the load line and leave the rest.

```markdown
Load /canonize:canon immediately.
```

When the canon root is not `docs/`, add a second line naming it, because `settings.json`
and `docs/CLAUDE.md` both live inside the root and so cannot say where it is:

```markdown
Canon root: <path>
```

Tell the user in chat, once, that the load line can be gated on a condition instead of
firing every session, for example "When work touches the model, the docs, or an
experiment, load /canonize:canon first." Do not write that suggestion into their file.
