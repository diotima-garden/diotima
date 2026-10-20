# Private Layer — a central store, outside every repo

*Created 2026-10-20. Architect-owned design record. Supersedes this file's own first
version (same date): the in-grove `private/` directory with two ignore layers
(`.gitignore` + `.git/info/exclude`) and a deferred `git add -f` socket. That design is
obsolete — replaced below, not reconciled with it. Reason for the reversal: see "Found
during exploration" below; the short version is that a symlinked `memory/` cannot
coexist with git's tracked-file semantics, which rules out making the private directory
a relocatable mount point inside the grove at all.*

---

## The asymmetry this feature exists to hold

Groves are built to be published, forked and re-aimed — `product-vision.md`'s
"anything added to a grove must survive being forked and inherited." Practising a grove
produces the exact opposite kind of material. The motivating instance:
`social-dynamics/private/cueues.md`, 13 KB of cue set keyed to one practitioner's own
life — `G. Family`, a section headed `Patterns to watch (not cues — awareness and
therapy material)`. That is not a method anyone can re-aim; it is one person's life keyed
to a method. More groves will grow this.

Two requirements pull against each other, and the design is whatever holds both:

- It must **never** reach a grove's published repo.
- It must be **reliably findable** by a session working in that grove. A private layer a
  session cannot locate is dead weight, and the practitioner pastes the content into the
  prompt instead — strictly worse, because it then lands in session transcripts and from
  there in a mem-bank.

The second requirement is the one a naive "just gitignore it" answer drops.

## Found during exploration, and it shapes everything below

- `cueues.md` was untracked **and** matched by no ignore rule, in a repo with a public
  remote. Closed mid-session with two local files (reverted by this design — see
  Migration below).
- `manifest.py:125` resolves `bank:` via `(node_root / bank).resolve()` with **no
  containment check** anywhere in mneme/dafne/diotima. Banks can already point outside a
  grove natively — no symlink is needed to relocate one.
- `registry.py:20` builds the *default* trigger pattern from the **resolved** path, while
  patterns match paths **as typed in transcripts** (`crawler.py:41-62`). Relocate a bank
  without explicit `patterns:` and capture **silently never fires**.
- A symlinked `memory/` cannot work: its three tracked files are mode `100644`, a symlink
  is mode `120000` *at the path* `memory`, so git records `context.md`,
  `this-bank-prompt.md` and `big-bank/.gitkeep` as **deleted**. The grove's bank prompt —
  publishable method a fork needs — would stop being versioned with the grove. This is
  what rules out symlinking anything, and with it the entire in-grove `private/`
  approach this file originally proposed.

**Outcome:** private material lives in one central directory outside every git repo. No
symlinks, no gitignore machinery, no change to how banks work.

## The design

**Storage.** A new `private_root` key in `system/diotima/config.json`, default
`~/Documents/diotima-private` — sibling of `~/Documents/diotima-garden`. Layout
`<private_root>/<node-name>/`. One directory for the user to version, sync or back up as
they choose; this design mandates nothing about that.

Because nothing private is ever inside a git repo, the entire ignore problem this file's
first version solved disappears with it — no two-layer `.gitignore` + `info/exclude`, no
one-time `git add -f` socket, no permanently non-portable exclude line.

**Why a new `config.json` key, and not `$DIOTIMA_GARDEN/private`.** This reverses this
file's own exit criterion 6 ("no new `config.json` key"), and the reason is worth stating
plainly rather than silently dropping it: `$DIOTIMA_GARDEN` is deliberately overloaded
(`orientation_scope.md` §6) — it names the garden root in one launch mode and the
resolved subject in the other, so `$DIOTIMA_GARDEN/private` is two different directories
depending on how the session was launched:

| Launch | `$DIOTIMA_GARDEN/private` resolves to |
|---|---|
| `diotima` from the garden | `diotima-garden/private/` |
| `diotima` from inside the grove | `diotima-garden/social-dynamics/private/` |

— which is not a location, it is a coin flip. A dedicated key is one fixed path in both
modes, at the cost of one new config field — a trade worth making given the alternative
is silently wrong half the time.

**Scope: subject nodes only, no parent recursion.** A parent is published method, shared
across consumers (`parents/behavior-rewiring` is a submodule with its own remote). Note
the asymmetry deliberately: `orientation_for()` gathers banks parent-inclusive via
`discover_banks()`; private stays subject-only. Keyed by directory name, unique among a
garden's top-level nodes (node names are *not* unique down the `parents/` chain — another
reason not to recurse). A `private/`-shaped directory appearing under a parent node is
not a configuration this design supports — it is a finding, and the right response is to
move the content up to the consumer node.

