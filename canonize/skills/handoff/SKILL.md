---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up. Use when the user wants to branch off and work on something separately, hand work to a fresh session, bring findings back to an earlier session, or mentions "handoff".
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work.

Save location: check the `## docs` steering block for a `Handoffs` setting. `local` means write to the current workspace; `temp dir` means the OS temporary directory. Default to temp dir when no steering block exists.

Include a "suggested skills" section in the document, which suggests skills that the agent should invoke.

## Before drafting

Summarising from memory drops things, so derive rather than recall. Sweep this session and account for each of the following, either in the document or by a deliberate decision to leave it out:

- Every file read or modified. A file that shaped a conclusion gets named where that conclusion appears; the rest can go.
- Every option considered and rejected, with the reason. Without it the next session re-proposes what this one already ruled out.

Give rejected options their own section. Everything else belongs beside the claim it bears on.

## Confidence

Every claim carries its own standing in the sentence that makes it: verified how, or believed on what basis. Do not segregate the unverified into a section — that implies everything outside it was checked, which is a stronger claim than you can usually make.

Do not duplicate content already captured in other artifacts. Reference them by path or URL instead. Do not refer to any previous handoffs - any relevant details should be added to the new handoff.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
