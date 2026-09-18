# Grove Sync — the consumer propagation flow

*Created 2026-09-18. Architect-owned design record for `dafne_plan.md` Phase 4's
consumer-sync item. Companion to `assisted_parent_update.md`, which designs the
**author** half of propagation and is deliberately shelved; this is the half that
ships. Deliberately small — the value here is the seam, not the machinery.*

---

## What this is

A grove you cloned falls behind the version its author published. This flow catches it
up, automatically, whenever doing so is provably safe.

**User ruling, 2026-09-18:** *pull automatically at launch when the grove is on its
default branch and no tracked file has been edited.* Those two conditions are exactly
the conditions under which a fast-forward cannot conflict, cannot lose work, and cannot
create a merge commit — so when they hold there is nothing to ask about, and asking is
just friction in front of the answer.

This supersedes an earlier sketch in which the runtime *reported* drift into session
context and left the pulling to the model. That design had a defect this one doesn't:
injected text saying "spanish is 3 commits behind" reads to an LLM as a task, and would
get acted on before the user said anything. **A deterministic pull performed by code is
safer than a nudge interpreted by a model** — the safe version is the one with less AI
in the loop.

### Why this does not reopen D4

It looks like the auto-propagation D4 rejected, and is not. D4 refused *version ranges*
because a parent's improvements would flow into a child without the **child author's**
consent — `spanish` silently recomposing against a newer `language`, so `spanish`'s own
published output changes under its author. That is the grove-as-record breakage.

Grove sync moves a **local working copy** to the exact commit its author already made
and published, **that author's pin choices included**. Nothing recomposes; nothing is
resolved; no version is chosen by a machine. This is following a repository, which is
what git is for. D4 stays intact and this flow needs no exception from it.

---

## The ruling that shapes the module: three operations, separately callable

The open question is whether this belongs to `bin/diotima` (the launcher) or to
`session-start.py` (the hook). **That question does not have to be answered now, and
separating the operations is what makes deferring it free** — because it resolves
*differently for each operation*:

| Operation | Touches | Safe in a hook? | Safe in the launcher? |
|---|---|---|---|
| **`fetch`** | network | **No** — blocks the first prompt; `session-start.py` already commits in writing to being network-free (`system/diotima/session-start.py:32-34`), and its swallow-all-errors posture turns an offline machine into a *hang*, not an error | Yes — a visible, interruptible, hard-timeout second before `exec` |
| **`status`** | local refs only | Yes — instant, offline, no writes | Yes |
| **`sync`** | working tree | policy call, not a mechanics call | Yes |

A monolithic `update_groves()` would force one answer for all three and freeze it.
Three functions in one module let the caller be decided — and *changed* — later, which
is the whole point of putting this in its own file rather than inlining it into
whichever component happens to call it first.

**Corollary worth stating:** `status` being hook-safe means the hook can always report
state without any of this becoming a network dependency. Whatever we decide about where
`fetch` and `sync` run, the reporting half has no constraints.

---

## Layer placement

**`system/diotima/grove_sync.py`** — orchestrator, not engine.

Not `plugins/dafne/`, for the reason `session-start.py` already records for itself:
grove discovery about *this runtime's garden* is this runtime's concern. dafne is a pure
engine over manifests and structure; the git state of working copies on this machine is
not engine work, and dafne must not read `$DIOTIMA_GARDEN` (orchestrator→engine is the
only permitted direction, `layers.md`). This is the same split
`bank_discovery_wiring.md` and `requires_refusal.md` both landed on.

---

## Scope: reuse `garden.py`, do not re-derive

The "is this session about one grove or the whole garden" question is **already
answered and already separated** — `system/diotima/garden.py`. `bin/diotima` narrows
`$DIOTIMA_GARDEN` to a single grove when launched from inside one, else it names the
garden; `resolve_subject()` reads that, `is_grove()` classifies it. Two consumers exist
today and share one idiom (`bank_union.py:41-44`):

```python
subject = resolve_subject()
if is_grove(subject):
    ...            # this one grove
...                # every grove under the garden
```

