# Phase 4 details — Launch UX

*Moved out of `dafne_plan.md` unedited, per the 2026-09-07 plan split — see that
file's Phase 4 for the checklist, bullet definitions, and exit criteria. This file
carries the execution narrative for the one bullet that's done.*

## Bullet 1 — `bin/diotima`, the minimum launcher

→ **Executed 2026-09-07.** Grew one requirement beyond the bullet's original text,
forced by the cwd-exact-match finding recorded under Phase 3's manifest-injection
bullet (`dafne-plan-details/phase-3.md`): `bin/diotima` *does* now resolve whether
the invocation `cwd` is a grove (`cwd/DAFNE.md` exists, checked *before* any `cd`, no
ancestor-walking — matching `is_a_grove`), but **it does not launch the runtime there.**
It always launches with `cwd = master` regardless, since that's the only `cwd` Claude
Code will load master's `.claude/settings.json` from. What the cwd-is-a-grove check
controls instead is which single directory (that grove, or the garden) gets
`--add-dir`-ed and handed to the session via `$DIOTIMA_GARDEN` for the `SessionStart`
hook to read — see that bullet for the full mechanism and the reasoning for reusing the
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

## Bullet 5 — grove sync, the consumer propagation flow

→ **Executed 2026-09-18.** Built as designed in `grove_sync.md`: a standalone
`system/diotima/grove_sync.py` with the three separately-callable operations
(`fetch`/`status`/`sync`), scope from `garden.py` alone, `should_sync()` as its own
git-free predicate, and one `DIOTIMA_GARDEN="$dir" python3 … || true` line in
`bin/diotima` before `exec claude`. `garden.py` gained the `groves_in()` helper the
design asked for, and `session-start.py` adopted it in the same change (its inline
re-implementation of the grove test is gone). Tunables (`fetch_max_age_s: 14400`,
`fetch_timeout_s: 5`) live in `config.json`. New suite: `system/diotima/tests/`,
20 tests, all passing; `plugins/dafne`'s 53 still pass.

**Four corrections to the design, each forced by something that failed in execution.**
The design is otherwise unamended — these are the places building it proved it wrong.

- **`git merge --ff-only @{u}`, not `git pull --ff-only`.** The commands table said
  `pull`; the Mechanics section said "the fast-forward is a local ref merge — instant,
  and it still works offline." Those contradict, and the table was the wrong half.
  Verified on a throwaway repo with the remote renamed away: `pull --ff-only` dies with
  `Could not read from remote repository` and leaves the grove behind, while
  `merge --ff-only @{u}` fast-forwards against the last-fetched ref. `pull` also
  re-fetches, defeating the `FETCH_HEAD` throttle the same document specifies.
- **`bin/diotima` never exported `DIOTIMA_GARDEN`.** `$dir` is a plain shell variable;
  the name is set only as a prefix on the `exec claude` line. A bare
  `python3 grove_sync.py` before the exec would have resolved scope from the *caller's*
  environment — working fine on a machine whose shell exports the garden, and syncing
  the whole garden when launched from inside a single grove. Fixed by prefixing the
  call. Verified by deleting every `FETCH_HEAD` and launching from inside `spanish`:
  only `spanish` was fetched.
- **Fetches run concurrently.** Serially, an unreachable network costs
  `len(groves) × fetch_timeout_s` before *every* launch — 20s for four groves, which is
  the "network unplugged → launch proceeds at normal speed" exit criterion failing
  quietly. A thread per grove bounds the walk at roughly one timeout: measured 6.8s → 2.1s
  cold on the real garden, and 5.3s (not 20s) against four blackhole remotes. `fetch()`
  stays the single-grove operation the API promises; `fetch_all()` is only how the CLI
  drives it.
- **`skip_reason()` names the branch before it tests upstream.** The design's own
  example output has `SKIPPED: instruments — on branch try-new-layout, not main`, but a
  feature branch that was never pushed *also* has no upstream, so checking upstream
  first silenced exactly the case the example shows. A resolvable `origin/HEAD` proves a
  remote exists, so that check now leads; silence is reserved for a grove with no remote
  at all, which was the ruling's actual intent.

**Two bugs the tests caught that prose review would not have.** Both are the
self-disabling failure mode `structural-lessons.md` names as this project's default,
and both were invisible without the mandatory submodule regression test:

- `submodules_aligned()` read `git submodule status --recursive` through a helper that
  `.strip()`s stdout — eating the leading space that *is* the aligned marker. Every
  grove with a submodule reported misaligned, forever. It now reads raw stdout.
- The trigger log recorded only the *first* stderr line, and git leads with progress and
  `registered for path` chatter while putting the actual `fatal:` last — so the log
  faithfully recorded a failure while hiding its cause. It now logs the last few lines.
  (This surfaced while debugging the submodule test: the log was the thing that found
  the bug, and was itself the second bug.)

Verified against the exit criteria end-to-end on a purpose-built demo garden — one grove
behind and clean (synced), one with a tracked edit, one on a feature branch, one with
unpushed commits, one with no remote, one already current — producing exactly the
specified output and nothing for the last two. Real-garden runs are read-only in effect:
all four groves are current, clean and aligned.

**Not done, deliberately:** no `.claude/settings.json` entry, per the design's own
reasoning — the sync runs before `exec claude`, outside any session, so the permission
system is not involved and an allow rule would be inert. If the CLI is ever called from
*inside* a session, it stays prompted like any other mutation.

**Three gaps closed after the first working build**, each a case where the design's own
"report the exception, not the success" stance had no branch to report through:

- **A misaligned submodule on a grove that is otherwise current was completely silent.**
  `should_sync` never consults `submodules_aligned`, so `behind == 0` + clean + adrift
  produced no sync and no line. Worse, the *uninitialized* flavor (`-`) does not appear in
  `git status --porcelain` at all — verified — so `dirty` did not catch it either: the
  grove reads as perfectly healthy forever. `skip_reason` now reports it, ahead of the
  `dirty` check, since a submodule at the wrong SHA *does* show as a modified path and
  "uncommitted changes" would send the user hunting for an edit they never made. Reported,
  **not** healed: a grove that is behind gets realigned by `sync()` as part of the
  indivisible unit, and re-running submodule update on a grove with nothing to pull would
  be a second, undesigned operation.
- **`git submodule update` is a network call too.** When a pin moves to a SHA the local
  object store lacks, it clones. `GIT_TERMINAL_PROMPT=0` covers the credential-prompt
  hang, but only a timeout covers a remote that accepts and then stalls — the no-hang
  exit criterion had been tested against `fetch` alone. Bounded by a new
  `submodule_timeout_s` (60s), deliberately far above `fetch_timeout_s` because a real
  first clone legitimately takes longer than a ref check.
- **An unexpected error printed nothing.** The per-grove `except` logged and moved on,
  which on stdout is indistinguishable from "already current" — the one reading that
  would leave a genuine failure unnoticed. It now prints a `SKIPPED: … — error, see
  system/diotima/diotima.log` line.
