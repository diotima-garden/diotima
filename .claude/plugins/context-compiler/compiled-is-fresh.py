#!/usr/bin/env python3
"""
Check whether the compiled output for a source file is up-to-date.

Exit 0 if <stem>.compiled.md exists and is newer than all transitive #include inputs.
Exit 1 otherwise.

Usage: python3 .claude/plugins/context-compiler/compiled-is-fresh.py <source-file.md>
"""
import sys
from pathlib import Path
from include_graph import collect_inputs


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <source-file.md>", file=sys.stderr)
        sys.exit(2)

    source = Path(sys.argv[1])
    compiled = source.parent / f"{source.stem}.compiled.md"
    project_root = Path.cwd()

    if not source.exists():
        print(f"source file not found: {source}", file=sys.stderr)
        sys.exit(1)

    if not compiled.exists():
        print(f"compiled output not found: {compiled}")
        sys.exit(1)

    compiled_mtime = compiled.stat().st_mtime
    inputs = collect_inputs(source, project_root, set())

    for f in inputs:
        if f.stat().st_mtime > compiled_mtime:
            print(f"stale: {f.name} is newer")
            sys.exit(1)

    print("up-to-date")
    sys.exit(0)
