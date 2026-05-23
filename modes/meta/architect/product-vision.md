# Product Vision

*Forward-looking north star. Architect-owned. Updated when direction shifts, not on every
session. For the frozen point-in-time retrospective, consult `.claude/meta/memory/context.md`

---

## What This Is Becoming

A **generalized learning conductor** — an interface a person inhabits to learn skills
seamlessly, without interruptions. The flashcard generation use case remains real, but
it is one capability among several; the system's shape is becoming domain-agnostic.

The product is an AI agent running in **user mode**, operating over a tree of
**areas** (currently named `decks/`, rename to `areas/` pending) where each leaf
directory is a self-contained learning domain — Spanish, English, instruments, and more
to come. An area is no longer just "an Anki deck"; it is a learning workspace that may
include intake (sourcing material), encoding (cards, notes), execution (study sessions),
and observability (progress, retention).

## Model-Agnostic, Open-Source Direction

The system is moving toward **model-agnosticism and open-source friendliness**. This
shapes the project layout directly:

- **`.claude/` holds only what is Claude-specific** — things that cannot be abstracted
  to a generic AI agent: Claude's slash-command skills, hooks, `settings.json`, and
  agent definitions. Everything else migrates out.
- **System infrastructure, modes, and plugins live at the project root** — visible,
  portable, not buried in a vendor-specific directory. A future port to another model
  provider touches only `.claude/`; the rest of the system is unchanged.
- **Open-source readability is a first-class constraint** — a contributor unfamiliar
  with Claude Code should be able to navigate the repo without understanding its AI
  tooling. The directory structure must communicate intent, not implementation detail.

## The Four-Pillar Trajectory

Three branches in flight today, plus the existing core, sketch the four pillars the
system is growing into:

| Pillar | Branch / Subsystem | Role |
|---|---|---|
| **Intake** | `lit_search` | Discover and ingest upstream material (reading lists, EPUBs, sources) |
| **Memory** | `mem_bank` (this branch) | Persist project-development state across sessions and worktrees |
| **Execution** | execution pipelines + MCP integration layer | Encode and act on material; MCP exposes external tools natively |
| **Observability** | `health_agent` | Detect operational friction, accumulate findings |

The four pillars are not a finished list; they are the visible shape of the system
right now. New pillars will be admitted only when an existing area's needs cannot be
served by composing the existing ones.

## Invariants the Vision Protects

- **User mode is the product.** Architect and builder modes evolve the system, but the
  thing the user experiences is user mode acting over an area. Anything that requires
  the user to enter architect or builder mode to use the product is a design failure.
- **Areas are sovereign.** Each area carries its own rules, state, and capabilities.
  The system reads from areas; areas do not need to know about the system's internals.
- **Domain-agnostic by composition.** Adding a new area should require only context
  files (and area-specific state if the area needs it), never new skills or pipelines.
  This invariant has held since Phase 2; the vision extends it to all future capabilities.

## What This Is Not

Not an MCP server. Not a flashcard tool. Not a study-app frontend. The closest
description is: *what a well-architected Claude Code workspace looks like when treated
as a personal learning operating system.*
