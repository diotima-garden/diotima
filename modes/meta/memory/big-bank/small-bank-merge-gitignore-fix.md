# Small Bank Merge Gitignore Fix

<2026-05-07 — branch master — sessions 509d7d>

## Summary
A data loss bug was identified where small-bank.md files were being overwritten with empty versions during merges on master. The root cause was a missing `**/small-bank.md` entry in .gitignore, which allowed git to track and propagate empty small-bank files from other branches into the working tree. The fix was minimal: adding the gitignore entry so small-bank files remain local-only and cannot be overwritten by merge operations. This preserves the host-handles architecture, where each branch owns its own small-bank state without coordination overhead. To document the expected workflow going forward, a "Merge dynamics" section was added to the mem-bank README, clarifying the graduate-before-merge pattern and the practical meaning of small-banks being local-only. A merge conflict in the todo file was noted but left unresolved at the time of the session.

## Archive
[Small bank sessions](small-bank-archive/20260507T144136-small-bank.md)