Grove sync is the **third consumer of the same mechanism** and must use it verbatim. It
introduces no env var, no config key, and no notion of scope of its own.

**One small consolidation to make while here.** That grove-or-garden branch is
currently open-coded at each call site, and `session-start.py:57-84` even re-implements
`is_grove`'s check inline rather than importing it. Add the canonical helper to
`garden.py`:

```python
def groves_in(subject: Path) -> list[Path]:
    """[subject] when it is itself a grove, else its DAFNE.md-carrying children."""
```

Grove sync uses it; `session-start.py` should adopt it in the same change. dafne keeps
its own `discover_grove_banks` readdir — that one is engine-side and correctly knows
nothing about `$DIOTIMA_GARDEN`. Non-duplication applies **within** a layer, not across
the engine boundary.

---

## The safety policy, as its own function

```python
def should_sync(st: GroveStatus) -> bool:
    return (
        st.has_upstream                    # else: skip silently, not a finding
        and st.branch == st.default_branch # not doing feature work
        and not st.dirty                   # no tracked-file modifications
        and st.behind > 0                  # something to get
        and st.ahead == 0                  # fast-forward is possible
    )
```

**Keep "no upstream" and "not on the default branch" as separate facts.** They are
different situations wanting different messages — one is silent and normal, the other is
a one-line skip notice — and collapsing them (an unresolvable `default_branch` standing
in for "no remote") makes the predicate skip for the right reason with the wrong
explanation.

Separate from execution so it is testable without git, and changeable without touching
the operations. Notes on each condition:

- **`on_default_branch` is resolved, never hardcoded.** Verified 2026-09-18: all four
  groves are on `main`, while the orchestrator repo is on `master`. Resolve the remote's
  default (`git symbolic-ref refs/remotes/origin/HEAD`) and compare.
- **`dirty` means tracked modifications only** — `git status --porcelain
  --untracked-files=no`. Untracked files must not block: every generated artifact in a
  grove is already gitignored (`*.compiled.md`, `*.preprocessed.md`,
  `*.md.feedback.jsonl`, `small-bank.md`, `*.apkg` — verified in
  `diotima-garden/spanish/.gitignore`), and a stray untracked note cannot break a
  fast-forward.
- **`ahead == 0`** is what makes this safe for the author on their own machine: local
  commits mean the fast-forward is refused, and refusal is correct.
- **No upstream at all** (a locally-created grove) → not a finding, not an error. Skip
  silently.

---

## `sync` is pull **and** submodule update, as one unit

```
git merge --ff-only @{u}                    # not `git pull` -- see the amendment below
git submodule update --init --recursive     # never --force
```

**This is not two steps that can be split.** If the author bumped a parent pin, pulling
alone updates the *recorded* pin while `parents/language` stays checked out at the old
SHA — and `git status` then reports `modified: parents/language (new commits)`. The tree
now **looks dirty**, which trips this flow's own `dirty` precondition on the next launch
and silently disables auto-sync from then on. A self-disabling feature that reports
nothing is precisely this project's stated default failure mode
(`structural-lessons.md:19-24`); the two commands are one operation or the feature rots.

`--force` is omitted deliberately: without it, a genuinely dirty submodule refuses,
which is the wanted behavior.

---

## Mechanics

- **Fetch is the only network operation.** Throttle it on `.git/FETCH_HEAD`'s mtime —
  git stamps that on every fetch, so **git's own refs are the cache** and there is no
  cache file, staleness marker, or throttle bookkeeping to invent.
- **Hard timeout, fail open.** A flaky network must never fail a launch. In
  `bin/diotima` this matters doubly: the script runs under `set -euo pipefail`
  (`bin/diotima:2`), so every git call needs an explicit `|| true`.
- **The fast-forward is a local ref merge** — instant, and it still works offline
  against whatever was last fetched.
- **Report the exception, not the success.** A sync that works needs no announcement. A
  sync that was *skipped* because you are on a feature branch or have uncommitted work
  is worth exactly one line, or you stay behind and never learn why.
