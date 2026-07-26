# Mneme Extraction Repo Split

<2026-07-26 — branch mneme-extraction — sessions fe8ced, b6c91c>

## Summary
The mem-bank subsystem was extracted from the monorepo into two standalone public repositories, diotima-garden/session-crawler and diotima-garden/mneme, both pushed and verified via end-to-end tests. During the move, the mount location was deliberately changed from the originally planned .claude/mem-bank to plugins/mneme, to stay consistent with the existing plugins/anki-mcp convention already used for a similar extracted subsystem. That single deviation cascaded into a broader cleanup: subscriptions.json had to be relocated to groves/mem-bank-subscriptions.json, and every reference to the old paths had to be updated across settings hooks, commands, navigation docs, and .gitmodules. By the end of the session the working tree was staged and ready for commit, with the extraction otherwise complete. The only remaining loose end is a local mem-bank-extract branch, left over from the subtree split, which can be deleted at any time. A follow-up session used a lighthearted user-provided story purely to validate that the mneme end-session hook correctly captures and processes session content, confirming the hook works without making any further substantive changes to the extraction itself.

## Archive
[Small bank sessions](small-bank-archive/20260726T195504-small-bank.md)
