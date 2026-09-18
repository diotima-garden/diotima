# DAFNE Execution Plan

*Created 2026-07-19. All decisions feeding this plan are closed — see
`grove_inheritance_decisions.md` (D0–D4 + 2026-07-18/19 rulings) and
`interaction_north_star.md`. This file is pure execution: phases in dependency order,
each with concrete steps and an exit criterion. Check off as you go.*

*Split 2026-09-07: this file stays the big-picture view — checklists, task
definitions, exit criteria, current status. Per-phase execution narrative (the
"→ Designed/Executed" write-ups and long ruling records) lives in
`dafne-plan-details/`, one file per phase that has one. Each moved block is replaced
below by a one-line summary plus a pointer.*

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

**Exit — Phase 2 complete (2026-08-15).** Every grove clones standalone and compiles
byte-identical to golden with zero edits; context-compiler is gone. Six repos pushed and
mounted, not three (an unplanned `social-dynamics` grove was extracted too). Full
narrative, deviations, and verification detail: `dafne-plan-details/phase-2.md`.

---

## Phase 3 — Runtime wiring

*The runtime discovers what groves declare — the D1(b) contract goes live. Full
execution narrative for every bullet below lives in `dafne-plan-details/phase-3.md`,
in the same order as these bullets.*

- [x] **Kill the last runtime→grove-interior path:** move each bank's declaration
      (`name`, `patterns`, `graduate`, `recurse-mem-enable: false` default) from
      `.claude/mem-bank/subscriptions.json` into the owning grove's `DAFNE.md` bank
      config. mem-bank machinery enumerates mounted groves and reads their manifests;
      `subscriptions.json` retains only runtime-side preferences, or dies.
      → Designed in `bank_discovery_wiring.md`, executed and verified 2026-08-29.
- [x] **`requires:` refusal:** opening a grove whose effective (unioned) requires
      includes `anki` in a runtime without anki-mcp produces a plain, early message —
      not a deep pipeline failure. A grove requiring nothing is first-class.
      → Designed in `requires_refusal.md`, executed and verified 2026-08-29.
- [x] **Manifest injection at session start:** a `SessionStart` hook shipped by
      `plugins/dafne` (`hooks/hooks.json`) injects orientation as `additionalContext`.
      Two branches: cwd is a grove → inject its `DAFNE.md`; otherwise → inject the
      garden's grove list.
      → Spiked and executed 2026-09-07, with one design reversal along the way (the
      hook ended up staying engine-shipped, but cwd resolution moved to the launcher —
      see the detail file). Includes the same-day user ruling on the garden search
      path (`DIOTIMA_GARDEN`, bounded `find`, no registry) and, appended the same day,
      ruling (a)'s execution — unmounting `groves/*` from master and populating the
      garden — plus a later same-day amendment reversing the `managed-models.json`
      placement it had landed on. Full account: `dafne-plan-details/phase-3.md`.
