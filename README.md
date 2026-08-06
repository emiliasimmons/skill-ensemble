# skill-ensemble

A Claude Code plugin marketplace: agent skills for computational modeling work, split into three plugins that are useful alone and better together.

The shared premise is that a modeling project's value sits in the reasoning behind its numbers, and that reasoning is what agentic workflows lose first. Each plugin covers one place it leaks: the record of what was decided, the evidence it was decided on, and the conversation where it should have been questioned.

## The plugins

| Plugin | What it does |
|---|---|
| [canonize](canonize) | Turns a project's decisions, sources, and findings into a compiled wiki. Capture is a side effect of the verbs you already run; the reading surfaces regenerate themselves. |
| [bibliomancy](bibliomancy) | Literature search over OpenAlex and file attachment into Zotero, with metadata resolved rather than recalled. |
| [inquisitry](inquisitry) | Interaction discipline: assumption-checking, design interviews, one-question-at-a-time triage. |

## How they compose

No plugin requires another; composition is something you invoke, not a dependency. `bibliomancy` finds a paper and exports BibTeX, and `canonize`'s `ingest-source` will take that and write a source page placed under a topic. `inquisitry` is where a design gets interrogated, and `canonize`'s `record-doc` is where the settled decision lands as a page.

Installed alone, each still works: `inquisitry` is conversation protocol with no state at all, `bibliomancy` wants a Zotero library and no wiki, and `canonize` interviews inline for the choices it needs rather than reaching for another plugin's skills.

## Install

Add the marketplace, then install what you want:

```bash
claude plugin marketplace add emiliasimmons/skill-ensemble
```

```bash
claude plugin install canonize@skill-ensemble
```

`bibliomancy` and `inquisitry` install the same way. From an interactive session, `/plugin` gives you the same thing as a browser.

To work on the skills instead of using them, clone the repo and point the marketplace at the checkout:

```bash
claude plugin marketplace add ./skill-ensemble
```

Skills load on their own when the work matches their description. A couple (`slow-down`, `wait-what`) set `disable-model-invocation: true` and only run when you name them.

## Requirements

Python 3, stdlib only, for `canonize`'s compile script and `bibliomancy`'s scripts. `canonize`'s PDF and DOCX extractors declare their own dependencies inline and run under `uv run`. `bibliomancy` also wants a free [OpenAlex API key](https://openalex.org/settings/api) for search, and a running Zotero 10+ desktop app for attachments.
