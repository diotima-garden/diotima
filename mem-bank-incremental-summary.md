# mem-bank: incremental summaries on resume

## Problem

When a session is closed and resumed (via `/compact` mid-session or explicit `claude --resume`),
the hook fires again and creates a new job with the **full transcript**. The resulting summary
repeats everything already captured in the previous entry — the new content may be a single
exchange, but the summary looks identical to the prior one.

## Root cause

`small-bank.py` builds the summary prompt from `collect_user_prompts(events)` and
`last_n_assistant_responses(events)` over **all** events. It has no concept of "what was
already summarized".

## Proposed fix

### Data: store `resume_from` in the job

In `small-bank.py`, when creating a new job for a session that already has a **processed**
job targeting the same `target`:

```python
# find the latest processed job for this (session_id, target)
prev = max(
    (j for j in existing
     if j["session_id"] == session_id
     and j["target"] == str(target)
     and j.get("processed")),
    key=lambda j: j["created_at"],
    default=None,
)
resume_from = prev["created_at"] if prev else None
new_job["resume_from"] = resume_from   # ISO string or None
```

### Filtering: slice events by timestamp

Events in the JSONL transcript each carry a `timestamp` field (ISO 8601, UTC):

```python
{'parentUuid': ..., 'type': ..., 'message': ..., 'uuid': ..., 'timestamp': '2026-07-08T18:59:28.000Z', 'sessionId': ...}
```

In `collect_user_prompts` and `last_n_assistant_responses`, accept an optional `after` param:

```python
def collect_user_prompts(events, after=None):
    for ev in events:
        if after and ev.get("timestamp", "") <= after:
            continue
        ...
```

Pass `job.get("resume_from")` as `after` when building the prompt in the worker.

### Prompt hint

Add a sentence to the summary prompt when `resume_from` is set:

```
- This is a RESUMED session. Summarize only what happened AFTER the previous summary
  (events from {resume_from} onward). Do not repeat what was already captured.
```

## Edge cases

- **First job for a session**: `resume_from=None` → full transcript, current behaviour.
- **Compact within a session**: same session_id fires twice; the second job gets
  `resume_from` = first job's `created_at`. Only the post-compact exchanges are summarised.
- **`claude --resume`**: creates a new session_id entirely → `resume_from=None`, full
  summary of that resumed session (correct, it starts fresh).
- **Timestamp comparison**: job `created_at` is local ISO (no Z); event `timestamp` is UTC
  with Z. Use string comparison only if you normalize both to the same format first, or
  parse to datetime objects with `fromisoformat` (Python 3.11+ handles the Z suffix).

## Files to touch

| File | Change |
|---|---|
| `.claude/mem-bank/small-bank.py` | Populate `resume_from` in new job dict |
| `.claude/mem-bank/small-job-worker.py` | Pass `resume_from` to prompt-building helpers |
| `.claude/mem-bank/small-bank.py` | Filter `collect_user_prompts` / `last_n_assistant_responses` by timestamp |
