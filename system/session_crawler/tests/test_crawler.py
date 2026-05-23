"""
Tests for session_crawler.crawler.

Covers:
  - SessionTranscript: mode(), modes_seen(), lazy loading, from_hook_stdin(), matches()
  - Edge cases: missing file, empty file, malformed JSONL
"""
import re
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).parent
FIXTURES_DIR = TESTS_DIR / "fixtures"
CLAUDE_DIR = TESTS_DIR.parent.parent  # .claude/

sys.path.insert(0, str(CLAUDE_DIR))

from session_crawler import SessionTranscript  # noqa: E402

FIXTURES = {
    "user":            FIXTURES_DIR / "user-session.jsonl",
    "architect":       FIXTURES_DIR / "architect-session.jsonl",
    "builder":         FIXTURES_DIR / "builder-session.jsonl",
    "arch_then_build": FIXTURES_DIR / "architect-then-builder.jsonl",
    "build_then_arch": FIXTURES_DIR / "builder-then-architect.jsonl",
}


# ---------------------------------------------------------------------------
# Mode detection
# ---------------------------------------------------------------------------

class TestMode:
    def test_user_session(self):
        assert SessionTranscript(str(FIXTURES["user"])).mode() == "user"

    def test_architect_session(self):
        assert SessionTranscript(str(FIXTURES["architect"])).mode() == "architect"

    def test_builder_session(self):
        assert SessionTranscript(str(FIXTURES["builder"])).mode() == "builder"

    def test_architect_then_builder_first_wins(self):
        # architect context read first → mode() returns 'architect'
        assert SessionTranscript(str(FIXTURES["arch_then_build"])).mode() == "architect"

    def test_builder_then_architect_first_wins(self):
        # builder context read first → mode() returns 'builder'
        assert SessionTranscript(str(FIXTURES["build_then_arch"])).mode() == "builder"


class TestModesSeen:
    def test_user_session(self):
        assert SessionTranscript(str(FIXTURES["user"])).modes_seen() == {"user"}

    def test_architect_only(self):
        assert SessionTranscript(str(FIXTURES["architect"])).modes_seen() == {"architect"}

    def test_builder_only(self):
        assert SessionTranscript(str(FIXTURES["builder"])).modes_seen() == {"builder"}

    def test_arch_then_build_both_seen(self):
        assert SessionTranscript(str(FIXTURES["arch_then_build"])).modes_seen() == {"architect", "builder"}

    def test_build_then_arch_both_seen(self):
        assert SessionTranscript(str(FIXTURES["build_then_arch"])).modes_seen() == {"architect", "builder"}


# ---------------------------------------------------------------------------
# Lazy loading
# ---------------------------------------------------------------------------

class TestLazyLoading:
    def test_events_not_loaded_on_init(self):
        t = SessionTranscript(str(FIXTURES["user"]))
        assert t._events is None

    def test_events_loaded_on_first_access(self):
        t = SessionTranscript(str(FIXTURES["user"]))
        _ = t.events
        assert t._events is not None
        assert isinstance(t._events, list)

    def test_events_cached_across_accesses(self):
        t = SessionTranscript(str(FIXTURES["user"]))
        first = t.events
        second = t.events
        assert first is second


# ---------------------------------------------------------------------------
# from_hook_stdin
# ---------------------------------------------------------------------------

class TestFromHookStdin:
    def test_valid_path(self):
        t = SessionTranscript.from_hook_stdin({"transcript_path": str(FIXTURES["builder"])})
        assert t is not None
        assert t.mode() == "builder"

    def test_missing_key_returns_none(self):
        assert SessionTranscript.from_hook_stdin({}) is None

    def test_empty_path_returns_none(self):
        assert SessionTranscript.from_hook_stdin({"transcript_path": ""}) is None

    def test_nonexistent_path_returns_none(self):
        assert SessionTranscript.from_hook_stdin({"transcript_path": "/no/such/file.jsonl"}) is None


# ---------------------------------------------------------------------------
# matches / matched_any
# ---------------------------------------------------------------------------

class TestMatching:
    def test_matched_any_hit(self):
        pats = [re.compile(r"builder")]
        assert SessionTranscript(str(FIXTURES["builder"])).matched_any(pats) is True

    def test_matched_any_miss(self):
        pats = [re.compile(r"builder")]
        assert SessionTranscript(str(FIXTURES["user"])).matched_any(pats) is False

    def test_matches_returns_set_of_pattern_strings(self):
        pats = [re.compile(r"builder"), re.compile(r"architect")]
        result = SessionTranscript(str(FIXTURES["arch_then_build"])).matches(pats)
        assert isinstance(result, set)
        assert r"builder" in result
        assert r"architect" in result

    def test_matches_partial_hit(self):
        pats = [re.compile(r"builder"), re.compile(r"NEVER_APPEARS_XYZ")]
        result = SessionTranscript(str(FIXTURES["builder"])).matches(pats)
        assert r"builder" in result
        assert r"NEVER_APPEARS_XYZ" not in result


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_nonexistent_file_empty_events(self):
        t = SessionTranscript("/no/such/file.jsonl")
        assert t.events == []

    def test_nonexistent_file_mode_user(self):
        assert SessionTranscript("/no/such/file.jsonl").mode() == "user"

    def test_nonexistent_file_modes_seen_user(self):
        assert SessionTranscript("/no/such/file.jsonl").modes_seen() == {"user"}

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.jsonl"
        f.write_text("")
        t = SessionTranscript(str(f))
        assert t.events == []
        assert t.mode() == "user"

    def test_malformed_lines_skipped(self, tmp_path):
        f = tmp_path / "bad.jsonl"
        f.write_text(
            'not json\n'
            '{"type":"user","message":{"role":"user","content":"hi"}}\n'
            '{broken\n'
        )
        t = SessionTranscript(str(f))
        assert len(t.events) == 1

    def test_blank_lines_skipped(self, tmp_path):
        f = tmp_path / "blanks.jsonl"
        f.write_text(
            '\n'
            '{"type":"user","message":{"role":"user","content":"hi"}}\n'
            '\n'
        )
        assert len(SessionTranscript(str(f)).events) == 1
