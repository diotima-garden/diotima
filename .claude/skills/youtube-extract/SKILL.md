---
name: youtube-extract
description: Extract learnable Spanish phrases from a YouTube video using Gemini
disable-model-invocation: true
---

Extract learnable phrases from a YouTube video and write them for review.

## Usage

`/youtube-extract <url> <context_file> [bias_hint]`

- `<url>` — YouTube video URL
- `<context_file>` — deck context file (e.g. `decks/languages/spanish/compiled.md`)
- `[bias_hint]` — optional free-text focus hint appended to the extraction prompt (e.g. `focus on subjunctive`)

Output is written to `<context_file_dir>/youtube-phrases.txt`.

## Notes

- **Long-running, foreground only.** The Gemini video pipeline takes 2–3 minutes. Never run this in the background — the default 120s Bash timeout will kill it before the output is written. Always run foreground with `timeout=300000`.

## Step 1 — Run extractor

```bash
python3 .claude/skills/youtube-extract/extract.py <url> <context_file> [bias_hint]
```

## Step 2 — Report

Display the extracted phrases and report the output file path.

Then show:
```
Review <context_file_dir>/youtube-phrases.txt, then run:
/anki-add-cards spanish <context_file_dir>/youtube-phrases.txt
```
