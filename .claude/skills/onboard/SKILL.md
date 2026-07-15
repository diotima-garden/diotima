---
name: onboard
description: Welcome a newcomer to the project — audit their machine, diagnose the Anki wiring, and guide them to a first real success
disable-model-invocation: false
---

Welcome a person who has just cloned this repository and opened Claude Code inside it.
Diagnose what works on *their* machine, be honest about what doesn't, and get them to
one real first success. Assume zero prior context — this may be the first thing they
ever run here.

This skill **diagnoses and instructs — it never fixes on its own**. Every repair
(initializing submodules, creating venvs, installing software) is offered as an exact
command and run only on the person's go-ahead. Permission prompts on those commands are
intentional; do not ask for them to be whitelisted.

**Usage** `/onboard`

## Meet the person

Ask, in one message: their technical background, and what they came to learn (which
skill or language). Calibrate everything downstream to the answer — for a
non-technical person, say what each check *means* before running it and translate
failures into plain consequences; for a technical one, stay terse.

If they are on Windows, set expectations immediately: the project is untested there,
and `.mcp.json` points at a POSIX venv path (`plugins/anki-mcp/.venv/bin/python3`)
while Windows venvs use `Scripts\python.exe` — they will need to adjust `.mcp.json`
locally. Cross-platform support is the top item in the README's contributor backlog;
say so honestly.

## Audit the clone

Submodules are the classic miss — a non-recursive clone leaves `plugins/anki-mcp` and
`.claude/utils` empty and nothing downstream works.

```bash
git submodule status
```

A leading `-` on any line means uninitialized. Offer the fix and let them run it:

```bash
git submodule update --init --recursive
```

## Audit the machine

Python drives the hooks, the memory subsystem, and the MCP server:

```bash
python3 --version
```

The Anki MCP server runs from its own venv — `.mcp.json` spawns it from there, so if
this is missing the `anki` MCP tools simply won't exist in the session:

```bash
ls plugins/anki-mcp/.venv/bin/python3
```

The card pipeline also compiles grove context through its own venv:

```bash
ls plugins/context-compiler/.venv/bin/python3
```

For any missing venv, point at the component's own README for the exact setup commands
(`plugins/anki-mcp/README.md`, and the README's "moving parts" section for the full
list) — don't improvise the commands here. The Gemini venv and `GOOGLE_API_KEY` are
**optional** (YouTube extraction only); mention them, don't gate on them.

## Probe Anki

The whole system drives Anki through the AnkiConnect add-on's local server:

```bash
curl -s http://localhost:8765
```

An `AnkiConnect` banner means Anki is running with the add-on — done. No response
means, in order of likelihood: Anki isn't running, or the AnkiConnect add-on
(code `2055492159`, from Tools → Add-ons in Anki) isn't installed. Anki must stay
open in the background whenever this project is in use.

## Smoke-test the MCP bridge

Only meaningful once the anki-mcp venv exists and Anki answers the probe. Call
`mcp__anki__deck_names`. Three outcomes:

- **Deck list returns** — the full chain works (Claude Code → MCP server → AnkiConnect
  → Anki). Keep the list; the first act uses it.
- **The `anki` MCP tools don't exist in this session** — the server wasn't up at
  startup. Have them restart Claude Code (the MCP server is spawned once, at launch)
  and run `/onboard` again; the audits will pass quickly the second time.
- **Tools exist but the call fails** — re-check the Anki probe; if that passes, read
  the error to them plainly and debug together.

Managed note types bootstrap themselves lazily on first tool use — no manual step.

## Deliver the verdict

Summarize as a short table: component → status → what it means *for them*. Be honest in
the project's own register — this is early infrastructure, not a polished product.
Three tiers:

- **Full** — everything green: card generation, feedback loop, memory, the lot.
- **Degraded** — the Anki bridge works but something peripheral doesn't (hooks,
  optional venvs). Say exactly what they lose (e.g. session memory, YouTube
  extraction) and that card work still functions.
- **Blocked** — the bridge itself is down. Name the single next fix, offer to help,
  and stop; don't march into the first act over a broken bridge.

## First act

The front end of this project is this chat — tell them that. They don't operate the
machinery; they ask, and it acts.

Then walk them to a first success, shaped by what they said they came to learn:

- Show the decks found in the smoke test (reuse that result — don't re-call).
- Open `groves/languages/spanish/context.md` together as the worked example of a
  *grove* — a per-domain spec the generator obeys.
- If their goal is a language: offer to scaffold a grove for it under
  `groves/languages/`, inheriting `groves/languages/language-defaults.md` the way
  Spanish and English do. Otherwise: model the structure on the Spanish grove and
  `groves/instruments/`.
- With a grove in hand (theirs or an existing one), invite their first real input and
  run `/pipe:anki-add-cards <grove-dir> <input>` — backup, generation, and the
  approval gate will introduce themselves.

Close by pointing at `CLAUDE.md` as the map, and the README's contributor backlog if
they made it through with scars and ideas.
