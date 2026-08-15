# CLAUDE.md

AI context garden and suite of tools to aid learning for humans
- working with human memory (spaced repetition - Anki - high level MCP integration)
- finding learning materials suitable to current domain skill level
- reuse and scalability of built infrastructure to evolve with demand
- potentially adaptibility to motivation curves and plateus

The longer-term direction is a generalized **learning conductor** — an interface for learning skills seamlessly, where each area carries its own intake, encoding, execution, and observability.

## Navigation

| Where | What |
|---|---|
| `groves/` | Knowledge isles — one subdirectory per area (a *grove*). Each grove holds that area's knowledge specification and, where applicable, maps to an Anki deck. This is where all area-specific knowledge lives. |
| `groves/spanish/context.md` | Spanish grove — directory overview and file index |
| `groves/english/english.md` | English grove — card types, domain tags |
| `groves/instruments/instruments.md` | Instruments grove — visual identification, image handling, IPA |
| `groves/social-dynamics/context.md` | Social dynamics grove — frame-control drills under social pressure (text-only simulator, no Anki) |
| `modes/meta/builder/context.md` | Builder mode — read before creating or modifying files outside of user areas |
| `modes/meta/architect/context.md` | Architect mode — read before any structural or design decisions |
| `modes/world-adoption/context.md` | World adoption mode — strategy, outreach, and go-to-market thinking |
| `/pipe:add-cards-to-grove` | Add cards |

When the user's intent is ambiguous — unclear whether to invoke an atomic skill or a pipeline — default to the pipeline. Pipelines are the safer path.
