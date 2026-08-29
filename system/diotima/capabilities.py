"""
Capability probes — the orchestrator's half of the requires:/refusal seam.

dafne answers what a node needs and who said so (manifest.py's
requirements_with_provenance); this module answers whether the runtime has
it, right now, on this machine. Neither side learns the other's vocabulary
— see modes/meta/architect/requires_refusal.md for the full design.

`installed_capabilities()` is the one seam a future package manager,
plugin path, or marketplace replaces the body of. Nothing else changes
when it does.
"""
import json
from pathlib import Path


def _anki_paths(project_dir: Path) -> list[Path] | None:
    """Resolves the interpreter + server paths out of .mcp.json rather than
    hardcoding plugins/anki-mcp/.venv, so a future delivery-mechanism change
    (e.g. uvx) only requires updating .mcp.json and this probe together, not
    hunting a hardcoded path. Returns None if .mcp.json itself is unreadable
    or malformed — a distinct case from "paths don't exist"."""
    mcp_config = Path(project_dir) / ".mcp.json"
    try:
        config = json.loads(mcp_config.read_text())
        anki = config["mcpServers"]["anki"]
        return [Path(project_dir) / anki["command"], Path(project_dir) / anki["args"][0]]
    except (OSError, KeyError, IndexError, ValueError):
        return None


def _anki_installed(project_dir: Path) -> bool:
    """Structural probe only — never calls AnkiConnect."""
    paths = _anki_paths(project_dir)
    return paths is not None and all(p.exists() for p in paths)


def _anki_missing_path(project_dir: Path) -> str | None:
    """First path this probe would need but doesn't find, for the refusal
    message. None if .mcp.json can't even be read, or nothing is missing."""
    paths = _anki_paths(project_dir)
    if paths is None:
        return str(Path(project_dir) / ".mcp.json")
    for p in paths:
        if not p.exists():
            return str(p)
    return None


CAPABILITIES = {
    "anki": _anki_installed,
}

_MISSING_PATH_PROBES = {
    "anki": _anki_missing_path,
}


def installed_capabilities(project_dir: Path) -> set[str]:
    """Probed at query time, never a maintained list — .venv/ is
    gitignored, so a fresh clone has the plugin's source but not its
    interpreter; a cached list would lie about exactly that machine."""
    installed = set()
    for name, probe in CAPABILITIES.items():
        try:
            if probe(project_dir):
                installed.add(name)
        except Exception:
            # A failing probe must degrade to "not installed", never crash
            # the caller — this mirrors invoke-mneme-on-groves.py's defensiveness.
            pass
    return installed


def missing_path(name: str, project_dir: Path) -> str | None:
    """Decorates a refusal with the first path the named capability's probe
    couldn't find — Provision-layer detail, never fed back into the
    Resolution decision above. Returns None if there's no such detail probe,
    or the probe itself fails; the caller degrades to a generic message."""
    probe = _MISSING_PATH_PROBES.get(name)
    if probe is None:
        return None
    try:
        return probe(project_dir)
    except Exception:
        return None
