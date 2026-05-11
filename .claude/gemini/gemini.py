import subprocess
import pathlib

_HERE = pathlib.Path(__file__).parent
_VENV_PYTHON = _HERE / ".venv" / "bin" / "python3"
_WORKER = _HERE / "_worker.py"


def _run(extra_args: list, prompt: str) -> str:
    result = subprocess.run(
        [str(_VENV_PYTHON), str(_WORKER)] + extra_args,
        input=prompt,
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gemini worker exited {result.returncode}: {result.stderr.strip()}")
    return result.stdout.strip()


def call_gemini(prompt: str, model: str) -> str:
    return _run(["text", model], prompt)


def call_gemini_video(url: str, prompt: str, model: str) -> str:
    return _run(["video", model, url], prompt)


def list_models() -> list[dict]:
    """Return all generateContent-capable models for the current API key."""
    import json
    return json.loads(_run(["list"], ""))


def probe_model(model: str) -> dict:
    """Probe a model with a minimal request. Returns {status, model, ...}.

    status values:
      "ok"           — model responded normally
      "rate_limited" — 429; quota exhausted or no free-tier allocation
      "error"        — other API error
    """
    import json
    return json.loads(_run(["probe", model], "hi"))
