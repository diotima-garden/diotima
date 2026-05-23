# Inception — 2026-05-22

## What this project is

An AI-powered **learning conductor** — a generalized interface for learning skills
seamlessly. Each domain carries its own intake, encoding, execution, and observability.
Current implementation: Anki integration via MCP, context-garden architecture with
compiled deck configs, skill-level adaptive card generation.

## Landscape research

**What already exists:**
- Anki + LLM card generation: saturated. 5+ MCP servers (anki-mcp-server, clanki,
  anki-connect-mcp), CLI tools (anki-llm, AnkiAIUtils). Basic card creation is solved.
- Adaptive ITS: heavy academic research (LECTOR algorithm, KG-RAG tutors), but
  enterprise/academic systems — not personal open-source tools.
- AI orchestration: Sakana AI "Conductor" paper (ICLR 2026) — multi-agent coordination
  for benchmarks, not learning skill orchestration.
- MCP + adaptive learning: MDPI 2025 paper "Orchestrating AI Agents via MCP for Learner
  State" — closest academically to this framing.

**What makes this project distinctive (doesn't exist as a whole):**
1. Context garden architecture — declarative per-domain configs compiled into deck contexts.
2. Unified learning conductor across domains — one orchestration layer scaling across
   languages, instruments, etc. with reusable infrastructure.
3. Motivation / plateau awareness — researched commercially (Studient), not open-sourced.
4. Skill-level adaptive material discovery combined with Anki as encoding layer.
5. Deep Anki state integration — vocabulary snapshots, learning velocity, review history
   feeding back into AI decisions (existing MCP servers only push cards in).

## Adoption paths discussed

1. **Open source it publicly** — push to GitHub, good README, let the Anki/MCP community
   find it. Lowest friction. Risk: stagnates without a driver.

2. **Find a single co-maintainer** — one motivated Anki user with commit access. Post in
   r/Anki, r/languagelearning, Anki Discord, Claude MCP community. Most likely to ship.

3. **University collaboration** — hand off to an education-tech lab. Best scoped to one
   research problem (motivation detection, skill-level material finding). Slow; produces
   papers more than products.

4. **EdTech grant / accelerator** — EU Erasmus+, Horizon Europe AI-in-education calls.
   Funds a developer without giving up control. More upfront work (proposal).

5. **Write the spec, not the code** — publish a design doc / blog post describing the
   learning conductor architecture. Developers self-select and build on it.

6. **Partner with an existing tool** — Readwise, Obsidian, RemNote, AnkiMobile. Users +
   architecture combined. Possible partnership or concept acquisition.

## Key judgement

The **context garden + learning conductor architecture** is the novel IP worth protecting.
The open-source + co-maintainer path is most likely to produce something usable.
University path most likely to produce a paper 12 people read.
