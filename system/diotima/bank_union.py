"""
Bank union — the one place dafne and mneme's vocabularies meet.

Unions the orchestrator's own banks (system/mem-bank-subscriptions.json —
for banks with no owning grove, e.g. meta, world-adoption) with the
session's grove bank(s), discovered by walking the tree with dafne.
Neither dafne nor mneme learns the other exists; see
modes/meta/architect/bank_discovery_wiring.md for the full design.

Groves live outside the tree (garden ruling (a), dafne_plan.md Phase 3) —
grove_banks() resolves the same `$DIOTIMA_GARDEN` "subject" session-start.py
injects from: a single grove's banks when the session was launched from
inside one, else every grove's banks under the garden. This mirrors the
SessionStart hook's own scoping deliberately — session-end capture and
graduation are about whatever the session's subject was, not "every grove
that happens to exist," per the 2026-09-07 ruling recorded in
dafne_plan.md.
"""
import importlib.util
import json
import sys
from pathlib import Path

_OWN_SUBSCRIPTIONS = "mem-bank-subscriptions.json"


def own_banks(project_dir: Path) -> list[dict]:
    path = Path(project_dir) / "system" / _OWN_SUBSCRIPTIONS
    if not path.exists():
        return []
    return json.loads(path.read_text()).get("banks", [])


def grove_banks(project_dir: Path) -> list[dict]:
    sys.path.insert(0, str(Path(project_dir) / "plugins" / "dafne"))
    from manifest import discover_banks, discover_grove_banks

    sys.path.insert(0, str(Path(project_dir) / "system" / "diotima"))
    from garden import resolve_subject, is_grove

    subject = resolve_subject()
    if is_grove(subject):
        return _mark_in_session_scope(discover_banks(subject), subject)
    return discover_grove_banks(subject)


def _mark_in_session_scope(banks: list[dict], subject: Path) -> list[dict]:
    """Declare, mechanically, that this session's subject owns these banks.

    mneme's match gate is a transcript pattern -- a *proxy* for "this session
    was about this bank". Injecting the manifest at session start removed the
    read the proxy keyed on, and the proxy then measured the wrong thing
    (see modes/meta/architect/bank_discovery_wiring.md, 2026-10-20). The
    subject is known here with certainty, so it is stated rather than
    re-derived from text evidence downstream.

    Only banks the subject grove itself declares are tagged -- inherited
    parent banks stay on pattern matching, since nothing says the session
    engaged the parent. The garden-wide branch is never tagged: it would put
    every grove's bank in scope for every session.
    """
    subject = subject.resolve()
    tagged = []
    for bank in banks:
        bank = dict(bank)
        path = bank.get("bank")
        if path and Path(path).resolve().is_relative_to(subject):
            bank["in_session_scope"] = True
        tagged.append(bank)
    return tagged


def unioned_banks(project_dir: Path) -> list[dict]:
    """Concatenation, not a dedup'd set — accepted per the design record:
    duplicate names across sources queue twice but degrade harmlessly."""
    return own_banks(project_dir) + grove_banks(project_dir)


def load_mneme_main(project_dir: Path, script_name: str):
    """mneme's entry-point scripts are hyphenated (not plain-importable);
    load them by file path instead of renaming mneme's own files."""
    mneme_dir = Path(project_dir) / "plugins" / "mneme"
    module_name = script_name.removesuffix(".py").replace("-", "_")
    spec = importlib.util.spec_from_file_location(
        f"mneme_{module_name}",
        mneme_dir / script_name,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
