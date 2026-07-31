---
name: fixup-docs
description: Mechanical repairs over the project — broken links, frontmatter conformance, recompile, tag cleanup. Unilateral; no sign-off needed. Use when the user asks for a health check on the project's plumbing, or when another skill needs a recompile. Do NOT use for substantive changes to content or taxonomy.
---

**First**, immediately orient with /canon. All operations use the /canon script.

Fix in one pass, no permission needed:

- **Broken and non-root-anchored links.** /canon check --links finds them. A moved page's outgoing links survive root-anchoring; only inbound links need repair.
- **Format conformance.** /canon check --frontmatter flags pages missing `type`, the authored core, or a birth timestamp, and pages carrying an unregistered type.
- **Pages in no hub.** The same check flags a hub-surfacing page that no hub lists. Propose a topic tag for each.
- **Full recompile.** /canon compile regenerates every compiled surface from frontmatter.
- **Orphan and near-duplicate tags.** Flag tags past the aging threshold with too few members, and merge near-duplicates into one canonical form.
- **Aged placeholders.** Provisional DRs past the placeholder-aging threshold: surface them for the user to revisit.

Repairs commit with a `fixup:` message.
