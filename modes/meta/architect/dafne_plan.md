# DAFNE Execution Plan

*Created 2026-07-19. All decisions feeding this plan are closed — see
`major_architectural_decision_to_be_made.md` (D0–D4 + 2026-07-18/19 rulings) and
`interaction_north_star.md`. This file is pure execution: phases in dependency order,
each with concrete steps and an exit criterion. Check off as you go.*

**Standing rules during execution** (from the record — repeated here so no phase needs
to re-read it):

- Includes are `./`-relative only; no `../` escaping a node's root; `.private/` targets
  only within the including node's own tree.
- The engine reads manifests and structure, never content.
- Version truth = submodule SHA (D4: pins + assisted update). No version data in
  `DAFNE.md`. No `parents:` field — enumeration is `readdir(parents/)`, URLs live in
  `.gitmodules`.
- `requires:` unions up the parent tree; vocabulary starts at exactly `anki`.
- Unknown manifest fields are ignored, never fatal.

---

## Phase 0 — Baseline and spike

*Nothing moves until the "before" state is frozen and the one unverified assumption is
checked.*

- [ ] Commit the pending architect-mode files (this plan, `interaction_north_star.md`,
      record amendments).
- [ ] **Golden snapshot:** compile every production entry file with the current
      context-compiler and store outputs under
      `modes/meta/architect/golden/` (or scratch, but committed is safer):
      `rioplatense-anki.md`, `english.md`, `instruments.md`. These are the byte-identity
      oracle for Phases 1–2.
- [ ] **Spike (D0's "VERIFY"):** confirm a session-start context-injection point exists —
      Claude Code hook events (`settings.json` currently uses `UserPromptSubmit`,
      `InstructionsLoaded`, …) and the opencode equivalent — and whether a *plugin* can
      ship it. Write the finding into D0's paragraph in the decision record. Blocks only
      Phase 3's injection step; everything else proceeds regardless.

**Exit:** golden outputs committed; D0 spike note written.

---

## Phase 1 — The DAFNE engine repo

*The engine exists as its own repo before any grove depends on it.*

- [ ] Create repo `diotima-garden/dafne`; mount as submodule `plugins/dafne`.
- [ ] **Absorb context-compiler** (it does not sit beside it — constitution's
      non-duplication rule): move `include_graph.py`, `preprocess.py`,
      `compiled-is-fresh.py`, `tests/`, and the compile skills into `plugins/dafne`.
- [ ] **Simplify the resolver:** delete the `project_root` branch and parameter from
      `resolve_include_path` — non-dotted include paths become a hard error with a
      message naming the discipline ("includes are `./`-relative; see DAFNE format").
- [ ] **Add the two remaining validations:** reject `../` that escapes the including
      node's root; enforce the `.private/` rule (target must lie in the including node's
      own tree, or in a transitively vendored parent tree *outside* any `.private/`).
- [ ] **Manifest reader:** parse `DAFNE.md` (`format`, `requires`, bank config);
      implement the `requires:` union walk over `parents/` manifests. Unknown fields
      ignored.
- [ ] Port the existing compiler unit tests; add fixtures for: non-dotted rejection,
      `../` escape rejection, `.private` visibility, requires-union over a two-level
      parent chain.
- [ ] Do **not** repoint the production skills yet — production includes are still
      root-relative until Phase 2 rewrites them. The old context-compiler keeps serving
      daily use until Phase 2's last step.

**Exit:** `plugins/dafne` compiles the *sandbox* (`dafne_simulation/spanish`)
byte-identical to the golden-equivalent sandbox output; all new validation fixtures
pass; production still compiles via the old path.

---

## Phase 2 — Production groves surgery (promote → vendor → rewrite)

*The transform the sandbox validated the target of, executed on the real tree. Sequence
matters: promoting before vendoring avoids ever authoring the `../`-escape
anti-pattern.*

**Target topology** (sandbox-proven; hierarchy expressed by `parents/`, not by directory
nesting — grove repos are siblings):

```
deck        ← groves/deck-defaults.md + groves/languages/cloze-deletion.md   (bare node)
language    ← language-defaults, creative-usages, production_vs_comprehension
              + parents/deck                                                 (bare node)
spanish     ← spanish grove content + state + parents/language               (grove)
english     ← english.md + backups + parents/language                        (grove)
instruments ← instruments.md + backups + parents/deck                        (grove)
```

- [ ] **Promote:** create repos `diotima-garden/deck` and `diotima-garden/language` from
      the loose files above, each with a `DAFNE.md` (copy from
      `dafne_simulation/deck/DAFNE.md` and `language/DAFNE.md` — they are the validated
      templates). `language` gets `parents/deck` as a pinned submodule; rewrite its
      includes to `./parents/deck/...`. Push both.
