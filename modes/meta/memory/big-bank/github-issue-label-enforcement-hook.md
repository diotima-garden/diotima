# Github Issue Label Enforcement Hook

<2026-07-13 — branch master — sessions acc038>

## Summary
A `PreToolUse` hook was implemented under `system/scm-integration/` that enforces at least one label on every GitHub issue created via `gh issue create`. The hook discovers existing repo labels at block time and proposes them in stderr, so a single retry lets the model read the menu and re-run the command without having to discover labels itself first. It degrades gracefully when label discovery fails (offline, bad repo, etc.) by falling back to instructing the model to run discovery manually rather than hard-failing. The implementation landed as commit `9ff6f65` and was verified working against the real repo, resolving an earlier open question about enforcing semantic rules through hooks rather than prose in `.claude/rules/`.

## Archive
[Small bank sessions](small-bank-archive/20260726T225907-small-bank.md)
