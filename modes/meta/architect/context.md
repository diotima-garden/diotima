# Design Philosophy

*Read this when making architectural decisions — new features, structural changes, or
anything that shapes how the system grows. Not for everyday card operations.*

---

## The Skill Being Practiced Here

This project is a sandbox for **context engineering** — the discipline of shaping what
AI knows, when it knows it, and how reliably it acts on that knowledge.

The goal is to develop fluency in:

- Designing context packages that load exactly when needed, not more
- Building governance that enforces itself (hooks > manual review)
- Making AI's behavior observable and verifiable, not just assumed
- Understanding where mechanical enforcement is necessary vs. where navigation suffices

Each architectural decision is also a hypothesis about how AI behaves. Treat gaps
and failures as data, not just bugs.

---

## The Non-Duplication Principle

**If something exists somewhere, it shall be reused or made automatically reusable —
never repeated.**

This applies at every level:
- Skills are generic so a new domain needs only a context file, not a new skill
- If a rule is in its canonical location, it is not also here or in AI.md

Duplication is a signal that something hasn't found its canonical home yet.
When you notice it, consolidate — don't patch both copies.

---

## Core Pattern

```
generic skill + context file = specialized behavior
```

Skills are thin orchestration. All domain intelligence lives in context files.
The context files *are* the programs. Adding a new domain requires only a new context
file — no skill changes. This composability is the architecture's primary invariant.
Protect it.

The same principle extends to the project structure itself: new modes, new domains,
new governance layers should all slot in without modifying what already works.

---

## Design Principles

**Composability over monoliths**
New capabilities should slot in without modifying existing skills or pipelines.
If a new feature requires changing a generic skill, the context file isn't carrying
enough of the domain logic.

**Governance contracts are first-class**
Authoring rules, security constraints, and operational policies each have a single
canonical location. When a new contract is needed, find or create its home — don't
scatter it. Everything else references, never repeats.

**Token economics: lazy-load heavy context**
Always-loaded context should be minimal. Heavy context loads on demand.
Any growing file is a candidate for splitting into a thin handle and a full spec.
Apply this pattern wherever context accumulates.

---

## Modes of Operation

Three distinct modes require different context. They must not bleed into each other.

**User mode** — operational context only. The user is adding cards, running pipelines,
using the system. Architectural context should not be present.

**Builder mode** — extending current infrastructure along established patterns.
The entry points are the governance contracts (for modifying skills/pipelines) and
domain context files. No architectural decisions needed.

**Architect mode** — you are here. Changing how the system grows: new layers,
new primitives, new governance patterns, reconsidering structure.

---

## Project State

Read `product-vision.md` on entry.
Read `../memory/context.md` on entry.

---

## Layer Responsibilities

The system has distinct layers. Each layer has a single responsibility and a direction
of dependency — upper layers know about lower layers, never the reverse.

- **Domain packages** — carry their own rules and behavior; the system reads from them
- **Stdlib (skills)** — generic operations; read from packages, know nothing about pipelines
- **Application layer (pipelines)** — orchestrate skills with error handling; no inline logic
- **Enforcement layer (hooks)** — enforce contracts at write time; independent of content
- **Constitution (meta/)** — design record and governance; referenced, never modified lightly

Two structures sit alongside the stack rather than inside it:
- **Shared primitives (`.claude/utils/`)** — consumed across hooks, scripts, and pipelines; no directional dependency
- **Integration boundary (`plugins/anki-mcp/`)** — exposes external systems as native tools; referenced by pipelines, maintained as an independently-versioned submodule packaged as a plugin

Collapsing layers for convenience is always a short-term gain and a long-term cost.

---

## Structural Lessons

Meta-patterns distilled from building the systems in this project. Read these when
designing something new — they describe the shape every subsystem here has converged on.

**AI-powered subsystems follow a consistent primitive: orchestrator + isolated worker + artifact.**
The orchestrator (Python) handles deterministic mechanics: file I/O, process management,
state. The AI worker (`claude -p --bare`) handles judgment: summarization, generation,
analysis. The artifact carries output and serves as the interface between components.
This shape — and the decoupling it enforces — appears in mem-bank, health-agent, and
compiled-context generation. New AI-powered subsystems should fit it.

**Behavior is data, not code.**
AI behavior is parameterized via context files, not skill implementations. New domain =
new context file; no skill changes. This invariant has held since Phase 2. When a new
capability can't be added with only a context file, that's a signal the skill isn't
generic enough — fix the skill, don't embed the logic.

**Structural isolation is stronger than behavioral rules.**
Rules can be accidentally skipped; process boundaries cannot. When isolation matters,
use a subprocess boundary with explicit context passing — not a navigation instruction.
The compiled-context pattern is the reference: context is flattened to a single `/tmp/`
file and passed to a bare subprocess with no access to CLAUDE.md, memory, or hooks.

---
