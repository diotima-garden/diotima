# mem-bank: SessionEnd hook for automatic active-context updates

**Date:** 2026-04-27

## Context

`active-context.md` updates were soft-enforced by instruction in `meta/builder/context.md`
and `meta/architect/context.md`: "before finishing, update active-context.md." The rule
loads at session start but needs to fire at session end — by which time the agent's
attention is on its final response, not on a constitutional contract from thousands of
tokens earlier. Sessions also abort. The mechanism was unreliable by design.

The wider question was: what *are* rules good for, and where do hooks beat them?

## Decision

A generic Python script — `.claude/mem-bank/append-session-summary.py` —
registered as a `SessionEnd` hook. It takes `--keywords` (comma-separated regex
patterns) and `--target` (project-relative path). When the session transcript matches
any pattern, the script pre-processes content in Python (all user prompts + last
assistant response + `git status`), spawns `claude -p` (no `--bare`, since `--bare`
requires `ANTHROPIC_API_KEY` and plain `-p` reuses the parent's auth), and appends a
2–4 sentence summary to the target file with a timestamp + short session-id heading.
Append-only — never rewrites prior content. Failures log silently to `mem-bank.log`
and exit 0; SessionEnd errors must never block teardown.

The same primitive generalizes: any "regex matches → summarize → append here"
destination is a new entry under `SessionEnd` in `settings.json`. `active-context.md`
is the first user; the pattern is open to user-defined persistent-memory needs.

## Why

**Rules vs. hooks.** Rules are good for things that require judgment in the moment —
shaping decisions while the agent has context, content generation, cross-cutting
principles. Hooks are good for deterministic triggers, format/policy enforcement, and
events that must fire regardless of agent attention. The active-context update sits on
the boundary: trigger is mechanical (session ending in a relevant mode), content
requires judgment (what's open, what's closed, where to resume). Pure-rule fails for
lack of mechanical trigger; pure-hook would fail for lack of judgment. Pre-process in
Python + spawn claude -p separates the two cleanly.

**SessionEnd over Stop.** Stop fires per turn, producing N partial summaries per
session and forcing dedup logic. SessionEnd fires once per session — one summary, no
dedup, simpler code. Trade-off: hard kills skip the hook. Acceptable.

**Append-only.** Never overwriting protects against the spawned claude producing a
worse summary than what was there. Each block is stamped with timestamp + short
session id, so duplicates (if they ever occur) are visible and collapsible by hand.

**Cheapness in the prompt, not the model.** The prompt explicitly forbids file opens
and tool use. Cheap by instruction, model choice deferred. If costs bite, escalate to
Haiku or `--allowed-tools ""`.

**Generalization without complexity.** One script, two parameters. Adding a memory
destination is one more `command` entry in `settings.json` — no script changes.
Honors the non-duplication principle: the rule is replaced by the mechanism, not
duplicated alongside it.

## Trade-offs accepted

- Hard session terminations skip the summary (no SessionEnd fires).
- Spawned `claude -p` carries the parent's auth and project context; cheapness relies
  on prompt discipline rather than mechanical tool restriction.
- Detection is regex over user message text and tool_input file paths only — a
  mode-touching session that *only* edited unrelated paths but discussed the mode in
  prose would still match (via the user prompts), which is the desired behavior.
