#!/usr/bin/env python3
"""
Orchestrator — the launcher: everything `bin/diotima` used to do in bash.

`bin/diotima` is now a two-line shim that resolves this file and execs it.
The body moved here because it had stopped being glue: it resolves the
session's subject, derives two permission-bearing paths through
garden.py, and decides whether prompt suggestions are safe -- logic that
was the only untested piece of this machinery, and the only one that
could not be tested, bash having no test harness here.

Everything is a function over explicit arguments (cwd, environment)
rather than a read of the ambient process, so tests/test_launch.py can
pin the contract without a shell, a garden, or a running claude.

Ends in os.execvpe, never subprocess: this launches an interactive TUI,
and an extra process in the tree changes Ctrl-C delivery, TTY ownership
and exit-code propagation. The exec is load-bearing.

Usage: python3 launch.py [prompt]
"""
import os
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
import garden  # noqa: E402

PROJECT_ROOT = _SCRIPT_DIR.parent.parent


class UsageError(Exception):
    """A caller mistake worth a message, not a traceback."""


def resolve_subject(orig_cwd: Path, env: dict[str, str]) -> tuple[Path, bool]:
    """The session's subject -- one grove, or a garden of them -- and whether
    the caller was standing inside a grove when they launched.

    orig_cwd is passed in, and must be read before main() chdirs to the
    project root: being inside a grove is what tells us the caller meant
    that grove, and a resolved-later cwd would always be the project root.

    The second value is *how* the subject was reached, not what it is -- it
    is false for `DIOTIMA_GARDEN=<a grove>` even though that subject is one
    grove. Only the prompt-suggestion switch reads it, and only because that
    is the behaviour the bash this replaces had; the private grant asks
    is_grove(subject) instead and so is launch-mode independent. Worth
    revisiting: the two could reasonably be the same question.
    """
    if garden.is_grove(orig_cwd):
        return orig_cwd, True
    raw = env.get("DIOTIMA_GARDEN")
    if raw:
        return Path(raw).expanduser(), False
    return garden.default_garden(), False


def plugin_args(project_root: Path) -> list[str]:
    args: list[str] = []
    plugins_dir = project_root / "plugins"
    if not plugins_dir.is_dir():
        return args
    for child in sorted(plugins_dir.iterdir()):
        if (child / ".claude-plugin").is_dir():
            args += ["--plugin-dir", str(child)]
    return args


def private_read_rule(subject: Path) -> str:
    """The private layer lives outside every git repo
    (modes/meta/architect/private_layer.md), so a session reading it gets
    prompted per file, and orientation's whole promise of a findable private
    store degrades into friction. The path belongs to config.json, not to a
    user's settings file: an absolute `Read(//home/<user>/...)` rule would be
    dead on a fresh clone, so it is derived here through garden.py -- the one
    place config paths are read -- and never re-derived.

    A narrow read rule rather than a second --add-dir, deliberately:
    --add-dir would make the store part of the session's workspace, so an
    incidental project-wide grep or glob would pull private filenames and
    content into context unasked. That is exactly the disclosure orient.py's
    presence-only line (a path and a count, never a filename) exists to
    prevent. Read-on-demand is the sanctioned access; writes stay prompted.

    Scoped the same way --add-dir is, and from the same resolved subject: the
    grove's own private directory when the subject is a grove, the whole
    store when it is a garden of them. Private material is subject-only by
    design, so a session working in one grove gets no silent read of
    another's -- and `DIOTIMA_GARDEN=<a grove>` narrows the grant exactly as
    launching from inside the grove does.

    Double slash is the filesystem-absolute form for a path permission rule;
    the rule is inert, not an error, when the directory does not exist yet.
    """
    directory = garden.private_dir_for(subject) if garden.is_grove(subject) else garden.private_root()
    return f"Read(//{str(directory).lstrip('/')}/**)"


def prompt_from(argv: list[str]) -> str | None:
    """None for the no-argument TUI launch, else the one prompt argument.

    More than one argument is refused rather than joined. `claude` binds a
    single positional to its [prompt] and *silently drops the rest*, so
    forwarding "$@" turned `diotima do xyz now` into the prompt "do" with no
    warning -- the defect this replaces. Joining them would fix the
    truncation but buy a worse problem: an unquoted prompt is the shell's
    text, not ours, so `?` is a glob (a hard error under zsh's NOMATCH), an
    apostrophe opens a quote that is never closed, and `*`, `$`, `|` and `>`
    all act before this process exists. A prompt is therefore one quoted
    argument, and anything else is a usage error the caller can see.
    """
    if not argv:
        return None
    if len(argv) > 1:
        raise UsageError(
            f"a prompt must be one quoted argument (got {len(argv)}). "
            f"The claude CLI takes a single positional prompt and silently "
            f"drops the rest, and an unquoted prompt is mangled by the shell "
            f"before it reaches here.\n"
            f'  try: diotima "{" ".join(argv)}"'
        )
    return argv[0]


