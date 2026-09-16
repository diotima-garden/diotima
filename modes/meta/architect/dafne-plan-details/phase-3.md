# Phase 3 details — Runtime wiring

*Moved out of `dafne_plan.md` unedited, per the 2026-09-07 plan split — see that
file's Phase 3 for the checklist, bullet definitions, and exit criteria. This file
carries the execution/design narrative for each bullet, in the same order they
appear there.*

## Bullet 1 — Kill the last runtime→grove-interior path

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

## Bullet 2 — `requires:` refusal

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

## Bullet 3 — Manifest injection at session start

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
- `bin/diotima` (pulled forward from Phase 4, see its own bullet in
  `dafne-plan-details/phase-4.md`) always launches with `cwd = master`, regardless
  of where it was invoked from — this is what keeps settings/hooks/permissions
  loading reliably. It resolves one thing before launch: `dir = <invocation cwd> if
  that cwd carries a DAFNE.md, else the garden`. That `dir` is exported to the
  child `claude` process only, reusing the `DIOTIMA_GARDEN` name — deliberate, not
  an accident: within that one process it *is* the single directory the hook needs
  to look at, and the reuse never touches the caller's own shell variable (env vars
  don't propagate from a child process back to its parent shell, the same reason
  the `cd` itself needs no save/restore).
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

## Ruling (a)'s execution half — completed 2026-09-07, builder-mode session

Entered per its own entry contract (`modes/meta/builder/context.md`). Unmounted `groves/spanish`,
`groves/english`, `groves/instruments`, `groves/social-dynamics` from master
(`git submodule deinit` + `git rm` + `.git/modules/groves` cleanup); `.gitmodules` now
carries only `.claude/utils`, `plugins/mneme`, `plugins/dafne`. Before unmounting,
verified no local-only state would be lost (`git submodule foreach 'git status --short'`
clean; `git log @{u}..` empty for all four grove submodules), then populated
`$DIOTIMA_GARDEN` (`~/Documents/diotima-garden`) with `git clone --recursive` of all four
grove repos — each clone's `HEAD` matched master's last-recorded submodule SHA exactly,
confirming zero drift between the mount being retired and the garden replacing it.

Two hardcodes retired as planned: `system/diotima/bank_union.py:30`'s
`Path(project_dir) / "groves"` is gone, and `CLAUDE.md`'s hand-maintained four-row grove
table is replaced by one row pointing at `$DIOTIMA_GARDEN` and `bin/diotima`.

**One design decision surfaced mid-execution, put to the user rather than assumed:**
`bin/diotima` narrows `$DIOTIMA_GARDEN` to a single grove's path (not the garden) when
launched from inside one — a fact this bullet's own manifest-injection design already
relies on for the SessionStart hook's grove-vs-garden branching. `bank_union.py`'s
pre-unmount `grove_banks()` always scanned every mounted grove regardless of session cwd
(since `groves/` was unconditionally fully mounted in master). Making the post-unmount
version read `$DIOTIMA_GARDEN` the same way `session-start.py` does would silently change
that: a session launched from inside one grove would only capture/graduate *that* grove's
bank at session end, not every grove in the garden. Asked the user directly — ruled: scope
to the current grove when cwd is a grove, mirroring the SessionStart hook's own scoping,
on the reasoning that session-end capture and graduation should be about whatever the
session's subject was, not "every grove that happens to exist." Implemented as
`system/diotima/garden.py` — a new shared module (`default_garden()`, `resolve_subject()`,
`is_grove()`) factoring out what was previously duplicated inline in `session-start.py`,
now imported by both `session-start.py` and `bank_union.py`'s `grove_banks()`. Verified
both branches directly (`grove_banks()` called with `$DIOTIMA_GARDEN` pointed at a single
grove vs. at the garden root — correct scoping both times) and end-to-end via `bin/diotima`
print-mode runs from both a garden-default cwd and from inside `diotima-garden/spanish`
(codeword-equivalent: asked the session to report what the hook told it, no other source
for the answer). All 53 `plugins/dafne` tests still pass unchanged.

An advisor pass caught two gaps in that verification: it hadn't touched the real
`SessionEnd` path (`invoke-mneme-on-groves.py`, which is what actually calls
`grove_banks()` in production — my direct calls exercised the same function but not the
hook wiring around it), and hadn't checked whether `own_banks()` (meta, world-adoption)
being unioned in regardless of grove scope could double-capture. Both resolved by reading
`plugins/mneme/mem-bank.log` rather than re-running anything — the two `bin/diotima`
print-mode sessions above had already exercised the real hook and left a record: the
garden-cwd session logged `banks passed in-process (4)` (own 2 + grove-wide 2) and queued
a `social-dynamics` job whose target path is the new garden location
(`/home/papa/Documents/diotima-garden/social-dynamics/memory/small-bank.md`, not the old
`groves/` mount); the spanish-cwd session logged `banks passed in-process (3)` (own 2 +
grove-scoped 1), confirming the scoping ruling took effect through the real hook, not
just in the direct-call test. Neither session's short transcript matched the meta/
world-adoption banks' patterns, so no double-capture occurred — consistent with
`bank_union.py`'s existing "concatenation, not a dedup'd set... degrades harmlessly"
design note, not a new risk this bullet introduced.