- [ ] **Vendor + rewrite the groves:** create repos `spanish`, `english`, `instruments`.
      Move all content *and state* (backups, `reading-log/`, `files/`,
      `deck_quality_bootstrapping/`, feedback `.jsonl`) into them — state lives in the
      grove. Add `parents/language` (spanish, english) / `parents/deck` (instruments)
      submodules; rewrite every include to `./`-relative. Each grove's `DAFNE.md`
      carries its bank config (Phase 3 fills the values).
- [ ] **Remount in master:** delete the old `groves/` contents; mount the three grove
      repos as submodules (`groves/spanish`, `groves/english`, `groves/instruments` —
      flat; `deck` and `language` arrive only as nested submodules inside them).
      `groves/managed-models.json` is runtime/anki state, not grove content — move it to
      the anki-mcp side, not into any grove.
- [ ] **Verify:** `git clone --recursive` each grove repo to a temp dir; compile
      standalone with `plugins/dafne`; byte-compare against Phase 0 golden outputs.
      This is the record's own D3 test, now on production content.
- [ ] **Repoint and retire:** switch the compile skills to `plugins/dafne`; remove
      `plugins/context-compiler` (its repo is absorbed, per Phase 1).
- [ ] **Cleanup:** delete `dafne_simulation/` — it has served; fold any still-open notes
      from `dafne_simulation/context.md` into the decision record first.

**Exit:** every grove clones standalone and compiles byte-identical to golden with zero
edits; master's `groves/` holds only submodule mounts; context-compiler is gone.

---

## Phase 3 — Runtime wiring

*The runtime discovers what groves declare — the D1(b) contract goes live.*

- [ ] **Kill the last runtime→grove-interior path:** move each bank's declaration
      (`name`, `patterns`, `graduate`, `recurse-mem-enable: false` default) from
      `.claude/mem-bank/subscriptions.json` into the owning grove's `DAFNE.md` bank
      config. mem-bank machinery enumerates mounted groves and reads their manifests;
      `subscriptions.json` retains only runtime-side preferences, or dies.
- [ ] **`requires:` refusal:** opening a grove whose effective (unioned) requires
      includes `anki` in a runtime without anki-mcp produces a plain, early message —
      not a deep pipeline failure. A grove requiring nothing is first-class.
- [ ] **Manifest injection at session start**, per the Phase 0 spike finding. Claude
      Code port lives in `.claude/`; the mechanism itself is vendor-neutral.
- [ ] **Assisted update (D4's second half):** a "tend parents" flow — fetch upstreams of
      everything under `parents/` (recursively), nudge on new commits, show the
      **compiled-output diff**, and on acceptance commit the new pin. Runtime-side, so
      it improves ambiently; no grove is touched by its existence.

**Exit:** `subscriptions.json` contains no path into any grove's interior; a
missing-anki refusal is demonstrable; a parent update lands via the tend flow end-to-end
on one real grove.

---

## Phase 4 — Launch UX (north-star stage B + A-as-default)

*From `interaction_north_star.md`: git-model primitive, garden dir as default, C
deferred.*

- [ ] `diotima` launcher on PATH: if cwd (or an ancestor) has `DAFNE.md` → launch the
      runtime there, grove = project root; else → show the picker.
- [ ] Picker sources = union of dumb, disposable data: `readdir(~/diotima-garden)`
      filtered on `DAFNE.md` ∪ MRU recents file (`~/.local/state/diotima/recent`,
      appended on every grove open). No daemon, no registry, no grove-side
      registration — this keeps the simple-GUI door open.
- [ ] Grove creation defaults to `~/diotima-garden/<name>` unless a path is given.

**Exit:** clone `spanish` to an arbitrary directory → `diotima` → the session plays it;
it appears in the picker afterward; a fresh install with an empty garden leads with
"plant your first grove."

---

## Phase 5 — Deferred: doors held open, nothing built

| Door | Trigger to build | What was pre-paid |
|---|---|---|
| Version ranges | first real cross-grove propagation pain | additive `versions:` field; unknown-fields rule degrades old runtimes to pins |
| `requires:` local mask | first grove that must suppress an inherited capability | union doesn't foreclose it |
| Content-addressed text dedup | first vendored diamond actually splicing twice | content is intrinsic; no field needed |
| D5 marketplace / scenario-C verbs | first *published* grove + real adoption demand | store dir unions into the picker; verbs layer on the same primitive |
| Node-carried skills | first real instance | harvest → declare → consent contract already ruled |

Building any of these before its trigger is designing from zero instances.

---

## Dependency graph

```
Phase 0 ──> Phase 1 ──> Phase 2 ──> Phase 3 ──> Phase 4
   └── spike blocks only Phase 3's injection step
```

Phases 1–2 are the irreversible core (published-format discipline); 3–4 are runtime-side
and stay cheap to revise. When Phase 2 completes, `major_architectural_decision_to_be_made.md`
can be renamed to a closed decision record — every question in it will be either ruled
or executed.
