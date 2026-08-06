---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up. Use when the user wants to branch off and work on something separately, hand work to a fresh session, bring findings back to an earlier session, or mentions "handoff".
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work.

Save location: check the `## docs` steering block for a `Handoffs` setting. `local` means write to the current workspace; `temp dir` means the OS temporary directory. Default to temp dir when no steering block exists.

Include a "suggested skills" section in the document, which suggests skills that the agent should invoke.

Do not duplicate content already captured in other artifacts. Reference them by path or URL instead. Do not refer to any previous handoffs - any relevant details should be added to the new handoff.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
