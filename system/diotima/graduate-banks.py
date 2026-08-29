#!/usr/bin/env python3
"""
Orchestrator — graduation entry point.

Replaces the old `big-bank.py --subscriptions groves/mem-bank-subscriptions.json`
call from the mem-bank-big-bank skill. Unions the orchestrator's own banks
with every mounted grove's banks (via dafne) and hands the merged list to
mneme's big-bank main() in-process. See
modes/meta/architect/bank_discovery_wiring.md — this script exists because
that design added the banks= parameter to big-bank.py's main() but never
wrote its caller; without it, trimming subscriptions.json would silently
stop grove banks from ever reaching graduation.
"""
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
from bank_union import load_mneme_main, unioned_banks  # noqa: E402

sys.path.insert(0, str(_SCRIPT_DIR.parent.parent / ".claude"))
from utils.project_dir_infrastructure import get_project_root  # noqa: E402


def main(argv):
    project = get_project_root()
    banks = unioned_banks(project)
    big_bank = load_mneme_main(project, "big-bank.py")
    return big_bank.main(argv, banks=banks)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
