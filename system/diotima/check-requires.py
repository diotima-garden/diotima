#!/usr/bin/env python3
"""
Preflight: does this node's effective requires: hold on this machine?

Exit 0 always, printing exactly one leading token — the caller branches on
that token, not the exit code, same convention as compiled-is-fresh.py.
Exit non-zero (with stderr) only for a genuine error: bad usage, or the
node directory not found.

Refusal attaches to operations, never to opening: this script belongs at
the top of a pipeline that actually needs a capability, not to any
grove-reading or -compiling step.

Precedence: any unsatisfied name wins over unknown ones — REQUIRES_UNSATISFIED
leads whenever it applies, with unknown names listed underneath as a notice.
An unnamed capability blocks nothing on its own (REQUIRES_UNKNOWN) — the
runtime cannot forever recognize every name a 2028 grove might declare.

Usage: python3 check-requires.py <node-dir>
"""
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR.parent.parent / "plugins" / "dafne"))
from manifest import requirements_with_provenance  # noqa: E402

sys.path.insert(0, str(_SCRIPT_DIR))
from capabilities import CAPABILITIES, installed_capabilities, missing_path  # noqa: E402

sys.path.insert(0, str(_SCRIPT_DIR.parent.parent / ".claude"))
from utils.project_dir_infrastructure import get_project_root  # noqa: E402


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("USAGE_ERROR: check-requires.py <node-dir>", file=sys.stderr)
        return 2

    node_dir = Path(argv[0])
    if not node_dir.is_dir():
        print(f"NODE_NOT_FOUND: {node_dir} — stop and report this.", file=sys.stderr)
        return 1

    project_dir = get_project_root()
    requirements = requirements_with_provenance(node_dir)

    if not requirements:
        print("REQUIRES_SATISFIED: no requirements declared — proceed.")
        return 0

    installed = installed_capabilities(project_dir)
    unsatisfied = [r for r in requirements if r.name in CAPABILITIES and r.name not in installed]
    unknown = [r for r in requirements if r.name not in CAPABILITIES]

    if unsatisfied:
        lines = []
        for req in unsatisfied:
            declared_by = ", ".join(str(p) for p in req.declared_by)
            lines.append(f"REQUIRES_UNSATISFIED: {node_dir} requires '{req.name}', which is not available here.")
            lines.append(f"  declared by {declared_by}")
            missing = missing_path(req.name, project_dir)
            if missing is not None:
                lines.append(f"  missing: {missing}")
            lines.append(f"  fix: set up '{req.name}' (see /onboard), or use a node that requires nothing.")
        if unknown:
            for req in unknown:
                declared_by = ", ".join(str(p) for p in req.declared_by)
                lines.append(f"REQUIRES_UNKNOWN: '{req.name}' (declared by {declared_by}) is not a failure — it blocks nothing.")
        lines.append("Stop and report this to the user — do not continue the pipeline.")
        print("\n".join(lines))
        return 0

    if unknown:
        lines = []
        for req in unknown:
            declared_by = ", ".join(str(p) for p in req.declared_by)
            lines.append(
                f"REQUIRES_UNKNOWN: {node_dir} requires '{req.name}', which this runtime has never heard of."
            )
            lines.append(f"  declared by {declared_by}")
        lines.append(
            "  This is not a failure — an unknown capability blocks nothing. Continue, "
            "and expect any step that needed it to be unavailable."
        )
        print("\n".join(lines))
        return 0

    names = ", ".join(r.name for r in requirements)
    print(f"REQUIRES_SATISFIED: {names} — proceed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
