#!/usr/bin/env python3
"""
Orchestrator -- grove orientation: closes the gap between what
session-start.py injects (raw DAFNE.md text) and what a session actually
needs to continue a grove's work -- its populated mem-bank content and its
own repo's git state. Designed in modes/meta/architect/grove_orientation.md.

Same layer as bank_union.py and grove_sync.py: orchestrator-owned, the
place dafne's and mneme's vocabularies meet -- on the read side, mirroring
bank_union.py's discovery-side reuse of the same two modules.

The module returns data; it does not print (grove_sync.md's ruling, reused
verbatim). format_orientation() is the one formatter shared by
session-start.py's hook injection and this file's own CLI, so the two
framings cannot drift apart. They differ in exactly one parameter: the
hook passes a byte `budget` and the CLI does not, because only the hook
is writing into a context window with a ceiling. Everything about how the
package reads stays shared; the budget only decides how many bank
entries survive, and says so in the output when it drops any.

Takes the grove directly -- does not call resolve_subject() itself. A
caller decides scope exactly once (garden.py's own commitment); the hook
passes its already-resolved subject, the CLI takes --grove as a required
argument with no resolve_subject() fallback.

Imports garden.py for one thing only: private_dir_for(grove), a config
lookup keyed by a name the caller already resolved, not a second scope
resolution -- see modes/meta/architect/private_layer.md.
"""
import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
sys.path.insert(0, str(_SCRIPT_DIR))
import garden  # noqa: E402
import grove_sync  # noqa: E402

sys.path.insert(0, str(_PROJECT_ROOT / "plugins" / "mneme"))
from registry import bank_small_bank_path as _bank_small_bank_path  # noqa: E402
from registry import populated_banks as _populated_banks  # noqa: E402

# dafne's manifest.py needs pyyaml, which lives in plugins/dafne/.venv --
# gitignored, absent on a fresh clone -- while this module (like
# grove_sync.py) must keep running under plain `python3`. Degrade to "no
# banks discovered" rather than let an ImportError take the hook down;
# same failure shape as a grove with no `banks:` declared at all.
try:
    sys.path.insert(0, str(_PROJECT_ROOT / "plugins" / "dafne"))
    from manifest import discover_banks
except ImportError:
    discover_banks = None


@dataclass(frozen=True)
class PrivatePresence:
    """Reports presence only -- never content, never filenames (both are
    disclosure). path is where it does or would live; exists/entry_count let
    the formatter distinguish 'nothing there yet' from 'N entries, read on
    demand' without ever enumerating what's inside. Counts every directory
    entry, not just files -- a subdirectory full of content must not report
    as empty."""
    path: Path
    exists: bool
    entry_count: int


@dataclass(frozen=True)
class GroveOrientation:
    manifest_text: str
    populated_banks: list[tuple[dict, str]]   # (bank_cfg, small_bank_content)
    git_status: str | None                    # None = clean, nothing to report
    private: PrivatePresence


def orientation_for(grove: Path) -> GroveOrientation:
    """Gathers manifest + populated-bank content + this grove's own git status
    + private-layer presence. Takes the resolved grove directly -- does not
    call resolve_subject() itself, so the hook and the mid-session CLI share
    one function with two different callers deciding scope."""
    manifest_text = (grove / "DAFNE.md").read_text()

    banks = discover_banks(grove) if discover_banks else []
    populated = [
        (bank_cfg, path.read_text())
        for bank_cfg, path in _populated_banks(banks)
    ]

    return GroveOrientation(
        manifest_text=manifest_text,
        populated_banks=populated,
        git_status=_git_status_text(grove),
        private=_private_presence(grove),
    )


def _private_presence(grove: Path) -> PrivatePresence:
    private_dir = garden.private_dir_for(grove)
    exists = private_dir.is_dir()
    entry_count = sum(1 for _ in private_dir.iterdir()) if exists else 0
    return PrivatePresence(path=private_dir, exists=exists, entry_count=entry_count)


