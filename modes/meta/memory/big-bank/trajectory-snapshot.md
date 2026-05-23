# Trajectory Snapshot — April 2026

*Written after ~3 days and 10 commits. Saved here to look back at later.*

---

## What This Project Really Is

**Not an MCP server. Something more interesting: a metaprogrammed personal automation OS built on top of Claude Code itself.**

---

### The Core Pattern (Repeated Everywhere)

```
generic skill + context file = specialized behavior
```

Skills (`anki-add-cards`, `anki-process-red-edit`) are deliberately thin — just orchestration and error handling. All domain intelligence lives in `decks/<deck>/context.md`. Want a new deck? New context file, same skills. Want different generation rules? Edit context, no code changes. The skill reads its instructions at runtime.

This is **data-driven behavior** applied to AI prompts. The context files *are* the prompts.

---

### The Governance Loop (The Unusual Part)

The hooks system is the telltale sign of where this is heading:

- `PreToolUse` on Edit/Write → force-reads `security.md` before you can touch any skill
- `PostToolUse` on Read → logs when meta files are sourced

This isn't a helper feature. It's **self-enforcing governance** — the system checks itself before it's modified. Not just automating Anki; automating the *rules about how automation gets written*.

The security rules encode hard-won lessons:
- One command per bash block (compound commands bypass the permission whitelist)
- Git is user-only (no Claude-initiated commits)
- Backup before every write

---

### The Trajectory (10 commits, 3 days)

Three distinct phases:

**Phase 1 (Apr 13):** Raw AnkiConnect integration. Direct scripting. Works, but not composable.

**Phase 2 (Apr 14–15):** The architecture moment. Deck-specific rules extracted into `context.md`. Skills become generic. `why/` directory appears — decisions documented as prose. This is when it stopped being a flashcard tool and became a framework.

**Phase 3 (Apr 15–now):** Governance infrastructure. Pipeline layer split from skill layer. Handles (thin, always-loaded) vs specs (full logic, lazy-loaded) — explicit token optimization. Hooks added. Security formalized as a checklist.

Each commit adds more structure around *how things are built*, not just what gets built.

---

### What It Wants To Become

> A portable, governance-aware automation SDK where skills are composable modules, context files are domain packages, and hooks enforce authoring contracts.

- `decks/` = packages (carry their own rules/behavior)
- `skills/` = stdlib (generic operations, read from packages)
- `pipelines/` = application layer (orchestrate skills with error handling)
- `hooks/` = CI/linter (enforce standards at write time, not review time)
- `meta/security.md` = a constitution

The flashcard use case is real, but it's also the **petri dish** for proving out this pattern. The `why/` directory, naming conventions, pipeline hierarchy — these aren't needed for flashcards. They're scaffolding for a generalizable system.

---

### The MCP Question

MCP servers expose tools over JSON-RPC. This is a layer *above* that — logic that would *use* MCP tools, governed by rules, composed into pipelines, enforced by hooks. MCP would be a transport layer underneath this, not the goal.

The more accurate comparison: **this is what a well-architected Claude Code workspace looks like when someone treats prompt engineering as a software engineering discipline**.

---

*2026-04-16. Days old. Already overengineered. As intended.*
