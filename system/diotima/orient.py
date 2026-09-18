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
framings cannot drift apart.

Takes the grove directly -- does not call resolve_subject() itself. A
caller decides scope exactly once (garden.py's own commitment); the hook
passes its already-resolved subject, the CLI takes --grove as a required
argument with no resolve_subject() fallback.
"""
import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
sys.path.insert(0, str(_SCRIPT_DIR))
import grove_sync  # noqa: E402

sys.path.insert(0, str(_PROJECT_ROOT / "plugins" / "mneme"))
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
class GroveOrientation:
    manifest_text: str
    populated_banks: list[tuple[dict, str]]   # (bank_cfg, small_bank_content)
    git_status: str | None                    # None = clean, nothing to report


def orientation_for(grove: Path) -> GroveOrientation:
    """Gathers manifest + populated-bank content + this grove's own git status.
    Takes the resolved grove directly -- does not call resolve_subject() itself,
    so the hook and the mid-session CLI share one function with two different
    callers deciding scope."""
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
    )


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


def format_orientation(o: GroveOrientation, grove: Path) -> str:
    lines = [
        f"You are in grove `{grove.name}` ({grove}). Its manifest (DAFNE.md):",
        "",
        o.manifest_text.rstrip("\n"),
        "",
    ]

    if o.populated_banks:
        lines.append("Populated mem-banks:")
        for bank_cfg, content in o.populated_banks:
            label = bank_cfg.get("name", bank_cfg.get("bank"))
            lines.append(f"\n--- {label} ({bank_cfg['bank']}/small-bank.md) ---")
            lines.append(content.rstrip("\n"))
    else:
        lines.append(
            "No grove-side memory captured yet in any bank -- normal for a "
            "fresh or rarely-triggered bank, not a problem."
        )

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
