"""
grove_sync: the safety policy, the status reads, and the sync unit.

Each exit criterion in modes/meta/architect/grove_sync.md has a test here.
The submodule-pin case is the mandatory one — it is the regression test for
the self-disabling footgun where a merged parent bump leaves the tree
looking dirty, which trips this flow's own precondition on the next launch
and silently turns auto-sync off forever.
"""
from pathlib import Path

import pytest

import grove_sync
from conftest import commit, git, make_bare, publish
from grove_sync import GroveStatus, should_sync, skip_reason, status, sync


def _st(**overrides) -> GroveStatus:
    base = dict(
        path=Path("/nowhere"), branch="main", has_upstream=True,
        default_branch="main", behind=1, ahead=0, dirty=False,
        submodules_aligned=True,
    )
    return GroveStatus(**{**base, **overrides})


# --- the policy, with no git involved ---------------------------------------

def test_syncs_when_behind_and_clean():
    assert should_sync(_st()) is True


@pytest.mark.parametrize("overrides", [
    {"has_upstream": False},
    {"default_branch": None},
    {"branch": "try-new-layout"},
    {"dirty": True},
    {"behind": 0},
    {"ahead": 1},
])
def test_refuses_when_any_condition_fails(overrides):
    assert should_sync(_st(**overrides)) is False


def test_no_upstream_is_silent_but_unresolvable_default_is_not():
    """Two different situations wanting two different messages — collapsing
    them would skip for the right reason with the wrong explanation."""
    assert skip_reason(_st(has_upstream=False)) is None
    assert skip_reason(_st(default_branch=None)) is not None


def test_current_grove_says_nothing():
    assert skip_reason(_st(behind=0)) is None


# --- status, against real repos ---------------------------------------------

def test_behind_only_is_not_read_as_ahead(tmp_path, grove, upstream):
    """`rev-list --left-right --count` is ahead-then-behind; swapping the two
    makes should_sync fire exactly backwards, so both directions are tested."""
    publish(tmp_path, upstream, "new.md")
    grove_sync.fetch(grove, max_age_s=0, timeout_s=10)
    st = status(grove)
    assert (st.behind, st.ahead) == (1, 0)
    assert st.branch == st.default_branch == "main"
    assert should_sync(st)


def test_ahead_only_is_not_read_as_behind(grove):
    commit(grove, "local.md")
    st = status(grove)
    assert (st.behind, st.ahead) == (0, 1)
    assert not should_sync(st)
    assert "not pushed" in skip_reason(st)


def test_untracked_files_do_not_count_as_dirty(tmp_path, grove, upstream):
    """Every generated artifact in a grove is gitignored; a stray untracked
    note cannot break a fast-forward and must not block one."""
    publish(tmp_path, upstream, "new.md")
    grove_sync.fetch(grove, max_age_s=0, timeout_s=10)
    (grove / "spanish.compiled.md").write_text("generated")
    st = status(grove)
    assert st.dirty is False
    assert should_sync(st)


def test_tracked_edit_is_dirty(grove):
    (grove / "DAFNE.md").write_text("edited by hand")
    st = status(grove)
    assert st.dirty is True
    assert "uncommitted changes" in skip_reason(st)


def test_feature_branch_is_named_in_the_skip(grove):
    git(grove, "checkout", "--quiet", "-b", "try-new-layout")
    st = status(grove)
    assert not should_sync(st)
    assert "try-new-layout" in skip_reason(st)


def test_grove_with_no_remote_is_silently_skipped(tmp_path):
    local = tmp_path / "homegrown"
    local.mkdir()
    git(local, "init", "--quiet", "-b", "main")
    commit(local, "DAFNE.md", "# locally created\n")
    st = status(local)
    assert st.has_upstream is False
    assert not should_sync(st)
    assert skip_reason(st) is None


# --- sync -------------------------------------------------------------------

def test_sync_fast_forwards(tmp_path, grove, upstream):
    published = publish(tmp_path, upstream, "new.md")
    grove_sync.fetch(grove, max_age_s=0, timeout_s=10)
    result = sync(grove)
    assert result.ok
    assert git(grove, "rev-parse", "--short", "HEAD") == published
    assert (grove / "new.md").exists()


def test_sync_works_offline_against_already_fetched_refs(tmp_path, grove, upstream):
    """`git merge --ff-only @{u}` rather than `git pull --ff-only`: pull
    re-fetches and fails outright when the remote is gone, where the local
    ref merge still lands. This is why a flaky network cannot fail a launch."""
    publish(tmp_path, upstream, "new.md")
    grove_sync.fetch(grove, max_age_s=0, timeout_s=10)
    upstream.rename(tmp_path / "remote-unplugged.git")

    result = sync(grove)
    assert result.ok
    assert (grove / "new.md").exists()


