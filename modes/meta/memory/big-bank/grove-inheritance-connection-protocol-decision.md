# Grove Inheritance Connection Protocol Decision

<2026-07-17 — branch master — sessions f1eedd, 19284e>

## Summary
The raw grove-inheritance dictation file (see [[grove-inheritance-raw-dictation]]), which serves as a decision-record source of truth, was reviewed and corrected for 24 ASR mishearings — predominantly "grove/groves" misheard as "growth/grows/Bros," plus substitutions like "four King"→"forking," "bass class"→"base class," and "automatic rag"→"automatic RAG" — with all corrections applied in place while preserving the raw stream-of-consciousness texture. This cleanup fed directly into resolving the grove-inheritance architectural decision itself: future-proof architecture was prioritized over preserving existing component mechanics, memory banks follow the author's own git choice (commit vs. gitignore) rather than an enforced format, and the unnecessary `id` field was dropped in favor of git content-addressing plus parent-repo URLs. The one open question left unresolved is the connection protocol for standalone groves — whether new grove repos should connect to the main Diotima orchestrator via environment variables, directory infrastructure, MCP, or some other mechanism still to be discovered — plus the interaction model (does the user initiate from Diotima or from the grove itself). At session end, `modes/meta/architect/context.md` still carried half-finished edits (an empty "Core Pattern" heading, truncated bullets) needing cleanup, alongside the untracked raw dictation file.

## Archive
[Small bank sessions](small-bank-archive/20260726T225907-small-bank.md)
