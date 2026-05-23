# session_crawler

Reads and queries Claude Code session transcripts (JSONL). Provides mode detection, pattern matching, and a hook-context factory — the primary interface for anything that needs to inspect session history.

## Public API

```python
from session_crawler import SessionTranscript

t = SessionTranscript("/path/to/session.jsonl")
t.mode()            # 'architect' | 'builder' | 'user'
t.modes_seen()      # set — all modes observed (useful for multi-mode sessions)
t.matched_any(pats) # bool
t.matches(pats)     # set of matched pattern strings

# In hooks: build from parsed stdin
t = SessionTranscript.from_hook_stdin(json.loads(sys.stdin.read()))
if t:
    mode = t.mode()
```

## Module-level shims (backward compatible)

```python
from session_crawler import read_transcript, detect_mode, matched_any, matches
```

These exist only for callers not yet migrated to the class API. See `tests/test_crawler.py` → `TestLegacyShimParity` for the parity suite used to validate safe removal.

## Tests

```
tests/
  fixtures/           JSONL transcripts versioned as test data
  test_crawler.py     Class tests + legacy parity suite
```

**Run:**
```bash
session_crawler/.venv/bin/python3 -m pytest session_crawler/tests/ -v
```

## Setup

**Create the venv and install dependencies (one-time):**
```
python3 -m venv session_crawler/.venv
session_crawler/.venv/bin/pip install pytest
```

The venv is gitignored — run these commands after cloning or on a fresh machine.