def test_fetch_failure_is_not_fatal(tmp_path, grove, upstream):
    upstream.rename(tmp_path / "remote-unplugged.git")
    assert grove_sync.fetch(grove, max_age_s=0, timeout_s=10) is False
    assert status(grove).has_upstream is True   # the config is still there


def test_fetch_is_throttled_on_fetch_head(tmp_path, grove, upstream):
    assert grove_sync.fetch(grove, max_age_s=0, timeout_s=10) is True
    assert grove_sync.fetch(grove, max_age_s=3600, timeout_s=10) is False


# --- the mandatory regression: a bumped parent pin --------------------------

def test_parent_pin_bump_leaves_no_dirty_tree(tmp_path, grove, upstream):
    """An upstream commit that bumps a parent pin must leave the grove clean
    and its submodules aligned after sync.

    Merging without `submodule update --init --recursive` updates the
    *recorded* pin while parents/<x> stays at the old SHA — `git status`
    then reports `modified: parents/... (new commits)`, the tree looks
    dirty, and this flow's own precondition turns auto-sync off from then
    on. That is the failure this test exists to catch.
    """
    parent_remote = make_bare(tmp_path / "parent.git")
    parent_work = tmp_path / "parent-work"
    git(tmp_path, "clone", "--quiet", str(parent_remote), "parent-work")
    commit(parent_work, "DAFNE.md", "# parent v1\n")
    git(parent_work, "push", "--quiet", "-u", "origin", "main")

    # The author mounts the parent and publishes.
    author = tmp_path / "author"
    git(tmp_path, "clone", "--quiet", str(upstream), "author")
    git(author, "submodule", "add", "--quiet", str(parent_remote), "parents/deck")
    git(author, "commit", "--quiet", "-m", "mount parents/deck")
    git(author, "push", "--quiet", "origin", "main")

    # The consumer catches up to that, with submodules.
    grove_sync.fetch(grove, max_age_s=0, timeout_s=10)
    assert sync(grove).ok
    assert (grove / "parents" / "deck" / "DAFNE.md").exists()

    # The author improves the parent and re-pins.
    commit(parent_work, "improvement.md", "better\n")
    git(parent_work, "push", "--quiet", "origin", "main")
    git(author / "parents" / "deck", "pull", "--quiet", "--ff-only")
    git(author, "add", "parents/deck")
    git(author, "commit", "--quiet", "-m", "bump parents/deck")
    git(author, "push", "--quiet", "origin", "main")

    grove_sync.fetch(grove, max_age_s=0, timeout_s=10)
    st_before = status(grove)
    assert should_sync(st_before), "the consumer should see the pin bump as a plain fast-forward"

    result = sync(grove)
    assert result.ok
    assert result.submodules_aligned, "submodule left behind — the self-disabling footgun"
    assert (grove / "parents" / "deck" / "improvement.md").exists()

    # And the decisive part: the tree is clean, so the *next* launch still syncs.
    st_after = status(grove)
    assert st_after.dirty is False, "a bumped pin left the tree looking dirty; auto-sync would now be off"
    assert st_after.submodules_aligned
    assert should_sync(_st(behind=1)) and not should_sync(st_after)  # clean and current


# --- the silent-rot case: current, clean, but submodules adrift -------------

def test_misaligned_submodules_are_never_silent(tmp_path, grove, upstream):
    """A grove that is current and clean but has an uninitialized submodule
    is the one state nothing else catches: `git status` reports it clean, so
    `dirty` is False, `behind` is 0, and without this branch it would be
    skipped with no line at all — indistinguishable from healthy, forever.
    """
    parent_remote = make_bare(tmp_path / "parent.git")
    parent_work = tmp_path / "parent-work"
    git(tmp_path, "clone", "--quiet", str(parent_remote), "parent-work")
    commit(parent_work, "DAFNE.md", "# parent\n")
    git(parent_work, "push", "--quiet", "-u", "origin", "main")

    author = tmp_path / "author"
    git(tmp_path, "clone", "--quiet", str(upstream), "author")
    git(author, "submodule", "add", "--quiet", str(parent_remote), "parents/deck")
    git(author, "commit", "--quiet", "-m", "mount parents/deck")
    git(author, "push", "--quiet", "origin", "main")

    grove_sync.fetch(grove, max_age_s=0, timeout_s=10)
    assert sync(grove).ok

    # Now break it the way a half-finished manual checkout would.
    git(grove, "submodule", "deinit", "--force", "parents/deck")

    st = status(grove)
    assert st.dirty is False, "precondition: git status considers this clean"
    assert st.behind == 0, "precondition: nothing to pull"
    assert st.submodules_aligned is False
    assert not should_sync(st)
    assert "submodules out of sync" in skip_reason(st)


def test_submodule_misalignment_outranks_the_dirty_message(grove):
    """A submodule at the wrong SHA *does* show in `git status`, so `dirty`
    would fire first and blame an edit the user never made."""
    st = _st(dirty=True, submodules_aligned=False)
    assert "submodules out of sync" in skip_reason(st)
