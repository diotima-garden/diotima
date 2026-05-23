# Anki Mcp Migration

<2026-05-07 — branch anki-mcp — sessions 98d083, 84ef61, c246a1, a3ec05, 1412bd, 0d4ca7, 3f6fdf, b76e5e>

## Summary
Evaluated Model Context Protocol (MCP) as an alternative to the existing bash-anki.py-HTTP-AnkiConnect transport chain, motivated by the desire to let Claude call Anki tools natively without JSON string construction or permission friction. Built a minimal MCP server at `.claude/anki-mcp/` with `add_notes` and `sync` tools, organized as a separate directory with its own venv, README, and server.py, and registered it in `.mcp.json`. Migrated both pipeline specs (`anki-add-cards` and `process-flags`) to call `mcp__anki__sync` and `mcp__anki__add_notes` directly, deleting the intermediate `anki-sync` skill. The `anki.py` whitelist entry was retained because backup, red-edit, and purple-delete flows still depend on it. Implemented lazy-startup for the Anki desktop daemon via a `launcher.py` module with `ensure_anki_running()`, which auto-launches Anki on the first MCP tool call if it is not already running and waits up to 30 seconds for AnkiConnect to respond. Lifecycle logic was kept in a separate launcher module rather than inlined into the server to maintain separation of concerns. The net result is a simpler skill-implementation surface where pipelines call MCP tools directly rather than constructing JSON payloads and invoking bash intermediaries.

## Archive
[Small bank sessions](small-bank-archive/20260507T144515-small-bank.md)
