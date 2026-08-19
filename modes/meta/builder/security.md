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

`git push` is allowed when the user explicitly asks for it in the moment — confirm
scope (which repo/branch) if it's ambiguous, then run it. Don't push proactively or
bundle it into unrelated work without being asked.

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

## Checklist Before Saving a Skill

- [ ] Every bash block contains exactly one command (see `.claude/rules/bash-commands.md`)
- [ ] Every command that runs on every invocation has a matching entry in `.claude/settings.json`
- [ ] One-time setup steps are left unwhitelisted (prompt is intentional)
- [ ] No destructive commands are present or whitelisted
- [ ] Writes are scoped to `/tmp` or the project tree
- [ ] All bash block paths are project-root-relative (see `.claude/rules/portability.md`)