def _git_status_text(grove: Path) -> str | None:
    """Reuses grove_sync.status() (non-duplication, per grove_orientation.md)
    for branch/dirty/ahead-behind. None when there's nothing notable --
    on the default branch (or no remote to compare against), clean, and
    current. Recent commits are appended only when there IS something
    notable, matching this codebase's "report the exception, not the
    success" convention (grove_sync.py's own skip_reason/main())."""
    st = grove_sync.status(grove)

    notable = []
    if st.default_branch is not None and st.branch != st.default_branch:
        notable.append(f"on branch {st.branch}, not {st.default_branch}")
    if st.dirty:
        notable.append("uncommitted changes")
    if st.ahead:
        notable.append(f"{st.ahead} commit(s) ahead of upstream")
    if st.behind:
        notable.append(f"{st.behind} commit(s) behind upstream")
    if not st.submodules_aligned:
        notable.append("submodules out of sync")

    if not notable:
        return None

    text = f"branch {st.branch} -- " + ", ".join(notable)
    log = grove_sync._git_out(grove, "log", "--oneline", "-n", "3")
    if log:
        text += "\nrecent commits:\n" + log
    return text


# Bank entry shape: mneme appends one `## <date> <time> (session <id>)`
# section per captured session. The canonical pattern is big-bank.py's
# SESSION_HEADER_RE; it is restated rather than imported because that
# module's filename is not importable and registry.py -- the submodule's
# importable surface -- does not re-export it. Lifting it into
# registry.py is a mneme-side change, deliberately out of scope for an
# orchestrator-only fix; until then this is the one other copy.
_BANK_ENTRY_RE = re.compile(
    r"^## \d{4}-\d{2}-\d{2} \d{2}:\d{2} \(session [a-zA-Z0-9]+\)",
    re.MULTILINE,
)


def _split_bank_entries(content: str) -> list[str]:
    starts = [m.start() for m in _BANK_ENTRY_RE.finditer(content)]
    if not starts:
        return []
    bounds = starts + [len(content)]
    return [content[bounds[i]:bounds[i + 1]].strip() for i in range(len(starts))]


def _is_skip_entry(entry: str) -> bool:
    """A session the bank's own filter excluded. mneme stopped appending
    these in 45c6615 (2026-08-19), but banks written before that still
    carry them -- pure framing, no training signal, so they are the first
    thing to go when the injection has to fit a budget."""
    return _BANK_ENTRY_RE.sub("", entry, count=1).strip().startswith("SKIP")


def _trim_bank(content: str, budget: int) -> tuple[str, tuple[int, int] | None]:
    """Fits one bank's content into `budget` bytes, preferring recent entries.

    Drops in order of expendability: SKIP placeholders unconditionally,
    then the oldest substantive entries until the remainder fits. The
    newest entry is always kept even if it alone busts the budget --
    "continue with the drills" resumes from the newest thread, so a
    session holding no recent bank content is worse off than one slightly
    over budget.

    Returns the text plus (skips, older-entries) counts when anything was
    dropped, or None when the content passed through whole so the caller
    can stay silent.
    """
    entries = _split_bank_entries(content)
    if not entries:
        # Shape we don't recognize -- hand it over untouched rather than
        # risk emitting a fragment. Over budget beats silently wrong.
        return content, None

    substantive = [e for e in entries if not _is_skip_entry(e)]
    skips = len(entries) - len(substantive)

    kept: list[str] = []
    used = 0
    for entry in reversed(substantive):
        cost = len(entry.encode()) + 2        # +2 for the blank-line join
        if kept and used + cost > budget:
            break
        kept.append(entry)
        used += cost
    kept.reverse()                            # back to chronological order

    dropped = len(substantive) - len(kept)
    if not skips and not dropped:
        return content, None
    return "\n\n".join(kept), (skips, dropped)


def _trim_notice(counts: tuple[int, int], bank_path: Path) -> str:
    """Says out loud that the injection is partial. The failure this whole
    mechanism exists to prevent is a *silent* truncation -- a session that
    believes it holds the full bank when it holds a prefix -- so an
    announced trim with a path to the rest is the entire point, not a
    footnote."""
    skips, dropped = counts
    parts = []
    if dropped:
        parts.append(
            f"{dropped} older {'entry' if dropped == 1 else 'entries'} withheld "
            "to stay inside the session-start context budget"
        )
    if skips:
        parts.append(
            f"{skips} SKIP placeholder{'' if skips == 1 else 's'} dropped "
            "(excluded sessions, no training signal)"
        )
    return (
        "[bank trimmed: " + "; ".join(parts) + f". Full history: {bank_path} "
        "-- read it directly if the entries above do not cover the thread you need.]"
    )


