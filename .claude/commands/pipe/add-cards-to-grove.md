Usage: `/pipe:add-cards-to-grove <grove-dir> [input]`

# Pipeline: add-cards

- mandatory step fails → notify user with the step name and error, stop immediately
- optional step fails → notify user with the step name and error, ask whether to continue
- never silently swallow failures

## Steps

- bash: `plugins/dafne/.venv/bin/python3 system/diotima/check-requires.py <grove-dir>` [mandatory]
  Why: this pipeline needs anki. Refuse here — before the background compile fork is
  spawned — rather than dying deep at the first mcp__anki__ call.
  `REQUIRES_UNSATISFIED` → stop and report. `REQUIRES_UNKNOWN` or `REQUIRES_SATISFIED` → proceed.

- read `<grove-dir>/context.md` [mandatory] — identify the deck config file and derive `<backupDir>` = `<grove-dir>/backups`
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

- skill: anki-mcp:add-cards-to-deck `<ankiDeckName>` `<compiled context>` `<input>` [mandatory]
  Why: the actual card generation (isolated subprocess) and injection. The worker is
  Anki-domain and grove-blind — the pipeline hands it the resolved deck and context file;
  it never learns the grove or that compilation happened.

- mcp__anki__sync [mandatory]
  Why: push changes to anki
