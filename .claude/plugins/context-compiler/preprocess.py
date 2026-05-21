#!/usr/bin/env python3
"""
Context Compiler — preprocessor.

Resolves #include directives recursively, deduplicating by canonical path.

Usage:
    python3 .claude/plugins/context-compiler/preprocess.py <entry-file> [output-file]

    If output-file is omitted, prints to stdout.

Directive syntax (must be the entire line, no leading whitespace):
    #include <path>

Path resolution:
    - Starts with . or .. → relative to the file containing the directive
    - Otherwise          → relative to project root (cwd)

Guarantees:
    - Each file is included at most once (keyed by canonical resolved path).
    - Circular includes are detected and reported as errors.
"""
import sys
import pathlib
from include_graph import resolve_include_path


def preprocess(
    entry: pathlib.Path,
    project_root: pathlib.Path,
    included: set[pathlib.Path],
    in_progress: set[pathlib.Path],
) -> str:
    resolved = entry.resolve()

    if resolved in in_progress:
        raise ValueError(f"Circular include: {entry}")
    if resolved in included:
        return ""
    if not resolved.exists():
        raise FileNotFoundError(f"File not found: {entry}")

    included.add(resolved)
    in_progress.add(resolved)

    lines = resolved.read_text().splitlines(keepends=True)
    parts: list[str] = []

    for line in lines:
        bare = line.rstrip("\r\n")
        if bare.startswith("#include "):
            path_str = bare[len("#include "):].strip()
            child = resolve_include_path(path_str, resolved, project_root)
            expansion = preprocess(child, project_root, included, in_progress)
            if expansion:
                parts.append(expansion)
                if not expansion.endswith("\n"):
                    parts.append("\n")
        else:
            parts.append(line)

    in_progress.discard(resolved)
    return "".join(parts)


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <entry-file> [output-file]", file=sys.stderr)
        sys.exit(2)

    entry = pathlib.Path(sys.argv[1])
    output_file = pathlib.Path(sys.argv[2]) if len(sys.argv) >= 3 else None
    project_root = pathlib.Path.cwd()

    try:
        result = preprocess(entry, project_root, set(), set())
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(result)
        print(f"✓ {entry} → {output_file}", file=sys.stderr)
    else:
        sys.stdout.write(result)


if __name__ == "__main__":
    main()
