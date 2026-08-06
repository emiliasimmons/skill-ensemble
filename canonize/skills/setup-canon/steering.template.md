# docs steering block

`setup-canon` adds this block to the project's agent instructions file (`AGENTS.md`, or `CLAUDE.md` if that is what the project already uses). Keep it short. Add to it when a real preference shows up; re-run `setup-canon` to change it. Commit and handoff behavior live here; thresholds and types live in `schema.md`.

Other skills append their own standing permissions as bullets, such as `- PDF extraction: docling approved` once the user has agreed to that install. Leave those in place when re-running.

## New project

```markdown
## docs

- Substrate root: <root> (canon compiles the spine)
- Commits: [commit each write | stage for review]
- Handoffs: [local | temp dir]
- Structural changes (new topic, new type, split/merge/rename) need sign-off; tag minting is unilateral but registered in the same write.

To change how the skills behave, re-run setup-canon and say what is annoying.
```

## Linked repo

Add these bullets and list any other loaded skill systems or plugins with their purpose.

```markdown
## docs

- Shared docs: symlinked from <upstream project path>
- Workspace: <name> (findings write to findings/<name>/)
- [Other plugin]: <one-line purpose>
- Commits: [commit each write | stage for review]
- Handoffs: [local | temp dir]
- Structural changes need sign-off; tag minting is unilateral but registered.

To change how the skills behave, re-run setup-canon and say what is annoying.
```
