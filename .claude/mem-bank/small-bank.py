import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HOOK_DIR = Path(__file__).resolve().parent
CLAUDE_DIR = HOOK_DIR.parent
JOBS_DUMP_PATH = HOOK_DIR / "small-jobs.json"
LOG_PATH = HOOK_DIR / "mem-bank.log"
WORKER_PATH = HOOK_DIR / "small-job-worker.py"

sys.path.insert(0, str(HOOK_DIR))
sys.path.insert(0, str(CLAUDE_DIR))
from utils.project_dir_infrastructure import get_system_dir  # noqa: E402
sys.path.insert(0, str(get_system_dir()))
from session_crawler import SessionTranscript, extract_text  # noqa: E402
from registry import load_banks, bank_effective_patterns, bank_small_bank_path, bank_capture_prompt  # noqa: E402
from utils.log import make_logger  # noqa: E402

log = make_logger("small-bank", LOG_PATH)


def parse_args(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--subscriptions")
    return p.parse_args(argv)


def collect_user_prompts(events):
    prompts = []
    for ev in events:
        if ev.get("type") != "user":
            continue
        text = extract_text(ev.get("message", {}).get("content", "")).strip()
        if text:
            prompts.append(text)
    return prompts


def last_n_assistant_responses(events, n=3):
    out = []
    for ev in reversed(events):
        if ev.get("type") != "assistant":
            continue
        text = extract_text(ev.get("message", {}).get("content", "")).strip()
        if text:
            out.append(text)
            if len(out) >= n:
                break
    return list(reversed(out))


def git_status(cwd):
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=cwd, capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip()
    except Exception as e:
        return f"(git status failed: {e})"


RESPONSE_CAP = 3000
PROMPT_CAP = 3000

SYSTEM_REMINDER_RE = re.compile(
    r"<system-reminder\b[^>]*>.*?</system-reminder>",
    re.DOTALL | re.IGNORECASE,
)
COMMAND_NAME_RE = re.compile(
    r"<command-name>([^<]+)</command-name>",
    re.IGNORECASE,
)
TASK_NOTIFICATION_RE = re.compile(
    r"<task-notification\b[^>]*>.*?</task-notification>",
    re.DOTALL | re.IGNORECASE,
)
TASK_SUMMARY_RE = re.compile(
    r"<summary>([^<]+)</summary>",
    re.IGNORECASE,
)


def _format_task_notification(block):
    m = TASK_SUMMARY_RE.search(block)
    if m:
        return f"[task-notification: {m.group(1).strip()}]"
    return "[task-notification]"


def _elide(text, cap):
    if len(text) <= cap:
        return text
    head = text[:1000]
    tail = text[-300:]
    elided = len(text) - len(head) - len(tail)
    return f"{head}\n…[elided {elided} chars]…\n{tail}"


def clean_user_prompt(text):
    m = COMMAND_NAME_RE.search(text)
    if m:
        return f"[invoked /{m.group(1).strip()}]"
    text = TASK_NOTIFICATION_RE.sub(lambda mm: _format_task_notification(mm.group(0)), text)
    return _elide(SYSTEM_REMINDER_RE.sub("", text).strip(), PROMPT_CAP)


def slim_assistant(text):
    return _elide(SYSTEM_REMINDER_RE.sub("", text).strip(), RESPONSE_CAP)


def build_prompt(prompts, last_responses, gstatus, bank_prompt=""):
    cleaned_prompts = [clean_user_prompt(p) for p in prompts]
    cleaned_prompts = [p for p in cleaned_prompts if p]
    slim_responses = [slim_assistant(r) for r in last_responses]
    numbered = "\n".join(f"{i+1}. {p}" for i, p in enumerate(cleaned_prompts))
    total = len(slim_responses)
    rendered_responses = "\n\n".join(
        f"[{i+1}/{total}] {r}" for i, r in enumerate(slim_responses)
    )

    return (
        "You are summarizing a session for an append-only project memory file.\n\n"
        "STRICT RULES:\n"
        "- Do NOT open any files.\n"
        "- Do NOT use any tools.\n"
        "- Summarize only from the text provided below.\n"
        "- Output 2-4 plain prose sentences. No headings, no lists, no code fences.\n"
        "- Focus on what changed, what is still open, and where to resume.\n"
        f"- {bank_prompt}\n\n"
        f"--- USER PROMPTS ---\n{numbered}\n\n"
        f"--- LAST ASSISTANT RESPONSES (chronological, oldest first) ---\n{rendered_responses}\n\n"
        #f"--- GIT STATUS ---\n{gstatus}\n"
    )


def spawn_worker():
    cmd = [sys.executable, str(WORKER_PATH)]
    devnull_r = open(os.devnull, "rb")
    devnull_w = open(os.devnull, "ab")
    env = os.environ.copy()
    env["HOOK_RECURSION_GUARD"] = "1"
    proc = subprocess.Popen(
        cmd,
        stdin=devnull_r,
        stdout=devnull_w,
        stderr=devnull_w,
        start_new_session=True,
        close_fds=True,
        env=env,
    )
    log(f"detached worker spawned pid={proc.pid}")


def run_hook(args):
    try:
        raw = sys.stdin.read()
        inp = json.loads(raw) if raw.strip() else {}
    except Exception as e:
        log(f"failed to parse stdin: {e}")
        return 0

    if os.environ.get("HOOK_RECURSION_GUARD") == "1":
        log("recursion guard tripped (called from child claude -p) — skipping")
        return 0

    transcript_path = inp.get("transcript_path")
    session_id = inp.get("session_id", "")
    cwd = inp.get("cwd") or os.getcwd()

    if not transcript_path or not os.path.exists(transcript_path):
        log(f"missing transcript_path: {transcript_path}")
        return 0

    if not args.subscriptions:
        log("hook mode requires --subscriptions")
        return 0

    log(
        f"called: subscriptions={args.subscriptions!r} "
        f"transcript={transcript_path} session={session_id} cwd={cwd}"
    )

    try:
        banks = load_banks(args.subscriptions, cwd)
    except Exception as e:
        log(f"failed to load subscriptions: {e}")
        return 0

    transcript = SessionTranscript(transcript_path)

    try:
        events = transcript.events
        prompts = collect_user_prompts(events)
        last_responses = last_n_assistant_responses(events, n=3)
        gstatus = git_status(cwd)
    except Exception as e:
        log(f"hook failed building transcript data: {e}")
        return 0

    new_jobs = []
    for bank in banks:
        name = bank.get("name", "?")
        pattern_strs = bank_effective_patterns(bank)
        try:
            patterns = [re.compile(s) for s in pattern_strs]
        except re.error as e:
            log(f"bad pattern for bank {name!r}: {e}")
            continue
        if transcript.matched_any(patterns):
            target = bank_small_bank_path(bank, cwd)
            bp = bank_capture_prompt(bank, cwd)
            prompt = build_prompt(prompts, last_responses, gstatus, bp)
            new_jobs.append({
                "session_id": session_id,
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "target": str(target),
                "prompt": prompt,
                "processed": False,
                "processed_at": None,
            })
            log(f"bank matched: {name!r} -> {target} (bank-prompt: {'yes' if bp else 'no'})")

    if not new_jobs:
        log("no bank matched in transcript — skipping")
        return 0

    try:
        existing = json.loads(JOBS_DUMP_PATH.read_text()) if JOBS_DUMP_PATH.exists() else []
    except Exception:
        existing = []

    all_jobs = list(existing)
    for new_job in new_jobs:
        replaced = False
        for i, ej in enumerate(all_jobs):
            if (ej.get("session_id") == new_job["session_id"]
                    and ej.get("target") == new_job["target"]
                    and not ej.get("processed")):
                all_jobs[i] = new_job
                replaced = True
                log(f"replaced unprocessed job for session={new_job['session_id'][:8]}...")
                break
        if not replaced:
            all_jobs.append(new_job)

    try:
        JOBS_DUMP_PATH.write_text(json.dumps(all_jobs, indent=2))
        log(f"jobs written: {len(new_jobs)} bank(s), session={session_id}")
        spawn_worker()
    except Exception as e:
        log(f"hook failed before spawn: {e}")
        return 0

    return 0


def main(argv):
    try:
        args = parse_args(argv)
    except SystemExit:
        log("argparse failed")
        return 0

    return run_hook(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
