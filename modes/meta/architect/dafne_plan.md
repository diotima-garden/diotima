# DAFNE Execution Plan

*Created 2026-07-19. All decisions feeding this plan are closed — see
`grove_inheritance_decisions.md` (D0–D4 + 2026-07-18/19 rulings) and
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

- [x] Commit the pending architect-mode files (this plan, `interaction_north_star.md`,
      record amendments). — `7ce9675`
- [x] **Golden snapshot:** preprocessed (deterministic `#include`-resolved) output for
      every production entry file, stored at `modes/meta/architect/golden/`:
      `spanish.golden.md`, `english.golden.md`, `instruments.golden.md` (named off
      `*.golden.md`, not `*.preprocessed.md`, since the latter is project-gitignored as
      a regenerable build artifact — these are a deliberate committed oracle). This is
      the byte-identity oracle for Phases 1–2. **Bonus verification run now:**
      `dafne_simulation/spanish`'s `.`-relative rewrite recompiles byte-identical to
      `golden/spanish.golden.md` — the DAFNE amendments' claim is confirmed against
      production content, not just the sandbox's own fixtures.
- [x] **Spike (D0's "VERIFY"):** confirmed via Claude Code docs. `SessionStart` is a
      native hook event (distinct from `UserPromptSubmit`), fires once per session before
      the first prompt, supports `additionalContext` injection, and plugins ship it via
      `hooks/hooks.json` with automatic merge on install — no grove-level config needed.
      Finding written into D0's paragraph in the decision record. opencode's equivalent
      remains unverified but is not architecture-blocking.

**Exit:** golden outputs committed; D0 spike note written. **Phase 0 complete.**

---

## Phase 1 — The DAFNE engine repo

*The engine exists as its own repo before any grove depends on it.*

- [x] Create repo `diotima-garden/dafne`; mount as submodule `plugins/dafne`.
- [x] **Absorb context-compiler** (it does not sit beside it — constitution's
      non-duplication rule): move `include_graph.py`, `preprocess.py`,
      `compiled-is-fresh.py`, `tests/`, and the compile skills into `plugins/dafne`.
- [x] **Simplify the resolver:** delete the `project_root` branch and parameter from
      `resolve_include_path` — non-dotted include paths become a hard error with a
      message naming the discipline ("includes are `./`-relative; see DAFNE format").
- [x] **Add the two remaining validations:** reject `../` that escapes the including
      node's root; enforce the `.private/` rule (target must lie in the including node's
      own tree, or in a transitively vendored parent tree *outside* any `.private/`).
- [x] **Manifest reader:** parse `DAFNE.md` (`format`, `requires`, bank config);
      implement the `requires:` union walk over `parents/` manifests. Unknown fields
      ignored.
- [x] Port the existing compiler unit tests; add fixtures for: non-dotted rejection,
      `../` escape rejection, `.private` visibility, requires-union over a two-level
      parent chain.
- [x] Do **not** repoint the production skills yet — production includes are still
      root-relative until Phase 2 rewrites them. The old context-compiler keeps serving
      daily use until Phase 2's last step.

**Exit:** `plugins/dafne` compiles the *sandbox* (`dafne_simulation/spanish`)
byte-identical to the golden-equivalent sandbox output; all new validation fixtures
pass; production still compiles via the old path. **Phase 1 complete** — 39/39 tests
pass; sandbox recompiles byte-identical to `golden/spanish.golden.md`; repo pushed to
`diotima-garden/dafne` (public), mounted as submodule. One deviation from the plan's
literal wording: the node-root escape check operates on the *authored* include path
lexically, not on the fully symlink-resolved target — the sandbox's `parents/` mounts
are relative symlinks that physically escape upward (documented fidelity gap vs. real
submodules in `dafne_simulation/context.md`), so a resolve()-based check would reject
legitimate parent traversal. Real submodules sit physically inside the node's tree, so
this makes no difference in production.

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

- [x] **Promote:** create repos `diotima-garden/deck` and `diotima-garden/language` from
      the loose files above, each with a `DAFNE.md` (copy from
      `dafne_simulation/deck/DAFNE.md` and `language/DAFNE.md` — they are the validated
      templates). `language` gets `parents/deck` as a pinned submodule; rewrite its
      includes to `./parents/deck/...`. Push both.
- [x] **Vendor + rewrite the groves:** create repos `spanish`, `english`, `instruments`.
      Move all content *and state* (backups, `reading-log/`, `files/`,
      `deck_quality_bootstrapping/`, feedback `.jsonl`) into them — state lives in the
      grove. Add `parents/language` (spanish, english) / `parents/deck` (instruments)
      submodules; rewrite every include to `./`-relative. Each grove's `DAFNE.md`
      carries its bank config (Phase 3 fills the values).