- **Silent to the user, never silent to the record.** This is the first thing in the
  system that mutates the user's *content* repos without asking, so the trigger-log
  contract applies with full force (`structural-lessons.md:19-24`: every hook and worker
  writes a trigger log as its primary debugging surface). Every sync appends one line —
  `spanish: ff 7ba8124..3f9c1a0, submodules aligned` — and so does every skip, with its
  reason. When a grove's text changes underneath the user and a card generation goes
  sideways an hour later, that line is the only thing connecting the two.

---

## Caller-agnostic API, thin CLI

The module returns data; it does not print. Formatting belongs to whoever calls it —
that is what keeps the hook-vs-launcher decision open.

```python
@dataclass(frozen=True)
class GroveStatus:
    path: Path
    branch: str
    has_upstream: bool              # False -> skip silently; a distinct fact from the one below
    default_branch: str | None      # None = remote present but default unresolvable
    behind: int
    ahead: int
    dirty: bool
    submodules_aligned: bool

def fetch(grove: Path, max_age_s: int, timeout_s: int) -> bool     # False = skipped/failed, never raises
def status(grove: Path) -> GroveStatus                             # local reads only
def should_sync(st: GroveStatus) -> bool
def sync(grove: Path) -> SyncResult                                # pull + submodule update, as one unit
```

Plus a `main()` for the bash caller, following this project's semantic-token convention
(`compiled-is-fresh.py:1-9` — exit 0 with a leading token, non-zero only for genuine
errors). Git calls use `subprocess.run(..., cwd=grove)`, never `git -C` and never
chained shell.

Today's wiring: `bin/diotima` calls the CLI before `exec claude`. Tomorrow's may be the
hook, or both. Neither the module nor `garden.py` changes when that moves.

### No `.claude/settings.json` entry — and why that isn't a policy violation

`security.md:32-40` forbids ever whitelisting a git command that stages, commits, or
pushes. A builder will reach for a permission rule here by analogy to
`check-requires.py` (`.claude/settings.json:45`) and then find this design apparently in
conflict with that rule. It isn't, and the reason is placement, not exemption:
**`bin/diotima` runs the sync before `exec claude`, so the mutation happens outside any
session** — the permission system is not involved, and an allow rule would be inert
ceremony. The user's consent here is the standing ruling that auto-sync is the wanted
launch behavior, granted once, at design time.

The moment that changes, the rule reasserts itself: if the CLI is ever invoked from
*inside* a session — the sync-on-demand skill in the doors table below — that
invocation is an in-session mutation of the user's content and stays prompted like any
other, with no allow rule added for it.

---

## Handoff notes — the details a fresh builder would otherwise guess

*Added 2026-09-18 after auditing this document for build-readiness. Each item was
genuinely underspecified above; each is now verified against the tree.*

**Enter builder mode first** (`modes/meta/builder/context.md`) — this touches
`system/`, `bin/`, and possibly `.claude/`, so its entry contract applies.

### Interpreter: plain `python3`, **not** the dafne venv — this one is load-bearing

Every whitelisted script in this project runs under
`plugins/dafne/.venv/bin/python3`, and copying that pattern here would **break the
feature on exactly the machines it exists to serve.** That venv is gitignored
(`plugins/dafne/.gitignore:1`), so it is absent on every fresh clone — the same finding
`requires_refusal.md` recorded as an adjacent gap. A consumer who just cloned the
orchestrator and their groves has no venv yet, and grove sync must work on their first
launch.

It can, because nothing in the path needs a third-party package: `grove_sync.py` needs
only `subprocess`, `pathlib`, `dataclasses`; `garden.py` imports `json`/`os`/`pathlib`;
`utils/log.py` imports `datetime`/`pathlib`. **All stdlib.** `bin/diotima` already calls
plain `python3` (`bin/diotima:16`) — use the same.

### Trigger log: the convention already exists, reuse it verbatim

From `invoke-mneme-on-groves.py:22-26`:

```python
sys.path.insert(0, str(_SCRIPT_DIR.parent.parent / ".claude"))
from utils.log import make_logger   # noqa: E402

log = make_logger("grove-sync", _SCRIPT_DIR / "diotima.log")
```

