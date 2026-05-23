---
name: compile-context
description: Preprocess and compile a context file into a flat human-readable document
context: fork
disable-model-invocation: false
---

Preprocess a file's `#include` chain and merge it into a single flat document.

Usage: `/context-compiler:compile-context <file.md>`

e.g. `/context-compiler:compile-context decks/languages/spanish/spanish.md`

## Step 1 — Validate Input

If `<file.md>` does not exist, report "File not found: <file.md>" and stop.

## Step 2 — Freshness Check

Run:
```
python3 .claude/plugins/context-compiler/compiled-is-fresh.py <file.md>
```

- Exit code 0 → already up-to-date. Report and stop:
  ```
  ✓ <file.md> already up-to-date — <stem>.compiled.md is newer than all inputs.
  ```
- Exit code 1 → proceed to Step 3.

## Step 3 — Preprocess

```bash
python3 .claude/plugins/context-compiler/preprocess.py <file.md> <dir>/<stem>.preprocessed.md
```

Where `<dir>` is the directory containing `<file.md>` and `<stem>` is the filename without `.md`.

e.g. `decks/languages/spanish/spanish.md` → `decks/languages/spanish/spanish.preprocessed.md`

## Step 4 — Merge to Human-Readable

Run `/context-compiler:compile <dir>/<stem>.preprocessed.md`.

This produces `<dir>/<stem>.compiled.md` — a clean, flat document with no layer markers.

## Step 5 — Report

```
✓ Compiled <file.md> → <dir>/<stem>.compiled.md
```
