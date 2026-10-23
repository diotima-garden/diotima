"""
launch.py — the launcher body that used to be bash in bin/diotima.

What is worth pinning is what the shell could silently get wrong: which
directory becomes the subject, that the prompt reaches claude intact or
not at all, that the private grant is scoped to the subject, and that
nothing in grove sync can stop a session from starting.

No test execs anything: main() takes exec_fn, so the argument vector and
the environment are inspected instead of launched.
"""
import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import garden  # noqa: E402
import launch  # noqa: E402


@pytest.fixture(autouse=True)
def keep_cwd(monkeypatch, tmp_path):
    """main() chdirs to the project root, as the real launch must. Restore it
    so the suite's own cwd is not a side effect of test order."""
    import os
    before = Path.cwd()
    yield
    os.chdir(before)


@pytest.fixture
def stub_grove_sync(monkeypatch):
    """A grove_sync whose main() is ours. sync_groves imports it lazily and
    sets DIOTIMA_GARDEN in the real environment, so that is pinned here too
    and restored by monkeypatch."""
    monkeypatch.setenv("DIOTIMA_GARDEN", "unset-by-fixture")

    def install(main):
        module = types.ModuleType("grove_sync")
        module.main = main
        monkeypatch.setitem(sys.modules, "grove_sync", module)
    return install


@pytest.fixture
def exec_spy(monkeypatch):
    """Records the exec that would have happened, and keeps grove sync out of
    every test but the ones about it -- it walks the subject with git."""
    calls = []
    monkeypatch.setattr(launch, "sync_groves", lambda subject: None)
    return calls


class Execd(Exception):
    """A successful exec never returns; the spy models that by raising."""


def spy(calls):
    def exec_fn(file, args, env):
        calls.append((file, args, env))
        raise Execd
    return exec_fn


def run(exec_spy, argv, cwd, env=None):
    with pytest.raises(Execd):
        launch.main(argv, orig_cwd=cwd, env=dict(env or {}),
                    exec_fn=spy(exec_spy))
    assert len(exec_spy) == 1
    file, args, env_out = exec_spy[0]
    assert file == "claude"
    assert args[0] == "claude"
    return args, env_out


def make_grove(path: Path) -> Path:
    path.mkdir(parents=True)
    (path / "DAFNE.md").write_text("# fixture grove\n")
    return path


# --- the prompt ------------------------------------------------------------

def test_no_argument_passes_no_prompt(exec_spy, tmp_path):
    args, _ = run(exec_spy, [], make_grove(tmp_path / "g"))
    assert "--" not in args


def test_one_quoted_argument_is_the_prompt(exec_spy, tmp_path):
    args, _ = run(exec_spy, ["let's do xyz"], make_grove(tmp_path / "g"))
    # The terminator matters: every flag before it is variadic, so an
    # unterminated prompt is swallowed as one more value of the last one.
    assert args[-2:] == ["--", "let's do xyz"]


def test_several_arguments_are_refused_not_joined(exec_spy, tmp_path, capsys):
    """The defect this replaces: claude binds one positional to [prompt] and
    drops the rest, so `diotima do xyz now` ran with the prompt "do" and said
    nothing. Refused rather than joined -- an unquoted prompt is mangled by
    the shell before this process exists."""
    code = launch.main(["do", "xyz", "now"], orig_cwd=make_grove(tmp_path / "g"),
                       env={}, exec_fn=spy(exec_spy))
    assert code == 2
    assert exec_spy == []
    err = capsys.readouterr().err
    assert "one quoted argument" in err
    assert '"do xyz now"' in err


# --- the subject -----------------------------------------------------------

def test_cwd_inside_a_grove_makes_that_grove_the_subject(exec_spy, tmp_path):
    grove = make_grove(tmp_path / "garden" / "social-dynamics")
    args, env = run(exec_spy, [], grove, {"DIOTIMA_GARDEN": str(tmp_path / "garden")})
    assert args[args.index("--add-dir") + 1] == str(grove)
    # The hook reads this to know what the session is about; cwd wins over an
    # inherited garden-wide value.
    assert env["DIOTIMA_GARDEN"] == str(grove)


def test_env_names_the_subject_when_cwd_is_not_a_grove(exec_spy, tmp_path):
    garden_dir = tmp_path / "garden"
    make_grove(garden_dir / "social-dynamics")
    args, env = run(exec_spy, [], tmp_path / "elsewhere", {"DIOTIMA_GARDEN": str(garden_dir)})
    assert args[args.index("--add-dir") + 1] == str(garden_dir)
    assert env["DIOTIMA_GARDEN"] == str(garden_dir)


def test_subject_directory_is_created(exec_spy, tmp_path):
    subject = tmp_path / "garden-not-yet"
    run(exec_spy, [], tmp_path / "elsewhere", {"DIOTIMA_GARDEN": str(subject)})
    assert subject.is_dir()