One shared `system/diotima/diotima.log`, tagged per script. `make_logger` already
swallows its own write failures (`.claude/utils/log.py:9-14`), so logging can never take
a launch down. Path derives from `__file__`, so it is cwd-independent — which matters,
since the launcher runs this from wherever the user invoked `diotima`.

### CLI output shape

This deviates from the single-leading-token convention (`compiled-is-fresh.py:1-9`)
deliberately, and the reason should not be re-litigated: those CLIs answer about **one**
subject for an **LLM** reader, while this one reports on **many** groves to **bash**.
So: one prefixed line per grove that did something, and **nothing at all** for groves
already current — the "report the exception, not the success" ruling, applied to stdout.

```
SYNCED: spanish 7ba8124..3f9c1a0 (submodules aligned)
SKIPPED: english — uncommitted changes on main
SKIPPED: instruments — on branch try-new-layout, not main
```

Exit 0 whenever the walk completed, including when everything was skipped; non-zero only
for genuine errors (bad usage, unreadable subject). A fetch failure is a logged skip,
never a non-zero exit — one unreachable remote must not fail a launch.

### The git commands, concretely

| Fact | Command (run with `subprocess.run(..., cwd=grove)`) |
|---|---|
| has upstream | `git rev-parse --abbrev-ref --symbolic-full-name @{u}` — non-zero ⇒ no upstream ⇒ skip silently |
| current branch | `git rev-parse --abbrev-ref HEAD` |
| default branch | `git symbolic-ref --short refs/remotes/origin/HEAD` → `origin/main` ⇒ strip prefix |
| behind / ahead | `git rev-list --left-right --count HEAD...@{u}` → `"<ahead>\t<behind>"` |
| dirty (tracked only) | `git status --porcelain --untracked-files=no` — empty ⇒ clean |
| submodules aligned | `git submodule status --recursive` — any line starting `+` ⇒ misaligned |
| fetch | `git fetch --quiet` |
| sync | `git merge --ff-only @{u}` then `git submodule update --init --recursive` — **not `git pull --ff-only`**, corrected at build time 2026-09-18; see the amendment at the foot of this file |

Verified live 2026-09-18: all four groves are on `main`, clean, submodules aligned; the
orchestrator is on `master` — which is why the default branch is resolved, never
assumed.

### Tunables belong in `config.json`

`system/diotima/config.json` is already the home for this kind of value (it holds
`default_garden`, read by `garden.py:17-19`). Add `fetch_max_age_s` (start at `14400` —
four hours) and `fetch_timeout_s` (start at `5`). Starting values, not rulings; the
point is that they are not literals buried in the module.

### Tests: a new `system/diotima/tests/`

No test directory exists under `system/` today — dafne has `plugins/dafne/tests/` and
the orchestrator has nothing. Create the sibling. Fixtures are throwaway git repos built
in pytest's `tmp_path` (`git init` a bare "remote," clone it, commit into the remote to
manufacture "behind"), which is also how the submodule-footgun regression test must be
built — that one is named in the exit criteria as mandatory, and a manual-only check
will not survive.

---

## Exit criteria

- A grove cloned fresh, left untouched, with new upstream commits → next `diotima`
  launch leaves it at the upstream tip with submodules aligned, no prompt, no
  announcement.
- The same grove with one tracked file edited → not pulled, one line saying why.
- The same grove on a feature branch → not pulled, one line saying why.
- A grove with local unpushed commits → not pulled (`ahead > 0`), one line saying why.
- A grove with no remote → silently skipped, no line, no error.
- Network unplugged → launch proceeds at normal speed; no hang, no failure.
- An upstream commit that bumps a parent pin → after sync, `git submodule status
  --recursive` shows no `+` and `git status` is clean. **This is the regression test for
  the self-disabling footgun above** and must exist before the feature is called done.
- `grove_sync.py` contains no env-var read and no garden path of its own; scope comes
  from `garden.py` alone.
