import json, os, sys
from datetime import datetime, timezone

hooks_dir = os.path.dirname(os.path.abspath(__file__))
subsystem_dir = os.path.dirname(hooks_dir)
claude_dir = os.path.dirname(subsystem_dir)
summary_path = os.path.join(subsystem_dir, "run-summary.json")
events_path = os.path.join(subsystem_dir, "permission-events.jsonl")
findings_path = os.path.join(subsystem_dir, "health-findings.jsonl")
flag_path = os.path.join(subsystem_dir, "pending-ai-review.flag")
log_path = os.path.join(subsystem_dir, "hooks.log")

sys.path.insert(0, subsystem_dir)
sys.path.insert(0, claude_dir)
from detectors import bash_chaining, git_policy, destructive_ops
from detectors import whitelist_gap, skill_circumvention, refactoring_rot
from utils.log import make_logger  # noqa: E402
from utils.project_dir_infrastructure import get_system_dir  # noqa: E402
sys.path.insert(0, str(get_system_dir()))
from session_crawler import SessionTranscript  # noqa: E402

log = make_logger("detect-health-issues", log_path)

ALL_DETECTORS = [
    bash_chaining,
    git_policy,
    destructive_ops,
    whitelist_gap,
    skill_circumvention,
    refactoring_rot,
]


def parse_utc(ts):
    ts = ts.rstrip("Z")
    return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)


def _is_internal(detail):
    """Return True if this permission event is from .claude/ infrastructure."""
    if not detail:
        return False
    cwd = os.environ.get("CLAUDE_CWD", os.getcwd())
    normalized = os.path.relpath(detail, cwd) if os.path.isabs(detail) else detail
    return "/.claude/" in normalized or normalized.startswith(".claude/")


def _build_context(summary):
    """Parse transcript and sidecar files into a unified context dict."""
    started_at = parse_utc(summary["started_at"])
    transcript_path = summary.get("transcript_path", "")

    tool_uses = []
    tool_results = []

    if transcript_path and os.path.exists(transcript_path):
        with open(transcript_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts = event.get("timestamp")
                if ts and parse_utc(ts) < started_at:
                    continue

                # Extract tool_use blocks from assistant messages
                if event.get("type") == "assistant":
                    msg = event.get("message") or {}
                    for block in msg.get("content") or []:
                        if isinstance(block, dict) and block.get("type") == "tool_use":
                            tool_uses.append(block)

                # Collect tool_result events
                if event.get("type") == "tool_result":
                    tool_results.append(event)

    permission_events = []
    if os.path.exists(events_path):
        with open(events_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if ev.get("transcript_path") != transcript_path:
                    continue
                ev_ts = ev.get("timestamp", "")
                if ev_ts and parse_utc(ev_ts) < started_at:
                    continue
                detail = ev.get("detail") or ev.get("tool_name", "")
                if _is_internal(detail):
                    continue
                permission_events.append(ev)

    return {
        "skill": summary.get("skill", "unknown"),
        "started_at": started_at,
        "transcript_path": transcript_path,
        "tool_uses": tool_uses,
        "tool_results": tool_results,
        "permission_events": permission_events,
        "claude_dir": claude_dir,
    }


def analyze(summary):
    skill = summary.get("skill", "unknown")
    ctx = _build_context(summary)

    findings = []

    # Legacy: tool errors from transcript (keep existing signal)
    for result in ctx["tool_results"]:
        if result.get("is_error"):
            content = result.get("content", "")
            if isinstance(content, list):
                content = " ".join(
                    c.get("text", "") for c in content if isinstance(c, dict)
                )
            findings.append({
                "id": f"{skill}-error-{datetime.utcnow().isoformat()}Z",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "skill": skill,
                "type": "tool_error",
                "rule": "tool_error",
                "severity": "warning",
                "error": content[:300],
                "evidence": content[:300],
                "suggested_fix": None,
                "status": "unreviewed",
            })

    # Detector modules
    for detector in ALL_DETECTORS:
        try:
            for det in detector.detect(ctx):
                findings.append({
                    "id": f"{skill}-{det['rule']}-{datetime.utcnow().isoformat()}Z",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "skill": skill,
                    "type": det["severity"],
                    "rule": det["rule"],
                    "severity": det["severity"],
                    "error": det["evidence"],
                    "evidence": det["evidence"],
                    "suggested_fix": det.get("suggested_fix"),
                    "status": "unreviewed",
                })
        except Exception as e:
            # Detector failures must not crash the hook
            findings.append({
                "id": f"{skill}-detector-error-{datetime.utcnow().isoformat()}Z",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "skill": skill,
                "type": "warning",
                "rule": f"detector_error_{detector.__name__.split('.')[-1]}",
                "severity": "warning",
                "error": str(e),
                "evidence": str(e),
                "suggested_fix": None,
                "status": "unreviewed",
            })

    if not findings:
        log(f"analyzed skill={skill}: no findings")
        return

    log(f"analyzed skill={skill}: {len(findings)} finding(s) → {[f['rule'] for f in findings]}")

    with open(findings_path, "a") as f:
        for finding in findings:
            f.write(json.dumps(finding) + "\n")

    # Signal that AI review is pending
    with open(flag_path, "w") as f:
        f.write(datetime.utcnow().isoformat() + "Z\n")


def load_summary():
    if not os.path.exists(summary_path):
        return None
    try:
        with open(summary_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def mark_analyzed(summary):
    summary["analyzed_at"] = datetime.utcnow().isoformat() + "Z"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)


if __name__ == "__main__":
    sys.stdin.read()  # consume stdin (hook event data; not needed for detection)

    summary = load_summary()
    if not summary:
        log("skip: no run-summary.json")
        sys.exit(0)
    if summary.get("analyzed_at"):
        log(f"skip: skill={summary.get('skill')} already analyzed at {summary['analyzed_at']}")
        sys.exit(0)
    if not summary.get("started_at"):
        log("skip: run-summary has no started_at")
        sys.exit(0)

    transcript_path = summary.get("transcript_path", "")
    if transcript_path and os.path.exists(transcript_path):
        try:
            mode = SessionTranscript(transcript_path).mode()
        except Exception:
            mode = "user"
        if mode != "user":
            log(f"mode={mode!r} — skipping detection")
            mark_analyzed(summary)
            sys.exit(0)

    log(f"triggered for skill={summary.get('skill')} started_at={summary.get('started_at')}")
    analyze(summary)
    mark_analyzed(summary)