- [x] **Remount in master:** delete the old `groves/` contents; mount the three grove
      repos as submodules (`groves/spanish`, `groves/english`, `groves/instruments` —
      flat; `deck` and `language` arrive only as nested submodules inside them).
      `groves/managed-models.json` is runtime/anki state, not grove content — move it to
      the anki-mcp side, not into any grove.
- [x] **Verify:** `git clone --recursive` each grove repo to a temp dir; compile
      standalone with `plugins/dafne`; byte-compare against Phase 0 golden outputs.
      This is the record's own D3 test, now on production content.
- [x] **Repoint and retire:** switch the compile skills to `plugins/dafne`; remove
      `plugins/context-compiler` (its repo is absorbed, per Phase 1).
- [x] **Cleanup:** delete `dafne_simulation/` — it has served; fold any still-open notes
      from `dafne_simulation/context.md` into the decision record first.

**Exit:** every grove clones standalone and compiles byte-identical to golden with zero
edits; master's `groves/` holds only submodule mounts; context-compiler is gone.
**Phase 2 complete (2026-08-15).** Six repos pushed and mounted, not three — the plan's
target topology didn't cover `groves/social-dynamics/`; extracted anyway as a bare root
grove per an explicit scope decision when this phase began (see `grove_inheritance_decisions.md`).
Two smaller deviations from the plan's literal text, both decided the same way:
`queue-policy.md` (not in the plan's file table at all) landed in `language` alongside
`language-defaults.md`; `groves/managed-models.json` stayed in `groves/` rather than
moving to the anki-mcp side — deferred, not forgotten, since it touches a second repo
(`plugins/anki-mcp`) this session left alone. `spanish`/`english`/`instruments` verified
byte-identical to `golden/*.golden.md` three ways: from the master-mounted submodules,
from a genuinely standalone `git clone --recursive`, and (for spanish) from the sandbox
before it was deleted. `groves/mem-bank-subscriptions.json`'s `spanish-reading` bank path
was updated to the new mount point as a courtesy — the live subscription source of truth
stays this file, not any grove's `DAFNE.md`, until Phase 3 runs.

---

## Phase 3 — Runtime wiring

*The runtime discovers what groves declare — the D1(b) contract goes live.*

- [x] **Kill the last runtime→grove-interior path:** move each bank's declaration
      (`name`, `patterns`, `graduate`, `recurse-mem-enable: false` default) from
      `.claude/mem-bank/subscriptions.json` into the owning grove's `DAFNE.md` bank
      config. mem-bank machinery enumerates mounted groves and reads their manifests;
      `subscriptions.json` retains only runtime-side preferences, or dies.
      → **Designed in `bank_discovery_wiring.md` (2026-08-29), executed and verified
      2026-08-29.** `plugins/dafne/manifest.py` gained `discover_banks`/
      `discover_grove_banks` (recursive, absolute `bank:` paths, opaque payload
      passthrough) plus a `discover_banks.py` CLI, with 9 new fixtures (48/48 dafne
      tests pass). `plugins/mneme` gained one optional `banks=` parameter on
      `small-bank.py`'s `run_hook` and `big-bank.py`'s `main` — standalone CLI
      behavior confirmed byte-identical when omitted. `system/diotima/bank_union.py`
      is the one place the two vocabularies meet; `invoke-mneme-on-groves.py`
      replaces the old session-end hook entry, and `graduate-banks.py` replaces the
      `mem-bank-big-bank` skill's direct call — this second script fills a gap the
      design doc's spec left open (it added `banks=` to `big-bank.py.main` but never
      wrote a caller for it; without one, trimming `subscriptions.json` would have
      silently stopped grove banks from ever graduating). `system/mem-bank-
      subscriptions.json` now holds only `meta`/`world-adoption`; `groves/mem-bank-
      subscriptions.json` is deleted. `groves/spanish/DAFNE.md` and `groves/social-
      dynamics/DAFNE.md` had their placeholder-scaffold paragraphs removed. Verified
      end-to-end against scratch fixtures (not production banks): a `graduate: true`
      grove bank was proven to actually reach `big-bank`'s read step (discriminated
      from a `graduate: false` sibling, which was correctly skipped before ever being
      read) and a pattern-matching session-end transcript was proven to queue a job
      with the bank path resolved from the grove's manifest — with `JOBS_DUMP_PATH`
      and `spawn_worker` monkeypatched so no real job queue or LLM subprocess was
      touched. Standalone `--subscriptions` invocation of both mneme scripts confirmed
      unchanged. Commits pending across `plugins/dafne`, `plugins/mneme`,
      `groves/spanish`, `groves/social-dynamics`, and `master` (submodule pointer
      bumps) — not yet pushed.
