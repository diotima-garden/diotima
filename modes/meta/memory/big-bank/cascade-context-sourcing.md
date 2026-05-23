# Why Cascade Context Sourcing

*Added 2026-04-16, commit `ce5fe2a`.*

---

Context files at different levels were repeating inherited rules. Every new package —
deck, mode, or anything added later — would require copying shared defaults in full.
That's the non-duplication principle failing at the context layer.

The fix: any `context.md` is read cascade-style. Walk up from its directory to the
project root, read every ancestor `context.md` root-first, then read the target.
Overrides land in the right order; shared rules live exactly once.

The rule lives in `.claude/rules/context-inheritance.md` (globbed to `**/context.md`)
and applies universally — decks, meta modes, any future package type. A new context
package carries only its specializations. No duplication, no drift.

A hook (`notify-context-read.py`) logs each read, making the cascade observable
rather than assumed.

---

*Related: `rules/context-inheritance.md` (the sourcing rule)*
