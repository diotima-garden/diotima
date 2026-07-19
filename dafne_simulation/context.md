# DAFNE simulation — grove inheritance played out on disk

*This is the sandbox, not the engine. DAFNE (Directory Architecture for Fractal Nested Ecosystems) — the deterministic interpreter of the node tree — will be its own
repository, mounted under `plugins/` like context-compiler and anki-mcp.*

Experimental space for the grove inheritance & distribution decision
(`modes/meta/architect/major_architectural_decision_to_be_made.md`).
Each top-level directory here simulates a **standalone repository**;
`parents/<name>` symlinks simulate git submodules. Nothing here is
production — `groves/` remains the live tree until this graduates.

## The chain under test

```
spanish (grove) ──parents──> language (node) ──parents──> deck (node, root)
```

| Dir | Simulated repo | Kind | Carries |
|---|---|---|---|
| `deck/` | SRS card base | bare node, root | `deck-defaults.md`, `cloze-deletion.md` |
| `language/` | language-learning base | bare node | `language-defaults.md`, pedagogy notes |
| `spanish/` | leaf | **grove** (node + memory) | rioplatense deck spec, focus area, reading-log mem-bank |

## Protocol rulings enacted here (2026-07-18)

- **`DAFNE.md` is the manifest.** Its presence marks a directory as a DAFNE
  node. Carries `format`, `requires`, and — for groves — bank config.
- **Node vs grove:** a *grove* is a node carrying memory. Inferred
  structurally (bank declaration / `memory/`), never via a `type:` field.
- **Parents are never manifest data.** Enumeration = `readdir(parents/)`;
  URLs = `.gitmodules`. Termination = no `parents/` directory — no sentinel
  repo, no `parents: []` field. (An earlier `grove/` root-base dir was
  built, stayed empty, and was deleted — hypothesis confirmed.)
- **All includes `.`-relative** (D3 discipline); verified byte-identical to
  the production `groves/` chain and position-independent standalone.

## Boundary calls made when populating (challenge these)

- `deck-defaults.md` is not universal content — anki is an optional
  capability (D2); it became the root `deck` node.
- `cloze-deletion.md` moved from `language` to `deck` — its content is
  Anki cloze mechanics, not language-specific. Also tests multi-file
  parent access (language includes two files from one parent).

## Open questions parked here

- Does `requires:` union up the parent tree, or must each node re-declare?
  (flagged in `language/DAFNE.md`)
- D4 pin vs range: dropping `parents:` from the manifest leans toward
  submodule pins — a range would need the field back, since `.gitmodules`
  can only express pins. Keep this a conscious choice, not a default.
- `.private/` visibility (reserved concept, not yet exercised here): an
  include may target its own tree, or a vendored parent tree *outside* any
  `.private/`.

## Known fidelity gap vs real submodules

Symlinks canonicalize: a diamond parent reached via two symlink chains
resolves to **one** real path, so path-keyed dedup collapses it. Real
vendored submodules would be two distinct copies — the case that needs
content-addressed dedup. Do not use this sandbox to claim diamonds are
solved.
