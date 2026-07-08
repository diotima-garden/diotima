import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

WORKER_DIR = Path(__file__).resolve().parent
CLAUDE_DIR = WORKER_DIR.parent
JOBS_DUMP_PATH = WORKER_DIR / "small-jobs.json"
LOG_PATH = WORKER_DIR / "mem-bank.log"

sys.path.insert(0, str(WORKER_DIR))
sys.path.insert(0, str(CLAUDE_DIR))
from utils.log import make_logger  # noqa: E402
from utils.llm_triggers import call_isolated  # noqa: E402

log = make_logger("small-job-worker", LOG_PATH)


def parse_args(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--session-id", default="")
    return p.parse_args(argv)


def append_to_target(target, summary, session_id):
    target.parent.mkdir(parents=True, exist_ok=True)
    short_id = (session_id or "unknown")[:6]
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    block = f"## {stamp} (session {short_id})\n{summary}\n\n"
    with open(target, "a") as f:
        f.write(block)


def load_jobs():
    try:
        return json.loads(JOBS_DUMP_PATH.read_text())
    except Exception as e:
        log(f"failed to read jobs: {e}")
        return []


def save_jobs(jobs):
    JOBS_DUMP_PATH.write_text(json.dumps(jobs, indent=2))


def main(argv):
    try:
        args = parse_args(argv)
    except SystemExit:
        log("argparse failed")
        return 0

    jobs = load_jobs()
    if not jobs:
        log("no jobs found")
        return 0

    if args.session_id:
        targets = [j for j in jobs if j.get("session_id") == args.session_id]
        if not targets:
            log(f"no jobs found for session={args.session_id}")
            return 0
    else:
        targets = [j for j in jobs if not j.get("processed")]
        if not targets:
            log("no unprocessed jobs")
            return 0

    session_ids = list(dict.fromkeys(j.get("session_id", "unknown") for j in targets))
    log(f"worker started: pid={os.getpid()} sessions={session_ids} jobs={len(targets)}")

    for job in targets:
        target = Path(job["target"])
        prompt = job["prompt"]
        session_id = job.get("session_id", "")

        log(f"processing: session={session_id} target={target}")

        try:
            summary = call_isolated(prompt, "haiku")
        except Exception as e:
            log(f"claude call failed for {target}: {e}")
            continue

        if not summary:
            log(f"claude returned empty for {target}")
            continue

        log(f"claude response ({len(summary)} chars): {summary!r}")

        try:
            append_to_target(target, summary, session_id)
            log(f"appended summary to {target}")
        except Exception as e:
            log(f"append failed for {target}: {e}")
            continue

        job["processed"] = True
        job["processed_at"] = datetime.now().isoformat(timespec="seconds")
        save_jobs(jobs)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
