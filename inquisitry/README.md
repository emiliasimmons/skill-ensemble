# inquisitry

Skills that make the agent stop and ask.

The default failure mode of a capable coding agent is enthusiastic compliance: it builds what you described, at the complexity you described, without ever testing whether the description was right. These skills interrupt that. Each one hands the initiative back to the human at a point where a wrong assumption is still cheap to fix.

## The skills

**challenge-me** — a socratic mirror. Mirrors your thinking back as questions, names the assumptions you're treating as settled (especially the unstated ones), and for every piece of complexity asks what breaks if you remove it. The simpler version is correct until you can say why it isn't. Challenges the framing, not just the details. One question at a time, unsoftened.

**grill-me** — the interview. Maps a plan as a design tree, then works it in rounds: the frontier is every decision whose prerequisites are already settled, and the whole frontier goes to you in one round, numbered, each question carrying a recommended answer. Every round opens with the tree so you can see where you are. Facts are the agent's job (it dispatches sub-agents rather than asking you to look things up); decisions are yours. Done when the frontier is empty and you confirm the understanding is shared.

**slow-down** — for when a previous response raised eight things at once. Collects everything outstanding into a numbered list ordered by what unblocks the most, then takes item 1 alone: state it, recommend, stop. Nothing is bundled, even when the answer to one item obviously determines the next. Each turn reopens with the remaining list so you can see what's left. Facts get fetched by the agent, so you only answer what genuinely needs your judgment. Explicit invocation only.

**wait-what** — one line, one job. The last message didn't land; re-pitch it with context, in Simplified Technical English, using the project's own vocabulary. Explicit invocation only.

**planning-presentations** — content strategy before slide syntax: who's in the room, what they should do afterward, how much time you actually have once Q&A comes out. Interviews thoroughly even when you dump context up front, then produces a structured outline. Quarto-aware, so it suggests revealjs and pptx features that serve the narrative rather than decorating it.

## Interaction discipline

Two rules recur across these skills and are the point of the collection:

- **Nothing is asked whose answer depends on an open question.** `slow-down` and `challenge-me` take that to its limit and ask one thing per turn; `grill-me` batches a round, but only ever the questions that are askable now.
- **Every question comes with a recommendation.** You confirm or overrule a position rather than doing the agent's thinking for it.

`slow-down` and `wait-what` set `disable-model-invocation: true` — they only fire when you ask for them, because they are corrections to the conversation rather than steps in a task.