**Discovery is the runtime's job, not the manifest's.** Groves carry no path to the
private store — no new `DAFNE.md` field, no filename. No runtime path enters a manifest,
so sovereignty holds, and the design survives forking automatically: a fork is a `git
clone` of the grove repo alone, and the private store was never inside it to begin with.
(This is also why the authoring contract below lives in the orientation line rather than
in a manifest row — the home this file's first version gave it. With the store outside
every repo, a fork has no private layer for a manifest contract to describe; the
contract has to travel with the thing that actually reaches every session, which is the
orientation package.)

**Orientation reports presence, never content — and never filenames.** `CONTEXT_BUDGET_BYTES`
is 10,000; the live `cueues.md` file alone is 13,128 bytes. Injecting it would re-create
the silent-truncation defect that constant exists to prevent. A filename is disclosure
too — `therapy-notes-G.md` leaks on its own — so the line reports a path and a count,
nothing enumerated inside it.

**The line fires on absence too, worded differently.** Silence-on-absence is this
project's own named failure mode (`CONTEXT_BUDGET_BYTES`'s comment, `_trim_notice`'s
entire reason for existing): a session told nothing can't distinguish "no private layer
exists here" from "the runtime forgot to check." So the presence line is unconditional —
`none yet (would live at <path>)` when the directory doesn't exist, a count otherwise.

**Banks are untouched.** `memory/` stays where it is: `context.md` and
`this-bank-prompt.md` tracked (publishable method), `small-bank.md` gitignored,
`graduate: false` already set on both bank-carrying groves. No mneme change in this
design — per the user, `big-bank.py` gets its own privacy patch later (see Deferred).

## Execution

**Step 1 — this file and `dafne_plan.md`.** Durable record first, so a `/clear`
mid-build still resumes from a file, not a lost plan-mode transcript. This file now
carries both the design and the execution steps; `dafne_plan.md` Phase 3 carries one
bullet pointing here.

**Step 2 — code.**

| File | Change |
|---|---|
| `system/diotima/config.json` | add `private_root`, default `~/Documents/diotima-private` |
| `system/diotima/garden.py` | add `private_root()` and `private_dir_for(node)` beside the existing `default_garden()` / `resolve_subject()` — the one place config paths are read |
| `system/diotima/orient.py` | `GroveOrientation` gains a `private` field (path, exists, entry count); `orientation_for()` populates it via `garden.private_dir_for()`; `format_orientation()` renders one unconditional line — path, count, and the authoring contract — and its byte cost is folded into `_bank_budget()`'s overhead accounting, same as the manifest and git-status text |
| `system/diotima/tests/conftest.py` | autouse fixture pointing `garden.private_root()` at a per-test `tmp_path`, same precedent as the existing `isolate_log` fixture — without it every existing `test_orient.py` case starts statting the real `~/Documents/diotima-private` |
| `system/diotima/tests/test_orient.py` | cases: no private dir, empty, populated with a distinctive filename and content — assert neither the filename nor the content appears in formatted output, only the count |

**Reuse, don't re-derive:** `garden.py:resolve_subject()` + `groves_in()` already answer
scope correctly in both launch modes — no new env var, no new scope logic.
`format_orientation()` stays the single shared formatter. This is also the first time
`orient.py` imports `garden.py` — a deliberate, noted exception to its docstring's "does
not call `resolve_subject()` itself": `private_dir_for(grove)` is a config lookup keyed
by a name the caller already resolved, not a second scope resolution.

**Known interaction:** a private-presence line in `format_orientation()` changes
`orient.py --grove X` output, against `orientation_scope.md` exit criterion 5. Legitimate:
that criterion keeps *scope claims* (session facts) out of the CLI. Private presence is a
*grove* fact, true regardless of launch mode, so the shared formatter is correct to carry
it in both callers.

**Step 3 — migrate the live instance. Last, after the code lands**, so the 13 KB cue file
is never homeless mid-build:

1. `mkdir -p ~/Documents/diotima-private/social-dynamics`.
2. Copy `social-dynamics/private/cueues.md` to the new location; verify the byte count
   matches (13,128) before touching the source.
3. Delete the source file, then `social-dynamics/private/.gitignore`, then `rmdir` the
   now-empty `private/` directory — an empty directory is invisible to `git status`, so
   leaving it behind would not actually restore the pre-session state.
4. Remove the `/private/` line from `social-dynamics/.git/info/exclude` — added earlier
   this session, unnecessary once nothing private sits in the repo.
5. Confirm `git status --untracked-files=all` in the grove is back to its pre-session
   state (only the pre-existing `drills/dating-frame/calibration.md` modification).

Nothing is committed in either repo without the user asking.

## Deferred, recorded with un-defer triggers

- **Graduation privacy (`big-bank.py`).** `big-bank.py:255` is `bank.get("graduate",
  True)` — an unsafe default; both existing groves close it by per-grove convention a new
  grove author has no reason to know. Explicitly **out of scope** per the user: mneme
  gets its own privacy patch. Nothing regresses meanwhile, since `social-dynamics` and
  `spanish` both already declare `graduate: false`. **Un-defer trigger:** that patch, or
  a third grove declaring a bank.
