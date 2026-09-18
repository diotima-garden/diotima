"""
Shared garden/subject resolution — the one place `$DIOTIMA_GARDEN` and
`config.json`'s `default_garden` are read from. `bin/diotima` narrows
`$DIOTIMA_GARDEN` to a single grove's path when invoked from inside one,
else it names the garden itself; both session-start.py (manifest
injection) and bank_union.py (mem-bank discovery) need that same
"subject" — a directory that is either a grove or a garden of groves —
resolved the same way.
"""
import json
import os
from pathlib import Path

_CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


def default_garden() -> Path:
    config = json.loads(_CONFIG_PATH.read_text())
    return Path(config["default_garden"]).expanduser()


def resolve_subject() -> Path:
    raw = os.environ.get("DIOTIMA_GARDEN")
    return Path(raw).expanduser() if raw else default_garden()


def is_grove(path: Path) -> bool:
    return (path / "DAFNE.md").exists()


def groves_in(subject: Path) -> list[Path]:
    """[subject] when it is itself a grove, else its DAFNE.md-carrying children.

    The grove-or-garden branch, in one place. Every consumer of
    resolve_subject() needs it; it was open-coded at each call site until
    grove sync became the third. dafne keeps its own readdir — that one is
    engine-side and correctly knows nothing about $DIOTIMA_GARDEN.
    """
    if is_grove(subject):
        return [subject]
    if not subject.is_dir():
        return []
    return sorted(
        child for child in subject.iterdir()
        if child.is_dir() and is_grove(child)
    )
