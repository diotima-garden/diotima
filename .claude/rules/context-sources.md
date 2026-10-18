# Context Sources: Diotima Only

The harness's own auto-memory is **off** in this project — `autoMemoryEnabled: false` and
`autoDreamEnabled: false` in `.claude/settings.json`. Nothing is read from or written to
`~/.claude/projects/<slug>/memory/`.

**Why:** it is a second, invisible context channel running alongside the one this project
populates (the `SessionStart` hook, `DAFNE.md` manifests, mem-banks). Keeping it on masks
defects — a grove whose manifest or bank fails to carry a fact still *looks* fine, because
the harness remembered it out-of-band. Context population and the mem-bank machinery are
the thing under test here, so they must be the only source.

**Consequences:**

- Anything worth remembering across sessions goes into the garden, not into harness memory:
  a grove's `DAFNE.md`, its mem-bank, a mode context under `modes/`, or a rule here.
- A request to "remember this" is a request to write one of those files. Ask which, don't
  default to a memory store that is switched off.
- Existing files under the old auto-memory directory are dormant, not deleted. Treat them
  as unavailable.
- If a session appears to know something the injected context never stated, that is a
  finding — say so rather than using it.
