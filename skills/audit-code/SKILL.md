---
name: audit-code
description: Check the model's code against its recorded reasoning and report the discrepancies. Use when the user wants to verify the code matches the project record, before a release or review, or when checking for drift between code and decisions or provenance. Read-only by default. Do NOT use to check whether the model fits the data — that is a finding, recorded with ingest-source.
---

**First**, immediately orient with /canon.

Walk the relation graph into the model's code. Read it, never run it. Resolution is whatever the user says next.

## Walk

- **Provenance → code.** Each `provenance` page's `code_site` names a code location (path and symbol). Follow it; check the value in code matches. A recorded value disagreeing with code is a discrepancy.
- **Decision → code.** Read each `decision` against the code it governs. Is the thing a DR calls a random screen still a random screen? Has a structural change slipped in with no DR superseded?
- **Code → docs.** Scan the other way: a hardcoded value with no provenance pointing at it, or code behavior no DR covers, is an orphan worth flagging.

If the project has no `provenance` type, skip that direction; the decision and code→docs walks still run.

If the memory is shared across repos, audit only this repo against the shared record.

## Report

**A table.** Columns: `#`, `where` (code site), `discrepancy` (one line), `evidence` (root-anchored link to the DR or provenance it disagrees with), `recommendation`. Put detail notes below the table by number where one line is not enough.

**Each item carries a recommended direction,** one of two, and they resolve asymmetrically:

- **Fix code** — the docs look authoritative; the code drifted. Resolution is approval of a diff. Code fixes are **never unilateral**, even trivial ones: the skill cannot tell drift from an unrecorded change of mind.
- **Record decision** — the code looks deliberate; the docs are silent or stale. Approval alone cannot resolve it, because code shows *what* was decided, never *why*. Spend one or two inline questions to extract the rationale, then /record-doc files the DR (new or superseding). If the item remains unresolved after discussion, offer to run a /grilling session to settle it, or file it provisional so it lands in the open-decisions register rather than being lost.

## Close

Prompt roughly: fix all per recommendations, fix one by one, run a /grilling session on specific items, or dismiss. **Dismissals are session-only — there is no persistent waiver.** Code is never modified without explicit per-diff approval.
