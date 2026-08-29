#!/usr/bin/env python3
"""
Orchestrator — session-end hook.

Replaces the old `small-bank.py --subscriptions groves/mem-bank-subscriptions.json`
hook entry. Unions the orchestrator's own banks with every mounted grove's
banks (discovered via dafne) and hands the merged list to mneme's
run_hook() in-process — mneme still reads stdin itself; this script never
touches it. See modes/meta/architect/bank_discovery_wiring.md.

A dafne failure here must not take session-end memory capture down with
it — errors are logged and degrade to the orchestrator's own banks only.
"""
import sys
from pathlib import Path
from types import SimpleNamespace

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
from bank_union import load_mneme_main, own_banks, grove_banks  # noqa: E402

sys.path.insert(0, str(_SCRIPT_DIR.parent.parent / ".claude"))
from utils.log import make_logger  # noqa: E402
from utils.project_dir_infrastructure import get_project_root  # noqa: E402

log = make_logger("invoke-mneme-on-groves", _SCRIPT_DIR / "diotima.log")


def main():
    project = get_project_root()

    banks = own_banks(project)
    try:
        banks += grove_banks(project)
    except Exception as e:
        log(f"grove bank discovery failed, continuing with own banks only: {e}")

    small_bank = load_mneme_main(project, "small-bank.py")
    args = SimpleNamespace(subscriptions=None)
    return small_bank.run_hook(args, banks=banks)


if __name__ == "__main__":
    sys.exit(main())
