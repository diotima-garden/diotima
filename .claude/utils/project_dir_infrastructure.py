from pathlib import Path


def _find_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / ".git").exists():
            return p
    raise RuntimeError(f"project root not found (no .git) searching from {start}")


_ROOT = _find_root(Path(__file__).resolve())


def get_project_root() -> Path:
    return _ROOT


def get_system_dir() -> Path:
    return _ROOT / "system"


def get_plugins_dir() -> Path:
    return _ROOT / "plugins"
