#!/usr/bin/env python3
"""
Shared #include graph traversal for the context-compiler plugin.

Provides resolve_include_path and collect_inputs — used by both
preprocess.py (text assembly) and compiled-is-fresh.py (freshness check).
"""
from pathlib import Path


def resolve_include_path(path_str: str, from_file: Path, project_root: Path) -> Path:
    if path_str.startswith("."):
        return (from_file.parent / path_str).resolve()
    return (project_root / path_str).resolve()


def collect_inputs(entry: Path, project_root: Path, seen: set[Path]) -> list[Path]:
    """Return all files reachable from entry via #include, in DFS order."""
    resolved = entry.resolve()
    if resolved in seen or not resolved.exists():
        return []
    seen.add(resolved)
    results = [resolved]
    for line in resolved.read_text().splitlines():
        bare = line.rstrip("\r\n")
        if bare.startswith("#include "):
            path_str = bare[len("#include "):].strip()
            child = resolve_include_path(path_str, resolved, project_root)
            results.extend(collect_inputs(child, project_root, seen))
    return results
