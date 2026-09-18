#!/usr/bin/env python3
"""
Orchestrator — grove sync: the consumer propagation flow.

A grove you cloned falls behind the version its author published. This
catches it up automatically, but only when doing so is provably safe: on
the default branch, no tracked file edited, nothing local to lose. Those
conditions are exactly the ones under which a fast-forward cannot
conflict, cannot lose work and cannot create a merge commit — so when
they hold there is nothing to ask about. Designed in
modes/meta/architect/grove_sync.md.

Three operations, separately callable, because where each belongs
resolves differently:
  - fetch()  — the only network call. Launcher-only: it would block a
               SessionStart hook's first prompt, and an offline machine
               would turn a swallow-all-errors hook into a hang.
  - status() — local ref reads only. Safe anywhere, including a hook.
  - sync()   — mutates the working tree. A policy call, not a mechanics one.
A monolithic update_groves() would force one answer for all three and
freeze it; keeping them apart is what lets the launcher-vs-hook question
stay open.

Scope is never derived here. garden.py owns "is this session about one
grove or the whole garden" ($DIOTIMA_GARDEN, config.json) and this module
is its third consumer — no env var, no config key, no garden path of its
own.

stdlib only, and run under plain `python3`. The dafne venv is gitignored,
so it is absent on exactly the fresh clones this feature exists to serve.

Usage: python3 grove_sync.py [--no-fetch]
"""
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
from garden import groves_in, resolve_subject  # noqa: E402

sys.path.insert(0, str(_SCRIPT_DIR.parent.parent / ".claude"))
from utils.log import make_logger  # noqa: E402

log = make_logger("grove-sync", _SCRIPT_DIR / "diotima.log")

_CONFIG_PATH = _SCRIPT_DIR / "config.json"
_DEFAULT_FETCH_MAX_AGE_S = 14400
_DEFAULT_FETCH_TIMEOUT_S = 5
_DEFAULT_SUBMODULE_TIMEOUT_S = 60

# An https remote with no cached credential hangs on a prompt, and a
# timeout alone does not cover that -- git must be told there is no one
# to ask before it opens its mouth.
_NONINTERACTIVE = {
    "GIT_TERMINAL_PROMPT": "0",
    "GIT_ASKPASS": "/bin/true",
    "SSH_ASKPASS": "/bin/true",
}


@dataclass(frozen=True)
class GroveStatus:
    path: Path
    branch: str
    has_upstream: bool          # False -> skip silently; distinct fact from the one below
    default_branch: str | None  # None = remote present but default unresolvable
    behind: int
    ahead: int
    dirty: bool
    submodules_aligned: bool


@dataclass(frozen=True)
class SyncResult:
    path: Path
    ok: bool
    before: str
    after: str
    submodules_aligned: bool
    detail: str


def _tunable(key: str, fallback: int) -> int:
    try:
        return int(json.loads(_CONFIG_PATH.read_text())[key])
    except Exception:
        return fallback


def _git(grove: Path, *args: str, timeout: int | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=grove,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, **_NONINTERACTIVE},
    )


def _stderr_tail(done: subprocess.CompletedProcess, keep: int = 3) -> str:
    """The last few stderr lines, joined. Not the first: git leads with
    progress and "registered for path" chatter and puts the actual fatal
    last, so logging line one hides the very thing the trigger log exists
    to surface."""
    lines = [ln.strip() for ln in (done.stderr or "").splitlines() if ln.strip()]
    return " | ".join(lines[-keep:]) or "(no stderr)"


def _git_out(grove: Path, *args: str) -> str | None:
    """Stripped stdout, or None when git exited non-zero — the non-zero is
    itself the answer for several of these (no upstream, no origin/HEAD)."""
    try:
        done = _git(grove, *args)
    except Exception:
        return None
    return done.stdout.strip() if done.returncode == 0 else None


# --- fetch: network, launcher-only -----------------------------------------

def fetch(grove: Path, max_age_s: int, timeout_s: int) -> bool:
    """True when a fetch actually ran. Never raises: a flaky network must
    not fail a launch.

    Throttled on .git/FETCH_HEAD's mtime — git stamps that on every fetch,
    so git's own refs are the cache and there is no throttle bookkeeping
    to invent.
    """
    if _fetched_recently(grove, max_age_s):
        return False
    try:
        done = _git(grove, "fetch", "--quiet", timeout=timeout_s)
    except subprocess.TimeoutExpired:
        log(f"{grove.name}: fetch timed out after {timeout_s}s, continuing with local refs")
        return False
    except Exception as e:
        log(f"{grove.name}: fetch failed ({e}), continuing with local refs")
        return False
    if done.returncode != 0:
        log(f"{grove.name}: fetch failed ({_stderr_tail(done)}), continuing with local refs")
        return False
    return True


