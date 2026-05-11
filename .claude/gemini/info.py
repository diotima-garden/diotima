#!/usr/bin/env python3
"""
Inspect available Gemini models and their availability under your API key.

Usage:
    python3 .claude/gemini/info.py --list              # list all generateContent models
    python3 .claude/gemini/info.py --probe <model>     # probe one model
    python3 .claude/gemini/info.py --probe --all       # probe all listed models
"""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from utils.llm_triggers import list_gemini_models, probe_gemini_model

_QUOTA_LABELS = {
    "PerDay": "daily-req",
    "InputTokens": "rpm-tokens",
    "PerMinute": "rpm-req",
}


def _short_violations(violations: list[str]) -> str:
    labels = set()
    for v in violations:
        for key, label in _QUOTA_LABELS.items():
            if key in v:
                labels.add(label)
                break
        else:
            labels.add(v[:30])
    return ", ".join(sorted(labels))


def cmd_list():
    models = list_gemini_models()
    print(f"{'Model':<50} Display name")
    print("-" * 80)
    for m in models:
        print(f"{m['name']:<50} {m.get('display_name', '')}")
    print(f"\n{len(models)} models support generateContent")


def cmd_probe_one(model: str):
    result = probe_gemini_model(model)
    print(f"model:       {result['model']}")
    print(f"status:      {result['status']}")
    if result.get("code"):
        print(f"code:        {result['code']}")
    if result.get("violations"):
        print(f"violations:  {_short_violations(result['violations'])}")
        print(f"retry_delay: {result.get('retry_delay', 'n/a')}")


def cmd_probe_all():
    models = list_gemini_models()
    print(f"{'Model':<50} {'Status':<14} Quota violations")
    print("-" * 95)
    for m in models:
        result = probe_gemini_model(m["name"])
        status = result["status"]
        vstr = _short_violations(result.get("violations", []))
        print(f"{m['name']:<50} {status:<14} {vstr}")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    elif args == ["--list"]:
        cmd_list()
    elif args[0] == "--probe" and len(args) == 2 and args[1] != "--all":
        cmd_probe_one(args[1])
    elif args == ["--probe", "--all"]:
        cmd_probe_all()
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
