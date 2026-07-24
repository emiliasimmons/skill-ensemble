---
name: curate-docs
description: Review the project's knowledge state — find contradictions, stale claims, missing concepts, taxonomy issues, and data gaps. Conversational; every change needs sign-off. Use when the user asks for a curation pass, a deep review, or wants the project re-examined after accumulating material.
---

**First**, immediately orient with /canon.

## Sweep

Do a full sweep of the project and present findings grouped by category:

- **Stale claims** — pages whose claims newer sources have superseded.
- **Contradictions** — pages that conflict with each other.
- **Missing concepts** — important ideas mentioned across pages but lacking their own concept page.
- **Taxonomy issues** — topics that should be split, merged, or renamed; pages that belong in a different topic.
- **Hub rewrites** — hubs past the staleness threshold whose synthesis no longer reflects their members.
- **Data gaps** — questions the project's evidence doesn't answer but could with a targeted source or analysis.

## Working through findings

Present the grouped list to the user. Ask which category to address first.

- Stale claims and contradictions: propose concept pages that capture the updated picture, or propose handoffs for substantial re-synthesis.
- Missing concepts: ask whether the user wants to run a /query-docs pass or write the concept directly.
- Taxonomy changes: argue each one and get approval before files move. After moves, run /canon check --links and /canon compile.
- Hub rewrites: rewriting a hub synthesis resets its staleness counter. Propose a handoff for complex hubs.

Curations commit with a `curate:` message.
