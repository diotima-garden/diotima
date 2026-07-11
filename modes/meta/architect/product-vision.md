# Product Vision

*Forward-looking north star. Architect-owned. Updated when direction shifts, not on every
session. For the frozen point-in-time retrospective, consult `.claude/meta/memory/context.md`

---

## What This Is Becoming

An **ecosystem and infrastructure for knowledge generators**, under the name **Diotima**
(diotima.garden, github.com/diotima-garden).

The system has two layers, and the distinction between them is the central architectural
fact:

- **Groves are the product.** A grove is a sovereign, self-contained knowledge package —
  a domain's generative spec: how a knowledgeable person breaks the subject down, what's
  worth encoding, what "good" looks like, how source material gets pulled in. Groves are
  designed to be **published, inherited, and re-aimed**: you take an expert's grove and
  redirect its method at your own subject (fork-and-refocus). A grove carries its own
  rules, state, and — as the format matures — its own infrastructure.
- **The orchestrator is the runtime.** The learning-conductor machinery (pipelines,
  skills, MCP integration, context compilation) is what *plays* a grove: intake, encoding,
  execution, observability. It is domain-blind by design. Think MP3 player and music: the
  runtime is necessary, but the value people exchange is the groves.

The flashcard-generation use case remains real and daily-driven, but it is one capability
of the runtime — not the product's identity. The strategic direction is making groves
trivially easy to **create, deploy, share, and compose**, so that sharing *how to learn a
domain* becomes as natural as sharing what to learn.

Design inspiration for the grove format comes from ecosystems that solved analogous
problems: **Docker images** (self-contained, layered, composable units with their own
infrastructure) and **multiple inheritance** (a grove derives from several parents and
recombines their methods). These are reference points, not commitments — the concrete
semantics are not yet designed.

## Model-Agnostic, Open-Source Direction

The system is moving toward **model-agnosticism and open-source friendliness**. The
concrete planned direction is a migration toward **opencode** as a portable,
provider-agnostic runtime. This shapes the project layout directly:

- **`.claude/` holds only what is Claude-specific** — things that cannot be abstracted
  to a generic AI agent: Claude's slash-command skills, hooks, `settings.json`, and
  agent definitions. Everything else migrates out.
- **System infrastructure, modes, and plugins live at the project root** — visible,
  portable, not buried in a vendor-specific directory. A port to another provider touches
  only `.claude/`; the rest of the system is unchanged.
- **Open-source readability is a first-class constraint** — a contributor unfamiliar
  with Claude Code should be able to navigate the repo without understanding its AI
  tooling. The directory structure must communicate intent, not implementation detail.

## The Ecosystem Trajectory

The visible shape of where the system is growing, replacing the earlier four-pillar
subsystem view:

| Pillar | Role |
|---|---|
| **Grove format** | What makes a grove self-contained and portable: its packaging boundary, its declared capabilities, its internal infrastructure |
| **Inheritance & composition** | Fork-and-refocus and multi-parent derivation — the semantics of building a new grove from existing ones |
| **Distribution** | The marketplace/registry layer: how groves are published, discovered, and adopted |
| **Runtime** | The orchestrator that plays any grove — moving toward a provider-agnostic base |

Groves are not runtime infrastructure: a grove relies on infrastructure existing but
never knows which implementation serves it. What the grove format takes from packaging
ecosystems is the property set — independently versioned, distributable, behind a clean
boundary — not a place in the runtime's plugin machinery.

## Invariants the Vision Protects

- **User mode is the product.** Architect and builder modes evolve the system, but the
  thing the user experiences is user mode acting over a grove. Anything that requires the
  user to enter architect or builder mode to use the product is a design failure.
- **Groves are sovereign.** The runtime reads from groves; groves never need to know
  about the runtime's internals.
- **Groves are the unit of sharing.** Anything added to a grove must survive being
  forked and inherited; publishing a grove must never require touching the orchestrator.
- **Domain-agnostic by composition.** Adding a new grove should require only context
  files (and grove-specific state if the grove needs it), never new skills or pipelines.
  This invariant has held since Phase 2; the vision extends it to all future capabilities.

## What This Is Not

Not an MCP server. Not a flashcard tool. Not a study-app frontend. The closest
description is: *a runtime, a package format, and an ecosystem for knowledge
generators — groves people build for their own daily learning and share at no extra
cost.*