def _private_line(private: PrivatePresence) -> str:
    """Presence, never content, never filenames -- see PrivatePresence. Fires
    unconditionally, including on absence: silence-on-absence is this
    project's own named failure mode (CONTEXT_BUDGET_BYTES's own reason for
    existing), and a session told nothing can't distinguish 'no private
    layer' from 'the runtime forgot to check.' Each branch is a complete,
    independently-worded sentence -- not one fragment reused across three
    grammatical frames, which produced nonsense ("material there would read
    on demand") in the absence case, the default state for most groves."""
    if not private.exists:
        return (
            f"Private layer: none yet (would live at {private.path}). "
            "Material placed there informs this grove's work but must "
            "never be copied into a tracked file."
        )
    if private.entry_count == 0:
        return (
            f"Private layer: {private.path} (empty). Read on demand; "
            "never copy its content into a tracked file."
        )
    noun = "entry" if private.entry_count == 1 else "entries"
    return (
        f"Private layer: {private.path} ({private.entry_count} {noun}). "
        "Read on demand; never copy its content into a tracked file."
    )


def _bank_budget(o: GroveOrientation, grove: Path, budget: int, extra: int = 0) -> int:
    """Bytes left per bank once the parts that are never trimmed are paid for.

    The manifest is deliberately not negotiable: it is the grove's routing
    contract, and a half-delivered table is exactly the defect that
    prompted this. The overhead allowance is generous on purpose --
    undershooting costs one bank entry, overshooting costs the whole
    injection. `extra` folds in any other never-trimmed text (currently
    just the private-layer line) so the accounting stays honest -- this
    whole module exists because of a truncation incident."""
    overhead = len(o.manifest_text.encode()) + len(str(grove).encode()) + 512 + extra
    if o.git_status:
        overhead += len(o.git_status.encode())
    return max((budget - overhead) // len(o.populated_banks), 0)


def format_orientation(
    o: GroveOrientation, grove: Path, budget: int | None = None
) -> str:
    """Renders the orientation package. `budget` caps the result at roughly
    that many bytes by trimming bank content (see _trim_bank); None means
    no cap, which is what the CLI wants -- a deliberate read at a terminal
    has no context ceiling to respect. Only the hook passes a budget."""
    lines = [
        f"You are in grove `{grove.name}` ({grove}). Its manifest (DAFNE.md):",
        "",
        o.manifest_text.rstrip("\n"),
        "",
    ]

    private_line = _private_line(o.private)

    if o.populated_banks:
        per_bank = (
            _bank_budget(o, grove, budget, extra=len(private_line.encode()))
            if budget else None
        )
        lines.append("Populated mem-banks:")
        for bank_cfg, content in o.populated_banks:
            label = bank_cfg.get("name", bank_cfg.get("bank"))
            lines.append(f"\n--- {label} ({bank_cfg['bank']}/small-bank.md) ---")
            if per_bank is None:
                lines.append(content.rstrip("\n"))
                continue
            trimmed, omitted = _trim_bank(content, per_bank)
            lines.append(trimmed.rstrip("\n"))
            if omitted:
                lines.append(
                    _trim_notice(omitted, _bank_small_bank_path(bank_cfg, grove))
                )
    else:
        lines.append(
            "No grove-side memory captured yet in any bank -- normal for a "
            "fresh or rarely-triggered bank, not a problem."
        )

    lines.append("")
    lines.append(private_line)

    lines.append("")
    lines.append(
        f"This grove's own git status: {o.git_status if o.git_status else 'clean, up to date -- nothing to report.'}"
    )

    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Gather one grove's full orientation package: manifest, "
                     "populated mem-banks, and the grove's own git status."
    )
    parser.add_argument("--grove", required=True, type=Path,
                         help="Path to the grove (must contain a DAFNE.md).")
    args = parser.parse_args(argv)

    grove = args.grove.expanduser().resolve()
    if not (grove / "DAFNE.md").exists():
        print(f"NOT_A_GROVE: {grove} (no DAFNE.md)", file=sys.stderr)
        return 1

    print(format_orientation(orientation_for(grove), grove))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
