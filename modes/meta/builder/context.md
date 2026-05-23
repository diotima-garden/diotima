# Builder Mode

*Read this when creating, modifying, or deleting skills, pipelines, hooks, utilities,
or external integrations. Not for everyday card operations or architectural decisions.*

---

## Entry Contract

Before modifying any file under `.claude/` read:
    - `utilities.md`
    - `security.md`
    - `user_experience.md`
    - `mcp.md`

## What Builder Mode Covers

- **Skills** — generic operations that pipelines compose
- **Pipelines** — orchestration of skills and external tool calls
- **Hooks** — enforcement contracts that fire at write time
- **Shared utilities** — helpers imported across hooks and scripts
- **External integrations** — MCP servers and other protocol boundaries
- **Permissions** — the allow list in `.claude/settings.json`

## What Builder Mode Does Not Cover

- Adding cards, running pipelines, or other operational tasks (user mode)
- Changing how the system grows, adding new layers or primitives (architect mode)

## Branch Hygiene

If your work touches hooks, utilities, the MCP server, or the mem-bank subsystem — it
is infrastructure, not a feature. Extract it to master via an isolated PR before
continuing feature work. Infrastructure coupled to feature branches cannot be shared
and is expensive to untangle later.

## Project State

Read `../memory/context.md` on entry.