- [x] **`requires:` refusal:** opening a grove whose effective (unioned) requires
      includes `anki` in a runtime without anki-mcp produces a plain, early message —
      not a deep pipeline failure. A grove requiring nothing is first-class.
      → **Designed in `requires_refusal.md` (2026-08-29), executed and verified
      2026-08-29.** `plugins/dafne/manifest.py` gained `Requirement` and
      `requirements_with_provenance` (5 new fixtures, 53/53 dafne tests pass);
      `system/diotima/capabilities.py` is the new probe (`installed_capabilities`,
      reading the interpreter/server paths out of `.mcp.json` rather than hardcoding
      them) and `system/diotima/check-requires.py` the CLI, emitting
      `REQUIRES_SATISFIED` / `REQUIRES_UNSATISFIED` / `REQUIRES_UNKNOWN` per the design's
      exact token convention. Both pipeline command files
      (`add-cards-to-grove.md`, `tackle-feedback-on-grove.md`) gained a step-0 preflight
      bash call, before the background compile fork. The `requires: []` line was
      dropped from the four leaf grove manifests (spanish, english, instruments,
      social-dynamics); `language`'s copy was deliberately left alone per the design's
      own carve-out, so "every `requires:` line in the tree is a real claim" holds for
      the four leaves grove authors copy, not literally tree-wide. Verified against
      production, not just fixtures: `requirements_with_provenance` returns the exact
      provenance paths the design's exit criteria name for spanish
      (`parents/language/parents/deck`), instruments (`parents/deck`), and empty for
      social-dynamics; with `plugins/anki-mcp/.venv` temporarily renamed (and restored
      immediately after), the CLI against `groves/spanish` printed
      `REQUIRES_UNSATISFIED` with the provenance path and the `missing:` path line,
      never reaching a compile fork — the fork claim is structurally true from
      preflight placement rather than independently driven, since this session has no
      way to run the LLM pipeline itself; a fabricated node declaring an unnamed
      capability correctly returned `REQUIRES_UNKNOWN` and would block nothing; `grep`
      over non-test `plugins/dafne` files confirms zero mentions of anki, `.mcp.json`,
      or installation. One implementation deviation from the design's literal text:
      `requirements_with_provenance` guards recursion with a per-path `ancestors` set
      (frozenset, copied down each branch) instead of `effective_requires`'s global
      `seen` set — a diamond's second branch to the same physical parent must still be
      walked and recorded (two distinct declaring paths), which a global visited-set
      would suppress. A new test asserts the two functions' name-sets still agree on
      the diamond fixture, since that agreement is now load-bearing. One adjacent,
      out-of-scope finding surfaced during golden-oracle verification: recompiling
      `groves/spanish/rioplatense-anki.md` no longer matches
      `golden/spanish.golden.md` (183-line diff) — confirmed pre-existing (identical
      with this session's changes stashed out), unrelated to `DAFNE.md` edits (manifests
      were never part of the include graph), and not caused by this bullet; the golden
      snapshot itself is stale against real content drift and needs its own refresh,
      tracked separately. Commits pending across `plugins/dafne`, the four grove repos,
      and `master` (submodule pointer bumps, plus `.claude/settings.json` and the two
      pipeline command files) — not yet pushed.
- [ ] **Manifest injection at session start:** `plugins/dafne` ships a `SessionStart`
      hook (`hooks/hooks.json`) that reads `DAFNE.md` from cwd and returns it as
      `additionalContext` — confirmed viable in Phase 0, no grove-side files needed. The
      Claude Code hook is the vendor-specific port; opencode gets its own when that
      migration starts.
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
```

Phases 0–2 are complete (2026-08-15). No open spike remains blocking any later phase.

Phases 1–2 were the irreversible core (published-format discipline); 3–4 are
runtime-side and stay cheap to revise. `grove_inheritance_decisions.md` has been
renamed from `major_architectural_decision_to_be_made.md` — every question in it is
now either ruled or executed. Phase 3 (runtime wiring: `subscriptions.json` →
`DAFNE.md` bank config, `requires:` refusal, `SessionStart` manifest injection,
assisted-update flow) and Phase 4 (launch UX) remain, deliberately deferred — not
part of this session's scope.
