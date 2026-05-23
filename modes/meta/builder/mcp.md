# MCP Integration

Read this before implementing a new external integration or modifying `.claude/anki-mcp/`.

## When to prefer MCP over bash

Prefer MCP when the integration is:
- **Repeated** — the same operation runs across multiple pipeline steps (bash adds permission friction each time)
- **Stateful** — the external system maintains state you'd otherwise preserve across calls
- **Typed** — the tool accepts structured input that would require JSON construction in bash

Use bash for one-shot commands that don't repeat across pipelines.

## Implementation

Read `.claude/anki-mcp/README.md` — it covers tool registration, server structure, and
the AnkiConnect API. That README is the reference; this file covers only the decisions
and constraints that apply to any MCP integration.

Restart Claude Code after any changes to `.mcp.json` or the server — it is spawned at startup.

## Protocol discipline

The MCP server uses stdio transport. Stdout is the JSON-RPC channel.
- Never `print()` outside the SDK — it corrupts the protocol stream silently
- All debug output goes to `stderr` or the project logger (`utils/log.py`)

## Permissions

MCP tool permissions are separate from the bash whitelist in `settings.json`. If a
pipeline calls an MCP tool that triggers a permission prompt on every run, add it to
`permissions.allow` using the `mcp__<server>__<tool>` form (e.g., `mcp__anki__sync`).
