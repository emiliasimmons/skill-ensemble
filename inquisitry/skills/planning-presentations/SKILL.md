---
name: planning-presentations
description: Use when planning a presentation, talk, or slide deck before writing slides -- determines what to say, how to structure it, and how many slides to use
---

# Planning Presentations

Content strategy for presentations. Focused on *what to say* and *how to structure it*, not slide syntax or markdown formatting. Quarto-aware -- knows what revealjs and pptx can do, and suggests features that serve the narrative. Produces a structured outline artifact in the plan file.

## Interview Workflow

Always interview the user thoroughly before producing an outline. Even when the user dumps context up front, probe for gaps. Use the question tool to ask in batches.

### Required Questions

**Audience**

- Who is in the room? (Roles, seniority, technical level)
- What do they already know about the topic?
- What do they care about? What are their concerns or objections?
- Are there decision-makers present? Who needs to be convinced?
- Is this a recurring presentation (e.g., quarterly review) with established expectations, or a one-off?

**Objective**

- Complete this sentence: "After this presentation, the audience should ___."
- Is there a specific ask? (Approval, funding, adoption, understanding)
- What does success look like?

**Constraints**

- Time limit (strict or flexible?). Does it include Q&A? If so, subtract Q&A time before estimating slide count.
- Format: live in-person, live remote, recorded/async, self-serve deck?
- Venue: conference stage, meeting room, webinar, shared screen?
- Solo presenter, or part of a panel/multi-speaker session? If multi, what's your segment?
- Any required content? (Compliance slides, logos, specific data)

**Tone and Depth**

- Formal or conversational?
- Technical depth: executive summary, practitioner detail, or deep dive?
- Is storytelling appropriate, or is this strictly informational?

**Content Inputs**

- What material already exists? Docs, repos, data, previous decks?
- Are there diagrams, charts, or visuals that should be included?
- Any demos or live code to show?

**Output Format**

- Revealjs (HTML), PowerPoint (pptx), or undecided?
- Will the deck be shared standalone or only presented live?
- Any branding requirements? (Logo, color scheme, template)

### Adaptive Depth

If the user has already provided rich context, acknowledge what's covered and only ask about gaps. Never re-ask what's been clearly stated. But always confirm the objective -- it's the single most important input.

## Narrative Frameworks

Suggest a framework based on presentation type. The user can mix or override.

| Type | Framework | Structure | When to use |
|---|---|---|---|
| Proposal / pitch | Problem > Solution > Outcome | Name the pain, present the fix, show the payoff | Requesting approval, budget, or buy-in |
| Data / findings | What > So What > Now What | Present facts, explain significance, recommend action | Sharing research, metrics, or analysis |
| Decision support | Context > Options > Recommendation | Set the scene, lay out choices, argue for one | Complex decisions with tradeoffs |
| Technical demo | Setup > Demo > Takeaway | Explain the problem, show the solution working, highlight what matters | Showing how something works |
| Teaching | Hook > Concept > Practice > Summary | Grab attention, teach the idea, let it sink in, reinforce | Training, workshops, educational talks |
| Status update | Progress > Blockers > Next Steps | What's done, what's stuck, what's next | Regular cadence meetings |
| Thought leadership | Conventional Wisdom > Contradiction > New Model | State what people believe, challenge it, offer a better frame | Conference keynotes, opinion pieces |

## Outline Structure

The outline is the deliverable. Write it in the plan file as structured markdown. It serves as the spec that the writing skill will implement.

### Required Sections

```markdown
## Presentation Outline

**Title:** [title]
**Subtitle:** [subtitle if any]
**Author:** [name]
**Date:** [date or TBD]
**Duration:** [target minutes]
**Estimated Slides:** [count] ([X] content + [Y] section headers)
**Format:** [revealjs / pptx / TBD]
**Narrative Framework:** [chosen framework]

### Opening ([time estimate])
- Hook: [specific hook -- question, stat, story, demo]
- Context: [what the audience needs to know first]
- Roadmap: [brief overview of what's coming]

### Section 1: [Name] ([time estimate])

#### Slide: [Title]
- [Key point 1]
- [Key point 2]
- [Key point 3-6]
- **Speaker notes intent:** [what to say that isn't on the slide]
- **Visual:** [suggested diagram, chart, image, or code demo]

[repeat for each slide]

**Transition to next section:** [how this section leads to the next -- the connecting thread]

### Section 2: [Name] ([time estimate])
[...]

### Closing ([time estimate])
- Summary: [key takeaways, max 3]
- Call to action: [specific ask or next step]
- Final thought: [memorable closing -- callback to hook, quote, or vision]

### Quarto Features to Use
- [e.g., "Mermaid flowchart for the data pipeline"]
- [e.g., "Auto-animate to show architecture evolution across 3 slides"]
- [e.g., "Two-column layout comparing before/after metrics"]
```

### Slide Count Estimation

Start from the time budget and work backward:

- Content slides: 1-2 minutes each
- Code/demo slides: 3-5 minutes each
- Section headers: 5-10 seconds (don't count toward content time)
- Opening hook: 1-2 minutes
- Closing: 1-2 minutes

A 20-minute talk typically has 12-18 content slides. A 45-minute talk: 25-35. Err toward fewer, denser slides rather than many sparse ones.

## Density and Pacing

- Every content slide needs at least 3 substantive points, unless it's a standalone visual or diagram
- Speaker notes are required for every content slide in the outline -- even if brief
- Suggested visuals should be specific ("mermaid sequence diagram showing auth flow"), not vague ("add a diagram")
- The opening hook is mandatory. Never start with "Today I'm going to talk about..."
- The closing call-to-action is mandatory. Never end with "Any questions?"

## Quarto Feature Awareness

When suggesting features in the outline, match them to the chosen format. Consult the writing skill's feature reference for format-specific capabilities -- don't duplicate that knowledge here.

**General guidance:** Mermaid diagrams, two-column layouts, speaker notes, incremental lists, figures, and tables work in both revealjs and pptx. Features like auto-animate, fragments, and slide backgrounds are revealjs-only. PowerPoint is stronger for offline sharing, corporate templates, and non-technical reviewers.

Don't suggest format-specific features if the format isn't decided yet -- flag them as "if using revealjs" or "if using pptx."

## Common Mistakes

| Mistake | What to do instead |
|---|---|
| Starting with slides instead of audience/objective | Always establish who, why, and what-should-they-do-after before any content |
| Too many slides for the time slot | Budget time first, then fill slides. Cut scope, not density |
| No narrative arc -- just a topic list | Pick a framework from the table and commit to it |
| Burying the recommendation | State the ask or key insight in the first 3 slides, then support it |
| Vague visual suggestions | Be specific: "Gantt chart of Q3 timeline" not "add a timeline" |
| Skipping speaker notes | Notes are where the narrative lives -- the slide is just the visual aid |
| Identical opening and closing | The closing should transform the opening: callback to the hook with the new understanding |

## Handoff

Present the outline to the user and confirm: (1) the objective is captured correctly, (2) the slide count fits the time budget, and (3) no critical content is missing. Once the user confirms, point to the appropriate writing skill by purpose:

- For HTML presentations: "Load the revealjs presentation writing skill to implement this outline."
- For PowerPoint: "Load the PowerPoint slide writing skill to implement this outline."

Do not start writing slides in this skill. The boundary is: planning produces the outline, writing produces the `.qmd` file.
