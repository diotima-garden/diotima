# Utils Subsystem Extraction

<2026-05-07 — branch health_agent — sessions 98d083, 84ef61, c246a1, a3ec05, afa3ee, c911c9, b0c8e3>

## Summary
A shared utilities subsystem was extracted from the mem-bank and health-agent codebases into a new `.claude/utils/` directory containing three modules: `log.py` for project-wide logging, `llm_triggers.py` for isolated LLM calls, and `session_crawler.py` for transcript functions including `detect_mode()` for inferring session context. Both subsystems were refactored to import directly from utils, eliminating code duplication and hardcoded logic. As part of this work, dead-code shims (`listener.py` and `mem-bank/utils.py`) that had been forwarding to utils were identified and deleted, leaving utils as the sole source of shared primitives. Builder-mode awareness was wired into the health-agent: `detect-health-issues.py` now reads the full session transcript at startup and suppresses health findings when architect or builder context files are detected, preventing noise during meta work. Documentation was updated across the board — a new `.claude/meta/builder/utilities.md` guide was added to make utilities discoverable to the builder without forcing bulk imports, and dangling references to deleted hook documentation were cleaned up. The design philosophy favors conscious opt-in over eager loading, so builders check the inventory and import only what their task requires.

## Archive
[Small bank sessions](small-bank-archive/20260507T141050-small-bank.md)
