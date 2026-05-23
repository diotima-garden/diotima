# Health Agent And Session Crawler

<2026-04-24 to 2026-05-10 — branch health_agent>

## Summary

The health agent subsystem was built and iterated across April–May 2026 to create a feedback loop for pipeline health issues that had been recurring without institutional memory.

The initial build (April 2026) established three layers: hooks at session boundaries detect signals (skill invocations via `PostToolUse(Skill)`, session stops via `Stop`), a Haiku-model subagent reads accumulated findings and produces structured verdicts against builder rules, and per-rule detector modules in `detectors/` enforce the contract that every builder rule must have a complementing detector. Key design decisions included dropping a slash-command guard that was silently skipping all natural-language sessions, surfacing findings at next-session start rather than interrupting running pipelines, and adding trigger logs on every hook script as the primary debugging surface. The recurring lesson: in context-engineering applications the feedback loop is long and lossy — an assumption correct at design time silently becomes the bug as the system evolves, and the system has no mechanism to surface that the assumption is now violated.

The May 2026 iteration promoted `session_crawler` from a functional shim to a proper class-based module (`SessionTranscript`), relocated to its own directory with JSONL fixture transcripts as test inputs. Twenty-seven unit tests were rewritten against the new interface, backward-compatibility shims were deleted after parity was confirmed, and callers (`small-bank.py`, `detect-health-issues.py`) were migrated directly. `surface-session-health.py` also gained mode-gating: it now reads stdin, detects the current session mode via `SessionTranscript`, and exits silently unless the session is in builder mode — preventing health findings from surfacing during exploratory or architectural work where they are not actionable. All 34 tests pass.

## Archive

[Small bank sessions — May 2026](small-bank-archive/20260510T210720-small-bank.md)

*Files: `.claude/agents/health-agent.md` · `.claude/hooks/health-agent/` · `.claude/meta/builder/health-agent-contract.md`*
