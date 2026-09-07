#!/usr/bin/env python3
"""
Orchestrator -- SessionStart hook: injects orientation as additionalContext.

bin/diotima always launches this session with cwd = master (the only cwd
Claude Code will load master's .claude/settings.json, hooks and
permissions from -- confirmed empirically, no ancestor-walking). It
resolves what the session's *subject* is (a grove, or the garden) before
launch and hands it down as $DIOTIMA_GARDEN, reusing that name since
within this process it *is* the one directory this hook needs: a grove
if invoked from inside one, else the garden. This script never re-derives
that choice -- it only reads the one directory it's given and reports
what's there:
  - $DIOTIMA_GARDEN itself carries a DAFNE.md -> inject its manifest text.
  - otherwise -> enumerate it one level deep for DAFNE.md-carrying
    children. is_a_grove(repo) is DAFNE.md alone -- no `parents/`
    requirement, since a root grove legitimately has none. Mirrors
    plugins/dafne/manifest.py's discover_grove_banks readdir-not-
    configuration discipline (which groves exist is a directory listing,
    never orchestrator config) without importing the engine: this check
    is only ever "does this file exist", never manifest content.

Orchestrator-owned, not shipped by the dafne engine plugin: grove
discovery about *this* runtime's garden is this runtime's concern, the
same split bank discovery and requires-refusal already used (dafne stays
a pure engine; system/diotima/ wires it into this orchestrator's hooks).

Direct invocation (no bin/diotima, no $DIOTIMA_GARDEN set) falls back to
system/diotima/config.json's default_garden -- the one place that default
is written down; never duplicated here.

No network call in the empty-garden case -- a static pointer to
https://github.com/diotima-garden is printed instead; live enumeration of
that org is deferred (see dafne_plan.md Phase 3 bullet 3).

A failure here must not take session start down with it -- errors are
swallowed and no context is injected, mirroring invoke-mneme-on-groves.py's
degrade-gracefully posture for hooks.
"""
import json
import os
import sys
from pathlib import Path

_CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


def default_garden() -> Path:
    config = json.loads(_CONFIG_PATH.read_text())
    return Path(config["default_garden"]).expanduser()


def resolve_dir() -> Path:
    raw = os.environ.get("DIOTIMA_GARDEN")
    return Path(raw).expanduser() if raw else default_garden()


def emit(text: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": text,
        }
    }))


def context_for(dir_path: Path) -> str:
    manifest_path = dir_path / "DAFNE.md"
    if manifest_path.exists():
        return (
            f"You are in grove `{dir_path.name}` ({dir_path}). Its manifest (DAFNE.md):\n\n"
            + manifest_path.read_text()
        )
    return garden_listing(dir_path)


def garden_listing(garden: Path) -> str:
    garden.mkdir(parents=True, exist_ok=True)

    groves = sorted(
        child for child in garden.iterdir()
        if child.is_dir() and (child / "DAFNE.md").exists()
    )

    if not groves:
        return (
            f"No groves found in the garden ({garden}). "
            "Check out existing groves at https://github.com/diotima-garden."
        )

    lines = [f"Groves available in the garden ({garden}):"]
    for g in groves:
        lines.append(f"- {g.name}  ({g / 'DAFNE.md'})")
    return "\n".join(lines)


def main() -> int:
    try:
        emit(context_for(resolve_dir()))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
