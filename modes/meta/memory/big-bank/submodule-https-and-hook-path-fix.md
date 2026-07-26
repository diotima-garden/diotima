# Submodule Https And Hook Path Fix

<2026-07-14 — branch master — sessions a5d04d>

## Summary
Submodule URLs were converted from SSH to HTTPS in both the top-level and nested `.gitmodules` files to unblock external users who clone without SSH keys configured, while a `git config` rewrite rule was added so HTTPS clones transparently map back to SSH for the user's own pushes. During this work, a hook bug was discovered in `.claude/settings.json` where relative paths could deadlock if the working directory shifted; all hooks were rewritten to use `$CLAUDE_PROJECT_DIR` for robustness instead. The top-level change was committed as `0a4aaea`; the nested anki-mcp submodule commit `280e543` existed only locally and needed to be pushed before the parent repo could be pushed.

## Archive
[Small bank sessions](small-bank-archive/20260726T225907-small-bank.md)
