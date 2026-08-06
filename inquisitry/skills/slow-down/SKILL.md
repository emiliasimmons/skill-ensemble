---
name: slow-down
description: Work through a pile of open items one at a time. Use when a previous response raised many separate questions or issues at once, or on any 'sift' trigger phrase.
disable-model-invocation: true
---

Take everything currently outstanding — questions asked, issues raised, decisions pending — and put it in front of the user as a numbered list, one line each. No detail yet. Order by what unblocks the most other items, then by cost of getting it wrong.

Then take item 1 alone.

For each item: state it in a sentence or two, give your recommendation, and stop. Wait for the answer before touching item 2. Never bundle two items into one turn, even when they're closely related and the answer to one obviously determines the other — say so and take them in sequence anyway.

Open each turn with the remaining list so the user sees what's left:

<list_format>
 1. <settled item1> ✅
 2. ~~<strikeout item2>~~
 3. **<current item3>** ◀
 4. <pending item4>
 5. <pending item5>
</list_format>

Items can be dropped, deferred, or split. If the user drops one, strike it and move on without argument. If an answer makes a later item moot, remove it and say which. New items discovered mid-session go on the end unless they block something still pending.

Find facts yourself. If an item needs something from the filesystem, a tool, or the web, go get it before presenting the item — the user should only be answering questions that genuinely require their judgment.

One question per turn is the whole point. If a turn contains a question mark in more than one paragraph, it's too much.