def fetch_all(groves: list[Path], max_age_s: int, timeout_s: int) -> None:
    """fetch() across groves concurrently, so the launch cost is one timeout
    rather than one per grove.

    Serially, an unreachable network costs `len(groves) * timeout_s` before
    every launch — 20s for four groves — which is the "no hang" exit
    criterion failing quietly. Fetches are independent network waits with no
    shared state, so a thread each bounds the whole walk at roughly one
    timeout. fetch() stays the single-grove operation the API promises; this
    is only how the CLI drives it.
    """
    if not groves:
        return
    with ThreadPoolExecutor(max_workers=min(len(groves), 8)) as pool:
        futures = [pool.submit(fetch, g, max_age_s, timeout_s) for g in groves]
        for f in futures:
            try:
                f.result()
            except Exception:
                pass  # fetch already swallows its own; belt and braces


def _fetched_recently(grove: Path, max_age_s: int) -> bool:
    import time
    stamp = grove / ".git" / "FETCH_HEAD"
    try:
        return (time.time() - stamp.stat().st_mtime) < max_age_s
    except OSError:
        return False  # never fetched, or .git is a file (submodule) — just fetch


# --- status: local reads only, hook-safe ------------------------------------

def status(grove: Path) -> GroveStatus:
    branch = _git_out(grove, "rev-parse", "--abbrev-ref", "HEAD") or "HEAD"
    has_upstream = _git_out(grove, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}") is not None

    default_branch = None
    origin_head = _git_out(grove, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    if origin_head:
        default_branch = origin_head.split("/", 1)[1] if "/" in origin_head else origin_head

    ahead = behind = 0
    if has_upstream:
        counts = _git_out(grove, "rev-list", "--left-right", "--count", "HEAD...@{u}")
        if counts:
            parts = counts.split()
            if len(parts) == 2:
                # left = HEAD-only commits = ahead; right = upstream-only = behind.
                ahead, behind = int(parts[0]), int(parts[1])

    porcelain = _git_out(grove, "status", "--porcelain", "--untracked-files=no")
    dirty = bool(porcelain)

    return GroveStatus(
        path=grove,
        branch=branch,
        has_upstream=has_upstream,
        default_branch=default_branch,
        behind=behind,
        ahead=ahead,
        dirty=dirty,
        submodules_aligned=submodules_aligned(grove),
    )


def submodules_aligned(grove: Path) -> bool:
    """`git submodule status --recursive` marks every out-of-sync line with a
    leading character: '+' bumped, '-' uninitialized, 'U' conflicted. An
    aligned line leads with a *space* — which is why this reads raw stdout
    rather than going through _git_out(), whose strip() would eat the one
    character being tested.
    """
    try:
        done = _git(grove, "submodule", "status", "--recursive")
    except Exception:
        return True
    if done.returncode != 0:
        return True  # no submodules, or not a repo — nothing to be misaligned
    return all(line.startswith(" ") for line in done.stdout.splitlines() if line.strip())


# --- the policy, as its own function ----------------------------------------

def should_sync(st: GroveStatus) -> bool:
    return (
        st.has_upstream                     # else: skip silently, not a finding
        and st.default_branch is not None
        and st.branch == st.default_branch  # not doing feature work
        and not st.dirty                    # no tracked-file modifications
        and st.behind > 0                   # something to get
        and st.ahead == 0                   # fast-forward is possible
    )


def skip_reason(st: GroveStatus) -> str | None:
    """The one line a skip is worth. None = nothing to say (already current,
    or no remote at all — silent by ruling)."""
    # A resolvable origin/HEAD proves a remote exists, so name the branch
    # mismatch *before* testing upstream: a feature branch that was never
    # pushed has no upstream either, and "on branch try-new-layout, not
    # main" is the fact worth one line. Silence is for a grove with no
    # remote at all.
    if st.default_branch is not None and st.branch != st.default_branch:
        return f"on branch {st.branch}, not {st.default_branch}"
    if not st.has_upstream:
        return None
    if st.default_branch is None:
        return "remote's default branch could not be resolved"
    # Before `dirty`, because it is the more precise diagnosis of the same
    # symptom: a submodule checked out at the wrong SHA *does* show up in
    # `git status` as a modified path, and calling that "uncommitted
    # changes" would send the user looking for an edit they never made. An
    # *uninitialized* submodule does not show up there at all — that grove
    # is current, clean, and silently broken, which is the case this branch
    # exists for. Reported, never healed here: a grove that is behind gets
    # realigned by sync() as part of the one indivisible unit, and
    # re-running submodule update on a grove with nothing to pull would be
    # a second, undesigned operation.
    if not st.submodules_aligned:
        return "submodules out of sync — `git submodule update --init --recursive`"
    if st.dirty:
        return f"uncommitted changes on {st.branch}"
    if st.ahead > 0:
        return f"{st.ahead} local commit(s) not pushed"
    return None


# --- sync: pull and submodule update, as one indivisible unit ---------------

def sync(grove: Path, timeout_s: int = _DEFAULT_SUBMODULE_TIMEOUT_S) -> SyncResult:
    """Fast-forward to the already-fetched upstream, then realign submodules.

    `git merge --ff-only @{u}`, not `git pull --ff-only`: pull re-fetches,
    which defeats the FETCH_HEAD throttle and — verified 2026-09-18 —
    fails outright when the remote is unreachable, where the local ref
    merge still succeeds offline against whatever was last fetched.

    The submodule update is not a separable second step. If the author
    bumped a parent pin, merging alone updates the *recorded* pin while
    parents/language stays checked out at the old SHA, and `git status`
    then reports `modified: parents/language (new commits)` — the tree
    looks dirty, which trips this flow's own precondition on the next
    launch and silently disables auto-sync from then on. `--force` is
    omitted deliberately: a genuinely dirty submodule should refuse.
    """
    before = _git_out(grove, "rev-parse", "--short", "HEAD") or "?"

    merged = _git(grove, "merge", "--ff-only", "@{u}")
    if merged.returncode != 0:
        log(f"{grove.name}: ff refused ({_stderr_tail(merged)}) — left at {before}")
        return SyncResult(grove, False, before, before, submodules_aligned(grove),
                          "fast-forward refused")

    after = _git_out(grove, "rev-parse", "--short", "HEAD") or "?"

    # Bounded: when a pin moves to a SHA the local object store lacks, this
    # clones over the network. GIT_TERMINAL_PROMPT=0 covers the credential
    # hang; only a timeout covers a remote that accepts and then stalls.
    try:
        subs = _git(grove, "submodule", "update", "--init", "--recursive", timeout=timeout_s)
    except subprocess.TimeoutExpired:
        log(f"{grove.name}: ff {before}..{after}, submodule update timed out after {timeout_s}s")
        return SyncResult(grove, True, before, after, submodules_aligned(grove),
                          "submodule update timed out")
    aligned = submodules_aligned(grove)
    if subs.returncode != 0:
        log(f"{grove.name}: ff {before}..{after}, submodule update failed ({_stderr_tail(subs)})")
        return SyncResult(grove, True, before, after, aligned, "submodule update failed")

    log(f"{grove.name}: ff {before}..{after}, submodules {'aligned' if aligned else 'MISALIGNED'}")
    return SyncResult(grove, True, before, after, aligned, "synced")


# --- CLI: the launcher's caller ---------------------------------------------

def main(argv: list[str]) -> int:
    """One prefixed line per grove that did something, nothing at all for
    groves already current — "report the exception, not the success",
    applied to stdout. This deviates from the single-leading-token
    convention (compiled-is-fresh.py) on purpose: those CLIs answer about
    one subject for an LLM reader; this one reports on many groves to bash.
    """
    do_fetch = "--no-fetch" not in argv
    unknown = [a for a in argv if a != "--no-fetch"]
    if unknown:
        print(f"USAGE_ERROR: grove_sync.py [--no-fetch] (got {unknown})", file=sys.stderr)
        return 2

    subject = resolve_subject()
    if not subject.is_dir():
        print(f"SUBJECT_NOT_FOUND: {subject}", file=sys.stderr)
        return 1

    max_age_s = _tunable("fetch_max_age_s", _DEFAULT_FETCH_MAX_AGE_S)
    timeout_s = _tunable("fetch_timeout_s", _DEFAULT_FETCH_TIMEOUT_S)
    submodule_timeout_s = _tunable("submodule_timeout_s", _DEFAULT_SUBMODULE_TIMEOUT_S)

    groves = groves_in(subject)
    if do_fetch:
        fetch_all(groves, max_age_s, timeout_s)

    for grove in groves:
        try:
            st = status(grove)
            if should_sync(st):
                result = sync(grove, timeout_s=submodule_timeout_s)
                if result.ok:
                    aligned = "submodules aligned" if result.submodules_aligned else "SUBMODULES MISALIGNED"
                    print(f"SYNCED: {grove.name} {result.before}..{result.after} ({aligned})")
                else:
                    print(f"SKIPPED: {grove.name} — {result.detail}")
            else:
                reason = skip_reason(st)
                if reason:
                    log(f"{grove.name}: skipped — {reason}")
                    print(f"SKIPPED: {grove.name} — {reason}")
        except Exception as e:
            # One broken grove must never fail a launch, nor stop the walk —
            # but it must not be *silent* either: silence here is
            # indistinguishable from "already current", which is the one
            # reading that would leave a real failure unnoticed.
            log(f"{grove.name}: unexpected error, skipped ({e})")
            print(f"SKIPPED: {grove.name} — error, see system/diotima/diotima.log")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
