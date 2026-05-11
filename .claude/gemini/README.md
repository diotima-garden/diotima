# Gemini Subsystem

Provides `call_gemini` and `call_gemini_video` to the rest of the project.
Callers use these via `utils/llm_triggers.py` and are unaware of this directory.

## Setup

**Create the venv and install dependencies (one-time):**
```
python3 -m venv .claude/gemini/.venv
.claude/gemini/.venv/bin/pip install google-genai
```

The venv is gitignored — run these commands after cloning or on a fresh machine.

## Environment

Set `GOOGLE_API_KEY` in your shell before invoking any skill that calls Gemini.
Get a key at https://aistudio.google.com/apikey (free tier available).

## Files

| File | Role |
|---|---|
| `gemini.py` | Public API — `call_gemini`, `call_gemini_video`, `list_models`, `probe_model` |
| `_worker.py` | Private — runs under `.venv/bin/python3`, performs the actual `google.genai` calls |
| `info.py` | CLI — inspect available models and probe availability from the shell |

## Checking available models

```bash
# List all generateContent-capable models
python3 .claude/gemini/info.py --list

# List + probe each model for availability (ok / rate_limited / error)
python3 .claude/gemini/info.py

# Probe a single model
python3 .claude/gemini/info.py --probe models/gemini-2.0-flash
```

**Note:** There is no API-key-accessible quota endpoint in the Google GenAI API.
`probe_model` detects availability by sending a minimal request — a 429 means the
model has no remaining free-tier allocation (or billing isn't enabled). Exact quota
counts are only visible in Google AI Studio or via the Cloud Quotas API (requires OAuth).
