# Word document extraction

Requires `pandoc`.

Convert a `.docx` to markdown with comments preserved. Resolve script paths relative to this skill's directory (`$S` = `<skill-dir>/scripts`).

```sh
bash $S/extract_docx.sh document.docx docs/sources/<slug>/
```

The script uses `--track-changes=all` to keep Word comments and tracked changes in the output, and `--extract-media` to pull embedded images.

Output depends on whether the document contains embedded media:

| Case | Output |
|---|---|
| No media | `<name>.md` in the output directory |
| With media | `<name>/contents.md` + `<name>/media/` in the output directory |

When ingesting a docx, do not read the docx directly. Extract it first (if not yet extracted), then read the contents from the extracted markdown.