- **The bank interface rework.** The user's proposal: `bank: private | public` in the
  `DAFNE.md` header, still accepting a path, deciding whether the bank resolves to
  `./memory` or `<private_root>/<grove>/memory`. Plus their observation that
  `context.md` is essentially vestigial — it functions only as a session-crawler grep
  cue. Out of scope now ("not for now"). **Un-defer trigger:** the next grove that wants
  its bank content private, or any change to the crawler's trigger mechanism.
- **Person-level private layer.** `G. Family` and the therapy-adjacent `Patterns to
  watch` section are not domain material; they will duplicate when a second grove grows
  a private layer. The central store makes this cheap later (a sibling `_person/`
  directory). **Un-defer trigger:** the second grove whose private material is
  person-level.
- **Pre-commit path guard.** Clobbers an existing `pre-commit`, silently inert under
  `core.hooksPath`. Moot now that nothing private sits in a repo. **Un-defer trigger:**
  a private file reappearing inside a grove.
- **Content-derivation check** (did a tracked file absorb private material) — the
  judgment half of the authoring contract. **Un-defer trigger:** first observed
  instance.

## Rejected

**In-grove `private/` with a symlinked or relocated `memory/`.** This file's own first
version. Killed by the git mode-bit finding above: a symlink at `memory` makes git
record the grove's publishable bank-prompt files as deleted. No variant of
symlink-the-mount survives that.

**Inject private content into the orientation package.** It is routinely larger than the
entire context budget, and it is the lazy-load case by construction.

**A `PreToolUse` gate on reading the private store.** Reading is the legitimate use; the
gate would block the feature rather than the leak. Same reasoning `orientation_scope.md`
used for its own text-not-gate call: the invariant is not absolute, so it fails the
mechanical-trigger half of the decision test.

## Verification

1. **Resolution is launch-mode-independent:** `private_dir_for()` returns the same path
   whether `$DIOTIMA_GARDEN` names the garden or the single grove. This is the defect
   that killed the `$DIOTIMA_GARDEN/private` option, so it is the test that matters most.
2. **Orientation, both callers:** `python3 system/diotima/orient.py --grove
   <garden>/social-dynamics` — one line naming the private dir and its entry count, and
   **no cue content, no filename**. Then a print-mode `bin/diotima` run from inside the
   grove, asking the session to report what it was told about the private layer, with no
   other source for the answer (the technique `orientation_scope.md` and Phase 3 both
   used).
3. **Budget:** the injected package stays under `CONTEXT_BUDGET_BYTES` — the presence
   line is a path and a count, so unchanged within noise, and is itself counted in
   `_bank_budget()`'s overhead.
4. **Capture still fires — skipped, moot by construction.** This design relocates no
   bank; `registry.py:20`'s pattern hazard is a risk for the bank-interface rework
   (Deferred, above), not for anything built here. Recorded as not-run rather than left
   looking silently passed.
5. **Regression — passes, with one pre-existing caveat found, not caused, by this
   work.** From `system/diotima/tests/`:
   `PYTHONPATH=. ../../plugins/dafne/.venv/bin/pytest test_grove_sync.py test_orient.py`
   — 31 passed (28 pre-existing + 3 new private-layer cases). The literal exit-criterion
   wording, `python3 -m pytest system/diotima/tests`, does not currently work in this
   environment on either branch: plain `python3` has no `pytest` installed, and the
   dafne-venv's pytest 9.1.1 fails to *collect* `test_grove_sync.py` (`from conftest
   import ...` → `ModuleNotFoundError`) under its current import-mode defaults.
   Confirmed via `git stash` that this collection failure predates every change in this
   session — an environment/pytest-version drift, not a regression introduced here, and
   out of scope for this plan to fix. The `PYTHONPATH=.` invocation above is the
   workaround that actually exercises both test modules until that's addressed.
6. **Hook-path budget, the path with an actual ceiling:** the CLI (`orient.py --grove
   X`) passes no `budget`, so measuring it says nothing about `CONTEXT_BUDGET_BYTES`.
   Measured instead through `session-start.py`'s `context_for()` — the one caller that
   passes `budget=CONTEXT_BUDGET_BYTES` — against the live, post-migration
   `social-dynamics` grove: 9,248 bytes vs. the 10,000-byte ceiling. This is also the
   only run that exercises `_bank_budget()`'s new `extra=` term against a grove with
   populated banks.
7. **Migration left no trace:** `git status --untracked-files=all` in `social-dynamics`
   matches its pre-session state; `~/Documents/diotima-private/social-dynamics/cueues.md`
   exists and is byte-identical (13,128 bytes) to what `social-dynamics/private/cueues.md`
   held before the move. One note carried forward rather than fixed: the source file was
   untracked, so no git history anywhere holds a copy independent of this one file —
   the design deliberately mandates nothing about versioning the private store, so this
   is a handoff note for the user, not a defect.
