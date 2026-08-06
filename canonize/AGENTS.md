Agent skills for computational modelers — structured evidence trails behind every modeling decision.

This is a repository for **designing and maintaining the skills**. It is *not* a repository *using* the skills. Adding information to this file does **not** impact the behavior of these skills.

Read the `skills/` directory to see the list of skills.

**Do not load or look for installed skills**. *This* repository is the *source* of those skills.

## No editorializing

Every sentence in a skill either constrains behavior or provides information the agent cannot derive. A sentence that does neither is a deletion target.

**Cut these on sight:**

- Body text restating the frontmatter description — the description already loaded; don't echo it
- Skill system internals the agent already knows: path resolution, how skills load each other, what language the script is written in
- Cross-skill narration of another skill's internals ("It stamps frontmatter, writes file-relative links..." inside ingest-source — record-doc owns that)
- Narrating the absence of things that were never in play ("there is no `log.md`", "there is no separate fix mode")
- Redundant qualifiers shown by operations elsewhere in the skill set ("deterministic", "mutable" when compile/append rules already cover it)
- Value statements about the system's design ("the wiki stays made of things worth keeping") — the agent follows instructions, not aspirations
- `<root>` as a path prefix in skill prose — use `docs/` directly; `<root>` belongs only in templates that `setup-canon` fills at scaffold time