- [ ] **Assisted update (D4's second half):** a "tend parents" flow — fetch upstreams of
      everything under `parents/` (recursively), nudge on new commits, show the
      **compiled-output diff**, and on acceptance commit the new pin. Runtime-side, so
      it improves ambiently; no grove is touched by its existence.
      → Designed in `assisted_parent_update.md`, then **deferred the same day
      (2026-09-16, user ruling) — do not build.** The design session surfaced that D4
      was written from the grove *author's* seat and hid a split: the **author** flow
      (re-pin a parent, compiled diff, commit — this bullet) has **zero** real
      instances, because no cross-owner parent/child pair exists; re-pinning your own
      parents is two git commands in a session. The **consumer** flow (a cloned grove
      fast-forwards to its author's published state) is the one every adopter needs, and
      it needs none of this bullet's machinery — it moves to Phase 4 as its own item.
      This bullet stays **open, unchecked**: D4's second half is genuinely not done, and
      checking it off with the consumer flow would make the plan lie about that.
      **Un-defer trigger:** the first parent you do not own publishing an improvement you
      want.
- [x] **Session orientation completeness — bank content + grove git state; mid-session
      grove-switch parity.** Bullet 3's manifest injection stops at the raw `DAFNE.md`
      text: a grove's own populated mem-bank content and its own repo's git state never
      reach the session automatically, and opening a grove from a multi-grove/garden
      session has no equivalent to the single-grove hook path at all — both are
      prose-navigation gaps, not gaps in what dafne/mneme already resolve. Does not
      reopen bullet 3, which is checked off and executed exactly as scoped.
      → Designed in `grove_orientation.md`. Resolves `diotima-garden/diotima#25`
      (semantic-vs-mechanical small-bank read), which was already filed against this
      exact question and named the same two blockers this design addresses:
      `diotima-garden/diotima#24` (per-bank `context.md` is a hand-copied, drifting
      duplicate — stopgapped here with one added sentence per copy, pending #24's
      centralization) and `diotima-garden/mneme#8` (the trigger layer is
      regex-over-raw-text, which is the verified reason both production grove banks
      have never captured anything — not fixed here, but no longer mistaken for a
      per-grove pattern-tuning problem).
      → **Built 2026-09-18** (`orient.py`, wired into `session-start.py`, CLI
      whitelisted; 6 new tests in `system/diotima/tests/test_orient.py`, all passing
      alongside the existing 21 — one test loads `session-start.py`'s `context_for()`
      by file path and asserts it byte-matches `orient.py`'s CLI stdout, so the
      parity claim is machine-checked, not eyeballed). Also verified by direct
      invocation against the live social-dynamics grove, and against the CLI run
      under plain `python3` (the interpreter it's whitelisted under) with a seeded
      populated bank in a throwaway grove, confirming bank discovery actually works
      under that interpreter and not just when accidentally run under the dafne venv.
      **Live-verified 2026-09-18** in two real `bin/diotima`-launched sessions (not
      this one): a garden-mode session (launched from `~`) ran the `orient.py` CLI
      against social-dynamics and got manifest + "none captured yet" + this grove's
      own dirty-tree status; a single-grove session (launched from inside
      social-dynamics) had that exact block injected by its `SessionStart` hook, and
      its "let's continue our work" reply talked only about the grove's own state
      (branch, uncommitted changes, empty bank, dating-frame drill) — the original
      motivating bug from `grove_orientation.md`'s opening paragraph does not
      reproduce. Both sessions wrote their findings to `/tmp/diotima-verify-garden.txt`
      / `/tmp/diotima-verify-grove.txt`; the two sessions' self-reported verdicts were
      independently confirmed here with a literal `diff` of the two blocks (exit 0,
      byte-identical), not just eyeballed. Checking this bullet off. One scope note: the
      `context.md` stopgap sentence reaches 3 of 4 copies (meta, world-adoption,
      social-dynamics already had it going into this session) — spanish's
      `reading-log/context.md` is a separate repo not reachable from this session's
      grove boundary, left as a follow-up.
      **Portability risk found, not in the original design:** `discover_banks()`
      needs `plugins/dafne/.venv`'s `pyyaml`, but `session-start.py` (like
      `grove_sync.py`) must keep running under plain `python3` for fresh-clone
      compatibility per `python-venvs.md`. `orient.py` degrades to "no banks
      discovered" (identical to the already-designed empty-bank case) when that
      import fails, rather than crashing the hook — untested on a machine that
      actually lacks system `yaml`, since this dev machine happens to have it.
      **Second finding, raised by the user reviewing this build:** hook-injected
      bank content leaves no transcript trace the mem-bank capture trigger can match
      (`crawler.py`'s pattern scan never sees `SessionStart`'s `additionalContext`) —
      doesn't regress real grove usage (that path was already dead, per the bullet's
      own `mneme#8` reference above) but does remove the one accidental path an
      investigative session had. See `grove_orientation.md`'s "consequence found
      during the build" section and its "Doors held open" table.

**Exit:** `subscriptions.json` contains no path into any grove's interior; a
missing-anki refusal is demonstrable; a session started in the orchestrator lists the
garden's groves from the manifest hook alone, with the hand-maintained grove table gone
from `CLAUDE.md`; a parent update lands via the tend flow end-to-end on one real grove.
*(The manifest-injection bullet is executed and both its branches demonstrated
end-to-end via `bin/diotima`, per `dafne-plan-details/phase-3.md`. The phase is still
not fully exited: only the assisted-update bullet remains — pre-design, the one Phase 3
bullet with no design work done on it.)*

---

## Phase 3.5 — Manual edit audit (context.md → DAFNE.md sweep)

*Not a scripted execution phase like the others — a checkpoint. Between designing/
executing Phase 3's bullets, edits (the `context.md` → `DAFNE.md` rename among them)
were made by hand across master and several submodules, outside any checklist step.
This quasi-phase closes the loop before Phase 4 starts: confirm the manual work is
complete and consistent, then commit it everywhere. Full account per item:
`dafne-plan-details/phase-3.5.md`.*

- [x] Recursive status check — dirty set confirmed exactly as expected.
- [x] Rename completeness — repo-wide `context.md` grep returned only legitimate
      survivors.
- [x] Diff review per dirty repo — all four submodule diffs read in full; one real
      anomaly found and confirmed intentional with the user.
- [x] Cross-check against this plan's own text — no stale mentions found.
- [x] Commit sweep — four submodules committed and pushed; master committed with the
      resulting pointer bumps.

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
      → Executed 2026-09-07; grew one requirement beyond the original text (cwd
      resolution moved here from the hook — see `dafne-plan-details/phase-4.md`).
- [ ] `diotima` launcher on PATH: ~~if cwd (or an ancestor) has `DAFNE.md` → launch the
      runtime there, grove = project root~~ **this phrasing is wrong, corrected 2026-09-07
      — see the cwd-exact-match finding under Phase 3's manifest-injection bullet
      (`dafne-plan-details/phase-3.md`).**
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
- [x] **Grove sync — the consumer propagation flow (added 2026-09-16, reshaped by user
      ruling 2026-09-18; executed 2026-09-18).** The flow every adopter needs, and the one Phase 3 bullet 4
      was mistakenly carrying: a cloned grove fast-forwards to what its author published.
      *"Most users will only ever need a recursive git pull; they will never change a
      grove."* **Ruling: pull automatically at launch when the grove is on its default
      branch with no tracked file edited** — exactly the conditions under which a
      fast-forward cannot conflict, lose work, or create a merge commit, so there is
      nothing to ask about. This replaces an earlier report-and-let-the-model-pull
      sketch, which had a real defect: injected "spanish is 3 commits behind" text reads
      to an LLM as a task and gets acted on unprompted.
      → Designed in `grove_sync.md`. The load-bearing decisions: a standalone
      `system/diotima/grove_sync.py` (orchestrator, not dafne) exposing **three
      separately callable operations** — `fetch` (network, launcher-only), `status`
      (local reads, hook-safe), `sync` (mutation) — which is what lets the
      launcher-vs-hook question be deferred rather than frozen, since it resolves
      differently per operation; scope comes from `garden.py`'s existing
      `resolve_subject()`/`is_grove()`, making this its **third** consumer with no env
      var or config of its own; and `pull --ff-only` + `submodule update --init
      --recursive` is **one indivisible unit** (pulling alone leaves a bumped parent pin
      looking like a dirty tree, which trips this flow's own precondition and silently
      disables it forever).

      **Why this needs no write-permission machinery.** Every generated artifact is
      already gitignored inside the groves (`*.compiled.md`, `*.preprocessed.md`,
      `*.md.feedback.jsonl`, `small-bank.md`, `*.apkg` — verified in
      `diotima-garden/spanish/.gitignore`), so a regular user's session dirties nothing
      *tracked*. Staleness after a pull is already handled: pull stamps source mtimes to
      now, and `compiled-is-fresh.py` reports STALE on exactly that. **Git's
      tracked/untracked line is therefore the consumer/author boundary, drawn for free**
      — you become an author by making a tracked change, and git tells you by refusing
      the fast-forward. No `$DIOTIMA_GARDEN` write ban (it would break state-in-grove, a
      Phase 2 ruling — mem-bank, backups and feedback logs live in the grove by design),
      and no persona flag to declare up front.
      → **Executed 2026-09-18.** `system/diotima/grove_sync.py` as designed (three
      separately-callable operations, scope from `garden.py` alone, `should_sync()` as a
      git-free predicate), `groves_in()` added to `garden.py` and adopted by
      `session-start.py`, tunables in `config.json`, one throttled call from
      `bin/diotima` before `exec claude`, and a new `system/diotima/tests/` — 20 tests
      including the mandatory submodule-pin regression. Four design corrections were
      forced during the build (the commands table's `git pull --ff-only` had to become
      `git merge --ff-only @{u}`; `bin/diotima` never actually exported
      `DIOTIMA_GARDEN`; fetches had to go concurrent to hold the no-hang criterion;
      `skip_reason` had to test the branch before the upstream) — each is amended into
      `grove_sync.md` and narrated in `dafne-plan-details/phase-4.md`.

**Exit:** clone `spanish` to an arbitrary directory → `diotima` → the session plays it;
it appears in the picker afterward; a fresh install with an empty garden leads with
"plant your first grove"; and a clone left untouched while its author publishes catches
up on the next launch with no prompt, submodules aligned (`grove_sync.md`'s criteria).

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

**Open as of 2026-09-07 (updated same day, three times):** Phase 3's first three bullets
(bank discovery, `requires:` refusal, `SessionStart` manifest injection) are executed;
Phase 3.5 (manual edit audit) is committed; `bin/diotima` (Phase 4's first slice) is
executed too, pulled forward and built first as planned. Ruling (a)'s execution half —
unmounting `groves/*` from master, retiring the `groves/` hardcodes in `bank_union.py`
and `CLAUDE.md`, populating `$DIOTIMA_GARDEN` with all four grove repos — is also now
executed and verified end-to-end via `bin/diotima`, in a second builder-mode session the
same day; see `dafne-plan-details/phase-3.md` for the full account, including one
mid-execution decision (per-grove vs. whole-garden bank scoping) put to the user rather
than assumed, and a later same-day amendment reversing the `managed-models.json`
placement that session had landed on (it moved again, to `system/managed-models.json` —
see that file's amendment note for the reasoning). None of this session's `master`-side
changes are pushed yet [pushed as of `9bdd0b4`, 2026-09-16]. What remains, in build
order: **grove sync** (Phase 4 — the flow every adopter needs, and the cheapest
remaining item: `system/diotima/grove_sync.py` plus a throttled call to it from
`bin/diotima`; designed in `grove_sync.md`), then the rest of Phase 4 (picker, MRU, grove creation — the picker's cwd-detection half is already done,
see that bullet's note). **Phase 3's bullet 4 is designed but deliberately not being
built** (`assisted_parent_update.md`, deferred 2026-09-16 with a stated un-defer
trigger) — it is the *author* half of propagation, and it has zero real instances until
a parent someone else owns publishes something you want. Phase 5 stays trigger-gated by
construction.

**The 2026-09-16 scope ruling, stated once so it isn't re-litigated:** propagation has
two flows, not one. D4 designed the author's (re-pin, diff, commit); every actual
adopter needs the consumer's (fast-forward to what the author published). They share a
motivation and almost no machinery. Build the consumer's; keep the author's on the
shelf, fully designed, until it has an instance.

Also worth carrying forward: the cwd-exact-match finding (`.claude/settings.json` loads
only when `cwd` is exactly a project's root, no ancestor-walking) is now load-bearing for
any future orchestrator-owned hook or permission, not just this one — check it before
assuming a hook "should just work" from a nested directory (full finding:
`dafne-plan-details/phase-3.md`). Likewise the `$DIOTIMA_GARDEN`-narrows-to-a-single-grove
behavior of `bin/diotima` — any future script under `system/diotima/` that needs "the
whole garden" regardless of session subject should resolve via `system/diotima/garden.py`,
not assume `$DIOTIMA_GARDEN` always names the garden root.

One item remains carried in prose rather than as a checkbox, and doesn't block a phase
exit: the `golden/` snapshot is stale against real grove content — see
`dafne-plan-details/phase-3.md`'s bullet-2 section. The golden refresh is deliberately
parked until DAFNE migration finishes and integration tests start, since that is when the
oracle is next load-bearing.
