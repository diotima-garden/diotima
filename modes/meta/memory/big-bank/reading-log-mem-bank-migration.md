# Reading Log Mem Bank Migration

<2026-05-07 — branch mem-graduate — sessions b30804, 9eedac, abeb0e>

## Summary
The Spanish deck's reading log subsystem was migrated from a flat reading-log.md file to a small-bank directory structure, integrating the memory bank mechanics introduced earlier in the branch. The hook mechanism that drives per-bank captures was refactored to simplify the handoff between sessions: the previous two-file approach using last-prompt.txt and last-targets.txt was replaced with a single last-jobs.json, allowing one Claude call per bank rather than one shared call across all banks. The capture prompt template file was renamed from capture-prompt.md to this-bank-prompt.md to more accurately reflect its role as the bank's own custom prompt, not a generic pipeline artifact. A merge of master into lit_search was performed before this work began, with gitignore conflicts resolved by retaining both branches' additions. The session concluded with all changes staged and ready for commit.

## Archive
[Small bank sessions](small-bank-archive/20260507T093416-small-bank.md)
