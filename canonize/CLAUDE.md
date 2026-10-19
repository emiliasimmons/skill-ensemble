## Releases

Claude Code compares `version` in `.claude-plugin/plugin.json` to decide whether an
installed copy updates, so a change pushed without a bump never reaches existing users.
Bump it with every change meant to ship. A release carrying a Required migration step is
a breaking change: bump the middle number while below 1.0, the first number after.

## Migration guide

`MIGRATIONS.md` holds instructions for an agent bringing an existing canon up to date.
At session start, `hooks/migrate_notice.py` compares `canonize_version` in the canon's
`settings.json` with the plugin's version, and hands the agent every step from the
releases in between, verbatim. The agent asks the user before running them in a subagent.

Add a `## <version>` section, newest at the top, when a release changes something existing
canons should act on. Under it, give each level that has steps its own heading:

- `### Required`: the canon fails `check`, or the skills misread it, until the step is done.
- `### Recommended`: brings older pages in line with what the skills now write.
- `### Minor`: optional tidying.

Write each step as an instruction to a subagent that has never seen the change: the skill
to load, the section of the skill or format doc to read, what to look for in the canon,
and how to change it. Describe the work, and leave the record of what changed to the
commit history. Releases that leave existing canons nothing to do get no section.
