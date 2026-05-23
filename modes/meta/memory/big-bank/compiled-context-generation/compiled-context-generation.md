# Why Compiled Context + Isolated Generation

*Added 2026-04-19, plan `cheerful-stirring-matsumoto`.*

---

Card generation previously relied on a navigation rule (`context-inheritance.md`) telling
Claude to walk up the directory tree and read ancestor `context.md` files at generation
time. This is unenforced — Claude can silently skip layers, and the full CLAUDE.md,
memory, hooks, and conversation history all bleed into what should be a pure generation
step.

The fix: split generation into two phases.

**Compilation** (`compile-deck-context`) flattens the full context inheritance chain into
a single file at `/tmp/compiled-context-<deck>.md`. This uses the existing `depolymorphize`
skills — no duplication of merge logic.

**Generation** (`anki-add-cards`) spawns a bare Claude subprocess (`claude -p --bare`)
that sees only the compiled context as its system prompt and the user's card input as
the user prompt. No CLAUDE.md, no memory, no rules, no hooks — a clean slate. The
parent session captures stdout, previews the cards, waits for confirmation, and pushes
to AnkiConnect.

The isolation guarantee is structural, not behavioral. It doesn't matter whether
Claude would have read the context correctly in the old flow — the subprocess
physically cannot access anything outside what it's given.

---

*Related: `skill/compile-deck-context.md`, `skill/anki-add-cards.md`, plan `cheerful-stirring-matsumoto`*
