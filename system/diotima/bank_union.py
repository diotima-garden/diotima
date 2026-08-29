"""
Bank union — the one place dafne and mneme's vocabularies meet.

Unions the orchestrator's own banks (system/mem-bank-subscriptions.json —
for banks with no owning grove, e.g. meta, world-adoption) with every
mounted grove's declared banks, discovered by walking the tree with dafne.
Neither dafne nor mneme learns the other exists; see
modes/meta/architect/bank_discovery_wiring.md for the full design.
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
    dafne_dir = Path(project_dir) / "plugins" / "dafne"
    sys.path.insert(0, str(dafne_dir))
    from manifest import discover_grove_banks

    return discover_grove_banks(Path(project_dir) / "groves")


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
