# Skill Security Guide

Read this before creating or modifying any skill in `.claude/commands/`.

## Core Rule: One Command Per Bash Block

See `.claude/rules/bash-commands.md` — that is the canonical location. This rule applies
at both authoring time and execution time.

---

## Whitelist Contract

The whitelist in `.claude/settings.json` covers commands that run **every time a skill is invoked**. When you add a repeatable command to a skill, add its whitelist entry at the same time.

One-time setup commands (e.g., creating a directory on first run) should **not** be whitelisted. It is intentional that the user is prompted for these — they happen rarely and the confirmation is a useful signal.

The current set of whitelisted rules is the source of truth: `.claude/settings.json`.

---

## Git Policy

`git add`, `git commit`, and `git push` must **never** be run by Claude in this project — not even when asked generically. All git staging, committing, and pushing is the user's responsibility exclusively. Do not suggest or offer to run these commands.

Read-only git commands (`git log`, `git diff`, `git status`) are fine and whitelisted.

---

## What Always Requires a Prompt (Do Not Whitelist)

These must never be added to the allow list — they should always surface for user confirmation:

- One-time setup steps (directory creation, initial config, etc.)
- Destructive operations: `rm`, `git reset`, `git checkout --`, `git clean`
- Any `git` command that stages, commits, or pushes changes
- Writes outside `/tmp` and the project tree
- Any command that modifies shared state outside this project

---

## Pipeline Authoring

Pipeline specifications live in `.claude/pipeline-specifications/`. Each step must be
tagged `[mandatory]` or `[optional]` — no untagged steps allowed.

- `[mandatory]` — stop immediately on failure, notify user with step name and error
- `[optional]` — notify user with step name and error, ask whether to continue
- Never silently swallow failures
- Only compose existing skills and MCP tools — no inline logic in pipeline definitions
- Pipeline steps must follow the same security rules as atomic skills

Pipeline entry points (thin wrappers) live in `.claude/commands/pipe/`.

---

## Checklist Before Saving a Skill

- [ ] Every bash block contains exactly one command (see `.claude/rules/bash-commands.md`)
- [ ] Every command that runs on every invocation has a matching entry in `.claude/settings.json`
- [ ] One-time setup steps are left unwhitelisted (prompt is intentional)
- [ ] No destructive commands are present or whitelisted
- [ ] Writes are scoped to `/tmp` or the project tree
- [ ] All bash block paths are project-root-relative (see `.claude/rules/portability.md`)
