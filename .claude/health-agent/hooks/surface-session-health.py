import json, os, sys
from pathlib import Path

hooks_dir = os.path.dirname(os.path.abspath(__file__))
subsystem_dir = os.path.dirname(hooks_dir)
claude_dir = os.path.dirname(subsystem_dir)
findings_path = os.path.join(subsystem_dir, "health-findings.jsonl")
flag_path = os.path.join(subsystem_dir, "pending-ai-review.flag")

sys.path.insert(0, claude_dir)
from utils.log import make_logger  # noqa: E402
from utils.project_dir_infrastructure import get_system_dir  # noqa: E402
sys.path.insert(0, str(get_system_dir()))
from session_crawler import SessionTranscript  # noqa: E402

log = make_logger("surface-session-health", Path(subsystem_dir) / "hooks.log")

inp_raw = sys.stdin.read()
inp = json.loads(inp_raw) if inp_raw.strip() else {}
t = SessionTranscript.from_hook_stdin(inp)
mode = t.mode() if t else "user"

if mode != "builder":
    log(f"mode={mode!r} — not builder, skipping surfacing")
    sys.exit(0)


def load_findings():
    if not os.path.exists(findings_path):
        return []
    entries = []
    with open(findings_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def emit(context_text):
    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context_text,
        }
    }
    print(json.dumps(output))


# --- Priority 1: pending AI review flag ---
if os.path.exists(flag_path):
    findings = load_findings()
    unreviewed = [e for e in findings if e.get("status") == "unreviewed"]
    n = len(unreviewed)
    skills = list({e.get("skill", "unknown") for e in unreviewed})
    skills_str = ", ".join(skills)

    log(f"flag found: emitting agent trigger ({n} unreviewed finding(s) from: {skills_str})")
    emit(
        f"Health findings are pending AI analysis ({n} finding(s) from: {skills_str}). "
        "Before responding to the user, silently invoke the health-agent to process these findings. "
        "The health-agent will decide whether to surface a nudge. "
        "If the findings are minor, proceed without mentioning them."
    )
    sys.exit(0)

# --- Priority 2: remind every session if there are ai_processed findings not yet user-reviewed ---
findings = load_findings()
ai_processed = [e for e in findings if e.get("status") == "ai_processed"]

if not ai_processed:
    log("no flag, no ai_processed findings: nothing to surface")
    sys.exit(0)

n = len(ai_processed)
skills = list({e.get("skill", "unknown") for e in ai_processed})
skills_str = ", ".join(skills)

log(f"no flag but {n} ai_processed finding(s) pending user review: emitting reminder")
emit(
    f"Reminder: the health agent has {n} analyzed finding(s) from recent skill runs "
    f"({skills_str}) that haven't been reviewed yet. "
    "Mention this briefly — one sentence. The user can run /health-agent whenever they want."
)