def test_tilde_in_the_env_subject_is_expanded(exec_spy, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    subject, single = launch.resolve_subject(tmp_path / "elsewhere",
                                            {"DIOTIMA_GARDEN": "~/garden"})
    assert subject == tmp_path / "garden"
    assert single is False


def test_no_cwd_grove_and_no_env_falls_back_to_the_configured_garden(tmp_path, monkeypatch):
    monkeypatch.setattr(garden, "default_garden", lambda: tmp_path / "configured")
    subject, single = launch.resolve_subject(tmp_path / "elsewhere", {})
    assert subject == tmp_path / "configured"
    assert single is False


# --- prompt suggestions ----------------------------------------------------

def test_single_grove_disables_prompt_suggestions(exec_spy, tmp_path):
    """Some groves are drills: ghost text would hand the practitioner an
    answer to the scenario they are there to answer themselves."""
    grove = make_grove(tmp_path / "g")
    _, env = run(exec_spy, [], grove)
    assert env["CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION"] == "false"


def test_a_garden_subject_keeps_prompt_suggestions(exec_spy, tmp_path):
    garden_dir = tmp_path / "garden"
    make_grove(garden_dir / "social-dynamics")
    _, env = run(exec_spy, [], tmp_path / "elsewhere", {"DIOTIMA_GARDEN": str(garden_dir)})
    assert "CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION" not in env


def test_env_naming_one_grove_keeps_suggestions(exec_spy, tmp_path):
    """Pinning the bash's behaviour, not endorsing it: the switch keys on
    *how* the subject was reached, so `DIOTIMA_GARDEN=<a grove>` keeps ghost
    text where `cd <that grove>` removes it. The private grant below does not
    make this distinction. If the two should agree, this test is the one that
    says which way it changed."""
    grove = make_grove(tmp_path / "garden" / "social-dynamics")
    args, env = run(exec_spy, [], tmp_path / "elsewhere", {"DIOTIMA_GARDEN": str(grove)})
    assert "CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION" not in env
    # ... while the private grant does narrow to that grove.
    assert args[args.index("--allowedTools") + 1].endswith("social-dynamics/**)")


def test_the_callers_environment_is_not_mutated(exec_spy, tmp_path):
    caller = {"DIOTIMA_GARDEN": str(tmp_path / "garden")}
    run(exec_spy, [], make_grove(tmp_path / "g"), caller)
    assert caller == {"DIOTIMA_GARDEN": str(tmp_path / "garden")}


# --- the private grant -----------------------------------------------------

def test_grove_subject_grants_read_of_that_groves_private_directory(exec_spy, tmp_path):
    """isolate_private_root (conftest) points private_root() at tmp_path."""
    grove = make_grove(tmp_path / "garden" / "social-dynamics")
    args, _ = run(exec_spy, [], grove)
    rule = args[args.index("--allowedTools") + 1]
    expected = tmp_path / "private-root" / "social-dynamics"
    assert rule == f"Read(//{str(expected).lstrip('/')}/**)"


def test_garden_subject_grants_read_of_the_whole_store(exec_spy, tmp_path):
    garden_dir = tmp_path / "garden"
    make_grove(garden_dir / "social-dynamics")
    args, _ = run(exec_spy, [], tmp_path / "elsewhere", {"DIOTIMA_GARDEN": str(garden_dir)})
    rule = args[args.index("--allowedTools") + 1]
    assert rule == f"Read(//{str(tmp_path / 'private-root').lstrip('/')}/**)"


def test_the_rule_is_filesystem_absolute(exec_spy, tmp_path):
    """Double slash is the absolute form for a path permission rule; a
    single-slash rule would resolve against the project, granting nothing."""
    args, _ = run(exec_spy, [], make_grove(tmp_path / "g"))
    assert args[args.index("--allowedTools") + 1].startswith("Read(//")


def test_one_allowed_tools_value_only(exec_spy, tmp_path):
    """--allowedTools is variadic: a second value here would be read as one
    more tool pattern, and the grant would quietly widen. Asserted as the
    whole tail rather than by position, so a flag added after it fails here
    instead of silently widening the grant."""
    args, _ = run(exec_spy, [], make_grove(tmp_path / "g"))
    i = args.index("--allowedTools")
    assert args[i + 1].startswith("Read(//")
    assert args[i + 2:] == []


# --- grove sync ------------------------------------------------------------

def test_grove_sync_failure_never_fails_a_launch(stub_grove_sync, tmp_path, capsys):
    """The `|| true` the bash carried, as a stated guarantee rather than a
    shell accident."""
    def boom(argv):
        raise RuntimeError("git exploded")
    stub_grove_sync(boom)
    calls = []
    with pytest.raises(Execd):
        launch.main([], orig_cwd=make_grove(tmp_path / "g"), env={},
                    exec_fn=spy(calls))
    assert len(calls) == 1
    assert "grove sync skipped" in capsys.readouterr().err


def test_grove_sync_sees_this_sessions_subject(stub_grove_sync, tmp_path):
    """grove_sync resolves its own scope from the environment, so a grove
    launch must not have it sync the whole garden."""
    grove = make_grove(tmp_path / "garden" / "social-dynamics")
    seen = {}

    def record(argv):
        import os
        seen["subject"] = os.environ.get("DIOTIMA_GARDEN")
        return 0
    stub_grove_sync(record)
    with pytest.raises(Execd):
        launch.main([], orig_cwd=grove, env={}, exec_fn=spy([]))
    assert seen["subject"] == str(grove)


# --- the exec itself -------------------------------------------------------

def test_a_failed_exec_is_reported_not_swallowed(exec_spy, tmp_path, capsys):
    """os.execvpe returns only when the exec failed -- claude not on PATH, or
    not executable. Returning 0 there would have `diotima` exit successfully
    having launched nothing, and with no prompt given it would print nothing
    either: the silent success the `exec claude` this replaces never had."""
    def failed_exec(file, args, env):
        return None
    code = launch.main([], orig_cwd=make_grove(tmp_path / "g"), env={},
                       exec_fn=failed_exec)
    assert code == 127
    assert "could not exec" in capsys.readouterr().err
