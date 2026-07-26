# Anki Mcp Followups And Server Issues

<2026-07-23 to 2026-07-26 — branch master — sessions 6853c9, c9a274, 202fb2>

## Summary
An end-to-end test of the Spanish deck feedback-processing pipeline ran backup, user-feedback extraction, LLM-driven edits, and confirmation successfully (exit 0); changes were committed and pushed to both the diotima parent repo and the anki-mcp submodule, and a known gap — missing `TimeoutExpired` handling in the retry loop — was filed as anki-mcp#4 rather than fixed inline, validating that the feedback-application infrastructure runs cleanly end-to-end. Separately, the `youtube-extract` skill was changed to append extracted phrases to `youtube-phrases.txt` instead of overwriting it, enabling safe accumulation across multiple video extractions in a single run (committed as `2dfada7`), with the output file remaining gitignored so only the source code is tracked. Three further GitHub issues were later filed across the anki-mcp and diotima repos: card feedback-driven state changes (unsuspend/unbury), extending card-creation logs to capture source text via the existing `log` field mechanism already managed by `_update_note_fields`, and completing Gemini extraction by moving `.claude/gemini` into a dedicated `utils/llm_invoke` hierarchy — noting `youtube-extract` specifically needs Gemini's video-URL capability rather than a generic multi-provider abstraction. All three issues flagged open design decisions (where seeding happens, field-size constraints, target location vs. precedent, eventual provider split) without prescribing solutions, deliberately reusing existing patterns rather than proposing new infrastructure.

## Archive
[Small bank sessions](small-bank-archive/20260726T225907-small-bank.md)
