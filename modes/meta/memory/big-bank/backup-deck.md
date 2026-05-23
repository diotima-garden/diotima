# Why: backup-deck

## The problem it solves

The project originally kept pipe-separated CSV files as the source of truth — partly as a safety net before AnkiConnect was integrated, partly for git versioning. Once AnkiConnect became stable and the flag-based edit/delete workflow made Anki the live editing surface, maintaining CSV in parallel became synchronization overhead with no real benefit.

Dropping CSV as a live system meant the backup responsibility had to go somewhere.

## Why .apkg and not JSON

The first instinct was JSON from AnkiConnect's `notesInfo` — human-readable, git-diffable, no Anki dependency. But `.apkg` turned out to be the stronger choice:

- It's a ZIP containing a SQLite database (`collection.anki21`) — fully extractable without Anki, using standard tools
- The SQLite schema is [publicly documented](https://github.com/ankidroid/Anki-Android/wiki/Database-Structure) and has been stable for years
- The `notes.id` field *is* the creation timestamp (Unix ms) — so full card history is embedded without any extra effort
- It includes scheduling state (review history, due dates, intervals) — something a JSON notes export doesn't capture
- Converting `.apkg` to JSON or CSV in 10 years is ~20 lines of Python: unzip → query SQLite → serialize

JSON would have been better for git diffs between snapshots. That was the main trade-off. Decision: a durable, complete archive beats a diffable but partial one. If detailed history is ever needed, it's all inside the SQLite.

