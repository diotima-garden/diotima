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
    children. Both branches come from garden.py's groves_in(), the one
    place that grove-or-garden test lives; being a grove is DAFNE.md
    alone -- no `parents/` requirement, since a root grove legitimately
    has none. Mirrors plugins/dafne/manifest.py's discover_grove_banks
    readdir-not-configuration discipline (which groves exist is a
    directory listing, never orchestrator config) without importing the
    engine: this check is only ever "does this file exist", never
    manifest content.

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
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from garden import groves_in, resolve_subject  # noqa: E402
from orient import format_orientation, orientation_for  # noqa: E402


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
        # Bank/git enrichment is best-effort: a manifest is always
        # injectable on its own, and a failure gathering the rest (a
        # malformed bank entry, a git call throwing) must not regress
        # that -- fall back to manifest-only rather than losing
        # injection entirely.
        try:
            return format_orientation(orientation_for(dir_path), dir_path)
        except Exception:
            return (
                f"You are in grove `{dir_path.name}` ({dir_path}). Its manifest (DAFNE.md):\n\n"
                + manifest_path.read_text()
            )
    return garden_listing(dir_path)


def garden_listing(garden: Path) -> str:
    garden.mkdir(parents=True, exist_ok=True)

    groves = groves_in(garden)

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
        emit(context_for(resolve_subject()))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
