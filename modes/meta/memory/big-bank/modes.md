# Why Three Modes (User / Builder / Architect)

*Added 2026-04-16, commit `86b7204`.*

---

Before modes existed, meta-context had no address. Architectural reasoning and governance
contracts were either always loaded (token waste) or absent when needed (compliance gap).

The fix: three named modes, each with its own context package. User mode loads nothing
meta. Builder mode loads governance contracts. Architect mode loads this directory.
Routing is explicit in CLAUDE.md; a hook makes compliance observable.

The alternative — injecting everything via hooks — would make compliance invisible.
Navigation makes the mode switch legible and the gap diagnosable. That's the point:
this project exists to understand how Claude behaves, so enforcement that can't be
observed defeats the purpose.

---

*Related: `context.md` (architect-mode spec) · `meta/builder/context.md` (builder contracts)*
