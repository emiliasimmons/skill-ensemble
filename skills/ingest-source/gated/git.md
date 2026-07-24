# Git repository ingestion

## Detection

A source directory containing `.git/`, or a URL the user provides.

When given a URL, clone into `sources/<repo-name>/` where `<repo-name>` is the last path segment of the URL (strip trailing `.git`). Full clone, not shallow — tags and history are needed for version checkout.

## Role classification

Check the project's dependency manifests (`pyproject.toml`, `uv.lock`, `requirements.txt`, conda environment files) for the repo's package name.

- **Dependency**: the repo's package appears in a manifest. The project builds on it.
- **Reference**: the repo's package does not appear in any manifest. The project studies it.

If the check is ambiguous (monorepo, namespace packages, indirect dependency), ask the user. Always confirm the classification before proceeding.

## Version checkout

For dependencies with a pinned version in the manifest, check out the corresponding git tag or commit in the clone. Common tag formats: `v1.5.7`, `1.5.7`, `release-1.5.7`. If no matching tag exists, note the pin in the summary page and stay on the default branch.

For references or unpinned dependencies, stay on the default branch.

## Dependency flow

Assess the repo's external documentation (project website, hosted API docs, ReadTheDocs):

**Good external docs exist:** link to them. Write a dense summary oriented toward agent consumption: what the library provides, key classes and extension points the project uses or will use, parameter surfaces, conventions for subclassing or configuration. Refer to specific doc pages and code paths where useful. The summary supplements the docs, not replaces them.

**External docs are absent or thin:** build local documentation from the code. Key modules, class hierarchies, public API, configuration patterns, extension points. More depth than the link-and-summarize case since there's nothing else to point to.

In both cases, the summary page should focus on what this project needs from the library, not be an exhaustive library reference.

## Reference flow

Interview the user before writing. What do they want from this repo? Implementation patterns, calibration approach, scenario structure, analysis pipeline, data processing, something else? Build shared understanding of what matters before reading and summarizing.

Read the repo guided by the user's stated interests. The summary page captures what was learned for this project's purposes.
