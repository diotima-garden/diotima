# Pipeline: process-flags

- mandatory step fails → notify user with the step name and error, stop immediately
- optional step fails → notify user with the step name and error, ask whether to continue
- never silently swallow failures

## Steps

- read `<deck-dir>/context.md` [mandatory] — identify the deck config file and derive `<backupDir>` = `<deck-dir>/backups`
  Why: deck config filename may not match the deck directory name; context.md is the authoritative index

- skill: compile-context `<resolved anki deck specification file>` [mandatory] — fire as background fork
  Why: no dependency on sync or deck name resolution

- mcp__anki__sync [mandatory]
  Why: ensure local Anki state is current before reading or modifying any cards

- mcp__anki__deck_names → fuzzy-match `<deck>` → `<ankiDeckName>` [mandatory]
  Why: resolves once at pipeline level; threads through to backup and red-edit

- skill: anki-backup-deck `<ankiDeckName>` `<backupDir>` [mandatory]

- await compile-context result [mandatory]
  Why: compiled context must be ready before card processing begins

- skill: anki-process-red-edit `<compiled context file path>` `<ankiDeckName>` [mandatory]
  Why: the actual red-flag processing and in-place edits

- skill: anki-process-purple-delete [mandatory]
  Why: cleanup unneeded cards

- mcp__anki__sync [mandatory]
  Why: push changes to Anki
