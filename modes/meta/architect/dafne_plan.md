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
      unchanged. Committed and pushed across `plugins/dafne`, `plugins/mneme`,
      `groves/spanish`, `groves/social-dynamics`, and `master` (submodule pointer
      bumps, `da0f805`).
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
      snapshot itself is stale against real content drift and needs its own refresh —
      parked by an explicit 2026-08-29 call until the DAFNE migration finishes and
      integration testing begins; no issue tracks it, this note is the record.
      Committed and pushed across `plugins/dafne`, the four grove repos, and `master`
      (submodule pointer bumps, plus `.claude/settings.json` and the two pipeline
      command files, `39330e6`).
- [x] **Manifest injection at session start:** a `SessionStart` hook shipped by
      `plugins/dafne` (`hooks/hooks.json`) injects orientation as `additionalContext`.
      Two branches, per the 2026-09-07 rulings below: cwd is a grove → inject its
      `DAFNE.md`; otherwise → inject the garden's grove list. Only the second is
      reachable today, since sessions start in the orchestrator; the first goes live when
      the launcher can drop a session into a grove directory. The Claude Code hook is the
      vendor-specific port; opencode gets its own when that migration starts.
      → **Spiked 2026-09-07.** Results, all empirical (nested `claude` sessions, scratch
      fixtures):
      (a) `SessionStart` fires — including in print mode — and its `additionalContext`
      **provably reaches the model**: a codeword injected by the hook came back from a
      session that had no other source for it. Phase 0 had only confirmed this from docs.
      (b) `InstructionsLoaded`, which this project already runs with `session_start:`
      context, does **not** accept `additionalContext` — the same codeword test returned
      `NONE`. It is not an alternative injection path.
      (c) **Plugin-root `hooks/hooks.json` merges, and the hook travels with the engine.**
      A first run of this test concluded the opposite. It was invalid, and is recorded
      here because the failure mode is easy to repeat. Plugins in this workspace are
      **not** auto-discovered from `plugins/`: the workspace-level `profile` defines a
      `claude` shell function that scans `master/plugins/*/` for `.claude-plugin` and
      passes an explicit `--plugin-dir` for each. The first test invoked the binary
      directly, bypassing that function, so dafne was never loaded and its hooks were
      never eligible to fire. Re-run with `--plugin-dir` pointed at `plugins/dafne`, both
      a `SessionStart` and a `UserPromptSubmit` hook declared at the plugin root fired.
      **Lesson for any future spike: a plugin's behaviour can only be tested through a
      launch path that actually loads it.**
      **Consequence for the design:** the hook ships in `plugins/dafne/hooks/hooks.json`,
      travels with the engine, and needs no builder-mode entry — nothing is added to
      master's `.claude/settings.json`. What it requires instead is that the plugin be
      *loaded*, which is the launcher's job (Phase 4).
      **Shape:** two branches, no new concepts — cwd has `DAFNE.md` → inject it; else
      enumerate the garden per the rulings below. The second branch reuses
      `manifest.discover_grove_banks`'s readdir discipline ("which groves exist is a
      directory listing, never configuration").

      → **User ruling, 2026-09-07 — the garden search path, and master stops mounting
      groves.** Two decisions taken together:

      **(a) `master` will never again mount groves as submodules.** The current
      `groves/spanish` … mounts are transitional Phase-2 artifacts, not the end state.
      Groves live in the garden directory; the orchestrator points at it and owns nothing
      inside it. This retires the `groves/` hardcode in
      `system/diotima/bank_union.py:30` and the hand-maintained grove table in
      `CLAUDE.md` — the same class of win as this phase's first bullet killing
      `subscriptions.json`'s paths into grove interiors: orchestrator-side knowledge of
      grove interiors, replaced by a directory listing.

      **(b) An env var names the garden.** `DIOTIMA_GARDEN`, defaulting to
      `~/Documents/diotima-garden`. This is **not** the mechanism D0 rejected. D0's
      dismissal of `DIOTIMA_GARDEN=/a/b/c` is scoped to the *binding* problem — "how does
      the runtime find the grove I opened" — which stays dissolved by grove = cwd.
      *Enumerating* a garden is a different problem, and Phase 4's picker bullet already
      concedes it needs a location; it merely hardcodes `~/diotima-garden` instead of
      making it configurable. The governing distinction: **a registry lists groves; a
      search path lists a directory.** D0 killed the registry — a grove registering
      itself, discovery flowing grove → runtime. A search path plus readdir keeps
      discovery flowing runtime → grove, and no grove knows anything.

      The user's sketch, preserved verbatim as authored:

      ```
      dir = DIOTIMA_GARDEN ?? ~/Documents/diotima-garden
      if dir not exist - create

      available_groves= for f in $(ls dir): str_concat(dir, f)

      define function: is_a_grove(repo): return repo root has DAFNE.md & repo root has 'parents' dir

      if available_groves empty:
          print "no groves avail check out existing at https://github.com/diotima-garden"

          gh or curl deterministic for each repo under https://github.com/diotima-garden
              if is_a_grove(repo) print repo

      else
          print all avail groves
      ```

      **Author's amendments to the sketch, same day — these override it where they
      differ:**

      - **`is_a_grove(repo)` is `DAFNE.md` alone.** The `parents/` condition is dropped:
        a root grove legitimately has none (`social-dynamics` is exactly this), and the
        engine's own `discover_grove_banks` already filters on `DAFNE.md` alone.
        Requiring `parents/` would have hidden every root grove.
      - **Non-empty-garden enumeration is a bounded `find`**, not `ls`:

        ```
        find dir -maxdepth 1 or 2 -type f -name DAFNE.md
        ```

        yielding absolute manifest paths:

        ```
        /home/papa/Documents/diotima-garden/grove_a/DAFNE.md
        /home/papa/Documents/diotima-garden/spanish/DAFNE.md
        ...
        /home/papa/Documents/diotima-garden/another_grove/DAFNE.md
        ```

        Note for the implementer: **the depth bound is load-bearing, not a performance
        tweak.** Depth 1 matches only the garden's own `DAFNE.md`, if it has one; depth 2
        matches each grove's. Vendored parents sit at depth 3 and deeper
        (`spanish/parents/language/DAFNE.md`), so `-maxdepth 2` is exactly what keeps
        inherited parents out of the grove list. An unbounded `find` would present every
        vendored parent as a top-level grove.

      Remaining open points, none blocking:
      - The empty-garden branch reaches the network at session start. Fine as an
        occasional first-run nudge; it should not run on every launch.
      - This sketch is Phase 4's picker built early, in the only place it can live before
        a `diotima` launcher exists. It does not retire this bullet's *other* branch —
        cwd-is-a-grove → inject that grove's `DAFNE.md` — which becomes reachable again
        once the launcher can drop a session directly into a grove directory.

      → **Executed 2026-09-07, with a design reversal from the spike's "Consequence for
      the design" above — the engine-shipped placement it recommended turned out to be
      wrong, discovered empirically while implementing it.**

      **Finding that forced the reversal:** `.claude/settings.json` project config
      (permissions, hooks) loads only when a session's `cwd` is *exactly* that project's
      root — confirmed via `-d hooks --debug-file`, which showed Claude Code checking for
      `{cwd}/.claude/settings.json` with zero ancestor-walking. Launching from
      `groves/spanish` (a subdirectory, submodule or not) never finds master's settings.
      Two consequences, not one:
      1. An engine-shipped hook (`plugins/dafne/hooks/hooks.json`, the spiked design) is
         the only way to get a hook to fire when `cwd` is a grove — a project-owned hook
         structurally cannot, no matter when Phase 4's launcher arrives. This was verified
         both ways: the plugin-shipped hook *did* fire correctly from `groves/spanish`
         before this bullet moved it; a `system/diotima/`-owned hook, tested the same way,
         did not.
      2. **This also means Phase 4's second bullet's literal text — "cwd has `DAFNE.md` →
         launch the runtime there, `grove = project root`" — is not just undemonstrated,
         it's wrong as written.** Making a grove the literal project root would silence
         master's own `.claude/settings.json` for that session: every whitelisted
         anki/dafne bash command, every existing hook, the whole permissions allowlist —
         gone, because groves carry no `.claude/` of their own. See the corrected shape
         below; Phase 4's bullet needs re-reading against it before anyone picks it up.

      **Ruling, same day, in response to the finding:** grove discovery is orchestrator
      policy (which garden, what's in it) — split it back to match the precedent bullets
      1 and 2 already set (dafne stays a pure engine; `system/diotima/` wires it into
      *this* orchestrator's hooks), and solve the cwd-exact-match constraint at the
      launcher instead of the hook. Corrected shape:
      - `bin/diotima` (pulled forward from Phase 4, see its own bullet below) always
        launches with `cwd = master`, regardless of where it was invoked from — this is
        what keeps settings/hooks/permissions loading reliably. It resolves one thing
        before launch: `dir = <invocation cwd> if that cwd carries a DAFNE.md, else the
        garden`. That `dir` is exported to the child `claude` process only, reusing the
        `DIOTIMA_GARDEN` name — deliberate, not an accident: within that one process it
        *is* the single directory the hook needs to look at, and the reuse never touches
        the caller's own shell variable (env vars don't propagate from a child process
        back to its parent shell, the same reason the `cd` itself needs no save/restore).
      - `system/diotima/session-start.py`, wired into master's own `.claude/settings.json`
        (a plain `"SessionStart"` entry, alongside the existing `"SessionEnd"` one) reads
        only `$DIOTIMA_GARDEN` and collapses to one check: does that directory itself
        carry a `DAFNE.md`? Yes → inject its manifest text (the grove case). No → treat it
        as a garden and enumerate `DAFNE.md`-carrying children one level deep (the
        original `is_a_grove`/bounded-`find` shape above, unchanged). Two branches, one
        function, no `cwd`-reading in the hook at all — the launcher already resolved it.
      - **No hardcoded default anywhere.** The `~/Documents/diotima-garden` default lives
        in exactly one place, `system/diotima/config.json`'s `default_garden` key; both
        `bin/diotima` (bash, via a `python3 -c` one-liner) and the hook's own
        direct-invocation fallback read it from there. A missing/broken config file fails
        loudly (no silent duplicate default anywhere to fall back to) rather than masking
        a real misconfiguration.

      **Verified end-to-end** through the actual launch path (the spike's own lesson
      applied to this bullet too — "a plugin's behaviour can only be tested through a
      launch path that actually loads it"), using the same codeword-injection technique:
      a uniquely-named scratch grove (`plovendrix-3347`) was returned by a print-mode
      session with no other source for it when `bin/diotima` was run from elsewhere with
      `$DIOTIMA_GARDEN` pointed at it (garden branch); a second scratch grove
      (`xanthoreum`) was returned, manifest text and all, when `bin/diotima` was run from
      *inside* that directory (grove branch, cwd-exact-match constraint satisfied by the
      launcher's own resolution, not by the hook).

      Two implementation-detail lessons worth keeping for the next hook written here: the
      `SessionStart` output contract is `{"hookSpecificOutput": {"hookEventName":
      "SessionStart", "additionalContext": "<plain string>"}}` — `hookEventName` **is**
      required despite one doc lookup claiming otherwise, and `additionalContext` is a
      plain string for this event, not the array-of-`{type,text}` form some other events
      use. Both were wrong on the first attempt and only caught via `-d hooks
      --debug-file`'s validation error, not from documentation.
- [ ] **Assisted update (D4's second half):** a "tend parents" flow — fetch upstreams of
      everything under `parents/` (recursively), nudge on new commits, show the
      **compiled-output diff**, and on acceptance commit the new pin. Runtime-side, so
      it improves ambiently; no grove is touched by its existence.

**Exit:** `subscriptions.json` contains no path into any grove's interior; a
missing-anki refusal is demonstrable; a session started in the orchestrator lists the
garden's groves from the manifest hook alone, with the hand-maintained grove table gone
from `CLAUDE.md`; a parent update lands via the tend flow end-to-end on one real grove.
*(The manifest-injection bullet is executed and both its branches demonstrated
end-to-end via `bin/diotima`, per the note above. The phase is still not fully exited:
`groves/*` submodules are still mounted in master, `CLAUDE.md`'s grove table and
`system/diotima/bank_union.py:30`'s `groves/` hardcode are not yet retired — that unmount
is explicitly deferred out of this session's scope, see the dependency-graph notes below
— and the assisted-update bullet remains pre-design.)

---

## Phase 3.5 — Manual edit audit (context.md → DAFNE.md sweep)

*Not a scripted execution phase like the others — a checkpoint. Between designing/
executing Phase 3's bullets, edits (the `context.md` → `DAFNE.md` rename among them)
were made by hand across master and several submodules, outside any checklist step.
This quasi-phase closes the loop before Phase 4 starts: confirm the manual work is
complete and consistent, then commit it everywhere. Added 2026-09-07; dirty state at
the time this was written:* `.claude/commands/pipe/add-cards-to-grove.md`,
`.claude/commands/pipe/tackle-feedback-on-grove.md`, `.claude/skills/onboard/SKILL.md`,
`CLAUDE.md`, `README.md`, `modes/world-adoption/shared/cvut/SP1/project.md`, this plan
file, and modified content in submodules `groves/english`, `groves/social-dynamics`,
`groves/spanish`, `plugins/anki-mcp`.

- [x] **Recursive status check:** confirmed the dirty set was exactly as recorded above;
      `groves/instruments`, `plugins/dafne`, `plugins/mneme`, `.claude/utils` were all
      clean — nothing missed the top-level `m` marker.
- [x] **Rename completeness:** repo-wide grep for `context.md` returned only legit
      survivors — mode-level `context.md` (`modes/meta/builder/context.md`,
      `architect/context.md`, `world-adoption/context.md`), mem-bank entry-point files
      (`reading-log/context.md`, `memory/context.md`), a pre-DAFNE debug hook
      (`.claude/hooks/debug/notify-context-read.py`, predates groves entirely — 2026-04-28),
      and historical mentions of the deleted `dafne_simulation/context.md`. No missed
      renames found.
- [x] **Diff review per dirty repo:** all four submodule diffs were read in full.
      `groves/spanish` and `groves/social-dynamics`: each grove's old top-level
      `context.md` body was moved verbatim into `DAFNE.md` (content byte-matched against
      `git show HEAD:context.md`), then the redundant file deleted — a clean
      context.md→DAFNE.md *merge*, not just a rename. `plugins/anki-mcp/README.md`: the
      feedback-pipeline caption was de-named from `context.md` to generic "context
      file" rather than renamed to `DAFNE.md` — confirmed deliberate and correct, since
      the screenshot it captions (`assets/feedback-01-invoke.png`) shows a stale
      pre-Phase-1/2 state (`groves/languages/spanish/context.md`, the old
      `context-compiler` skill) that predates this migration; naming `DAFNE.md` there
      would trade one stale claim for another, and the screenshot's own staleness is a
      separate, out-of-scope issue. `groves/english/english.md`: a real anomaly —
      content unrelated to the rename (the Input Format code block and the Cloze Logic
      MULTI-CLOZE bullet) had been deleted by hand, left as a dangling empty heading.
      Surfaced to the user rather than assumed: confirmed intentional (the rigid
      `Text | Book Title | Chapter/Location` format was tedious for day-to-day pasting)
      and kept as-authored, committed separately (`4767dd8`) from the rename work.
- [x] **Cross-check against this plan's own text:** grepped this file itself — the only
      `context.md` mentions left are historical (`dafne_simulation/context.md`,
      pre-deletion) and this phase's own text; nothing stale.
- [x] **Commit sweep:** four submodules committed and pushed —
      `groves/english` (`4767dd8`, the Input Format/Cloze Logic edit, unrelated to the
      rename), `groves/spanish` (`90902d9`), `groves/social-dynamics` (`441b92e`,
      also fixes a stale `context.md` mention in `improvement-plan.md`), `plugins/anki-mcp`
      (`d905d87`). Master committed with the resulting pointer bumps plus its own direct
      edits.

**Exit:** no dirty submodules and no unexplained untracked files remain anywhere in the
tree; a repo-wide `context.md` grep returns only deliberate non-grove-infra hits; every
touched repo (master + each submodule) has a commit; master's submodule pointers match
what was actually pushed. **Phase 3.5 complete (2026-09-07).**

---

## Phase 4 — Launch UX (north-star stage B + A-as-default)

*From `interaction_north_star.md`: git-model primitive, garden dir as default, C
deferred.*

**Reclassified 2026-09-07 — the launcher is a prerequisite, not sugar.** D0 and
`interaction_north_star.md` both call it optional sugar layered on the git-model
primitive. Two findings from the same day promote it to load-bearing, and both are about
*capability grants a session cannot make for itself*:

- **Plugin loading.** dafne's `SessionStart` hook fires only when dafne is actually
  loaded, and plugins here are loaded by explicit `--plugin-dir` flags at launch — not by
  living in `plugins/`. Nothing inside a session can load a plugin after the fact.
- **Out-of-tree access.** Once groves leave the tree (Phase 3 ruling (a)), grove reads and
  writes are outside the project root. A *committed* project `.claude/settings.json`
  cannot grant that — `additionalDirectories` only lifts it from personal settings
  (`.claude/settings.local.json`, `~/.claude/settings.json`). Requiring every user to
  hand-edit personal settings would sink issue #27's "trivially installable" and the
  `onboard` skill. `--add-dir` at launch grants it with nothing committed and nothing
  per-machine.

Both are launch-time flags. That makes the launcher the single place where a session
acquires its capabilities, and it must therefore exist before Phase 3's hook can be
demonstrated end-to-end.

- [x] **`bin/diotima` — the minimum launcher (approved 2026-09-07; do this first).** A
      committed script in the orchestrator repo that assembles the launch line: one
      `--plugin-dir` per `plugins/*/` carrying `.claude-plugin`, plus `--add-dir` for the
      garden (`$DIOTIMA_GARDEN`, defaulting to `~/Documents/diotima-garden`), then
      `exec`s `claude "$@"`. This formalizes a wrapper that already exists as an
      uncommitted shell function in the workspace's `profile` — the pattern is proven in
      daily use; what changes is that it becomes versioned, shippable, and testable.
      Two requirements on the port:
      - **Derive paths from the script's own location** (`dirname $(realpath "$0")/..`),
        never hardcoded absolute paths. The existing function hardcodes one, which is
        precisely what makes it unshippable and violates the repo's portability rule.
      - **Stay a plain `exec` wrapper over `claude`, composable from outside.** Anyone
        wrapping it for their own environment (credential injection, sandboxing) does so
        by calling `bin/diotima`, which needs no knowledge of that layer and must carry
        none.
      Explicitly *not* in this slice: the picker and the MRU file. Those stay in the
      bullet below.
      → **Executed 2026-09-07.** Grew one requirement beyond the bullet's original text,
      forced by the cwd-exact-match finding recorded under Phase 3's manifest-injection
      bullet: `bin/diotima` *does* now resolve whether the invocation `cwd` is a grove
      (`cwd/DAFNE.md` exists, checked *before* any `cd`, no ancestor-walking — matching
      `is_a_grove`), but **it does not launch the runtime there.** It always launches with
      `cwd = master` regardless, since that's the only `cwd` Claude Code will load
      master's `.claude/settings.json` from. What the cwd-is-a-grove check controls
      instead is which single directory (that grove, or the garden) gets `--add-dir`-ed
      and handed to the session via `$DIOTIMA_GARDEN` for the `SessionStart` hook to read
      — see that bullet for the full mechanism and the reasoning for reusing the
      `DIOTIMA_GARDEN` name. Net effect: this slice already **absorbs the next bullet's
      cwd-detection half** under a corrected mechanism; only the picker and MRU remain
      open below. The garden default (`~/Documents/diotima-garden`) is not hardcoded in
      the script — it lives in `system/diotima/config.json`'s `default_garden` key, read
      by both `bin/diotima` and the hook's own fallback, so there is exactly one place to
      change it. Verified: cwd-independence (`pwd` before and after differ, confirmed via
      a fake `claude` binary substituted on `PATH`), correct `--plugin-dir` enumeration
      (`anki-mcp`, `dafne`; `mneme` correctly excluded, no `.claude-plugin`), and all three
      `dir`-resolution branches (grove cwd; `$DIOTIMA_GARDEN` set; config-default
      fallback, which also exercises "if dir not exist → create").
- [ ] `diotima` launcher on PATH: ~~if cwd (or an ancestor) has `DAFNE.md` → launch the
      runtime there, grove = project root~~ **this phrasing is wrong, corrected 2026-09-07
      — see the cwd-exact-match finding under Phase 3's manifest-injection bullet.**
      Literally making a grove the project root would silence master's own
      `.claude/settings.json` for that session (permissions, hooks — groves carry no
      `.claude/` of their own). `bin/diotima`'s minimum-launcher slice above already
      implements the corrected version of this bullet's cwd-detection half (resolve, but
      never `cd` the runtime into, a grove). What's left here, once picked up again, is
      genuinely just: else → show the picker.
- [ ] Picker sources = union of dumb, disposable data: `readdir($DIOTIMA_GARDEN)`
      filtered on `DAFNE.md` ∪ MRU recents file (`~/.local/state/diotima/recent`,
      appended on every grove open). No daemon, no registry, no grove-side
      registration — this keeps the simple-GUI door open.
- [ ] Grove creation defaults to `$DIOTIMA_GARDEN/<name>` unless a path is given.

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
Phase 0 ──> Phase 1 ──> Phase 2 ──> Phase 3 ──> Phase 3.5 ──> Phase 4
                                        │                       │
                                        └── bullet 3 needs ─────┘
                                            bin/diotima first
```

Phases 0–2 are complete (2026-08-15). No open spike remains blocking any later phase.

**Amended 2026-09-07 — the graph is no longer a straight line.** Phase 3's manifest-
injection bullet depends on Phase 4's `bin/diotima` slice, because the hook only fires
when the plugin is loaded and grove files are only reachable once the garden is added at
launch — both launch-time flags, neither grantable from inside a session. Build
`bin/diotima` first, then bullet 3. The rest of Phase 4 (picker, MRU, grove creation)
keeps its original position after Phase 3.

Phases 1–2 were the irreversible core (published-format discipline); 3–4 are
runtime-side and stay cheap to revise. `grove_inheritance_decisions.md` has been
renamed from `major_architectural_decision_to_be_made.md` — every question in it is
now either ruled or executed.

**Open as of 2026-09-07 (updated same day):** Phase 3's first three bullets (bank
discovery, `requires:` refusal, `SessionStart` manifest injection) are executed; Phase
3.5 (manual edit audit) is committed; `bin/diotima` (Phase 4's first slice) is executed
too, pulled forward and built first as planned. None of this session's `master`-side
changes are pushed yet (`plugins/dafne` had no net changes — the hook it briefly carried
was moved out — so nothing to push there either). What remains, in build order: the
**assisted parent-update flow** (Phase 3, bullet 4 — still pre-design, the only remaining
bullet with no design work done on it), then the rest of Phase 4 (picker, MRU, grove
creation — the picker's cwd-detection half is already done, see that bullet's note).
Phase 5 stays trigger-gated by construction.

Also worth carrying forward: the cwd-exact-match finding (`.claude/settings.json` loads
only when `cwd` is exactly a project's root, no ancestor-walking) is now load-bearing for
any future orchestrator-owned hook or permission, not just this one — check it before
assuming a hook "should just work" from a nested directory.

Also outstanding from the garden rulings, and not yet checkboxed anywhere: unmounting the
`groves/*` submodules from master and retiring the `groves/` hardcode in
`system/diotima/bank_union.py:30` plus the grove table in `CLAUDE.md`. That is the
execution half of Phase 3 ruling (a); sequence it with `bin/diotima`, since nothing can
reach a grove out-of-tree until the launcher grants access.

Two items are carried in prose above rather than as checkboxes, and neither blocks a
phase exit: `groves/managed-models.json` still sits in `groves/` instead of moving to the
anki-mcp side (deferred out of Phase 2), and the `golden/` snapshot is stale against real
grove content — see the note under Phase 3's `requires:` bullet. The golden refresh is
deliberately parked until DAFNE migration finishes and integration tests start, since
that is when the oracle is next load-bearing.
