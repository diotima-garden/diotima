---
name: anki-backup-deck
description: Back up a single Anki deck to a dated .apkg file
disable-model-invocation: false
---

Back up a single Anki deck to a dated .apkg file.

**Usage** `/anki-backup-deck <ankiDeckName> <backupDir>`

Both args are required. The pipeline resolves them; for standalone use, supply them directly.

## Step 1 — Derive filename

Determine `TODAY`:
```bash
date +%Y-%m-%d
```

Check if `<backupDir>/<TODAY>.apkg` already exists:
```bash
ls <backupDir>/<TODAY>.apkg 2>/dev/null
```

- If it **does** exist: append a short poetic suffix drawn from Homer's Iliad (2–3 memorable words, lowercase, hyphen-separated — e.g. `2026-04-15-rosy-fingered-dawn.apkg`). Pick something fitting; no two backups should feel the same.

## Step 2 — Export

Call `mcp__anki__export_deck` with:
- `deck`: `<ankiDeckName>`
- `path`: `<PROJECT_ROOT>/<backupDir>/<FILENAME>` (absolute path)
- `include_sched`: `true`
