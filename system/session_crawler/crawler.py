"""
Session transcript reader and mode detector.

Primary interface: SessionTranscript(path)
    .events             — lazy-loaded list of JSONL events
    .mode()             — 'architect' | 'builder' | 'user' (first indicator wins)
    .modes_seen()       — set of all modes observed (use for multi-mode sessions)
    .matches(patterns)  — set of matched pattern objects
    .matched_any(patterns) -> bool

    SessionTranscript.from_hook_stdin(data)
        Build from parsed hook stdin dict. Reliable in PostToolUse / Stop / SessionEnd;
        likely available in UserPromptSubmit. Always handle None return.
"""

import json
import os
import re


_ARCHITECT_RE = re.compile(r"meta/architect/context\.md")
_BUILDER_RE = re.compile(r"meta/builder/context\.md")


def _extract_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "\n".join(parts)
    return ""


# Public alias used by callers that import extract_text directly.
extract_text = _extract_text


def _candidate_strings(ev):
    if ev.get("type") == "user":
        yield _extract_text(ev.get("message", {}).get("content", ""))
        return
    if ev.get("type") == "assistant":
        content = ev.get("message", {}).get("content", [])
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    tool_input = block.get("input", {}) or {}
                    for key in ("file_path", "path", "pattern"):
                        val = tool_input.get(key, "")
                        if isinstance(val, str):
                            yield val


def _detect_mode_from_events(events):
    for ev in events:
        for s in _candidate_strings(ev):
            if _ARCHITECT_RE.search(s):
                return "architect"
            if _BUILDER_RE.search(s):
                return "builder"
    return "user"


class SessionTranscript:
    """
    Lazy-loading wrapper around a Claude Code session transcript (JSONL).

    mode() returns the *first* mode indicator found in the transcript.
    In sessions that switch modes mid-conversation, use modes_seen() instead.
    """

    def __init__(self, path: str):
        self.path = path
        self._events = None

    @classmethod
    def from_hook_stdin(cls, data: dict) -> "SessionTranscript | None":
        """
        Build from parsed hook stdin dict.

        Reliable in PostToolUse, Stop, and SessionEnd hooks. Likely available
        in UserPromptSubmit; not guaranteed across Claude Code versions.
        Always handle the None return.
        """
        path = data.get("transcript_path", "")
        if not path or not os.path.exists(path):
            return None
        return cls(path)

    @property
    def events(self) -> list:
        if self._events is None:
            self._events = self._load()
        return self._events

    def _load(self) -> list:
        events = []
        try:
            with open(self.path) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except OSError:
            pass
        return events

    def mode(self) -> str:
        """Return 'architect' | 'builder' | 'user' based on first mode indicator found."""
        return _detect_mode_from_events(self.events)

    def modes_seen(self) -> set:
        """Return set of all modes observed (useful when a session switched modes)."""
        found = set()
        for ev in self.events:
            for s in _candidate_strings(ev):
                if _ARCHITECT_RE.search(s):
                    found.add("architect")
                if _BUILDER_RE.search(s):
                    found.add("builder")
        return found if found else {"user"}

    def matches(self, patterns) -> set:
        found = set()
        target = len(patterns)
        for ev in self.events:
            for s in _candidate_strings(ev):
                for pat in patterns:
                    if pat.pattern in found:
                        continue
                    if pat.search(s):
                        found.add(pat.pattern)
            if len(found) == target:
                break
        return found

    def matched_any(self, patterns) -> bool:
        return bool(self.matches(patterns))
