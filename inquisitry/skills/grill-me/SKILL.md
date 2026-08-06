---
name: grill-me
description: Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled — the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Each question should be formatted like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Open every round with the tree, so the user can see at a glance where they are:

```
🌳
├─ <settled branch> ✅
├─ **<current branch>** ◀
├─ <next branch>
└─ <later branch>
```

A branch that needs more than one round unfolds while it is current:

```
├─ **<current branch>**
│  ├─ <round already asked> ✅
│  ├─ **<this round>** ◀
│  └─ <round still blocked>
```

One line per major branch, in order, with `✅` on settled ones. Most branches are a single round and stay a single line — `◀` on the branch itself is the common case.

Unfold the current branch only when it holds real sub-branches, decisions that depend on each other and so can't be asked together. Each unfolded node is **one round**, not one question: exactly one carries `◀`, with several of this round's questions under it, and the rest are rounds settled (`✅`) or still blocked. If every node would carry `◀`, you are listing questions — fold them back into one. A settled branch folds up to its `✅` line and the next branch unfolds in its place.

Never more than six branches and four unfolded nodes; collapse or merge to stay under. No prose, no annotations, no legend.

Each round the user answers reshapes the tree — settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent to find it — don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report — ask the rest of the frontier now. The _decisions_ are the user's — put each to them and wait.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.
