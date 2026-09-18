"""
Fixtures for grove_sync tests: throwaway git repos in tmp_path.

Everything here is deliberately version-independent — `git init -b main`
and an explicitly set bare HEAD — because grove_sync resolves the default
branch from `refs/remotes/origin/HEAD` rather than assuming one. A fixture
that inherited the machine's `init.defaultBranch` would make the suite
pass or fail by accident.
"""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import grove_sync  # noqa: E402

# Local-path submodules are refused by default since git 2.38 (CVE-2022-39253);
# the fixtures use file:// remotes, so the tests opt back in explicitly.
_GIT_ENV_ARGS = [
    "-c", "user.email=test@example.com",
    "-c", "user.name=Test",
    "-c", "protocol.file.allow=always",
    "-c", "commit.gpgsign=false",
]


def git(cwd: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", *_GIT_ENV_ARGS, *args],
        cwd=cwd, capture_output=True, text=True,
    )
    assert done.returncode == 0, f"git {' '.join(args)} failed in {cwd}:\n{done.stderr}"
    return done.stdout.strip()


def make_bare(path: Path) -> Path:
    path.mkdir(parents=True)
    git(path, "init", "--bare", "--quiet", "-b", "main")
    # Pin the bare repo's HEAD so clones get a resolvable origin/HEAD.
    git(path, "symbolic-ref", "HEAD", "refs/heads/main")
    return path


def commit(repo: Path, name: str, text: str = "x") -> str:
    (repo / name).write_text(text)
    git(repo, "add", name)
    git(repo, "commit", "--quiet", "-m", f"add {name}")
    return git(repo, "rev-parse", "--short", "HEAD")


@pytest.fixture
def upstream(tmp_path: Path) -> Path:
    """A bare remote on `main` with one commit already in it."""
    bare = make_bare(tmp_path / "remote.git")
    seed = tmp_path / "seed"
    git(tmp_path, "clone", "--quiet", str(bare), "seed")
    commit(seed, "DAFNE.md", "# fixture grove\n")
    git(seed, "push", "--quiet", "-u", "origin", "main")
    return bare


@pytest.fixture
def grove(tmp_path: Path, upstream: Path) -> Path:
    """A clone of `upstream`, current, clean, on main."""
    git(tmp_path, "clone", "--quiet", str(upstream), "grove")
    clone = tmp_path / "grove"
    # Clones don't always record origin/HEAD; make it explicit, as a real
    # `git clone` from a server does.
    git(clone, "remote", "set-head", "origin", "-a")
    return clone


def publish(tmp_path: Path, upstream: Path, name: str) -> str:
    """Add a commit to the remote, as the grove's author would."""
    work = tmp_path / f"author-{name}"
    git(tmp_path, "clone", "--quiet", str(upstream), work.name)
    sha = commit(work, name)
    git(work, "push", "--quiet", "origin", "main")
    return sha


@pytest.fixture(autouse=True)
def allow_file_submodules(monkeypatch):
    """grove_sync calls plain `git` with no -c flags — correctly, since it
    must work on a fresh consumer machine. These fixtures use file://
    remotes, refused for submodules since git 2.38 (CVE-2022-39253), and a
    repo-local `protocol.file.allow` does *not* reach the clone `git
    submodule update` spawns — that subprocess starts outside any repo. The
    GIT_CONFIG_* env form does reach it, and grove_sync inherits os.environ.
    Test scaffolding only; nothing in the product depends on it.
    """
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "protocol.file.allow")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "always")


@pytest.fixture(autouse=True)
def isolate_log(tmp_path, monkeypatch):
    """grove_sync.log is bound at import time to the real
    system/diotima/diotima.log. Left alone, every test run appends there —
    and since the `grove` fixture always clones to a directory literally
    named "grove", every line reads `grove: ff <sha>..<sha>, ...`, which is
    indistinguishable from every other test run and carries no identifying
    grove name. Rebind it to a per-test file so the product log stays real
    runs only.
    """
    monkeypatch.setattr(grove_sync, "log", grove_sync.make_logger("grove-sync", tmp_path / "test.log"))