- Every sync and every skip leaves a trigger-log line with its reason — so a grove whose
  text changed under the user is always traceable after the fact, even though nothing
  was announced at the time.

---

## Doors held open, nothing built

| Door | Trigger | Pre-paid by |
|---|---|---|
| Move `fetch`/`sync` into the SessionStart hook | a launch-time cost that annoys, or a need to sync mid-session | the three-operation split; `status` is already hook-safe |
| Ask before syncing (opt-in prompt) | a user who wants to review before their content changes | `should_sync` is one function |
| Author-side re-pinning | a parent you don't own publishing an improvement you want | `assisted_parent_update.md`, fully designed and shelved |
| Sync-on-demand as a skill | wanting it without relaunching | the CLI already exists for the launcher |


---

## Built 2026-09-18 — amendments from execution

*Implemented in `system/diotima/grove_sync.py`. The full execution narrative, including
two bugs the tests caught, is in `dafne-plan-details/phase-4.md`. Recorded here because
each item below means this document said something that turned out to be wrong, and a
future reader must not re-derive the original.*

**`git merge --ff-only @{u}`, never `git pull --ff-only`.** This document contradicted
itself: the commands table said `pull`, while Mechanics said "the fast-forward is a
local ref merge — instant, and it still works offline." Mechanics was right. Verified on
a throwaway repo with the remote renamed away — `pull --ff-only` dies with `Could not
read from remote repository` and leaves the grove behind, where `merge --ff-only @{u}`
fast-forwards against the last-fetched ref. `pull` also re-fetches, which would defeat
the `FETCH_HEAD` throttle this same document specifies. Both spellings above are
corrected in place.

**`fetch` is called concurrently across groves.** The three-operation split is unchanged
and `fetch()` is still the single-grove operation the API promises, but the CLI drives
it through a `fetch_all()` thread pool. Serially, an unreachable network costs
`len(groves) × fetch_timeout_s` before *every* launch — 20s for four groves — which is
this document's own "network unplugged → launch proceeds at normal speed" criterion
failing quietly. Measured: 6.8s → 2.1s cold on the real garden; 5.3s rather than 20s
against four blackhole remotes.

**`skip_reason` names the branch before it tests upstream.** "No upstream → skip
silently" and the example line `SKIPPED: instruments — on branch try-new-layout, not
main` collide in the common case: a feature branch that was never pushed has no
upstream either, so testing upstream first silenced exactly the case the example shows.
A resolvable `origin/HEAD` proves a remote exists, so the branch mismatch leads; silence
is reserved for a grove with **no remote at all**, which is what the ruling meant. The
two facts stay separate as this document insisted — the ordering is what changed.

**Still true and worth keeping:** a failed *or timed-out* fetch still stamps
`.git/FETCH_HEAD`, so the throttle covers failures as well as successes — a permanently
offline machine pays one timeout every `fetch_max_age_s`, not one per launch. "Git's own
refs are the cache" holds more completely than the design claimed.

**`should_sync` does not consult `submodules_aligned` — and `skip_reason` must.** The
predicate above is correct as designed, but it leaves one state unreported: a grove that
is current and clean with an *uninitialized* submodule. That flavor of misalignment does
not appear in `git status --porcelain` (verified), so `dirty` is False, `behind` is 0,
and the grove reads as healthy forever while its parents are missing from disk. The skip
path now names it, ahead of the `dirty` check — a submodule at the wrong SHA *does* show
as a modified path, and "uncommitted changes" would misdescribe it. Reporting only:
healing a grove with nothing to pull would be a second operation this document never
designed, and the "one indivisible unit" ruling is about the merge, not about re-running
submodule update on demand.

**`git submodule update` is a network operation as well as a working-tree one.** The
three-operation table treats `sync` as a pure working-tree call, but when a pin moves to
a SHA the local object store lacks, it clones. `fetch` is therefore not quite "the only
network operation" — it is the only *unconditional* one. Bounded by its own
`submodule_timeout_s` (60s, well above `fetch_timeout_s`, since a real first clone
legitimately takes longer than a ref check).
