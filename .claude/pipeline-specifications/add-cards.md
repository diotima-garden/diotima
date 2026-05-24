# Pipeline: add-cards

- mandatory step fails → notify user with the step name and error, stop immediately
- optional step fails → notify user with the step name and error, ask whether to continue
- never silently swallow failures

## Steps

- read `<deck-dir>/context.md` [mandatory] — identify the deck config file and derive `<backupDir>` = `<deck-dir>/backups`
  Why: deck config filename may not match the deck directory name; context.md is the authoritative index

- skill: compile-context `<resolved anki deck config file>` [mandatory] — fire as background fork
  Why: no dependency on sync or deck name resolution

- mcp__anki__sync [mandatory]
  Why: ensure local Anki state is current before modifying it

- mcp__anki__deck_names → fuzzy-match `<deck>` → `<ankiDeckName>` [mandatory]
  Why: resolves once at pipeline level; threads through to backup

- skill: anki-backup-deck `<ankiDeckName>` `<backupDir>` [mandatory]

- await compile-context result [mandatory]
  Why: compiled context must be ready before generation begins

- skill: anki-add-cards `<compiled context>` `<input>` [mandatory]
  Why: the actual card generation (isolated subprocess) and injection

- mcp__anki__sync [mandatory]
  Why: push changes to anki