def claude_argv(project_root: Path, subject: Path, prompt: str | None) -> list[str]:
    args = ["claude"]
    args += plugin_args(project_root)
    args += ["--add-dir", str(subject)]
    args += ["--allowedTools", private_read_rule(subject)]
    if prompt is not None:
        # `--` before the caller's prompt: every flag built above
        # (--plugin-dir, --add-dir, --allowedTools) is variadic, so without a
        # terminator the prompt is collected as one more value of whichever
        # flag came last, and claude exits with "Input must be provided
        # either through stdin or as a prompt argument". Verified against the
        # real CLI, which accepts `--` and treats what follows as the prompt.
        args += ["--", prompt]
    return args


def session_env(env: dict[str, str], subject: Path, launched_in_grove: bool) -> dict[str, str]:
    """The exec'd process's environment. A copy: never the caller's own, which
    this process has no business mutating for whatever runs after claude.
    """
    out = dict(env)
    # DIOTIMA_GARDEN reused here as "the one directory this session's
    # SessionStart hook should look at" -- a grove if the caller was in one,
    # else the garden. Set on the exec'd process only; the caller's own
    # DIOTIMA_GARDEN, if they have one in their shell, is untouched.
    out["DIOTIMA_GARDEN"] = str(subject)
    if launched_in_grove:
        # Launched from inside a grove only. Such a session is work
        # *inside* that grove, and some groves are drills -- the input field's
        # Tab-accept ghost text would hand the practitioner a decent answer to
        # the very scenario they are there to answer themselves. Garden-wide
        # sessions are orchestration, not practice, and keep the suggestions.
        # The env var is read before any settings file, so this wins
        # regardless of user config.
        #
        # Blanket across all groves for now: the grove that actually knows
        # whether it is a drill has no way to say so until the DAFNE.md header
        # can carry it -- diotima-garden/dafne#1. Drop this in favour of the
        # manifest once that lands.
        out["CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION"] = "false"
    return out


def sync_groves(subject: Path) -> None:
    """Grove sync runs here, before the exec, and never inside the session:
    the mutation therefore happens outside any Claude Code session, which is
    why it needs no allow rule in .claude/settings.json (security.md's ban on
    whitelisting mutating git commands is about in-session calls, and the
    moment this CLI is invoked from inside one it stays prompted like any
    other).

    Nothing here may fail a launch -- the bash this replaces ran grove_sync.py
    under `|| true`, and that tolerance is a stated guarantee, not an
    accident. The import is inside the try for the same reason: a grove_sync
    that cannot even be imported must still leave the session startable.

    Scope comes from the environment, as it does for every other garden.py
    consumer, so it is set before the call rather than passed: grove_sync
    resolves its own subject and must see this session's, not the caller's.
    """
    os.environ["DIOTIMA_GARDEN"] = str(subject)
    try:
        import grove_sync
        grove_sync.main([])
    except Exception as e:
        print(f"diotima: grove sync skipped ({e})", file=sys.stderr)


def main(argv: list[str], *, orig_cwd: Path | None = None,
         env: dict[str, str] | None = None, exec_fn=os.execvpe) -> int:
    # Read before any chdir: this is what tells us whether the caller invoked
    # `diotima` from inside a grove.
    orig_cwd = orig_cwd if orig_cwd is not None else Path.cwd()
    env = env if env is not None else dict(os.environ)

    try:
        prompt = prompt_from(argv)
    except UsageError as e:
        print(f"diotima: {e}", file=sys.stderr)
        return 2

    subject, launched_in_grove = resolve_subject(orig_cwd, env)
    subject.mkdir(parents=True, exist_ok=True)

    # Claude Code only loads a project's .claude/settings.json (permissions,
    # hooks) when cwd is exactly that project's root -- master must stay cwd
    # for the session's tooling to be there, regardless of which grove or
    # garden the session's subject is. This runs in a child process of the
    # caller's shell, so the chdir never propagates back to it and no state
    # needs saving to "return" the caller to their own cwd.
    os.chdir(PROJECT_ROOT)

    sync_groves(subject)

    args = claude_argv(PROJECT_ROOT, subject, prompt)
    exec_fn("claude", args, session_env(env, subject, launched_in_grove))

    # Only reached when the exec *failed* -- claude missing from PATH, or not
    # executable; os.execvpe does not return otherwise. Falling through to a 0
    # here would make `diotima` exit successfully having launched nothing, and
    # with no prompt given it would print nothing either. 127 and a line on
    # stderr is what the shell reported for the `exec claude` this replaces.
    print("diotima: could not exec `claude` -- is the CLI on your PATH?",
          file=sys.stderr)
    return 127


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
