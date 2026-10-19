---
name: grill-me
description: Settle every open design decision in a plan, idea, or change before any of it gets built. Use when the user says "grill me", wants a design interviewed end to end, is about to start building something with unresolved choices in it, or asks what still needs deciding. Assumes the framing is sound — to attack the framing itself, use challenge-me.
disable-model-invocation: true
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are
already settled: the questions you can ask _now_ without guessing at answers you haven't
heard yet. Results that don't exist yet (timing runs, experiment outputs) count as
prerequisites too, so keep decisions that wait on them off the frontier until the results
land. Each round, ask up to four frontier questions, choosing the ones whose answers
unblock the most of the tree. Then wait for the user's answers before the next round.

Ask only **forks**: decisions with *at least* two answers a reasonable person could pick.
Treat choices with one sensible answer as assumptions. List them after the round's
questions, numbered so the user can address them if appropriate.

<question_format>
❓ **Q1** - **<question title>**: <the question, one sentence ending in "?">

- **A.** <option>
- **B.** <option>
...

<context the user needs to choose, if any>

➡️ **<letter>**. <why it beats the runner-up>
</question_format>

<assumption_format>
**Assuming notes:**
- **N1** <assumption, one line>
</assumption_format>

Question and assumption numbers continue across rounds. The sentence after the title is
the question itself, answerable without reading the context below it. Keep context to what
the choice needs. Name things by what they are ("the survival plot"), and give labels only
to things that already exist.

Open every round with the tree, so the user can see at a glance where they are:

<header_format>
🌳
├─ <settled branch> ✅
├─ **<current branch>** ◀
├─ <next branch>
└─ <later branch>
</header_format>

Unfold branches that need more than one round while they are current:

<branch_format>
├─ **<current branch>**
│  ├─ <round already asked> ✅
│  ├─ **<this round>** ◀
│  └─ <round still blocked>
</branch_format>

One line per major branch, in order, with `✅` on settled ones. Most branches are a single
round and stay a single line, with `◀` on the branch itself.

Unfold the current branch only when it holds real sub-branches, decisions that depend on
each other and so can't be asked together. Each unfolded node is **one round**, not one
question: exactly one carries `◀`, with several of this round's questions under it, and
the rest are rounds settled (`✅`) or still blocked. If every node would carry `◀`, you
are listing questions, so fold them back into one. Fold settled branches up to their `✅`
lines, and unfold the next branch in their place.

Never more than six branches and four unfolded nodes. Collapse or merge to stay under. No
prose, no annotations, no legend.

Each round the user answers may reshape the tree: settled decisions push the frontier
outward and unblock questions that depended on them. Recompute the frontier and ask the
next round. Move questions whose answers depend on another question still open in this
round to a _later_ round.

Count answers as **settled** when you can act on them without interpreting them. Replies
that ask something back, hedge, reject your recommendation for a reason you can't restate,
or leave you to fill in the specifics keep their questions open. Answer what the user
raised, re-put each open question as your reading of their answer, and wait. Close
a **round** when every question in it is settled, and move the frontier only from closed
rounds.

Check the settled answers before asking each question. Apply earlier answers that cover
it. When they cover only part of it, quote them and ask about the gap by name.

Finding _facts_ is your job, never the user's. When frontier questions need facts from the
environment (filesystem, tools, etc.), dispatch sub-agents to find them, and never ask the
user for anything you could look up yourself. Keep asking while they run: running
explorations are unsettled prerequisites, so only the questions downstream of them wait
for the reports. The _decisions_ are the user's: put each to them and wait.

The session is done when the frontier is empty: every branch of the design tree visited,
and every assumption listed. Do not act on it until the user confirms you have reached
a shared understanding.
