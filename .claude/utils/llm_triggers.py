import os
import subprocess


def call_isolated(prompt, model, recursion_guard=False):
    """Spawn a fresh `claude -p` subprocess with no session context."""
    env = os.environ.copy()
    if recursion_guard:
        env["HOOK_RECURSION_GUARD"] = "1"
    result = subprocess.run(
        ["claude", "-p", "--model", model, prompt],
        capture_output=True, text=True, timeout=300, env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude exited {result.returncode}: {result.stderr.strip()}")
    return result.stdout.strip()


def call_gemini(prompt: str, model: str) -> str:
    """Call Gemini with a plain text prompt. Requires GOOGLE_API_KEY in environment."""
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "gemini"))
    from gemini import call_gemini as _call
    return _call(prompt, model)


def call_gemini_video(url: str, prompt: str, model: str) -> str:
    """Call Gemini with a YouTube URL + text prompt. Requires GOOGLE_API_KEY in environment."""
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "gemini"))
    from gemini import call_gemini_video as _call
    return _call(url, prompt, model)