Two adjacent cleanups the unmount forced, both flagged as outstanding in this plan's own
prior notes: `groves/managed-models.json` — flagged since Phase 2 as runtime/anki state,
not grove content, and now literally homeless once `groves/` stops existing — moved to
`plugins/anki-mcp/managed-models.json`, with `.mcp.json` and
`plugins/anki-mcp/README.md`'s `--managed-config` references updated to match. A dead
`.claude/settings.json` whitelist entry (`Bash(cp groves/**)`, unreachable once `groves/`
no longer exists in master, and unreferenced by any live skill even before that) was
removed rather than left to rot.

**Amendment, later the same day (2026-09-07), a second builder-mode session:** the
`managed-models.json` placement above was revisited and reversed. The user disagreed with
housing it inside `plugins/anki-mcp` — anki-mcp is a portable, installable plugin (the
DAFNE groves precedent: engines/plugins stay generic, state lives with the consumer, per
`product-vision.md`'s "`.claude/` holds only what is Claude-specific... everything else
migrates out" and the architect non-duplication principle). `managed-models.json` is
orchestrator-owned config (which note types *this* deployment manages), not plugin code —
same shape as `system/mem-bank-subscriptions.json` (flat file, config-only, consumed by a
plugin, orchestrator-owned, no accompanying orchestrator-side code). Moved to
`system/managed-models.json` — no new `system/anki/` directory, since `system/`'s
directory-per-subsystem pattern (`scm-integration/`, `diotima/`) is reserved for
subsystems with scripts, and a one-config-file directory would be structure with zero
instances (the thing Phase 5's table explicitly declines to build ahead of need).
`.mcp.json`'s `--managed-config` arg and `plugins/anki-mcp/README.md`'s path mention were
updated to match; the README's config-shape documentation itself was left untouched — the
path was the only stale part of it.

Doc sweep, same discipline as Phase 3.5's `context.md` audit: grepped the tree for
`groves/` after the unmount and fixed every live reference that would otherwise be a
broken path or stale claim — `README.md` (the monolith→DAFNE section rewritten past
tense, the worked-example link repointed at the real `diotima-garden/spanish` repo),
`.claude/skills/onboard/SKILL.md` (now describes cloning the grove into
`$DIOTIMA_GARDEN` rather than a fixed in-tree path) and
`.claude/skills/youtube-extract/SKILL.md` (its copy-paste command example uses a
placeholder, not literal `$DIOTIMA_GARDEN/spanish` — that string is a slash-command
argument, never shell-expanded, so the literal env-var form would have pasted wrong; an
advisor pass caught this after the first edit), and two not-yet-delivered CVUT outreach docs
(`modes/world-adoption/shared/cvut/SP1/project.md`,
`.../brief-2-learning-analytics.md`) whose relative links into `groves/spanish/...`
would have 404'd — repointed at the `diotima-garden` GitHub org. Left alone, matching
Phase 3.5's own precedent for exactly this kind of hit: historical/decision-record
mentions in `modes/meta/architect/*.md` and `modes/meta/memory/big-bank/*`, dafne's own
test fixtures (`"groves/lang.md"` as an arbitrary example include path, not a real
mount), and `plugins/anki-mcp/README.md`'s stale pre-migration screenshot caption
(already ruled out-of-scope once, in Phase 3.5).

Also same session: `CLAUDE.md`'s navigation-table row for the garden was trimmed. It had
restated the `~/Documents/diotima-garden` default and the `$DIOTIMA_GARDEN` mechanism —
both already living in exactly one place (`system/diotima/config.json`'s `default_garden`,
per this bullet's own "no hardcoded default anywhere" rule above). The row now states only
the concept (grove = knowledge isle, own `DAFNE.md`, not mounted here, opened via
`bin/diotima`) and leaves the mechanism to the `SessionStart` hook, which already lists
groves with full manifest paths — the "readdir, not configuration" discipline applied to
documentation, not just code.

Nothing in this bullet's work is pushed anywhere — `plugins/anki-mcp` has the
`managed-models.json` move uncommitted, master has everything above uncommitted; per
`security.md`, committing and pushing are the user's call, not proactive.
